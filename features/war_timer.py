import time

class WarTimer:

    def __init__(self, event, start_date_time):
        self.id = None
        self.start_date_time = start_date_time
        self.name = event['name']