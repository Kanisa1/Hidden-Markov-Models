"""
Finalize cleaned CSV: read `merged_all_sensors_cleaned.csv`, ensure `activity` column exists,
create `Activity` title-cased for compatibility, and write final CSV
"""
import os
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IN_PATH = os.path.join(ROOT, 'data', 'merged_all_sensors_cleaned.csv')
OUT_PATH = os.path.join(ROOT, 'data', 'merged_all_sensors_cleaned_final.csv')

print('Reading', IN_PATH)
df = pd.read_csv(IN_PATH)
print('Initial rows:', len(df))

# If activity_clean exists, promote it to activity
if 'activity' not in df.columns and 'activity_clean' in df.columns:
    df['activity'] = df['activity_clean']

# If Activity exists (original), create lowercase activity for consistency
if 'activity' not in df.columns and 'Activity' in df.columns:
    df['activity'] = df['Activity'].astype(str)

# Normalize and ensure lowercase
if 'activity' in df.columns:
    df['activity'] = df['activity'].astype(str).str.strip().str.lower()
    df['Activity'] = df['activity'].str.title()
else:
    print('Warning: no activity column found; creating placeholder with empty strings')
    df['activity'] = ''
    df['Activity'] = ''

# If timestamp_iso exists, ensure it exists; if not, try to create from timestamp
if 'timestamp_iso' not in df.columns and 'timestamp' in df.columns:
    try:
        df['timestamp_iso'] = pd.to_datetime(df['timestamp'], unit='ns', errors='coerce').dt.tz_localize('UTC').dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    except Exception:
        df['timestamp_iso'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.tz_localize('UTC').dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

# Write final tidy CSV
print('Writing final cleaned CSV to', OUT_PATH)
df.to_csv(OUT_PATH, index=False)
print('Done. Final rows:', len(df))
