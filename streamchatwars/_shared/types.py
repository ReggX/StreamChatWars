'''
Collection of objects used for type hinting
'''

# native imports
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any
from typing import Awaitable
from typing import Coroutine
from typing import Literal
from typing import NotRequired
from typing import Protocol
from typing import Required
from typing import TypeAlias
from typing import TypedDict
from uuid import UUID

# internal imports
from .constants import INPUT_TYPE as _INPUT_TYPE  # Don't re-export
from .primitive_types import millisecs
from .primitive_types import seconds


AXIS_SETTER_TYPE: TypeAlias = Callable[[int], None]
AXIS_GETTER_TYPE: TypeAlias = Callable[[], int]
AXIS_TUPLE_TYPE: TypeAlias = tuple[
  AXIS_SETTER_TYPE,  # axis setter function
  int,               # max value for setter function
  AXIS_GETTER_TYPE   # getter for current axis value
]
AXIS_MAP_TYPE: TypeAlias = dict[str, AXIS_TUPLE_TYPE]
# ------------------------------------------------------------------------------


class VerbParamDict(TypedDict):
  '''
  Type hinting for verb_parameters entry in `verb_dict`

  Also used in JSON contents of JSON macro file: `/macros/{}/[]/`
  '''
  key:         Required[str]
  '''The lookup key for key_dict'''
  duration:    Required[millisecs]
  '''The default duration if not explicitly specified'''
  min_time:    Required[millisecs]
  '''The minimum amount of time duration is allowed to take'''
  max_time:    Required[millisecs]
  '''The maximum amount of time delay+duration are allowed to take'''
  delay:       Required[millisecs]
  '''Inherent delay of key action, should be 0 for the first key'''
  input_type:  Required[_INPUT_TYPE]
  '''Type of the input (press/hold/release), see input_handler'''
# ------------------------------------------------------------------------------


class FuncArgsDict(TypedDict):
  '''
  Type hinting for **keyword-arguments for `input_handler.press_multiple_Keys`
  '''
  key:       Required[str]
  '''Key value to pass to input handler'''
  duration:  Required[millisecs]
  '''Duration value to pass to input handler'''
  delay:     Required[millisecs]
  '''Delay value to pass to input handler'''
# ------------------------------------------------------------------------------


class Partial_VerbParamDict(Protocol):
  '''
  Type hinting class for create_verb_params()
  '''
  def __call__(
    self,
    key: str,
    duration: millisecs = 1,
    delay: millisecs = 0,
    min_time: millisecs = 1,
    max_time: millisecs = 1000,
    input_type: _INPUT_TYPE = _INPUT_TYPE.PRESS_KEY
  ) -> VerbParamDict:
    ...  # pragma: no cover
# ------------------------------------------------------------------------------


# ===== TypeAlias for JSON schema files ============================================================
SCHEMA_MAPPING: TypeAlias = Mapping[str, Any]
'''TypeAlias for JSON schema files'''
# ------------------------------------------------------------------------------


# ===== TypedDict for UserList Dict ================================================================
class UserListDict(TypedDict):
  '''Type hinting for UserList export/import dicts'''
  users:   NotRequired[Sequence[str]]
  groups:  NotRequired[Mapping[str, Sequence[str]]]
# ------------------------------------------------------------------------------


# ===== TypedDict for Team snapshots ===============================================================
class TeamSnapshotDict(TypedDict):
  '''Type hinting for UserList export/import dicts'''
  members:    NotRequired[Sequence[str]]
  whitelist:  NotRequired[UserListDict]
  blacklist:  NotRequired[UserListDict]
  macros:     NotRequired[dict[str, list[VerbParamDict]]]
# ------------------------------------------------------------------------------


# ===== TypedDict for Snapshots ====================================================================
class SnapshotDict(TypedDict):
  '''Type hinting for UserList export/import dicts'''
  timestamp:  NotRequired[str]
  teams:      NotRequired[dict[str, TeamSnapshotDict]]
# ------------------------------------------------------------------------------


# ===== TypedDicts for JSON config files ===========================================================
class InputServerConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/teams/[]/actionset/input_server`'''
  type:             NotRequired[Literal['local', 'remote']]
  '''Type of input server (local/remote)'''
  host:             NotRequired[str]
  '''Hostname/IP of the remote input server, required if type is remote'''
  port:             NotRequired[int]
  '''Port of the remote input server, required if type is remote'''
  encryption_key:   NotRequired[str]
  '''Pre-shared key used by remote input server, empty means no encryption'''
  encryption_mode:  NotRequired[Literal['AES-GCM']]
  '''Encryption algorithm used by remote input server'''
# ------------------------------------------------------------------------------


class ActionsetConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/teams/[]/actionset/`'''
  type:                   NotRequired[str]
  '''Type of the actionset object, influences how action commands are handled'''
  doc_url:                NotRequired[str]
  '''Link to a page where the available action commands are explained to users'''
  action_prefix:          NotRequired[str]
  '''Prefix of action commands in chat for this actionset'''
  player_index:           NotRequired[int]
  '''Determines which keybindings/gamepad are used for this actionset'''
  allow_changing_macros:  NotRequired[bool]
  '''Allow runtime manipulation of macros (like addMacro command)?'''
  macro_file:             NotRequired[str]
  '''Path of json files that contains macro data'''
  persistent_macros:      NotRequired[bool]
  '''Does changing a macro during runtime also modify the macro file?'''
  input_server:           NotRequired[InputServerConfigDict]
  '''Data which determines how input is sent to the game'''
# ------------------------------------------------------------------------------


class TeamConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/teams/[]/`'''
  type:               NotRequired[str | list[str]]
  '''Type of the team object, influences how members are selected'''
  name:               NotRequired[str]
  '''Identifier of the team, required for certain chat commands'''
  queue_length:       NotRequired[int]
  '''How many messages max are queued for every command cycle'''
  hidden:             NotRequired[bool]
  '''Is this team available to everybody or just to operators?'''
  joinable:           NotRequired[bool]
  '''Can this team be joined via chat commands?'''
  leavable:           NotRequired[bool]
  '''Can this team be left via chat commands?'''
  exclusive:          NotRequired[bool]
  '''Being a member of this team excludes you from being a member in other teams?'''
  use_random_inputs:  NotRequired[bool]
  '''Execute random commands instead of sleeping?'''
  spam_protection:    NotRequired[bool]
  '''Prevent users from bumping by spamming the same message'''
  pattern:            NotRequired[str]
  '''Regex pattern used in username matching, only needed for type=NameRegex'''
  number:             NotRequired[int]
  '''Number index used for PredictionNumber Teams'''
  channels:           NotRequired[list[str]]
  '''List of all channels where this team should check for action commands'''
  user_whitelist:     NotRequired[list[str]]
  '''List of all users that are allowed to join this team'''
  user_blacklist:     NotRequired[list[str]]
  '''List of all users that are NOT allowed to join this team'''
  actionset:          NotRequired[ActionsetConfigDict]
  '''Settings for a team's assinged actionset'''
# ------------------------------------------------------------------------------


class IrcConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/irc/`'''
  host:                    NotRequired[str]
  '''Hostname/IP of the chat server'''
  port:                    NotRequired[int]
  '''Port of the chat server'''
  message_interval:        NotRequired[float]
  '''Cooldown in seconds between sending non-priority messages in chat'''
  connection_timeout:      NotRequired[float]
  '''Timeout value in seconds before canceling a connection attempt'''
  join_rate_limit_amount:  NotRequired[int]
  '''Amount of channels that can be joined in one rate limit period'''
  join_rate_limit_time:    NotRequired[seconds]
  '''Cooldown between joining chans after rate limit has been reached'''
# ------------------------------------------------------------------------------


class FileEventsConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/events/file_events/`'''
  enabled:  NotRequired[bool]
  '''Should files in the event folder influence the behaviour of StreamChatWars?'''
  path:     NotRequired[str]
  '''Location of the file event folder, leave empty to use default temp directory'''
# ------------------------------------------------------------------------------


class HotkeysConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/events/hotkeys/`'''
  failsafe:           NotRequired[str]
  '''Global hotkey to abort execution in any context'''
  accept_input:       NotRequired[str]
  '''Global hotkey to toggle input parsing'''
  random_action:      NotRequired[str]
  '''Global hotkey to toggle random actions'''
  reset_teams:        NotRequired[str]
  '''Global hotkey to reset teams'''
  random_delay_plus:  NotRequired[str]
  '''Global hotkey to increase random action delay'''
  random_delay_minus: NotRequired[str]
  '''Global hotkey to decrease random action delay'''
# ------------------------------------------------------------------------------


class EventsConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/events/`'''
  file_events:        NotRequired[FileEventsConfigDict]
  '''Collection of settings related to file events'''
  hotkeys:            NotRequired[HotkeysConfigDict]
  '''Collection of global hotkey sequences, leave blank to disable'''
  max_delay_random:   NotRequired[millisecs]
  '''Maximum delay (at 100%) for random actions, in milliseconds'''
  step_delay_random:  NotRequired[float]
  '''Step size for random actions delay, in percent points'''
# ------------------------------------------------------------------------------


class CommandsConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/commands/`'''
  prefix:     NotRequired[str]
  '''The character that's used to prefix chat commands (NOT action commands!)'''
  mode:       NotRequired[Literal['all', 'blacklist', 'whitelist', 'none']]
  '''Determines which commands are enabled'''
  blacklist:  NotRequired[list[str]]
  '''List of all blacklisted commands that can't be used'''
  whitelist:  NotRequired[list[str]]
  '''List of all whitelisted commands that are the only ones that can be used'''
# ------------------------------------------------------------------------------


class SessionlogConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/sessionlog/`'''
  enable_consolelog:       NotRequired[bool]
  '''Store a record of all console messages?'''
  enable_chatlog:          NotRequired[bool]
  '''Store a record of all chat messages?'''
  enable_channelpointlog:  NotRequired[bool]
  '''Store a record of all channel point redeems?'''
  enable_periodic_dumps:   NotRequired[bool]
  '''Dump the session log to disk periodically?'''
  dumping_interval:        NotRequired[seconds]
  '''Number of seconds between dumping the session log to disk'''
  counter_cap:             NotRequired[int]
  '''Cap of the rolling counter for the session log file name'''
# ------------------------------------------------------------------------------


class TTSConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/tts/`'''
  enabled:              NotRequired[bool]
  '''Can the bot use text-to-speech?'''
  voice_ids:             NotRequired[list[str]]
  '''IDs of the voices to use for TTS'''
  rate:                 NotRequired[int]
  '''Speed of the TTS voice, in words per minute'''
  volume:               NotRequired[float]
  '''Volume of the TTS voice, in percent'''
  number_of_channels:   NotRequired[int]
  '''How many channels can be used for TTS at the same time'''
  max_duration:         NotRequired[float]
  '''Maximum duration of a TTS message, in seconds'''
# ------------------------------------------------------------------------------


class ConfigDict(TypedDict):
  '''JSON contents of JSON config file: `/`'''
  config_name:        NotRequired[str]
  '''Human readable name of this configuration'''
  events:             NotRequired[EventsConfigDict]
  '''Collection of settings related to events'''
  commands:           NotRequired[CommandsConfigDict]
  '''Collection of command settings'''
  operators:          NotRequired[list[str]]
  '''List of operators (privileged users with access to advanced commands)'''
  irc:                NotRequired[IrcConfigDict]
  '''Collection of settings related to the IRC server connection'''
  tts:                NotRequired[TTSConfigDict]
  '''Collection of settings related to OpenAI'''
  sessionlog:         NotRequired[SessionlogConfigDict]
  '''Collection of settings related to storing session information'''
  default_team_data:  NotRequired[TeamConfigDict]
  '''Default team data'''
  teams:              NotRequired[list[TeamConfigDict]]
  '''Collection of team setting objects'''
# ==================================================================================================


# ===== TypedDicts for JSON credential files =======================================================
class CredentialTypeDict(TypedDict):
  '''JSON contents of JSON credential file: `#/$defs/credential`'''
  type:  Required[Literal['cleartext', 'hex', 'base64', 'file', 'env']]
  '''How the credentials are stored.'''
  value: Required[str]
  '''The value of the credentials, decoding is based on the `type`.'''
# ------------------------------------------------------------------------------


class TwitchChatCredentialDict(TypedDict):
  '''JSON contents of JSON credential file: `/TwitchChat/`'''
  username:     Required[CredentialTypeDict]
  '''Username of the chat bot, all lowercase'''
  oauth_token:  Required[CredentialTypeDict]
  '''OAUTH token used to authenticate your chat bot'''
# ------------------------------------------------------------------------------


class TwitchAPICredentialDict(TypedDict):
  '''JSON contents of JSON credential file: `/TwitchAPI/`'''
  client_id:      Required[CredentialTypeDict]
  '''Client ID of your Twitch API access key'''
  client_secret:  Required[CredentialTypeDict]
  '''Client Secret of your Twitch API access key'''
# ------------------------------------------------------------------------------

class CredentialDict(TypedDict):
  '''JSON contents of JSON credential file: `/`'''
  TwitchChat:  NotRequired[TwitchChatCredentialDict]
  '''Collection of credentials required to access Twitch Chat'''
  TwitchAPI:   NotRequired[TwitchAPICredentialDict]
  '''Collection of credentials required to access Twitch API calls'''
# ==================================================================================================


# ===== TypedDict for JSON macro files =============================================================
class MacroDict(TypedDict):
  '''JSON contents of JSON macro file: `/`'''
  name:    NotRequired[str]
  '''Name of the macro collection, can be different from filename'''
  macros:  NotRequired[dict[str, list[VerbParamDict]]]
  '''Mapping of macro name to macro data'''
# ==================================================================================================


# ===== TypedDicts for Input Server data packs =====================================================
INPUT_DATA_PACK_TYPE: TypeAlias = Literal['input']


class InputServerDataPack(TypedDict):
  '''JSON contents of RemoteInputServer's data packs'''
  type:        Required[INPUT_DATA_PACK_TYPE]
  '''Type of data pack, can be extended for future use'''
  encryption:  Required[None | Literal['AES-GCM']]
  '''Type of encryption used, can be extended for future use'''
  data:        Required[str]
  '''contents of data pack'''
  auth_tag:    NotRequired[str]
  '''message tag for verification purposes'''
  nonce:       NotRequired[str]
  '''nonce used for encryption'''
# ==================================================================================================


# ===== Twitch API types ===========================================================================
class UserInfoDict(TypedDict):
  broadcaster_type:   Required[str]
  created_at:         Required[str]
  description:        Required[str]
  display_name:       Required[str]
  id:                 Required[str]
  login:              Required[str]
  offline_image_url:  Required[str]
  profile_image_url:  Required[str]
  type:               Required[str]
  view_count:         Required[int]
  email:              NotRequired[str]
# ------------------------------------------------------------------------------


class GetUsersResponse(TypedDict):
  data:  Required[list[UserInfoDict]]
# ------------------------------------------------------------------------------


class ImageDict(TypedDict):
  url_1x:  Required[str]
  url_2x:  Required[str]
  url_4x:  Required[str]
# ------------------------------------------------------------------------------


class UserDict(TypedDict):
  display_name:  Required[str]
  id:            Required[str]
  login:         Required[str]
# ------------------------------------------------------------------------------


class GlobalCooldownDict(TypedDict):
  global_cooldown_seconds:  Required[int]
  is_enabled:               Required[bool]
# ------------------------------------------------------------------------------


class MaxPerStreamDict(TypedDict):
  is_enabled:      Required[bool]
  max_per_stream:  Required[int]
# ------------------------------------------------------------------------------


class MaxPerUserPerStreamDict(TypedDict):
  is_enabled:               Required[bool]
  max_per_user_per_stream:  Required[int]
# ------------------------------------------------------------------------------


class RewardDict(TypedDict):
  background_color:                       Required[str]
  channel_id:                             Required[str]
  cooldown_expires_at:                    Required[str | None]
  cost:                                   Required[int]
  default_image:                          Required[ImageDict | None]
  global_cooldown:                        Required[GlobalCooldownDict]
  id:                                     Required[str]
  image:                                  Required[ImageDict | None]
  is_enabled:                             Required[bool]
  is_in_stock:                            Required[bool]
  is_paused:                              Required[bool]
  is_sub_only:                            Required[bool]
  is_user_input_required:                 Required[bool]
  max_per_stream:                         Required[MaxPerStreamDict]
  max_per_user_per_stream:                Required[MaxPerUserPerStreamDict]
  prompt:                                 Required[str]
  redemptions_redeemed_current_stream:    Required[int | None]
  should_redemptions_skip_request_queue:  Required[bool]
  template_id:                            Required[str | None]
  title:                                  Required[str]
  updated_for_indicator_at:               Required[str | None]
# ------------------------------------------------------------------------------


class RedemptionDict(TypedDict):
  channel_id:   Required[str]
  cursor:       Required[str]
  id:           Required[str]
  redeemed_at:  Required[str]
  reward:       Required[RewardDict]
  status:       Required[Literal['UNFULFILLED', 'FULFILLED', 'CANCELED']]
  user:         Required[UserDict]
# ------------------------------------------------------------------------------


class RedemptionPubSubDict(TypedDict):
  redemption:  Required[RedemptionDict]
  timestamp:   Required[str]
# ------------------------------------------------------------------------------


class CustomRewardUpdatedPubSubDict(TypedDict):
  timestamp:       Required[str]
  updated_reward:  Required[RewardDict]
# ------------------------------------------------------------------------------


class CommunityPointsPubSubDict_reward(TypedDict):
  type:  Required[Literal['custom-reward-updated']]
  data:  Required[CustomRewardUpdatedPubSubDict]
# ------------------------------------------------------------------------------


class CommunityPointsPubSubDict_reward_redeemed(TypedDict):
  type:  Required[Literal['reward-redeemed']]
  data:  Required[RedemptionPubSubDict]
# ------------------------------------------------------------------------------


class CommunityPointsPubSubDict_redemption_status_update(TypedDict):
  type:  Required[Literal['redemption-status-update']]
  data:  Required[RedemptionPubSubDict]
# ------------------------------------------------------------------------------


CommunityPointsPubSubDict: TypeAlias = (
  CommunityPointsPubSubDict_redemption_status_update
  | CommunityPointsPubSubDict_reward_redeemed
  | CommunityPointsPubSubDict_reward
)
# ------------------------------------------------------------------------------


LISTEN_CHANNELPOINTS_TYPE: TypeAlias = Callable[
  [
    str,
    Callable[[UUID, CommunityPointsPubSubDict], Awaitable[None]]
  ],
  Coroutine[Any, Any, UUID]
]
# ==================================================================================================


# ===== TypedDict for ChatMessage.as_dict() ========================================================
class ChatMessageDict(TypedDict):
  '''Type hinting for dicts created by ChatMessage.as_dict()'''
  msg_type:   Required[str]
  '''Message/Event type of the IRC message'''
  id:         Required[str]
  '''UUID of the chat message'''
  timestamp:  Required[seconds]
  '''Timestamp when the message was received'''
  user:       Required[str]
  '''Username of the message sender'''
  channel:    Required[str]
  '''Channel the message was sent in'''
  message:    Required[str]
  '''Message contents'''
  tags:       Required[dict[str, str]]
  '''Additional metadata'''
# ------------------------------------------------------------------------------


# ===== TypedDict for ChatLog.export_dict() ========================================================
class ChatLogDict(TypedDict):
  '''Type hinting for dicts created by ChatLog.export_dict()'''
  messages:          Required[dict[str, ChatMessageDict]]
  '''Dict[UUID: ChatMessage]'''
  notices:           Required[dict[str, ChatMessageDict]]
  '''Dict[UUID: ChatMessage]'''
  actions:           Required[list[str]]
  '''List of UUIDs that were actions'''
  executed_actions:  Required[list[str]]
  '''List of UUIDs that were executed actions'''
  commands:          Required[list[str]]
  '''List of UUIDs that were chat commands'''
# ------------------------------------------------------------------------------


# ===== TypedDict for TeamLog.export_dict() ========================================================
class TeamLogDict(TypedDict):
  '''Type hinting for dicts created by '''
  name:              Required[str]
  '''Unique name of the team'''
  actions:           Required[list[str]]
  '''List of UUIDs that were actions'''
  executed_actions:  Required[list[str]]
  '''List of UUIDs that were executed actions'''
# ------------------------------------------------------------------------------


# ===== TypedDict for ConsoleLog.export_list() =====================================================
class ConsoleMessageDict(TypedDict):
  '''Type hinting for dicts created by ConsoleMessage.as_dict()'''
  message:    Required[str]
  '''Message that was displayed in the console'''
  timestamp:  Required[seconds]
  '''Timestamp when the message was displayed'''
# ------------------------------------------------------------------------------


# ===== TypedDict for SessionLog.dump() ============================================================
class SessionLogDict(TypedDict):
  '''Type hinting for dicts created by Session.dump()'''
  config:         NotRequired[ConfigDict]
  console:        NotRequired[list[ConsoleMessageDict]]
  channelpoints:  NotRequired[list[CommunityPointsPubSubDict]]
  chat:           NotRequired[ChatLogDict]
  teams:          NotRequired[dict[str, TeamLogDict]]
# ==================================================================================================
