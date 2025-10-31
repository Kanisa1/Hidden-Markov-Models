"""
Cleaning script for data/merged_all_sensors.csv
- Standardizes activity labels (jumping, still, standing, walking, running)
- Normalizes timestamp to ISO UTC (column 'time' assumed to be nanoseconds since epoch)
- Drops rows with invalid/missing timestamps or activity
- Drops exact duplicate rows
- Drops rows where all sensor axes are missing
- Sorts by timestamp
- Writes cleaned CSV to data/merged_all_sensors_cleaned.csv and stats JSON

Usage: python scripts/clean_merge.py
"""
import os
import sys
import json
from collections import Counter

try:
    import pandas as pd
except ImportError:
    print("pandas not found, installing pandas...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])  # may take a moment
    import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IN_PATH = os.path.join(ROOT, 'data', 'merged_all_sensors.csv')
OUT_PATH = os.path.join(ROOT, 'data', 'merged_all_sensors_cleaned.csv')
STATS_PATH = os.path.join(ROOT, 'data', 'merged_all_sensors_cleaned_stats.json')

print('Reading', IN_PATH)
# Read CSV (let pandas infer dtypes)
df = pd.read_csv(IN_PATH)
print('Initial rows:', len(df))

# Normalize column names (strip spaces)
df.columns = [c.strip() for c in df.columns]

# Identify timestamp column
if 'time' in df.columns:
    ts_col = 'time'
elif 'timestamp' in df.columns:
    ts_col = 'timestamp'
else:
    # fallback to first numeric column
    possible = [c for c in df.columns if df[c].dtype.kind in 'iu' or df[c].dtype.kind == 'f']
    ts_col = possible[0] if possible else df.columns[0]
    print('Using', ts_col, 'as timestamp column (fallback)')

# Convert timestamp: file appears to store nanoseconds since unix epoch -> use unit='ns'
print('Parsing timestamp column', ts_col)
try:
    df['timestamp'] = pd.to_datetime(df[ts_col], unit='ns', origin='unix', errors='coerce')
except Exception as e:
    # fallback: try seconds
    print('Failed to parse as ns, trying seconds:', e)
    df['timestamp'] = pd.to_datetime(df[ts_col], unit='s', origin='unix', errors='coerce')

# Standardize activity labels
if 'Activity' in df.columns:
    act_col = 'Activity'
elif 'activity' in df.columns:
    act_col = 'activity'
else:
    act_col = None

def clean_activity(a):
    if pd.isna(a):
        return None
    s = str(a).strip().lower()
    # Check common substrings as labels sometimes include prefixes/suffixes (e.g. 'rene-running-2025-10-29')
    if 'jump' in s:
        return 'jumping'
    if 'stand' in s:
        return 'standing'
    if 'still' in s:
        return 'still'
    if 'walk' in s:
        return 'walking'
    if 'run' in s:
        return 'running'
    # common synonyms
    if s in ('jog', 'jogging'):
        return 'running'
    # if label already one of desired
    if s in ('jumping', 'standing', 'still', 'walking', 'running'):
        return s
    return s  # keep as-is but lowercased

if act_col:
    df['activity_clean'] = df[act_col].apply(clean_activity)
else:
    print('No activity column found; creating placeholder activity_clean')
    df['activity_clean'] = None

# Remove rows with missing activity or timestamp
before = len(df)
df = df[~df['timestamp'].isna()]
df = df[~df['activity_clean'].isna()]
after_ts_act = len(df)
print('Rows after removing missing timestamp/activity:', after_ts_act, '(removed', before - after_ts_act, ')')

# Drop rows where all axes (x,y,z) are NaN if present
axis_cols = [c for c in ['x', 'y', 'z'] if c in df.columns]
if axis_cols:
    before_axes = len(df)
    df = df.dropna(how='all', subset=axis_cols)
    print('Rows after dropping rows with all axis NaN:', len(df), '(removed', before_axes - len(df), ')')

# Drop exact duplicates
before_dups = len(df)
df = df.drop_duplicates()
print('Rows after dropping exact duplicates:', len(df), '(removed', before_dups - len(df), ')')

# Sort by timestamp
df = df.sort_values('timestamp').reset_index(drop=True)

# Reformat timestamp to ISO and create final columns order
df['timestamp_iso'] = df['timestamp'].dt.tz_localize('UTC').dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

# Choose output columns: keep time(s), timestamp_iso, seconds_elapsed if exists, x,y,z,Sensor,SourceFile,activity_clean
out_cols = []
for c in ['time', 'timestamp_iso', 'seconds_elapsed', 'x', 'y', 'z', 'Sensor', 'SourceFile', 'activity_clean']:
    if c in df.columns:
        out_cols.append(c)

# write cleaned CSV
print('Writing cleaned CSV to', OUT_PATH)
df[out_cols].to_csv(OUT_PATH, index=False)

# stats
counts = dict(Counter(df['activity_clean']))
stats = {
    'rows_before': int(before),
    'rows_after': int(len(df)),
    'removed_timestamp_or_activity': int(before - after_ts_act),
    'activity_counts': counts,
    'columns': list(df.columns)
}
with open(STATS_PATH, 'w', encoding='utf-8') as fh:
    json.dump(stats, fh, indent=2)

print('Done. Summary:')
print(json.dumps(stats, indent=2))
print('Cleaned CSV:', OUT_PATH)
print('Stats JSON:', STATS_PATH)
