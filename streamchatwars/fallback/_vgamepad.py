'''
Fallback implementation of basic vgamepad data types if vgamepad is not
available (e.g. ViGEm not installed)
'''

# native imports
from ctypes import Structure
from ctypes import c_byte
from ctypes import c_short
from ctypes import c_ushort
from enum import IntFlag
from typing import Any


# ==================================================================================================
class XUSB_BUTTON(IntFlag):
  """
  Possible XUSB report buttons.
  """
  XUSB_GAMEPAD_DPAD_UP = 0x0001
  XUSB_GAMEPAD_DPAD_DOWN = 0x0002
  XUSB_GAMEPAD_DPAD_LEFT = 0x0004
  XUSB_GAMEPAD_DPAD_RIGHT = 0x0008
  XUSB_GAMEPAD_START = 0x0010
  XUSB_GAMEPAD_BACK = 0x0020
  XUSB_GAMEPAD_LEFT_THUMB = 0x0040
  XUSB_GAMEPAD_RIGHT_THUMB = 0x0080
  XUSB_GAMEPAD_LEFT_SHOULDER = 0x0100
  XUSB_GAMEPAD_RIGHT_SHOULDER = 0x0200
  XUSB_GAMEPAD_GUIDE = 0x0400
  XUSB_GAMEPAD_A = 0x1000
  XUSB_GAMEPAD_B = 0x2000
  XUSB_GAMEPAD_X = 0x4000
  XUSB_GAMEPAD_Y = 0x8000
# ==================================================================================================


# ==================================================================================================
class XUSB_REPORT(Structure):
  """
  Represents an XINPUT_GAMEPAD-compatible report structure.
  """
  _fields_ = [
    ("wButtons", c_ushort),
    ("bLeftTrigger", c_byte),
    ("bRightTrigger", c_byte),
    ("sThumbLX", c_short),
    ("sThumbLY", c_short),
    ("sThumbRX", c_short),
    ("sThumbRY", c_short)
  ]
# ==================================================================================================


# ==================================================================================================
class VX360Gamepad:
  '''
  Fallback implementation of vgamepad's VX360Gamepad class signature.
  '''
  # VGamepad methods
  def __del__(self) -> None:
    pass
  # ----------------------------------------------------------------------------

  def get_vid(self) -> Any:
    return None
  # ----------------------------------------------------------------------------

  def get_pid(self) -> Any:
    return None
  # ----------------------------------------------------------------------------

  def set_vid(self, vid: Any) -> Any:
    return None
  # ----------------------------------------------------------------------------

  def set_pid(self, pid: Any) -> Any:
    return None
  # ----------------------------------------------------------------------------

  def get_index(self) -> Any:
    return None
  # ----------------------------------------------------------------------------

  def get_type(self) -> Any:
    return None
  # ----------------------------------------------------------------------------

  # VX360Gamepad methods
  def __init__(self) -> None:
    self.report = self.get_default_report()
    self.update()
  # ----------------------------------------------------------------------------

  def get_default_report(self) -> XUSB_REPORT:
    return XUSB_REPORT(
      wButtons=0,
      bLeftTrigger=0,
      bRightTrigger=0,
      sThumbLX=0,
      sThumbLY=0,
      sThumbRX=0,
      sThumbRY=0
    )
  # ----------------------------------------------------------------------------

  def reset(self) -> None:
    self.report = self.get_default_report()
  # ----------------------------------------------------------------------------

  def press_button(self, button: int) -> None:
    self.report.wButtons = self.report.wButtons | button
  # ----------------------------------------------------------------------------

  def release_button(self, button: int) -> None:
    self.report.wButtons = self.report.wButtons & ~button
  # ----------------------------------------------------------------------------

  def left_trigger(self, value: int) -> None:
    self.report.bLeftTrigger = value
  # ----------------------------------------------------------------------------

  def right_trigger(self, value: int) -> None:
    self.report.bRightTrigger = value
  # ----------------------------------------------------------------------------

  def left_trigger_float(self, value_float: float) -> None:
    self.left_trigger(round(value_float * 255))
  # ----------------------------------------------------------------------------

  def right_trigger_float(self, value_float: float) -> None:
    self.right_trigger(round(value_float * 255))
  # ----------------------------------------------------------------------------

  def left_joystick(self, x_value: int, y_value: int) -> None:
    self.report.sThumbLX = x_value
    self.report.sThumbLY = y_value
  # ----------------------------------------------------------------------------

  def right_joystick(self, x_value: int, y_value: int) -> None:
    self.report.sThumbRX = x_value
    self.report.sThumbRY = y_value
  # ----------------------------------------------------------------------------

  def left_joystick_float(
    self,
    x_value_float: float,
    y_value_float: float
  ) -> None:
    self.left_joystick(
      round(x_value_float * 32767),
      round(y_value_float * 32767)
    )
  # ----------------------------------------------------------------------------

  def right_joystick_float(
    self,
    x_value_float: float,
    y_value_float: float
  ) -> None:
    self.right_joystick(
      round(x_value_float * 32767),
      round(y_value_float * 32767)
    )
  # ----------------------------------------------------------------------------

  def update(self) -> None:
    pass
  # ----------------------------------------------------------------------------

  def register_notification(self, callback_function: Any) -> None:
    pass
  # ----------------------------------------------------------------------------

  def unregister_notification(self) -> None:
    pass
  # ----------------------------------------------------------------------------

  def target_alloc(self) -> Any:
    return None
# ==================================================================================================
