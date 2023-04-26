'''
This module deals with controlling state variables/functions based
on certain files being present in the folder `EVENT_FOLDER`.
'''

# native imports
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from time import sleep
from typing import Final

# pip imports
from keyboard import is_pressed

# internal imports
from .._interfaces._thread_support import AbstractThreadSupport
from .._shared.constants import ACCEPT_INPUT_FILE
from .._shared.constants import DELAY_RANDOM_FILE
from .._shared.constants import RANDOM_ACTIONS_FILE
from .._shared.constants import RESET_TEAMS_FILE
from .._shared.constants import UPDATE_INTERVAL
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from .._shared.primitive_types import millisecs
from ..config.config import Event_Settings
from ..config.config import Hotkey_Settings
from ..teams.functions import clear_team_members
from .events_states import GlobalEventStates


# ==================================================================================================
def create_Path(path: Path) -> None:
  try:
    path.open('x', encoding='utf-8').close()
  except FileExistsError:
    pass
# ==================================================================================================


# ==================================================================================================
@dataclass
class PressedKey:
  accept_input: bool
  random_action: bool
  reset_teams: bool
  random_delay_plus: bool
  random_delay_minus: bool
# ==================================================================================================


# ==================================================================================================
class GlobalEventHandler(AbstractThreadSupport):
  '''
  (Singleton) class for handling all filesystem events that allow
  controlling application behaviour during runtime with
  other external programs/scripts.
  '''
  # Instance variables:
  keep_running: bool
  event_settings: Event_Settings
  pressed: PressedKey
  thread: Thread
  # ----------------------------------------------------------------------------

  def __init__(
    self,
    event_settings: Event_Settings,
  ) -> None:
    self.keep_running = True
    self.pressed = PressedKey(False, False, False, False, False)
    self.event_settings = event_settings
    if self.event_settings.file_events.enabled:
      path_colored: str = ColorText.path(str(
        self.event_settings.file_events.path.absolute()
      ))
      thread_print(
        f"Observing event files in {path_colored} "
      )
    else:
      thread_print(ColorText.warning(
        "All File Events disabled!"
      ))
  # ----------------------------------------------------------------------------

  def handle_hotkey_event_triggers(self) -> None:
    hotkeys: Hotkey_Settings = self.event_settings.hotkeys
    # Accept Input
    if (
      hotkeys.accept_input
      and is_pressed(hotkeys.accept_input)
    ):
      # 2nd check since we don't want to permanently toggle between states
      if not self.pressed.accept_input:
        self.toggle_state_accept_input()
        self.pressed.accept_input = True
    else:
      self.pressed.accept_input = False

    # Random Actions
    if (
      hotkeys.random_action
      and is_pressed(hotkeys.random_action)
    ):
      # 2nd check since we don't want to permanently toggle between states
      if not self.pressed.random_action:
        self.toggle_state_random_action()
        self.pressed.random_action = True
    else:
      self.pressed.random_action = False

    # Reset Teams
    if (
      hotkeys.reset_teams
      and is_pressed(hotkeys.reset_teams)
    ):
      # 2nd check since we don't want to permanently toggle between states
      if not self.pressed.reset_teams:
        self.toggle_state_reset_teams()
        self.pressed.reset_teams = True
    else:
      self.pressed.reset_teams = False

    # Random Delay Plus
    if (
      hotkeys.random_delay_plus
      and is_pressed(hotkeys.random_delay_plus)
    ):
      # 2nd check since we don't want to permanently toggle between states
      if not self.pressed.random_delay_plus:
        self.add_state_delay_random(self.event_settings.step_delay_random)
        self.pressed.random_delay_plus = True
    else:
      self.pressed.random_delay_plus = False

    # Random Delay Minus
    if (
      hotkeys.random_delay_minus
      and is_pressed(hotkeys.random_delay_minus)
    ):
      # 2nd check since we don't want to permanently toggle between states
      if not self.pressed.random_delay_minus:
        self.add_state_delay_random(-1 * self.event_settings.step_delay_random)
        self.pressed.random_delay_minus = True
    else:
      self.pressed.random_delay_minus = False
  # ----------------------------------------------------------------------------

  def handle_file_event_triggers(self) -> None:
    '''
    Event handling function. Changes state variables and executes functions
    based on files (not) present in `EVENT_FOLDER`
    '''
    if self.event_settings.file_events.enabled:
      # ACCEPT INPUT
      self.change_state_accept_input(ACCEPT_INPUT_FILE.exists())

      # RANDOM ACTIONS
      self.change_state_random_action(RANDOM_ACTIONS_FILE.exists())

      # RESET TEAMS
      self.change_state_reset_teams(RESET_TEAMS_FILE.exists())

      # DELAY RANDOM
      try:
        with open(DELAY_RANDOM_FILE, mode='r', encoding='utf-8') as file:
          file_contents: str = file.readline()
        delay_percent: float = float(file_contents)
      except ValueError:
        # not a valid integer value, skip this read, maybe it works next time
        pass
      except FileNotFoundError:
        # If the file doesn't exist -> no delay set
        GlobalEventStates.state_delay_random = None
      except OSError as e:
        # DEBUG: print exception, so we know which ones to look
        # out for in the future
        thread_print(f"Exception during updating Delay Random state: {e}")
      else:
        self.change_state_delay_random(delay_percent)
  # ----------------------------------------------------------------------------

  def change_state_accept_input(self, new_state: bool) -> None:
    old_state: bool | None = GlobalEventStates.state_accept_input
    if old_state != new_state:
      GlobalEventStates.state_accept_input = new_state
      color_on_off: str = ColorText.on_off(GlobalEventStates.state_accept_input)
      thread_print(f"Accept Input: {color_on_off} ")
      # Make sure file system reflects changes if they were made manually
      if self.event_settings.file_events.enabled:
        filepath: Final[Path] = ACCEPT_INPUT_FILE
        if new_state:
          create_Path(filepath)
        else:
          filepath.unlink(missing_ok=True)
  # ----------------------------------------------------------------------------

  def change_state_random_action(self, new_state: bool) -> None:
    old_state: bool | None = GlobalEventStates.state_random_action
    if old_state != new_state:
      GlobalEventStates.state_random_action = new_state
      color_on_off: str = ColorText.on_off(GlobalEventStates.state_random_action)
      thread_print(f"Random Input: {color_on_off} ")
      # Make sure file system reflects changes if they were made manually
      if self.event_settings.file_events.enabled:
        filepath: Final[Path] = RANDOM_ACTIONS_FILE
        if new_state:
          create_Path(filepath)
        else:
          filepath.unlink(missing_ok=True)
  # ----------------------------------------------------------------------------

  def change_state_reset_teams(self, new_state: bool) -> None:
    GlobalEventStates.state_reset_teams = new_state
    if new_state:
      teams_were_cleared: bool = clear_team_members()
      if teams_were_cleared:
        GlobalEventStates.state_reset_teams = False
        # Teams have been cleared, reset relevant event file
        if self.event_settings.file_events.enabled:
          RESET_TEAMS_FILE.unlink(missing_ok=True)
  # ----------------------------------------------------------------------------

  def change_state_delay_random(self, delay_percent: float) -> None:
    new_delay: float = (
      delay_percent * self.event_settings.max_delay_random * 0.01
    )
    new_delay = max(new_delay, 0)
    if GlobalEventStates.state_delay_random != new_delay:
      GlobalEventStates.state_delay_random = new_delay
      thread_print(f"Delay random actions: {new_delay} ms")
      # Make sure file system reflects changes if they were made manually
      if self.event_settings.file_events.enabled:
        filepath: Final[Path] = DELAY_RANDOM_FILE
        new_file_contents = str(max(delay_percent, 0))
        try:
          with open(filepath, mode='w', encoding='utf-8') as file:
            file.write(new_file_contents)
        except OSError as e:
          thread_print(f"Exception during updating Delay Random state: {e}")
  # ----------------------------------------------------------------------------

  def toggle_state_accept_input(self) -> None:
    self.change_state_accept_input(not GlobalEventStates.state_accept_input)
  # ----------------------------------------------------------------------------

  def toggle_state_random_action(self) -> None:
    self.change_state_random_action(not GlobalEventStates.state_random_action)
  # ----------------------------------------------------------------------------

  def toggle_state_reset_teams(self) -> None:
    self.change_state_reset_teams(not GlobalEventStates.state_reset_teams)
  # ----------------------------------------------------------------------------

  def add_state_delay_random(self, offset: float) -> None:
    old_state: float = 0.0
    if GlobalEventStates.state_delay_random is not None:
      max_delay: millisecs = self.event_settings.max_delay_random
      if max_delay == 0:
        old_state = 0
      else:
        old_state = (
          GlobalEventStates.state_delay_random * 100 / max_delay
        )
    self.change_state_delay_random(old_state + offset)
  # ----------------------------------------------------------------------------

  def run_file_event_thread(self) -> None:
    '''
    Periodically run event handling function.
    '''
    while self.keep_running:
      self.handle_hotkey_event_triggers()
      self.handle_file_event_triggers()
      sleep(UPDATE_INTERVAL)
    return
  # ----------------------------------------------------------------------------

  def create_thread(self) -> None:
    '''
    Create thread.
    '''
    self.thread = Thread(
      target=self.run_file_event_thread,
      daemon=True
    )
  # ----------------------------------------------------------------------------

  def start_thread(self) -> None:
    '''
    Start thread.
    '''
    self.thread.start()
  # ----------------------------------------------------------------------------

  def stop_thread(self) -> None:
    '''
    Stop thread.
    '''
    self.keep_running = False
# ==================================================================================================
