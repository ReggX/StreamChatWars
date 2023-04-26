'''
This module contains the class definitions used for logging prints
to the console. It's imported into _shared.helpers and _shared.global_data,
which is why need to pay special attention to not import anything that
could result circular imports!
'''

# native imports
from dataclasses import dataclass
from dataclasses import field
from time import time

# internal imports
from .._shared.primitive_types import seconds
from .._shared.types import ConsoleMessageDict


# ==================================================================================================
@dataclass(slots=True)
class ConsoleMessage:
  '''Stored console prints with metadata in a single data instance.'''
  message: str
  timestamp: seconds = field(default_factory=lambda: time())
  # ----------------------------------------------------------------------------

  def as_dict(self) -> ConsoleMessageDict:
    '''Export ConsoleMessage as dict instance.'''
    return {
      'message': self.message,
      "timestamp": self.timestamp,
    }
# ==================================================================================================


# ==================================================================================================
@dataclass
class ConsoleLog:
  '''List of all collected console messages with related functions.'''
  messages: list[ConsoleMessage] = field(default_factory=list)
  # ----------------------------------------------------------------------------

  def log_message(self, message: str) -> None:
    '''Add message to the log.'''
    self.messages.append(ConsoleMessage(message))
  # ----------------------------------------------------------------------------

  def export_list(self) -> list[ConsoleMessageDict]:
    '''Export list of collected messages in a JSON serializable way.'''
    return [msg.as_dict() for msg in self.messages]
  # ----------------------------------------------------------------------------

  def clear(self) -> None:
    '''Clear out all messages.'''
    self.messages.clear()
# ==================================================================================================


# We need to initialize the global ConsoleLog object in here because
# it's needed by _shared.helpers which is very strict on imports
# to prevent circular imports!
CONSOLELOG: ConsoleLog = ConsoleLog()
