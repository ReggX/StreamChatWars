'''
This module contains primitive types that can be used
in constants and types modules.
'''


# native imports
from typing import Annotated
from typing import TypeAlias


seconds: TypeAlias = Annotated[float, "floating point value representing seconds"]
'''floating point value representing seconds'''

millisecs: TypeAlias = Annotated[int, "integer value representing milliseconds"]
'''integer value representing milliseconds'''
