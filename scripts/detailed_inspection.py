import json
import pandas as pd
import numpy as np

# Load GeoJSON
with open('data/geo/india_states.geojson', 'r', encoding='utf-8') as f:
    geo = json.load(f)

print("="*60)
print("GEOJSON PROPERTIES")
print("="*60)
for feat in geo['features']:
    props = feat['properties']
    print(f"state: {props.get('state'):<40} | shapeName: {props.get('shapeName'):<35} | ISO: {props.get('shapeISO')}")

# Load all CSVs
tts = pd.read_csv('data/processed/tourism_timeseries.csv')
t25 = pd.read_csv('data/extracted_2026_compendium/tourism_2025_statewise.csv')
audit = pd.read_csv('data/extracted_2026_compendium/statewise_extraction_audit.csv')
fc = pd.read_csv('data/processed/forest_cover_long.csv')
gw = pd.read_csv('data/processed/groundwater_long.csv')
sdg = pd.read_csv('data/processed/sdg_scores_long.csv')
snap = pd.read_csv('data/processed/state_sustainability_snapshot.csv')

print("\n" + "="*60)
print("STATE NAMES COMPARISON")
print("="*60)
geo_states = sorted([f['properties']['state'] for f in geo['features']])
tts_states = sorted(tts['state'].unique())
t25_states = sorted(t25['state'].unique())
snap_states = sorted(snap['state'].unique())

print("TTS states vs Snapshot states match:", tts_states == snap_states)
if tts_states != snap_states:
    print("Diff:", set(tts_states) ^ set(snap_states))

print("\nTTS states vs 2025 states match:", tts_states == t25_states)
if tts_states != t25_states:
    print("Diff:", set(tts_states) ^ set(t25_states))
    for s in t25_states:
        if s not in tts_states:
            print(f"  In 2025 but not TTS: '{s}'")
    for s in tts_states:
        if s not in t25_states:
            print(f"  In TTS but not 2025: '{s}'")

print("\nTTS states vs GeoJSON 'state' match:", tts_states == geo_states)
if tts_states != geo_states:
    print("Diff:", set(tts_states) ^ set(geo_states))
    for s in tts_states:
        if s not in geo_states:
            print(f"  In TTS but not GeoJSON: '{s}'")
    for s in geo_states:
        if s not in tts_states:
            print(f"  In GeoJSON but not TTS: '{s}'")
