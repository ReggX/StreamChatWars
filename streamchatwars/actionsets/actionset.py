'''
Actionset base module
Serves as the base for every module in actionsets sub-package
'''

from __future__ import annotations

# native imports
from functools import partial
from pathlib import Path
from time import sleep
from typing import ClassVar

# internal imports
from .._interfaces._actionset import AbstractActionset
from .._interfaces._chatmsg import AbstractChatMessage
from .._interfaces._input_server import AbstractInputServer
from .._shared.types import VerbParamDict
from ..virtual_input.input_server import LocalInputServer


# ==================================================================================================
class Actionset(AbstractActionset):
  '''
  Base class for Actionsets

  Subclasses will need to at least implement `translate_user_message_to_action`.
  '''
  # Class variables:
  name: ClassVar[str]
  # Instance variables:
  doc_url: str
  action_prefix: str
  player_index: int
  allow_changing_macros: bool
  macro_file: Path | None
  persistent_macros: bool
  input_server: AbstractInputServer
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    *,
    doc_url: str = '',
    action_prefix: str = '+',
    player_index: int = 0,
    allow_changing_macros: bool = False,
    macro_file: Path | None = None,
    persistent_macros: bool = False,
    input_server: AbstractInputServer | None = None,
  ) -> None:
    '''
    Base constructor, implementation used by subclasses.

    Caution, changes made here will cascade!
    '''
    self.doc_url = doc_url
    self.action_prefix = action_prefix
    self.player_index = player_index
    self.allow_changing_macros = allow_changing_macros
    self.macro_file = macro_file
    self.persistent_macros = persistent_macros
    if input_server is None:
      input_server = LocalInputServer()
    self.input_server = input_server
  # ----------------------------------------------------------------------------

  def message_is_command(self, msg: AbstractChatMessage) -> bool:
    '''
    Identify if the message contains an action command that has to be
    handled by the team's thread.
    '''
    return msg.message.startswith(self.action_prefix)
  # ----------------------------------------------------------------------------

  def translate_user_message_to_action(
    self,
    msg: AbstractChatMessage
  ) -> partial[None] | None:
    '''
    Interface for Team classes to convert a simple text message into
    the inputs that will have to be executed.

    MUST be implemented by subclasses!
    '''
    raise NotImplementedError
  # ----------------------------------------------------------------------------

  def random_action(self) -> partial[None]:
    '''
    When the team's queue is empty, random actions can be performed
    instead of sleeping.

    This function serves as a backend function, which takes care of
    selecting which random action to take.

    Overridable by subclasses, the default implementation only sleeps
    (for actionsets that don't have support for random actions)
    '''
    return partial(sleep, 0.1)
  # ----------------------------------------------------------------------------

  def get_macro_dict(self) -> dict[str, list[VerbParamDict]]:
    '''
    Get all currently stored macro without action prefix.

    Returns empty dict for classes that don't support macros.
    '''
    return {}
  # ----------------------------------------------------------------------------

  def set_macro_dict(self, new_macros: dict[str, list[VerbParamDict]]) -> None:
    '''
    Change currently stored macros to macros stored in `new_macro_dict`

    Does nothing for classes that don't support macros.
    '''
    pass
  # ----------------------------------------------------------------------------

  def load_macros_from_file(self) -> None:
    '''
    Update the local copy of `self.macro_dict` with the contents of
    `self.macro_file`.

    Does nothing for classes that don't support macros.
    '''
    pass
  # ----------------------------------------------------------------------------

  def save_macros_to_file(self) -> None:
    '''
    Update the contents of `self.macro_file` with the local copy of
    `self.macro_dict`.

    Does nothing for classes that don't support macros.
    '''
    pass
  # ----------------------------------------------------------------------------

  def add_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro from `msg` and add it to `macro_dict` if possible.

    Always return `False` in base class, since it has no macro support.
    '''
    return False
  # ----------------------------------------------------------------------------

  def change_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro from `msg` and change the same macro in `macro_dict`
    if possible.

    Always return `False` in base class, since it has no macro support.
    '''
    return False
  # ----------------------------------------------------------------------------

  def remove_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro_name from `msg` and remove it from `macro_dict` if possible.

    Always return `False` in base class, since it has no macro support.
    '''
    return False
  # ----------------------------------------------------------------------------

  def reload_macros(self) -> bool:
    '''
    Reload macros from macro file and discard any local changes
    '''
    return False
  # ----------------------------------------------------------------------------

  def validate(self) -> bool:
    '''
    Validate that object data is internally consistent.

    Intended to be used after __init__ to detect stuff like
    dict members not behaving correctly!
    '''
    return True
# ==================================================================================================
