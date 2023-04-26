'''
Team base module
Serves as the base for every module in teams sub-package.
Contains some additional shared variables and functions.
'''

# native imports
from collections import deque
from collections.abc import Sequence
from functools import partial
from threading import Lock
from threading import Thread
from time import sleep
from typing import Any

# internal imports
from .._interfaces._actionset import AbstractActionset
from .._interfaces._chatbot import AbstractMessageSender
from .._interfaces._chatmsg import AbstractChatMessage
from .._interfaces._team import AbstractTeam
from .._interfaces._userlist import AbstractUserList
from .._shared.constants import EMPTY_QUEUE_SLEEP_DURATION
from .._shared.enums import Quadstate
from .._shared.global_data import GlobalData
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from .._shared.types import TeamSnapshotDict
from ..actionsets.actionset import Actionset
from ..userdata.userlist import UserList


# ==================================================================================================
class Team(AbstractTeam):
  '''
  Base class for Teams
  '''
  # Instance variables:
  name: str
  channels: set[str]
  actionset: AbstractActionset
  hidden: bool
  use_random_inputs: bool
  joinable: bool
  leavable: bool
  exclusive: bool
  spam_protection: bool
  user_whitelist: AbstractUserList
  user_blacklist: AbstractUserList
  members: set[str]
  keep_running: bool
  bot: AbstractMessageSender | None
  '''Back-reference to Chatbot for messaging purposes'''
  message_queue: deque[AbstractChatMessage]
  message_queue_lock: Lock
  action_queue: deque[tuple[AbstractChatMessage, partial[None]]]
  action_queue_lock: Lock
  translation_thread: Thread
  execution_thread: Thread
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    name: str = "",
    *,
    channels: set[str] | None = None,
    actionset: AbstractActionset | None = None,
    hidden: bool = False,
    queue_length: int = 10,
    use_random_inputs: bool = False,
    joinable: bool = False,
    leavable: bool = False,
    exclusive: bool = True,
    user_whitelist: Sequence[str] | None = None,
    user_blacklist: Sequence[str] | None = None,
    spam_protection: bool = True,
    **kwargs: Any  # Additional params only used by specifc subclasses
  ) -> None:
    '''
    Initializes all necessary object properties with reasonable
    default values, intendend to be usable as `super().__init__()`
    for every subclasss.
    '''
    if name == "":
      raise ValueError("Team name must be provided!")
    if not channels:  # len > 0
      raise ValueError("You need to specifiy at least one channel")
    if not isinstance(actionset, Actionset):
      raise ValueError("Actionset must be a valid Actionset object")

    self.name = name
    self.channels = channels
    self.actionset = actionset
    self.hidden = hidden
    self.use_random_inputs = use_random_inputs
    self.joinable = joinable
    self.leavable = leavable
    self.exclusive = exclusive
    self.spam_protection = spam_protection
    self.user_whitelist = UserList()
    self.user_blacklist = UserList()
    entry: str
    if user_whitelist:
      for entry in user_whitelist:
        self.user_whitelist.add_to_list(entry, self.channels)
    if user_blacklist:
      for entry in user_blacklist:
        self.user_blacklist.add_to_list(entry, self.channels)

    self.members = set()
    self.keep_running = True

    self.message_queue = deque(maxlen=queue_length)
    self.message_queue_lock = Lock()
    self.action_queue = deque(maxlen=queue_length)
    self.action_queue_lock = Lock()

    self.bot = None
  # ----------------------------------------------------------------------------

  def add_message(self, msg: AbstractChatMessage) -> None:
    '''
    add `msg` to queue and its user to the member list
    '''
    with self.message_queue_lock:
      if self.spam_protection:
        for existing_message in self.message_queue:
          if (
            msg.user == existing_message.user
            and msg.message == existing_message.message
          ):
            # don't add message if it's spammed by the same user
            return
      self.message_queue.append(msg)
    if self.exclusive and msg.user not in self.members:
      self.members.add(msg.user)
      GlobalData.Users.add(msg.user, self)
  # ----------------------------------------------------------------------------

  def belongs_to_team(self, msg: AbstractChatMessage) -> bool:
    '''
    Check if Message belongs to this Team,
    intended for INCLUSION criteria, vouching that `msg` belongs on this team.
    Overridable with criteria for specific Team and its private variant
    `_belongs_to_team()`.
    '''
    return bool(self._belongs_to_team(msg))
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Check if Message belongs to this Team,
    intended for INCLUSION criteria, vouching that `msg` belongs on this team.
    Overridable with criteria for specific Team.

    Subclasses overriding this method should start with the following snippet:

    ```python
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    ```
    '''
    if (
      msg.user in self.members  # already member of this team
      or msg in self.user_whitelist  # whitelist -> skip Team-specific checks
    ):
      return Quadstate.AbsolutelyTrue
    return Quadstate.MaybeFalse
  # ----------------------------------------------------------------------------

  def blocked_from_team(self, msg: AbstractChatMessage) -> bool:
    '''
    Check if Message/User are denied membership on Team,
    intended for EXCLUSION criteria. (True=blocked, False=not blocked)
    Overridable with criteria for specific Team.

    Subclasses overriding this method should start with the following snippet:

    ```python
    if super().blocked_from_Team(msg):
      # short circuit: Another team in the chain already denied membership
      return True
    ```
    '''
    if (
      # blacklisted user
      msg in self.user_blacklist
      or (
        # member of other exclusive team
        self.exclusive
        and (other_team := GlobalData.Users.get_team(msg.user)) is not None
        and other_team is not self
      )
    ):
      if msg.user in self.members:
        # kick out any illegitimate members
        self.members.discard(msg.user)
        GlobalData.Users.discard(msg.user)
      return True
    return False
  # ----------------------------------------------------------------------------

  def join_team(self, user: str) -> bool:
    '''
    Add `user` to team's member list
    '''
    if self.joinable and self.exclusive:
      self.members.add(user)
      GlobalData.Users.add(user, self)
      return True
    return False
  # ----------------------------------------------------------------------------

  def leave_team(self, user: str) -> bool:
    '''
    Remove `user` from team's member list.

    Return `True` if user was a member before and isn't now, `False` otherwise.
    '''
    if self.leavable:
      try:
        self.members.remove(user)
        GlobalData.Users.discard(user)
        return True
      except KeyError:
        pass  # drop through to return False
    return False
  # ----------------------------------------------------------------------------

  def create_snapshot(self) -> TeamSnapshotDict:
    '''
    Store runtime data in snapshot and return as dict.
    '''
    team_snapshot: TeamSnapshotDict = {
      'members':  list(self.members),
      'whitelist': self.user_whitelist.export_dict(),
      'blacklist': self.user_blacklist.export_dict(),
      'macros': self.actionset.get_macro_dict()
    }
    return team_snapshot
  # ----------------------------------------------------------------------------

  def restore_snapshot(self, team_snapshot: TeamSnapshotDict) -> None:
    '''
    Load snapshot data and overwrite existing data.
    '''
    self.members = set(team_snapshot.get("members", []))
    self.user_whitelist.import_dict(team_snapshot.get("whitelist", {}))
    self.user_blacklist.import_dict(team_snapshot.get("blacklist", {}))
    self.actionset.set_macro_dict(team_snapshot.get("macros", {}))
  # ----------------------------------------------------------------------------

  def continously_translate_messages(self) -> None:
    '''
    Continously translate messages from message_queue and feed action_queue.
    '''
    while self.keep_running:
      self._translate_queued_message()
  # ----------------------------------------------------------------------------

  def _translate_queued_message(self) -> None:
    '''
    Translate message from message_queue and store them in action_queue
    '''
    try:
      with self.message_queue_lock:
        msg: AbstractChatMessage = self.message_queue.pop()  # pop most recent
        func: partial[None] | None = (
          self.actionset.translate_user_message_to_action(msg)
        )
        if func is None:
          # Release and reaquire lock to try again,
          # give producers a chance to update the queue
          return
        # not None:
        with self.action_queue_lock:
          self.action_queue.append((msg, func))
        # discard rest of queue after we got a valid function
        self.message_queue.clear()
    except IndexError:
      sleep(EMPTY_QUEUE_SLEEP_DURATION)
  # ----------------------------------------------------------------------------

  def continously_execute_actions(self) -> None:
    '''
    Continously grab most recent translated message
    and send it to the input server.
    '''
    while self.keep_running:
      self._execute_queued_action()
  # ----------------------------------------------------------------------------

  def _execute_queued_action(self) -> None:
    '''
    Grab most recent translated message and send it to the input server.

    If the queue is empty, send a Callable from `empty_queue_action()`
    to the input server instead.
    '''
    try:
      with self.action_queue_lock:
        msg: AbstractChatMessage
        func: partial[None]
        msg, func = self.action_queue.pop()  # pop most recent
        thread_print(
          f"{msg.user} [{self.name}|{self.actionset.name}|"
          f"{self.actionset.player_index}]: {msg.message.lower()}"
        )
        GlobalData.Session.Chat.log_executed_message(msg, self)
        # discard rest of queue after we got a valid function
        self.action_queue.clear()
    except IndexError:
      # queue empty
      func = self.empty_queue_action()

    try:
      self.actionset.input_server.execute(func)
    except ConnectionRefusedError:
      self.keep_running = False
      thread_print(ColorText.error(
        f"Remote connection refused, stopping input handling for {self.name}"
      ))
  # ----------------------------------------------------------------------------

  def empty_queue_action(self) -> partial[None]:
    '''
    Called when `_execute_queued_action()` encounters an empty message queue.

    Will return a random action if `use_random_inputs` is enabled
    and random actions are currently active (set by file event).
    Defaults to sleeping for 0.1 seconds otherwise.
    '''
    if self.use_random_inputs and GlobalData.EventStates.random_action():
      return self.actionset.random_action()
    else:
      return partial(sleep, EMPTY_QUEUE_SLEEP_DURATION)
  # ----------------------------------------------------------------------------

  def create_thread(self) -> None:
    '''
    Create Team-specific Thread objects.
    '''
    self.translation_thread = Thread(
      target=self.continously_translate_messages,
      daemon=True
    )
    self.execution_thread = Thread(
      target=self.continously_execute_actions,
      daemon=True
    )
  # ----------------------------------------------------------------------------

  def start_thread(self) -> None:
    '''
    Start Team-specific threads.
    '''
    self.translation_thread.start()
    self.execution_thread.start()
  # ----------------------------------------------------------------------------

  def stop_thread(self) -> None:
    '''
    Stop Team-specific threads.
    '''
    self.keep_running = False
# ==================================================================================================
