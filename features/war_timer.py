class WarTimer:

    def __init__(self, event, start_date_time):
        self.id = None
        self.key = event['key']
        self.name = event['name']
        self.start_date_time = int(start_date_time)
        
        