'''
This module serves as the basis for other modules that send
input via the `press_multiple_keys` method.
'''

# native imports
from collections.abc import Mapping
from collections.abc import Sequence
from functools import partial
from random import choices
from typing import Any
from typing import ClassVar

# internal imports
from ..._interfaces._actionset import ActionsetValidationError
from ..._interfaces._chatmsg import AbstractChatMessage
from ..._interfaces._input_handler import AbstractInputHandler
from ..._shared.constants import INPUT_TYPE
from ..._shared.constants import VERB_DELAY_DURATION_REGEX
from ..._shared.helpers_color import ColorText
from ..._shared.helpers_native import clamp
from ..._shared.helpers_print import thread_print
from ..._shared.types import FuncArgsDict
from ..._shared.types import MacroDict
from ..._shared.types import Partial_VerbParamDict
from ..._shared.types import VerbParamDict
from ...config.json_utils import read_macro_file
from ...config.json_utils import write_macro_file
from ..actionset import Actionset


class InvalidVerbException(Exception):
  '''
  Indicates that verb_dict does not accept the given argument.
  '''
  pass
# ------------------------------------------------------------------------------


# ==================================================================================================
class MultiKey_BaseActionset(Actionset):
  '''
  Advanced base class for Actionsets that use
  `input_handler.press_multiple_Keys` for sending input.
  '''
  # Class variables:
  name: ClassVar[str] = 'MultiKey Base Actionset'
  key_dict: ClassVar[Mapping[str, str | Sequence[str]]] = {}
  input_handler: ClassVar[type[AbstractInputHandler]]
  # Instance variables:
  verb_dict: dict[str, list[VerbParamDict]]
  macro_dict: dict[str, list[VerbParamDict]]
  random_verb: list[str]
  random_weight: list[float]
  # ----------------------------------------------------------------------------

  def __init__(self, **kwargs: Any) -> None:
    '''
    Advanced base class for Actionsets that use
    `input_handler.press_multiple_Keys` for sending input.
    '''
    super().__init__(**kwargs)
    self.verb_dict = {}
    self.macro_dict = {}

    self.load_macros_from_file()

    _random_args: list[tuple[str, float]] = []
    # iterating over _random_args twice since zip(*_random_args)
    # does not infer type information correctly!
    self.random_verb = [t[0] for t in _random_args]
    self.random_weight = [t[1] for t in _random_args]
  # ----------------------------------------------------------------------------

  def print_macro_diff(
    self,
    config_name: str,
    older_macro_dict: dict[str, list[VerbParamDict]],
    newer_macro_dict: dict[str, list[VerbParamDict]]
  ) -> None:
    '''
    Diff the differences between older and newer macro_dict and
    print in human-readable colorful format.
    '''
    if self.macro_file is None:
      return
    older_keys: set[str] = set(older_macro_dict.keys())
    newer_keys: set[str] = set(newer_macro_dict.keys())
    removed_macro_names: set[str] = older_keys - newer_keys  # old without new
    added_macro_names: set[str] = newer_keys - older_keys  # new without old
    same_macro_names: set[str] = older_keys & newer_keys  # intersect old & new
    changed_macro_names: set[str] = set()
    for macro_name in same_macro_names:
      if older_macro_dict[macro_name] != newer_macro_dict[macro_name]:
        changed_macro_names.add(macro_name)
    thread_print(
      f'Actionset {self.name}: Updating macros with macro file "{config_name}" '
      f'located in {ColorText.path(str(self.macro_file.absolute()))} '
    )
    if removed_macro_names:
      thread_print(ColorText.removed(
        f"- Removing macros: {', '.join(removed_macro_names)}"
      ))
    if added_macro_names:
      thread_print(ColorText.added(
        f"+ Adding macros: {', '.join(added_macro_names)}"
      ))
    if changed_macro_names:
      thread_print(ColorText.changed(
        f"± Changing macros: {', '.join(changed_macro_names)}"
      ))
  # ----------------------------------------------------------------------------

  def get_macro_dict(self) -> dict[str, list[VerbParamDict]]:
    '''
    Get all currently stored macro without action prefix.
    '''
    local_macro_dict: dict[str, list[VerbParamDict]] = {
      key: value
      for key, value in self.macro_dict.items()
      if not key.startswith(self.action_prefix)  # Remove prefixed macros
    }
    return local_macro_dict
  # ----------------------------------------------------------------------------

  def set_macro_dict(self, new_macros: dict[str, list[VerbParamDict]]) -> None:
    '''
    Change currently stored macros to macros stored in `new_macro_dict`
    '''
    new_macro_dict = new_macros.copy()  # Don't modifiy original
    new_macro_dict.update({
      f"{self.action_prefix}{key}": value  # Add prefixed macros to dict
      for key, value in new_macro_dict.items()
    })
    self.macro_dict = new_macro_dict
  # ----------------------------------------------------------------------------

  def load_macros_from_file(self) -> None:
    '''
    Update the local copy of `self.macro_dict` with the contents of
    `self.macro_file`
    '''
    if self.macro_file is None:
      return
    macro_config: MacroDict = read_macro_file(self.macro_file)
    if not macro_config:
      return
    # Old = local
    # New = file
    local_macro_dict: dict[str, list[VerbParamDict]] = self.get_macro_dict()
    file_macro_dict: dict[str, list[VerbParamDict]] = (
      macro_config.get('macros', {})
    )

    self.print_macro_diff(
      config_name=macro_config.get('name', ''),
      older_macro_dict=local_macro_dict,
      newer_macro_dict=file_macro_dict
    )

    self.set_macro_dict(file_macro_dict)
  # ----------------------------------------------------------------------------

  def save_macros_to_file(self) -> None:
    '''
    Update the contents of `self.macro_file` with the local copy of
    `self.macro_dict`
    '''
    if not (self.persistent_macros and self.macro_file):
      return
    macro_config: MacroDict = read_macro_file(self.macro_file)

    # Old = file
    # New = local
    local_macro_dict: dict[str, list[VerbParamDict]] = self.get_macro_dict()
    file_macro_dict: dict[str, list[VerbParamDict]] = (
      macro_config.get('macros', {})
    )

    self.print_macro_diff(
      config_name=macro_config.get('name', ''),
      older_macro_dict=file_macro_dict,
      newer_macro_dict=local_macro_dict
    )

    # Change macro_config contents and then write back to file:
    macro_config['macros'] = local_macro_dict
    write_macro_file(self.macro_file, macro_config)
  # ----------------------------------------------------------------------------

  def translate_verb_parameters_to_key(
    self,
    verb_parameters: VerbParamDict
  ) -> str | None:
    '''
    Extract the relevant value from `key_dict` based on the `key`
    parameter of `verb_parameters`.

    Outsourced to its own method, since it is subclass implementation
    dependent.
    '''
    raise NotImplementedError
  # ----------------------------------------------------------------------------

  def translate_message_contents_to_args_list(
    self,
    message: str
  ) -> list[FuncArgsDict]:
    '''
    Extracts a list of keyword arguments for `input_handler.press_multiple_Keys`
    from the contents of the message provided by user action commands.
    '''
    args_list: list[FuncArgsDict] = []

    regex_result: tuple[str, str, str]
    for regex_result in VERB_DELAY_DURATION_REGEX.findall(message.lower()):
      verb: str = regex_result[0]
      param_delay: int = int(regex_result[1]) if regex_result[1] else 0
      param_duration: int = int(regex_result[2]) if regex_result[2] else 0

      try:
        lookup_result: list[VerbParamDict] | None
        # Lookup order: verb_dict -> macro_dict -> Skip
        lookup_result = (
          self.verb_dict.get(verb, self.macro_dict.get(verb, None))
        )
        if lookup_result is None:
          continue
        verb_param_list: list[VerbParamDict] = lookup_result

        # first default duration in param list decides total action duration,
        # all other durations in other list entries will be offset accordingly.
        # Example:
        # verb +example with 3 sub actions with different default durations:
        # * first duration 100 ms,
        # * second duration 150 ms,
        # * third duration 80 ms
        # explicitly called with duration 200 ms (+example 200),
        # will result in the first action taking 200+(100-100)=200 ms,
        # the second 200+(150-100)=250 ms,
        # the third 200+(80-100)=180 ms
        inherent_duration: int = verb_param_list[0]['duration']

        for verb_param in verb_param_list:
          function_args: FuncArgsDict = {
            'key': '',
            'delay': 0,
            'duration': 0,
          }

          key = self.translate_verb_parameters_to_key(verb_param)
          if key is None:
            # This should never happen if verb_dict and key_dict are matching
            # to each other. (covered by validate() method)
            thread_print(ColorText.error(
              "Mismatch between verb_dict and key_dict detected!\n"
              f"No key found for verb_parameters {verb_param}"
            ))
            # Nevertheless, we continue execution to not stop the app dead in its track.
            # Other commands should still work after all.
            raise TypeError("Mismatch between verb_dict and key_dict detected!")
          function_args['key'] = key

          min_time: int = verb_param['min_time']
          max_time: int = verb_param['max_time']
          inherent_delay: int = verb_param['delay']

          delay = int(clamp(0, param_delay + inherent_delay, max_time))
          function_args['delay'] = delay

          if verb_param["input_type"] == INPUT_TYPE.PRESS_KEY:
            # delay and duration share the same max time for troll prevention
            if param_duration:
              # duration_offset will always be 0 for first entry in verb_param_list
              # and is therefore only useful for advanced multi-key verbs
              duration_offset: int = verb_param['duration'] - inherent_duration
              duration = int(clamp(
                min_time, param_duration + duration_offset, max_time - delay
              ))
            else:
              # no duration value in user input -> no offset adjustment necessary
              default_duration: int = verb_param['duration']
              duration = int(clamp(
                min_time, default_duration, max_time - delay
              ))
            function_args['duration'] = duration
          else:
            # Type hold/release
            function_args['duration'] = verb_param["input_type"]

          args_list.append(function_args.copy())

      except (IndexError, TypeError, AttributeError, KeyError) as e:
        thread_print(ColorText.error(
          f"{self.__class__.__name__}."
          f"translate_message_contents_to_args_list(message={message!r}): "
          f"Exception {e!r}\n"
          "This should not have happened! This message will be ignored and "
          "execution will continue, but the root cause should be investigated!"
        ))
        continue
    return args_list
  # ----------------------------------------------------------------------------

  def compile_action_string_into_macro(self, message: str) -> list[VerbParamDict]:
    '''
    Transform a series of action commands into its own dedicated macro.
    '''
    macro: list[VerbParamDict] = []

    regex_result: tuple[str, str, str]
    for regex_result in VERB_DELAY_DURATION_REGEX.findall(message.lower()):
      verb: str = regex_result[0]
      delay: int = int(regex_result[1]) if regex_result[1] else 0
      duration: int = int(regex_result[2]) if regex_result[2] else 0

      try:
        lookup_result: list[VerbParamDict] | None
        # Lookup order: verb_dict -> macro_dict -> raise InvalidVerbException
        lookup_result = (
          self.verb_dict.get(verb, self.macro_dict.get(verb, None))
        )
        if lookup_result is None:
          raise InvalidVerbException(f"'{verb}' is not a valid verb/macro")
        verb_param_list: list[VerbParamDict] = lookup_result

        for original_verb_param in verb_param_list:
          verb_param: VerbParamDict = original_verb_param.copy()
          min_time: int = verb_param['min_time']
          max_time: int = verb_param['max_time']

          delay = int(clamp(0, delay, max_time))
          verb_param['delay'] = delay

          if duration:
            duration = int(clamp(min_time, duration, max_time - delay))
            # only modify duration if it's explicit, otherwise keep default
            verb_param['duration'] = duration

          macro += [verb_param]

      except (TypeError, AttributeError, KeyError):
        raise InvalidVerbException(
          f"'{verb}' is not a valid verb in verb_dict"
        )
    return macro
  # ----------------------------------------------------------------------------

  def add_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro from `msg` and add it to `macro_dict` if possible.

    Return `True` if successful, `False` otherwise.
    '''
    # Returns False instead of raising exceptions because the chat command
    # will iterate through all exisiting actionsets.
    # In a 8 player configuration, that could result in raising 8 exceptions. So
    # the chat command has been designed to just collect all failed actionsets
    # TODO: Find an elegant way to return something else beside False and
    # give more detailed feedback
    if not self.allow_changing_macros:
      return False
    message: str = msg.message
    # split into 3 parts: addmacro_command, macro_name, macro_contents
    split_message = message.split(maxsplit=2)
    if len(split_message) < 3:
      thread_print(ColorText.warning(
        "Misformed addMacro command, need 3 arguments!"
      ))
      return False
    macro_name: str = split_message[1].lower()  # force lower case
    if macro_name.startswith(self.action_prefix):  # Remove action prefix
      macro_name = macro_name[len(self.action_prefix):]
    if macro_name in self.macro_dict:
      thread_print(ColorText.warning(
        f"Can't add macro '{macro_name}', macro with same name already exists!"
      ))
      return False
    macro_contents: str = split_message[2]
    # compile macro instructions and handle errors
    try:
      macro: list[VerbParamDict] = (
        self.compile_action_string_into_macro(macro_contents)
      )
    except InvalidVerbException as e:
      thread_print(ColorText.warning(
        f"Can't add macro {macro_name}, {e}"
      ))
      return False
    if not macro:
      thread_print(ColorText.warning(
        f"Can't add macro {macro_name}, Unknown macro compilation error!"
      ))
      return False
    # add macro to dict (unprefixed and prefixed)
    self.macro_dict[macro_name] = macro
    self.macro_dict[f"{self.action_prefix}{macro_name}"] = macro
    # save macro to file if option is set
    if self.persistent_macros and self.macro_file:
      self.save_macros_to_file()
    return True
  # ----------------------------------------------------------------------------

  def change_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro from `msg` and change the same macro in `macro_dict`
    if possible.

    Return `True` if successful, `False` otherwise.
    '''
    # Returns False instead of raising exceptions because the chat command
    # will iterate through all exisiting actionsets.
    # In a 8 player configuration, that could result in raising 8 exceptions. So
    # the chat command has been designed to just collect all failed actionsets
    # TODO: Find an elegant way to return something else beside False and
    # give more detailed feedback
    if not self.allow_changing_macros:
      return False
    message: str = msg.message
    # split into 3 parts: addmacro_command, macro_name, macro_contents
    split_message = message.split(maxsplit=2)
    if len(split_message) < 3:
      thread_print(ColorText.warning(
        "Misformed addMacro command, need 3 arguments!"
      ))
      return False
    macro_name: str = split_message[1].lower()  # force lower case
    if macro_name.startswith(self.action_prefix):  # Remove action prefix
      macro_name = macro_name[len(self.action_prefix):]
    if macro_name not in self.macro_dict:
      thread_print(ColorText.warning(
        f"Can't change macro '{macro_name}', no such macro exists!"
      ))
      return False
    macro_contents: str = split_message[2]
    # compile macro instructions and handle errors
    try:
      macro: list[VerbParamDict] = (
        self.compile_action_string_into_macro(macro_contents)
      )
    except InvalidVerbException as e:
      thread_print(ColorText.warning(
        f"Can't change macro {macro_name}, {e}"
      ))
      return False
    if not macro:
      thread_print(ColorText.warning(
        f"Can't change macro {macro_name}, Unknown macro compilation error!"
      ))
      return False
    # add macro to dict (unprefixed and prefixed)
    self.macro_dict[macro_name] = macro
    self.macro_dict[f"{self.action_prefix}{macro_name}"] = macro
    # save macro to file if option is set
    if self.persistent_macros and self.macro_file:
      self.save_macros_to_file()
    return True
  # ----------------------------------------------------------------------------

  def remove_macro(self, msg: AbstractChatMessage) -> bool:
    '''
    Extract macro_name from `msg` and remove it from `macro_dict` if possible.

    Return `True` if successful, `False` otherwise.
    '''
    # Returns False instead of raising exceptions because the chat command
    # will iterate through all exisiting actionsets.
    # In a 8 player configuration, that could result in raising 8 exceptions. So
    # the chat command has been designed to just collect all failed actionsets
    # TODO: Find an elegant way to return something else beside False and
    # give more detailed feedback
    if not self.allow_changing_macros:
      return False
    message: str = msg.message
    # split into 3 parts: addmacro_command, macro_name
    split_message = message.split(maxsplit=2)
    if len(split_message) < 2:
      thread_print(ColorText.warning(
        "Misformed removeMacro command, need 2 arguments!"
      ))
      return False
    macro_name: str = split_message[1].lower()  # force lower case
    if macro_name.startswith(self.action_prefix):  # Remove action prefix
      macro_name = macro_name[len(self.action_prefix):]
    if macro_name not in self.macro_dict:
      thread_print(ColorText.warning(
        f"Can't remove macro '{macro_name}', no such macro exists!"
      ))
      return False
    del self.macro_dict[macro_name]
    del self.macro_dict[f"{self.action_prefix}{macro_name}"]
    # save macro removal to file if option is set
    if self.persistent_macros and self.macro_file:
      self.save_macros_to_file()
    return True
  # ----------------------------------------------------------------------------

  def reload_macros(self) -> bool:
    '''
    Reload macros from macro file and discard any local changes
    '''
    self.load_macros_from_file()
    return True
  # ----------------------------------------------------------------------------

  def build_partial(self, message: str) -> partial[None] | None:
    '''
    Based on `message`, create a partial function to be used in `input_server`.
    '''
    args_list: list[FuncArgsDict] = (
      self.translate_message_contents_to_args_list(message)
    )
    if len(args_list) == 0:
      return None
    return partial(
      self.input_handler.press_multiple_Keys,
      self.player_index,
      args_list
    )
  # ----------------------------------------------------------------------------

  def translate_user_message_to_action(
    self,
    msg: AbstractChatMessage
  ) -> partial[None] | None:
    '''
    Extract message from `msg` and use its contents to create a
    partial function to be used in `input_server`.
    '''
    if self.message_is_command(msg):
      return self.build_partial(msg.message)
    return None
  # ----------------------------------------------------------------------------

  def random_action(self) -> partial[None]:
    '''
    When the team's queue is empty, random actions can be performed
    instead of sleeping. (Based on `random_verb` and `random_weight`)

    This function serves as a backend function, which takes care of
    selecting which random action to take.
    '''
    random_command: str = (
      choices(self.random_verb, self.random_weight)[0]  # nosec B311
    )
    partial_function = self.build_partial(random_command)
    if partial_function is None:
      raise ValueError(
        f"{self.__class__.__name__}.random_action() Invalid input: "
        f"{random_command}"
      )
    return partial_function
  # ----------------------------------------------------------------------------

  def validate(self) -> bool:
    '''
    Validate that object data is internally consistent.

    Intended to be used after __init__ to detect stuff like
    dict members not behaving correctly!

    * Are all keys in verb_dict present in key_dict?
    '''
    if not super().validate():
      return False
    for verb_dict_key, verb_param_list in self.verb_dict.items():
      for verb_param in verb_param_list:
        if not verb_param['key'] in self.key_dict:
          raise ActionsetValidationError(
            f"Key '{verb_param['key']}' from verb_dict '{verb_dict_key}' is "
            f"missing in key_dict of Actionset '{self.name}'!"
          )
        if verb_param["min_time"] > verb_param["max_time"]:
          raise ActionsetValidationError(
            f"min_time > max_time for key '{verb_param['key']}' of "
            f"verb_dict '{verb_dict_key}' of Actionset '{self.name}'!"
          )
        if (
          verb_param["delay"] + verb_param["duration"] > verb_param["max_time"]
        ):
          raise ActionsetValidationError(
            f"Default delay+duration > max_time for key '{verb_param['key']}' "
            f"of verb_dict '{verb_dict_key}' of Actionset '{self.name}'!"
          )
    return True
# ==================================================================================================


def create_verb_params(
  key: str,
  duration: int = 50,
  delay: int = 0,
  min_time: int = 1,
  max_time: int = 1000,
  input_type: INPUT_TYPE = INPUT_TYPE.PRESS_KEY
) -> VerbParamDict:
  '''
  Helper function to create VerbParamDicts.

  All time values in milliseconds.
  '''
  return {
    'key': key,
    "delay": delay,
    'duration': duration,
    'min_time': min_time,
    'max_time': max_time,
    'input_type': input_type
  }
# ------------------------------------------------------------------------------


def partial_create_verb_params(
  duration: int = 50,
  delay: int = 0,
  min_time: int = 1,
  max_time: int = 1000,
  input_type: INPUT_TYPE = INPUT_TYPE.PRESS_KEY
) -> Partial_VerbParamDict:
  '''
  return partial object with support for type hinting
  '''
  return partial(
    create_verb_params,
    duration=duration,
    delay=delay,
    min_time=min_time,
    max_time=max_time,
    input_type=input_type
  )
# ------------------------------------------------------------------------------


# List of all Classes that should be available in config files.
# Leave empty if classes are not supposed to be used directly.
_EXPORT_CLASSES_: list[type[Actionset]] = [
]
