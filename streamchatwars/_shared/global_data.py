'''
This module is a collection of global variables, encapsulated in a
singelton non-instance class.
'''
# native imports
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import ClassVar
from typing import ItemsView
from typing import KeysView
from typing import SupportsIndex
from typing import ValuesView

# internal imports
from .._interfaces._chatmsg import AbstractChatMessage
from .._interfaces._gamepads import AbstractGamepad
from .._interfaces._team import AbstractTeam
from .._interfaces._tts import AbstractTTSQueue
from .._interfaces._userlist import AbstractUserList
from .._shared.types import ChatLogDict
from .._shared.types import CommunityPointsPubSubDict
from .._shared.types import ConfigDict
from .._shared.types import ConsoleMessageDict
from .._shared.types import RedemptionDict
from .._shared.types import SessionLogDict
from .._shared.types import TeamLogDict
from ..events.events_states import GlobalEventStates
from ..session.channelpointlog import ChannelPointLog
from ..session.chatlog import ChatLog
from ..session.chatlog import TeamLog
from ..session.consolelog import CONSOLELOG
from ..session.consolelog import ConsoleLog


# ------------------------------------------------------------------------------
class DuplicateTeamNameError(KeyError):
  '''
  Raised when a team name is already in use.
  '''
  pass
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
def write_session(
  session_dict: SessionLogDict,
  filename: str | Path | None = None
) -> str:  # pragma: no cover
  '''
  Late import proxy function (allows mocking)
  '''
  # internal imports
  from ..config.json_utils import write_session
  return write_session(session_dict, filename)
# ------------------------------------------------------------------------------


# ==================================================================================================
class GlobalData:
  '''
  Non-instance singleton that contains all global data structures
  and their related access methods.
  '''
  # ==== Teams =====================================================================================
  class Teams:
    _all_teams_dict: ClassVar[dict[str, AbstractTeam]] = {}
    '''
    Dictionary of all teams, `{team_name: Team}`,
    where `team_name := Team.name.lower()`.

    Used by a lot of other modules.
    Doesn't change after initial assignment in the config module.
    '''

    @classmethod
    def add(cls, team: AbstractTeam) -> None:
      '''Add team to global collection of teams.'''
      if team.name.lower() in cls._all_teams_dict.keys():
        raise DuplicateTeamNameError(
          f'"{team.name}" already exists! '
          'Creating duplicate teams is not allowed!'
        )
      cls._all_teams_dict[team.name.lower()] = team
    # --------------------------------------------------------------------------

    @classmethod
    def get_by_name(cls, team_name: str) -> AbstractTeam | None:
      '''Return matching team for team_name if it exists, otherwise None.'''
      return cls._all_teams_dict.get(team_name.lower(), None)
    # --------------------------------------------------------------------------

    @classmethod
    def get_all_teams(cls) -> ValuesView[AbstractTeam]:
      '''Return a view of all teams.'''
      return cls._all_teams_dict.values()
    # --------------------------------------------------------------------------

    @classmethod
    def get_all_lowercase_names(cls) -> KeysView[str]:
      '''Return a view of lowercase names of all teams.'''
      return cls._all_teams_dict.keys()
    # --------------------------------------------------------------------------

    @classmethod
    def get_all_name_team_pairs(cls) -> ItemsView[str, AbstractTeam]:
      '''Return a view of tuples (lowercase team names, team) of all teams.'''
      return cls._all_teams_dict.items()
    # --------------------------------------------------------------------------

    @classmethod
    def get_list_of_original_names(cls) -> list[str]:
      '''
      Original case team names,
      since cls.__all_teams_dict keys are all lowercase.
      '''
      return [t.name for t in cls._all_teams_dict.values()]
    # --------------------------------------------------------------------------

    @classmethod
    def clear(cls) -> None:
      '''Remove all teams from global collection of teams.'''
      cls._all_teams_dict.clear()
  # ================================================================================================

  # ===== Users ====================================================================================
  class Users:
    _all_users_dict: ClassVar[dict[str, AbstractTeam | None]] = {}
    '''
    Dictionary of all users added to any team
    with reference to their respective team.
    Supports `add` and `discard` similar to `set`
    '''

    @classmethod
    def get_team(cls, user: str) -> AbstractTeam | None:
      '''
      Get the Team object that is assigned to `user` from the global registry.
      '''
      return cls._all_users_dict.get(user)
    # --------------------------------------------------------------------------

    @classmethod
    def add(cls, user: str, team: AbstractTeam | None = None) -> None:
      '''
      Adds `user` to the global registry and points to their assigned team.
      '''
      cls._all_users_dict[user] = team
    # --------------------------------------------------------------------------

    @classmethod
    def discard(cls, user: str) -> None:
      '''Remove `user` from global registry (if they are in there)'''
      cls._all_users_dict.pop(user, None)
    # --------------------------------------------------------------------------

    @classmethod
    def clear(cls) -> None:
      '''Remove all users from the global registry.'''
      cls._all_users_dict.clear()
    # --------------------------------------------------------------------------

    @classmethod
    def is_known(cls, user: str) -> bool:
      '''Is `user` part of the global registry?'''
      return user in cls._all_users_dict
  # ================================================================================================

  # ===== Prefix ===================================================================================
  class Prefix:
    class Action:
      _action_prefixes: ClassVar[set[str]] = set()
      '''
      Set of all action prefixes, allows to quickly discard non-action messages
      '''

      @classmethod
      def add(cls, prefix: str) -> None:
        '''
        Add action prefix to internal set for easy action detection in messages.
        '''
        cls._action_prefixes.add(prefix)
      # ------------------------------------------------------------------------

      @classmethod
      def clear(cls) -> None:
        '''Clear internal action prefix set.'''
        cls._action_prefixes.clear()
      # ------------------------------------------------------------------------

      @classmethod
      def message_is_action(cls, msg: AbstractChatMessage) -> bool:
        '''
        * `True` if `msg` starts with a valid action prefix.
        * Otherwise `False`.
        '''
        return any(
          msg.message.startswith(prefix) for prefix in cls._action_prefixes
        )
      # ------------------------------------------------------------------------

    class Command:
      _command_prefix: ClassVar[str] = '?'
      '''The prefix character used for chat commands.'''

      @classmethod
      def get(cls) -> str:
        '''Get the prefix character used for chat commands.'''
        return cls._command_prefix
      # ------------------------------------------------------------------------

      @classmethod
      def set(cls, prefix: str) -> None:
        '''Change prefix character used for chat commands.'''
        cls._command_prefix = prefix
      # ------------------------------------------------------------------------

      @classmethod
      def message_is_command(cls, msg: AbstractChatMessage) -> bool:
        '''
        * `True` if `msg` starts with command prefix.
        * Otherwise `False`.
        '''
        return msg.message.startswith(cls._command_prefix)
      # ------------------------------------------------------------------------

      @classmethod
      def split_message(
        cls,
        msg: AbstractChatMessage,
        sep: str | None = None,
        maxsplit: SupportsIndex = -1
      ) -> list[str]:
        '''Split msg.message into multiple parts without prefix'''
        return (
          msg
          .message[len(cls._command_prefix):]
          .split(sep=sep, maxsplit=maxsplit)
        )
  # ================================================================================================

  # ===== Gamepads =================================================================================
  class Gamepads:
    _gamepads: ClassVar[dict[int, AbstractGamepad]] = {}
    '''Global collection of all virtual gamepads.'''

    @classmethod
    def has_index(cls, index: int) -> bool:
      '''Is `index` a key in the global gamepad collection?'''
      return index in cls._gamepads
    # --------------------------------------------------------------------------

    @classmethod
    def add(cls, index: int, gamepad: AbstractGamepad) -> None:
      '''Add `gamepad` to the gamepad collection at `index`.'''
      if index not in cls._gamepads:
        cls._gamepads[index] = gamepad
    # --------------------------------------------------------------------------

    @classmethod
    def remove(cls, index: int) -> None:
      '''Remove gamepad at `index` from the gamepad collection.'''
      if index in cls._gamepads:
        cls._gamepads[index].__del__()
        del cls._gamepads[index]
    # --------------------------------------------------------------------------

    @classmethod
    def get(cls, index: int) -> AbstractGamepad | None:
      '''Return gamepad at `index` from the gamepad collection.'''
      return cls._gamepads.get(index, None)
    # --------------------------------------------------------------------------

    @classmethod
    def clear(cls) -> None:
      '''Remove all gamepads from the gamepad collection.'''
      cls._gamepads.clear()
  # ================================================================================================

  # ===== Operators ================================================================================
  class Operators:
    _operator_list: ClassVar[AbstractUserList]
    '''special UserList which includes all users with operator privileges'''

    @classmethod
    def create_list(cls) -> None:
      # internal imports
      from ..userdata.userlist import UserList
      cls._operator_list = UserList()
    # --------------------------------------------------------------------------

    @classmethod
    def add(cls, entry: str, team_channel_set: set[str] | None = None) -> None:
      '''Add entry (= user/group) to UserList of operators.'''
      cls._operator_list.add_to_list(entry, team_channel_set)
    # --------------------------------------------------------------------------

    @classmethod
    def clear(cls) -> None:
      '''Remove all entries from the operator list.'''
      try:
        cls._operator_list.clear()
      except AttributeError:
        pass  # skip if not initialized
    # --------------------------------------------------------------------------

    @classmethod
    def is_operator(cls, msg: AbstractChatMessage) -> bool:
      '''Membership test without revealing the internal operator list.'''
      return msg in cls._operator_list
  # ================================================================================================

  # ===== EventStates ==============================================================================
  class EventStates:
    '''Access functions for file event states (read-only)'''

    @classmethod
    def accept_input(cls) -> bool:
      '''
      Getter for `state_accept_input`
      '''
      return bool(GlobalEventStates.state_accept_input)
    # --------------------------------------------------------------------------

    @classmethod
    def random_action(cls) -> bool:
      '''
      Getter for `state_random_action`
      '''
      return bool(GlobalEventStates.state_random_action)
    # --------------------------------------------------------------------------

    @classmethod
    def delay_random(cls) -> float:
      '''
      Getter for `state_delay_random`
      '''
      if GlobalEventStates.state_delay_random is None:
        return 0.0  # No delay
      return GlobalEventStates.state_delay_random
  # ================================================================================================

  # ===== TTSQueue =================================================================================
  class TTSQueue:
    '''Proxy object to queue up TTS messages'''
    _tts_queue: ClassVar[AbstractTTSQueue]
    _enabled: ClassVar[bool] = False

    @classmethod
    def enable_tts(cls, enabled: bool = True) -> None:
      '''(De)activate TTS messages'''
      cls._enabled = enabled
    # --------------------------------------------------------------------------

    @classmethod
    def assign_queue_object(cls, tts_queue: AbstractTTSQueue) -> None:
      '''
      Assign the TTS queue object to the global variable.
      '''
      cls._tts_queue = tts_queue
    # --------------------------------------------------------------------------

    @classmethod
    def queue_tts_message(cls, text: str, user: str) -> None:
      '''
      Add a message to TTS queue
      '''
      if cls._enabled:
        cls._tts_queue.queue_tts_message(text, user)
  # ================================================================================================

  # ===== Session ==================================================================================
  class Session:
    '''
    Store information regarding the current session so it can be analyzed
    on a later date.
    '''
    _startdate: ClassVar[datetime] = datetime(1970, 1, 1, tzinfo=timezone.utc)
    # --------------------------------------------------------------------------

    @classmethod
    def startdate(cls) -> datetime:
      '''Getter for `_startdate`'''
      return cls._startdate
    # --------------------------------------------------------------------------

    @classmethod
    def start(cls) -> None:
      '''
      Start session.
      '''
      cls._startdate = datetime.now(tz=timezone.utc)
    # --------------------------------------------------------------------------

    @classmethod
    def dump(
      cls,
      config: ConfigDict | None = None,
      filename: str | Path | None = None,
    ) -> str:
      '''Dump all collected session infos in a single file.'''
      session_dict: SessionLogDict = {}
      if config is not None:
        session_dict['config'] = config
      console_log: list[ConsoleMessageDict] | None = cls.Console.export_list()
      if console_log is not None:
        session_dict['console'] = console_log
      channelpoint_log: list[CommunityPointsPubSubDict] | None
      channelpoint_log = cls.ChannelPoints.export_list()
      if channelpoint_log is not None:
        session_dict['channelpoints'] = channelpoint_log
      chat_log: ChatLogDict | None = cls.Chat.export_dict()
      if chat_log is not None:
        session_dict['chat'] = chat_log
      teams_log: dict[str, TeamLogDict] | None = cls.Teams.export_dict()
      if teams_log is not None:
        session_dict['teams'] = teams_log
      if session_dict:
        return write_session(session_dict, filename)
      return ''  # Return empty string to signify that no file has been written
    # --------------------------------------------------------------------------

    class Console:
      _log_console_messages: ClassVar[bool] = False
      _consolelog: ClassVar[ConsoleLog] = CONSOLELOG
      # ------------------------------------------------------------------------

      @classmethod
      def enable_consolelog(cls, enabled: bool = True) -> None:
        '''(De)activate console logging'''
        cls._log_console_messages = enabled
      # ------------------------------------------------------------------------

      @classmethod
      def log_message(cls, msg: str) -> None:
        '''Add msg to console log'''
        cls._consolelog.log_message(msg)
      # ------------------------------------------------------------------------

      @classmethod
      def export_list(cls) -> list[ConsoleMessageDict] | None:
        '''Dump complete log to auto-generated session file'''
        if cls._log_console_messages:
          return cls._consolelog.export_list()
        return None
      # ------------------------------------------------------------------------

      @classmethod
      def clear(cls) -> None:
        '''Clear consolelog.'''
        cls._consolelog.clear()
        cls._log_console_messages = False
    # --------------------------------------------------------------------------

    class Teams:
      _log_chat_messages: ClassVar[bool] = False
      _teamlog: ClassVar[dict[str, TeamLog]] = {}
      # ------------------------------------------------------------------------

      @classmethod
      def init_teamlogs(cls, enabled: bool = True) -> None:
        '''create TeamLogs based on global Teams data'''
        cls._log_chat_messages = enabled
        for team_name, team in GlobalData.Teams.get_all_name_team_pairs():
          cls._teamlog[team_name] = TeamLog(team.name)
      # ------------------------------------------------------------------------

      @classmethod
      def get_teamlog_by_name(cls, name: str) -> TeamLog | None:
        '''return TeamLog object for a given team name (all lowercase)'''
        return cls._teamlog.get(name.lower(), None)
      # ------------------------------------------------------------------------

      @classmethod
      def export_dict(cls) -> dict[str, TeamLogDict] | None:
        '''Dump complete log to auto-generated session file'''
        if cls._log_chat_messages:
          return {
            name: log.export_dict() for name, log in cls._teamlog.items()
          }
        return None
      # ------------------------------------------------------------------------

      @classmethod
      def clear(cls) -> None:
        '''Clear teamlogs.'''
        for teamlog in cls._teamlog.values():
          teamlog.clear()
        cls._teamlog.clear()
        cls._log_chat_messages = False
    # --------------------------------------------------------------------------

    class Chat:
      _log_chat_messages: ClassVar[bool] = False
      _chatlog: ClassVar[ChatLog] = ChatLog()
      # ------------------------------------------------------------------------

      @classmethod
      def enable_chatlog(cls, enabled: bool = True) -> None:
        '''(De)activate chat logging'''
        cls._log_chat_messages = enabled
      # ------------------------------------------------------------------------

      @classmethod
      def log_message(cls, msg: AbstractChatMessage) -> None:
        '''Add general msg to chat log'''
        if cls._log_chat_messages:
          cls._chatlog.log_message(msg)
      # ------------------------------------------------------------------------

      @classmethod
      def log_notice(cls, msg: AbstractChatMessage) -> None:
        '''Add notice to chat log'''
        if cls._log_chat_messages:
          cls._chatlog.log_notice(msg)
      # ------------------------------------------------------------------------

      @classmethod
      def log_action_message(
        cls,
        msg: AbstractChatMessage,
        team: AbstractTeam
      ) -> None:
        '''Add action msg to chat log'''
        if cls._log_chat_messages:
          teamlog: TeamLog | None = (
            GlobalData.Session.Teams.get_teamlog_by_name(team.name)
          )
          if teamlog is not None:
            teamlog.log_action_message(msg)
          cls._chatlog.log_action_message(msg)
      # ------------------------------------------------------------------------

      @classmethod
      def log_executed_message(
        cls,
        msg: AbstractChatMessage,
        team: AbstractTeam
      ) -> None:
        '''Add executed action msg to chat log'''
        if cls._log_chat_messages:
          teamlog: TeamLog | None = (
            GlobalData.Session.Teams.get_teamlog_by_name(team.name)
          )
          if teamlog is not None:
            teamlog.log_executed_message(msg)
          cls._chatlog.log_executed_message(msg)
      # ------------------------------------------------------------------------

      @classmethod
      def log_command_message(cls, msg: AbstractChatMessage) -> None:
        '''Add general msg to chat log'''
        if cls._log_chat_messages:
          cls._chatlog.log_command_message(msg)
      # ------------------------------------------------------------------------

      @classmethod
      def export_dict(cls) -> ChatLogDict | None:
        '''Dump complete log to auto-generated session file'''
        if cls._log_chat_messages:
          return cls._chatlog.export_dict()
        return None
      # ------------------------------------------------------------------------

      @classmethod
      def clear(cls) -> None:
        '''Clear chatlog.'''
        cls._chatlog.clear()
        cls._log_chat_messages = False
    # --------------------------------------------------------------------------

    class ChannelPoints:
      _log_channelpoint_messages: ClassVar[bool] = False
      _channelpointlog: ClassVar[ChannelPointLog] = ChannelPointLog()
      # ------------------------------------------------------------------------

      @classmethod
      def is_enabled(cls) -> bool:
        '''Return True if channelpoint logging is enabled'''
        return cls._log_channelpoint_messages
      # ------------------------------------------------------------------------

      @classmethod
      def enable_channelpointlog(cls, enabled: bool = True) -> None:
        '''(De)activate channel point logging'''
        cls._log_channelpoint_messages = enabled
      # ------------------------------------------------------------------------

      @classmethod
      def log_message(cls, msg: CommunityPointsPubSubDict) -> None:
        '''Add msg to channel point log'''
        cls._channelpointlog.log_message(msg)
      # ------------------------------------------------------------------------

      @classmethod
      def export_list(cls) -> list[CommunityPointsPubSubDict] | None:
        '''Dump complete log to auto-generated session file'''
        if cls._log_channelpoint_messages:
          return cls._channelpointlog.export_list()
        return None
      # ------------------------------------------------------------------------

      @classmethod
      def get_user_redeems(cls) -> list[RedemptionDict]:
        '''Get a list of all user redeems.'''
        return cls._channelpointlog.get_user_redeems()
      # ------------------------------------------------------------------------

      @classmethod
      def clear(cls) -> None:
        '''Clear channel point log.'''
        cls._channelpointlog.clear()
        cls._log_channelpoint_messages = False
  # ================================================================================================
