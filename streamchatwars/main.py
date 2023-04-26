'''
streamchatwars package entry point (actual code)
'''

# native imports
import asyncio
import sys
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from json import JSONDecodeError
from threading import Thread
from threading import enumerate as enumerate_threads
from time import sleep

# pip imports
from jsonschema import ValidationError
from keyboard import is_pressed
from keyboard import parse_hotkey

# internal imports
from ._interfaces._actionset import ActionsetValidationError
from ._interfaces._input_server import InputServerConnectionFailed
from ._interfaces._team import TeamCreationError
from ._shared.constants import FILE_EVENT_WAIT_TIME
from ._shared.constants import THREAD_TIMEOUT
from ._shared.constants import ExitCode
from ._shared.global_data import DuplicateTeamNameError
from ._shared.global_data import GlobalData
from ._shared.helpers_color import ColorText
from ._shared.helpers_print import thread_print
from ._shared.primitive_types import seconds
from ._shared.types import ConfigDict
from ._shared.types import CredentialDict
from ._shared.types import TwitchAPICredentialDict
from ._shared.types import TwitchChatCredentialDict
from .chat.chatbot import ChatBot
from .chat.commands import set_available_commands
from .config.config import Command_Settings
from .config.config import Event_Settings
from .config.config import Hotkey_Settings
from .config.config import IRC_Settings
from .config.config import Sessionlog_Settings
from .config.config import TTS_Settings
from .config.config import build_operator_list
from .config.config import build_teams
from .config.config import extract_command_settings
from .config.config import extract_event_settings
from .config.config import extract_irc_settings
from .config.config import extract_sessionlog_settings
from .config.config import extract_tts_settings
from .config.config import read_json_configs
from .config.json_utils import InvalidCredentialsError
from .events.event_handler import GlobalEventHandler
from .session.dump import SessionDumper
from .tts.tts import TTS
from .twitch.api import Twitch_API


# ------------------------------------------------------------------------------
def join_all_threads(
  *thread_list: Thread,
  timeout: seconds = THREAD_TIMEOUT
) -> None:
  '''
  join all threads in thread_list at the same time, reducing effective
  maximum timeout.
  '''
  # The irony of starting worker threads to join other threads is not lost on me
  with ThreadPoolExecutor(max_workers=len(thread_list)) as executor:
    async def join_async(t: Thread) -> None:
      nonlocal executor, timeout
      await asyncio.get_running_loop().run_in_executor(
        executor,
        t.join,
        timeout
      )

    async def join_all_async(thread_list: Sequence[Thread]) -> None:
      await asyncio.gather(*[join_async(t) for t in thread_list])

    asyncio.run(join_all_async(thread_list))
# ------------------------------------------------------------------------------


# ==================================================================================================
class MainData:
  '''
  Data container for all of `main()`'s  variables and subroutines.

  Intended to be only used for its primary method: `main()`

  All other methods and attributes should only be accessed by tests, which
  cleanup their side-effects.
  '''
  # Instance Variables:
  config: ConfigDict
  credentials: CredentialDict
  sessionlog_settings: Sessionlog_Settings
  sessionlog_enabled: bool
  sessionfile_basename: str
  event_settings: Event_Settings
  global_event_handler: GlobalEventHandler
  channel_set: set[str]
  bot: ChatBot
  twitch_api: Twitch_API
  chatgpt_enabled: bool
  tts_settings: TTS_Settings
  tts_enabled: bool
  tts_manager: TTS
  session_dumper: SessionDumper
  periodic_dump_enabled: bool

  def _read_args_configs(self) -> None:
    '''
    Read and validate JSON configuration files, return Mappings.

    Update config and/or snapshot schema file if outdated.
    '''
    config_arg: str | None = sys.argv[1] if len(sys.argv) > 1 else None
    credentials_arg: str | None = sys.argv[2] if len(sys.argv) > 2 else None
    try:
      self.config, self.credentials = read_json_configs(
        config_arg,
        credentials_arg
      )
    except (OSError, JSONDecodeError, ValidationError):
      # printed in subroutine, just exit
      sys.exit(ExitCode.INVALID_CONFIG)
  # ----------------------------------------------------------------------------

  def _set_sessionlog_settings(self) -> None:
    '''
    Extract sessionlog settings from config and enable session logging if set
    in config.
    '''
    self.sessionlog_settings = extract_sessionlog_settings(self.config)
    GlobalData.Session.start()
    GlobalData.Session.Console.enable_consolelog(
      self.sessionlog_settings.enable_consolelog
    )
    GlobalData.Session.Chat.enable_chatlog(
      self.sessionlog_settings.enable_chatlog
    )
    GlobalData.Session.ChannelPoints.enable_channelpointlog(
      self.sessionlog_settings.enable_channelpointlog
    )
    self.sessionlog_enabled: bool = any([
      self.sessionlog_settings.enable_consolelog,
      self.sessionlog_settings.enable_chatlog,
      self.sessionlog_settings.enable_channelpointlog,
    ])
    timestamp: str = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]
    self.sessionfile_basename = f"session_{timestamp}"
  # ----------------------------------------------------------------------------

  def _set_command_settings(self) -> None:
    '''
    Extract command settings from config and limit available commands if set
    in config.
    '''
    command_settings: Command_Settings = extract_command_settings(self.config)
    # change chat command prefix
    GlobalData.Prefix.Command.set(command_settings.prefix)
    set_available_commands(  # Limit available commands if set in config
      mode=command_settings.mode,
      whitelist=command_settings.whitelist,
      blacklist=command_settings.blacklist
    )
  # ----------------------------------------------------------------------------

  def _set_event_settings(self) -> None:
    '''
    Extract Event settings and validate hotkey functionality.
    '''
    self.event_settings: Event_Settings = extract_event_settings(self.config)
    hotkey_settings: Hotkey_Settings = self.event_settings.hotkeys
    hotkeys: list[str] = [
      hotkey_settings.failsafe,
      hotkey_settings.accept_input,
      hotkey_settings.random_action
    ]
    for hotkey in hotkeys:
      if hotkey:
        try:
            parse_hotkey(hotkey)
        except ValueError as e:
          thread_print(ColorText.error(
            f"Invalid hotkey! Failed to parse: {hotkey!r}\n"
            f"{e.args[0]}"
          ))
          sys.exit(ExitCode.INVALID_HOTKEY)
  # ----------------------------------------------------------------------------

  def _create_tts_manager(self) -> None:
    '''
    Create TTS Manager.
    '''
    self.tts_settings = extract_tts_settings(self.config)
    self.tts_enabled = self.tts_settings.enabled
    if self.tts_enabled:
      self.tts_manager = TTS(
        voice_ids=self.tts_settings.voice_ids,
        rate=self.tts_settings.rate,
        volume=self.tts_settings.volume,
        number_of_channels=self.tts_settings.number_of_channels,
        max_duration=self.tts_settings.max_duration,
      )
      GlobalData.TTSQueue.assign_queue_object(self.tts_manager)
    GlobalData.TTSQueue.enable_tts(self.tts_enabled)
  # ----------------------------------------------------------------------------

  def _create_global_event_handler(self) -> None:
    '''
    Create FileEventHandler based on settings in config.
    '''
    self.global_event_handler = GlobalEventHandler(self.event_settings)
  # ----------------------------------------------------------------------------

  def _create_teams(self) -> None:
    '''
    Create all teams, including their Actionsets and InputServers.
    '''
    try:
      build_teams(self.config)
    except InputServerConnectionFailed as e:
      thread_print(ColorText.error(f"{e.args[0]}\nAborting..."))
      sys.exit(e.errno)
    except DuplicateTeamNameError as e:
      thread_print(ColorText.error(f"{e.args[0]}\nAborting..."))
      sys.exit(ExitCode.DUPLICATE_TEAM_NAME)
    except ActionsetValidationError as e:
      thread_print(ColorText.error(
        f"Actionset failed validation:\n{e.args[0]}\nAborting..."
      ))
      sys.exit(ExitCode.ACTIONSET_VALIDATION_FAILURE)
    except TeamCreationError:
      thread_print(ColorText.error(
        "Team creation failed!\nAborting..."
      ))
      sys.exit(ExitCode.TEAM_CREATION_FAILURE)
    # Enable Teamlog in Sessionlog once teams are created
    GlobalData.Session.Teams.init_teamlogs(
      self.sessionlog_settings.enable_chatlog
    )
  # ----------------------------------------------------------------------------

  def _extract_channel_set(self) -> None:
    '''
    Extract channels from teams and store them in channel_set attribute.
    '''
    self.channel_set: set[str] = set()
    for team in GlobalData.Teams.get_all_teams():
      self.channel_set.update(team.channels)
  # ----------------------------------------------------------------------------

  def _create_bot(self) -> None:
    '''
    Create Chatbot based on settings in config and credentials.
    '''
    # create chat bot based on config
    chat_credentials: TwitchChatCredentialDict | None
    chat_credentials = self.credentials.get("TwitchChat", None)
    if not chat_credentials:
      thread_print(ColorText.error(
        "Missing Credentials to access chat server!\n"
        "Please add chat credentials to the credential file listed above!"
      ))
      sys.exit(ExitCode.MISSING_CHAT_CREDENTIALS)
    try:
      irc_setting: IRC_Settings = extract_irc_settings(
        self.config,
        chat_credentials,
        self.channel_set
      )
    except InvalidCredentialsError:
      thread_print(ColorText.error(
        "Invalid Credentials to access chat server!\n"
        "Please check your credentials in the credential file listed above!"
      ))
      sys.exit(ExitCode.INVALID_CHAT_CREDENTIALS)
    self.bot: ChatBot = ChatBot(irc_setting)
  # ----------------------------------------------------------------------------

  def _create_api_client(self) -> None:
    '''
    Create Twitch API Client based on credentials
    '''
    api_credentials: TwitchAPICredentialDict | None
    api_credentials = self.credentials.get("TwitchAPI", None)
    if not api_credentials:
      thread_print(ColorText.error(
        "Missing Credentials to access Twitch API!\n"
        "Please add API credentials to the credential file listed above!"
      ))
      sys.exit(ExitCode.MISSING_API_CREDENTIALS)
    try:
      self.twitch_api = Twitch_API(api_credentials, self.channel_set)
    except InvalidCredentialsError:
      thread_print(ColorText.error(
        "Invalid Credentials to access Twitch API!\n"
        "Please check your credentials in the credential file listed above!"
      ))
      sys.exit(ExitCode.INVALID_API_CREDENTIALS)
  # ----------------------------------------------------------------------------

  def _create_session_dumper(self) -> None:
    '''
    Create SessionDumper based on settings in config.
    '''
    self.periodic_dump_enabled = (
      self.sessionlog_settings.enable_periodic_dumps
      and self.sessionlog_enabled
    )
    dumping_interval: seconds = 999999999
    counter_cap: int = 0
    if self.periodic_dump_enabled:
      dumping_interval = self.sessionlog_settings.dumping_interval
      counter_cap = self.sessionlog_settings.counter_cap
      thread_print(ColorText.info(
        f"Enabling Session Dumper with interval {dumping_interval} seconds"
      ))

    self.session_dumper = SessionDumper(
      self.config,
      dumping_interval=dumping_interval,
      file_basename=self.sessionfile_basename,
      counter_cap=counter_cap
    )
  # ----------------------------------------------------------------------------

  def _create_threads(self) -> None:
    '''
    Create Thread objects for Teams, GlobalEventHandler and Chatbot.
    '''
    # create threads for every team's command handling
    for team in GlobalData.Teams.get_all_teams():
      team.bot = self.bot
      team.create_thread()

    # create thread for Eventhandler
    self.global_event_handler.create_thread()

    # create thread for Chat Bot
    self.bot.create_thread()

    # create thread for Twitch API
    self.twitch_api.create_thread()

    # create thread for TTS manager
    if self.tts_enabled:
      self.tts_manager.create_thread()

    # create thread for Session Dumper
    if self.periodic_dump_enabled:
      self.session_dumper.create_thread()
  # ----------------------------------------------------------------------------

  def _print_hotkeys(self) -> None:
    '''
    Print information regarding hotkeys.
    '''
    hotkey_settings: Hotkey_Settings = self.event_settings.hotkeys
    colored_text: str = ColorText.error(' Ctrl+C ')
    thread_print(
      "Starting child threads and chat connection, "
      f"press {colored_text} in this window to exit."
    )
    if hotkey_settings.failsafe:
      colored_text = ColorText.error(f' {hotkey_settings.failsafe} ')
      thread_print(
        f"Use Failsafe {colored_text} "
        "to abort execution globally in any window."
      )
    if hotkey_settings.accept_input:
      colored_text = ColorText.good(f' {hotkey_settings.accept_input} ')
      thread_print(
        f"Use Hotkey {colored_text} "
        "to toggle accepting/pausing input globally in any window."
      )
    if hotkey_settings.random_action:
      colored_text = ColorText.good(f' {hotkey_settings.random_action} ')
      thread_print(
        f"Use Hotkey {colored_text} "
        "to toggle executing/pausing random actions globally in any window."
      )
    if hotkey_settings.random_delay_plus:
      colored_text = ColorText.good(f' {hotkey_settings.random_delay_plus} ')
      thread_print(
        f"Use Hotkey {colored_text} "
        "to increase random action delay globally in any window."
      )
    if hotkey_settings.random_delay_minus:
      colored_text = ColorText.good(f' {hotkey_settings.random_delay_minus} ')
      thread_print(
        f"Use Hotkey {colored_text} "
        "to decrease random action delay globally in any window."
      )
  # ----------------------------------------------------------------------------

  def _start_threads(self) -> None:
    '''
    Start all threads.
    '''
    # start eventhandler threads
    self.global_event_handler.start_thread()
    # wait for a little while, so current File Event state is printed first
    sleep(FILE_EVENT_WAIT_TIME)

    for team in GlobalData.Teams.get_all_teams():
      team.start_thread()

    self.bot.start_thread()

    self.twitch_api.start_thread()

    if self.tts_enabled:
      self.tts_manager.start_thread()

    if self.periodic_dump_enabled:
      self.session_dumper.start_thread()
  # ----------------------------------------------------------------------------

  def _loop_with_failsafe(self) -> None:
    '''
    Keep the program looping as long as bot.keep_running is active.
    Check for hotkeys and execute actions if press is detected.
    '''
    hotkey_settings: Hotkey_Settings = self.event_settings.hotkeys
    # keep looping until stop signal is encountered
    while self.bot.keep_running:
      # Failsafe
      if hotkey_settings.failsafe and is_pressed(hotkey_settings.failsafe):
        thread_print(ColorText.error("Failsafe engaged! Aborting execution!"))
        sys.exit(ExitCode.FAILSAFE_ENGAGED)

      sleep(0.1)
  # ----------------------------------------------------------------------------

  def _stop_threads(self) -> None:
    '''
    Stop all threads (reverse starting order).
    '''
    thread_print(ColorText.warning("Exiting and cleaning up child threads..."))

    # Session Dumper
    if self.periodic_dump_enabled:
      self.session_dumper.stop_thread()
    # TTS Manager
    if self.tts_enabled:
      self.tts_manager.stop_thread()
    # Twitch API
    self.twitch_api.stop_thread()
    # Bot
    self.bot.stop_thread()
    # Teams
    team_threads_list: list[Thread] = []
    for team in GlobalData.Teams.get_all_teams():
      team_threads_list.extend(
        (team.translation_thread, team.execution_thread)
      )
      team.stop_thread()
    # Eventhandler
    self.global_event_handler.stop_thread()

    join_all_threads(
      *team_threads_list,
      self.global_event_handler.thread,
      self.bot.thread,
      self.twitch_api.pubsub_thread,
      timeout=THREAD_TIMEOUT
    )
  # ----------------------------------------------------------------------------

  def _export_session_data(self) -> None:
    '''
    Export session data if available.
    '''
    if self.sessionlog_enabled:
      thread_print("Exporting session information...")
      self.session_dumper.final_dump()
  # ----------------------------------------------------------------------------

  def _inform_termination(self) -> None:
    '''
    Inform user that lingering threads will be forcefully terminated.
    '''
    if self.global_event_handler.thread.is_alive():
      thread_print(ColorText.warning(
        "File Event Thread still alive, forcing termination"
      ))

    team_threads_list: list[Thread] = []
    for team in GlobalData.Teams.get_all_teams():
      team_threads_list.extend(
        (team.translation_thread, team.execution_thread)
      )

    if any([t.is_alive() for t in team_threads_list]):
      thread_print(ColorText.warning(
        "Team Thread still alive, forcing termination"
      ))

    if self.bot.thread.is_alive():
      thread_print(ColorText.warning(
        "Chatbot Thread still alive, forcing termination"
      ))

    if self.twitch_api.pubsub_thread.is_alive():
      thread_print(ColorText.warning(
        "Twitch API Thread still alive, forcing termination"
      ))

    remaining_threads: list[Thread] = enumerate_threads()
    if len(remaining_threads) > 1:
      thread_print(ColorText.warning(
        "Remaining Threads still alive:"
      ))
      for thread in remaining_threads:
        thread_print(ColorText.warning(f"  {thread.name}: {thread.ident}"))
  # ----------------------------------------------------------------------------

  def main(self) -> None:
    '''
    Entry point of StreamChatWars
    '''
    try:  # KeyboardInterrupt
      # Initialize colored print() with colorama (for legacy Windows terminals)
      ColorText.init()

      # Read config and credentials from files
      self._read_args_configs()

      # Set Sessionlog settings
      self._set_sessionlog_settings()

      # Set Command settings
      self._set_command_settings()

      # Set Hotkey settings
      self._set_event_settings()

      # Create TTS Manager
      self._create_tts_manager()

      # Use File Events if specified in the config
      self._create_global_event_handler()

      # Create all teams, including their Actionsets and InputServers
      self._create_teams()

      # Extract a combined list of channels from all teams
      self._extract_channel_set()

      # create UserList of users with operator privileges
      build_operator_list(self.config, self.channel_set)

      # create chat bot based on config
      self._create_bot()

      # create api client based on config
      self._create_api_client()

      # create session dumper based on config
      self._create_session_dumper()

      # create threads
      self._create_threads()

    except KeyboardInterrupt:
      thread_print(ColorText.error(
        "Aborted execution early!"
      ))
      sys.exit(ExitCode.ABORT_EARLY)

    try:  # KeyboardInterrupt
      # print hotkey information
      self._print_hotkeys()

      # start threads
      self._start_threads()

      # keep looping while checking for pressed hotkeys
      self._loop_with_failsafe()
    except KeyboardInterrupt:
      # Go to `finally:`
      pass
    finally:
      # start shutdown procedure for all threads
      self._stop_threads()

      # export sessionlog if it has been enabled
      self._export_session_data()

      # Tell the user that all lingering threads will be forcefully terminated
      self._inform_termination()

      thread_print(ColorText.done("Done! Have a good day :)"))
# ==================================================================================================


# ------------------------------------------------------------------------------
def main() -> None:
  '''
  Entry point of StreamChatWars
  '''
  main_data = MainData()
  main_data.main()
# ------------------------------------------------------------------------------


# ==================================================================================================
if __name__ == '__main__':
  main()
# ==================================================================================================
