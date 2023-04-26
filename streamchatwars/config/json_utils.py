'''
This modules handles reading and validating config/credential files
and includes functions to transform the JSON Mappings into usable data
for the rest of the package.
'''

# native imports
import json
from base64 import b64decode
from binascii import unhexlify
from datetime import datetime
from json import JSONDecodeError
from os import getenv
from pathlib import Path
from typing import Any
from typing import overload

# pip imports
from json_source_map import calculate
from json_source_map.types import Entry
from json_source_map.types import Location
from json_source_map.types import TSourceMap
from jsonschema import ValidationError
from jsonschema import validate

# internal imports
from .._shared.constants import CONFIG_SCHEMA_FILE
from .._shared.constants import CONFIG_SCHEMA_TEMPLATE_FILE
from .._shared.constants import CREDENTIAL_SCHEMA_FILE
from .._shared.constants import CREDENTIALS_FOLDER
from .._shared.constants import DEFAULT_CONFIG_FILE
from .._shared.constants import DEFAULT_CREDENTIAL_CONTENTS
from .._shared.constants import DEFAULT_CREDENTIAL_FILE
from .._shared.constants import DEFAULT_INDENT_LEVEL
from .._shared.constants import MACRO_SCHEMA_FILE
from .._shared.constants import SESSION_FOLDER
from .._shared.constants import SNAPSHOT_SCHEMA_FILE
from .._shared.constants import SNAPSHOT_SCHEMA_TEMPLATE_FILE
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from .._shared.helpers_print import thread_print_exc
from .._shared.types import SCHEMA_MAPPING
from .._shared.types import ConfigDict
from .._shared.types import CredentialDict
from .._shared.types import CredentialTypeDict
from .._shared.types import MacroDict
from .._shared.types import SessionLogDict
from .._shared.types import SnapshotDict


def read_json_file(
  filename: str | Path,
  file_descriptor: str,
  *,
  suppress_error: bool = False,
) -> tuple[Any, str]:
  '''
  Open and read JSON file.

  Return as tuple (dumped_json_data, raw_file_contents)
  '''
  try:
    with open(filename, mode='r', encoding='utf-8') as json_file:
      raw_file_contents: str = json_file.read()
      dumped_json_data: Any = json.loads(raw_file_contents)
  except OSError:
    thread_print(ColorText.error(
      f"Failed to open {file_descriptor} file {Path(filename).absolute()}"
    ))
    if suppress_error:
      thread_print(ColorText.error(
        "You should investigate this error! Moving on for now..."
      ))
      thread_print_exc()
      return None, ''
    raise
  except JSONDecodeError as e:
    thread_print(ColorText.error(
      f"Failed to decode JSON file {Path(filename).absolute()} \n"
      f"Reason: {e.args[0]}"
    ))
    if suppress_error:
      thread_print(ColorText.error(
        "You should investigate this error! Moving on for now..."
      ))
      thread_print_exc()
      return None, ''
    raise
  return dumped_json_data, raw_file_contents
# ------------------------------------------------------------------------------


def write_json_file(
  json_data: Any,
  filename: str | Path,
  file_descriptor: str,
  *,
  suppress_error: bool = False,
) -> None:
  '''Open and write JSON file.'''
  try:
    with open(filename, mode='w', encoding='utf-8') as json_file:
      json.dump(json_data, json_file, indent=DEFAULT_INDENT_LEVEL)
      json_file.write('\n')
  except OSError:
    thread_print(ColorText.error(
      f"Failed to open {file_descriptor} file {Path(filename).absolute()}"
    ))
    if suppress_error:
      thread_print(ColorText.error(
        "You should investigate this error! Moving on for now..."
      ))
      thread_print_exc()
      return
    raise
  thread_print(ColorText.warning(
    f"Updated contents of {file_descriptor} file "
    f"{ColorText.path(str(Path(filename).absolute()))} "
  ))
# ------------------------------------------------------------------------------


def read_config_schema_file() -> SCHEMA_MAPPING:
  '''Open and read JSON config schema file.'''
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=CONFIG_SCHEMA_FILE,
    file_descriptor='configuration schema'
  )
  return schema_data
# ------------------------------------------------------------------------------


def read_config_schema_template_file() -> SCHEMA_MAPPING:
  '''Open and read JSON config schema template file.'''
  template_data: SCHEMA_MAPPING
  template_data, _ = read_json_file(
    filename=CONFIG_SCHEMA_TEMPLATE_FILE,
    file_descriptor='configuration schema template'
  )
  return template_data
# ------------------------------------------------------------------------------


def write_config_schema_file(schema_data: SCHEMA_MAPPING) -> None:
  '''Open and write JSON config schema file.'''
  write_json_file(
    json_data=schema_data,
    filename=CONFIG_SCHEMA_FILE,
    file_descriptor="configuration validation schema"
  )
# ------------------------------------------------------------------------------


def read_snapshot_schema_file() -> SCHEMA_MAPPING:
  '''Open and read JSON snapshot schema file.'''
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=SNAPSHOT_SCHEMA_FILE,
    file_descriptor='snapshot schema'
  )
  return schema_data
# ------------------------------------------------------------------------------


def read_snapshot_schema_template_file() -> SCHEMA_MAPPING:
  '''Open and read JSON schema template file.'''
  template_data: SCHEMA_MAPPING
  template_data, _ = read_json_file(
    filename=SNAPSHOT_SCHEMA_TEMPLATE_FILE,
    file_descriptor='snapshot schema template'
  )
  return template_data
# ------------------------------------------------------------------------------


def write_snapshot_schema_file(schema_data: SCHEMA_MAPPING) -> None:
  '''Open and write JSON schema file.'''
  write_json_file(
    json_data=schema_data,
    filename=SNAPSHOT_SCHEMA_FILE,
    file_descriptor="snapshot validation schema"
  )
# ------------------------------------------------------------------------------


def print_ValidationError_report(
  error: ValidationError,
  json_str: str,
  filename: str | Path,
) -> None:
  '''
  Print detailed validation report for ValidationError `error` with
  detailed position, reason and key description.
  '''
  error_path = f"/{'/'.join(str(o) for o in error.absolute_path)}"
  source_map: TSourceMap = calculate(json_str)
  error_source: Entry = source_map.get(
    error_path if error_path != '/' else '',
    Entry(Location(0, 0, 0), Location(0, 0, 0))
  )
  start: Location | None = error_source.key_start
  if start is None:
    start = error_source.value_start
  end: Location = error_source.value_end
  thread_print(
    ColorText.error(f"Validation error in {Path(filename).absolute()}")
  )
  thread_print(ColorText.error(
    f"-- Starting at line {start.line}, column {start.column}, "
    f"position {start.position}"
  ))
  thread_print(ColorText.error(
    f"-- Ending at line {end.line}, column {end.column}, "
    f"position {end.position}"
  ))
  thread_print(ColorText.error(f"Key: {error_path}"))
  thread_print(ColorText.error(f"Reason: {error.message}"))
  if 'description' in error.schema:
    thread_print(ColorText.error(
      f"Description: {error.schema['description']}"
    ))
# ------------------------------------------------------------------------------


def read_config(filename: str | Path = DEFAULT_CONFIG_FILE) -> ConfigDict:
  '''
  Read and validate JSON config file containing application data.

  Return a dict of the data contained in the config file.

  Config files that failed to validate will output the exact reason
  why and where they failed before raising their Exceptions again.
  '''
  # ----- Read files -----
  json_data: ConfigDict
  json_str: str
  json_data, json_str = read_json_file(
    filename=filename,
    file_descriptor='configuration'
  )
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=CONFIG_SCHEMA_FILE,
    file_descriptor='configuration schema'
  )
  # ----- Validate data -----
  try:
    validate(json_data, schema=schema_data)
  except ValidationError as e:
    print_ValidationError_report(e, json_str, filename)
    raise
  return json_data
# ------------------------------------------------------------------------------


def read_credentials(
  filename: str | Path = DEFAULT_CREDENTIAL_FILE
) -> CredentialDict:
  '''
  Read and validate JSON config file containing credential data.

  Return a dict of the data contained in the config file.

  Config files that failed to validate will output the exact reason
  why and where they failed before raising their Exceptions again.
  '''
  # ----- Read files -----
  json_data: CredentialDict
  json_str: str
  try:
    json_data, json_str = read_json_file(
      filename=filename,
      file_descriptor='credential'
    )
  except OSError:
    # Create a default credential file if none is found
    if Path(filename).absolute() == DEFAULT_CREDENTIAL_FILE.absolute():
      create_default_credential_file(filename)
    # still raise to exit, because the default crednetial file contents
    # are useless and need to be adjusted by the user!
    raise
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=CREDENTIAL_SCHEMA_FILE,
    file_descriptor='credential schema'
  )
  # ----- Validate data -----
  try:
    validate(json_data, schema=schema_data)
  except ValidationError as e:
    print_ValidationError_report(e, json_str, filename)
    raise
  return json_data
# ------------------------------------------------------------------------------


def create_default_credential_file(filename: Path | str) -> None:
  '''
  create missing credentials.json with default contents to fill out.
  '''
  filepath: Path = Path(filename)
  CREDENTIALS_FOLDER.mkdir(parents=True, exist_ok=True)
  with open(file=filepath, mode='w', encoding='utf-8') as file:
    file.write(DEFAULT_CREDENTIAL_CONTENTS)
    file.write('\n')
  fill_credentials: str = ColorText.error(
    'Please fill out the required credential data to authenticate bot.'
  )
  thread_print(
    "Created default credentials.json file for missing file "
    f"{ColorText.path(str(filepath.absolute()))}\n"
    f"{fill_credentials}"
  )
# ------------------------------------------------------------------------------


def read_config_and_credentials(
  config_arg: str | None = None,
  credential_arg: str | None = None
) -> tuple[ConfigDict, CredentialDict]:
  '''
  Read and validate JSON configuration files, return Mappings.

  Update schema file if outdated.
  '''
  # Read config and credentials from files
  config_file: str | Path = config_arg if config_arg else DEFAULT_CONFIG_FILE
  config_path: Path = Path(config_file)
  thread_print(
    "Reading application configuration from file: "
    f"{ColorText.path(str(config_path.absolute()))} "
  )
  try:
    config: ConfigDict = read_config(filename=config_path)
  except (OSError, JSONDecodeError, ValidationError):
    # printed in subroutine, explicitly raise again because caller has to catch
    raise
  credentials_file: str | Path = (
    credential_arg if credential_arg else DEFAULT_CREDENTIAL_FILE
  )
  credentials_path: Path = Path(credentials_file)
  thread_print(
    "Reading secret credentials from file: "
    f"{ColorText.path(str(credentials_path.absolute()))} "
  )
  try:
    credentials: CredentialDict = read_credentials(filename=credentials_path)
  except (OSError, JSONDecodeError, ValidationError):
    # printed in subroutine, explicitly raise again because caller has to catch
    raise
  return config, credentials
# ------------------------------------------------------------------------------


def read_macro_file(filename: str | Path) -> MacroDict:
  '''
  Read and validate JSON file containing macro data.

  Return a dict of the data contained in the macro file.

  Macro files that failed to validate will output the exact reason
  why and where they failed before raising their Exceptions again.
  '''
  if filename == '':
    return {}
  # ----- Read files -----
  json_data: MacroDict | None
  json_str: str
  json_data, json_str = read_json_file(
    filename=filename,
    file_descriptor='macro',
    suppress_error=True,
  )
  if json_data is None:
    return {}
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=MACRO_SCHEMA_FILE,
    file_descriptor='macro schema',
    suppress_error=True,
  )
  # ----- Validate data -----
  try:
    validate(json_data, schema=schema_data)
  except ValidationError as e:
    print_ValidationError_report(e, json_str, filename)
    thread_print_exc()
    return {}
  return json_data
# ------------------------------------------------------------------------------


def write_macro_file(filename: str | Path, macro_dict: MacroDict) -> None:
  '''
  Convert `macro_dict` into JSON and validate with `MACRO_SCHEMA_FILE`.

  Write JSON data to file pointed to by `filename`

  Macro files that fail to validate will output the exact reason
  why and where they failed before raising their Exceptions again.
  '''
  if filename == '':
    raise ValueError("Invalid argument: filename")
  json_data: MacroDict = macro_dict
  json_str: str = json.dumps(json_data, indent=DEFAULT_INDENT_LEVEL)
  # ----- Read file -----
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=MACRO_SCHEMA_FILE,
    file_descriptor='macro schema',
    suppress_error=True,
  )
  # ----- Validate data -----
  try:
    validate(json_data, schema=schema_data)
  except ValidationError as e:
    thread_print(
      "=== Contents of failed file: ===\n"
      f"{json_str}\n"
      "=== End of failed file ==="
    )
    print_ValidationError_report(e, json_str, filename)
    thread_print_exc()
    return
  # ----- Write file -----
  try:
    with open(
      filename,
      mode='w',
      encoding='utf-8',
      newline='\n'
    ) as config_file:
      config_file.write(json_str)
      config_file.write('\n')
  except OSError:
    thread_print(ColorText.error(
      f"Failed to open macro file {str(filename)}\n"
      "You should investigate this error! Moving on for now..."
    ))
    thread_print_exc()
# ------------------------------------------------------------------------------


def read_snapshot_file(filename: str | Path) -> SnapshotDict:
  '''
  Read and validate JSON file containing snapshot data.

  Return a dict of the data contained in the snapshot file.

  Snapshot files that failed to validate will output the exact reason
  why and where they failed before raising their Exceptions again.
  '''
  if filename == '':
    return {}
  # ----- Read files -----
  json_data: SnapshotDict | None
  json_str: str
  json_data, json_str = read_json_file(
    filename=filename,
    file_descriptor='snapshot',
    suppress_error=True,
  )
  if json_data is None:
    return {}
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=SNAPSHOT_SCHEMA_FILE,
    file_descriptor='snapshot schema',
    suppress_error=True,
  )
  # ----- Validate data -----
  try:
    validate(json_data, schema=schema_data)
  except ValidationError as e:
    print_ValidationError_report(e, json_str, filename)
    thread_print_exc()
    return {}
  return json_data
# ------------------------------------------------------------------------------


def write_snapshot_file(
  filename: str | Path,
  snapshot_dict: SnapshotDict
) -> None:
  '''
  Convert `snapshot_dict` into JSON and validate with `SNAPSHOT_SCHEMA_FILE`.

  Write JSON data to file pointed to by `filename`

  Snapshot files that fail to validate will output the exact reason
  why and where they failed before raising their Exceptions again.
  '''
  if filename == '':
    raise ValueError("Invalid argument: filename")
  json_data: SnapshotDict = snapshot_dict
  json_str: str = json.dumps(json_data, indent=DEFAULT_INDENT_LEVEL)
  # ----- Read file -----
  schema_data: SCHEMA_MAPPING
  schema_data, _ = read_json_file(
    filename=SNAPSHOT_SCHEMA_FILE,
    file_descriptor='snapshot schema',
    suppress_error=True,
  )
  # ----- Validate data -----
  try:
    validate(json_data, schema=schema_data)
  except ValidationError as e:
    thread_print(
      "=== Contents of failed file: ===\n"
      f"{json_str}\n"
      "=== End of failed file ==="
    )
    print_ValidationError_report(e, json_str, filename)
    thread_print_exc()
    return
  # ----- Write file -----
  try:
    with open(filename, mode='w', encoding='utf-8') as config_file:
      config_file.write(json_str)
      config_file.write('\n')
  except OSError:
    thread_print(ColorText.error(
      f"Failed to open snapshot file {str(filename)}\n"
      "You should investigate this error! Moving on for now..."
    ))
    thread_print_exc()
# ------------------------------------------------------------------------------


def write_session_file(
  filename: str | Path,
  session_dict: SessionLogDict
) -> None:
  '''
  Convert and dump `session_dict` to JSON file pointed to by `filename`.
  '''
  if filename == '':
    raise ValueError("Invalid argument: filename")
  json_data: SessionLogDict = session_dict
  # ----- Write file -----
  try:
    with open(filename, mode='w', encoding='utf-8') as config_file:
      json.dump(json_data, config_file, indent=None, separators=(',', ':'))
      config_file.write('\n')
  except OSError:
    thread_print(ColorText.error(
      f"Failed to write session file {str(filename)}\n"
      "You should investigate this error! Moving on for now..."
    ))
    thread_print_exc()
# ------------------------------------------------------------------------------


def write_session(
  session_dict: SessionLogDict,
  filename: str | Path | None = None
) -> str:
  '''
  Convert and dump `session_dict` to JSON file in (auto-generated) file
  in SESSION_FOLDER
  '''
  if filename is None:
    timestamp: str = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]
    filename = f"session_{timestamp}.json"
  filepath: Path
  if isinstance(filename, Path):
    filepath = filename
  else:
    filepath = SESSION_FOLDER / filename
  SESSION_FOLDER.mkdir(parents=True, exist_ok=True)
  write_session_file(filepath, session_dict)
  return str(filepath.absolute())
# ------------------------------------------------------------------------------


class InvalidCredentialsError(Exception):
  '''
  Raised when a credential is invalid.
  '''
  pass


@overload
def decode_credential(
  credential: CredentialTypeDict,
  _default: str,
  /,
) -> str:
  ...


@overload
def decode_credential(
  credential: CredentialTypeDict,
  _default: None,
  /,
) -> str | None:
  ...


@overload
def decode_credential(
  credential: None,
  _default: str,
  /,
) -> str:
  ...


@overload
def decode_credential(
  credential: None,
  _default: None,
  /,
) -> None:
  ...


def decode_credential(
  credential: CredentialTypeDict | None,
  _default: str | None = None,
  /,
) -> str | None:
  '''
  Decode credential data from JSON data.

  The deooding method is based on `credential['type']`.
  '''
  if credential is None:
    return _default
  decoder_method: str = credential['type']
  encoded_value: str = credential['value']
  decoded_value: str | None = _default

  if decoder_method == 'cleartext':
    decoded_value = encoded_value
    return decoded_value

  if decoder_method == 'hex':
    try:
      decoded_value = unhexlify(encoded_value).decode('utf-8')
    except ValueError:
      thread_print(ColorText.error(
        f"Unable to decode hex value to utf-8: {encoded_value}"
      ))
      return _default
    return decoded_value

  if decoder_method == 'base64':
    try:
      decoded_value = b64decode(encoded_value).decode('utf-8')
    except ValueError:
      thread_print(ColorText.error(
        f"Unable to decode base64 value to utf-8: {encoded_value}"
      ))
      return _default
    return decoded_value

  if decoder_method == 'file':
    path = Path(encoded_value)
    try:
      with path.open('r', encoding='utf-8', errors='strict') as file:
        decoded_value = file.readline().rstrip('\r\n')
    except (OSError, ValueError) as e:
      thread_print(ColorText.error(
        f"Unable to read file: {encoded_value}\n"
        f"due to error: {e}"
      ))
      return _default
    return decoded_value

  if decoder_method == 'env':
    decoded_value = getenv(encoded_value, None)
    if decoded_value is None:
      thread_print(ColorText.error(
        f"Missing environment variable: {encoded_value}"
      ))
      return _default
    return decoded_value
  # Default:
  return _default
# ------------------------------------------------------------------------------
