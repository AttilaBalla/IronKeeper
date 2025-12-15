from config.constants import Territories
from utilities.persistence import save_timers_to_csv, load_timers_from_csv

class TimeKeeper:

    def __init__(self):
        self.timers = []
        self.counter = 0
        self.persistence_path = None

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
        save_timers_to_csv(self.timers, self.persistence_path)

    def load_from_csv(self):
        print(f'Trying to load timers from {self.persistence_path}')
        return load_timers_from_csv(self.persistence_path, self)
