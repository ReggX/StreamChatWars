'''
This module containts enums that used in multiple other modules inside this
package.
'''

# native imports
from enum import IntFlag


_FALSE = 0b00
_TRUE = 0b01
_MAYBE = 0b10


class Quadstate(IntFlag):
  AbsolutelyTrue = _TRUE
  MaybeTrue = _TRUE | _MAYBE
  AbsolutelyFalse = _FALSE
  MaybeFalse = _FALSE | _MAYBE

  def __bool__(self) -> bool:
    return bool(self.value & _TRUE)

  def is_certain(self) -> bool:
    return not self.value & _MAYBE
