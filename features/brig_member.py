class BrigMember:

    def __init__(self, name, level, gear, fame):
        self.name = name
        self.level = int(level)
        # assign via property setter so numeric input is converted to the string code
        self.gear = gear
        self.fame = int(fame)
        self.fame_diff = 0

    @property
    def gear(self):
        return getattr(self, '_gear', None)

    @gear.setter
    def gear(self, value):
        """Set gear from a numeric code to its letter representation.
        Assumes only these numeric inputs occur; handles string-numeric input as well.
        """
        mapping = {
            1: 'B',
            16: 'M',
            256: 'A',
            4096: 'I'
        }
        # Try to normalize the incoming value to int (in case it's a string)
        try:
            key = int(value)
        except ValueError:
            # If conversion fails, store None to indicate unknown/invalid input
            self._gear = None
            return

        self._gear = mapping.get(key)
