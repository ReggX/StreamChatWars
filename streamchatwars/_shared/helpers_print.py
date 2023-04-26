'''
Helper functions for the rest of the package.
Internal imports to other parts of the package are not allowed!

(Importing CONSOLELOG unfortunately can't be avoided)
'''

# native imports
from datetime import datetime
from datetime import timezone
from io import StringIO
from threading import Lock
from traceback import print_exc
from typing import Any

# internal imports
from ..session.consolelog import CONSOLELOG


__print_lock: Lock = Lock()


def thread_print(*args: Any, **kwargs: Any) -> None:
  '''thread safe print function'''
  with __print_lock:
    with StringIO() as strio:
      mod_kwargs: dict[str, Any] = {**kwargs, 'file': strio}
      print(*args, **mod_kwargs)
      strio.flush()
      CONSOLELOG.log_message(strio.getvalue())
    print(*args, **kwargs)
# ------------------------------------------------------------------------------


def thread_print_timestamped(*args: Any, **kwargs: Any) -> None:
  '''thread safe print function starting with UTC timestamp'''
  with __print_lock:
    mod_args: tuple[Any, ...] = (
      f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC]",
      *args,
    )
    with StringIO() as strio:
      mod_kwargs: dict[str, Any] = {**kwargs, 'file': strio}
      print(
        *mod_args,
        **mod_kwargs
      )
      strio.flush()
      CONSOLELOG.log_message(strio.getvalue())
    print(*mod_args, **kwargs)
# ------------------------------------------------------------------------------


def thread_print_exc(*args: Any, **kwargs: Any) -> None:
  '''thread safe print_exc function'''
  with __print_lock:
    with StringIO() as strio:
      mod_kwargs: dict[str, Any] = {**kwargs, 'file': strio}
      print_exc(*args, **mod_kwargs)
      strio.flush()
      CONSOLELOG.log_message(strio.getvalue())
    print_exc(*args, **kwargs)
# ------------------------------------------------------------------------------
