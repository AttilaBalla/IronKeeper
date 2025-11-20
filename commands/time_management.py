import asyncio
from discord.ext import commands
from features.boss_time_keeper import BossTimeKeeper
from features.boss_timer import BossTimer
from utilities.helpers import find_boss, output_timer_data, parse_timer_args, validate_input_for_boss, find_event


class TimeManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time_keeper = BossTimeKeeper()

    async def dispatch_spawn_notification(self, ctx, timer, time):
        print(f'dispatch set for {timer.name} in {time / 60} minutes by {ctx.author.name}')
        channel_id = ctx.channel.id
        await asyncio.sleep(time)
        self.bot.dispatch('notify_spawn', channel_id, timer)

    @commands.command()
    async def show(self, ctx):
        if len(self.time_keeper.timers) == 0:
            await ctx.send('No timers are running right now.')
        else:
            await ctx.send(output_timer_data(self.time_keeper.timers))

    @commands.command()
    async def t(self, ctx, key, *args):
        event = find_event(key)
        boss = None

        if event is None:
            boss = find_boss(key)

        if boss is None and event is None:
            await ctx.send('Nothing found for that key.')
            return

        if event:
            await self.handle_event(ctx, event, args)

        if boss:
            await self.handle_boss(ctx, boss, args)


    @commands.command()
    async def dt(self, ctx, timer_id):
        if not timer_id:
            await ctx.send("You need to provide a timer ID to delete a timer!")
            return
        try:
            self.time_keeper.remove_timer(timer_id)
        except ValueError:
            await ctx.send('An error occurred: Command input contains invalid value, expecting `[id]`')

        await ctx.send(f"Timer with ID [{timer_id}] has been deleted.")

    @commands.command()
    async def hunt(self, ctx):

        bot_config = self.bot.get_cog('BotConfig')

        if not bot_config.boss_hunter_role_id:
            await ctx.send('The Boss Hunter Role ID has not been set. Set it by using ```!set_role [id]```')
            return

        role = ctx.guild.get_role(bot_config.boss_hunter_role_id)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author} has been added to Boss Hunters!")
        else:
            await ctx.send("Error: No role was found for that ID that is set.")

    @commands.command()
    async def leave(self, ctx):

        bot_config = self.bot.get_cog('BotConfig')

        if not bot_config.boss_hunter_role_id:
            await ctx.send('The Boss Hunter Role ID has not been set. Set it by using ```!set_role [id]```')
            return

        role = ctx.guild.get_role(bot_config.boss_hunter_role_id)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author} has been removed from Boss Hunters!")
        else:
            await ctx.send("Error: No role was found for that ID that is set.")

    @commands.Cog.listener()
    async def on_notify_spawn(self, channel_id, timer):
        bot_config = self.bot.get_cog('BotConfig')

        if not self.time_keeper.exists(timer.id):
            print(f'Tried to notify for [{timer.id}] {timer.name} but it does not exist anymore.')
            return
        
        channel = self.bot.get_channel(channel_id)

        if timer.territory:
            await channel.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! {timer.territory} {timer.name} has just spawned!")
        else:
            await channel.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! {timer.name} has just spawned!")

        self.time_keeper.remove_timer(timer.id)

    async def handle_event(self, ctx, event, args):
        pass


    async def handle_boss(self, ctx, boss, args):

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

        is_duplicate = self.time_keeper.check_duplicate(boss, territory)

        if is_duplicate:
            await ctx.send(f"There is already a timer running for that boss!")
        else:
            timer = BossTimer(boss, territory, offset)
            self.time_keeper.add_timer(timer)
            await ctx.send(output_timer_data(timer))
            self.bot.loop.create_task(self.dispatch_spawn_notification(ctx, timer, (boss['time'] - offset) * 60))