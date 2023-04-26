'''
TTS Interface
Provide an Abstract Base Class as reference for other modules.
'''

# native imports
from abc import ABC
from abc import abstractmethod


# ==================================================================================================
class AbstractTTSQueue(ABC):
  '''Interface class for TTS queues.'''

  @abstractmethod
  def queue_tts_message(self, text: str, user: str) -> None:
    '''
    Add a message to the queue.
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
