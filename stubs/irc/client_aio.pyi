import asyncio
from . import connection as connection
from .client import Event as Event, Reactor as Reactor, ServerConnection as ServerConnection, ServerNotConnectedError as ServerNotConnectedError, SimpleIRCClient as SimpleIRCClient
from typing import Any

log: Any

class IrcProtocol(asyncio.Protocol):
    connection: Any
    loop: Any
    def __init__(self, connection, loop) -> None: ...
    def data_received(self, data) -> None: ...
    def connection_lost(self, exc) -> None: ...

class AioConnection(ServerConnection):
    protocol_class: Any
    buffer: Any
    handlers: Any
    real_server_name: str
    real_nickname: Any
    server: Any
    port: Any
    server_address: Any
    nickname: Any
    username: Any
    ircname: Any
    password: Any
    connect_factory: Any
    transport: Any
    protocol: Any
    connected: bool
    async def connect(self, server, port, nickname, password: Any | None = ..., username: Any | None = ..., ircname: Any | None = ..., connect_factory=...): ...
    def process_data(self, new_data) -> None: ...
    def send_raw(self, string) -> None: ...
    def disconnect(self, message: str = ...) -> None: ...

class AioReactor(Reactor):
    connection_class: Any
    connections: Any
    handlers: Any
    mutex: Any
    loop: Any
    def __init__(self, on_connect=..., on_disconnect=..., loop: Any | None = ...) -> None: ...
    def process_forever(self) -> None: ...

class AioSimpleIRCClient(SimpleIRCClient):
    reactor_class: Any
    def connect(self, *args, **kwargs) -> None: ...
