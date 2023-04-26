'''
This module contains the class definitions used for periodically dumping
sessionlogs to disk.
'''

# native imports
from threading import Thread
from time import sleep
from time import time

# internal imports
from .._interfaces._thread_support import AbstractThreadSupport
from .._shared.global_data import GlobalData
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print_timestamped
from .._shared.primitive_types import seconds
from .._shared.types import ConfigDict


class SessionDumper(AbstractThreadSupport):
  '''
  Management class for dumping session logs to disk.
  '''
  keep_running: bool
  config: ConfigDict
  dumping_interval: seconds
  next_dumping_time: seconds
  file_basename: str
  file_counter: int
  counter_cap: int

  def __init__(
    self,
    config: ConfigDict,
    dumping_interval: seconds,
    file_basename: str,
    counter_cap: int = 2
  ) -> None:
    self.keep_running = True
    self.config = config
    self.dumping_interval = dumping_interval
    self.next_dumping_time = time() + dumping_interval
    self.file_basename = file_basename
    self.file_counter = -1
    self.counter_cap = counter_cap
  # ----------------------------------------------------------------------------

  def generate_temp_filename(self) -> str:
    '''
    Generate a temporary filename.
    '''
    file_extension: str = 'temp.json'
    if self.counter_cap <= 1:
      return f'{self.file_basename}.{file_extension}'
    self.file_counter += 1
    if self.file_counter >= self.counter_cap:
      self.file_counter = 0
    counter_length = len(str(self.counter_cap - 1))
    return (
      f'{self.file_basename}'
      f'.{self.file_counter:0>{counter_length}}'
      f'.{file_extension}'
    )
  # ----------------------------------------------------------------------------

  def final_dump(self) -> None:
    '''
    Dump the session log to disk.
    '''
    expected_filename: str = f'{self.file_basename}.json'
    real_filename = GlobalData.Session.dump(self.config, expected_filename)
    if real_filename:
      colored_text: str = ColorText.path(real_filename)
      thread_print_timestamped(
        f"Exported session information to file {colored_text} "
      )
    else:
      thread_print_timestamped(ColorText.error(
        "Failed export of session information to file: "
        f"{expected_filename}"
      ))
  # ----------------------------------------------------------------------------

  def periodic_dump(self) -> None:
    '''
    Dump the session log to disk with a temporary filename.
    '''
    while self.keep_running:
      if time() >= self.next_dumping_time:
        self.next_dumping_time = time() + self.dumping_interval
        expected_filename: str = self.generate_temp_filename()
        real_filename = GlobalData.Session.dump(self.config, expected_filename)
        if real_filename:
          colored_text: str = ColorText.path(real_filename)
          thread_print_timestamped(
            f"Periodic export of session information to file {colored_text} "
          )
      sleep(0.1)
  # ----------------------------------------------------------------------------

  def create_thread(self) -> None:
    '''
    Create thread.
    '''
    self.thread = Thread(
      target=self.periodic_dump,
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
