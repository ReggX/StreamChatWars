'''
This module implements Actionsets for the game Duck Game.
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
class Duckgame_KB_Actionset(Keyboard_Actionset):
  '''
  Keyboard-based Actionset that implements the controls for the game
  `Duck Game`
  '''
  # Class variables:
  name: ClassVar[str] = 'Duck Game (Keyboard)'
  # ----------------------------------------------------------------------------

  '''
  Duckgame Controls (Keyboard):

  Action      | Player 1     | Player 2      |
  ------------| ------------ | ------------- |
  Left        | A            | {Left Arrow}  |
  Right       | D            | {Right Arrow} |
  Up          | W            | {Up Arrow}    |
  Down/Crouch | S            | {Down Arrow}  |
  Jump        | {Space}      | {Right Ctrl}  |
  Grab/Drop   | G            | [             |
  Shoot       | H            | '             |
  Strafe      | {Left Shift} | L             |
  Trip        | F            | O             |
  Quack       | E            | P             |
  ------------| ------------ | ------------- |
  Menu        | Player 1     | Player 2      |
  ------------| ------------ | ------------- |
  Accept      | {Space}      | {Right Shift} |
  Cancel      | E            | P             |
  Start       | Escape       | ]             |

  Advanced Moves:
  Slide = Crouch + Left/Right
  Drop = Crouch + Jump
  '''

  key_dict: ClassVar[dict[str, Sequence[str]]] = {
    'left':   ('a', 'left'),
    'right':  ('d', 'right'),
    'up':     ('w', 'up'),
    'down':   ('s', 'down'),
    'jump':   ('space', 'ctrlright'),
    'grab':   ('g', '['),
    'shoot':  ('h', "'"),
    'strafe': ('shiftleft', 'l'),
    'trip':   ('f', 'o'),
    'quack':  ('e', 'p'),
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "https://gist.github.com/ReggX/45255e112b0bce5fae591227edcdf8d6",
    **kwargs: Any
  ) -> None:
    '''
    Keyboard-based Actionset that implements the controls for the game
    `Duck Game`
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
class Duckgame_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `Duck Game`
  '''
  # Class variables:
  name: ClassVar[str] = 'Duck Game (Gamepad)'
  # ----------------------------------------------------------------------------

  '''
  Duckgame Controls (XInput):

  Action      | Player       |
  ------------| ------------ |
  Left        | DPad Left    |
  Right       | DPad Right   |
  Up          | DPad Up      |
  Down/Crouch | DPad Down    |
  Jump        | A            |
  Grab/Drop   | Y            |
  Shoot       | X            |
  Strafe      | LB           |
  Trip        | RB           |
  Quack       | B            |
  ------------| ------------ |
  Menu        | Player 1     |
  ------------| ------------ |
  Accept      | A            |
  Cancel      | B            |
  Start       | Start        |

  Advanced Moves:
  Slide = Crouch + Left/Right
  Drop = Crouch + Up
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'left':   'dpad_left',
    'right':  'dpad_right',
    'up':     'dpad_up',
    'down':   'dpad_down',
    'jump':   'a',
    'grab':   'y',
    'shoot':  'x',
    'strafe': 'lb',
    'trip':   'rb',
    'quack':  'b',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "https://gist.github.com/ReggX/45255e112b0bce5fae591227edcdf8d6",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Duck Game`
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
    # up uses jump instead, because up by itself is pretty useless in Duckgame
    'up':     [verb_param(key='jump',   duration=250)],
    'down':   [verb_param(key='down',   duration=100)],
    'jump':   [verb_param(key='jump',   duration=250)],
    'hop':    [verb_param(key='jump',   duration=50)],
    'grab':   [verb_param(key='grab',   duration=50)],
    'shoot':  [verb_param(key='shoot',  duration=100, max_time=3000)],
    'strafe': [verb_param(key='strafe', duration=100)],
    'trip':   [verb_param(key='trip',   duration=20)],
    'quack':  [verb_param(key='quack',  duration=20)],
  }
  vd_aliases: dict[str, str] = {
    'l':          'left',
    'r':          'right',
    'u':          'up',
    'd':          'down',
    'j':          'jump',
    'crouch':     'down',
    'duck':       'down',
    'pickup':     'grab',
    'attack':     'shoot',
    'fire':       'shoot',
    'taunt':      'quack',
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
    ('left 100',  300),
    ('right 100', 300),
    ('up',        100),
    ('hop',       100),
    ('down',      100),
    ('grab',      50),
    ('shoot',     250),
    ('trip',      50),
    ('quack',     50),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  Duckgame_KB_Actionset,
  Duckgame_GP_Actionset,
]
