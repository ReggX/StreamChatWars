'''
This module implements a base actionset for subclassing based on
the MultiKey base Actionset.
NOT usable stand-alone.
'''

# native imports
from collections.abc import Mapping
from collections.abc import Sequence
from functools import partial
from typing import Any
from typing import ClassVar

# internal imports
from ..._interfaces._actionset import ActionsetValidationError
from ..._shared.types import VerbParamDict
from ...virtual_input.input_handler import BasicKeyboardHandler
from ...virtual_input.input_handler import DelayedKeyboardHandler
from ..actionset import Actionset
from .base_multikey import MultiKey_BaseActionset


# ==================================================================================================
class Keyboard_Actionset(MultiKey_BaseActionset):
  '''
  Advanced base class for Actionsets that uses
  `BasicKeyboardHandler.press_multiple_Keys` for sending input.
  '''
  # Class variables:
  name: ClassVar[str] = 'Keyboard Game'
  key_dict: ClassVar[Mapping[str, Sequence[str]]] = {}
  input_handler: ClassVar[type[BasicKeyboardHandler]] = BasicKeyboardHandler
  # ----------------------------------------------------------------------------

  def __init__(self, **kwargs: Any) -> None:
    '''
    Advanced base class for Actionsets that uses
    `BasicKeyboardHandler.press_multiple_Keys` for sending input.
    '''
    super().__init__(**kwargs)
  # ----------------------------------------------------------------------------

  def translate_verb_parameters_to_key(
    self,
    verb_parameters: VerbParamDict
  ) -> str | None:
    '''
    Extract the relevant value from `key_dict` based on the `key`
    parameter of `verb_parameters`.
    '''
    try:
      key: str = verb_parameters['key']
      key_tuple: Sequence[str] = self.key_dict[key]
    except KeyError:
      return None
    return key_tuple[self.player_index]
  # ----------------------------------------------------------------------------

  def random_action(self) -> partial[None]:
    '''
    When the team's queue is empty, random actions can be performed
    instead of sleeping. (Based on `random_verb` and `random_weight`)

    This function selects a random action and mutates the input handler
    into its delay variant.
    '''
    # get Basic random action
    partial_function = super().random_action()
    # replace with Delayed variant
    func_name: str = partial_function.func.__name__
    partial_function = partial(
      getattr(DelayedKeyboardHandler, func_name),
      *partial_function.args,
      **partial_function.keywords
    )
    return partial_function
  # ----------------------------------------------------------------------------

  def validate(self) -> bool:
    '''
    Validate that object data is internally consistent.

    Intended to be used after __init__ to detect stuff like
    dict members not behaving correctly!

    * Are all keys in verb_dict present in key_dict?
    * Is `player_index` a valid index for key tuples?
    * Are all keys in key_dict valid keyboard "keys"?
    '''
    if not super().validate():
      return False
    # additionally: validate that the used keys are mapped to the keyboard
    for keys in self.key_dict.values():
      try:
        key: str = keys[self.player_index]
      except IndexError:
        raise ActionsetValidationError(
          f"player_index {self.player_index} is higher than key_dict allows!"
        )
      if not self.input_handler.valid_key(self.player_index, key):
        raise ActionsetValidationError(
          f"Key '{keys[self.player_index]}' of Actionset '{self.name}' is not "
          f"a valid keyboard key!"
        )
    return True
# ==================================================================================================


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
]
