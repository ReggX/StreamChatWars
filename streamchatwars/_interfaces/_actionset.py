'''
Actionset Interface
Provide an Abstract Base Class as reference for other modules.
'''

from __future__ import annotations

# native imports
from abc import ABC
from abc import abstractmethod
from functools import partial
from pathlib import Path
from typing import ClassVar

# internal imports
from .._shared.types import VerbParamDict
from ._chatmsg import AbstractChatMessage
from ._input_server import AbstractInputServer


# ==================================================================================================
class ActionsetValidationError(Exception):
  pass
# ==================================================================================================


# ==================================================================================================
class AbstractActionset(ABC):
  '''Interface class for Actionsets'''
  # Class variables:
  name: ClassVar[str]
  # Instance variables:
  doc_url: str
  action_prefix: str
  player_index: int
  input_server: AbstractInputServer
  # ----------------------------------------------------------------------------

  @abstractmethod
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
    pass  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def message_is_command(self, msg: AbstractChatMessage) -> bool:
    '''
    Identify if the message contains an action command that has to be
    handled by the team's thread.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def translate_user_message_to_action(
    self,
    msg: AbstractChatMessage
  ) -> partial[None] | None:
    '''
    Interface for Team classes to convert a simple text message into
    the inputs that will have to be executed.

    MUST be implemented by subclasses!
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def random_action(self) -> partial[None]:
    '''
    When the team's queue is empty, random actions can be performed
    instead of sleeping.

    This function serves as a backend function, which takes care of
    selecting which random action to take.

    Overridable by subclasses, the default implementation only sleeps
    (for actionsets that don't have support for random actions)
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def get_macro_dict(self) -> dict[str, list[VerbParamDict]]:
    '''
    Get all currently stored macro without action prefix.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def set_macro_dict(self, new_macros: dict[str, list[VerbParamDict]]) -> None:
    '''
    Change currently stored macros to macros stored in `new_macro_dict`
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def load_macros_from_file(self) -> None:
    '''
    Update the local copy of `self.macro_dict` with the contents of
    `self.macro_file`
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def save_macros_to_file(self) -> None:
    '''
    Update the contents of `self.macro_file` with the local copy of
    `self.macro_dict`
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def add_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro from `msg` and add it to `macro_dict` if possible.

    Always return `False` in base class, since it has no macro support.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def change_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro from `msg` and change the same macro in `macro_dict`
    if possible.

    Always return `False` in base class, since it has no macro support.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def remove_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro_name from `msg` and remove it from `macro_dict` if possible.

    Always return `False` in base class, since it has no macro support.
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def reload_macros(self) -> bool:
    '''
    Reload macros from macro file and discard any local changes
    '''
    raise NotImplementedError  # pragma: no cover
  # ----------------------------------------------------------------------------

  @abstractmethod
  def validate(self) -> bool:
    '''
    Validate that object data is internally consistent.

    Intended to be used after __init__ to detect stuff like
    dict members not behaving correctly!
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
