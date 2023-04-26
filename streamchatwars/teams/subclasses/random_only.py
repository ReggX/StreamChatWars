'''
This module provides a Team class with the explicit intent of
not doing anything.
Rejects all users unless whitelisted or assigned.
'''

# native imports
from functools import partial
from time import sleep
from typing import Any

# internal imports
from ..._shared.constants import EMPTY_QUEUE_SLEEP_DURATION
from ..._shared.global_data import GlobalData
from ..team import Team


# ==================================================================================================
class RandomOnly_Team(Team):
  '''
  Team subclass that also executes random actions when the normal
  Accept Input state is active.

  Not really intended for human members, but they can assigned/whitelisted
  in case you need them.
  '''
  def __init__(
    self,
    name: str = "RandomOnly",
    **kwargs: Any
  ) -> None:
    '''
    Team subclass that also executes random actions when the normal
    Accept Input state is active.

    Not really intended for human members, but they can assigned/whitelisted
    in case you need them.
    '''
    super().__init__(name=name, **kwargs)
  # ----------------------------------------------------------------------------

  def empty_queue_action(self) -> partial[None]:
    '''
    Modified to return a random action when Accept Inputs or Random Inputs
    are enabled, regardless of team's `use_random_inputs` property.
    '''
    if (
      GlobalData.EventStates.accept_input()
      or GlobalData.EventStates.random_action()
    ):
      return self.actionset.random_action()
    else:
      return partial(sleep, EMPTY_QUEUE_SLEEP_DURATION)
# ==================================================================================================


_EXPORT_CLASSES_: list[type[Team]] = [
  RandomOnly_Team,
]
