'''
This module has been outsourced form chatbot to prevent circular imports.
Contains the ChatMessage class used to pass around chat messages to other
modules.
'''
from __future__ import annotations

# native imports
from dataclasses import KW_ONLY
from dataclasses import dataclass
from dataclasses import field
from time import time
from typing import TypeVar
from uuid import UUID
from uuid import uuid4

# pip imports
from irc.client import Event

# internal imports
from .._interfaces._chatbot import AbstractMessageSender
from .._interfaces._chatmsg import AbstractChatMessage
from .._shared.primitive_types import seconds
from .._shared.types import ChatMessageDict


# ------------------------------------------------------------------------------
ChatMsg = TypeVar('ChatMsg', bound='ChatMessage')
# ------------------------------------------------------------------------------


# ==================================================================================================
# This class will create possibly thousands of objects during the program's
# runtime, that's why we are using __slots__ to hopefully save a bit
# on memory and improve performance.
@dataclass(slots=True)
class ChatMessage(AbstractChatMessage):
  '''
  This class is very similar to Event class of the irc.client module,
  except that we reverse some of the mind-boggling data structures to make
  them fit our purpose.

  If you want to create a ChatMessage object from irc.client.Event data,
  then use the from_event() factory class method.
  '''
  # Instance variables:
  _: KW_ONLY
  id: UUID = field(default_factory=lambda: uuid4())
  msg_type: str = field(default='pubmsg')
  timestamp: seconds = field(default_factory=lambda: time())
  user: str
  channel: str
  message: str
  tags: dict[str, str]
  parent: AbstractMessageSender | None = field(default=None)
  # ----------------------------------------------------------------------------

  @classmethod
  def from_event(
    cls: type[ChatMsg],
    event: Event,
    *,
    timestamp: seconds | None = None,
    parent: AbstractMessageSender | None = None
  ) -> ChatMsg:  # TODO: Python 3.11 replace with `Self`, waiting on mypy...
    '''Create a ChatMessage object from IRC Event data.'''
    msg_type: str = event.type
    # downstream functions expect user/channel to be all lowercase
    user: str = str(event.source).split("!")[0].lower()
    channel: str = str(event.target).lower()
    message: str
    # message is enveloped as a list: event.arguments = [message]
    if event.arguments:
      message = event.arguments[0]
    else:
      message = ''
    # event.tags is a list of dictionaries that all are structured in
    # {'key': '<key value>', 'value': '<value value>'} pairs.
    # This is obviously stupid, so we reverse it into a normal dict.
    tags: dict[str, str] = {
      kv_pair['key']: kv_pair['value'] for kv_pair in event.tags
    }
    id: str | None = tags.get('id', None)
    uuid: UUID = uuid4() if id is None else UUID(id)
    if timestamp is None:
      timestamp = time()

    return cls(
      msg_type=msg_type,
      id=uuid,
      timestamp=timestamp,
      user=user,
      channel=channel,
      message=message,
      tags=tags,
      parent=parent
    )
  # ----------------------------------------------------------------------------

  def as_dict(self) -> ChatMessageDict:
    '''
    Create a dictionary based on this object.

    Convert `id` to str and don't include `parent`
    '''
    d: ChatMessageDict = {
      'id': str(self.id),
      'msg_type': self.msg_type,
      'timestamp': self.timestamp,
      'user': self.user,
      'channel': self.channel,
      'message': self.message,
      'tags': self.tags
    }
    return d
# ==================================================================================================
