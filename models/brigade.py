class Brigade:
    def __init__(self, name, monthly_fame, nation=0, total_fame=0):
        self.name = name
        self.nation = int(nation)
        self.total_fame = int(total_fame)
        self.monthly_fame = int(monthly_fame)
        self.fame_diff = 0

    def to_csv_row(self):
        return {
            'name': self.name,
            'nation': self.nation,
            'total_fame': self.total_fame,
            'monthly_fame': self.monthly_fame,
            'fame_diff': self.fame_diff
        }

    @classmethod
    def from_csv_row(cls, row):
        """Create a Brigade from a CSV row mapping."""
        inst = cls(
            name=row.get('name') or '',
            monthly_fame=row.get('monthly_fame') or 0,
            nation=row.get('nation') or 0,
            total_fame=row.get('total_fame') or 0
        )
        # Set fame_diff from CSV if present
        if row.get('fame_diff'):
            inst.fame_diff = int(row.get('fame_diff'))
        return inst
