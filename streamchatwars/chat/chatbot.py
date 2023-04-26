'''
This module handles the connection and communication to the chat server.
'''

# native imports
from collections import deque
from functools import partial
from ssl import SSLContext
from ssl import SSLSocket
from ssl import create_default_context
from threading import Thread
from time import sleep
from time import time
from typing import Callable

# pip imports
from irc.bot import SingleServerIRCBot
from irc.client import Event
from irc.client import Reactor
from irc.client import ServerConnection
from irc.client import ServerNotConnectedError
from irc.connection import Factory

# internal imports
from .._interfaces._chatbot import AbstractMessageSender
from .._interfaces._thread_support import AbstractThreadSupport
from .._shared.constants import CHECK_JOIN_INTERVAL
from .._shared.global_data import GlobalData
from .._shared.helpers_color import ColorText
from .._shared.helpers_native import nop
from .._shared.helpers_print import thread_print
from .._shared.helpers_print import thread_print_timestamped
from ..config.config import IRC_Settings
from ..teams.functions import add_message_to_assigned_team
from .chatmsg import ChatMessage
from .commands import handle_command


# ==================================================================================================
class StopBotException(Exception):
  '''
  Custom Exception that allows stopping the bot from within the reactor loop.
  '''
  pass
# ==================================================================================================


# ==================================================================================================
class Custom_Reactor(Reactor):
  '''
  Custom Reactor class that allows stopping the reactor loop by setting
  `keep_running` to `False`.
  '''
  # Instance variables:
  keep_running: bool
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    on_connect: Callable[[], None] = nop,
    on_disconnect: Callable[[], None] = nop
  ) -> None:
    '''
    Sub-classed `__init__` method with additional object property
    `keep_running`.
    '''
    self.keep_running = True
    super().__init__(on_connect=on_connect, on_disconnect=on_disconnect)
  # ----------------------------------------------------------------------------

  def process_once(self, timeout: float = 0) -> None:
    '''
    Sub-classed `process_once` method that raises `StopBotException` if
    it sees that `keep_running` is `False`.
    '''
    if not self.keep_running:
      raise StopBotException
    super().process_once(timeout=timeout)
# ==================================================================================================


# ==================================================================================================
class ChatBot(
  SingleServerIRCBot,
  AbstractMessageSender,
  AbstractThreadSupport
):
  '''
  (Singleton) class that is responsible for establishing the connection
  to the remote chat server and the subsequent sending and receiving
  of chat data.

  Not tested for multiple instance behaviour!
  '''
  # Class variables:
  reactor_class: type[Custom_Reactor] = Custom_Reactor
  # Instance variables:
  reactor: Custom_Reactor
  host: str
  port: int
  channel_set: set[str]
  message_interval: float
  connection_timeout: float
  join_rate_limit_amount: int
  join_rate_limit_time: float
  last_message_time: float
  '''Keep track of time when last message was sent to keep within rate-limits'''
  message_queue: deque[tuple[str, str]]
  keep_running: bool
  finished_startup: bool = False
  message_queue_thread: Thread
  # ----------------------------------------------------------------------------

  def __init__(self, irc_settings: IRC_Settings) -> None:
    '''
    Prepare `ChatBot`-specific object properties before letting
    `SingleServerIRCBot.__init__()` do the actual bot creation.
    '''

    server_list: list[tuple[str, int, str]] = [(
      irc_settings.host,
      irc_settings.port,
      irc_settings.oauth_token
    )]

    self.host = irc_settings.host
    self.port = irc_settings.port

    nickname: str = irc_settings.username
    realname: str = irc_settings.username

    self.channel_set = irc_settings.channel_set

    self.message_interval = irc_settings.message_interval
    self.connection_timeout = irc_settings.connection_timeout
    self.join_rate_limit_amount = irc_settings.join_rate_limit_amount
    self.join_rate_limit_time = irc_settings.join_rate_limit_time

    self.last_message_time = 0
    self.message_queue = deque()

    self.keep_running = True

    self.message_queue_thread = Thread(
      target=self.handle_message_queue,
      daemon=True)
    self.message_queue_thread.start()

    # let base class handle the rest
    super().__init__(
      server_list,
      nickname,
      realname,
      connect_factory=self.create_connect_factory()
    )
  # ----------------------------------------------------------------------------

  def create_connect_factory(self) -> Factory:
    '''
    We only need this to make the connection SSL compatible.
    Because for some reason nobody thought that SSL connections should be an
    easy default instead of diving into the code and finding out what needs
    to be wrapped...
    '''
    ssl_context: SSLContext = create_default_context()
    wrapping_func: partial[SSLSocket] = partial(
      ssl_context.wrap_socket,
      server_hostname=self.host
    )
    ssl_factory: Factory = Factory(wrapper=wrapping_func)
    return ssl_factory
  # ----------------------------------------------------------------------------

  def stop_bot(self) -> None:
    '''
    Disconnect from the IRC server and stop all looping operations
    (including self.reactor), so the bot's thread can be shut down.
    '''
    self.keep_running = False
    while self.message_queue_thread.is_alive():
      # Wait until sub-thread has shutdown so we're never in the
      # awkward position of trying to send messages after the connection
      # to the server has been disconnected.
      sleep(0.1)
    self.disconnect("Bye")
    self.reactor.keep_running = False
  # ----------------------------------------------------------------------------

  def handle_message_queue(self) -> None:
    '''
    Sub-thread function that sends out queued messages when rate limits allow.
    '''
    while self.keep_running:
      try:
        channel, message = self.message_queue.popleft()
        # This is kinda hacky, but it gets the job done.
        # Basically retry sending every 0.1 seconds
        # until rate limits allow sending and the message is out.
        while self.keep_running and not self.send_message(channel, message):
          sleep(0.1)
      except IndexError:
        sleep(0.1)
  # ----------------------------------------------------------------------------

  def on_disconnect(self, connection: ServerConnection, event: Event) -> None:
    '''
    Called when the bot has been disconnected from the server.
    '''
    thread_print_timestamped(ColorText.error(
      f"Disconnected from {self.host}:{self.port}!"
    ))
    if not self.finished_startup:
      # If the bot hasn't finished startup yet, we try an accelerated
      # reconnection attempt.
      sleep(1)
      self.start()
  # ----------------------------------------------------------------------------

  def on_welcome(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes after successfully establishing a connection
    to the server)

    Request IRCv3 capabilities and join all relevant channels.
    '''
    thread_print_timestamped(
      f"Connected to {self.host}:{self.port} as user "
      f"{ColorText.info(connection.username)}, joining channels..."
    )
    connection.cap('REQ', ':twitch.tv/membership')
    connection.cap('REQ', ':twitch.tv/tags')
    connection.cap('REQ', ':twitch.tv/commands')
    # outsource joining into an extra thread to have events continue
    # to be processed while waiting for rate limit delays.
    Thread(target=self.join_channels, args=[connection], daemon=True).start()
  # ----------------------------------------------------------------------------

  def on_join(self, c: ServerConnection, e: Event) -> None:
    '''
    IRC Event (executes when users are joining a channel)

    Only used for output to keep user in the loop.
    '''
    if str(e.source).split("!")[0] == c.nickname:
      thread_print(f"Joined channel {e.target}")
  # ----------------------------------------------------------------------------

  def join_channels(self, connection: ServerConnection) -> None:
    '''
    Join all channels in `self.channel_set` while respecting rate limits
    set by `self.join_rate_limit_amount` and `self.join_rate_limit_time`.

    Intended to be used in its own thread to prevent rate limit cooldowns
    stopping event processing for the rest of the bot.
    '''
    rate_limit_counter: int = 0
    join_set: set[str] = set()
    channel: str
    for channel in self.channel_set:
      if rate_limit_counter < self.join_rate_limit_amount:
        # Collect channels to join in one go a long as rate limit isn't reached
        join_set.add(channel)
        rate_limit_counter += 1
      else:
        # Rate limit reached: Join the collected channels and reset + wait
        thread_print(f"Attempting to join channels: {', '.join(join_set)}")
        for chan in join_set:
          if not self.keep_running:  # Safety: don't join in dead connection
            self.stop_bot()
            return
          connection.join(chan)
        join_set.clear()
        thread_print(ColorText.warning(
          f"Join rate limit reached. Waiting {self.join_rate_limit_time} "
          "seconds before attempting further joins."
        ))
        sleep(self.join_rate_limit_time)
        rate_limit_counter = 0
    # Join remaining channels
    if join_set:
      thread_print(f"Attempting to join channels: {', '.join(join_set)}")
      for chan in join_set:
        if not self.keep_running:  # Safety: don't join in dead connection
          self.stop_bot()
          return
        connection.join(chan)
  # ----------------------------------------------------------------------------

  def check_all_joined(self) -> None:
    '''
    Cancel the connection attempt if some channels could not be joined.

    Tell the user where the problem lies, so they get a chance to fix
    possible malformed configuration files.
    '''
    time_slept: float = 0
    missing_channel_set: set[str] = set()
    while time_slept <= self.connection_timeout:
      if not self.keep_running:
        self.stop_bot()
        return
      sleep(CHECK_JOIN_INTERVAL)
      time_slept += CHECK_JOIN_INTERVAL
      missing_channel_set = self.channel_set - set(self.channels.keys())
      if len(missing_channel_set) == 0:
        thread_print(ColorText.good(
          ">> Joined all channels, you're good to go! <<"
        ))
        self.finished_startup = True
        self.finish_connecting()
        return
    thread_print(ColorText.error(
      "Some channels could not be joined in time: "
      f"{' '.join(missing_channel_set)}"
    ))
    thread_print(ColorText.error("Aborting!"))
    self.stop_bot()
    self.abort_connection()
  # ----------------------------------------------------------------------------

  def finish_connecting(self) -> None:
    '''
    Entry point for a mock method to test other things that require a
    server connection or wrap up testing.

    Does nothing in its default implementation by design!
    '''
    pass
  # ----------------------------------------------------------------------------

  def abort_connection(self) -> None:
    '''
    Entry point for a mock method to test naturally failed connection
    attempts. (It happens sometimes in the real world)

    Does nothing in its default implementation by design!
    '''
    pass
  # ----------------------------------------------------------------------------

  def start_and_check(self) -> None:
    '''
    Start the bot and establish a connection to the chat server.

    Since the bot operates in a blocking way, check if the
    connection was successful in another thread.
    '''
    self.finished_startup = False
    Thread(target=self.check_all_joined).start()
    thread_print(ColorText.warning(
      f"Attempting connection to {self.host}:{self.port}"
    ))
    try:
      self.start()
    except ValueError as e:
      # sometimes start() raises an exception after die() has been called.
      if e.args[0] != "Read on closed or unwrapped SSL socket.":
        raise
    except ServerNotConnectedError:
      thread_print(ColorText.error("Server Connection lost!"))
      self.keep_running = False
      self.reactor.keep_running = False
      return
    except StopBotException:
      thread_print(ColorText.warning("Stopped bot."))
      return
    return
  # ----------------------------------------------------------------------------

  def on_pubmsg(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a message is sent in a channel)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_message(msg)
    if GlobalData.Prefix.Command.message_is_command(msg):
      handle_command(msg)
    else:
      add_message_to_assigned_team(msg)
  # ----------------------------------------------------------------------------

  def on_usernotice(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a usernotice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_message(msg)
    if GlobalData.Prefix.Command.message_is_command(msg):
      handle_command(msg)
    else:
      add_message_to_assigned_team(msg)
  # ----------------------------------------------------------------------------

  def on_pubnotice(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a notice to a channel is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    thread_print_timestamped(
      f"Received NOTICE to {msg.channel}: {msg.message}"
    )
  # ----------------------------------------------------------------------------

  def on_privnotice(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a notice to the user is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    thread_print_timestamped(
      f"Received NOTICE to {msg.channel}: {msg.message}"
    )
  # ----------------------------------------------------------------------------

  def on_action(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a CTCP ACTION message is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_message(msg)
    # thread_print(f"Received ACTION to {msg.channel}: {msg.message}")
  # ----------------------------------------------------------------------------

  def on_clearchat(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a CLEARCHAT notice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    banned_user = msg.message
    ban_duration = msg.tags.get('ban-duration', None)
    ban_msg: str = msg.message
    if msg.tags.get('target-user-id', None):
      ban_duration = (
        f"timed out for {ban_duration} seconds"
        if ban_duration
        else 'permanently banned'
      )
      ban_msg = f"{banned_user} has been {ban_duration}"
    thread_print_timestamped(
      f"Received CLEARCHAT to {msg.channel}: {ban_msg}"
    )
  # ----------------------------------------------------------------------------

  def on_clearmsg(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a CLEARMSG notice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    thread_print_timestamped(
      f"Received CLEARMSG to {msg.channel}: {msg.message}"
    )
  # ----------------------------------------------------------------------------

  def on_globaluserstate(
    self,
    connection: ServerConnection,
    event: Event
  ) -> None:
    '''
    IRC EVENT (executes when a GLOBALUSERSTATE notice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    thread_print_timestamped(
      f"Received GLOBALUSERSTATE to {msg.channel}: {msg.message}"
    )
  # ----------------------------------------------------------------------------

  def on_hosttarget(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a HOSTTARGET notice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    thread_print_timestamped(
      f"Received HOSTTARGET to {msg.channel}: {msg.message}"
    )
  # ----------------------------------------------------------------------------

  def on_reconnect(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a RECONNECT notice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    thread_print_timestamped(
      f"Received RECONNECT to {msg.channel}: {msg.message}"
    )
  # ----------------------------------------------------------------------------

  def on_roomstate(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a ROOMSTATE notice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    # thread_print(f"Received ROOMSTATE to {msg.channel}: {msg.message}")
  # ----------------------------------------------------------------------------

  def on_userstate(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a USERSTATE notice is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_notice(msg)
    # thread_print(f"Received USERSTATE to {msg.channel}: {msg.message}")
  # ----------------------------------------------------------------------------

  def on_whisper(self, connection: ServerConnection, event: Event) -> None:
    '''
    IRC EVENT (executes when a whisper message is received from server)

    Relevant event data is contained in `event` and needs some touch-up
    before being passed on to the rest of the application.
    '''
    msg: ChatMessage = ChatMessage.from_event(event, parent=self)
    GlobalData.Session.Chat.log_message(msg)
    thread_print_timestamped(
      f"Received WHISPER from {msg.user}: {msg.message}"
    )
  # ----------------------------------------------------------------------------

  def send_message(self, channel: str, message: str) -> bool:
    '''
    Send a `message` to the chosen `channel` (if rate limits allow).

    Don't rely on this function to send the message in the first place.

    Return `True` on success, `False` if message hasn't been sent.
    '''
    if time() - self.last_message_time > self.message_interval:
      self.send_priority_message(channel, message)
      return True
    return False
  # ----------------------------------------------------------------------------

  def send_priority_message(self, channel: str, message: str) -> None:
    '''
    Send a `message` to the chosen `channel` (ignore rate limits).

    This function will ignore any rate limits and just send the message
    anyways.

    Be cautious, because you are responsible for not getting
    your bot forcibly disconnected for spamming!
    '''
    # ignore last_message_time check
    self.connection.privmsg(channel, message)
    self.last_message_time = time()
  # ----------------------------------------------------------------------------

  def queue_message(self, channel: str, message: str) -> None:
    '''
    Send a `message` to the chosen `channel` (when rate limits allow).

    The message could be sent immediately, any time after, or never
    (if the bot disconnects before the message queue can be emptied).
    Don't use this function, if you need the message out there immediately!
    '''
    self.message_queue.append((channel, message))
  # ----------------------------------------------------------------------------

  def create_thread(self) -> None:
    '''
    Create thread.
    '''
    self.thread = Thread(
      target=self.start_and_check,
      daemon=True
    )
  # ----------------------------------------------------------------------------

  def start_thread(self) -> None:
    '''
    Start thread.
    '''
    self.thread.start()
  # ----------------------------------------------------------------------------

  def stop_thread(self) -> None:
    '''
    Stop thread.
    '''
    self.stop_bot()
# ==================================================================================================
