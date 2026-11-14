import os
import glob
import json
import pandas as pd
import numpy as np

print("="*60)
print("INSPECTING CSV FILES")
print("="*60)

csv_files = sorted(glob.glob("data/**/*.csv", recursive=True))

for fpath in csv_files:
    print(f"\n--- {fpath} ---")
    try:
        df = pd.read_csv(fpath)
        print(f"Shape: {df.shape} (Rows: {df.shape[0]}, Cols: {df.shape[1]})")
        print(f"Columns: {list(df.columns)}")
        print("Data Types:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")
        
        # Check years
        year_cols = [c for c in df.columns if 'year' in c.lower()]
        for yc in year_cols:
            vals = sorted(df[yc].dropna().unique())
            print(f"  Unique values in {yc}: {vals[:10]}... (Total {len(vals)} distinct, min={min(vals)}, max={max(vals)})")
            
        # Check state column
        state_cols = [c for c in df.columns if any(k in c.lower() for k in ['state', 'ut', 'st_nm', 'region'])]
        for sc in state_cols:
            states = sorted(df[sc].dropna().unique().astype(str))
            print(f"  Unique entities in {sc} ({len(states)}): {states[:5]}... to ...{states[-3:]}")

        # Missing values
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        if len(null_cols) > 0:
            print("  Missing values:")
            for col, n_missing in null_cols.items():
                print(f"    {col}: {n_missing} ({n_missing/len(df)*100:.2f}%)")
        else:
            print("  Missing values: None (0)")
            
        print("  Sample row:")
        print(df.head(1).to_dict(orient='records'))
    except Exception as e:
        print(f"Error reading {fpath}: {e}")

print("\n" + "="*60)
print("INSPECTING GEOJSON")
print("="*60)
geojson_path = "data/geo/india_states.geojson"
if os.path.exists(geojson_path):
    with open(geojson_path, "r", encoding="utf-8") as gf:
        geo_data = json.load(gf)
    features = geo_data.get("features", [])
    print(f"GeoJSON features count: {len(features)}")
    if features:
        sample_props = features[0].get("properties", {})
        print(f"Properties keys: {list(sample_props.keys())}")
        print(f"Sample properties: {sample_props}")
        # collect all state names across features
        # let's find the property name for state
        for key in sample_props.keys():
            unique_vals = sorted(list(set(str(f.get("properties", {}).get(key, "")) for f in features)))
            print(f"Property '{key}' has {len(unique_vals)} unique values: {unique_vals[:5]}... to ...{unique_vals[-3:]}")
else:
    print(f"GeoJSON not found at {geojson_path}")
