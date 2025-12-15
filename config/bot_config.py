from discord.ext import commands

class BotConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.boss_hunter_role_id = 0
        self.warrior_role_id = 0
        self.war_channel_id = 0
        self.boss_channel_id = 0

# IDs must be ints, otherwise discord will not find the channel or role
    @property
    def boss_hunter_role_id(self) -> int:
        return self._boss_hunter_role_id

    @property
    def warrior_role_id(self) -> int:
        return self._warrior_role_id

    @property
    def war_channel_id(self) -> int:
        return self._war_channel_id

    @property
    def boss_channel_id(self) -> int:
        return self._boss_channel_id

    @boss_hunter_role_id.setter
    def boss_hunter_role_id(self, value):
        self._boss_hunter_role_id = int(value)

    @warrior_role_id.setter
    def warrior_role_id(self, value):
        self._warrior_role_id = int(value)

    @war_channel_id.setter
    def war_channel_id(self, value):
        self._war_channel_id = int(value)

    @boss_channel_id.setter
    def boss_channel_id(self, value):
        self._boss_channel_id = int(value)