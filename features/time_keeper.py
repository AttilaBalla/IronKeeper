from config.constants import Territories, CSV_HEADERS_TIMERS
from models.boss_timer import BossTimer
from models.war_timer import WarTimer
from utilities.persistence import load_from_csv, save_data_to_csv
import time


class TimeKeeper:

    def __init__(self):
        self.timers = []
        self.counter = 0
        self.persistence_path = 'data/timers.csv'

    def exists(self, timer_id):
        for timer in self.timers:
            if timer.id == timer_id:
                return True

        return False

    def add_timer(self, timer):
        timer.id = self.counter
        self.counter += 1
        self.timers.append(timer)

    def find_timer(self, timer_id):
        for timer in self.timers:
            if timer.id == int(timer_id):
                return timer

        return None

    def remove_timer(self, timer_id):
        timer = self.find_timer(timer_id)
        if timer:
            self.timers.remove(timer)
        else:
            print(f'Could not remove timer, ID {timer_id} does not exist!')

    def check_duplicate(self, timer, territory):
        if territory is not None and timer['map'] == Territories.Both:
            for item in self.timers:
                if item.key == timer['key'] and item.territory == territory.upper():
                    return True
        else:
            for item in self.timers:
                if timer['key'] == item.key:
                    return True

        return False

    def save_timer_state(self):
        print(f'Saving current timers to {self.persistence_path}')
        save_data_to_csv(self.timers, CSV_HEADERS_TIMERS, 'timers', self.persistence_path)

    def load_timers_from_csv(self):
        """Load boss/war timers from CSV file and add to TimeKeeper.
        Returns:
            Number of timers loaded
        """
        print(f'Trying to timers from {self.persistence_path}')
        def timer_factory(row):
            timer_type = (row.get('timer_type') or '').lower()
            if timer_type == 'boss':
                return BossTimer.from_csv_row(row)
            elif timer_type == 'war':
                return WarTimer.from_csv_row(row)
            else:
                raise ValueError(f"Unknown timer type: {timer_type}")

        def timer_filter(row):
            # Skip expired timers: if due_time - current_time < 1, timer is in the past
            return int(row['due_time']) - int(time.time()) >= 1

        timers = load_from_csv(self.persistence_path, CSV_HEADERS_TIMERS, timer_factory, timer_filter)

        for timer in timers:
            self.add_timer(timer)