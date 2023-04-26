'''
Team base module
Serves as the base for every module in teams sub-package.
Contains some additional shared variables and functions.
'''

# native imports
from datetime import datetime as dt
from pathlib import Path

# internal imports
from .._interfaces._chatbot import AbstractMessageSender
from .._interfaces._chatmsg import AbstractChatMessage
from .._interfaces._team import AbstractTeam
from .._shared.constants import SNAPSHOT_FOLDER
from .._shared.global_data import GlobalData
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from .._shared.types import SnapshotDict
from ..config.json_utils import read_snapshot_file
from ..config.json_utils import write_snapshot_file


def clear_team_members() -> bool:
  '''
  Remove all users from all teams.
  '''
  had_non_empty_teams: bool = False
  for team in GlobalData.Teams.get_all_teams():
    if len(team.members) > 0:
      had_non_empty_teams = True
      team.members.clear()
  if had_non_empty_teams:
    # dict has at least one element if had_non_empty_teams is True
    team = list(GlobalData.Teams.get_all_teams())[0]
    bot: AbstractMessageSender | None = team.bot
    if bot is None:
      # Remove the None part of team.bot's typing
      raise ValueError(f'Team {team.name} has not bot reference!')
    for chan in bot.channel_set:
      bot.send_priority_message(chan, "Teams have been cleared!")
  return had_non_empty_teams
# ------------------------------------------------------------------------------


def save_snapshot(snapshot_filename: str = '') -> str:
  '''
  Save runtime-modifiable data in snapshot_filename for the purpose of
  seamlessly restorting operations after program restart.
  '''
  if snapshot_filename == '':
    snapshot_filename = f"snapshot_{dt.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}"
  snapshot: SnapshotDict = {
    "timestamp": str(dt.utcnow()),
    "teams": {
      team_name: team.create_snapshot()
      for team_name, team in GlobalData.Teams.get_all_name_team_pairs()
    }
  }
  snapshot_with_schema: SnapshotDict = {
    "$schema": "../schema/snapshot_schema.json"
  } | snapshot  # type: ignore[assignment] # TypedDict doesn't support $ char
  if not snapshot_filename.endswith('.json'):
    snapshot_filename = f"{snapshot_filename}.json"
  SNAPSHOT_FOLDER.mkdir(parents=True, exist_ok=True)
  write_snapshot_file(
    SNAPSHOT_FOLDER / snapshot_filename, snapshot_with_schema
  )
  return snapshot_filename
# ------------------------------------------------------------------------------


def load_snapshot(snapshot_filename: str = '') -> None:
  '''
  Load runtime-modifiable data from snapshot_filename.
  '''
  if snapshot_filename == '':
    return
  if not snapshot_filename.endswith('.json'):
    snapshot_filename = f"{snapshot_filename}.json"
  filename: Path = SNAPSHOT_FOLDER / snapshot_filename
  if not filename.exists():
    thread_print(ColorText.error(
      f'Snapshot file missing: "{filename.absolute()}"'
    ))
    return
  snapshot: SnapshotDict = read_snapshot_file(
    SNAPSHOT_FOLDER / snapshot_filename
  )
  for team_name, team_snapshot in snapshot.get('teams', {}).items():
    team = GlobalData.Teams.get_by_name(team_name)
    if team is None:
      continue
    team.restore_snapshot(team_snapshot)
# ------------------------------------------------------------------------------


def __add_message_to_team(
  msg: AbstractChatMessage,
  team: AbstractTeam
) -> bool:
  '''
  Helper function for `add_message_to_assigned_team`
  * `True` if `msg` has been added to `team`
  * Otherwise `False`
  '''
  if (
    msg.channel in team.channels
    and team.actionset.message_is_command(msg)
    and not team.blocked_from_team(msg)
    and team.belongs_to_team(msg)
  ):
    GlobalData.Session.Chat.log_action_message(msg, team)
    team.add_message(msg)
    return True
  return False
# ------------------------------------------------------------------------------


def add_message_to_assigned_team(msg: AbstractChatMessage) -> None:
  '''
  If actions are accepted (file event set), valid action messages
  will be added to their assigned team's queue.
  '''
  if (
    GlobalData.EventStates.accept_input()
    and GlobalData.Prefix.Action.message_is_action(msg)
  ):
    # fast path: user already in team?
    team: AbstractTeam | None = GlobalData.Users.get_team(msg.user)
    if team is not None:
      if __add_message_to_team(msg, team):
        return
    # fallback: look for a fitting team
    for team in GlobalData.Teams.get_all_teams():
      if __add_message_to_team(msg, team):
        return
    # if no fitting teams exist: ignore msg
    return  # syntactic sugar


def create_combined_team_class(
  *team_classes: type[AbstractTeam]
) -> type[AbstractTeam]:
  '''
  Combine multiple `Team` classes into one combined `Team` class.

  This function dynamically creates a class that inherits from all the classes
  passed as arguments. All classes must be a descendent of `AbstractTeam`.
  '''
  class CombinedTeamClass(
    *team_classes,  # type: ignore[misc]  # https://github.com/python/mypy/issues/5928
    AbstractTeam
  ):
    '''Combiner Class skeleton'''
    pass

  return CombinedTeamClass
