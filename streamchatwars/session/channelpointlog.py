'''
This module contains the class definitions used for logging channel point
redeems. It's imported into _shared.global_data, which is why need
to pay special attention to not import anything that could result
circular imports!
'''

# native imports
from dataclasses import dataclass
from dataclasses import field
from typing import cast

# internal imports
from .._shared.types import CommunityPointsPubSubDict
from .._shared.types import CommunityPointsPubSubDict_reward_redeemed
from .._shared.types import RedemptionDict


# ==================================================================================================
@dataclass
class ChannelPointLog:
  '''List of all collected console messages with related functions.'''
  messages: list[CommunityPointsPubSubDict] = field(default_factory=list)
  # ----------------------------------------------------------------------------

  def log_message(self, message: CommunityPointsPubSubDict) -> None:
    '''Add message to the log.'''
    self.messages.append(message)
  # ----------------------------------------------------------------------------

  def export_list(self) -> list[CommunityPointsPubSubDict]:
    '''Export list of collected messages in a JSON serializable way.'''
    return self.messages
  # ----------------------------------------------------------------------------

  def get_user_redeems(self) -> list[RedemptionDict]:
    '''Get a list of all user redeems.'''
    redeems: list[RedemptionDict] = []
    for message in self.messages:
      if message.get('type') == 'reward-redeemed':
        # need explicit cast here because type checkers may not recognize that
        # the value of message['type'] only allows one subtype.
        message = cast(CommunityPointsPubSubDict_reward_redeemed, message)
        redeems.append(message['data']['redemption'])
    return redeems
  # ----------------------------------------------------------------------------

  def clear(self) -> None:
    '''Clear out all messages.'''
    self.messages.clear()
# ==================================================================================================
