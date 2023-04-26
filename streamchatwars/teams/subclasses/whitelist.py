'''
This module provides a Team subclass that only accepts user that
are either in its whitelist or have been manually assigned to the
Team by a chat command.
'''

# native imports


# native imports
from typing import Any

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..team import Team


# ==================================================================================================
class Whitelist_Team(Team):
  '''
  Team subclass that only allows joining from users in whitelist.
  '''
  def __init__(
    self,
    name: str = "WhitelistOnly",
    **kwargs: Any
  ) -> None:
    '''
    Team subclass that only allows joining from users in whitelist.
    '''
    super().__init__(name=name, **kwargs)
  # ----------------------------------------------------------------------------

  def blocked_from_team(self, msg: AbstractChatMessage) -> bool:
    '''
    Kick out any member that bets on the opposite team.
    '''
    if super().blocked_from_team(msg):
      # short circuit: Another team in the chain already denied membership
      return True
    if not (
      msg.user in self.members  # not member of this team
      or msg in self.user_whitelist  # not on whitelist either
    ):
      return True
    return False
# ==================================================================================================


_EXPORT_CLASSES_: list[type[Team]] = [
  Whitelist_Team,
]
