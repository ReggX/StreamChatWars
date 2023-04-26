'''
This module contains data classes that store received messages.
It's imported into _shared.global_data, which is why need
to pay special attention to not import anything that could result
circular imports!
'''

# native imports
from dataclasses import dataclass
from dataclasses import field

# internal imports
from .._interfaces._chatmsg import AbstractChatMessage
from .._shared.types import ChatLogDict
from .._shared.types import TeamLogDict


# ==================================================================================================
@dataclass
class ChatLog:
  '''
  Collect all chat mesages in a single data instance to store
  them for later analysis.
  '''
  all_messages: list[AbstractChatMessage] = field(
    default_factory=list, init=False
  )
  '''list of all messages sent by all users'''
  all_notices: list[AbstractChatMessage] = field(
    default_factory=list, init=False
  )
  '''list of all notices sent by the server'''
  action_messages: list[AbstractChatMessage] = field(
    default_factory=list, init=False
  )
  '''list of messages containing action commands sent by all users'''
  executed_messages: list[AbstractChatMessage] = field(
    default_factory=list, init=False
  )
  '''
  list of messages containing action commands that were executed
  sent by all users.
  '''
  command_messages: list[AbstractChatMessage] = field(
    default_factory=list, init=False
  )
  '''list of messages containing chat commands sent by all users'''
  # ----------------------------------------------------------------------------

  def log_message(self, msg: AbstractChatMessage) -> None:
    '''Add general msg to chat log'''
    self.all_messages.append(msg)
  # ----------------------------------------------------------------------------

  def log_notice(self, msg: AbstractChatMessage) -> None:
    '''Add general msg to chat log'''
    self.all_notices.append(msg)
  # ----------------------------------------------------------------------------

  def log_action_message(self, msg: AbstractChatMessage) -> None:
    '''Add action msg to chat log'''
    self.action_messages.append(msg)
  # ----------------------------------------------------------------------------

  def log_executed_message(self, msg: AbstractChatMessage) -> None:
    '''Add executed action msg to chat log'''
    self.executed_messages.append(msg)
  # ----------------------------------------------------------------------------

  def log_command_message(self, msg: AbstractChatMessage) -> None:
    '''Add general msg to chat log'''
    self.command_messages.append(msg)
  # ----------------------------------------------------------------------------

  def export_dict(self) -> ChatLogDict:
    '''Export messages into a JSON serializable dict.'''
    return {
      'messages': {
        (d := msg.as_dict())['id']: d
        for msg in self.all_messages
      },
      'notices': {
        (d := msg.as_dict())['id']: d
        for msg in self.all_notices
      },
      'actions': [
        msg.as_dict()['id'] for msg in self.action_messages
      ],
      'executed_actions': [
        msg.as_dict()['id'] for msg in self.executed_messages
      ],
      'commands': [
        msg.as_dict()['id'] for msg in self.command_messages
      ],
    }
  # ----------------------------------------------------------------------------

  def clear(self) -> None:
    '''Clear out all lists.'''
    self.all_messages.clear()
    self.all_notices.clear()
    self.action_messages.clear()
    self.executed_messages.clear()
    self.command_messages.clear()
# ==================================================================================================


# ==================================================================================================
@dataclass
class TeamLog:
  '''
  Collect team-related data for later analysis.
  '''
  name: str
  action_messages: list[AbstractChatMessage] = field(
    default_factory=list, init=False
  )
  '''list of messages containing action commands sent by all users'''
  executed_messages: list[AbstractChatMessage] = field(
    default_factory=list, init=False
  )
  '''
  list of messages containing action commands that were executed
  sent by all users.
  '''
  # ----------------------------------------------------------------------------

  def log_action_message(self, msg: AbstractChatMessage) -> None:
    '''Add action msg to chat log'''
    self.action_messages.append(msg)
  # ----------------------------------------------------------------------------

  def log_executed_message(self, msg: AbstractChatMessage) -> None:
    '''Add executed action msg to chat log'''
    self.executed_messages.append(msg)
  # ----------------------------------------------------------------------------

  def export_dict(self) -> TeamLogDict:
    '''Export messages into a JSON serializable dict.'''
    return {
      'name': self.name,
      'actions': [
        msg.as_dict()['id'] for msg in self.action_messages
      ],
      'executed_actions': [
        msg.as_dict()['id'] for msg in self.executed_messages
      ],
    }
  # ----------------------------------------------------------------------------

  def clear(self) -> None:
    '''Clear out all lists.'''
    self.action_messages.clear()
    self.executed_messages.clear()
# ==================================================================================================
