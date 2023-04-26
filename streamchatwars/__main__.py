'''
streamchatwars package entry point
'''


# ------------------------------------------------------------------------------
required_packages: list[tuple[str, str]] = [
  ('colorama', 'colorama'),
  ('irc', 'irc'),
  ('json-source-map', 'json_source_map'),
  ('jsonschema', 'jsonschema'),
  ('keyboard', 'keyboard'),
  ('pycryptodomex', 'Cryptodome'),
  ('pydirectinput-rgx', 'pydirectinput'),
  ('pygame', 'pygame'),
  ('pyttsx3', 'pyttsx3'),
  ('twitchAPI', 'twitchAPI'),
  ('vgamepad', 'vgamepad'),
]
'''Format: [(pypi_name, package_name), ...]'''
# ------------------------------------------------------------------------------


def check_pip_packages() -> None:
  '''
  This function is only supposed to called when python is executing the package
  with -m in an unfrozen state, before the rest of the package make any imports!

  It will check the presence of import packages and will alert to user on how
  to take steps to remedy the problem.

  You should never see any complaints from this function as long as you just
  installed all core requirements beforehand.
  '''
  # native imports
  import sys
  from importlib.util import find_spec

  for pypi_name, package_name in required_packages:
    if package_name in sys.modules:
      pass
    elif find_spec(package_name) is None:
      raise ImportError(
        f"Missing package '{package_name}'. Use command\n"
        f"pip install {pypi_name}"
      )
# ------------------------------------------------------------------------------


# ===== PACKAGE ENTRY POINT ========================================================================
if __name__ == '__main__':
  check_pip_packages()
  # internal imports
  from .main import main
  main()
# ==================================================================================================
