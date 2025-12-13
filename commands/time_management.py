import asyncio
import time
from discord.ext import commands
from features.time_keeper import TimeKeeper
from features.boss_timer import BossTimer
from features.war_timer import WarTimer
from utilities.helpers import find_boss, output_boss_timer_data, output_event_timer_data, parse_event_date_time, parse_timer_args, validate_input_for_boss, find_event, calculate_notification_time


class TimeManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.time_keeper = TimeKeeper()

    async def cog_load(self):
        if len(self.time_keeper.timers):
            for timer in self.time_keeper.timers:
                self.bot.loop.create_task(self.dispatch_notification(timer, timer.respawn_time - time.time()))

    async def dispatch_notification(self, timer, respawn_time):
        bot_config = self.bot.get_cog('BotConfig')
        channel_id = bot_config.war_channel_id if isinstance(timer, WarTimer) else bot_config.boss_hunter_role_id
        print(f'dispatch set for {timer.name} in {respawn_time / 60} minutes')
        await asyncio.sleep(respawn_time)
        self.bot.dispatch('notify_spawn', channel_id , timer)

    @commands.command()
    async def show(self, ctx):
        if len(list(filter(lambda timer: isinstance(timer, BossTimer), self.time_keeper.timers))) == 0:
            await ctx.send('No timers are running right now.')
        else:
            await ctx.send(output_boss_timer_data(self.time_keeper.timers))

    @commands.command()
    async def update_events(self, ctx):
        if len(list(filter(lambda timer: isinstance(timer, WarTimer), self.time_keeper.timers))) == 0:
            await ctx.send('No events are scheduled right now.')
        else:
            bot_config = ctx.bot.get_cog('BotConfig')
            channel = self.bot.get_channel(bot_config.war_channel_id)
            if channel is None:
                await ctx.send('War channel is not set or invalid.')
                return
            await channel.purge(limit=None)
            await channel.send(output_event_timer_data(self.time_keeper.timers))

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

        if isinstance(timer, WarTimer):
            await channel.send(f"Event '{timer.name}' is starting in 1 hour!")
            self.time_keeper.remove_timer(timer.id)
            return

        if timer.territory:
            await channel.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! {timer.territory} {timer.name} has just spawned!")
        else:
            await channel.send(f"Hey, <@&{bot_config.boss_hunter_role_id}>! {timer.name} has just spawned!")

        self.time_keeper.remove_timer(timer.id)

    async def handle_event(self, ctx, event, args):
        datetime = parse_event_date_time(args)
        if not datetime:
            await ctx.send("Invalid date format. Please use YYYYMMDDHHmm.")
            return

        if self.time_keeper.check_duplicate(event, None):
            await ctx.send(f"There is already a timer running for that event!")
        else:
            timer = WarTimer(event, datetime.timestamp())
            self.time_keeper.add_timer(timer)
            await ctx.send(f"Event '{event['name']}' scheduled for <t:{int(datetime.timestamp())}:f>")
            self.bot.loop.create_task(self.dispatch_notification(timer, calculate_notification_time(timer)))

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

        if self.time_keeper.check_duplicate(boss, territory):
            await ctx.send(f"There is already a timer running for that boss!")
        else:
            timer = BossTimer(boss, int(time.time()), territory, offset)
            self.time_keeper.add_timer(timer)
            await ctx.send(output_boss_timer_data(timer))
            self.bot.loop.create_task(self.dispatch_notification(timer, (boss['time'] - offset) * 60))