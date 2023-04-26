'''
This module implements a Gamepad supporting Actionset based on the
MultiKey base Actionset.
Usable stand-alone.
'''

# native imports
from collections.abc import Mapping
from functools import partial
from typing import Any
from typing import ClassVar

# internal imports
from ..._interfaces._actionset import ActionsetValidationError
from ..._shared.types import VerbParamDict
from ...virtual_input.input_handler import BasicGamepadHandler
from ...virtual_input.input_handler import DelayedGamepadHandler
from ..actionset import Actionset
from .base_multikey import MultiKey_BaseActionset
from .base_multikey import create_verb_params


# ==================================================================================================
class Gamepad_Actionset(MultiKey_BaseActionset):
  '''
  Advanced base class for Actionsets that uses
  `BasicGamepadHandler.press_multiple_Keys` for sending input.
  '''
  # Class variables:
  name: ClassVar[str] = 'Gamepad Game'
  input_handler: ClassVar[type[BasicGamepadHandler]] = BasicGamepadHandler
  key_dict: ClassVar[Mapping[str, str]] = {
    'a':          'a',
    'b':          'b',
    'x':          'x',
    'y':          'y',
    'rb':         'rb',
    'lb':         'lb',
    'rs':         'rs',
    'ls':         'ls',
    'dpad_up':    'dpad_up',
    'dpad_down':  'dpad_down',
    'dpad_left':  'dpad_left',
    'dpad_right': 'dpad_right',
    'start':      'start',
    'back':       'back',
    'guide':      'guide',
    'rt':         'rt',
    'lt':         'lt',
    'ls_right':   'ls_right',
    'ls_left':    'ls_left',
    'ls_up':      'ls_up',
    'ls_down':    'ls_down',
    'rs_right':   'rs_right',
    'rs_left':    'rs_left',
    'rs_up':      'rs_up',
    'rs_down':    'rs_down',
  }
  # ----------------------------------------------------------------------------

  def __init__(self, **kwargs: Any) -> None:
    '''
    Advanced base class for Actionsets that uses
    `BasicGamepadHandler.press_multiple_Keys` for sending input.
    '''
    super().__init__(**kwargs)
    self.input_server.add_gamepad(self.player_index)
    self.verb_dict = {
      k: [create_verb_params(
        key=k,
        duration=150,
        delay=0,
        min_time=1,
        max_time=1000
      )]
      for k in self.key_dict.keys()
    }
    key: str
    # need list(dict.keys()) here because we're changing dict size during iteration
    for key in list(self.verb_dict.keys()):
      prefixed_key: str = f"{self.action_prefix}{key}"
      self.verb_dict[prefixed_key] = self.verb_dict[key]
  # ----------------------------------------------------------------------------

  def translate_verb_parameters_to_key(
    self,
    verb_parameters: VerbParamDict
  ) -> str | None:
    '''
    Extract the relevant value from `key_dict` based on the `key`
    parameter of `verb_parameters`.
    '''
    key: str = verb_parameters['key']
    return self.key_dict.get(key)
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
      getattr(DelayedGamepadHandler, func_name),
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
    * Are all keys in key_dict valid gamepad "buttons"?
    '''
    if not super().validate():
      return False
    # additionally: validate that all keys are correctly mapped to the gamepad
    for key in self.key_dict.values():
      if not self.input_handler.valid_key(self.player_index, key):
        raise ActionsetValidationError(
          f"Key '{key}' of Actionset '{self.name}' is not a valid gamepad key!"
        )
    return True
# ==================================================================================================


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  Gamepad_Actionset,
]
