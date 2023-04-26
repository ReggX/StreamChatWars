'''
This module implements Actionsets for the game Tricky Towers.
Includes Keyboard and XInput Gamepad variants.
'''

# native imports
from collections.abc import Sequence
from typing import Any
from typing import ClassVar

# internal imports
from ..._shared.types import Partial_VerbParamDict
from ..._shared.types import VerbParamDict
from ..actionset import Actionset
from .base_multikey import partial_create_verb_params
from .gamepad import Gamepad_Actionset
from .keyboard import Keyboard_Actionset


# ==================================================================================================
class TrickyTowers_KB_Actionset(Keyboard_Actionset):
  '''
  Keyboard-based Actionset that implements the controls for the game
  `Tricky Towers`
  '''
  # Class variables:
  name: ClassVar[str] = 'Tricky Towers (Keyboard)'

  '''
  Tricky Towers Controls (Keyboard):

  Action      | Player       |
  ------------| ------------ |
  Left        | {Left}       |
  Right       | {Right}      |
  Down (fast) | {Down}       |
  Rotate      | {Up}         |
  Nudge Left  | U            |
  Nudge Right | I            |
  Light Magic | J            |
  Dark Magic  | K            |
  '''

  key_dict: ClassVar[dict[str, Sequence[str]]] = {
    'left':        ('left', ),
    'right':       ('right', ),
    'down':        ('down', ),
    'rotate':      ('up', ),
    'nudge_left':  ('u', ),
    'nudge_right': ('i', ),
    'light_magic': ('j', ),
    'dark_magic':  ('k', ),
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Keyboard-based Actionset that implements the controls for the game
    `Tricky Towers`
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
class TrickyTowers_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `Tricky Towers`
  '''
  # Class variables:
  name: ClassVar[str] = 'Tricky Towers (Gamepad)'

  '''
  Tricky Towers Controls (XInput):

  Action      | Player       |
  ------------| ------------ |
  Left        | {DPad Left}  |
  Right       | {DPad Right} |
  Down (fast) | {Dpad Down}  |
  Rotate      | A            |
  Nudge Left  | LB           |
  Nudge Right | RB           |
  Light Magic | X            |
  Dark Magic  | B            |
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'left':        'dpad_left',
    'right':       'dpad_right',
    'down':        'dpad_down',
    'rotate':      'a',
    'nudge_left':  'lb',
    'nudge_right': 'rb',
    'light_magic': 'x',
    'dark_magic':  'b',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Tricky Towers`
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
    'left':         [verb_param(key='left',        duration=50)],
    'right':        [verb_param(key='right',       duration=50)],
    'down':         [verb_param(key='down',        duration=50)],
    'rotate':       [verb_param(key='rotate',      duration=50)],
    'nudge_left':   [verb_param(key='nudge_left',  duration=50)],
    'nudge_right':  [verb_param(key='nudge_right', duration=50)],
    'light_magic':  [verb_param(key='light_magic', duration=50)],
    'dark_magic':   [verb_param(key='dark_magic',  duration=50)],
  }
  vd_aliases: dict[str, str] = {
    'l':           'left',
    'r':           'right',
    'd':           'down',
    'rot':         'rotate',
    'nudgeleft':   'nudge_left',
    'nudgeright':  'nudge_right',
    'lightmagic':  'light_magic',
    'darkmagic':   'dark_magic',
    'left_nudge':  'nudge_left',
    'right_nudge': 'nudge_right',
    'leftnudge':   'nudge_left',
    'rightnudge':  'nudge_right',
    'nudgel':      'nudge_left',
    'nudger':      'nudge_right',
    'lnudge':      'nudge_left',
    'rnudge':      'nudge_right',
    'light':       'light_magic',
    'dark':        'dark_magic',
    'nl':          'nudge_left',
    'nr':          'nudge_right',
    'ln':          'nudge_left',
    'rn':          'nudge_right',
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
    ('left 50+50',        100),
    ('right 50+50',       100),
    ('down 50+50',         20),
    ('rotate 50+50',      100),
    ('nudge_left 50+50',   50),
    ('nudge_right 50+50',  50),
    ('light_magic 50+50',  20),
    ('dark_magic 50+50',   20),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  TrickyTowers_KB_Actionset,
  TrickyTowers_GP_Actionset,
]
