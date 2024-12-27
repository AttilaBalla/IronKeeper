class BotConfig:

    def __init__(self):
        self.boss_hunter_role_id = 0
        self.channel_id = 0
        self.managed_roles = [
            {
                "name": "boss_hunter_role",
                "id": 0
            },
            {
                "name": "pvp_role",
                "id": 0
            },
        ]


    def set_role_id(self, role_id):
        self.boss_hunter_role_id = int(role_id)