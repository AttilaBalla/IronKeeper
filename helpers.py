from discord.ext import commands
from constants import admins, bosses, Territories

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

def validate_input_for_boss(boss, territory):

    if boss['map'] != Territories.Both:
        return True

    if territory == '':
        return False

    if territory not in ['ANI', 'BCU']:
        return False

    return True

def output_timer_data(timer_data):

    if isinstance(timer_data, list):
        return f"".join(
            f"Timer for: {timer.name + ' ' + timer.territory}\n"
            f"started: <t:{timer.start_time}:f>\n"
            f"spawns: <t:{timer.respawn_time}:f>\n"
            f"<t:{timer.respawn_time}:R>\n"
            f"\n"
            for timer in timer_data)
    else:
        return (
            f"Timer for: {timer_data.name + ' ' + timer_data.territory}\n"
            f"started: <t:{timer_data.start_time}:f>\n"
            f"spawns: <t:{timer_data.respawn_time}:f>\n"
            f"<t:{timer_data.respawn_time}:R>\n"
        )

def make_boss_list():
    boss_list = f"```{"".join(f'{boss['name']} - {boss['key']} - {boss['time']}\n' for boss in bosses)}```"

    return boss_list
