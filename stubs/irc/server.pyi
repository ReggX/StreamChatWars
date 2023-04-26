import socketserver
import typing
from . import events as events
from typing import Any

log: Any

class IRCError(Exception):
    code: Any
    value: Any
    def __init__(self, code, value) -> None: ...
    @classmethod
    def from_name(cls, name, value): ...

class IRCChannel:
    name: Any
    topic_by: str
    topic: Any
    clients: Any
    def __init__(self, name, topic: str = ...) -> None: ...

class IRCClient(socketserver.BaseRequestHandler):
    class Disconnect(BaseException): ...
    user: Any
    host: Any
    realname: Any
    nick: Any
    send_queue: Any
    channels: Any
    def __init__(self, request, client_address, server) -> None: ...
    buffer: Any
    def handle(self) -> None: ...
    def handle_nick(self, params): ...
    mode: Any
    def handle_user(self, params): ...
    def handle_ping(self, params): ...
    def handle_join(self, params) -> None: ...
    def handle_privmsg(self, params) -> None: ...
    def handle_topic(self, params): ...
    def handle_part(self, params) -> None: ...
    def handle_quit(self, params) -> None: ...
    def handle_dump(self, params) -> None: ...
    def handle_ison(self, params): ...
    def client_ident(self): ...
    def finish(self) -> None: ...

class IRCServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads: bool
    allow_reuse_address: bool
    channels: typing.Dict[str, IRCChannel]
    clients: typing.Dict[str, IRCClient]
    servername: str
    def __init__(self, *args, **kwargs) -> None: ...

def get_args(): ...
def main() -> None: ...
