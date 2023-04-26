'''
Gamepad Interface
Provide an Abstract Base Class as reference for other modules.
'''

# native imports
from abc import ABC
from abc import abstractmethod
from ctypes import Structure

# internal imports
from .._shared.types import AXIS_MAP_TYPE


# ==================================================================================================
class AbstractReport(Structure):  # needs Structure to be metaclass-compatible
  '''Interface class for Gamepad Reports'''
  # Instance variables:
  wButtons: int
  bLeftTrigger: int
  bRightTrigger: int
  sThumbLX: int
  sThumbLY: int
  sThumbRX: int
  sThumbRY: int
# ==================================================================================================


# ==================================================================================================
class AbstractGamepad(ABC):
  '''Interface class for gamepads'''
  # Instance variables:
  report: AbstractReport
  axis_mapping: AXIS_MAP_TYPE
  # ----------------------------------------------------------------------------

  @abstractmethod
  def __del__(self) -> None:
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def update(self) -> None:
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def press_pseudo_key(self, pseudo_key: str) -> None:
    '''
    Combine both "button keys" and "axis keys" and delegate
    to the correct handling function automatically.

    Raise ArgumentError if the given argument is not a support
    "key" value.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def release_pseudo_key(self, pseudo_key: str) -> None:
    '''
    Combine both "button keys" and "axis keys" and delegate
    to the correct handling function automatically.

    Raise ArgumentError if the given argument is not a support
    "key" value.
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
