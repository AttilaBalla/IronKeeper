from discord.ext import commands

class BotConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.boss_hunter_role_id = 0
        self.warrior_role_id = 0
        self.channel_id = 0