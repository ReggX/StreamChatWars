'''
Fallback implementation of basic pydirectinput_rgx functions, so that
partial imports (like GamepadClient) can skip out on the dependency.
'''


# ----- isValidKey -------------------------------------------------------------
def isValidKey(key: str) -> bool:
  '''
  Not implemented!
  '''
  raise NotImplementedError
# ------------------------------------------------------------------------------


# ----- keyDown ----------------------------------------------------------------
def keyDown(
  key: str,
  logScreenshot: None = None,
  _pause: bool = True,
  *,
  auto_shift: bool = False
) -> bool:
  '''
  Not implemented!
  '''
  raise NotImplementedError
# ------------------------------------------------------------------------------


# ----- keyUp ------------------------------------------------------------------
def keyUp(
  key: str,
  logScreenshot: None = None,
  _pause: bool = True,
  *,
  auto_shift: bool = False
) -> bool:
  '''
  Not implemented!
  '''
  raise NotImplementedError
# ------------------------------------------------------------------------------


# ----- typewrite --------------------------------------------------------------
def typewrite(
  message: str,
  interval: float = 0.0,
  logScreenshot: None = None,
  _pause: bool = True,
  *,
  auto_shift: bool = False,
  delay: float = 0.0,
  duration: float = 0.0
) -> None:
  '''
  Not implemented!
  '''
  raise NotImplementedError
# ------------------------------------------------------------------------------


# ----- typewrite alias --------------------------------------------------------
write = typewrite
# ------------------------------------------------------------------------------
