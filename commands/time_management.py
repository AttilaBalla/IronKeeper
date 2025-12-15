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
                self.bot.loop.create_task(self.dispatch_notification(timer, timer.due_time - time.time()))

    async def dispatch_notification(self, timer, respawn_time):
        bot_config = self.bot.get_cog('BotConfig')
        channel_id = bot_config.war_channel_id if isinstance(timer, WarTimer) else bot_config.boss_channel_id
        print(f'dispatch set for {timer.name} in {respawn_time / 60} minutes, channel ID: {channel_id}')
        await asyncio.sleep(respawn_time)
        self.bot.dispatch("timer_expired", channel_id , timer)

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
    async def restart_timers(self, ctx):
        """Restart all currently running boss timers

        This removes the existing BossTimer instances (so previously-scheduled notification tasks won't trigger)
        and creates new timers starting at the current time. War timers are ignored.
        """
        now = int(time.time())
        restarted = 0
        # iterate over a copy because we'll be removing timers during the loop
        timers_snapshot = list(self.time_keeper.timers)

        for timer in timers_snapshot:
            if not isinstance(timer, BossTimer):
                continue

            # try to find boss definition to get canonical spawn time
            boss = find_boss(timer.key)
            if not boss:
                # can't compute new timer without boss definition; skip
                continue

            boss_time = int(boss['time'])
            # original duration that was set when the timer was created (in minutes)
            try:
                original_duration_minutes = (int(timer.due_time) - int(timer.start_time)) / 60
            except Exception:
                original_duration_minutes = boss_time

            # derive the original offset in minutes
            offset_minutes = boss_time - original_duration_minutes
            # normalize offset
            offset = int(round(offset_minutes)) if offset_minutes > 0 else 0
            if offset < 0:
                offset = 0
            if offset > boss_time - 1:
                offset = 0

            # remove old timer so its scheduled task (sleep) will be ignored by the notifier
            self.time_keeper.remove_timer(timer.id)

            # create and add a fresh timer starting now preserving territory and offset
            new_timer = BossTimer(boss, now, timer.territory, offset)
            self.time_keeper.add_timer(new_timer)

            # schedule notification for the new timer
            self.bot.loop.create_task(self.dispatch_notification(new_timer, (boss_time - offset) * 60))

            restarted += 1

        # persist the new state
        self.time_keeper.save_timer_state()
        await ctx.send(f"Restarted {restarted} boss timer(s).")
        await ctx.bot.get_command("show").invoke(ctx)


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
    async def on_timer_expired(self, channel_id, timer):
        bot_config = self.bot.get_cog('BotConfig')

        if not self.time_keeper.exists(timer.id):
            print(f'Tried to notify for [{timer.id}] {timer.name} but it does not exist anymore.')
            return
        
        channel = self.bot.get_channel(channel_id)

        if isinstance(timer, WarTimer):
            await channel.send(f"Hey <@&{bot_config.warrior_role_id}>! Event `{timer.name}` is starting in 1 hour!")
            self.time_keeper.remove_timer(timer.id)
            return

        if timer.territory:
            await channel.send(f"Hey <@&{bot_config.boss_hunter_role_id}>! {timer.territory} {timer.name} has just spawned!")
        else:
            await channel.send(f"Hey <@&{bot_config.boss_hunter_role_id}>! {timer.name} has just spawned!")

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
            await ctx.send(f"Event `{event['name']}` scheduled for <t:{int(datetime.timestamp())}:f>")
            self.bot.loop.create_task(self.dispatch_notification(timer, calculate_notification_time(timer)))
            self.time_keeper.save_timer_state()

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
            self.time_keeper.save_timer_state()