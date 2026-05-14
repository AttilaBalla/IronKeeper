from discord.ext import commands

class BotConfig(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.brigade = "",
        self.boss_hunter_role_id = 0
        self.warrior_role_id = 0
        self.war_channel_id = 0
        self.boss_channel_id = 0
        self.stat_channel_id = 0
        self._auto_reschedule_wars = True  # Default enabled

    @property
    def brigade(self) -> str:
        return self._brigade

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

    @property
    def stat_channel_id(self) -> int:
        return self._stat_channel_id

    @brigade.setter
    def brigade(self, value):
        self._brigade = value

    @property
    def auto_reschedule_wars(self) -> bool:
        return self._auto_reschedule_wars

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

    @stat_channel_id.setter
    def stat_channel_id(self, value):
        self._stat_channel_id = int(value)

    @auto_reschedule_wars.setter
    def auto_reschedule_wars(self, value: bool):
        self._auto_reschedule_wars = value