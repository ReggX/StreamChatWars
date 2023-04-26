'''
Team Interface
Provide an Abstract Base Class as reference for other modules.
'''

# native imports
from abc import ABC
from abc import abstractmethod
from collections import deque
from collections.abc import Sequence
from functools import partial
from threading import Lock
from threading import Thread
from typing import Any

# internal imports
from .._shared.types import TeamSnapshotDict
from ._actionset import AbstractActionset
from ._chatbot import AbstractMessageSender
from ._chatmsg import AbstractChatMessage
from ._thread_support import AbstractThreadSupport
from ._userlist import AbstractUserList


# ==================================================================================================
class TeamCreationError(Exception):
  pass
# ==================================================================================================


# ==================================================================================================
class AbstractTeam(AbstractThreadSupport, ABC):
  '''Interface class for Teams'''
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

  @abstractmethod
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
    pass  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def add_message(self, msg: AbstractChatMessage) -> None:
    '''
    add `msg` to queue and its user to the member list
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def belongs_to_team(self, msg: AbstractChatMessage) -> bool:
    '''
    Check if Message belongs to this Team,
    intended for INCLUSION criteria.
    Overridable with criteria for specific Team.

    A return value of `None` indicates that subclasses have to handle
    the return value themselves!
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def blocked_from_team(self, msg: AbstractChatMessage) -> bool:
    '''
    Check if Message/User are denied membership on Team,
    intended for EXCLUSION criteria. (True=blocked, False=not blocked)
    Overridable with criteria for specific Team.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def join_team(self, user: str) -> bool:
    '''
    Add `user` to team's member list
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def leave_team(self, user: str) -> bool:
    '''
    Remove `user` from team's member list.

    Return `True` if user was a member before, `False` otherwise
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def create_snapshot(self) -> TeamSnapshotDict:
    '''
    Store runtime data in snapshot and return as dict.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def restore_snapshot(self, team_snapshot: TeamSnapshotDict) -> None:
    '''
    Load snapshot data and overwrite existing data.
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
