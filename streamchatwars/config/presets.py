'''
This module contains lookups for Teams/Actionsets/InputServers

Outsourced from config to reduce the number of imports there
and keep it independent from subclass additions/changes/removals.
'''

# native imports
import sys
from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType
from typing import Final
from typing import TypeVar

# internal imports
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from ..actionsets.actionset import Actionset
from ..teams.team import Team
from ..virtual_input.input_server import InputServer
from ..virtual_input.input_server import LocalInputServer
from ..virtual_input.input_server import RemoteInputServer


def import_submodules_as_dict(package_name: str) -> dict[str, ModuleType]:
  '''
  Import all submodules in `package_name` (not recursive)
  and return them in dict{name: module}.
  '''
  package: ModuleType = sys.modules[package_name]
  return {
    module_name: import_module(f"{package_name}.{module_name}")
    for _, module_name, _ in iter_modules(package.__path__)
  }
# ------------------------------------------------------------------------------


BaseClass = TypeVar("BaseClass")


def create_class_dict(
  package_name: str,
  super_class: type[BaseClass]
) -> dict[str, type[BaseClass]]:
  '''
  Import all submodules of package `package_name` and create a
  dict{class_name: class} based on the contents of their
  `_EXPORT_CLASSES_` attributes
  '''
  class_dict: dict[str, type[BaseClass]] = {}
  submodule_dict: dict[str, ModuleType] = import_submodules_as_dict(package_name)
  for module in submodule_dict.values():
    class_list: list[type[BaseClass]] | None = getattr(
      module,
      '_EXPORT_CLASSES_',
      None
    )
    if class_list is None:
      thread_print(ColorText.warning(
        f'WARNING: Imported module "{module.__name__}", but no '
        '_EXPORT_CLASSES_ attribute was found!'
      ))
      continue
    for cls in class_list:
      if not issubclass(cls, super_class):
        raise TypeError(
          f'Expected subclass of {super_class.__name__}, '
          f'got {cls.__name__} instead!'
        )
    class_dict.update({cls.__name__: cls for cls in class_list})
  # sort before return to fix key order regardless of import order
  return dict(sorted(class_dict.items()))
# ------------------------------------------------------------------------------


def create_TEAMS_DICT() -> dict[str, type[Team]]:
  '''
  Create a class dict based on the submodules of .teams
  '''
  from ..teams.subclasses import __name__ as package_name  # isort: skip
  return create_class_dict(package_name, Team)
# ------------------------------------------------------------------------------


def create_ACTIONSET_DICT() -> dict[str, type[Actionset]]:
  '''
  Create a class dict based on the submodules of .actionsets
  '''
  from ..actionsets.subclasses import __name__ as package_name  # isort: skip
  return create_class_dict(package_name, Actionset)
# ------------------------------------------------------------------------------


# Non-outsourced constants, since the sole purpose of this module is the
# creation and initialization of these quasi-constants.
TEAMS_DICT: Final[dict[str, type[Team]]] = create_TEAMS_DICT()

ACTIONSETS_DICT: Final[dict[str, type[Actionset]]] = create_ACTIONSET_DICT()

INPUTSERVER_DICT: Final[dict[str, type[InputServer]]] = {
  'local': LocalInputServer,
  'remote': RemoteInputServer,
}
