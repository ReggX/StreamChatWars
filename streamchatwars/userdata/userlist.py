'''
This module allows creating advanced user lists that not only
accept usernames but also special group identifiers that
dynamically change the userlist and add/remove members
based on them fulfilling the membership criteria for the
group identifiers.
'''

# native imports
from collections.abc import Callable
from re import Pattern
from re import compile
from re import escape
from typing import Final

# internal imports
from .._interfaces._chatmsg import AbstractChatMessage
from .._interfaces._userlist import AbstractUserList
from .._shared.constants import CHANNEL_NAME_PATTERN
from .._shared.types import UserListDict


# ==================================================================================================
class SpecialGroupsContainer:
  '''
  Data class to easily access special group sets
  '''
  # Instance variables:
  broadcaster: set[str]
  mods: set[str]
  vips: set[str]
  subs: set[str]
  tier3subs: set[str]
  tier2subs: set[str]
  tier1subs: set[str]
  partners: set[str]
  founders: set[str]
  staff: set[str]
  prime: set[str]
  turbo: set[str]
  users: set[str]
  mapping: dict[str, set[str]]
  # ----------------------------------------------------------------------------

  def __init__(self) -> None:
    self.broadcaster = set()
    self.mods = set()
    self.vips = set()
    self.subs = set()
    self.tier3subs = set()
    self.tier2subs = set()
    self.tier1subs = set()
    self.partners = set()
    self.founders = set()
    self.staff = set()
    self.prime = set()
    self.turbo = set()
    self.users = set()

    self.mapping = {
      '$broadcaster': self.broadcaster,
      '$mods':        self.mods,
      '$vips':        self.vips,
      '$subs':        self.subs,
      '$tier3subs':   self.tier3subs,
      '$tier2subs':   self.tier2subs,
      '$tier1subs':   self.tier1subs,
      '$partners':    self.partners,
      '$founders':    self.founders,
      '$staff':       self.staff,
      '$prime':       self.prime,
      '$turbo':       self.turbo,
      '$users':       self.users,
    }

    # create a OR regex pattern from the special group $identifiers
    # (keys in mapping)
    group_pattern: str = "|".join(
      escape(group_name) for group_name in self.mapping.keys()
    )
    # optionally, add a [#channel] limiter after the special group
    # in square brackets
    # $groupname[channelname] -> e.g. $mods[dansgaming]
    pattern = rf"^({group_pattern})(?:\[({CHANNEL_NAME_PATTERN})\])?$"
    # pattern allows upper case A-Z, since entries always gets converted
    # to lower case by the methods that use REGEX
    self.REGEX: Final[Pattern[str]] = compile(pattern)
# ==================================================================================================


# ==================================================================================================
class UserList(AbstractUserList):
  '''
  Special membership list that allows defining some subgroups to include.

  Subgroups have an associated is_subgroup function that checks
  if the user/message fulfill the subgroup membership criteria.
  '''
  cache_users: bool
  '''
  Should the user sets keep their last known status or get rechecked?

  Be aware that this setting could have serious performance implications,
  since, in the worst case, every message checks for whitelist and
  blacklist membership for every single team.
  '''
  # Type hints
  known_users: set[str]
  '''set of all users that have been checked against the list'''
  included_users: set[str]
  '''set of all users that have been checked and passed'''
  fixed_users: set[str]
  '''set of all users that are included by default/have been added manually'''
  special_groups: SpecialGroupsContainer
  '''`SpecialGroups` object that contains all subgroup sets'''
  subgroup_checks: list[Callable[[AbstractChatMessage], bool]]
  '''List of all checks for subgroup membership'''

  def __init__(self, cache_users: bool = True) -> None:
    '''
    Real init method gets called in __init_helper().
    '''
    self.__init_helper(cache_users=cache_users)
  # ----------------------------------------------------------------------------

  def __init_helper(self, cache_users: bool = True) -> None:
    '''
    Real workhorse of __init__()
    '''
    self.cache_users = cache_users
    self.known_users = set()
    self.included_users = set()
    self.fixed_users = set()
    self.special_groups = SpecialGroupsContainer()

    self.subgroup_checks = [
      self.is_broadcaster,
      self.is_mod,
      self.is_vip,
      self.is_subscribed,
      self.is_tier3sub,
      self.is_tier2sub,
      self.is_tier1sub,
      self.is_partner,
      self.is_founder,
      self.is_staff,
      self.is_prime,
      self.is_turbo,
      self.is_user,
    ]
  # ----------------------------------------------------------------------------

  def clear(self) -> None:
    '''
    Reset Userlist to its initialized state.
    '''
    self.__init_helper(cache_users=self.cache_users)
  # ----------------------------------------------------------------------------

  def add_to_list(
    self,
    entry: str,
    team_channel_set: set[str] | None = None
  ) -> None:
    '''
    Adds `entry` to UserList.

    * If `entry` is a special group token (`$group[chan]`), it will add
    `chan` (`team_channel_set` if no channel is specified) to the
    special subgroup `group` and invalidate the `known_users` and
    `excluded_users` sets.
    * Otherwise add `entry` to the `fixed_users` set.
    '''
    if team_channel_set is None:
      team_channel_set = set()
    lower_case_entry: str = str(entry).lower()
    regex_result: list[tuple[str, str]] = (
      self.special_groups.REGEX.findall(lower_case_entry)
    )
    if regex_result:
      group: str = regex_result[0][0]
      chan: str = regex_result[0][1]
      if chan:  # is not empty
        chan = chan if chan.startswith('#') else f'#{chan}'
        self.special_groups.mapping[group].add(chan)
      else:
        for chan in team_channel_set:
          self.special_groups.mapping[group].add(chan)
      # the subgroup list has been modified, so we need to invalidate some sets
      self.known_users.clear()
    else:
      self.fixed_users.add(lower_case_entry)
      self.included_users.add(lower_case_entry)
      self.known_users.add(lower_case_entry)
  # ----------------------------------------------------------------------------

  def remove_from_list(
    self,
    entry: str,
    team_channel_set: set[str] | None = None
  ) -> None:
    '''
    Remove `entry` from UserList.

    * If `entry` is a special group token (`$group[chan]`), it will remove
    `chan` (`team_channel_list` if no channel is specified) from the
    special subgroup `group` and invalidate the `known_users` and
    `included_users` sets.
    * Otherwise remove `entry` from the `fixed_users` set.
    '''
    if team_channel_set is None:
      team_channel_set = set()
    lower_case_entry: str = str(entry).lower()
    regex_result: list[tuple[str, str]] = (
      self.special_groups.REGEX.findall(lower_case_entry)
    )
    if regex_result:
      group: str = regex_result[0][0]
      chan: str = regex_result[0][1]
      if chan:  # is not empty
        chan = chan if chan.startswith('#') else f'#{chan}'
        self.special_groups.mapping[group].discard(chan)
      else:
        for chan in team_channel_set:
          self.special_groups.mapping[group].discard(chan)
      # the subgroup list has been modified, so we need to invalidate some sets
      self.known_users.clear()
      self.included_users.clear()
    else:
      self.fixed_users.discard(lower_case_entry)
      self.included_users.discard(lower_case_entry)
      # We also need to remove the user from known_users, since they could
      # still be included via a special group, so we can't have their removal
      # cached yet. The subgroup could bring them back into included_users.
      self.known_users.discard(lower_case_entry)
  # ----------------------------------------------------------------------------

  def __contains__(self, item: AbstractChatMessage | str) -> bool:
    '''
    `in` operator, calls `message_in_list()` if `item` is a
    `AbstractChatMessage` object, otherwise falls back on `user_in_list()`
    '''
    if isinstance(item, AbstractChatMessage):
      return self.message_in_list(item)
    # Fallback (hides the third state [None] of user_in_list):
    return bool(self.user_in_list(item))
  # ----------------------------------------------------------------------------

  def message_in_list(self, msg: AbstractChatMessage) -> bool:
    '''
    Return `True` if message fits any of the UserList criteria.

    * If `cache_users` is enabled, it will check its cache of known_users.
    * If it not cached, it will then check the `fixed_users` set.
    * If not in the set, it will check if any special subgroups apply.
    * Otherwise, return `False` and cache result.
    '''
    if self.cache_users and msg.user in self.known_users:
      return msg.user in self.included_users
    if msg.user in self.fixed_users:
      self.included_users.add(msg.user)
      self.known_users.add(msg.user)
      return True
    if self.is_in_any_subgroup(msg=msg):
      self.included_users.add(msg.user)
      self.known_users.add(msg.user)
      return True
    self.known_users.add(msg.user)
    return False
  # ----------------------------------------------------------------------------

  def user_in_list(self, user: str) -> bool | None:
    '''
    * If `user` is cached in `known_users`, return cache status.
    * Return `True` if included in `fixed_users` set
    * Otherwise, return `None` to indicate that the
    exact status could not be determined.
    '''
    if self.cache_users and user in self.known_users:
      return user in self.included_users
    if user in self.fixed_users:
      self.included_users.add(user)
      self.known_users.add(user)
      return True
    return None  # status unknown!
  # ----------------------------------------------------------------------------

  def export_dict(self) -> UserListDict:
    '''
    Export Userlist instance data into simple dict for snapshot purposes.
    '''
    ul_dict: UserListDict = {
      'users': list(self.fixed_users),
      'groups': {
        group_name: list(group_channels)
        for group_name, group_channels in self.special_groups.mapping.items()
      }
    }
    return ul_dict
  # ----------------------------------------------------------------------------

  def import_dict(self, ul_dict: UserListDict) -> None:
    '''
    Import Userlist instance data from simple snapshot dict.
    '''
    # Add users
    for user in ul_dict.get('users', []):
      self.fixed_users.add(user)
    # Add groups
    for group_name, channel_list in ul_dict.get('groups', {}).items():
      group = self.special_groups.mapping[group_name]
      for chan in channel_list:
        group.add(chan)
    # invalidate cache
    self.known_users.clear()
  # ----------------------------------------------------------------------------

  def is_in_any_subgroup(self, msg: AbstractChatMessage) -> bool:
    '''
    Check if any subgroups flag positive for `msg`
    '''
    return any(is_in_group(msg) for is_in_group in self.subgroup_checks)
  # ----------------------------------------------------------------------------

  def is_broadcaster(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Broadcaster badge
    '''
    if self.special_groups.broadcaster:
      if msg.channel in self.special_groups.broadcaster:
        return 'broadcaster' in msg.tags.get('badges', '')
    return False
  # ----------------------------------------------------------------------------

  def is_mod(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Moderator status
    '''
    if self.special_groups.mods:
      if msg.channel in self.special_groups.mods:
        return msg.tags.get('mod', '0') != '0'
    return False
  # ----------------------------------------------------------------------------

  def is_vip(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has VIP badge
    '''
    if self.special_groups.vips:
      if msg.channel in self.special_groups.vips:
        return 'vip' in msg.tags.get('badges', '')
    return False
  # ----------------------------------------------------------------------------

  def is_subscribed(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Subscriber status
    '''
    if self.special_groups.subs:
      if msg.channel in self.special_groups.subs:
        return msg.tags.get('subscriber', '0') != '0'
    return False
  # ----------------------------------------------------------------------------

  def is_tier3sub(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Tier 3 subscriber badge flair
    '''
    if self.special_groups.tier3subs:
      if msg.channel in self.special_groups.tier3subs:
        if msg.tags.get('subscriber', '0') != '0':
          badge: str
          for badge in msg.tags.get('badges', '').split(','):
            badge_split: list[str] = badge.split('/')
            if badge_split[0] == 'subscriber':
              # Tier 3 subs are 3xyz with xyz being the real number of months
              # e.g. subscriber/3012 is a twelve months Tier 3 subscriber
              return int(int(badge_split[1]) / 1000) == 3
    return False
  # ----------------------------------------------------------------------------

  def is_tier2sub(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Tier 2 subscriber badge flair
    '''
    if self.special_groups.tier2subs:
      if msg.channel in self.special_groups.tier2subs:
        if msg.tags.get('subscriber', '0') != '0':
          badge: str
          for badge in msg.tags.get('badges', '').split(','):
            badge_split: list[str] = badge.split('/')
            if badge_split[0] == 'subscriber':
              # Tier 2 subs are 2xyz with xyz being the real number of months
              # e.g. subscriber/2012 is a twelve months Tier 2 subscriber
              return int(int(badge_split[1]) / 1000) == 2
    return False
  # ----------------------------------------------------------------------------

  def is_tier1sub(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has flairless subscriber badge
    '''
    if self.special_groups.tier1subs:
      if msg.channel in self.special_groups.tier1subs:
        if msg.tags.get('subscriber', '0') != '0':
          badge: str
          for badge in msg.tags.get('badges', '').split(','):
            badge_split: list[str] = badge.split('/')
            if badge_split[0] == 'subscriber':
              # Tier 1 subs are xyz with xyz being the real number of months
              # e.g. subscriber/12 is a twelve months Tier 1 subscriber
              return int(int(badge_split[1]) / 1000) == 0
    return False
  # ----------------------------------------------------------------------------

  def is_partner(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Partner badge
    '''
    if self.special_groups.partners:
      if msg.channel in self.special_groups.partners:
        return 'partner' in msg.tags.get('badges', '')
    return False
  # ----------------------------------------------------------------------------

  def is_founder(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Founder badge
    '''
    if self.special_groups.founders:
      if msg.channel in self.special_groups.founders:
        return 'founder' in msg.tags.get('badges', '')
    return False
  # ----------------------------------------------------------------------------

  def is_staff(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Staff/Admin badge
    '''
    if self.special_groups.staff:
      if msg.channel in self.special_groups.staff:
        return (
          'staff' in msg.tags.get('badges', '')
          or 'admin' in msg.tags.get('badges', '')
        )
    return False
  # ----------------------------------------------------------------------------

  def is_prime(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Founder badge
    '''
    if self.special_groups.prime:
      if msg.channel in self.special_groups.prime:
        return 'premium' in msg.tags.get('badges', '')
    return False
  # ----------------------------------------------------------------------------

  def is_turbo(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg` has Founder badge
    '''
    if self.special_groups.turbo:
      if msg.channel in self.special_groups.turbo:
        return 'turbo' in msg.tags.get('badges', '')
    return False
  # ----------------------------------------------------------------------------

  def is_user(self, msg: AbstractChatMessage) -> bool:
    '''
    Check subgroup: `msg.channel` in group
    '''
    if self.special_groups.users:
      return msg.channel in self.special_groups.users
    return False
# ==================================================================================================
