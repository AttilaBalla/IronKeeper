from discord.ext import commands, tasks
import datetime

from config.constants import CSV_HEADERS_MEMBER_STATS, CSV_HEADERS_BRIG_STATS
from models.brig_member import BrigMember
from models.brigade import Brigade
from utilities.helpers import create_members_table, calculate_member_fame_diff, calculate_brig_fame_diff, \
    create_brigs_table, require_bot_owner
from utilities.persistence import save_data_to_csv, load_from_csv
from utilities.web_requests import request_rankings_data


class BrigStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # list of BrigMember objects
        self.previous_member_stats = []
        self.current_member_stats = []
        self.previous_brig_stats = []
        self.current_brig_stats = []
        self.member_persistence_path = 'data/member_stats.csv'
        self.brig_persistence_path = 'data/brig_stats.csv'

        self.stat_update_scheduler.start()

    def cog_load(self):
        self.load_members_from_csv()
        self.load_brig_stats_from_csv()

    def cog_unload(self):
        self.stat_update_scheduler.cancel()

    def load_members_from_csv(self):
        print(f'Trying to load brig member stats from {self.member_persistence_path}')

        def member_factory(row):
            return BrigMember.from_csv_row(row)

        members = load_from_csv(self.member_persistence_path, CSV_HEADERS_MEMBER_STATS, member_factory)
        self.previous_member_stats = members

    def load_brig_stats_from_csv(self):
        print(f'Trying to load brigade stats from {self.brig_persistence_path}')

        def brigade_factory(row):
            return Brigade.from_csv_row(row)

        brigades = load_from_csv(self.brig_persistence_path, CSV_HEADERS_BRIG_STATS, brigade_factory)
        self.previous_brig_stats = brigades

    async def update_stats(self):
        # get stat channel ID
        bot_config = self.bot.get_cog('BotConfig')
        channel = self.bot.get_channel(bot_config.stat_channel_id)
        # get most recent stats
        fresh_stats = request_rankings_data(bot_config.brigade)
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
        # save stats to CSV
        save_data_to_csv(self.current_member_stats, CSV_HEADERS_MEMBER_STATS, 'member_stats', self.member_persistence_path)
        save_data_to_csv(self.current_brig_stats, CSV_HEADERS_BRIG_STATS, 'brig_stats', self.brig_persistence_path)

    @tasks.loop(time=datetime.time(hour=12, minute=0))
    async def stat_update_scheduler(self):
        if datetime.datetime.now().weekday() == 0:  # Monday
            await self.update_stats()

    @require_bot_owner()
    @commands.command()
    async def stats(self, ctx):
        await self.update_stats()