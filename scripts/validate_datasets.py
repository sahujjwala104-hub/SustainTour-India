import json
import pandas as pd
import numpy as np

print("="*70)
print("COMPREHENSIVE DATASET VALIDATION")
print("="*70)

datasets = {
    'national_tourism_statistics': 'data/extracted_2026_compendium/national_tourism_statistics.csv',
    'tourism_2025_statewise': 'data/extracted_2026_compendium/tourism_2025_statewise.csv',
    'statewise_extraction_audit': 'data/extracted_2026_compendium/statewise_extraction_audit.csv',
    'data_sources': 'data/extracted_2026_compendium/data_sources.csv',
    'tourism_timeseries': 'data/processed/tourism_timeseries.csv',
    'forest_cover_long': 'data/processed/forest_cover_long.csv',
    'groundwater_long': 'data/processed/groundwater_long.csv',
    'sdg_scores_long': 'data/processed/sdg_scores_long.csv',
    'state_sustainability_snapshot': 'data/processed/state_sustainability_snapshot.csv'
}

for name, path in datasets.items():
    print(f"\n>>> Dataset: {name} ({path})")
    df = pd.read_csv(path)
    print(f"Shape: {df.shape}")
    print("Columns and Types:")
    for col in df.columns:
        print(f"  - {col}: {df[col].dtype} (non-null: {df[col].count()}/{len(df)})")
    
    # Check nulls
    nulls = df.isnull().sum()
    if nulls.any():
        print("Missing values:")
        for col, cnt in nulls[nulls > 0].items():
            print(f"  * {col}: {cnt} ({cnt/len(df)*100:.1f}%)")
    else:
        print("Missing values: None")
        
    # Check numeric ranges
    num_cols = df.select_dtypes(include=[np.number]).columns
    for nc in num_cols:
        vals = df[nc].dropna()
        neg_cnt = (vals < 0).sum()
        print(f"  Numeric [{nc}]: min={vals.min()}, max={vals.max()}, negatives={neg_cnt}")
        
    # Check duplicates
    if 'state' in df.columns and 'year' in df.columns:
        dups = df.duplicated(subset=['state', 'year']).sum()
        print(f"Duplicate (state, year) pairs: {dups}")
    elif 'state' in df.columns and 'tourism_year' in df.columns:
        dups = df.duplicated(subset=['state', 'tourism_year']).sum()
        print(f"Duplicate (state, tourism_year) pairs: {dups}")
    elif 'year' in df.columns:
        dups = df.duplicated(subset=['year']).sum()
        print(f"Duplicate years: {dups}")
        
    # Check year ranges
    year_col = [c for c in df.columns if 'year' in c.lower()]
    for yc in year_col:
        print(f"Years in {yc}: {sorted(df[yc].dropna().unique())}")

print("\n" + "="*70)
print("GEOJSON VALIDATION")
print("="*70)
with open('data/geo/india_states.geojson', 'r', encoding='utf-8') as f:
    geo = json.load(f)
features = geo.get('features', [])
print(f"Total features: {len(features)}")
states_geo = [f['properties'].get('state') for f in features]
print(f"Unique 'state' values ({len(set(states_geo))}): {sorted(states_geo)}")
iso_geo = [f['properties'].get('shapeISO') for f in features]
print(f"Unique 'shapeISO' values ({len(set(iso_geo))}): {sorted(iso_geo)}")
