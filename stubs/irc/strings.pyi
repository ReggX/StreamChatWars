from jaraco.text import FoldedCase
from typing import Any

class IRCFoldedCase(FoldedCase):
    translation: Any
    def lower(self): ...

def lower(str): ...
