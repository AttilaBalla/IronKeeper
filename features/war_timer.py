import time

class WarTimer:

    def __init__(self, event, start_date_time):
        self.id = None
        self.key = event['key']
        self.name = event['name']
        self.start_date_time = int(start_date_time)
        self.created_at = time.time()

    def to_csv_row(self):
        return {
            'id': int(self.id) if self.id is not None else '',
            'timer_type': 'war',
            'key': self.key,
            'name': self.name,
            'start_time': self.created_at,
            'respawn_time': int(self.start_date_time),
            'territory': None,
        }

    @classmethod
    def from_csv_row(cls, row):
        try:
            id_val = int(row.get('id')) if row.get('id') not in (None, '') else None
        except Exception:
            id_val = None

        try:
            spawn_ts = int(row.get('spawn_ts') or 0)
        except Exception:
            spawn_ts = 0

        event = {
            'key': row.get('key') or '',
            'name': row.get('name') or '',
        }

        inst = cls(event, spawn_ts)
        inst.id = id_val
        return inst