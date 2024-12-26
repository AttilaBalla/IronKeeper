import discord
import typing
import asyncio
from discord.ext import commands
from boss_timer import BossTimer
from bot_config import BotConfig
from time_keeper import TimeKeeper
from helpers import (
    require_bot_owner,
    NotBotOwner,
    find_boss,
    validate_input_for_boss,
    output_timer_data, make_boss_list
)

def init():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    token = ''

    time_keeper = TimeKeeper()
    bot_config = BotConfig()

    async def dispatch_spawn_notification(ctx, boss, time, territory):
        print(f'dispatch set for {boss} in {time / 60} minutes')
        await asyncio.sleep(time)
        bot.dispatch('notify_spawn', ctx, boss, territory)


    # todo designate a channel to output information to
    @bot.command()
    async def designate(ctx):
        pass

    #list currently active timers
    @bot.command()
    async def show(ctx):
        if len(time_keeper.timers) == 0:
            await ctx.send('No timers are running right now.')
        else:
            await ctx.send(output_timer_data(time_keeper.timers))

    # register and start a new timer
    @bot.command()
    async def t(ctx, key, territory: typing.Optional[str] = ''):
        boss = find_boss(key)

        if boss is None:
            await ctx.send('Nothing found for that key.')
            return

        is_valid = validate_input_for_boss(boss, territory)

        if not is_valid:
            await ctx.send('You need to specify ANI or BCU side for that boss!')
            return

        is_duplicate = time_keeper.check_duplicate(boss, territory)

        if is_duplicate:
            await ctx.send(f"There is already a timer running for that boss!")
        else:
            timer = BossTimer(boss, territory)
            time_keeper.add_timer(timer)
            await ctx.send(output_timer_data(timer))
            await dispatch_spawn_notification(ctx, boss, boss['time'] * 60, territory)

    @bot.command()
    async def join(ctx):
        if not bot_config.boss_hunter_role_id:
            await ctx.send('The Boss Hunter Role ID has not been set. Set it by using ```!set_role [id]```')
            return

        role = ctx.guild.get_role(bot_config.boss_hunter_role_id)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author} has been added to Boss Hunters!")
        else:
            await ctx.send("Error: No role was found for that ID that is set.")



    @bot.command()
    async def leave(ctx):
        if not bot_config.boss_hunter_role_id:
            await ctx.send('The Boss Hunter Role ID has not been set. Set it by using ```!set_role [id]```')
            return

        role = ctx.guild.get_role(bot_config.boss_hunter_role_id)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author} has been removed from Boss Hunters!")
        else:
            await ctx.send("Error: No role was found for that ID that is set.")


    # kill myself
    @bot.command()
    @require_bot_owner()
    async def kill(ctx):
        await ctx.send('Shutting down... :(')
        exit()

    # set boss hunters role ID
    @bot.command()
    @require_bot_owner()
    async def set_role(ctx, role_id):
        bot_config.set_role_id(role_id)
        await ctx.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! I will notify you when bosses spawn!")

    # list the available boss data
    @bot.command()
    @require_bot_owner()
    async def boss_list(ctx):
        await ctx.send(f"`name - key - spawn time in min`")
        await ctx.send(make_boss_list())


    @bot.event
    async def on_ready():
        print(f'I have logged in as {bot.user}')

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, NotBotOwner):
            await ctx.send('I will not do that for you!')
        else:
            await ctx.send(f"An error occurred: {error}")

    @bot.event
    async def on_notify_spawn(ctx, boss, territory):
        await ctx.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! {boss['name']} has just spawned!")
        if territory:
            await ctx.send(f"Territory: {territory}")
        time_keeper.remove_timer(boss["key"])


    bot.run(token)

if __name__ == "__main__":
    init()

