import time
from datetime import datetime
from discord.ext import commands
from config.constants import admins, bosses, events, Territories
from models.boss_timer import BossTimer
from models.war_timer import WarTimer

class NotBotOwner(commands.CheckFailure):
    ...

def to_upper(arg):
    return arg.upper()

def require_bot_owner():
    async def predicate(ctx):
        if ctx.author.name not in admins:
            raise NotBotOwner('You are not my owner!')
        return True
    return commands.check(predicate)


def find_boss(key):
    result = None
    for boss in bosses:
        if boss["key"] == key.lower() or boss["name"].lower() == key.lower():
            result = boss

    return result

def find_event(key):
    result = None
    for event in events:
        if event["key"] == key.lower() or event["name"].lower() == key.lower():
            result = event
    return result


def validate_input_for_boss(boss, territory):

    if boss['map'] != Territories.Both:
        return True

    if territory == '' or territory is None:
        return False

    if territory.upper() not in ['ANI', 'BCU']:
        return False

    return True

def output_boss_timer_data(timer_data):
    if isinstance(timer_data, list):
        return f"".join(
            f"`[{timer.id}]` {timer.name} {timer.territory if timer.territory else ""}\n"
            f"spawns <t:{timer.due_time}:R>\n"
            f"on <t:{timer.due_time}:f>\n"
            f"\n"
            # filter out event timers, we only want boss timers here
            for timer in list(filter(lambda timer: isinstance(timer, BossTimer), timer_data)))
    else:
        return (
            f"`[{timer_data.id}]` {timer_data.name} {timer_data.territory if timer_data.territory else ""}\n"
            f"started: <t:{timer_data.start_time}:f>\n"
            f"spawns: <t:{timer_data.due_time}:f>\n"
            f"<t:{timer_data.due_time}:R>\n"
        )
    
def output_event_timer_data(timer_data):
    return f"".join(
        f"`[{timer.id}]` {timer.name} - <t:{timer.due_time}:f>\n"
        f"starts: <t:{timer.due_time}:R>\n"
        f"\n"
        # filter out boss timers, we only want event timers here
        for timer in list(filter(lambda timer: isinstance(timer, WarTimer), timer_data)))

def create_members_table(member_data):

    if not member_data:
        return ""

    # Ensure string values and compute column widths (cap name width for readability)
    names = [str(member.name) for member in member_data]
    level_vals = [str(member.level) for member in member_data]
    gear_vals = [member.gear for member in member_data]
    fame_vals = [str(member.fame) for member in member_data]
    fame_diff_vals = [str(member.fame_diff) for member in member_data]

    name_w = max(4, min(30, max(len(n) for n in names)))
    lvl_w = max(3, max(len(v) for v in level_vals))
    gear_w = max(4, max(len(v) for v in gear_vals))
    fame_w = max(4, max(len(v) for v in fame_vals))
    fame_diff_w = max(2, max(len(v) for v in fame_diff_vals))

    # Header and separator
    header = f"{'Name':<{name_w}} | {'Lvl':^{lvl_w}} | {'Gear':^{gear_w}} | {'Fame':>{fame_w}} | {'Diff':>{fame_diff_w}}"
    sep = '-' * len(header)

    # Rows
    rows = '\n'.join(
        f"{names[i]:<{name_w}} | {level_vals[i]:^{lvl_w}} | {gear_vals[i]:^{gear_w}} | {fame_vals[i]:>{fame_w}} | {fame_diff_vals[i]:>{fame_diff_w}}"
        for i in range(len(member_data))
    )

    table = f"{header}\n{sep}\n{rows}"

    return table

def calculate_member_fame_diff(current, previous):
    """
    Compute fame differences for a list of BrigMember instances.

    - `current` and `previous` are lists of `BrigMember` objects.
    - For each member in `current`, set `member.fame_diff` to:
        current.fame - previous.fame (if a previous member with the same name exists)
        otherwise: current.fame (treat previous as 0)
    - Matching is done case-insensitively on `member.name` (stripped).
    - Returns the `current` list (with fame_diff set).
    """
    if len(previous) == 0:
        return current

    # Build a lookup by normalized name for previous members
    prev_map = {}
    for p in previous:
        key = str(p.name).strip().lower()
        prev_map[key] = p

    # Compute fame_diff for each current member
    for c in current:
        key = str(c.name).strip().lower()
        prev = prev_map.get(key)
        if prev is not None:
            c.fame_diff = int(c.fame) - int(prev.fame)

    # sort members based on fame_diff, desc
    current.sort(key=lambda m: getattr(m, 'fame_diff', 0), reverse=True)

    return current

def calculate_brig_fame_diff(current, previous):
    """
    Compute fame differences for a list of Brigade instances.

    - `current` and `previous` are lists of `Brigade` objects.
    - For each brigade in `current`, set `brigade.fame_diff` to:
        current.total_fames - previous.total_fames (if a previous brigade with the same name exists)
        otherwise: 0 (default)
    - Matching is done on `brigade.name`.
    - Returns the `current` list sorted by monthly_fame descending (with fame_diff set).
    """
    if len(previous) == 0:
        return sorted(current, key=lambda b: b.monthly_fame, reverse=True)

    # Build a lookup by name for previous brigades
    prev_map = {}
    for p in previous:
        prev_map[p.name] = p

    # Compute fame_diff for each current brigade
    for c in current:
        prev = prev_map.get(c.name)
        if prev is not None:
            c.fame_diff = int(c.total_fame) - int(prev.total_fames)

    # Sort by monthly_fame descending
    return sorted(current, key=lambda b: b.monthly_fame, reverse=True)


def create_brigs_table(brig_data):
    if not brig_data:
        return ""

    nation_mapping = {
        2: 'BCU',
        4: 'ANI'
    }
    # Extract and convert values from Brigade objects
    names = [brig.name for brig in brig_data]
    nation_codes = [int(brig.nation) for brig in brig_data]
    nation_vals = [nation_mapping.get(code, "UNKNOWN") for code in nation_codes]
    total_fame_vals = [str(brig.total_fame) for brig in brig_data]
    monthly_fame_vals = [str(brig.monthly_fame) for brig in brig_data]
    fame_diff_vals = [str(brig.fame_diff) for brig in brig_data]

    name_w = max(4, min(30, max(len(n) for n in names)))
    nation_w = 7
    total_fame_w = 7
    monthly_fame_w = 7
    fame_diff_w = 6

    # Header and separator
    header = f"{'Brigade - Monthly':<{name_w}} | {'Nation':^{nation_w}} | {'Total':^{total_fame_w}} | {'Monthly':^{monthly_fame_w}} | {'Diff':^{fame_diff_w}}"
    sep = '-' * len(header)

    # Rows
    rows = '\n'.join(
        f"{names[i]:<{name_w}} | {nation_vals[i]:^{nation_w}} | {total_fame_vals[i]:^{total_fame_w}} | {monthly_fame_vals[i]:^{monthly_fame_w}} | {fame_diff_vals[i]:^{fame_diff_w}}"
        for i in range(len(brig_data))
    )

    table = f"{header}\n{sep}\n{rows}"

    return table

def make_boss_list():
    boss_list = f"```{"".join(f'{boss['name']} - {boss['key']} - {boss['time']}\n' for boss in bosses)}```"

    return boss_list

def parse_event_date_time(args):
    if not len(args):
        return None
    try:
        return datetime.strptime(args[0], "%Y%m%d%H%M")
    except ValueError:
        return None

def parse_timer_args(boss, args):
    number_of_args = len(args)

    if number_of_args < 2:
        return {
            "territory": args[0] if number_of_args and boss['map'] == Territories.Both else None,
            "offset": args[0] if number_of_args and boss['map'] != Territories.Both else 0
        }
    else:
        return {
            "territory": args[0],
            "offset": args[1]
        }
    
def calculate_notification_time(timer):
    return (int(timer.due_time) - int(time.time())) - 3600  # notify 1 hour before start
