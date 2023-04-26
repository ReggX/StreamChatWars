'''
This module implements Actionsets for the game TowerFall Ascension.
Includes Keyboard and XInput Gamepad variants.
'''

# native imports
from collections.abc import Sequence
from typing import Any
from typing import ClassVar

# internal imports
from ..._shared.constants import INPUT_TYPE
from ..._shared.types import Partial_VerbParamDict
from ..._shared.types import VerbParamDict
from ..actionset import Actionset
from .base_multikey import partial_create_verb_params
from .gamepad import Gamepad_Actionset
from .keyboard import Keyboard_Actionset


# ==================================================================================================
class TowerFall_KB_Actionset(Keyboard_Actionset):
  '''
  Keyboard-based Actionset that implements the controls for the game
  `TowerFall Ascension`
  '''
  # Class variables:
  name: ClassVar[str] = 'TowerFall Ascension (Keyboard)'
  # ----------------------------------------------------------------------------

  '''
  TowerFall Controls (Keyboard):

  Action       | Player 1      |
  -------------| ------------- |
  Left         | {Left Arrow}  |
  Right        | {Right Arrow} |
  Up           | {Up Arrow}    |
  Down/Crouch  | {Down Arrow}  |
  Jump         | C             |
  Dodge        | {Shift}       |
  Shoot        | X             |
  Alt Shoot    | Z             |
  Arrow Toggle | S             |
  '''

  key_dict: ClassVar[dict[str, Sequence[str]]] = {
    'left':   ('left',),
    'right':  ('right',),
    'up':     ('up',),
    'down':   ('down',),
    'jump':   ('c',),
    'dodge':  ('shift',),
    'shoot':  ('x',),
    'alt':    ('z',),
    'toggle': ('s',),
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Keyboard-based Actionset that implements the controls for the game
    `TowerFall Ascension`
    '''
    super().__init__(
      doc_url=doc_url, **kwargs
    )
    self.verb_dict = _build_verb_dict(self.action_prefix)

    _random_args: list[tuple[str, float]] = _build_random_args()
    self.random_verb = [t[0] for t in _random_args]
    self.random_weight = [t[1] for t in _random_args]
# ==================================================================================================


# ==================================================================================================
class TowerFall_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `TowerFall Ascension`
  '''
  # Class variables:
  name: ClassVar[str] = 'TowerFall Ascension (Gamepad)'
  # ----------------------------------------------------------------------------

  '''
  TowerFall Controls (XInput):

  Action       | Player 1   |
  -------------| -----------|
  Left         | DPad Left  |
  Right        | DPad Right |
  Up           | DPad Up    |
  Down/Crouch  | DPad Down  |
  Jump         | A          |
  Dodge        | RT         |
  Shoot        | X          |
  Alt Shoot    | B          |
  Arrow Toggle | Y          |
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'left':   'dpad_left',
    'right':  'dpad_right',
    'up':     'dpad_up',
    'down':   'dpad_down',
    'jump':   'a',
    'dodge':  'rt',
    'shoot':  'x',
    'alt':    'b',
    'toggle': 'y',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `TowerFall Ascension`
    '''
    super().__init__(
      doc_url=doc_url, **kwargs
    )
    self.verb_dict = _build_verb_dict(self.action_prefix)

    _random_args: list[tuple[str, float]] = _build_random_args()
    self.random_verb = [t[0] for t in _random_args]
    self.random_weight = [t[1] for t in _random_args]
# ==================================================================================================


def _build_verb_dict(action_prefix: str) -> dict[str, list[VerbParamDict]]:
  '''
  Helper function to build the dictionary of verbs usable in chat,
  outsourced since the dict contents are the same for Keyboard and Gamepad
  '''
  # partial function with shared default values
  verb_param: Partial_VerbParamDict = partial_create_verb_params(
    duration=50,
    delay=0,
    min_time=1,
    max_time=1000,
    input_type=INPUT_TYPE.PRESS_KEY
  )

  verb_dict: dict[str, list[VerbParamDict]] = {
    'left':   [verb_param(key='left',   duration=150)],
    'right':  [verb_param(key='right',  duration=150)],
    'up':     [verb_param(key='up',     duration=150)],
    'down':   [verb_param(key='down',   duration=150)],
    'jump':   [verb_param(key='jump',   duration=250)],
    'dodge':  [verb_param(key='dodge',  duration=50)],
    'shoot':  [verb_param(key='shoot',  duration=100)],
    'alt':    [verb_param(key='alt',    duration=100)],
    'toggle': [verb_param(key='toggle', duration=20)],
  }
  vd_aliases: dict[str, str] = {
    'l':          'left',
    'r':          'right',
    'u':          'up',
    'd':          'down',
    'j':          'jump',
    'crouch':     'down',
    'duck':       'down',
    'dash':       'dodge',
    'catch':      'dodge',
    'attack':     'shoot',
    'fire':       'shoot',
    'altattack':  'alt',
    'altshoot':   'alt',
    'altfire':    'alt',
    'switch':     'toggle',
  }
  # Add aliases to verb_dict
  for alias, original in vd_aliases.items():
    verb_dict[alias] = verb_dict[original]

  # Add hold_* and release_* variants
  input_modifiers: list[tuple[str, INPUT_TYPE]] = [
    ('hold', INPUT_TYPE.HOLD_KEY),
    ('release', INPUT_TYPE.RELEASE_KEY)
  ]
  for keyword, verb_params in list(verb_dict.items()):
    for modifier_verb, input_type in input_modifiers:
      mod_kw: str = f"{modifier_verb}_{keyword}"
      mod_params: list[VerbParamDict] = [
        param.copy() for param in verb_params  # don't modify the original
      ]
      for param in mod_params:
        param['input_type'] = input_type
      verb_dict[mod_kw] = mod_params

  # Add action prefixed versions of verbs to verb_dict
  key: str
  # need list here because we're changing size during iteration
  for key in list(verb_dict.keys()):
    prefixed_key: str = f"{action_prefix}{key}"
    verb_dict[prefixed_key] = verb_dict[key]

  return verb_dict
# ------------------------------------------------------------------------------


def _build_random_args() -> list[tuple[str, float]]:
  '''
  Helper function to build the `random_verb` and `random_weight` lists
  for `random_action()`,
  outsourced since the `random_verb` and `random_weight` are the same
  for Keyboard and Gamepad
  '''
  _random_args: list[tuple[str, float]] = [
    ('left',      300),
    ('right',     300),
    ('up',        100),
    ('down',      100),
    ('jump',      200),
    ('dash',      50),
    ('shoot',     250),
    ('altshoot',  50),
    ('toggle',    50),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  TowerFall_KB_Actionset,
  TowerFall_GP_Actionset,
]
