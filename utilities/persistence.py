import os
import csv
import tempfile
import time
from features.boss_timer import BossTimer
from features.war_timer import WarTimer

CSV_HEADERS = [
    'id',
    'timer_type',
    'key',
    'name',
    'start_time',
    'due_time',
    'territory',
]

def _ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def save_timers_to_csv(timers, path):
    """Save a list of timer objects to a CSV file atomically.
    Each timer object must implement a to_csv_row() -> dict method that returns
    a mapping of CSV column name to serializable value.
    """
    if os.path.exists(path):
        os.remove(path)
    else:
        print('existing file not found, generating a new one.')

    _ensure_dir(path)
    tmp_fd, tmp_path = tempfile.mkstemp(prefix='timers-', suffix='.csv', dir=os.path.dirname(path) or '.')
    try:
        with os.fdopen(tmp_fd, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            for t in timers:
                row = t.to_csv_row()
                writer.writerow(row)
        # On success, atomically replace
        os.replace(tmp_path, path)
    except Exception as ex:
        print('An error occured when writing the csv')
        print(ex)
        # If anything goes wrong, remove temp file and re-raise
        try:
            os.remove(tmp_path)
        except Exception:
            print('An error occured :(')
            pass


def load_timers_from_csv(path, time_keeper):
    """Load timers from CSV into the provided TimeKeeper instance.
    - path: CSV file path
    - time_keeper: instance of TimeKeeper (features.time_keeper.TimeKeeper)
    Returns the number of timers loaded.
    """
    if not os.path.exists(path):
        return 0

    loaded = 0
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, raw in enumerate(reader, start=1):
            try:
                timer_type = (raw.get('timer_type') or '').lower()
                row = {k: raw.get(k, '') for k in CSV_HEADERS}
                # subtract the current time from the respawn time, if result is negative, timer is in the past
                if int(row['due_time']) - int(time.time()) < 1:
                    continue
                if timer_type == 'boss':
                    t = BossTimer.from_csv_row(row)
                elif timer_type == 'war':
                    t = WarTimer.from_csv_row(row)
                else:
                    # Unknown timer type -> skip
                    continue

                time_keeper.add_timer(t)
                loaded += 1
            except Exception as error:
                print(f'an error occurred when loading timers from csv: {error}')
                # Skip malformed rows
                continue

    return loaded
