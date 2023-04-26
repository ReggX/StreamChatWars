'''
This module provides multiple mutually-exclusive Prediction Team classes
that decide membership based on Twitch Predicitions and will kick out any
users that fulfill the criteria of another Prediction class.
'''

# native imports
from re import Match
from typing import Any

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..._interfaces._team import TeamCreationError
from ..._shared.constants import PREDICTION_NUMBER_REGEX
from ..._shared.enums import Quadstate
from ..._shared.global_data import GlobalData
from ..._shared.helpers_color import ColorText
from ..._shared.helpers_print import thread_print
from ..team import Team


# ==================================================================================================
class PredictionBlue_Team(Team):
  '''
  Team subclass that collects members based on Twitch Predictions (Blue).
  '''
  def __init__(
    self,
    name: str = "Blue",
    **kwargs: Any
  ) -> None:
    '''
    Team subclass that collects members based on Twitch Predictions (Blue).
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
    if "predictions/pink" in msg.tags['badges']:
      if msg.user in self.members:
        # kick out any illegitimate members
        self.members.discard(msg.user)
        GlobalData.Users.discard(msg.user)
      return True
    return False
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Allow `msg` on team if its prediction badge has the correct color.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    if "predictions/blue" in msg.tags['badges']:
      return Quadstate.MaybeTrue
    return Quadstate.AbsolutelyFalse
# ==================================================================================================


# ==================================================================================================
class PredictionPink_Team(Team):
  '''
  Team subclass that collects members based on Twitch Predictions (Pink).
  '''
  def __init__(
    self,
    name: str = "Pink",
    **kwargs: Any
  ) -> None:
    '''
    Team subclass that collects members based on Twitch Predictions (Pink).
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
    if "predictions/blue" in msg.tags['badges']:
      if msg.user in self.members:
        # kick out any illegitimate members
        self.members.discard(msg.user)
        GlobalData.Users.discard(msg.user)
      return True
    return False
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Allow `msg` on team if its prediction badge has the correct color.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    if "predictions/pink" in msg.tags['badges']:
      return Quadstate.MaybeTrue
    return Quadstate.AbsolutelyFalse
# ==================================================================================================


# ==================================================================================================
class PredictionNone_Team(Team):
  '''
  Team subclass that collects members based on Twitch Predictions
  (No Prediction placed).
  '''
  def __init__(
    self,
    name: str = "NoBet",
    **kwargs: Any
  ) -> None:
    '''
    Team subclass that collects members based on Twitch Predictions
    (No Prediction placed).
    '''
    super().__init__(name=name, **kwargs)
  # ----------------------------------------------------------------------------

  def blocked_from_team(self, msg: AbstractChatMessage) -> bool:
    '''
    Kick out any member that has placed bets.
    '''
    if super().blocked_from_team(msg):
      # short circuit: Another team in the chain already denied membership
      return True
    if (
      "predictions/blue" in msg.tags['badges']
      or "predictions/pink" in msg.tags['badges']
    ):
      if msg.user in self.members:
        # kick out any illegitimate members
        self.members.discard(msg.user)
        GlobalData.Users.discard(msg.user)
      return True
    return False
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Allow `msg` on team if it has NO prediction badge.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    if "predictions/" not in msg.tags['badges']:
      return Quadstate.MaybeTrue
    return Quadstate.AbsolutelyFalse
# ==================================================================================================


# ==================================================================================================
class PredictionNumber_Team(Team):
  '''
  Team subclass that collects members based on Twitch Predictions (Number).
  '''
  def __init__(
    self,
    *,
    name: str = "PredictionNumber",
    number: int = 0,  # Invalid default value by design
    **kwargs: Any
  ) -> None:
    '''
    Team subclass that collects members based on Twitch Predictions (Number).
    '''
    super().__init__(name=name, **kwargs)
    if not number or number < 1 or number > 10:
      thread_print(ColorText.error(
        f"Missing/Invalid parameter 'number' for Team {self.name!r}!"
      ))
      raise TeamCreationError
    self.number = number
  # ----------------------------------------------------------------------------

  def blocked_from_team(self, msg: AbstractChatMessage) -> bool:
    '''
    Kick out any member that bets on the opposite team.
    '''
    if super().blocked_from_team(msg):
      # short circuit: Another team in the chain already denied membership
      return True
    if "predictions/" in msg.tags['badges']:
      mo: Match[str] | None = PREDICTION_NUMBER_REGEX.match(msg.tags['badges'])
      if mo is not None and mo.group(1) != str(self.number):
        if msg.user in self.members:
          # kick out any illegitimate members
          self.members.discard(msg.user)
          GlobalData.Users.discard(msg.user)
        return True
    return False
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Allow `msg` on team if its prediction badge has the correct number.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    if "predictions/" in msg.tags['badges']:
      mo: Match[str] | None = PREDICTION_NUMBER_REGEX.match(msg.tags['badges'])
      if mo is not None and mo.group(1) == str(self.number):
        return Quadstate.MaybeTrue
    return Quadstate.AbsolutelyFalse
# ==================================================================================================


_EXPORT_CLASSES_: list[type[Team]] = [
  PredictionBlue_Team,
  PredictionPink_Team,
  PredictionNone_Team,
  PredictionNumber_Team,
]
