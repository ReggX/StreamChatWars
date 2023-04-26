'''
This module provides a default implementation of the Team base class,
accepting every user (unless blacklisted or member of another team)
'''

# native imports


# native imports
from typing import Any

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..._shared.enums import Quadstate
from ..team import Team


# ==================================================================================================
class Default_Team(Team):
  '''
  Default Implementation of the Team base class.
  '''
  def __init__(
    self,
    name: str = "Default",
    **kwargs: Any
  ) -> None:
    '''
    Default Implementation of the Team base class.
    '''
    super().__init__(name=name, **kwargs)
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Accepts every message that isn't explicitly disallowed by its base class.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    return Quadstate.MaybeTrue  # Always allow membership
# ==================================================================================================


_EXPORT_CLASSES_: list[type[Team]] = [
  Default_Team,
]
