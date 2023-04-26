'''
This module is responsible for executing InputHandler functions, either locally
on the same system or remotely on another system running a compatible server
application (in which case this local server acts as a proxy client to the
remote real server).

Actionset (client) -> LocalInputServer (server)

Actionset (client) -> RemoteInputServer (proxy) ->
StreamChatWars.InputServer running remotely (server)
'''

# native imports
import json
import pickle  # nosec B403
import socket
from base64 import b64encode
from functools import partial
from time import sleep
from typing import ClassVar
from typing import Final

# pip imports
from Cryptodome.Cipher import AES
from Cryptodome.Cipher._mode_gcm import GcmMode
from Cryptodome.Hash import SHA3_256

# internal imports
from .._interfaces._input_server import AbstractInputServer
from .._interfaces._input_server import InputServerConnectionFailed
from .._shared.constants import BACKOFF_FACTOR
from .._shared.constants import SOCKET_TIMEOUT
from .._shared.global_data import GlobalData
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from .._shared.helpers_print import thread_print_exc
from .._shared.types import INPUT_DATA_PACK_TYPE
from .._shared.types import InputServerDataPack
from .gamepads import NOP_Gamepad
from .gamepads import XInput_Gamepad
from .input_handler import BasicGamepadHandler
from .input_handler import BasicKeyboardHandler
from .input_handler import DelayedGamepadHandler
from .input_handler import DelayedKeyboardHandler
from .input_handler import DelayedSleepGamepadHandler
from .input_handler import DelayedSleepKeyboardHandler
from .input_handler import SleepGamepadHandler
from .input_handler import SleepKeyboardHandler


# ------------------------------------------------------------------------------
# not outsourced since this constant mapping is only needed in this one module
# and requires inter-module imports, which are illegal in the constants module.
HANDLER_REPLACEMENT_DICT: Final = {
  BasicKeyboardHandler: SleepKeyboardHandler,
  BasicGamepadHandler: SleepGamepadHandler,
  DelayedKeyboardHandler: DelayedSleepKeyboardHandler,
  DelayedGamepadHandler: DelayedSleepGamepadHandler
}
# ------------------------------------------------------------------------------


# ==================================================================================================
class InputServer(AbstractInputServer):
  '''
  Input execution is done through "server" instances that
  allow delegating commands to either local or remote
  input handling interfaces.

  Base class to define necessary interfaces.
  '''
  type: ClassVar[str] = 'base'
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    host: str = '',
    port: int = 0,
    encryption_key: str = '',
    encryption_mode: str = ''
  ) -> None:
    '''
    useless constructor arguments to stay in sync with subclasses
    '''
    pass
  # ----------------------------------------------------------------------------

  def execute(self, partial_function: partial[None]) -> None:
    '''
    Execute the function contained in `funcargs`
    '''
    raise NotImplementedError
  # ----------------------------------------------------------------------------

  @classmethod
  def add_gamepad(cls, player_index: int) -> None:
    '''
    Add virtual gamepad to this Input Server instance
    '''
    raise NotImplementedError
  # ----------------------------------------------------------------------------

  @classmethod
  def remove_gamepad(cls, player_index: int) -> None:
    '''
    Release and remove virtual gamepad from this Input Server instance
    '''
    GlobalData.Gamepads.remove(player_index)
# ==================================================================================================


# ==================================================================================================
class LocalInputServer(InputServer):
  '''
  Local implementation of the InputServer concept.

  Handles local virtual gamepads and executes
  partial function instances locally.
  '''
  type: ClassVar[str] = 'local'
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    host: str = '',
    port: int = 0,
    encryption_key: str = '',
    encryption_mode: str = ''
  ) -> None:
    '''
    useless constructor arguments to stay in sync with subclasses
    '''
    pass
  # ----------------------------------------------------------------------------

  def execute(self, partial_function: partial[None]) -> None:
    '''
    Execute the function contained in `funcargs`
    '''
    partial_function()
  # ----------------------------------------------------------------------------

  @classmethod
  def add_gamepad(cls, player_index: int) -> None:
    '''
    Create and add virtual gamepad to this Input Server instance
    '''
    GlobalData.Gamepads.add(player_index, XInput_Gamepad())
# ==================================================================================================


# ==================================================================================================
class RemoteInputServer(InputServer):
  '''
  Remote implementation of the InputServer concept.

  Connects to a remote server for input handling, and adds
  NOP_Gamepads to mirror the remote gamepad instance if necessary.
  '''
  # Class variables:
  type: ClassVar[str] = 'remote'
  # Instance variables:
  key: bytes
  encryption_mode: str
  remote_address: tuple[str, int]
  sock: socket.socket
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    host: str,
    port: int,
    encryption_key: str = '',
    encryption_mode: str = 'AES-GCM'
  ) -> None:
    '''
    Connect to remote server at `host`:`port`.
    '''
    self.key = b''
    self.encryption_mode = ''
    if encryption_key:
      self.key = SHA3_256.new(encryption_key.encode('utf-8')).digest()
      self.encryption_mode = encryption_mode
    self.remote_address = (host, int(port))
    self.create_socket()
  # ----------------------------------------------------------------------------

  def create_socket(self) -> None:
    '''
    Create socket and connect to remote server.
    '''
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    self.sock.settimeout(SOCKET_TIMEOUT)
    try:
      thread_print(
        "Attempting connection to remote input server at "
        f"{self.remote_address[0]}:{self.remote_address[1]}...",
      )
      self.sock.connect(self.remote_address)
    except (TimeoutError, ConnectionRefusedError) as e:
      raise InputServerConnectionFailed(
        "Failed to connect to remote input server at "
        f"{self.remote_address[0]}:{self.remote_address[1]}!"
      ) from e
    thread_print(ColorText.good(
      f"Established {'encrypted' if self.key else 'plaintext'} connection to "
      f"remote input server {self.remote_address[0]}:{self.remote_address[1]}"
    ))
  # ----------------------------------------------------------------------------

  def pack_data(self, pickled_data: bytes) -> bytes:
    '''
    Pack pickled_data into a encoded json string,
    with encryption if `encryption_key` was specified.
    '''
    data_pack: InputServerDataPack
    PACK_TYPE: Final[INPUT_DATA_PACK_TYPE] = 'input'
    if self.key:
      if self.encryption_mode == 'AES-GCM':
        # need explicit cast here since Cryptodome's AES factory function does
        # not handle type hinting very well.
        cipher: GcmMode = AES.new(  # pyright: ignore[reportUnknownMemberType]
          key=self.key,
          mode=AES.MODE_GCM
        )
        cipher.update(PACK_TYPE.encode('utf-8'))  # make sure type gets verified
        ciphertext, auth_tag = cipher.encrypt_and_digest(pickled_data)
        data_pack = {
          "type": PACK_TYPE,
          "encryption": 'AES-GCM',
          "data": b64encode(ciphertext).decode('utf-8'),
          "auth_tag": b64encode(auth_tag).decode('utf-8'),
          "nonce": b64encode(cipher.nonce).decode('utf-8')
        }
      else:
        raise ValueError(f'Unknown encryption mode: {self.encryption_mode}')
    else:
      data_pack = {
        "type": PACK_TYPE,
        "encryption": None,
        "data": b64encode(pickled_data).decode('utf-8')
      }
    json_string: str = json.dumps(data_pack)
    return json_string.encode('utf-8')
  # ----------------------------------------------------------------------------

  def send_data(
    self,
    data: bytes,
  ) -> None:
    '''
    Send `data` to the connected remote server.
    '''
    data_length: bytes = len(data).to_bytes(4, 'big')
    data_pack: bytes = data_length + data
    while True:
      try:
        self.sock.sendall(data_pack)
        break

      except (ConnectionResetError, ConnectionAbortedError) as e:
        cause: str = (
          "reset" if isinstance(e, ConnectionResetError) else "aborted"
        )
        thread_print(ColorText.warning(
          "Remote connection to "
          f"{self.remote_address[0]}:{self.remote_address[1]} {cause}"
        ))
        self._send_data_reconnect_after_error()
        # Reconnected, retry sending data
        continue

      except TimeoutError:
        # skip this data_pack
        thread_print(ColorText.warning(
          "Socket.Send Timeout: sending to remote address: "
          f"{self.remote_address[0]}:{self.remote_address[1]}"
        ))

      except OSError as e:
        if 10048 == e.winerror:
          thread_print(ColorText.warning(
            "WINERROR 10048, remote address: "
            f"{self.remote_address[0]}:{self.remote_address[1]}"
          ))
        else:
          thread_print(ColorText.error(
            f"remote address: {self.remote_address[0]}:{self.remote_address[1]}"
          ))
          raise

      # break after not triggering exception
      break
  # ----------------------------------------------------------------------------

  def _send_data_reconnect_after_error(self) -> None:
    backoff: float = 1.0
    while True:
      thread_print(ColorText.warning(
        f"Retrying connection to "
        f"{self.remote_address[0]}:{self.remote_address[1]} "
        f"in {backoff:.4} seconds"
      ))
      sleep(backoff)
      backoff *= BACKOFF_FACTOR
      try:
        self.create_socket()
        break  # break inner loop
      except InputServerConnectionFailed:
        # Reconnect failed, try again
        continue  # continue inner loop
  # ----------------------------------------------------------------------------

  def execute(self, partial_function: partial[None]) -> None:
    '''
    Pickle and send `partial_function` to remote server and
    execute the sleep-only variant of the given
    partial function locally to stay in sync.
    '''
    # send funcargs to remote server
    func_name: str = partial_function.func.__name__
    if func_name != "sleep":
      data: bytes = self.pack_data(pickle.dumps(partial_function))
      try:
        self.send_data(data)
      except Exception:
        thread_print(ColorText.error(
          "Failed to send data to remote server! Skipping action data..."
        ))
        thread_print_exc()
        return
      # replace partial function with sleep variant
      try:
        function_class = getattr(partial_function.func, '__self__')  # noqa: B009
      except AttributeError:
        # partial_function does not call a class method, so it's not one
        # we need to replace. (like Default_Actionset's print action)
        # Ignore such cases and just move on.
        pass
      else:
        # Make sure local and remote run/sleep for the same amount of time
        # to stay in sync.
        try:
          replacement_class = HANDLER_REPLACEMENT_DICT[function_class]
        except KeyError:
          thread_print(ColorText.error(
            f"No handler defined for function class {function_class}"
          ))
        else:
          partial_function = partial(
            getattr(replacement_class, func_name),
            *partial_function.args,
            **partial_function.keywords
          )
    partial_function()  # Execute sleep locally
  # ----------------------------------------------------------------------------

  @classmethod
  def add_gamepad(cls, player_index: int) -> None:
    '''
    Add a NOP_Gamepad to mirror the remote gamepad instance
    '''
    GlobalData.Gamepads.add(player_index, NOP_Gamepad())
# ==================================================================================================
