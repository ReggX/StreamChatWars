'''
InputServer Interface
Provide an Abstract Base Class as reference for other modules.
'''

# native imports
from abc import ABC
from abc import abstractmethod
from functools import partial
from typing import ClassVar


# ==================================================================================================
class InputServerConnectionFailed(TimeoutError, ConnectionRefusedError):
  '''
  Combine two Exception classes to raise as a single exception.
  '''
  pass
# ==================================================================================================


# ==================================================================================================
class AbstractInputServer(ABC):
  '''Interface class for Input Server'''
  # Class variables:
  type: ClassVar[str]
  # ----------------------------------------------------------------------------

  @abstractmethod
  def execute(self, partial_function: partial[None]) -> None:
    '''
    Execute the function contained in `funcargs`
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @classmethod
  @abstractmethod
  def add_gamepad(cls, player_index: int) -> None:
    '''
    Add virtual gamepad to this Input Server instance
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @classmethod
  @abstractmethod
  def remove_gamepad(cls, player_index: int) -> None:
    '''
    Release and remove virtual gamepad from this Input Server instance
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
