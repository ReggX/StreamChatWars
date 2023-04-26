from typing import Any

def identity(x): ...

class Factory:
    family: Any
    bind_address: Any
    wrapper: Any
    def __init__(self, bind_address: Any | None = ..., wrapper=..., ipv6: bool = ...) -> None: ...
    def connect(self, server_address): ...
    __call__: Any

class AioFactory:
    connection_args: Any
    def __init__(self, **kwargs) -> None: ...
    def connect(self, protocol_instance, server_address): ...
    __call__: Any
