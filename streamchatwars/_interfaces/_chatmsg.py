'''
ChatMessage Interface
Provide an Abstract Base Class as reference for other modules.
'''
from __future__ import annotations

# native imports
from abc import ABC
from abc import abstractmethod
from dataclasses import KW_ONLY
from dataclasses import dataclass
from uuid import UUID

# internal imports
from .._interfaces._chatbot import AbstractMessageSender
from .._shared.primitive_types import seconds
from .._shared.types import ChatMessageDict


# ==================================================================================================
# This class will create possibly thousands of objects during the program's
# runtime, that's why we are using __slots__ to hopefully save a bit
# on memory and improve performance.
@dataclass(slots=True)
class _DataclassMixin:
  '''
  We need to use a Mixin here because otherwise Mypy would complain when it
  sees a dataclass with @abstractmethod decorators.

  `error: Only concrete class can be given where
  "Type[AbstractChatMessage]" is expected  [misc]`

  See also Mypy issue #5374: https://github.com/python/mypy/issues/5374
  '''
  # Instance variables:
  _: KW_ONLY
  id: UUID
  msg_type: str
  timestamp: seconds
  user: str
  channel: str
  message: str
  tags: dict[str, str]
  parent: AbstractMessageSender | None
# ------------------------------------------------------------------------------


class AbstractChatMessage(ABC, _DataclassMixin):
  '''
  This class is very similar to Event class of the irc.client module,
  except that we reverse some of the mind-boggling data structures to make
  them fit our purpose.

  If you want to create a ChatMessage object from irc.client.Event data,
  then use the from_event() factory class method.
  '''
  @abstractmethod
  def as_dict(self) -> ChatMessageDict:
    '''
    Create a dictionary based on this object.

    Convert `id` to str and don't include `parent`
    '''
    raise NotImplementedError  # pragma: no cover
# ==================================================================================================
