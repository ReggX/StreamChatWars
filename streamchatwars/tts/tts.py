'''
This module contains code used for text-to-speech.
'''

# native imports
import os
from queue import Queue
from tempfile import TemporaryDirectory
from threading import Thread
from time import sleep

# pip imports
import pyttsx3
from pyttsx3.engine import Engine

# internal imports
from .._interfaces._thread_support import AbstractThreadSupport
from .._interfaces._tts import AbstractTTSQueue
from .._shared.constants import DEFAULT_VOICE_ID
from .._shared.helpers_print import thread_print


os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# pip imports
import pygame  # noqa: E402
from pygame.mixer import Channel  # noqa: E402
from pygame.mixer import Sound  # noqa: E402


# ==================================================================================================
class TTS(AbstractTTSQueue, AbstractThreadSupport):
  '''
  Management class for Text to speech messages.
  '''
  engine: Engine
  voice_ids: list[str]
  channel_dict: dict[str, Channel]
  max_duration: float
  message_queue: Queue[tuple[str, str]]
  keep_running: bool

  def __init__(
    self,
    voice_ids: list[str] | None = None,
    rate: int = 150,
    volume: float = 1.0,
    number_of_channels: int = 10,
    max_duration: float = 30.0
  ) -> None:
    if voice_ids is None:
      voice_ids = [DEFAULT_VOICE_ID]
    self.voice_ids = voice_ids
    pygame.mixer.init()
    pygame.mixer.set_num_channels(number_of_channels)
    self.max_duration = max_duration
    self.channel_dict = {}
    self.keep_running = True
    self.message_queue = Queue()
  # ----------------------------------------------------------------------------

  def init_engine(self) -> None:
    '''
    Initialize the TTS engine.
    '''
    self.engine = pyttsx3.init(driverName="sapi5", debug=False)
    self.engine.setProperty('voice', self.voice_ids[0])
    self.engine.setProperty('rate', 150)
    self.engine.setProperty('volume', 1.0)
    self.engine.runAndWait()
  # ----------------------------------------------------------------------------

  def play_tts_for_user(self, text: str, user: str) -> None:
    '''
    Play text to speech message for a user.
    If a channel is already playing for the user, then the current running
    message will be replaced with the new message.
    '''
    channel: Channel | None = self.channel_dict.get(user, None)
    with TemporaryDirectory(prefix="StreamChatWarsTTS-") as tmpdir:
      filename = f"{tmpdir}/tts.wav"
      user_index: int = hash(user) % len(self.voice_ids)
      voice_name = self.voice_ids[user_index].split("\\")[-1]
      thread_print(f"Playing TTS for {user} [{voice_name}]: {text}")
      self.engine.setProperty('voice', self.voice_ids[user_index])
      self.convert_text_to_sound_file(text, filename)
      try:
        channel = self.play_sound_file(filename, channel)
      except FileNotFoundError:
        thread_print(f"File not found: {filename}")
        return
    self.channel_dict[user] = channel
  # ----------------------------------------------------------------------------

  def convert_text_to_sound_file(self, text: str, filename: str) -> None:
    '''
    Create a sound file from the provided text.
    '''
    self.engine.save_to_file(text, filename)
    self.engine.runAndWait()
  # ----------------------------------------------------------------------------

  def play_sound_file(
    self,
    filename: str,
    channel: Channel | None = None,
  ) -> Channel:
    '''
    Play a sound file on the provided channel.
    If no channel is provided, then a free channel will be used.
    If no free channels are available, then the channel with the longest
    running sound will be replaced.

    The sound will automatically stop after the manager's max_duration value
    is reached (Spam reduction).
    '''
    snd = Sound(file=filename)
    if channel is None:
      channel = pygame.mixer.find_channel(force=True)
    channel.play(snd, maxtime=int(self.max_duration * 1000))
    return channel
  # ----------------------------------------------------------------------------

  def queue_tts_message(self, text: str, user: str) -> None:
    '''
    Add a message to the queue.
    '''
    self.message_queue.put((text, user))
  # ----------------------------------------------------------------------------

  def run_tts_thread(self) -> None:
    '''
    Periodically check the queue for messages and play them as TTS.
    '''
    # We need to initialize the engine in the thread, otherwise it will
    # fail to initialize its driver COM subcomponents, since they run in
    # apartment threading mode.
    self.init_engine()
    while self.keep_running:
      if not self.message_queue.empty():
        text, user = self.message_queue.get()
        self.play_tts_for_user(text, user)
      sleep(0.1)
    # Clean up the engine:
    # Since the engine is initialized in the thread, it must be
    # deinitialized in the thread as well.
    del self.engine
  # ----------------------------------------------------------------------------

  def create_thread(self) -> None:
    '''
    Create thread.
    '''
    self.thread = Thread(
      target=self.run_tts_thread,
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
