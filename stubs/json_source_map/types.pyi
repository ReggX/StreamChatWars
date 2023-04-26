import typing
from typing import Any

class TLocationDict(typing.TypedDict):
    line: int
    column: int
    pos: int

class Location:
    line: int
    column: int
    position: int
    def to_dict(self) -> TLocationDict: ...
    def __init__(self, line, column, position) -> None: ...

class TEntryDictBase(typing.TypedDict):
    value: TLocationDict
    valueEnd: TLocationDict

class TEntryDict(TEntryDictBase):
    key: TLocationDict
    keyEnd: TLocationDict

class Entry:
    value_start: Location
    value_end: Location
    key_start: typing.Optional[Location]
    key_end: typing.Optional[Location]
    def to_dict(self) -> TEntryDict: ...
    def __init__(self, value_start: Location, value_end: Location, key_start: Location | None = ..., key_end: Location | None = ...) -> None: ...

TSourceMapEntries: typing.TypeAlias = typing.List[typing.Tuple[str, Entry]]
TSourceMap: typing.TypeAlias = typing.Dict[str, Entry]
