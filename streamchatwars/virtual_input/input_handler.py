'''
This module is providing basic input functions to actionsets.

Classes are used as namespaces that hold no instance data.
'''

# native imports
import asyncio
from collections.abc import Callable
from collections.abc import Coroutine
from collections.abc import Sequence
from functools import partial
from time import sleep
from typing import Any
from typing import ClassVar

# internal imports
from .._interfaces._gamepads import AbstractGamepad
from .._interfaces._gamepads import AbstractReport
from .._interfaces._input_handler import AbstractInputHandler
from .._shared.constants import INPUT_TYPE
from .._shared.constants import MILLISEC_TO_SEC_MULT
from .._shared.constants import XUSB_BUTTON_MAPPING
from .._shared.global_data import GlobalData
from .._shared.helpers_native import nop
from .._shared.types import FuncArgsDict


# ------------------------------------------------------------------------------
# Try importing pydirectinput if it's available. Fall back to a local
# implementation so that the ImportError doesn't cascade.
# Reason: Downstream projects like GamepadClient don't need keyboard functions
try:
  # pip imports
  from pydirectinput import isValidKey
  from pydirectinput import keyDown
  from pydirectinput import keyUp
  from pydirectinput import write
except ImportError:
  # internal imports
  from ..fallback._pydirectinput import isValidKey
  from ..fallback._pydirectinput import keyDown
  from ..fallback._pydirectinput import keyUp
  from ..fallback._pydirectinput import write
# ------------------------------------------------------------------------------


# ==================================================================================================
class BasicGamepadHandler(AbstractInputHandler):
  '''
  Input Handler class that passes press_keys functions to the
  virtual gamepad instance.
  '''
  @classmethod
  def _keyDown(cls, index: int, key: str) -> None:
    '''
    set state of `key` of gamepad with index `index` to pressed.
    '''
    gamepad: AbstractGamepad | None = GlobalData.Gamepads.get(index)
    if gamepad is None:
      return
    gamepad.press_pseudo_key(key)
  # ----------------------------------------------------------------------------

  @classmethod
  def _keyUp(cls, index: int, key: str) -> None:
    '''
    set state of `key` of gamepad `index` to released.
    '''
    gamepad: AbstractGamepad | None = GlobalData.Gamepads.get(index)
    if gamepad is None:
      return
    gamepad.release_pseudo_key(key)
  # ----------------------------------------------------------------------------

  @classmethod
  async def async_press_Key(
    cls,
    index: int,
    key: str | None = None,
    duration: int = 0,
    delay: int = 0
  ) -> None:
    '''
    Press and release `key` of gamepad `index` asynchronously.

    Supports delayed execution.
    '''
    if key is None:
      return
    if delay > 0:
      await asyncio.sleep(delay * MILLISEC_TO_SEC_MULT)
    if duration != INPUT_TYPE.RELEASE_KEY:  # Don't hold when releasing
      cls._keyDown(index, key)
    if duration > 0:  # only branch if actually waiting
      await asyncio.sleep(duration * MILLISEC_TO_SEC_MULT)
    if duration != INPUT_TYPE.HOLD_KEY:  # Don't release when holding
      cls._keyUp(index, key)
  # ----------------------------------------------------------------------------

  @classmethod
  async def async_press_multiple_Keys(
    cls,
    index: int,
    args_list: Sequence[FuncArgsDict]
  ) -> None:
    '''
    Press and release multiple keys asynchronously.

    `args_list` contains a list of dictionaries that have to include
    the arguments for `async_press_Key`
    (`index`, `key`, `duration`, `delay`)
    '''
    kwargs: FuncArgsDict
    call_list: list[Coroutine[Any, Any, None]] = []
    for kwargs in args_list:
      call_list.append(cls.async_press_Key(index, **kwargs))
    await asyncio.gather(*call_list)
  # ----------------------------------------------------------------------------

  @classmethod
  def press_multiple_Keys(
    cls,
    index: int,
    args_list: Sequence[FuncArgsDict]
  ) -> None:
    '''
    Press and release multiple keys.
    Use asyncio to handle the timing of multiple keys in parallel.
    '''
    asyncio.run(cls.async_press_multiple_Keys(index, args_list))
  # ----------------------------------------------------------------------------

  @classmethod
  def set_REPORT(cls, index: int, report: AbstractReport) -> None:
    gamepad: AbstractGamepad | None = GlobalData.Gamepads.get(index)
    if gamepad is None:
      return
    gamepad.report = report
    gamepad.update()
  # ----------------------------------------------------------------------------

  @classmethod
  def valid_key(cls, index: int, key: str) -> bool:
    '''
    Does the key represent a valid key for this input handler
    (is it accepeted in press_multiple_Keys()'s args_list parameter)?
    '''
    gamepad: AbstractGamepad | None = GlobalData.Gamepads.get(index)
    if gamepad is None:
      raise ValueError(f"GAMEPAD_DICT has no index {index}")
    return (
      key in gamepad.axis_mapping
      or key in XUSB_BUTTON_MAPPING
    )
# ==================================================================================================


# ==================================================================================================
class SleepGamepadHandler(BasicGamepadHandler):
  '''
  Subclass of `BasicGamepadHandler` that replaces all actual
  input functions with NOPs, effectively leaving only the
  sleep routines. (To keep in sync with remote InputServer instances)
  '''
  @classmethod
  def _keyDown(cls, index: int, key: str) -> None:
    pass
  # ----------------------------------------------------------------------------

  @classmethod
  def _keyUp(cls, index: int, key: str) -> None:
    pass
# ==================================================================================================


# ==================================================================================================
class DelayedGamepadHandler(BasicGamepadHandler):
  '''
  Subclass of `BasicGamepadHandler` that adds an additional delay before
  actions are executed.
  The delay is variable based on global file event state, allowing
  the user to directly control random action delay and tweak its sheer
  input spam capabilities on the fly.
  '''
  @classmethod
  def press_multiple_Keys(
    cls,
    index: int,
    args_list: Sequence[FuncArgsDict]
  ) -> None:
    '''
    Press and release multiple keys after delay set by global file event state.
    '''
    artifical_delay: float = GlobalData.EventStates.delay_random()
    if artifical_delay > 0:
      sleep(artifical_delay * MILLISEC_TO_SEC_MULT)
    super().press_multiple_Keys(index, args_list)
# ==================================================================================================


# ==================================================================================================
class DelayedSleepGamepadHandler(SleepGamepadHandler, DelayedGamepadHandler):
  '''
  Combine Delay and Sleep for GamepadHandler
  '''
  pass
# ==================================================================================================


# ==================================================================================================
class BasicKeyboardHandler(AbstractInputHandler):
  '''
  Input Handler class that passes input functions to
  `WinAPI SendInput` for keyboard input emulation.

  (Uses `pydirectinput` instead of raw `SendInput` calls)
  '''
  _typewrite: ClassVar[Callable[..., None]] = partial(
    write,
    _pause=False,
    auto_shift=True,
  )
  _keyDown: ClassVar[Callable[..., None | bool]] = partial(
    keyDown,
    _pause=False,
  )
  _keyUp: ClassVar[Callable[..., None | bool]] = partial(
    keyUp,
    _pause=False,
  )
  # ----------------------------------------------------------------------------

  @classmethod
  def typewrite(cls, text: str) -> None:
    '''
    call `pydirectinput`'s `typewrite` function to translate
    `text` into a series of `SendInput` calls.
    '''
    cls._typewrite(text)
  # ----------------------------------------------------------------------------

  @classmethod
  async def async_press_Key(
    cls,
    key: str | None = None,
    duration: int = 0,
    delay: int = 0
  ) -> None:
    '''
    Press and release keyboard key `key` asynchronously.

    Supports delayed execution.
    '''
    if key is None:
      return
    if delay > 0:
      await asyncio.sleep(delay * MILLISEC_TO_SEC_MULT)
    if duration != INPUT_TYPE.RELEASE_KEY:  # Don't hold when releasing
      cls._keyDown(key)
    if duration > 0:  # only branch if actually waiting
      await asyncio.sleep(duration * MILLISEC_TO_SEC_MULT)
    if duration != INPUT_TYPE.HOLD_KEY:  # Don't release when holding
      cls._keyUp(key)
  # ----------------------------------------------------------------------------

  @classmethod
  async def async_press_multiple_Keys(
    cls,
    args_list: Sequence[FuncArgsDict]
  ) -> None:
    '''
    Press and release multiple keys asynchronously.

    `args_list` contains a list of dictionaries that have to include
    the arguments for `async_press_Key`
    (`key`, `duration`, `delay`)
    '''
    kwargs: FuncArgsDict
    call_list: list[Coroutine[Any, Any, None]] = []
    for kwargs in args_list:
      call_list.append(cls.async_press_Key(**kwargs))
    await asyncio.gather(*call_list)
  # ----------------------------------------------------------------------------

  @classmethod
  def press_multiple_Keys(
    cls,
    index: int,  # fake argument to stay in sync with Gamepad
    args_list: Sequence[FuncArgsDict]
  ) -> None:
    '''
    Press and release multiple keys.
    Use asyncio to handle the timing of multiple keys in parallel.
    '''
    asyncio.run(cls.async_press_multiple_Keys(args_list))
  # ----------------------------------------------------------------------------

  @classmethod
  def valid_key(
    cls,
    index: int,  # fake argument to stay in sync with Gamepad
    key: str
  ) -> bool:
    '''
    Does the key represent a valid key for this input handler
    (is it accepeted in press_multiple_Keys()'s args_list parameter)?
    '''
    return isValidKey(key)
# ==================================================================================================


# ==================================================================================================
class SleepKeyboardHandler(BasicKeyboardHandler):
  '''
  Subclass of `BasicKeyboardHandler` that replaces all actual
  input functions with NOPs, effectively leaving only the
  sleep routines. (To keep in sync with remote InputServer instances)
  '''
  _typewrite: ClassVar[Callable[..., None]] = nop
  _keyDown: ClassVar[Callable[..., None | bool]] = nop
  _keyUp: ClassVar[Callable[..., None | bool]] = nop
# ==================================================================================================


# ==================================================================================================
class DelayedKeyboardHandler(BasicKeyboardHandler):
  '''
  Subclass of `BasicKeyboardHandler` that adds an additional delay before
  actions are executed.
  The delay is variable based on global file event state, allowing
  the user to directly control random action delay and tweak its sheer
  input spam capabilities on the fly.
  '''
  @classmethod
  def press_multiple_Keys(
    cls,
    index: int,
    args_list: Sequence[FuncArgsDict]
  ) -> None:
    '''
    Press and release multiple keys after delay set by global file event state.
    '''
    artifical_delay: float = GlobalData.EventStates.delay_random()
    if artifical_delay > 0:
      sleep(artifical_delay * MILLISEC_TO_SEC_MULT)
    super().press_multiple_Keys(index, args_list)
# ==================================================================================================


# ==================================================================================================
class DelayedSleepKeyboardHandler(
  SleepKeyboardHandler,
  DelayedKeyboardHandler
):
  '''
  Combine Delay and Sleep for KeyboardHandler
  '''
  pass
# ==================================================================================================
