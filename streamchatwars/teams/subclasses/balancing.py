'''
This module provides a Team subclass that balances its members with
all other instances of the same subclass, trying to reach equal numbers
of members between all of them.
'''

# native imports


# native imports
from typing import Any

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..._interfaces._team import AbstractTeam
from ..._shared.enums import Quadstate
from ..._shared.global_data import GlobalData
from ..team import Team


# ==================================================================================================
class Balancing_Team(Team):
  '''
  A Team subclass with the intent to balance members between all its instances.
  '''
  def __init__(
    self,
    name: str = "AutoBalancing",
    **kwargs: Any
  ) -> None:
    '''
    A Team subclass with the intent to balance members between all its
    instances.
    '''
    super().__init__(name=name, **kwargs)
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Aside from the default (members, whitelist), this function will only
    return `True` if its associated team is the `Balancing_Team` with the
    lowest member count.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    # Default to self for the least member team (we need any starting point)
    team: AbstractTeam
    for team in GlobalData.Teams.get_all_teams():
      if (
        # Find an unhidden Balancing team with less members
        isinstance(team, Balancing_Team)
        and not team.hidden
        and len(team.members) < len(self.members)
      ):
        # Found a team with less members, can't vouch for membership
        return Quadstate.AbsolutelyFalse
    # Current team is still the least member team -> vouch for membership
    return Quadstate.MaybeTrue
# ==================================================================================================


_EXPORT_CLASSES_: list[type[Team]] = [
  Balancing_Team,
]
