'''
Thread-supporting Interface
Provide Abstract Base Class as reference for other modules
'''

# native imports
from abc import ABC
from abc import abstractmethod


# ==================================================================================================
class AbstractThreadSupport(ABC):
  @abstractmethod
  def create_thread(self) -> None:
    '''
    Create thread(s).
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def start_thread(self) -> None:
    '''
    Start thread(s).
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def stop_thread(self) -> None:
    '''
    Stop thread(s).
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
