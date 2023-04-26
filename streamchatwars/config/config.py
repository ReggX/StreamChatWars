'''
This modules handles reading and validating config/credential files
and includes functions to transform the JSON Mappings into usable data
for the rest of the package.
'''

# native imports
import asyncio
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Coroutine
from typing import Literal
from typing import TypeVar
from typing import cast

# internal imports
from .._interfaces._actionset import AbstractActionset
from .._interfaces._actionset import ActionsetValidationError
from .._interfaces._team import AbstractTeam
from .._interfaces._team import TeamCreationError
from .._shared.constants import DEFAULT_EVENT_FOLDER
from .._shared.constants import DEFAULT_VOICE_ID
from .._shared.global_data import GlobalData
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from .._shared.primitive_types import millisecs
from .._shared.primitive_types import seconds
from .._shared.types import SCHEMA_MAPPING
from .._shared.types import ActionsetConfigDict
from .._shared.types import CommandsConfigDict
from .._shared.types import ConfigDict
from .._shared.types import CredentialDict
from .._shared.types import EventsConfigDict
from .._shared.types import FileEventsConfigDict
from .._shared.types import HotkeysConfigDict
from .._shared.types import InputServerConfigDict
from .._shared.types import IrcConfigDict
from .._shared.types import SessionlogConfigDict
from .._shared.types import TeamConfigDict
from .._shared.types import TTSConfigDict
from .._shared.types import TwitchChatCredentialDict
from ..chat.commands import get_all_commands
from ..teams.functions import create_combined_team_class
from ..userdata.userlist import SpecialGroupsContainer
from ..virtual_input.input_server import InputServer
from .json_utils import InvalidCredentialsError
from .json_utils import decode_credential
from .json_utils import read_config_and_credentials
from .json_utils import read_config_schema_file
from .json_utils import read_config_schema_template_file
from .json_utils import read_snapshot_schema_file
from .json_utils import read_snapshot_schema_template_file
from .json_utils import write_config_schema_file
from .json_utils import write_snapshot_schema_file
from .presets import ACTIONSETS_DICT  # base classes
from .presets import INPUTSERVER_DICT
from .presets import TEAMS_DICT


def update_config_schema_file() -> None:
  '''
  Since Actionsets, Teams and Userlists are dynamically created,
  verification of JSON files has to be equally dynamic.

  This function creates `CONFIG_SCHEMA_FILE` by loading template
  JSON schema data stored in `CONFIG_SCHEMA_TEMPLATE_FILE` and modifying
  the fields that are relevant to the dynamic data listed above.

  If the existing `CONFIG_SCHEMA_FILE` does not match the generated
  json data, its contents will be replaced and overwritten.
  '''
  # ----- Read files -----
  schema_data: SCHEMA_MAPPING = read_config_schema_file()
  template_data: SCHEMA_MAPPING = read_config_schema_template_file()

  # ----- Modify template data -----
  teams_enum = [name[:-5] for name in TEAMS_DICT.keys()]
  actionsets_enum = [name[:-10] for name in ACTIONSETS_DICT.keys()]
  group_container = SpecialGroupsContainer()
  special_group_enum = [group for group in group_container.mapping.keys()]
  special_group_pattern = group_container.REGEX.pattern
  command_enum = get_all_commands()

  # Team Classes
  template_data["$defs"]["team_type_single"]["enum"] = teams_enum

  # Actionset Classes
  template_data["$defs"]["actionset_type"]["enum"] = actionsets_enum

  # Special Groups
  template_data["$defs"]["special_group_enum"]["enum"] = special_group_enum
  template_data["$defs"]["special_group_regex"]["pattern"] = (
    special_group_pattern
  )

  # Commands whitelist and blacklist
  template_data["$defs"]["command_enum"]["enum"] = command_enum

  # ----- Write modified template data to file -----
  # (Only write file if there are actual changes)
  if schema_data != template_data:
    write_config_schema_file(template_data)
# ------------------------------------------------------------------------------


def update_snapshot_schema_file() -> None:
  '''
  Since Userlists are dynamically created,
  verification of JSON files has to be equally dynamic.

  This function creates `SNAPSHOT_SCHEMA_FILE` by loading template
  JSON schema data stored in `SNAPSHOT_SCHEMA_TEMPLATE_FILE` and modifying
  the fields that are relevant to the dynamic data listed above.

  If the existing `SNAPSHOT_SCHEMA_FILE` does not match the generated
  json data, its contents will be replaced and overwritten.
  '''
  # ----- Read files -----
  schema_data: SCHEMA_MAPPING = read_snapshot_schema_file()
  template_data: SCHEMA_MAPPING = read_snapshot_schema_template_file()

  # ----- Modify template data -----
  group_container = SpecialGroupsContainer()
  groups_dict = {
    "description": "Mapping of groups to relevant channels",
    "type": "object",
    "properties": {
      group: {
        "description": f"Special group {group}",
        "type": "array",
        "items": {
          "$ref": "#/$defs/items"
        }
      }
      for group in group_container.mapping.keys()
    }
  }
  template_data["$defs"]["groups"] = groups_dict

  # ----- Write modified template data to file -----
  # (Only write file if there are actual changes)
  if schema_data != template_data:
    write_snapshot_schema_file(template_data)
# ------------------------------------------------------------------------------


def read_json_configs(
  config_arg: str | None = None,
  credential_arg: str | None = None
) -> tuple[ConfigDict, CredentialDict]:
  '''
  Read and validate JSON configuration files, return Mappings.

  Update config and/or snapshot schema file if outdated.
  '''
  # Update JSON schema if necessary
  update_config_schema_file()
  update_snapshot_schema_file()
  # Read config and credentials from files
  config: ConfigDict
  credentials: CredentialDict
  config, credentials = read_config_and_credentials(config_arg, credential_arg)
  return config, credentials
# ------------------------------------------------------------------------------


def get_team_class(team_type: str | None) -> type[AbstractTeam]:
  '''
  translate string to Team subclass

  Raise `ValueError` if class doesn't exit.
  (Shouldn't happen after config validation)
  '''
  team_class: type[AbstractTeam] | None = TEAMS_DICT.get(
    f"{team_type}_Team"
  )
  if team_class is None:
    raise ValueError(
      f"Team type {team_type!r} does not match any existing types"
    )
  return team_class
# ------------------------------------------------------------------------------


def get_actionset_class(actionset_type: str | None) -> type[AbstractActionset]:
  '''
  translate string to Actionset subclass

  Raise `ValueError` if class doesn't exit.
  (Shouldn't happen after config validation)
  '''
  actionset_class: type[AbstractActionset] | None = ACTIONSETS_DICT.get(
    f"{actionset_type}_Actionset"
  )
  if actionset_class is None:
    raise ValueError(
      f"Actionset type {actionset_type!r} does not match any existing types"
    )
  return actionset_class
# ------------------------------------------------------------------------------


def get_input_server_class(input_server_type: str | None) -> type[InputServer]:
  '''
  translate string to InputServer subclass

  Raise `ValueError` if class doesn't exit.
  (Shouldn't happen after config validation)
  '''
  input_server_class: type[InputServer] | None = INPUTSERVER_DICT.get(
    str(input_server_type)
  )
  if input_server_class is None:
    raise ValueError(
      f"Inputserver type {input_server_type!r} does not match any existing types"
    )
  return input_server_class
# ------------------------------------------------------------------------------


def create_input_server(
  input_server_dict: InputServerConfigDict
) -> InputServer:
  '''
  Create a new InputServer instance and set relevant data from config.
  '''
  server_type: str = input_server_dict.get('type', 'local')
  input_server_class: type[InputServer] = get_input_server_class(server_type)
  host: str = input_server_dict.get('host', 'localhost')
  port: int = int(input_server_dict.get('port', 33000))
  encryption_key: str = input_server_dict.get('encryption_key', '')
  encryption_mode: str = input_server_dict.get('encryption_mode', 'AES-GCM')
  if server_type == 'local':
    return input_server_class()
  else:
    return input_server_class(
      host=host,
      port=port,
      encryption_key=encryption_key,
      encryption_mode=encryption_mode
    )
# ------------------------------------------------------------------------------


def create_actionset(actionset_dict: ActionsetConfigDict) -> AbstractActionset:
  '''
  Create a new Actionset instance and set relevant data from config.
  '''
  actionset_class: type[AbstractActionset] = get_actionset_class(
    actionset_dict.get('type')
  )
  doc_url: str = actionset_dict.get('doc_url', '')
  action_prefix: str = actionset_dict.get('action_prefix', '+')
  player_index: int = int(actionset_dict.get('player_index', 0))
  allow_changing_macros: bool = bool(
    actionset_dict.get('allow_changing_macros', False)
  )
  macro_file_str: str = actionset_dict.get('macro_file', '')
  macro_file: Path | None = Path(macro_file_str) if macro_file_str else None
  if macro_file and not macro_file.exists():
    thread_print(ColorText.error(
      f"Error when trying to create Actionset {actionset_class.name}\n"
      f"Unable to find macro file {macro_file.absolute()}"
    ), flush=True)
    raise FileNotFoundError(
      f"Error when trying to create Actionset {actionset_class.name}: "
      f"No macro file found in {macro_file.absolute()}"
    )
  persistent_macros: bool = bool(
    actionset_dict.get('persistent_macros', False)
  )
  input_server_dict: InputServerConfigDict = (
    actionset_dict.get('input_server', {})
  )
  input_server: InputServer = create_input_server(input_server_dict)
  actionset: AbstractActionset = actionset_class(
    doc_url=doc_url,
    action_prefix=action_prefix,
    player_index=player_index,
    allow_changing_macros=allow_changing_macros,
    macro_file=macro_file,
    persistent_macros=persistent_macros,
    input_server=input_server,
  )
  if not actionset.validate():
    # Should raise ActionsetValidationError by itself, but in case it doesn't:
    thread_print(ColorText.error(
      f"Error when trying to validate Actionset {actionset.name}\n"
      "Please make sure that its internal variables don't mismatch!"
    ), flush=True)
    raise ActionsetValidationError(
      f"Error when trying to validate Actionset {actionset.name}"
    )
  return actionset
# ------------------------------------------------------------------------------


_T = TypeVar('_T', TeamConfigDict, ActionsetConfigDict, InputServerConfigDict)


def merged_dict(original_dict: _T, default_dict: _T) -> _T:
  EMPTY_DICT: _T = cast(_T, {})
  combined_dict = default_dict.copy()
  for key, value in original_dict.items():
    if isinstance(value, Mapping):
      combined_dict[key] = merged_dict(  # type: ignore[literal-required]
        original_dict[key],  # type: ignore[literal-required]
        default_dict.get(key, EMPTY_DICT),
      )
    else:
      combined_dict[key] = original_dict[key]  # type: ignore[literal-required]
  return combined_dict
# ------------------------------------------------------------------------------


def create_team(
  team_dict: TeamConfigDict,
  default_team_data: TeamConfigDict,
) -> AbstractTeam:
  '''
  Create a new Team instance and set relevant data from config.
  '''
  td: TeamConfigDict = merged_dict(team_dict, default_team_data)

  raw_team_type: str | list[str] | None = td.get('type', None)
  if raw_team_type is None:
    raise ValueError(
      f"Team type is not defined in config for team {td.get('name', '')}"
    )
  team_class: type[AbstractTeam]
  if isinstance(raw_team_type, str):
    team_class = get_team_class(raw_team_type)
  elif len(raw_team_type):
    team_class = create_combined_team_class(*[
      get_team_class(class_type)
      for class_type in raw_team_type
    ])
  else:
    raise ValueError(
      f"Team type {raw_team_type!r} does not match any "
      "existing type (combination)."
    )

  team_name: str = td.get('name', '')
  queue_length: int = int(td.get('queue_length', 10))
  hidden: bool = bool(td.get('hidden', False))
  joinable: bool = bool(td.get('joinable', False))
  leavable: bool = bool(td.get('leavable', False))
  exclusive: bool = bool(td.get('exclusive', True))
  use_random_inputs: bool = td.get('use_random_inputs', False)
  spam_protection: bool = bool(td.get('spam_protection', True))
  pattern: str = td.get('pattern', '')
  number: int = td.get('number', 1)
  chan_list: list[str] = td.get('channels', [])
  team_channel_set: set[str] = set()
  chan: str
  for chan in chan_list:
    chan = str(chan).lower()
    chan = chan if chan.startswith('#') else f'#{chan}'
    team_channel_set.add(chan)
  user_whitelist: list[str] = [
    str(user).lower() for user in td.get('user_whitelist', [])
  ]
  user_blacklist: list[str] = [
    str(user).lower() for user in td.get('user_blacklist', [])
  ]
  actionset_dict: ActionsetConfigDict = td.get('actionset', {})
  actionset: AbstractActionset = create_actionset(actionset_dict)
  GlobalData.Prefix.Action.add(actionset.action_prefix)
  team: AbstractTeam = team_class(
    name=team_name,
    channels=team_channel_set,
    actionset=actionset,
    hidden=hidden,
    queue_length=queue_length,
    use_random_inputs=use_random_inputs,
    joinable=joinable,
    leavable=leavable,
    exclusive=exclusive,
    user_whitelist=user_whitelist,
    user_blacklist=user_blacklist,
    spam_protection=spam_protection,
    pattern=pattern,
    number=number
  )
  return team
# ------------------------------------------------------------------------------


def build_teams(config: ConfigDict) -> None:
  '''
  Create all teams from config data and return a list of all channels
  associated with those teams.

  BEWARE: Team creation is done in parallel, which means the order in the
  global team list may not necessarily reflect the order they were defined
  in the config file.
  '''
  default_team_data: TeamConfigDict = config.get('default_team_data', {})
  team_dict_list: list[TeamConfigDict] = config.get('teams', [])
  if not team_dict_list:
    raise TeamCreationError("Must have at least one team!")
  with ThreadPoolExecutor(max_workers=len(team_dict_list)) as executor:
    async def single_task(
      team_dict: TeamConfigDict,
    ) -> AbstractTeam:
      return await asyncio.get_running_loop().run_in_executor(
        executor,
        create_team,
        team_dict,
        default_team_data,
      )

    async def all_tasks(
      team_dict_list: list[TeamConfigDict],
    ) -> list[AbstractTeam]:
      task_list: list[Coroutine[None, None, AbstractTeam]] = [
        single_task(team_dict) for team_dict in team_dict_list
      ]
      teams_list = await asyncio.gather(*task_list)
      # need cast here because mypy can't keep up with * unpack operator,
      # returns list[Any] instead
      return cast(list[AbstractTeam], teams_list)

    teams = asyncio.run(all_tasks(team_dict_list))
    for team in teams:
      GlobalData.Teams.add(team)
      thread_print(ColorText.info(
        f'> Created Team "{team.name}" with Actionset "{team.actionset.name}" '
        f'with Input Server type "{team.actionset.input_server.type}"'
      ))
# ------------------------------------------------------------------------------


def build_operator_list(config: ConfigDict, channel_set: set[str]) -> None:
  '''
  Build the operator privilege list from config data.
  '''
  GlobalData.Operators.create_list()
  entry: str
  for entry in config.get('operators', ['$broadcaster']):
    GlobalData.Operators.add(entry, channel_set)
# ------------------------------------------------------------------------------


# ==================================================================================================
@dataclass
class IRC_Settings:
  '''
  Dataclass for storing IRC-related settings
  '''
  host: str
  port: int
  message_interval: float
  connection_timeout: float
  join_rate_limit_amount: int
  join_rate_limit_time: float
  channel_set: set[str]
  username: str
  oauth_token: str
# ==================================================================================================


def extract_irc_settings(
  config: ConfigDict,
  credentials: TwitchChatCredentialDict,
  channel_set: set[str]
) -> IRC_Settings:
  '''
  Create a new IRC_Settings instance and set relevant data from config.
  '''
  irc_dict: IrcConfigDict = config.get('irc', {})
  host: str = irc_dict.get('host', "irc.chat.twitch.tv")
  port: int = int(irc_dict.get('port', 6697))
  username = decode_credential(credentials.get('username'), None)
  oauth_token = decode_credential(credentials.get('oauth_token'), None)
  if username is None or oauth_token is None:
    raise InvalidCredentialsError
  oauth_token = (
    oauth_token
    if oauth_token.startswith('oauth:') else
    f'oauth:{oauth_token}'
  )
  message_interval: float = float(irc_dict.get('message_interval', 3))
  connection_timeout: float = float(irc_dict.get('connection_timeout', 10))
  join_rate_limit_amount: int = int(irc_dict.get('join_rate_limit_amount', 18))
  join_rate_limit_time: float = float(irc_dict.get('join_rate_limit_time', 11))
  return IRC_Settings(
    host=host,
    port=port,
    message_interval=message_interval,
    connection_timeout=connection_timeout,
    join_rate_limit_amount=join_rate_limit_amount,
    join_rate_limit_time=join_rate_limit_time,
    channel_set=channel_set,
    username=username,
    oauth_token=oauth_token,
  )


# ==================================================================================================
@dataclass
class Sessionlog_Settings:
  '''
  Dataclass for storing Sessionlog-related settings
  '''
  enable_consolelog: bool
  enable_chatlog: bool
  enable_channelpointlog: bool
  enable_periodic_dumps: bool
  dumping_interval: seconds
  counter_cap: int
# ==================================================================================================


def extract_sessionlog_settings(
  config: ConfigDict
) -> Sessionlog_Settings:
  '''
  Create a new Sessionlog_Settings instance and set relevant data from config.
  '''
  sessionlog_dict: SessionlogConfigDict = config.get('sessionlog', {})
  enable_consolelog: bool = sessionlog_dict.get('enable_consolelog', False)
  enable_chatlog: bool = sessionlog_dict.get('enable_chatlog', False)
  enable_channelpointlog: bool = sessionlog_dict.get(
    'enable_channelpointlog',
    False
  )
  enable_periodic_dumps: bool = sessionlog_dict.get(
    'enable_periodic_dumps',
    False
  )
  dumping_interval: seconds = sessionlog_dict.get('dumping_interval', 15 * 60)
  counter_cap: int = sessionlog_dict.get('counter_cap', 2)
  return Sessionlog_Settings(
    enable_consolelog=enable_consolelog,
    enable_chatlog=enable_chatlog,
    enable_channelpointlog=enable_channelpointlog,
    enable_periodic_dumps=enable_periodic_dumps,
    dumping_interval=dumping_interval,
    counter_cap=counter_cap,
  )


# ==================================================================================================
@dataclass
class FileEvent_Settings:
  '''
  Dataclass for storing File-Event-related settings
  '''
  enabled: bool
  path: Path


@dataclass
class Hotkey_Settings:
  '''
  Dataclass for storing Hotkey-related settings
  '''
  failsafe: str
  accept_input: str
  random_action: str
  reset_teams: str
  random_delay_plus: str
  random_delay_minus: str


@dataclass
class Event_Settings:
  '''
  Dataclass for storing Hotkey-related settings
  '''
  file_events: FileEvent_Settings
  hotkeys: Hotkey_Settings
  max_delay_random: millisecs
  step_delay_random: float
# ==================================================================================================


def extract_event_settings(
  config: ConfigDict
) -> Event_Settings:
  '''
  Create a new Event_Settings instance and set relevant data from config.
  '''
  events_dict: EventsConfigDict = config.get('events', {})
  # file_events
  file_events_dict: FileEventsConfigDict = events_dict.get('file_events', {})
  enabled: bool = file_events_dict.get('enabled', False)
  raw_path: str = file_events_dict.get('path', '')
  path: Path = Path(raw_path)
  if not raw_path:
    path = DEFAULT_EVENT_FOLDER
    path.mkdir(parents=True, exist_ok=True)
  file_events: FileEvent_Settings = FileEvent_Settings(
    enabled=enabled,
    path=path,
  )
  # hotkeys
  hotkeys_dict: HotkeysConfigDict = events_dict.get('hotkeys', {})
  failsafe: str = hotkeys_dict.get('failsafe', 'Shift+Backspace')
  accept_input: str = hotkeys_dict.get('accept_input', '')
  random_action: str = hotkeys_dict.get('random_action', '')
  reset_teams: str = hotkeys_dict.get('reset_teams', '')
  random_delay_plus: str = hotkeys_dict.get('random_delay_plus', '')
  random_delay_minus: str = hotkeys_dict.get('random_delay_minus', '')
  hotkeys: Hotkey_Settings = Hotkey_Settings(
    failsafe=failsafe,
    accept_input=accept_input,
    random_action=random_action,
    reset_teams=reset_teams,
    random_delay_plus=random_delay_plus,
    random_delay_minus=random_delay_minus,
  )
  # events
  max_delay_random: millisecs = events_dict.get('max_delay_random', 0)
  step_delay_random: float = events_dict.get('step_delay_random', 5)
  return Event_Settings(
    file_events=file_events,
    hotkeys=hotkeys,
    max_delay_random=max_delay_random,
    step_delay_random=step_delay_random,
  )


# ==================================================================================================
@dataclass
class Command_Settings:
  '''
  Dataclass for storing Hotkey-related settings
  '''
  prefix: str
  mode: Literal['all', 'whitelist', 'blacklist', 'none']
  whitelist: list[str]
  blacklist: list[str]
# ==================================================================================================


def extract_command_settings(
  config: ConfigDict
) -> Command_Settings:
  '''
  Create a new Hotkey_Settings instance and set relevant data from config.
  '''
  hotkeys_dict: CommandsConfigDict = config.get('commands', {})
  prefix: str = hotkeys_dict.get('prefix', '?')
  mode: Literal['all', 'blacklist', 'whitelist', 'none'] = (
    hotkeys_dict.get('mode', 'all')
  )
  legal_modes = ['all', 'blacklist', 'whitelist', 'none']
  if mode not in legal_modes:
    raise ValueError(
      f"Invalid config value for /commands/mode: {mode!r}\n"
      f"Must be one of {', '.join(repr(m) for m in legal_modes)}"
    )
  whitelist: list[str] = hotkeys_dict.get('whitelist', [])
  blacklist: list[str] = hotkeys_dict.get('blacklist', [])
  return Command_Settings(
    prefix=prefix,
    mode=mode,
    whitelist=whitelist,
    blacklist=blacklist
  )


# ==================================================================================================
@dataclass
class TTS_Settings:
  '''
  Dataclass for storing TTS-related settings
  '''
  enabled: bool
  voice_ids: list[str]
  rate: int
  volume: float
  number_of_channels: int
  max_duration: seconds
# ==================================================================================================


def extract_tts_settings(
  config: ConfigDict
) -> TTS_Settings:
  '''
  Create a new TTS_settings instance and set relevant data from config.
  '''
  tts_dict: TTSConfigDict = config.get('tts', {})
  enabled: bool = tts_dict.get('enabled', False)
  voice_ids: list[str] = tts_dict.get('voice_ids', [DEFAULT_VOICE_ID])
  rate: int = tts_dict.get('rate', 150)
  volume: float = tts_dict.get('volume', 1.0)
  number_of_channels: int = tts_dict.get('number_of_channels', 10)
  max_duration: seconds = tts_dict.get('max_duration', 30.0)
  return TTS_Settings(
    enabled=enabled,
    voice_ids=voice_ids,
    rate=rate,
    volume=volume,
    number_of_channels=number_of_channels,
    max_duration=max_duration,
  )
