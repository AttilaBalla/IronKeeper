import discord
import typing
import asyncio
from discord.ext import commands
from secrets import token
from boss_timer import BossTimer
from bot_config import BotConfig
from time_keeper import TimeKeeper
from helpers import (
    require_bot_owner,
    NotBotOwner,
    find_boss,
    validate_input_for_boss,
    output_timer_data, make_boss_list, parse_timer_args
)

def init():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    time_keeper = TimeKeeper()
    bot_config = BotConfig()

    async def dispatch_spawn_notification(ctx, timer, time):
        print(f'dispatch set for {timer.name} in {time / 60} minutes')
        await asyncio.sleep(time)
        bot.dispatch('notify_spawn', ctx, timer)


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
    # format is !t [key] +[nation] *[offset]
    @bot.command()
    async def t(ctx, key, *args):
        boss = find_boss(key)

        if boss is None:
            await ctx.send('Nothing found for that key.')
            return

        # we have to handle inputs without nation BUT with offset
        # as well as inputs with both nation and offset
        parsed_args = parse_timer_args(boss, args)
        territory = parsed_args["territory"]
        offset = parsed_args["offset"]

        is_valid = validate_input_for_boss(boss, territory)

        if not is_valid:
            await ctx.send('You need to specify ANI or BCU side for that boss!')
            return

        if offset:
            try:
                offset = int(offset)
            except ValueError:
                await ctx.send("An error occurred: Offset has to be a number!")
                return

        if offset > boss['time'] - 1:
            await ctx.send('That offset is too large and would make no sense!')
            return

        is_duplicate = time_keeper.check_duplicate(boss, territory)

        if is_duplicate:
            await ctx.send(f"There is already a timer running for that boss!")
        else:
            timer = BossTimer(boss, territory, offset)
            time_keeper.add_timer(timer)
            await ctx.send(output_timer_data(timer))
            await dispatch_spawn_notification(ctx, timer, (boss['time'] - offset) * 60)

    #delete a timer
    @bot.command()
    async def dt(ctx, timer_id):
        if not timer_id:
            await ctx.send("You need to provide a timer ID to delete a timer!")
            return
        try:
            time_keeper.remove_timer(timer_id)
        except ValueError:
            await ctx.send('An error occurred: Command input contains invalid value, expecting `[id]`')

        await ctx.send(f"Timer with ID [{timer_id}] has been deleted.")

    # add role to member
    @bot.command()
    async def hunt(ctx):
        if not bot_config.boss_hunter_role_id:
            await ctx.send('The Boss Hunter Role ID has not been set. Set it by using ```!set_role [id]```')
            return

        role = ctx.guild.get_role(bot_config.boss_hunter_role_id)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author} has been added to Boss Hunters!")
        else:
            await ctx.send("Error: No role was found for that ID that is set.")


    # remove role from member
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

    @require_bot_owner()
    @bot.command()
    async def test(ctx, key, *args):
        print(args)
        await ctx.send(args)


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
    async def on_notify_spawn(ctx, timer):

        if not time_keeper.exists(timer.id):
            print(f'Tried to notify for [{timer.id}] {timer.name} but it does not exist anymore.')
            return

        if timer.territory:
            await ctx.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! {timer.territory} {timer.name} has just spawned!")
        else:
            await ctx.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! {timer.name} has just spawned!")

        time_keeper.remove_timer(timer.id)


    bot.run(token)

if __name__ == "__main__":
    init()

