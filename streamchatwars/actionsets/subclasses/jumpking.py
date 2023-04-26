'''
This module implements Actionsets for the game Jump King.
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
class JumpKing_KB_Actionset(Keyboard_Actionset):
  '''
  Keyboard-based Actionset that implements the controls for the game
  `Jump King`
  '''
  # Class variables:
  name: ClassVar[str] = 'Jump King (Keyboard)'
  # ----------------------------------------------------------------------------

  '''
  Jump King Controls (Keyboard):

  Action      | Player        |
  ------------| ------------- |
  Left        | {Left Arrow}  |
  Right       | {Right Arrow} |
  Jump        | {Space}       |
  '''

  key_dict: ClassVar[dict[str, Sequence[str]]] = {
    'left':   ('left',),
    'right':  ('right',),
    'up':     ('up',),
    'down':   ('down',),
    'jump':   ('space',),
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Keyboard-based Actionset that implements the controls for the game
    `Jump King`
    '''
    super().__init__(
      doc_url=doc_url, **kwargs
    )
    self.player_index = 0  # force player_index=0, since there is only one
    self.verb_dict = _build_verb_dict(self.action_prefix)

    _random_args: list[tuple[str, float]] = _build_random_args()
    self.random_verb = [t[0] for t in _random_args]
    self.random_weight = [t[1] for t in _random_args]
# ==================================================================================================


# ==================================================================================================
class JumpKing_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `Jump King`
  '''
  # Class variables:
  name: ClassVar[str] = 'Jump King (Gamepad)'
  # ----------------------------------------------------------------------------

  '''
  Jump King Controls (XInput):

  Action      | Player       |
  ------------| ------------ |
  Left        | DPad Left    |
  Right       | DPad Right   |
  Jump        | A            |
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'left':   'dpad_left',
    'right':  'dpad_right',
    'up':     'dpad_up',
    'down':   'dpad_down',
    'jump':   'a',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Jump King`
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
    'left':      [verb_param(key='left',  duration=150)],
    'right':     [verb_param(key='right', duration=150)],
    'jump':      [verb_param(key='jump',  duration=150)],
    'jumpleft':  [verb_param(key='jump',  duration=150),
                  verb_param(key='left',  duration=150)],
    'jumpright': [verb_param(key='jump',  duration=150),
                  verb_param(key='right', duration=150)],
  }
  vd_aliases: dict[str, str] = {
    'l': 'left',
    'r': 'right',
    'j': 'jump',
    'jl': 'jumpleft',
    'jr': 'jumpright',
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
    ('left 100',            300),
    ('right 100',           300),
    ('jump 100 left 100',   100),
    ('jump 100 right 100',  100),
    ('jump 100',            100),
    ('jump 200 left 200',   100),
    ('jump 200 right 200',  100),
    ('jump 200',            100),
    ('jump 300 left 300',   100),
    ('jump 300 right 300',  100),
    ('jump 300',            100),
    ('jump 400 left 400',   100),
    ('jump 400 right 400',  100),
    ('jump 400',            100),
    ('jump 500 left 500',   100),
    ('jump 500 right 500',  100),
    ('jump 500',            100),
    ('jump 600 left 600',   100),
    ('jump 600 right 600',  100),
    ('jump 600',            100),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  JumpKing_KB_Actionset,
  JumpKing_GP_Actionset,
]
