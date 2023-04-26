'''
Userlist Interface
Provide an Abstract Base Class as reference for other modules.
'''

# native imports
from abc import ABC
from abc import abstractmethod

# internal imports
from .._shared.types import UserListDict
from ._chatmsg import AbstractChatMessage


# ==================================================================================================
class AbstractUserList(ABC):
  '''Interface class for UserList'''

  @abstractmethod
  def clear(self) -> None:
    '''
    Reset Userlist to its initialized state.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def add_to_list(
    self,
    entry: str,
    team_channel_set: set[str] | None = None
  ) -> None:
    '''
    Adds `entry` to UserList.

    * If `entry` is a special group token (`$group[chan]`), it will add
    `chan` (`team_channel_set` if no channel is specified) to the
    special subgroup `group` and invalidate the `known_users` and
    `excluded_users` sets.
    * Otherwise add `entry` to the `fixed_users` set.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def remove_from_list(
    self,
    entry: str,
    team_channel_set: set[str] | None = None
  ) -> None:
    '''
    Remove `entry` from UserList.

    * If `entry` is a special group token (`$group[chan]`), it will remove
    `chan` (`team_channel_list` if no channel is specified) from the
    special subgroup `group` and invalidate the `known_users` and
    `included_users` sets.
    * Otherwise remove `entry` from the `fixed_users` set.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def __contains__(self, item: AbstractChatMessage | str) -> bool:
    '''
    `in` operator, calls `message_in_list()` if `item` is a `ChatMessage`
    object, otherwise falls back on `user_in_list()`
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  def export_dict(self) -> UserListDict:
    '''
    Export Userlist instance data into simple dict for snapshot purposes.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  def import_dict(self, ul_dict: UserListDict) -> None:
    '''
    Import Userlist instance data from simple snapshot dict.
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
