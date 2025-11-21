import time
from datetime import datetime
from discord.ext import commands
from config.constants import admins, bosses, events, Territories
from features.boss_timer import BossTimer
from features.war_timer import WarTimer

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
            f"spawns: <t:{timer.respawn_time}:R>\n"
            f"\n"
            # filter out event timers, we only want boss timers here
            for timer in list(filter(lambda timer: isinstance(timer, BossTimer), timer_data)))
    else:
        return (
            f"`[{timer_data.id}]` {timer_data.name} {timer_data.territory if timer_data.territory else ""}\n"
            f"started: <t:{timer_data.start_time}:f>\n"
            f"spawns: <t:{timer_data.respawn_time}:f>\n"
            f"<t:{timer_data.respawn_time}:R>\n"
        )
    
def output_event_timer_data(timer_data):
    return f"".join(
        f"`[{timer.id}]` {timer.name} - <t:{timer.start_date_time}:f>\n"
        f"starts: <t:{timer.start_date_time}:R>\n"
        f"\n"
        # filter out boss timers, we only want event timers here
        for timer in list(filter(lambda timer: isinstance(timer, WarTimer), timer_data)))

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
    return (int(timer.start_date_time) - int(time.time())) - 3600  # notify 1 hour before start
