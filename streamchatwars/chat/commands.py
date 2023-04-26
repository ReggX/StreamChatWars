'''
This module handles chat commands (not to be confused with action commands).
'''

# native imports
from collections.abc import Callable
from collections.abc import Sequence
from functools import wraps
from typing import Literal

# internal imports
from .._interfaces._team import AbstractTeam
from .._shared.constants import MACRO_NAME_REGEX
from .._shared.constants import MAX_MESSAGE_LENGTH
from .._shared.constants import SNAPSHOT_NAME_REGEX
from .._shared.global_data import GlobalData
from .._shared.helpers_color import ColorText
from .._shared.helpers_print import thread_print
from .._shared.types import RedemptionDict
from ..teams.functions import clear_team_members
from ..teams.functions import load_snapshot
from ..teams.functions import save_snapshot
from .chatmsg import ChatMessage


# ------------------------------------------------------------------------------
class ReturnException(Exception):
  pass
# ------------------------------------------------------------------------------


# ********** @operator decorator *******************************************************************
def operator_command(
  decorated_function: Callable[[ChatMessage], None]
) -> Callable[[ChatMessage], None]:
  '''
  Don't execute command if `ChatMessage` is not allowed to use operator
  commands!
  '''
  @wraps(decorated_function)
  def wrap_cmd(msg: ChatMessage) -> None:
    if GlobalData.Operators.is_operator(msg):
      decorated_function(msg)
  return wrap_cmd
# **************************************************************************************************


# ********** helper function: queue_long_message ***************************************************
def queue_long_message(
  msg: ChatMessage,
  message: str,
  command_name: str
) -> None:
  '''
  Split up potentially long message into multiple parts and add them to the
  message queue.
  '''
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  message_list: list[str] = []
  while len(message) > MAX_MESSAGE_LENGTH:
    last_space: int = message[:MAX_MESSAGE_LENGTH].rfind(' ')
    if last_space == -1:
      thread_print(ColorText.warning(
        f"Command {command_name}: can't send overly long message "
        f"(over {MAX_MESSAGE_LENGTH} characters): {message}"
      ))
      return
    message_list.append(message[:last_space])
    message = message[last_space + 1:]  # truncate message before last_space
  message_list.append(message)
  if len(message_list) > 1:
    for i, message in enumerate(message_list):
      msg.parent.queue_message(
        msg.channel,
        f"{message} ({command_name} {i+1}/{len(message_list)})"
      )
  else:
    msg.parent.queue_message(msg.channel, message)
# **************************************************************************************************


# ********** helper function: valid_macro_name *****************************************************
def valid_macro_name(msg: ChatMessage, macro_name: str) -> bool:
  '''
  Check `macro_name` against regex and message user's channel if they need
  to fix their input parameter.
  '''
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  if not MACRO_NAME_REGEX.match(macro_name):
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, invalid macro name, only a-z, 0-9 and _ allowed!"
    )
    return False
  return True
# **************************************************************************************************


# ========== Command: Teams ========================================================================
def cmd_teams(msg: ChatMessage) -> None:
  '''
  `teams` command: List all active non-hidden teams for the requesting user.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  # ### Execution ###
  teams: str = ', '.join([
    f'"{team.name}" {len(team.members)} members'
    for team in GlobalData.Teams.get_all_teams() if not team.hidden
  ])
  # ### Post-execution feedback ###
  message: str = f"Current team composition: {teams}"
  msg.parent.send_message(msg.channel, message)
# ==================================================================================================


# ========== Command: MyTeam =======================================================================
def cmd_myTeam(msg: ChatMessage) -> None:
  '''
  `myteam` command: Tell the requesting user which team they are assigned to.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  # ### Execution ###
  team: AbstractTeam | None = GlobalData.Users.get_team(msg.user)
  # ### Post-execution feedback ###
  if team is None:
    # No assigned team
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, you are not assigned to any team yet."
    )
    return
  if (
    not team.blocked_from_team(msg=msg)
    and team.belongs_to_team(msg)
  ):
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, your team is: {team.name}"
    )
  else:
    # Side effect: Remove if on team illegaly.
    team.members.discard(msg.user)
    GlobalData.Users.discard(msg.user)
    thread_print(ColorText.warning(
      f"Removed user {msg.user} from Team '{team.name}' since they don't meet"
      "the membership criteria anymore."
    ))
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, you are not assigned to any team yet."
    )
# ==================================================================================================


# ========== Command: YourTeam =====================================================================
def cmd_yourTeam(msg: ChatMessage) -> None:
  '''
  `yourteam <USER>` command: Tell <USER> user which team they are assigned to.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = GlobalData.Prefix.Command.split_message(msg)
  if len(args) < 2:
    return
  # ### Execution ###
  user_arg: str = args[1]
  user: str = (user_arg if user_arg[:1] != '@' else user_arg[1:]).lower()
  team: AbstractTeam | None = GlobalData.Users.get_team(user)
  # ### Post-execution feedback ###
  if team is None:
    # No assigned team
    msg.parent.send_message(
      msg.channel,
      f"@{user}, you are not assigned to any team yet."
    )
    return
  if (
    not team.blocked_from_team(msg=msg)
    and team.belongs_to_team(msg)
  ):
    msg.parent.send_message(msg.channel, f"@{user}, your team is: {team.name}")
  else:
    # Side effect: Remove if on team illegaly.
    team.members.discard(user)
    GlobalData.Users.discard(user)
    thread_print(ColorText.warning(
      f"Removed user {user} from Team '{team.name}' since they don't meet "
      "the membership criteria anymore."
    ))
    msg.parent.send_message(
      msg.channel,
      f"@{user}, you are not assigned to any team yet."
    )
# ==================================================================================================


# ========== Command: JoinTeam =====================================================================
def cmd_joinTeam(msg: ChatMessage) -> None:
  '''
  `jointeam <TEAM>` command: Add the requesting user to team
  if they are allowed.
  '''

  # ### Pre-execution checks ###
  try:
    team_name_arg = _joinTeam_pre_execution_checks(msg)
  except ReturnException:
    return

  # already checked and raised in Pre-execution checks
  assert msg.parent is not None  # nosec B101

  # all checks completed: assign user to selected team
  # ### Execution ###
  for team in GlobalData.Teams.get_all_teams():
    # remove from all teams
    team.members.discard(msg.user)
    # assign to new team
    if team.name.lower() == team_name_arg.lower():
      result: bool = team.join_team(msg.user)
      # ### Post-execution feedback ###
      if result:
        msg.parent.send_message(
          msg.channel,
          f"@{msg.user}, your new team is: {team.name}"
        )
# ------------------------------------------------------------------------------


def _joinTeam_pre_execution_checks(msg: ChatMessage) -> str:
  '''outsourced guard clause'''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')

  # Split message into arguments
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=1)
  )
  if len(args) < 2:
    raise ReturnException
  team_name_arg: str = args[1]

  # 1st check: can user leave their current team?
  team: AbstractTeam | None = GlobalData.Users.get_team(msg.user)
  if team is not None and not team.leavable:
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, you're not allowed to leave your current team: {team.name}"
    )
    raise ReturnException

  # 2nd check: are there teams that can be joined via command in the first place
  team_names: list[str] = [
    team.name for team in GlobalData.Teams.get_all_teams() if (
      team.joinable
      and team.exclusive
      and not team.hidden
      and not team.blocked_from_team(msg)
    )
  ]
  if len(team_names) == 0:
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, There are no teams you are allowed to join via command."
    )
    raise ReturnException

  # 3rd check: is the selected team one of the joinable teams?
  if team_name_arg.lower() not in [t.lower() for t in team_names]:
    allowed_team_names = f'''"{'" "'.join(team_names)}"'''
    msg.parent.send_message(
      msg.channel,
      f"Team {team_name_arg} can't be joined. "
      f"Team name must be one of the following: {allowed_team_names}"
    )
    raise ReturnException

  return team_name_arg
# ==================================================================================================


# ========== Command: LeaveTeam ====================================================================
def cmd_leaveTeam(msg: ChatMessage) -> None:
  '''
  `leaveteam` command: Remove the requesting user from their current team
  if they are allowed.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  team: AbstractTeam | None = GlobalData.Users.get_team(msg.user)
  if team is None:
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, you are not assigned to any team."
    )
    return
  if not team.leavable:
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, you're not allowed to leave team: {team.name}"
    )
    return
  # ### Execution ###
  result: bool = team.leave_team(msg.user)
  # ### Post-execution feedback ###
  if result:
    msg.parent.send_message(
      msg.channel,
      f"@{msg.user}, you left team: {team.name}"
    )
# ==================================================================================================


# ========== Command: HowToPlay ====================================================================
def cmd_howtoplay(msg: ChatMessage) -> None:
  '''
  `howtoplay` command: Send the requesting user a link with a small
  explanation on how to control the game.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  # ### Execution ###
  doc_set: set[str] = set()
  team: AbstractTeam
  for team in GlobalData.Teams.get_all_teams():
    if team.actionset.doc_url:
      doc_set.add(team.actionset.doc_url)
  # ### Post-execution feedback ###
  message: str = f"Here's how to play this game mode: {' '.join(doc_set)}"
  queue_long_message(msg, message, "HowToPlay")
# ==================================================================================================


# ========== Command: CountRedeens =================================================================
# @operator_command
def cmd_countRedeems(msg: ChatMessage) -> None:
  '''
  `countredeems` command: Send the requesting user information on how many
  redeems have been used this session.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  if not GlobalData.Session.ChannelPoints.is_enabled():
    return
  # ### Execution ###
  start_time: str = GlobalData.Session.startdate().strftime(
    '%Y-%m-%d %H:%M:%S UTC'
  )
  redeems: list[RedemptionDict]
  redeems = GlobalData.Session.ChannelPoints.get_user_redeems()
  number_of_redeems: int = len(redeems)
  points_spent: int = sum(r["reward"]["cost"] for r in redeems)
  video_redeems: list[RedemptionDict] = [
    r for r in redeems
    if (
      "e3ceb39f-2a7a-48b1-9f1e-d76bce1cd026" == r["reward"]["id"]  # 100k video
      or "6b52f009-3154-49e3-a970-8f636de720a6" == r["reward"]["id"]  # 12k video
    )
  ]
  number_of_video_redeems: int = len(video_redeems)
  points_spent_video: int = sum(r["reward"]["cost"] for r in video_redeems)
  sound_redeems: list[RedemptionDict] = [
    r for r in redeems
    if "Powered by Blerp" in r["reward"]["prompt"]  # Blerp sound alert
  ]
  number_of_sound_redeems: int = len(sound_redeems)
  points_spent_sound: int = sum(r["reward"]["cost"] for r in sound_redeems)
  message: str = (
    f"{points_spent} points have been spent on {number_of_redeems} redeems: "
    f"{points_spent_sound} points on {number_of_sound_redeems} sound redeems; "
    f"{points_spent_video} points on {number_of_video_redeems} video redeems. "
    f"(Refunded redeems included, counting since {start_time})"
  )
  msg.parent.send_message(
    msg.channel,
    message
  )
# ==================================================================================================


# ========== Command: TTS ==========================================================================
def cmd_tts(msg: ChatMessage) -> None:
  '''
  `tts <MESSAGE>` command: Add <MESSAGE> to the TTS queue so it can be played
  by the TTS thread.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  # Split message into arguments
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=1)
  )
  if len(args) < 2:
    return
  # ### Execution ###
  message: str = args[1]
  user: str = msg.user
  GlobalData.TTSQueue.queue_tts_message(message, user)
# ==================================================================================================


# ========== Command: chatgpt ======================================================================
def cmd_chatgpt(msg: ChatMessage) -> None:
  '''
  `chatgpt <MESSAGE>` command: Prompt ChatGPT with <MESSAGE> and send the
  response to the chat.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  # Split message into arguments
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=1)
  )
  if len(args) < 2:
    return
  # ### Execution ###
  message: str = args[1]

  # ............................................................................
  def _reply_with_answer(answer: str) -> None:
    nonlocal msg
    if msg.parent is None:
      # Remove the None part of msg.parent's typing
      raise ValueError('ChatMessage object has no reference to Bot!')
    if answer:
      answer = answer.replace('\n', ' ')
      if len(answer) > 450:
        answer = answer[:450] + "..."
      if answer.startswith('/'):
        answer = f'_ {answer}'
      msg.parent.queue_message(msg.channel, answer)
  # ............................................................................

  GlobalData.ChatGPT.queue_chat(message, _reply_with_answer)
# ==================================================================================================


# ========== Operator Command: AssignTeam ==========================================================
@operator_command
def cmd_assignTeam(msg: ChatMessage) -> None:
  '''
  `assignteam <USER> <TEAM>` command: Add <USER> to <TEAM> regardless of
  membership limitations.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  # Split message into arguments
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=2)
  )
  if len(args) < 3:
    msg.parent.send_priority_message(
      msg.channel,
      "This command needs TWO parameters: <user> <team>"
    )
    return
  user_arg: str = args[1]
  user: str = (user_arg if user_arg[:1] != '@' else user_arg[1:]).lower()
  team_name_arg: str = args[2]
  # Is Team argument valid?
  team_names: list[str] = GlobalData.Teams.get_list_of_original_names()
  if team_name_arg.lower() not in GlobalData.Teams.get_all_lowercase_names():
    # team doesn't exist
    allowed_team_names = f'''"{'" "'.join(team_names)}"'''
    msg.parent.send_priority_message(
      msg.channel,
      f"Team {team_name_arg} doesn't exist. "
      f"Team name must be one of the following: {allowed_team_names}"
    )
    return
  # ### Execution ###
  team: AbstractTeam
  for team in GlobalData.Teams.get_all_teams():
    # remove from all teams
    if user in team.members:
      team.members.remove(user)
    # assign to new team
    if team.name.lower() == team_name_arg.lower():
      team.members.add(user)
      GlobalData.Users.add(user, team)
      # ### Post-execution feedback ###
      msg.parent.send_priority_message(
        msg.channel,
        f'@{user} is now assigned to team "{team.name}"'
      )
# ==================================================================================================


# ==================================================================================================
def _blackwhitelist_pre_execution_checks(msg: ChatMessage) -> tuple[str, str]:
  '''
  Pre-execution checks for
  * addWhiteList,
  * addBlaclist
  * removeWhitelist
  * removeBlacklist
  '''
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=2)
  )
  if len(args) < 3:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, this command needs TWO parameters: <user/$group> <team>"
    )
    raise ReturnException
  user_arg: str = args[1]
  user_or_group: str = (
    user_arg if user_arg[:1] != '@' else user_arg[1:]
  ).lower()
  team_name_arg: str = args[2]
  return user_or_group, team_name_arg
# ==================================================================================================


# ========== Operator Command: AddWhitelist ========================================================
@operator_command
def cmd_addWhitelist(msg: ChatMessage) -> None:
  '''
  `addwhitelist <USER/$GROUP> <TEAM>` command:
  Add <USER/$GROUP> to <TEAM>'s whitelist.
  '''
  # ### Pre-execution checks ###
  try:
    user_or_group, team_name_arg = _blackwhitelist_pre_execution_checks(msg)
  except ReturnException:
    return

  # already checked and raised in Pre-execution checks
  assert msg.parent is not None  # nosec B101

  # ### Execution ###
  team: AbstractTeam | None
  team_names: list[str] = GlobalData.Teams.get_list_of_original_names()
  if team_name_arg.lower() not in GlobalData.Teams.get_all_lowercase_names():
    # team doesn't exist
    allowed_team_names_inner: str = '" "'.join(team_names)
    allowed_team_names: str = f'"{allowed_team_names_inner}"'
    msg.parent.send_priority_message(
      msg.channel,
      f"Team {team_name_arg} doesn't exist. "
      f"Team name must be one of the following: {allowed_team_names}"
    )
    return
  lower_case_team_dict: dict[str, AbstractTeam] = {
    k.lower(): v for k, v in GlobalData.Teams.get_all_name_team_pairs()
  }
  team = lower_case_team_dict.get(team_name_arg.lower(), None)
  if team is not None:
    # ### Execution ###
    team.user_whitelist.add_to_list(user_or_group)
    # ### Post-execution feedback ###
    msg.parent.send_priority_message(
      msg.channel,
      f'Added {user_or_group} to whitelist of team "{team.name}"'
    )
    return
# ==================================================================================================


# ========== Operator Command: RemoveWhitelist =====================================================
@operator_command
def cmd_removeWhitelist(msg: ChatMessage) -> None:
  '''
  `removewhitelist <USER/$GROUP> <TEAM>` command:
  Remove <USER/$GROUP> from <TEAM>'s whitelist.
  '''
  # ### Pre-execution checks ###
  try:
    user_or_group, team_name_arg = _blackwhitelist_pre_execution_checks(msg)
  except ReturnException:
    return

  # already checked and raised in Pre-execution checks
  assert msg.parent is not None  # nosec B101

  # ### Execution ###
  team: AbstractTeam | None
  team_names: list[str] = GlobalData.Teams.get_list_of_original_names()
  if team_name_arg.lower() not in GlobalData.Teams.get_all_lowercase_names():
    # team doesn't exist
    allowed_team_names_inner: str = '" "'.join(team_names)
    allowed_team_names: str = f'"{allowed_team_names_inner}"'
    msg.parent.send_priority_message(
      msg.channel,
      f"Team {team_name_arg} doesn't exist. "
      f"Team name must be one of the following: {allowed_team_names}"
    )
    return
  lower_case_team_dict: dict[str, AbstractTeam] = {
    k.lower(): v for k, v in GlobalData.Teams.get_all_name_team_pairs()
  }
  team = lower_case_team_dict.get(team_name_arg.lower(), None)
  if team is not None:
    # ### Execution ###
    team.user_whitelist.remove_from_list(user_or_group)
    # ### Post-execution feedback ###
    msg.parent.send_priority_message(
      msg.channel,
      f'Removed {user_or_group} from whitelist of team "{team.name}"'
    )
    return
# ==================================================================================================


# ========== Operator Command: AddBlacklist ========================================================
@operator_command
def cmd_addBlacklist(msg: ChatMessage) -> None:
  '''
  `addblacklist <USER/$GROUP> <TEAM>` command:
  Add <USER/$GROUP> to <TEAM>'s blacklist.
  '''
  # ### Pre-execution checks ###
  try:
    user_or_group, team_name_arg = _blackwhitelist_pre_execution_checks(msg)
  except ReturnException:
    return

  # already checked and raised in Pre-execution checks
  assert msg.parent is not None  # nosec B101

  # ### Execution ###
  team: AbstractTeam | None
  team_names: list[str] = GlobalData.Teams.get_list_of_original_names()
  if team_name_arg.lower() not in GlobalData.Teams.get_all_lowercase_names():
    # team doesn't exist
    allowed_team_names_inner: str = '" "'.join(team_names)
    allowed_team_names: str = f'"{allowed_team_names_inner}"'
    msg.parent.send_priority_message(
      msg.channel,
      f"Team {team_name_arg} doesn't exist. "
      f"Team name must be one of the following: {allowed_team_names}"
    )
    return
  lower_case_team_dict: dict[str, AbstractTeam] = {
    k.lower(): v for k, v in GlobalData.Teams.get_all_name_team_pairs()
  }
  team = lower_case_team_dict.get(team_name_arg.lower(), None)
  if team is not None:
    # ### Execution ###
    team.user_blacklist.add_to_list(user_or_group)
    # ### Post-execution feedback ###
    msg.parent.send_priority_message(
      msg.channel,
      f'Added {user_or_group} to blacklist of team "{team.name}"'
    )
    return
# ==================================================================================================


# ========== Operator Command: RemoveBlacklist =====================================================
@operator_command
def cmd_removeBlacklist(msg: ChatMessage) -> None:
  '''
  `removeblacklist <USER/$GROUP> <TEAM>` command:
  Remove <USER/$GROUP> from <TEAM>'s blacklist.
  '''
  # ### Pre-execution checks ###
  try:
    user_or_group, team_name_arg = _blackwhitelist_pre_execution_checks(msg)
  except ReturnException:
    return

  # already checked and raised in Pre-execution checks
  assert msg.parent is not None  # nosec B101

  # ### Execution ###
  team: AbstractTeam | None
  team_names: list[str] = GlobalData.Teams.get_list_of_original_names()
  if team_name_arg.lower() not in GlobalData.Teams.get_all_lowercase_names():
    # team doesn't exist
    allowed_team_names_inner: str = '" "'.join(team_names)
    allowed_team_names: str = f'"{allowed_team_names_inner}"'
    msg.parent.send_priority_message(
      msg.channel,
      f"Team {team_name_arg} doesn't exist. "
      f"Team name must be one of the following: {allowed_team_names}"
    )
    return
  lower_case_team_dict: dict[str, AbstractTeam] = {
    k.lower(): v for k, v in GlobalData.Teams.get_all_name_team_pairs()
  }
  team = lower_case_team_dict.get(team_name_arg.lower(), None)
  if team is not None:
    # ### Execution ###
    team.user_blacklist.remove_from_list(user_or_group)
    # ### Post-execution feedback ###
    msg.parent.send_priority_message(
      msg.channel,
      f'Removed {user_or_group} from blacklist of team "{team.name}"'
    )
    return
# ==================================================================================================


# ========== Operator Command: ClearTeams ==========================================================
@operator_command
def cmd_clearTeams(msg: ChatMessage) -> None:
  '''
  `clearteams` command: Allow users with operator privileges to
  remove all users from all teams.
  '''
  clear_team_members()
# ==================================================================================================


# ========== Operator Command: AddMacro ============================================================
@operator_command
def cmd_addMacro(msg: ChatMessage) -> None:
  '''
  Try adding a macro to all Actionsets
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=2)
  )
  if len(args) < 3:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, this command needs TWO parameters: "
      "<macro_name> <macro contents...>"
    )
    return
  macro_name_arg: str = args[1]
  # Check for macro_name conformity
  if not valid_macro_name(msg, macro_name_arg):
    return
  # ### Execution ###
  results: dict[str, tuple[bool, bool]] = {
    team.name: (team.actionset.add_macro(msg), team.hidden)
    for team in GlobalData.Teams.get_all_teams()
  }
  # ### Post-execution feedback ###
  successes = [
    name for name, res in results.items() if res[0] and not res[1]
  ]
  failures = [
    name for name, res in results.items() if not res[0] and not res[1]
  ]
  message: str
  if successes and failures:
    message = (
      f"Added macro \"{macro_name_arg}\" for Teams[{len(successes)}]: "
      f"{', '.join(successes)}; "
      f"Not added for Teams[{len(failures)}]: {', '.join(failures)};"
    )
  elif successes:
    message = (
      f"Added macro \"{macro_name_arg}\" for Teams[{len(successes)}]: "
      f"{', '.join(successes)}"
    )
  else:
    message = f"Failed to add macro \"{macro_name_arg}\" to any team."
  thread_print(f"addMacro: {message}")
  queue_long_message(msg, message, "addMacro")
# ==================================================================================================


# ========== Operator Command: ChangeMacro =========================================================
@operator_command
def cmd_changeMacro(msg: ChatMessage) -> None:
  '''
  Try changing a macro in all Actionsets
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=2)
  )
  if len(args) < 3:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, this command needs TWO parameters: "
      "<macro_name> <macro contents...>"
    )
    return
  macro_name_arg: str = args[1]
  # Check for macro_name conformity
  if not valid_macro_name(msg, macro_name_arg):
    return
  # ### Execution ###
  results: dict[str, tuple[bool, bool]] = {
    team.name: (team.actionset.change_macro(msg), team.hidden)
    for team in GlobalData.Teams.get_all_teams()
  }
  # ### Post-execution feedback ###
  successes = [
    name for name, res in results.items() if res[0] and not res[1]
  ]
  failures = [
    name for name, res in results.items() if not res[0] and not res[1]
  ]
  message: str
  if successes and failures:
    message = (
      f"Changed macro \"{macro_name_arg}\" for Teams[{len(successes)}]: "
      f"{', '.join(successes)}; "
      f"Not changed for Teams[{len(failures)}]: {', '.join(failures)};"
    )
  elif successes:
    message = (
      f"Changed macro \"{macro_name_arg}\" for Teams[{len(successes)}]: "
      f"{', '.join(successes)}"
    )
  else:
    message = f"Failed to change macro \"{macro_name_arg}\" to any team."
  thread_print(f"changeMacro: {message}")
  queue_long_message(msg, message, "changeMacro")
# ==================================================================================================


# ========== Operator Command: RemoveMacro =========================================================
@operator_command
def cmd_removeMacro(msg: ChatMessage) -> None:
  '''
  Try removing a macro in all Actionsets
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=2)
  )
  if len(args) < 2:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, this command needs ONE parameter: "
      "<macro_name>"
    )
    return
  macro_name_arg: str = args[1]
  # Check for macro_name conformity
  if not valid_macro_name(msg, macro_name_arg):
    return
  # ### Execution ###
  results: dict[str, tuple[bool, bool]] = {
    team.name: (team.actionset.remove_macro(msg), team.hidden)
    for team in GlobalData.Teams.get_all_teams()
  }
  # ### Post-execution feedback ###
  successes = [
    name for name, res in results.items() if res[0] and not res[1]
  ]
  failures = [
    name for name, res in results.items() if not res[0] and not res[1]
  ]
  message: str
  if successes and failures:
    message = (
      f"Removed macro \"{macro_name_arg}\" for Teams[{len(successes)}]: "
      f"{', '.join(successes)}; "
      f"Not removed for Teams[{len(failures)}]: {', '.join(failures)};"
    )
  elif successes:
    message = (
      f"Removed macro \"{macro_name_arg}\" for Teams[{len(successes)}]: "
      f"{', '.join(successes)}"
    )
  else:
    message = f"Failed to remove macro \"{macro_name_arg}\" from any team."
  thread_print(f"removeMacro: {message}")
  queue_long_message(msg, message, "removeMacro")
# ==================================================================================================


# ========== Operator Command: ReloadMacros ========================================================
@operator_command
def cmd_reloadMacros(msg: ChatMessage) -> None:
  '''
  Try reloading macros for given team.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=1)
  )
  if len(args) < 2:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, this command needs ONE parameter: "
      "<team_name>"
    )
    return
  team_name_arg: str = args[1]
  team: AbstractTeam | None = GlobalData.Teams.get_by_name(team_name_arg)
  if team is None:
    msg.parent.send_priority_message(
      msg.channel,
      f'@{msg.user}, no team found with name "{team_name_arg}"'
    )
    return
  # ### Execution ###
  team.actionset.reload_macros()
  # ### Post-execution feedback ###
  thread_print(f"reloadMacro: {team.name}")
  if not team.hidden:
    msg.parent.send_priority_message(
      msg.channel,
      f"Reloaded macros for team {team.name}"
    )
# ==================================================================================================


# ========== Operator Command: ReloadAllMacros =====================================================
@operator_command
def cmd_reloadAllMacros(msg: ChatMessage) -> None:
  '''
  Try reloading macros for given team.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  # ### Execution ###
  results: dict[str, tuple[bool, bool]] = {
    team.name: (team.actionset.reload_macros(), team.hidden)
    for team in GlobalData.Teams.get_all_teams()
  }
  # ### Post-execution feedback ###
  successes = [
    name for name, res in results.items() if res[0] and not res[1]
  ]
  failures = [
    name for name, res in results.items() if not res[0] and not res[1]
  ]
  message: str
  if successes and failures:
    message = (
      f"Reloaded macros for Teams[{len(successes)}]: {', '.join(successes)}; "
      f"Not reloaded for Teams[{len(failures)}]: {', '.join(failures)};"
    )
  elif successes:
    message = (
      f"Reloaded macros for Teams[{len(successes)}]: {', '.join(successes)}"
    )
  else:
    message = "Failed to reload any macros."
  thread_print(f"reloadAllMacros: {message}")
  queue_long_message(msg, message, "reloadAllMacros")
# ==================================================================================================


# ========== Operator Command: SaveSnapshot ========================================================
@operator_command
def cmd_saveSnapshot(msg: ChatMessage) -> None:
  '''
  Save current runtime data in a snapshot file to be able to easily restore
  that data later after a program restart.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=1)
  )
  filename: str = '' if len(args) < 2 else args[1]
  if not SNAPSHOT_NAME_REGEX.match(filename):
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, invalid filename! Only simple characters allowed: "
      f"{SNAPSHOT_NAME_REGEX.pattern}"
    )
    return
  if len(filename) > 100:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, filename too long! Please keep it under 100 characters!"
    )
    return
  # ### Execution ###
  try:
    saved_filename: str = save_snapshot(filename)
  except Exception:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, failed to save snapshot!"
    )
    return
  # ### Post-execution feedback ###
  msg.parent.send_priority_message(
    msg.channel,
    f"@{msg.user}, Saved snapshot as {saved_filename}"
  )
# ==================================================================================================


# ========== Operator Command: LoadSnapshot ========================================================
@operator_command
def cmd_loadSnapshot(msg: ChatMessage) -> None:
  '''
  Load runtime data from a snapshot file and replace current runtime data.
  '''
  # ### Pre-execution checks ###
  if msg.parent is None:
    # Remove the None part of msg.parent's typing
    raise ValueError('ChatMessage object has no reference to Bot!')
  args: Sequence[str] = (
    GlobalData.Prefix.Command.split_message(msg, maxsplit=1)
  )
  if len(args) < 2:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, this command needs ONE parameter: "
      "<snapshot_name>"
    )
    return
  filename: str = args[1]
  # ### Execution ###
  try:
    load_snapshot(filename)
  # ### Post-execution feedback ###
  except OSError:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, can't find snapshot with name {filename}"
    )
  except Exception:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, failed to save snapshot!"
    )
  else:
    msg.parent.send_priority_message(
      msg.channel,
      f"@{msg.user}, Loaded snapshot from {filename}"
    )
# ==================================================================================================


# ********** Delegation function *******************************************************************
def handle_command(msg: ChatMessage) -> None:
  '''
  Execute the relevant command function if the message contains a valid command.
  '''
  if GlobalData.Prefix.Command.message_is_command(msg):
    args: list[str] = GlobalData.Prefix.Command.split_message(msg)
    if len(args) == 0:
      return
    function: Callable[[ChatMessage], None] | None
    function = (_cmd2func_lookup_dict.get(args[0].lower()))
    if function is not None:
      GlobalData.Session.Chat.log_command_message(msg)
      function(msg)
# **************************************************************************************************


# ********** Limit available commands function *****************************************************
def set_available_commands(
  mode: Literal['all', 'whitelist', 'blacklist', 'none'],
  *,
  whitelist: list[str] | None = None,
  blacklist: list[str] | None = None
) -> None:
  '''
  Modify the lookup dict to only allow commands that the user specified in
  config.
  '''
  _cmd2func_lookup_dict.clear()
  match mode:
    case 'all':
      _cmd2func_lookup_dict.update(_raw_cmd2func_lookup_dict)
    case 'none':
      pass
    case 'whitelist':
      if whitelist is None:
        whitelist = []
      _cmd2func_lookup_dict.update({
        name: cmd for
        name, cmd in _raw_cmd2func_lookup_dict.items()
        if name in whitelist
      })
    case 'blacklist':
      if blacklist is None:
        blacklist = []
      _cmd2func_lookup_dict.update({
        name: cmd for
        name, cmd in _raw_cmd2func_lookup_dict.items()
        if name not in blacklist
      })
    case _:  # pyright: ignore[reportUnnecessaryComparison]
      raise ValueError(
        "mode argument has to be one of 'all', 'whitelist', 'blacklist', 'none'"
      )


def get_all_commands() -> list[str]:
  '''Get a list of all available commands.'''
  return list(_raw_cmd2func_lookup_dict.keys())
# **************************************************************************************************


_raw_cmd2func_lookup_dict: dict[str, Callable[[ChatMessage], None]] = {
  # normal commands
  'teams':            cmd_teams,
  'myteam':           cmd_myTeam,
  'yourteam':         cmd_yourTeam,
  'jointeam':         cmd_joinTeam,
  'leaveteam':        cmd_leaveTeam,
  'howtoplay':        cmd_howtoplay,
  'countredeems':     cmd_countRedeems,
  'tts':              cmd_tts,
  'chatgpt':          cmd_chatgpt,
  # operator commands
  'assignteam':       cmd_assignTeam,
  'addwhitelist':     cmd_addWhitelist,
  'removewhitelist':  cmd_removeWhitelist,
  'addblacklist':     cmd_addBlacklist,
  'removeblacklist':  cmd_removeBlacklist,
  'clearteams':       cmd_clearTeams,
  'addmacro':         cmd_addMacro,
  'changemacro':      cmd_changeMacro,
  'removemacro':      cmd_removeMacro,
  'reloadmacros':     cmd_reloadMacros,
  'reloadallmacros':  cmd_reloadAllMacros,
  'savesnapshot':     cmd_saveSnapshot,
  "loadsnapshot":     cmd_loadSnapshot,
}
'''
Dictionary for translating the message string to a callable function.

Don't modify directly, use `set_available_commands()` instead!
'''

_cmd2func_lookup_dict: dict[str, Callable[[ChatMessage], None]]
_cmd2func_lookup_dict = _raw_cmd2func_lookup_dict.copy()
