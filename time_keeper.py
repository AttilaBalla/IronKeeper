from constants import Territories


class TimeKeeper:

    def __init__(self):
        self.timers = []
        self.counter = 0

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

    def check_duplicate(self, boss, territory):
        if boss['map'] == Territories.Both:
            for timer in self.timers:
                if timer.key == boss['key'] and timer.territory == territory:
                    return True
        else:
            for timer in self.timers:
                if timer.key == boss['key']:
                    return True

        return False

