'''
This module contains all application constants.

Imports from other modules of this package are NOT allowed!
(except primitive_types)
'''

# native imports
from enum import IntEnum
from enum import auto
from pathlib import Path
from re import Pattern
from re import compile
from tempfile import gettempdir
from typing import Final

# internal imports
from .primitive_types import seconds


# ------------------------------------------------------------------------------
# Try importing vgamepad's XUSB_BUTTON enum if available, falling back to a
# local copy if it fails. (vgamepad tries to load ViGEm on import, so import
# will fail on all systems without ViGEm)
try:
  # pip imports
  from vgamepad import XUSB_BUTTON
except Exception:  # pragma: no cover
  # internal imports
  from ..fallback._vgamepad import XUSB_BUTTON  # type: ignore[assignment]
# ------------------------------------------------------------------------------


# ##############################################################################
# ##### Exit Codes #############################################################
# ##############################################################################
class ExitCode(IntEnum):
  '''
  Exit codes for the application.
  '''
  SUCCESS = 0
  '''
  Generic success exit code.
  Probably unused due to the way the application is structured.
  '''
  FAILURE = 1
  '''
  Generic failure exit code.
  Used when no specific exit code is available.
  '''
  INVALID_CONFIG = auto()
  '''
  Used when the configuration/credential files are invalid.
  (Most likely failed JSON Schema validation)
  '''
  INVALID_HOTKEY = auto()
  '''
  Used when a given hotkey can't be parsed into a valid keyboard hotkey.
  '''
  DUPLICATE_TEAM_NAME = auto()
  '''
  Used when the same team name is used more than once.
  '''
  ACTIONSET_VALIDATION_FAILURE = auto()
  '''
  Used when an actionset fails validation.
  '''
  TEAM_CREATION_FAILURE = auto()
  '''
  Generic error used when a team fails to be created.
  '''
  MISSING_CHAT_CREDENTIALS = auto()
  '''
  Used when the application is missing chat credentials.
  '''
  MISSING_API_CREDENTIALS = auto()
  '''
  Used when the application is missing API credentials.
  '''
  FAILSAFE_ENGAGED = auto()
  '''
  Used when the failsafe was triggered (by user).
  '''
  ABORT_EARLY = auto()
  '''
  Used when the application is aborted early (by user).
  '''
  INVALID_CHAT_CREDENTIALS = auto()
  '''
  Used when the chat credentials are invalid.
  '''
  INVALID_API_CREDENTIALS = auto()
  '''
  Used when the API credentials are invalid.
  '''


# ##############################################################################
# ##### Main Constants #########################################################
# ##############################################################################
THREAD_TIMEOUT: Final[seconds] = 5.0
'''
Constant `5.0`

Time interval in seconds for timing out thread.join() operations.
'''

FILE_EVENT_WAIT_TIME: Final[seconds] = 0.001
'''
Constant `0.001`

Time interval in seconds for waiting a small time after starting the
file event thread to reduce chances of console prints getting mixed up.
'''


# ##############################################################################
# ##### JSON Constants #########################################################
# ##############################################################################
DEFAULT_INDENT_LEVEL: Final = 2
'''
Constant: `2`

How many spaces JSON indentation should use.
'''

# Path to important folders
DATA_FOLDER: Final[Path] = Path('data')
'''Constant Path object pointing to the data folder.'''
SCHEMA_FOLDER: Final[Path] = DATA_FOLDER / 'schema'
'''Constant Path object pointing to the schema folder.'''
TEMPLATE_FOLDER: Final[Path] = SCHEMA_FOLDER / 'template'
'''Constant Path object pointing to the schema template folder.'''
CONFIG_FOLDER: Final[Path] = DATA_FOLDER / 'config'
'''Constant Path object pointing to the config folder.'''
CREDENTIALS_FOLDER: Final[Path] = DATA_FOLDER / 'credentials'
'''Constant Path object pointing to the credentials folder.'''
SNAPSHOT_FOLDER: Final[Path] = DATA_FOLDER / 'snapshots'
'''Constant Path object pointing to the snapshots folder.'''
SESSION_FOLDER: Final[Path] = DATA_FOLDER / 'session'
'''Constant Path object pointing to the sessions folder.'''

# Path to JSON schemas (for JSON validation)
CONFIG_SCHEMA_TEMPLATE_FILE: Final[Path] = (
  TEMPLATE_FOLDER / 'config_template.json'
)
'''
Constant Path object pointing to the JSON schema template for config files.
'''

SNAPSHOT_SCHEMA_TEMPLATE_FILE: Final[Path] = (
  TEMPLATE_FOLDER / 'snapshot_template.json'
)
'''
Constant Path object pointing to the JSON schema template for snapshot files.
'''

CONFIG_SCHEMA_FILE: Final[Path] = SCHEMA_FOLDER / 'config_schema.json'
'''Constant Path object pointing to the JSON schema for config files.'''

CREDENTIAL_SCHEMA_FILE: Final[Path] = SCHEMA_FOLDER / 'credential_schema.json'
'''Constant Path object pointing to the JSON schema for credential files.'''

MACRO_SCHEMA_FILE: Final[Path] = SCHEMA_FOLDER / 'macro_schema.json'
'''Constant Path object pointing to the JSON schema for macro files.'''

SNAPSHOT_SCHEMA_FILE: Final[Path] = SCHEMA_FOLDER / 'snapshot_schema.json'
'''Constant Path object pointing to the JSON schema for snapshot files.'''

# Path to default JSON files
DEFAULT_CONFIG_FILE: Final[Path] = CONFIG_FOLDER / "default.json"
'''Constant Path object pointing to the default configuration file.'''

DEFAULT_CREDENTIAL_FILE: Final[Path] = CREDENTIALS_FOLDER / "default.json"
'''Constant Path object pointing to the default credentials file.'''

# Contents of default JSON files
DEFAULT_CREDENTIAL_CONTENTS: Final = """{
  "$schema": "../schema/credential_schema.json",
  "TwitchChat": {
    "username": {
      "type": "cleartext",
      "value": "YOUR_BOT_USERNAME_LOWERCASE"
    },
    "oauth_token": {
      "type": "cleartext",
      "value": "YOUR_BOT_OAUTH_TOKEN"
    }
  },
  "TwitchAPI": {
    "client_id": {
      "type": "cleartext",
      "value": "YOUR_TWITCH_API_CLIENT_ID"
    },
    "client_secret": {
      "type": "cleartext",
      "value": "YOUR_TWITCH_API_CLIENT_SECRET"
    }
  }
}
"""  # end of file contents, next line start of doc string
'''
Constant default file constants of a newly created credential file,
for the user to fill out.

Pre-dumped JSON string that can be written straight to file without
calling json.dumps() first.
'''


# ##############################################################################
# ##### File Event Constants ###################################################
# ##############################################################################
DEFAULT_EVENT_FOLDER: Final[Path] = Path(gettempdir()) / "StreamChatWars"
'''Constant Path object pointing to the folder containing event files.'''
ACCEPT_INPUT_FILE: Final[Path] = DEFAULT_EVENT_FOLDER / "ACCEPT_INPUT"
'''Constant Path object pointing to the event file for accepting user input.'''
RANDOM_ACTIONS_FILE: Final[Path] = DEFAULT_EVENT_FOLDER / "RANDOM_ACTIONS"
'''
Constant Path object pointing to the event file for executing random actions.
'''
RESET_TEAMS_FILE: Final[Path] = DEFAULT_EVENT_FOLDER / "RESET_TEAMS"
'''
Constant Path object pointing to the event file for resetting team members.
'''
DELAY_RANDOM_FILE: Final[Path] = DEFAULT_EVENT_FOLDER / "DELAY_RANDOM"
'''
Constant Path object pointing to the event file for
artifical random action delay.
'''

UPDATE_INTERVAL: Final[seconds] = 0.05
'''
Constant `0.05`

Time interval in seconds for checking for new events (hotkeys, files)
'''


# ##############################################################################
# ##### Chat Bot Constants #####################################################
# ##############################################################################
CHECK_JOIN_INTERVAL: Final[seconds] = 0.1
'''
Constant: `0.1`

Time interval in seconds for checking if all channels have been joined and
normal operation can start.
'''

CHANNEL_NAME_PATTERN: Final = r"#?[a-zA-Z0-9_]+"
'''
Constant: `r"#?[a-zA-Z0-9_]+"`

The regular expression pattern used to detect valid channel names.

Allows uppercase A-Z for user convenience. Output needs to be converted
to lowercase internally!
'''


# ##############################################################################
# ##### Chat Commands Constants ################################################
# ##############################################################################
MACRO_NAME_REGEX: Final[Pattern[str]] = compile(r"^[a-zA-Z0-9_]+$")
'''
Constant compiled regex for checking for valid macro names.
'''

SNAPSHOT_NAME_REGEX: Final[Pattern[str]] = (
  compile(pattern=r"^[a-zA-Z0-9_+,. -]*$")
)
'''
Constant compiled regex for checking for valid snapshot names.
'''

MAX_MESSAGE_LENGTH: Final = 450
'''
Constant: `450`

The maximum character length of a single chat message.
Longer message will need to be split in multiple parts.
'''


# ##############################################################################
# ##### Text to Speech Constants ###############################################
# ##############################################################################
DEFAULT_VOICE_ID: Final = (
  R"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices"
  R"\Tokens\TTS_MS_EN-US_DAVID_11.0"
)
'''
Constant string that identifies the default voice used by the TTS engine.

For compatibility reasons, the default voice is set to the Microsoft David,
but in theory other SAPI-compatible voices could be used as well.
'''


# ##############################################################################
# ##### Team Constants #########################################################
# ##############################################################################
EMPTY_QUEUE_SLEEP_DURATION: Final[seconds] = 0.01
'''
Constant: `0.01`

Time interval in seconds for waiting on new message queue contents.

Lower values are more responsive, but may result in more wasted computations
done to check queue contents.
'''


# ##############################################################################
# ##### Actionset Constants ####################################################
# ##############################################################################
DELAY_SEPARATOR_PATTERN: Final = r"[+,;:]|->"
'''
Constant: `r"[+,;:]|->"`

The regular expression pattern used to separate delay and duration values
in Multikey Actionset action commands.
'''

VERB_DELAY_DURATION_REGEX: Final[Pattern[str]] = compile(
  rf"(\S+)(?:\s+(?:(\d+)?\s*(?:{DELAY_SEPARATOR_PATTERN})\s*)?(\d+)?(?:$|\s))?"
  # Groups:   [0]           [1]                                [2]
)
'''
Constant compiled regex for extracting action-verb parameters
from chat messages.

* Group[0]: mandatory verb of the action, e.g. +example
* Group[1]: optional execution delay of action in milliseconds,
requires the presence of a parameter separator, see `DELAY_SEPARATOR`
* Group[2]: optional execution duration of action in milliseconds
'''

PREDICTION_NUMBER_REGEX: Final[Pattern[str]] = compile(
  r"predictions/[a-z]+-([0-9]+)"
)
'''
Constant compiled regex for extracting the prediction number from badges.

Group[0] is the number of the predicition.
'''


# ##############################################################################
# ##### Input Handler Constants ################################################
# ##############################################################################
class INPUT_TYPE(IntEnum):
  '''
  Magic values that influence input handler behavior.
  '''
  PRESS_KEY = 1
  '''
  Constant: `1`

  The magic value representing a key PRESS action for input handlers.
  '''
  HOLD_KEY = -1
  '''
  Constant: `-1`

  The magic value representig a key HOLD action for input handlers.
  (-1 used to represent max unsigned integer aspseudo "infintely" long key
  press)
  '''
  RELEASE_KEY = 0
  '''
  Constant: `0`

  The magic value representing a key RELEASE action for input handlers.
  (0 used to represent an instant press/unpress action which would constitute
  releasing an already pressed key)
  '''


MILLISEC_TO_SEC_MULT: Final[seconds] = 0.001
'''
Constant: `0.001`

Convert millisecond values to second values by multiplying with this constant.
'''


# ##############################################################################
# ##### Input Server Constants #################################################
# ##############################################################################
SOCKET_TIMEOUT: Final[seconds] = 3.0
'''
Constant: `3.0`

Timeout value in seconds for RemoteInputServer's socket.
'''

BACKOFF_FACTOR: Final = 1.1
'''
Constant: `1.1`

Exponential factor that increases delay between reconnect attempts
'''


# ##############################################################################
# ##### Gamepads Constants #####################################################
# ##############################################################################
POS_MAX_UINT8: Final = 255
'''
Constant: `255 == 2**8 - 1`

Max value of unsigned 8 bit integer.
'''
POS_MAX_INT16: Final = 32767
'''
Constant: `32767 == 2**15 - 1`

Max postive value of signed 16 bit integer.
'''
NEG_MAX_INT16: Final = -32768
'''
Constant: `-32768 == -1 * 2**15`

Max negative value of signed 16 bit integer.
'''

XUSB_BUTTON_MAPPING: Final[dict[str, XUSB_BUTTON]] = {
  'a': XUSB_BUTTON.XUSB_GAMEPAD_A,
  'b': XUSB_BUTTON.XUSB_GAMEPAD_B,
  'x': XUSB_BUTTON.XUSB_GAMEPAD_X,
  'y': XUSB_BUTTON.XUSB_GAMEPAD_Y,
  'rb': XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
  'lb': XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
  'rs': XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
  'ls': XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
  'dpad_up': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
  'dpad_down': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
  'dpad_left': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
  'dpad_right': XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
  'start': XUSB_BUTTON.XUSB_GAMEPAD_START,
  'back': XUSB_BUTTON.XUSB_GAMEPAD_BACK,
  'guide': XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
}
'''
Constant dict mapping gamepad button names (strings) to their internal
XUSB_Button constant (integer enum).
'''
