'''
This module provides an Actionset class with the explicit
intent of not doing anything.
'''

# native imports
from functools import partial
from typing import ClassVar

# internal imports
from ..._interfaces._chatmsg import AbstractChatMessage
from ..actionset import Actionset


# ==================================================================================================
class None_Actionset(Actionset):
  '''
  Actionset with a single purpose: doing nothing.
  '''
  # Class variables:
  name: ClassVar[str] = 'No Actionset'
  # ----------------------------------------------------------------------------

  def translate_user_message_to_action(
    self,
    msg: AbstractChatMessage
  ) -> partial[None] | None:
    '''
    No message will trigger an action for this actionset.
    '''
    return None
# ==================================================================================================


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  None_Actionset,
]
