'''
This module provides a Team subclass that only allows users with names matching
the specified regular expression.
'''

# native imports


# native imports
from re import Pattern
from re import compile
from re import error as re_error
from typing import Any

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..._interfaces._team import TeamCreationError
from ..._shared.enums import Quadstate
from ..._shared.helpers_color import ColorText
from ..._shared.helpers_print import thread_print
from ..team import Team


# ==================================================================================================
class NameRegex_Team(Team):
  '''
  A Team subclass that only allows members that match its internal name regex.
  '''
  regex: Pattern[str]

  def __init__(
    self,
    name: str = "NameRegex",
    pattern: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Team subclass that only allows members that match its internal name regex.

    Requires the `pattern` argument, which will be compiled into a regular
    expression.

    Examples: `[a-m].*` for A Crew, `[n-z0-9].*` for Z Crew.
    '''
    super().__init__(name=name, **kwargs)
    if not pattern:
      thread_print(ColorText.error(
        f"Missing parameter 'pattern' for Team {self.name!r}!"
      ))
      raise TeamCreationError
    try:
      self.regex = compile(pattern)
    except re_error as e:
      thread_print(ColorText.error(
        f"Failed to compile regular expression for Team {self.name!r}:\n"
        f"Reason: {e.msg}"
      ))
      raise TeamCreationError from e
  # ----------------------------------------------------------------------------

  def _belongs_to_team(self, msg: AbstractChatMessage) -> Quadstate:
    '''
    Aside from the default (members, whitelist), this function will only
    return `True` if msg.user fits the internal regex.
    '''
    super_result: Quadstate = super()._belongs_to_team(msg)
    if super_result.is_certain():
      # short circuit: Another team in the chain already vouched for membership
      return super_result
    if self.regex.fullmatch(msg.user):
      return Quadstate.MaybeTrue
    return Quadstate.AbsolutelyFalse
# ==================================================================================================


_EXPORT_CLASSES_: list[type[Team]] = [
  NameRegex_Team,
]
