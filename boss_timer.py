import time

class BossTimer:

    def __init__(self, boss, territory, time_offset):
        self.id = None
        self.start_time = int(time.time())
        self.respawn_time = self.start_time + (int(boss['time']) - time_offset) * 60
        self.name = boss['name']
        self.key = boss['key']
        self.territory = territory.upper() if territory else None

    def get_elapsed_time(self):
        return round(time.time() - self.start_time, 2)