from constants import Territories


class TimeKeeper:

    def __init__(self):
        self.timers = []

    def add_timer(self, timer):
        self.timers.append(timer)

    def remove_timer(self, key):

        for index, timer in enumerate(self.timers):
            if timer.key == key and timer.territory:
                del self.timers[index]

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

