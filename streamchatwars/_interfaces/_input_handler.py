'''
InputHandler Interface
Provide an Abstract Base Class as reference for other modules.
'''

# native imports
from abc import ABC
from abc import abstractmethod
from collections.abc import Sequence

# internal imports
from .._shared.types import FuncArgsDict


# ==================================================================================================
class AbstractInputHandler(ABC):
  '''Interface class for Input Handler.'''

  @classmethod
  @abstractmethod
  def press_multiple_Keys(
    cls,
    index: int,
    args_list: Sequence[FuncArgsDict]
  ) -> None:
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @classmethod
  @abstractmethod
  def valid_key(cls, index: int, key: str) -> bool:
    '''
    Does the key represent a valid key for this input handler
    (is it accepeted in press_multiple_Keys()'s args_list parameter)?
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
