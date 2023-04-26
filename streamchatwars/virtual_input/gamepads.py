'''
This module is implementing the virtual gamepads that allow controlling games.
Heavily relies on vgamepad and ViGEm to make the actual gamepad emulation work.
'''

# native imports
from ctypes import ArgumentError
from typing import Any

# internal imports
from .._interfaces._gamepads import AbstractGamepad
from .._interfaces._gamepads import AbstractReport
from .._shared.constants import NEG_MAX_INT16
from .._shared.constants import POS_MAX_INT16
from .._shared.constants import POS_MAX_UINT8
from .._shared.constants import XUSB_BUTTON_MAPPING
from .._shared.types import AXIS_GETTER_TYPE
from .._shared.types import AXIS_MAP_TYPE
from .._shared.types import AXIS_SETTER_TYPE
from .._shared.types import AXIS_TUPLE_TYPE


# ------------------------------------------------------------------------------
# Try importing vgamepad's XUSB_REPORT struct and VX360Gamepad class if
# available, falling back to a local copy if it fails. (vgamepad tries to load
# ViGEm on import, so import will fail on all systems without ViGEm)
_real_vgamepad_imported_: bool
try:
  # pip imports
  from vgamepad import VX360Gamepad
  from vgamepad.win.vigem_commons import XUSB_REPORT
  _real_vgamepad_imported_ = True
except Exception:
  # internal imports
  from ..fallback._vgamepad import XUSB_REPORT  # type: ignore[assignment]
  from ..fallback._vgamepad import VX360Gamepad  # type: ignore[assignment]
  _real_vgamepad_imported_ = False
# ------------------------------------------------------------------------------


# ==================================================================================================
class XInput_REPORT(
  XUSB_REPORT,  # pyright: ignore[reportUntypedBaseClass,reportGeneralTypeIssues]
  AbstractReport
):
  '''
  Modified XUSB_REPORT from vgamepad for better type hinting support.
  '''

  def __init__(
    self,
    *args: Any,
    wButtons: int = 0,
    bLeftTrigger: int = 0,
    bRightTrigger: int = 0,
    sThumbLX: int = 0,
    sThumbLY: int = 0,
    sThumbRX: int = 0,
    sThumbRY: int = 0,
    **kw: Any
  ) -> None:
    '''
    Create a modified XUSB_REPORT with type hinting support.
    '''
    super().__init__(  # pyright: ignore[reportUnknownMemberType]
      *args,
      wButtons=wButtons,
      bLeftTrigger=bLeftTrigger,
      bRightTrigger=bRightTrigger,
      sThumbLX=sThumbLX,
      sThumbLY=sThumbLY,
      sThumbRX=sThumbRX,
      sThumbRY=sThumbRY,
      **kw
    )

  def __repr__(self) -> str:
    return (
      f'{self.__class__.__name__}('  # pyright: ignore[reportUnknownMemberType]
      f'{self.wButtons=}, '
      f'{self.bLeftTrigger=}, '
      f'{self.bRightTrigger=}, '
      f'{self.sThumbLX=}, '
      f'{self.sThumbLY=}, '
      f'{self.sThumbRX=}, '
      f'{self.sThumbRY=}'
      ')'
    )
# ==================================================================================================


# ==================================================================================================
class XInput_Gamepad(
  VX360Gamepad,  # pyright: ignore[reportUntypedBaseClass,reportGeneralTypeIssues]
  AbstractGamepad
):
  '''
  Virtual XInput Gamepad with the help of ViGEm

  The actual gamepad virtualization is handled by the super class
  (VX360Gamepad from vgamepad).

  Rather, this class acts as an interface with methods that accept
  string values instead of hardcoded enums.
  '''
  # Instance variables:
  report: AbstractReport
  axis_mapping: AXIS_MAP_TYPE
  # ----------------------------------------------------------------------------

  def __init__(self) -> None:
    if not _real_vgamepad_imported_:
      raise RuntimeError(
        "vgamepad package hasn't been imported properly! "
        "Using Gamepads requires vgamepad and ViGEm!"
      )
    self.report = self.get_default_report()
    self.init_mappings()
    super().__init__()  # pyright: ignore[reportUnknownMemberType]
  # ----------------------------------------------------------------------------

  def __del__(self) -> None:
    super().__del__()  # pyright: ignore[reportUnknownMemberType]
  # ----------------------------------------------------------------------------

  def update(self) -> None:
    super().update()  # pyright: ignore[reportUnknownMemberType]
  # ----------------------------------------------------------------------------

  def get_default_report(self) -> AbstractReport:
    return XInput_REPORT(
      wButtons=0,
      bLeftTrigger=0,
      bRightTrigger=0,
      sThumbLX=0,
      sThumbLY=0,
      sThumbRX=0,
      sThumbRY=0
    )
  # ----------------------------------------------------------------------------

  def init_mappings(self) -> None:
    '''
    create mapping dictionaries to translate string values to
    the XInput enums.
    '''
    # While button mappings can stay independent outside the class definition,
    # axis mappings are specific to the object instance, since treating every
    # axis as a pseudo button requires more knowledge about the axis'
    # bound functions and current values at runtime.
    self.axis_mapping = {
      # axis_name, (setter function,     max_value,       getter function)
      'rt':       (self.right_trigger, POS_MAX_UINT8, lambda: self.report.bRightTrigger),
      'lt':       (self.left_trigger,  POS_MAX_UINT8, lambda: self.report.bLeftTrigger),
      'ls_right': (self.left_stick_x,  POS_MAX_INT16, lambda: self.report.sThumbLX),
      'ls_left':  (self.left_stick_x,  NEG_MAX_INT16, lambda: self.report.sThumbLX),
      'ls_up':    (self.left_stick_y,  POS_MAX_INT16, lambda: self.report.sThumbLY),
      'ls_down':  (self.left_stick_y,  NEG_MAX_INT16, lambda: self.report.sThumbLY),
      'rs_right': (self.right_stick_x, POS_MAX_INT16, lambda: self.report.sThumbRX),
      'rs_left':  (self.right_stick_x, NEG_MAX_INT16, lambda: self.report.sThumbRX),
      'rs_up':    (self.right_stick_y, POS_MAX_INT16, lambda: self.report.sThumbRY),
      'rs_down':  (self.right_stick_y, NEG_MAX_INT16, lambda: self.report.sThumbRY),
    }
  # ----------------------------------------------------------------------------

  def press_str_button(self, button: str) -> None:
    '''
    Wrapper for VX360Gamepad.press_button

    Accept string input and automatically update.
    '''
    internal_button = XUSB_BUTTON_MAPPING.get(button)
    if internal_button is None:
      raise ArgumentError
    super().press_button(internal_button)  # pyright: ignore[reportUnknownMemberType]
    self.update()
  # ----------------------------------------------------------------------------

  def release_str_button(self, button: str) -> None:
    '''
    Wrapper for VX360Gamepad.release_button

    Accept string input and automatically update.
    '''
    internal_button = XUSB_BUTTON_MAPPING.get(button)
    if internal_button is None:
      raise ArgumentError
    super().release_button(internal_button)  # pyright: ignore[reportUnknownMemberType]
    self.update()
  # ----------------------------------------------------------------------------

  def left_trigger(self, value: int) -> None:
    """
    Sets the value of the left trigger

    :param: integer between 0 and 255 (0 = trigger released)
    """
    super().left_trigger(value)  # pyright: ignore[reportUnknownMemberType]

  def right_trigger(self, value: int) -> None:
    """
    Sets the value of the right trigger

    :param: integer between 0 and 255 (0 = trigger released)
    """
    super().right_trigger(value)  # pyright: ignore[reportUnknownMemberType]

  def left_stick_x(self, value: int) -> None:
    '''Change the horizontal axis of Left Stick only.'''
    self.left_joystick(  # pyright: ignore[reportUnknownMemberType]
      x_value=value,
      y_value=self.report.sThumbLY
    )
  # ----------------------------------------------------------------------------

  def left_stick_y(self, value: int) -> None:
    '''Change the vertical axis of Left Stick only.'''
    self.left_joystick(  # pyright: ignore[reportUnknownMemberType]
      x_value=self.report.sThumbLX,
      y_value=value
    )
  # ----------------------------------------------------------------------------

  def right_stick_x(self, value: int) -> None:
    '''Change the horizontal axis of Right Stick only.'''
    self.right_joystick(  # pyright: ignore[reportUnknownMemberType]
      x_value=value,
      y_value=self.report.sThumbRY
    )
  # ----------------------------------------------------------------------------

  def right_stick_y(self, value: int) -> None:
    '''Change the vertical axis of Right Stick only.'''
    self.right_joystick(  # pyright: ignore[reportUnknownMemberType]
      x_value=self.report.sThumbLX,
      y_value=value
    )
  # ----------------------------------------------------------------------------

  def press_axis(self, axis: str) -> None:
    '''
    "Press" an axis like it's a button (instantly jump to max value)

    Accept string input and automatically update.
    '''
    axis_tuple: AXIS_TUPLE_TYPE | None = self.axis_mapping.get(axis)
    if axis_tuple is None:
      raise ArgumentError
    setter_func: AXIS_SETTER_TYPE = axis_tuple[0]
    max_value: int = axis_tuple[1]
    setter_func(max_value)
    self.update()
  # ----------------------------------------------------------------------------

  def release_axis(self, axis: str) -> None:
    '''
    "Release" an axis like it's a button (instantly jump to 0)

    Only releases the axis if it hasn't been changed since "pressing" it,
    e.g. `press right, press left, release right, release left` would not
    change the axis on the first release function, since it sees that
    the current axis value is not fully right anymore and already considers
    it released.

    Accept string input and automatically update.
    '''
    axis_tuple: AXIS_TUPLE_TYPE | None = self.axis_mapping.get(axis)
    if axis_tuple is None:
      raise ArgumentError
    setter_func: AXIS_SETTER_TYPE = axis_tuple[0]
    max_value: int = axis_tuple[1]
    getter_func: AXIS_GETTER_TYPE = axis_tuple[2]
    current_value: int = getter_func()
    if current_value == max_value:  # only release when the axis didn't change
      setter_func(0)  # axis position == 0 --> axis released
      self.update()
  # ----------------------------------------------------------------------------

  def press_pseudo_key(self, pseudo_key: str) -> None:
    '''
    Combine both "button keys" and "axis keys" and delegate
    to the correct handling function automatically.

    Raise ArgumentError if the given argument is not a support
    "key" value.
    '''
    if pseudo_key in XUSB_BUTTON_MAPPING:
      self.press_str_button(pseudo_key)
    elif pseudo_key in self.axis_mapping:
      self.press_axis(pseudo_key)
    else:
      raise ArgumentError(f"{pseudo_key} is not a supported key")
  # ----------------------------------------------------------------------------

  def release_pseudo_key(self, pseudo_key: str) -> None:
    '''
    Combine both "button keys" and "axis keys" and delegate
    to the correct handling function automatically.

    Raise ArgumentError if the given argument is not a support
    "key" value.
    '''
    if pseudo_key in XUSB_BUTTON_MAPPING:
      self.release_str_button(pseudo_key)
    elif pseudo_key in self.axis_mapping:
      self.release_axis(pseudo_key)
    else:
      raise ArgumentError(f"{pseudo_key} is not a supported key")
# ==================================================================================================


# ==================================================================================================
class NOP_Gamepad(XInput_Gamepad):
  '''
  Subclass of XInput_Gamepad that doesn't communicate with
  the ViGEm virtual gamepad instance, thereby effectively doing
  nothing when called.
  '''
  def __init__(self) -> None:
    '''
    Create a "fake" virtual gamepad that doesn't bind any
    virtual gamepad driver ressources and effectively does nothing.
    '''
    self.report = self.get_default_report()
    self.init_mappings()
  # ----------------------------------------------------------------------------

  def __del__(self, *args: Any, **kwargs: Any) -> None:
    '''
    Don't try to release virtual gamepad driver ressources that don't exist.
    '''
    pass
  # ----------------------------------------------------------------------------

  def update(self) -> None:
    '''
    Don't try to update virtual gamepad driver ressources that don't exist.
    '''
    pass
# ==================================================================================================
