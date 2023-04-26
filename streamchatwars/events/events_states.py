'''
This modules is storing the internal state of file events.
'''


# native imports
from typing import ClassVar


# ==================================================================================================
class GlobalEventStates:
  '''Data store for event states, no instances necessary!'''
  # Class variables:
  state_accept_input: ClassVar[bool | None] = None
  state_random_action: ClassVar[bool | None] = None
  state_reset_teams: ClassVar[bool | None] = None
  state_delay_random: ClassVar[float | None] = None
# ==================================================================================================
