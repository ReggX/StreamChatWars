from . import fromUtf8 as fromUtf8, toUtf8 as toUtf8
from ..voice import Voice as Voice
from _typeshed import Incomplete
from collections.abc import Generator

engine: Incomplete
stream: Incomplete
MSSAM: str
MSMARY: str
MSMIKE: str
E_REG: Incomplete

def buildDriver(proxy): ...

class SAPI5Driver:
    def __init__(self, proxy) -> None: ...
    def destroy(self) -> None: ...
    def say(self, text) -> None: ...
    def stop(self) -> None: ...
    def save_to_file(self, text, filename) -> None: ...
    def getProperty(self, name): ...
    def setProperty(self, name, value) -> None: ...
    def startLoop(self) -> None: ...
    def endLoop(self) -> None: ...
    def iterate(self) -> Generator[None, None, None]: ...

class SAPI5DriverEventSink:
    def __init__(self) -> None: ...
    def setDriver(self, driver) -> None: ...
