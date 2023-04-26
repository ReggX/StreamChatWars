'''
This module provides a very simple Actionsets that types out
messages provided as action commands.
'''

# native imports
from functools import partial
from typing import ClassVar

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ...virtual_input.input_handler import BasicKeyboardHandler
from ..actionset import Actionset


# ==================================================================================================
class Typewrite_Actionset(Actionset):
  '''
  Simple Actionset subclass that passes action commands to
  `pydirectinput`'s `typewrite` function.

  Since `typewrite` comes with some caveats, it's usefulness
  is probably limited to debugging.
  '''
  # Class variables:
  name: ClassVar[str] = 'Typewriter'
  # ----------------------------------------------------------------------------

  def translate_user_message_to_action(
    self,
    msg: AbstractChatMessage
  ) -> partial[None] | None:
    '''
    Action command will be passed on to `pydirectinput`'s `typewrite` function
    '''
    if self.message_is_command(msg):
      return partial(
        BasicKeyboardHandler.typewrite,
        str(msg.message[len(self.action_prefix):]).lower()
      )
    return None
# ==================================================================================================


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  Typewrite_Actionset,
]
