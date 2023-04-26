from . import strings as strings
from jaraco.collections import KeyTransformingDict
from collections.abc import KeysView

class IRCDict(KeyTransformingDict):
    @staticmethod
    def transform_key(key): ...
    def keys(self) -> KeysView[str]: ...
