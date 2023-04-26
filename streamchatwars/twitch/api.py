'''
This module contains code used to access Twitch API functions.
'''

# native imports
import asyncio
import logging
from asyncio import new_event_loop
from asyncio import set_event_loop
from threading import Thread
from time import sleep
from typing import cast
from uuid import UUID

# pip imports
from twitchAPI.helper import first
from twitchAPI.object import TwitchUser
from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch

# internal imports
from .._interfaces._thread_support import AbstractThreadSupport
from .._shared.global_data import GlobalData
from .._shared.types import LISTEN_CHANNELPOINTS_TYPE
from .._shared.types import CommunityPointsPubSubDict
from .._shared.types import TwitchAPICredentialDict
from ..config.json_utils import InvalidCredentialsError
from ..config.json_utils import decode_credential


# ==================================================================================================
class Twitch_API(AbstractThreadSupport):
  '''
  Manage access to the Twitch API.
  '''
  # Instance variables:
  twitch: Twitch
  keep_running: bool
  channels: set[str]
  pubsub: PubSub
  pubsub_topics: list[UUID]
  pubsub_thread: Thread

  def __init__(
    self,
    credentials: TwitchAPICredentialDict,
    channels: set[str]
  ) -> None:
    '''
    Create a Manager for accessing Twitch API functions.
    '''
    self.keep_running = True
    self.channels = channels
    self.pubsub_topics = []
    client_id = decode_credential(credentials.get('client_id'), None)
    client_secret = decode_credential(credentials.get('client_secret'), None)
    if client_id is None or client_secret is None:
      raise InvalidCredentialsError
    self.twitch: Twitch = Twitch(
      app_id=client_id,
      app_secret=client_secret,
      authenticate_app=False
    )
  # ----------------------------------------------------------------------------

  async def authenticate(self) -> None:
    '''
    Authenticate with Twitch API credentials.
    '''
    await self.twitch.authenticate_app([])
  # ----------------------------------------------------------------------------

  async def get_username_for_id(self, id: str) -> str:
    '''
    Query Twitch API for the username belonging to a given user id.
    '''
    response: TwitchUser | None = await first(
      self.twitch.get_users(user_ids=[id])
    )
    if not response:
      raise ValueError(f'No data for user id {id}')
    return_value: str = response.login
    return return_value
  # ----------------------------------------------------------------------------

  async def get_id_for_username(self, username: str) -> str:
    '''
    Query Twitch API for the user id belonging to a given username.
    '''
    response: TwitchUser | None = await first(
      self.twitch.get_users(logins=[username])
    )
    if not response:
      raise ValueError(f'No data for login {username}')
    return_value: str = response.id
    return return_value
  # ----------------------------------------------------------------------------

  async def callback_channel_points(
    self,
    uuid: UUID,
    data: CommunityPointsPubSubDict
  ) -> None:
    '''
    Called everytime channel point pubsub events happen.
    '''
    GlobalData.Session.ChannelPoints.log_message(data)
  # ----------------------------------------------------------------------------

  async def run_pubsub_thread_async(self) -> None:
    '''
    Function called by pubsub thread.
    '''
    try:
      logging.getLogger('twitchAPI.pubsub').setLevel(logging.ERROR)
      set_event_loop(new_event_loop())
      await self.authenticate()
      self.pubsub = PubSub(self.twitch)
      self.pubsub.start()
      for chan in self.channels:
        id: str = await self.get_id_for_username(
          chan[1:] if chan.startswith('#') else chan
        )
        listen_channelpoints: LISTEN_CHANNELPOINTS_TYPE = cast(
          LISTEN_CHANNELPOINTS_TYPE,
          self.pubsub.listen_undocumented_topic  # pyright: ignore[reportUnknownMemberType]
        )
        uuid: UUID = await listen_channelpoints(
          f'community-points-channel-v1.{id}',
          self.callback_channel_points
        )
        self.pubsub_topics.append(uuid)
      while self.keep_running:
        sleep(0.1)
      # We don't need to manually unlisten, but do out of courtesy.
      for uuid in self.pubsub_topics:
        await self.pubsub.unlisten(uuid)
    except Exception:
      raise
    finally:
      self.pubsub.stop()
      await self.twitch.close()  # type: ignore[no-untyped-call]
  # ----------------------------------------------------------------------------

  def run_pubsub_thread(self) -> None:
    '''
    Function called by pubsub thread.
    '''
    asyncio.run(self.run_pubsub_thread_async())
  # ----------------------------------------------------------------------------

  def create_thread(self) -> None:
    '''
    Create PubSub thread.
    '''
    self.pubsub_thread = Thread(
      target=self.run_pubsub_thread,
      daemon=True
    )
  # ----------------------------------------------------------------------------

  def start_thread(self) -> None:
    '''
    Start PubSub thread.
    '''
    self.pubsub_thread.start()
  # ----------------------------------------------------------------------------

  def stop_thread(self) -> None:
    '''
    Stop PubSub thread.
    '''
    self.keep_running = False
# ==================================================================================================
