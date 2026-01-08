from discord.ext import commands, tasks
import datetime
from utilities.helpers import create_members_table, calculate_member_fame_diff, calculate_brig_fame_diff, \
    create_brigs_table, require_bot_owner
from utilities.web_requests import request_rankings_data


class BrigStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # list of BrigMember objects
        self.previous_member_stats = []
        self.current_member_stats = []
        self.previous_brig_stats = []
        self.current_brig_stats = []

        self.stat_update_scheduler.start()

    def cog_unload(self):
        self.stat_update_scheduler.cancel()

    async def update_stats(self):
        # get stat channel ID
        bot_config = self.bot.get_cog('BotConfig')
        channel = self.bot.get_channel(bot_config.stat_channel_id)
        # get most recent stats
        fresh_stats = request_rankings_data()
        # calc fame difference for each member and for brig based on previous stats
        self.current_member_stats = calculate_member_fame_diff(fresh_stats["members"], self.previous_member_stats)
        self.current_brig_stats = calculate_brig_fame_diff(fresh_stats["brigs"], self.previous_brig_stats)
        # create output format
        members_table = create_members_table(self.current_member_stats)
        brigs_table = create_brigs_table(self.current_brig_stats)
        if not members_table:
            await channel.send('No brig members found.')
        else:
            await channel.send(f"```{members_table}```")
        if not brigs_table:
            await channel.send('No brig data found.')
        else:
            await channel.send(f"```{brigs_table}```")

        # set current stats as previous
        self.previous_member_stats = self.current_member_stats
        self.previous_brig_stats = self.current_brig_stats

    @tasks.loop(time=datetime.time(hour=12, minute=0))
    async def stat_update_scheduler(self):
        if datetime.datetime.now().weekday() == 0:  # Monday
            await self.update_stats()

    @require_bot_owner()
    @commands.command()
    async def stats(self, ctx):
        await self.update_stats()