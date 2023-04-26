'''
Helper functions for the rest of the package.
This module has all functions that require the PyPI package colorama
'''

# pip imports
from colorama import Back
from colorama import Fore
from colorama import Style


class ColorText:
  '''
  Namespace for colorama wrapper functions
  '''
  @staticmethod
  def init() -> None:
    '''
    Initialize colorama

    (has to be called before other colorama functions to enable color on
    legacy Windows terminals)
    '''
    # pip imports
    from colorama import init
    init()
  # ----------------------------------------------------------------------------

  @staticmethod
  def on_off(state: bool) -> str:
    '''
    Format a boolean value to a colorful ON/OFF for STDOUT
    '''
    if state:
      return f"{Fore.BLACK}{Back.LIGHTGREEN_EX} ON {Style.RESET_ALL}"
    else:
      return f"{Fore.YELLOW}{Back.RED} OFF {Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def path(path: str) -> str:
    '''
    Format a file path with colors for STDOUT
    '''
    return f"{Fore.BLUE}{Back.LIGHTWHITE_EX}{path}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def error(message: str) -> str:
    '''
    Format a error message with colors for STDOUT
    '''
    return f"{Fore.RED}{Back.BLACK}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def warning(message: str) -> str:
    '''
    Format a warning message with colors for STDOUT
    '''
    return f"{Fore.YELLOW}{Back.BLACK}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def good(message: str) -> str:
    '''
    Format a positive message with colors for STDOUT
    '''
    return f"{Fore.GREEN}{Back.BLACK}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def info(message: str) -> str:
    '''
    Format an informational message with colors for STDOUT
    '''
    return f"{Fore.LIGHTCYAN_EX}{Back.BLACK}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def done(message: str) -> str:
    '''
    Format a final message with colors for STDOUT
    '''
    return f"{Fore.BLACK}{Back.LIGHTCYAN_EX}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def added(message: str) -> str:
    '''
    Format an addition message with colors for STDOUT
    '''
    return f"{Fore.LIGHTGREEN_EX}{Back.BLACK}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def removed(message: str) -> str:
    '''
    Format a removal message with colors for STDOUT
    '''
    return f"{Fore.LIGHTRED_EX}{Back.BLACK}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------

  @staticmethod
  def changed(message: str) -> str:
    '''
    Format a change message with colors for STDOUT
    '''
    return f"{Fore.LIGHTYELLOW_EX}{Back.BLACK}{message}{Style.RESET_ALL}"
  # ----------------------------------------------------------------------------
