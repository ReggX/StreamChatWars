'''
This module provides a basic default implementation of the Actionset
base class with limited functionality.
'''

# native imports
from functools import partial
from typing import ClassVar

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..actionset import Actionset


# ==================================================================================================
class Default_Actionset(Actionset):
  '''
  A simple default implementation of the base Actionset class,
  that does nothing more than simple print its recevied commands.

  It's usefulness is probably limited to debugging.
  '''
  # Class variables:
  name: ClassVar[str] = 'Default'
  # ----------------------------------------------------------------------------

  def translate_user_message_to_action(
    self,
    msg: AbstractChatMessage
  ) -> partial[None] | None:
    '''
    Returned action is a simple print command, useful for debugging.
    '''
    if self.message_is_command(msg):
      return partial(print, f"ACTION {msg.message[len(self.action_prefix):]}")
    return None
# ==================================================================================================


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  Default_Actionset,
]
