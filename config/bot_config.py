import os
from discord.ext import commands

class BotConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.boss_hunter_role_id = 0
        self.warrior_role_id = 0
        self.war_channel_id = 0
        self.boss_channel_id = 0

    async def cog_load(self):
        self.war_channel_id = os.getenv('WAR_CHANNEL_ID')
        self.boss_channel_id = os.getenv('BOSS_CHANNEL_ID')