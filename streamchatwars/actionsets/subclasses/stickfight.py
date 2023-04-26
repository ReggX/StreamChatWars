'''
This module implements Actionsets for the game Stick Fight: The Game.
Only XInput Gamepad variant supported at this time.
'''

# native imports
from typing import Any
from typing import ClassVar

# internal imports
from ..._shared.types import Partial_VerbParamDict
from ..._shared.types import VerbParamDict
from ..actionset import Actionset
from .base_multikey import partial_create_verb_params
from .gamepad import Gamepad_Actionset


# No Keyboard Actionset since aiming would require use of Mouse


# ==================================================================================================
class StickFight_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `Stick Fight: The Game`
  '''
  # Class variables:
  name: ClassVar[str] = 'Stick Fight: The Game (Gamepad)'

  '''
  Stick Fight Controls (XInput):

  Action      | Player       |
  ------------| ------------ |
  Left        | DPad Left    |
  Right       | DPad Right   |
  Up          | DPad Up      |
  Down/Crouch | DPad Down    |
  Jump        | A / LB       |
  Attack      | X / RT       |
  Guard       | LT           |
  Throw       | Y            |
  Aim         | Right Stick  |

  Player Colors are determined by order of joining game:
  1st player: Yellow
  2nd player: Blue
  3rd player: Red
  4th player: Green
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'left':     'dpad_left',
    'right':    'dpad_right',
    'up':       'dpad_up',
    'down':     'dpad_down',
    'jump':     'lb',
    'attack':   'rt',
    'guard':    'lt',
    'throw':    'y',
    'aimleft':  'rs_left',
    'aimright': 'rs_right',
    'aimup':    'rs_up',
    'aimdown':  'rs_down',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Stick Fight: The Game`
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
    delay=0,
    min_time=1,
    max_time=1000
  )

  verb_dict: dict[str, list[VerbParamDict]] = {
    'left':     [verb_param(key='left',     duration=150)],
    'right':    [verb_param(key='right',    duration=150)],
    'up':       [verb_param(key='up',       duration=150)],
    'down':     [verb_param(key='down',     duration=150)],
    'jump':     [verb_param(key='jump',     duration=250)],
    'hop':      [verb_param(key='jump',     duration=50)],
    'attack':   [verb_param(key='attack',   duration=50)],
    'guard':    [verb_param(key='guard',    duration=100)],
    'throw':    [verb_param(key='throw',    duration=50)],
    'aimleft':  [verb_param(key='aimleft',  duration=150)],
    'aimright': [verb_param(key='aimright', duration=150)],
    'aimup':    [verb_param(key='aimup',    duration=150)],
    'aimdown':  [verb_param(key='aimdown',  duration=150)],
  }
  vd_aliases: dict[str, str] = {
    'l':          'left',
    'r':          'right',
    'u':          'up',
    'd':          'down',
    'j':          'jump',
    'crouch':     'down',
    'duck':       'down',
    'yeet':       'throw',
    'shoot':      'attack',
    'fire':       'attack',
    'defend':     'guard',
    'shield':     'guard',
    'aim_left':   'aimleft',
    'aim_right':  'aimright',
    'aim_up':     'aimup',
    'aim_down':   'aimdown',
    'aiml':       'aimleft',
    'aimr':       'aimright',
    'aimu':       'aimup',
    'aimd':       'aimdown',
  }
  # Add aliases to verb_dict
  for t in vd_aliases.items():
    verb_dict[t[0]] = verb_dict[t[1]]

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
    ('jump',      100),
    ('hop',       100),
    ('down',      100),
    ('throw',     50),
    ('attack',    250),
    ('guard',     50),
    ('aimleft',   50),
    ('aimright',  50),
    ('aimup',     50),
    ('aimdown',   50),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  StickFight_GP_Actionset,
]
