'''
Helper functions for the rest of the package.
Internal imports to other parts of the package and 3rd party modules
are not allowed!
'''

# native imports
from typing import Any


def clamp(
  minimum: int | float,
  value: int | float,
  maximum: int | float
) -> float:
  '''
  Limit `value` to be at least `minimum` and at most `maximum`
  '''
  if minimum > maximum:
    minimum, maximum = maximum, minimum
  return max(minimum, min(value, maximum))
# ------------------------------------------------------------------------------


def nop(*args: Any, **kwargs: Any) -> None:
  '''No operation'''
  pass
# ------------------------------------------------------------------------------
