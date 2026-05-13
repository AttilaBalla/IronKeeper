import os
import csv
import tempfile

from config.constants import CSV_HEADERS_MEMBER_STATS
from models.brigade import Brigade

def _ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def _clear_previous_file(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print('existing file not found, generating a new one.')

def save_data_to_csv(data, headers, prefix, path):
    _clear_previous_file(path)
    _ensure_dir(path)

    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.csv', prefix=prefix, dir=os.path.dirname(path) or '.')
    try:
        with os.fdopen(tmp_fd, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in data:
                row = item.to_csv_row()
                writer.writerow(row)
        # On success, atomically replace
        os.replace(tmp_path, path)
        print(f'saved data to {path}.csv')
    except Exception as ex:
        print('An error occurred when writing the csv: {0}'.format(prefix))
        print(ex)
        # If anything goes wrong, remove temp file and re-raise
        try:
            os.remove(tmp_path)
        except Exception:
            print('An error occurred :(')
            pass


def load_from_csv(path, headers, factory_fn, filter_fn=None):
    """Load generic data from CSV file.

    Args:
        path: CSV file path
        headers: List of expected CSV column headers to validate/extract
        factory_fn: Callable that takes a row dict and returns an object
        filter_fn: Optional callable that takes a row dict and returns True to include, False to skip

    Returns:
        List of objects created by factory_fn (filtered by filter_fn if provided)
    """

    if not os.path.exists(path):
        print('CSV File not found')
        return []

    loaded = []

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, raw in enumerate(reader, start=1):
            try:
                # Extract row with expected headers
                row = {k: raw.get(k, '') for k in headers}

                # Apply optional filter
                if filter_fn and not filter_fn(row):
                    continue

                # Create object using factory
                obj = factory_fn(row)
                loaded.append(obj)
            except Exception as error:
                print(f'an error occurred when reading {path}: {error}')
                # Skip malformed rows
                continue

    return loaded

def load_members_from_csv(path):
    """Load brig member stats from CSV file.

    Args:
        path: CSV file path

    Returns:
        List of Brigade objects.
    """
    return load_from_csv(path, CSV_HEADERS_MEMBER_STATS, Brigade.from_csv_row)

