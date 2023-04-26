'''
This module implements Actionsets for the game Divekick.
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
class Divekick_KB_Actionset(Keyboard_Actionset):
  '''
  Keyboard-based Actionset that implements the controls for the game
  `Divekick`
  '''
  # Class variables:
  name: ClassVar[str] = 'Divekick (Keyboard)'
  # ----------------------------------------------------------------------------

  '''
  Divekick Controls (Keyboard):

  Action      | Player 1     | Player 2      |
  ------------| ------------ | ------------- |
  Dive        | W            | {Up Arrow}    |
  Kick        | S            | {Down Arrow}  |
  '''

  key_dict: ClassVar[dict[str, Sequence[str]]] = {
    'dive':   ('w', 'up'),
    'kick':   ('s', 'down'),
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Keyboard-based Actionset that implements the controls for the game
    `Divekick`
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
class Divekick_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `Divekick`
  '''
  # Class variables:
  name: ClassVar[str] = 'Divekick (Gamepad)'
  # ----------------------------------------------------------------------------

  '''
  Divekick Controls (XInput):

  Action      | Player       |
  ------------| ------------ |
  Dive        | Y            |
  Kick        | X            |
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'dive':  'y',
    'kick':  'x',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Divekick`
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
    'dive': [verb_param(key='dive', duration=150)],
    'kick': [verb_param(key='kick', duration=150)],
  }
  vd_aliases: dict[str, str] = {
    'd':          'dive',
    'k':          'kick',
    'jump':       'dive',
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
    ('dive 10',  100),
    ('kick 10',  100),
    ('dive 50',  100),
    ('kick 50',  100),
    ('dive 100', 100),
    ('kick 100', 100),
    ('dive 200', 100),
    ('kick 200', 100),
    ('dive 300', 100),
    ('kick 300', 100),
    ('dive 400', 100),
    ('kick 400', 100),
    ('dive 500', 100),
    ('kick 500', 100),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  Divekick_KB_Actionset,
  Divekick_GP_Actionset,
]
