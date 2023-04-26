import abc
from . import connection as connection, ctcp as ctcp, events as events, features as features, message as message, schedule as schedule
from collections.abc import Generator
from typing import Any, Callable, TypedDict

log: Any

class IRCError(Exception): ...
class InvalidCharacters(ValueError): ...
class MessageTooLong(ValueError): ...

class Connection(metaclass=abc.ABCMeta):
    transmit_encoding: str
    @property
    @abc.abstractmethod
    def socket(self): ...
    reactor: Any
    def __init__(self, reactor) -> None: ...
    def encode(self, msg): ...

class ServerConnectionError(IRCError): ...
class ServerNotConnectedError(ServerConnectionError): ...

class ServerConnection(Connection):
    buffer_class: Any
    socket: Any
    connected: bool
    features: Any
    def __init__(self, reactor) -> None: ...
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
    def connect(self, server, port, nickname, password: Any | None = ..., username: Any | None = ..., ircname: Any | None = ..., connect_factory=...): ...
    def reconnect(self) -> None: ...
    def close(self) -> None: ...
    def get_server_name(self): ...
    def get_nickname(self): ...
    def as_nick(self, name) -> Generator[Any, None, None]: ...
    def process_data(self) -> None: ...
    def is_connected(self): ...
    def add_global_handler(self, *args) -> None: ...
    def remove_global_handler(self, *args) -> None: ...
    def action(self, target, action) -> None: ...
    def admin(self, server: str = ...) -> None: ...
    def cap(self, subcommand: str, *args: str) -> None: ...
    def ctcp(self, ctcptype, target, parameter: str = ...) -> None: ...
    def ctcp_reply(self, target, parameter) -> None: ...
    def disconnect(self, message: str = ...) -> None: ...
    def globops(self, text) -> None: ...
    def info(self, server: str = ...) -> None: ...
    def invite(self, nick, channel) -> None: ...
    def ison(self, nicks) -> None: ...
    def join(self, channel: str, key: str = ...) -> None: ...
    def kick(self, channel, nick, comment: str = ...) -> None: ...
    def links(self, remote_server: str = ..., server_mask: str = ...) -> None: ...
    def list(self, channels: Any | None = ..., server: str = ...) -> None: ...
    def lusers(self, server: str = ...) -> None: ...
    def mode(self, target, command) -> None: ...
    def motd(self, server: str = ...) -> None: ...
    def names(self, channels: Any | None = ...) -> None: ...
    def nick(self, newnick) -> None: ...
    def notice(self, target, text) -> None: ...
    def oper(self, nick, password) -> None: ...
    def part(self, channels, message: str = ...) -> None: ...
    def pass_(self, password) -> None: ...
    def ping(self, target, target2: str = ...) -> None: ...
    def pong(self, target, target2: str = ...) -> None: ...
    def privmsg(self, target: str, text: str) -> None: ...
    def privmsg_many(self, targets, text): ...
    def quit(self, message: str = ...) -> None: ...
    def send_items(self, *items) -> None: ...
    def send_raw(self, string) -> None: ...
    def squit(self, server, comment: str = ...) -> None: ...
    def stats(self, statstype, server: str = ...) -> None: ...
    def time(self, server: str = ...) -> None: ...
    def topic(self, channel, new_topic: Any | None = ...) -> None: ...
    def trace(self, target: str = ...) -> None: ...
    def user(self, username, realname) -> None: ...
    def userhost(self, nicks) -> None: ...
    def users(self, server: str = ...) -> None: ...
    def version(self, server: str = ...) -> None: ...
    def wallops(self, text) -> None: ...
    def who(self, target: str = ..., op: str = ...) -> None: ...
    def whois(self, targets) -> None: ...
    def whowas(self, nick, max: str = ..., server: str = ...) -> None: ...
    def set_rate_limit(self, frequency) -> None: ...
    def set_keepalive(self, interval) -> None: ...

class PrioritizedHandler:
    def __lt__(self, other): ...

class Reactor:
    scheduler_class: Any
    connection_class: Any
    scheduler: Any
    connections: Any
    handlers: Any
    mutex: Any
    def __init__(self, on_connect: Callable[[], None] = ..., on_disconnect: Callable[[], None] = ...) -> None: ...
    def server(self): ...
    def process_data(self, sockets) -> None: ...
    def process_timeout(self) -> None: ...
    @property
    def sockets(self): ...
    def process_once(self, timeout: float = ...) -> None: ...
    def process_forever(self, timeout: float = ...) -> None: ...
    def disconnect_all(self, message: str = ...) -> None: ...
    def add_global_handler(self, event, handler, priority: int = ...) -> None: ...
    def remove_global_handler(self, event, handler): ...
    def dcc(self, dcctype: str = ...): ...

class DCCConnectionError(IRCError): ...

class DCCConnection(Connection):
    socket: Any
    connected: bool
    passive: bool
    peeraddress: Any
    peerport: Any
    dcctype: Any
    def __init__(self, reactor, dcctype) -> None: ...
    buffer: Any
    handlers: Any
    def connect(self, address, port): ...
    def listen(self, addr: Any | None = ...): ...
    def disconnect(self, message: str = ...) -> None: ...
    def process_data(self) -> None: ...
    def privmsg(self, text): ...
    def send_bytes(self, bytes) -> None: ...

class SimpleIRCClient:
    reactor_class: Any
    reactor: Any
    connection: ServerConnection
    dcc_connections: Any
    def __init__(self) -> None: ...
    def connect(self, *args, **kwargs) -> None: ...
    def dcc(self, *args, **kwargs): ...
    def dcc_connect(self, address, port, dcctype: str = ...): ...
    def dcc_listen(self, dcctype: str = ...): ...
    def start(self) -> None: ...

class TagDict(TypedDict):
    key: str
    value: str

class Event:
    type: Any
    source: str
    target: str
    arguments: list[str]
    tags: list[TagDict]
    def __init__(self, type, source, target, arguments: Any | None = ..., tags: Any | None = ...) -> None: ...

def is_channel(string): ...
def ip_numstr_to_quad(num): ...
def ip_quad_to_numstr(quad): ...

class NickMask(str):
    @classmethod
    def from_params(cls, nick, user, host): ...
    @property
    def nick(self): ...
    @property
    def userhost(self): ...
    @property
    def host(self): ...
    @property
    def user(self): ...
    @classmethod
    def from_group(cls, group): ...
