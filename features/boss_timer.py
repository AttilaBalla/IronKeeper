import time

class BossTimer:

    def __init__(self, boss, start_time, territory, time_offset, respawn_time=None):
        self.id = None
        self.name = boss['name']
        self.key = boss['key']
        self.start_time = start_time
        self.territory = territory.upper() if territory else None
        # if loaded from csv, respawn time is already calculated
        self.due_time = int(respawn_time) if respawn_time else self.start_time + (int(boss['time']) - time_offset) * 60

    def get_elapsed_time(self):
        return round(time.time() - self.start_time, 2)

    def to_csv_row(self):
        """Return a dict representing this timer for CSV writing."""
        return {
            'id': int(self.id) if self.id is not None else '',
            'timer_type': 'boss',
            'key': self.key,
            'name': self.name,
            'start_time': int(self.start_time),
            'due_time': int(self.due_time),
            'territory': self.territory or '',
        }

    @classmethod
    def from_csv_row(cls, row):
        """Create a BossTimer from a CSV row mapping."""
        # Reconstruct a minimal boss-like dict for constructor
        boss = {
            'key': row.get('key') or '',
            'name': row.get('name') or '',
        }
        territory = row.get('territory') or None
        inst = cls(boss, row.get('start_time'), territory, 0, row.get('due_time'))
        return inst