'''
This module implements Actionsets for the game Splody.
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
class Splody_KB_Actionset(Keyboard_Actionset):
  '''
  Keyboard-based Actionset that implements the controls for the game
  `Splody`
  '''
  # Class variables:
  name: ClassVar[str] = 'Splody (Keyboard)'
  # ----------------------------------------------------------------------------

  '''
  Splody Controls (Keyboard):

  Action      | Player 1      | Player 2     |
  ------------| ------------- | ------------ |
  Up          | {Up Arrow}    | W            |
  Down        | {Down Arrow}  | S            |
  Left        | {Left Arrow}  | A            |
  Right       | {Right Arrow} | D            |
  Bomb        | L             | E            |
  Secondary   | K             | Q            |
  Taunt       | J             | R            |
  '''

  key_dict: ClassVar[dict[str, Sequence[str]]] = {
    'up':        ('up', 'w'),
    'down':      ('down', 's'),
    'left':      ('left', 'a'),
    'right':     ('right', 'd'),
    'bomb':      ('l', 'e'),
    'secondary': ('k', 'q'),
    'taunt':     ('j', 'r'),
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Keyboard-based Actionset that implements the controls for the game
    `Splody`
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
class Splody_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `Splody`
  '''
  # Class variables:
  name: ClassVar[str] = 'Splody (Gamepad)'
  # ----------------------------------------------------------------------------

  '''
  Splody Controls (XInput):

  Action      | Player        |
  ------------| ------------- |
  Up          | DPad Up       |
  Down        | DPad Down     |
  Left        | DPad Left     |
  Right       | DPad Right    |
  Bomb        | A             |
  Secondary   | B             |
  Taunt       | RB            |
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'left':      'dpad_left',
    'right':     'dpad_right',
    'up':        'dpad_up',
    'down':      'dpad_down',
    'bomb':      'a',
    'taunt':     'rb',
    'secondary': 'b',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Splody`
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
    'up':        [verb_param(key='up',        duration=250)],
    'down':      [verb_param(key='down',      duration=250)],
    'left':      [verb_param(key='left',      duration=250)],
    'right':     [verb_param(key='right',     duration=250)],
    'bomb':      [verb_param(key='bomb',      duration=50)],
    'secondary': [verb_param(key='secondary', duration=50)],
    'taunt':     [verb_param(key='taunt',     duration=250)],
  }
  vd_aliases: dict[str, str] = {
    'l':          'left',
    'r':          'right',
    'u':          'up',
    'd':          'down',
    'b':          'bomb',
    'ping':       'secondary',
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
    ('up',        300),
    ('down',      300),
    ('left',      300),
    ('right',     300),
    ('bomb',      200),
    ('secondary', 100),
    ('taunt',     100),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  Splody_KB_Actionset,
  Splody_GP_Actionset,
]
