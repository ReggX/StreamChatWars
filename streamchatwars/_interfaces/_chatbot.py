'''
Chatbot Interface
Provide an Abstract Base Class as reference for other modules.
'''

# native imports
from abc import ABC
from abc import abstractmethod


# ==================================================================================================
class AbstractMessageSender(ABC):
  '''Interface class for the back reference of ChatMessages to ChatBot'''
  # Instance variables:
  channel_set: set[str]
  # ----------------------------------------------------------------------------

  @abstractmethod
  def send_message(self, channel: str, message: str) -> bool:
    '''
    Send a `message` to the chosen `channel` (if rate limits allow).

    Don't rely on this function to send the message in the first place.

    Return `True` on success, `False` if message hasn't been sent.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def send_priority_message(self, channel: str, message: str) -> None:
    '''
    Send a `message` to the chosen `channel` (ignore rate limits).

    This function will ignore any rate limits and just send the message
    anyways.

    Be cautious, because you are responsible for not getting
    your bot forcibly disconnected for spamming!
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def queue_message(self, channel: str, message: str) -> None:
    '''
    Send a `message` to the chosen `channel` (when rate limits allow).

    The message could be sent immediately, any time after, or never
    (if the bot disconnects before the message queue can be emptied).
    Don't use this function, if you need the message out there immediately!
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
