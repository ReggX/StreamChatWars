'''
This module implements Actionsets for the game Lethal League.
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
class LethalLeague_KB_Actionset(Keyboard_Actionset):
  '''
  Keyboard-based Actionset that implements the controls for the game
  `Lethal League`
  '''
  # Class variables:
  name: ClassVar[str] = 'Lethal League (Keyboard)'
  # ----------------------------------------------------------------------------

  '''
  Lethal League Controls (Keyboard):

  Action      | Default Layout |
  ------------|----------------|
  Left        | {Left Arrow}   |
  Right       | {Right Arrow}  |
  Up          | {Up Arrow}     |
  Down/Crouch | {Down Arrow}   |
  Jump        | {Spacebar}     |
  Swing       | Z              |
  Bunt        | X              |
  Express     | A              | (used to taunt)
  Pause       | {Enter}        |
  '''

  key_dict: ClassVar[dict[str, Sequence[str]]] = {
    'left':    ('left', ),
    'right':   ('right', ),
    'up':      ('up', ),
    'down':    ('down', ),
    'jump':    ('space', ),
    'swing':   ('z', ),
    'bunt':    ('x', ),
    'express': ('a', ),
    'pause':   ('enter', ),
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Keyboard-based Actionset that implements the controls for the game
    `Lethal League`
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
class LethalLeague_GP_Actionset(Gamepad_Actionset):
  '''
  Gamepad-based Actionset that implements the controls for the game
  `Lethal League`
  '''
  # Class variables:
  name: ClassVar[str] = 'Lethal League (Gamepad)'
  # ----------------------------------------------------------------------------

  '''
  Lethal League Controls (XInput):

  Action      | Default Layout |
  ------------|----------------|
  Left        | {Left Stick}   |
  Right       | {Right Stick}  |
  Up          | {Up Stick}     |
  Down/Crouch | {Down Stick}   |
  Jump        | A              |
  Swing       | X              |
  Bunt        | B              |
  Express     | Y              | (used to taunt)
  Pause       | Start          |
  '''

  key_dict: ClassVar[dict[str, str]] = {
    'left':    'ls_left',
    'right':   'ls_right',
    'up':      'ls_up',
    'down':    'ls_down',
    'jump':    'a',
    'swing':   'x',
    'bunt':    'b',
    'express': 'y',
    'pause':   'start',
  }
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    doc_url: str = "",
    **kwargs: Any
  ) -> None:
    '''
    Gamepad-based Actionset that implements the controls for the game
    `Lethal League`
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
    'left':        [verb_param(key='left', duration=150)],
    'right':       [verb_param(key='right', duration=150)],
    'up':          [verb_param(key='up')],
    'down':        [verb_param(key='down')],
    'jump':        [verb_param(key='jump', duration=150)],
    'swing':       [verb_param(key='swing')],
    'bunt':        [verb_param(key='bunt')],
    'express':     [verb_param(key='express')],
    'uptaunt':     [verb_param(key='express'),
                    verb_param(key='up')],
    'lefttaunt':   [verb_param(key='express'),
                    verb_param(key='left')],
    'righttaunt':  [verb_param(key='express'),
                    verb_param(key='right')],
    'downtaunt':   [verb_param(key='express'),
                    verb_param(key='down')],
    'upswing':     [verb_param(key='swing'),
                    verb_param(key='up')],
    'downswing':   [verb_param(key='swing'),
                    verb_param(key='down')],
    'upbunt':      [verb_param(key='bunt'),
                    verb_param(key='up')],
    'downbunt':    [verb_param(key='bunt'),
                    verb_param(key='down')],
    'jumpleft':    [verb_param(key='jump'),
                    verb_param(key='left')],
    'jumpright':   [verb_param(key='jump'),
                    verb_param(key='right')],
  }
  vd_aliases: dict[str, str] = {
    'l':          'left',
    'r':          'right',
    'u':          'up',
    'd':          'down',
    'j':          'jump',
    'jl':         'jumpleft',
    'jr':         'jumpright',
    'crouch':     'down',
    'duck':       'down',
    'smash':      'swing',
    's':          'swing',
    'parry':      'bunt',
    'b':          'bunt',
    'taunt':      'express',
    't':          'express',
    'nice':       'uptaunt',
    'oops':       'lefttaunt',
    'wow':        'righttaunt',
    'bringit':    'downtaunt',
  }
  # Add aliases to verb_dict
  for alias, original in vd_aliases.items():
    verb_dict[alias] = verb_dict[original]

  if False:  # Doesn't need hold_ or release_ variants
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
    ('left',       200),
    ('right',      200),
    ('jump',       200),
    ('jumpleft',   200),
    ('jumpright',  200),
    ('down',        40),
    ('swing',      100),
    ('upswing',    100),
    ('downswing',  100),
    ('bunt',        50),
    ('upbunt',      50),
    ('downbunt',    50),
    ('taunt',        5),
    ('uptaunt',      5),
    ('downtaunt',    5),
    ('lefttaunt',    5),
    ('righttaunt',   5),
  ]
  return _random_args
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
  LethalLeague_KB_Actionset,
  LethalLeague_GP_Actionset,
]
