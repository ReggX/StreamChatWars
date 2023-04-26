'''
This module provides a Team class with the explicit intent of
not doing anything.
Rejects all users unless whitelisted or assigned.
'''

# native imports
from time import sleep
from typing import Any

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..._shared.enums import Quadstate
from ..team import Team


# ==================================================================================================
class None_Team(Team):
  '''
  Team subclass with the intent of not doing anything, regardless of actionset.
  '''
  def __init__(
    self,
    name: str = "NoTeam",
    **kwargs: Any
  ) -> None:
    '''
    Team subclass with the intent of not doing anything, regardless of
    actionset.
    '''
    super().__init__(name=name, **kwargs)
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Only accepts existing members and whitelist.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    return Quadstate.AbsolutelyFalse  # Don't vouch for anybody
  # ----------------------------------------------------------------------------

  def continously_translate_messages(self) -> None:
    '''
    Do nothing, actionset doesn't matter
    '''
    while self.keep_running:
      sleep(0.1)
  # ----------------------------------------------------------------------------

  def continously_execute_actions(self) -> None:
    '''
    Do nothing, actionset doesn't matter
    '''
    while self.keep_running:
      sleep(0.1)
# ==================================================================================================


_EXPORT_CLASSES_: list[type[Team]] = [
  None_Team,
]
