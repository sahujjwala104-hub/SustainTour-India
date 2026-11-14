#!/usr/bin/env python3
"""
merge_tourism_data.py
=====================
Merges newly extracted 2025 state-wise tourism statistics into the historical
tourism time series (2011-2024) to produce the complete 2011-2025 time series.

Deliverable:
- Output: data/processed/tourism_timeseries_2011_2025.csv
- Preserves original CSVs without modification.
- Implements explicit state name standardization.
- Validates data integrity, GeoJSON alignment, and source reconciliation.
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

# Project root setup
BASE_DIR = Path(__file__).resolve().parent.parent

HISTORICAL_CSV = BASE_DIR / "data" / "processed" / "tourism_timeseries.csv"
DATA_2025_CSV = BASE_DIR / "data" / "extracted_2026_compendium" / "tourism_2025_statewise.csv"
NATIONAL_CSV = BASE_DIR / "data" / "extracted_2026_compendium" / "national_tourism_statistics.csv"
GEOJSON_FILE = BASE_DIR / "data" / "geo" / "india_states.geojson"
OUTPUT_CSV = BASE_DIR / "data" / "processed" / "tourism_timeseries_2011_2025.csv"

# Explicit State / UT Name Mapping
# Standardizes 2025 compendium labels to canonical project names used in historical time series
STATE_NAME_MAPPING_2025 = {
    "Dadra Nagar Haveli & Daman & Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Jammu & Kashmir": "Jammu and Kashmir"
}

# Explicit mapping between Canonical Dataset State Names and GeoJSON properties
CANONICAL_TO_GEOJSON_MAPPING = {
    "Andaman & Nicobar Islands": "Andaman and Nicobar Islands",
    "Dadra & Nagar Haveli and Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu"
}

def load_and_validate_inputs():
    """Verify input files exist and load datasets."""
    print("Step 1: Loading input datasets...")
    for p in [HISTORICAL_CSV, DATA_2025_CSV, NATIONAL_CSV, GEOJSON_FILE]:
        if not p.is_file():
            raise FileNotFoundError(f"Required input file missing: {p}")
            
    df_hist = pd.read_csv(HISTORICAL_CSV)
    df_2025 = pd.read_csv(DATA_2025_CSV)
    df_nat = pd.read_csv(NATIONAL_CSV)
    
    with open(GEOJSON_FILE, "r", encoding="utf-8") as gf:
        geojson_data = json.load(gf)
        
    print(f"  - Historical time series loaded: {df_hist.shape[0]} rows, {df_hist.shape[1]} columns (Years: {df_hist['year'].min()}–{df_hist['year'].max()})")
    print(f"  - 2025 state data loaded: {df_2025.shape[0]} rows (Year: {df_2025['year'].unique().tolist()})")
    print(f"  - National statistics loaded: {df_nat.shape[0]} years (1991, 2001, 2011–2025)")
    print(f"  - GeoJSON features loaded: {len(geojson_data['features'])} features")
    return df_hist, df_2025, df_nat, geojson_data


def standardize_2025_data(df_2025, df_hist):
    """Apply documented name mapping to standardize 2025 state names."""
    print("\nStep 2: Standardizing state and UT names...")
    df_2025_std = df_2025.copy()
    
    # Track renames
    df_2025_std["state"] = df_2025_std["state"].replace(STATE_NAME_MAPPING_2025)
    
    hist_states = set(df_hist["state"].unique())
    std_2025_states = set(df_2025_std["state"].unique())
    
    print(f"  - Renamed according to explicit mapping: {STATE_NAME_MAPPING_2025}")
    print(f"  - Unique states in historical: {len(hist_states)}")
    print(f"  - Unique states in 2025 (standardized): {len(std_2025_states)}")
    
    unmatched_in_2025 = std_2025_states - hist_states
    unmatched_in_hist = hist_states - std_2025_states
    
    if unmatched_in_2025 or unmatched_in_hist:
        raise ValueError(f"State mismatch after standardization!\nIn 2025 only: {unmatched_in_2025}\nIn historical only: {unmatched_in_hist}")
        
    print("  ✓ All 36 states/UTs in 2025 exactly match historical time series states.")
    return df_2025_std


def calculate_2025_derived_metrics(df_2025_std, df_hist):
    """Compute total_visits, foreign_share_pct, domestic_yoy_growth_pct, and metadata columns for 2025."""
    print("\nStep 3: Calculating derived indicators for 2025...")
    
    # 2024 domestic visits baseline for YoY growth calculation
    df_2024 = df_hist[df_hist["year"] == 2024].set_index("state")["domestic_visits"]
    
    df_2025_calc = df_2025_std.copy()
    
    # 1. total_visits = domestic + foreign
    df_2025_calc["total_visits"] = df_2025_calc["domestic_visits"] + df_2025_calc["foreign_visits"]
    
    # 2. foreign_share_pct = round((foreign / total) * 100, 4)
    df_2025_calc["foreign_share_pct"] = (
        df_2025_calc["foreign_visits"] / df_2025_calc["total_visits"] * 100
    ).round(4)
    
    # 3. domestic_yoy_growth_pct = round(((2025_dtv - 2024_dtv) / 2024_dtv) * 100, 4)
    dtv_2024_vals = df_2025_calc["state"].map(df_2024)
    df_2025_calc["domestic_yoy_growth_pct"] = (
        (df_2025_calc["domestic_visits"] - dtv_2024_vals) / dtv_2024_vals * 100
    ).round(4)
    
    # 4. foreign_2024_estimate_caveat is specific to 2024 RBI estimates -> np.nan for 2025
    df_2025_calc["foreign_2024_estimate_caveat"] = np.nan
    
    # 5. Source citations
    df_2025_calc["source_domestic"] = "India Tourism Data Compendium 2026 Table 4.1.2"
    df_2025_calc["source_foreign"] = "India Tourism Data Compendium 2026 Table 4.1.2"
    
    # Verify column alignment with historical schema
    hist_cols = list(df_hist.columns)
    df_2025_calc = df_2025_calc[hist_cols]
    
    print(f"  ✓ Derived metrics computed successfully for all 36 states.")
    return df_2025_calc


def merge_and_sort(df_hist, df_2025_calc):
    """Concatenate historical and 2025 datasets and sort deterministically."""
    print("\nStep 4: Merging historical series (2011–2024) with 2025 records...")
    df_merged = pd.concat([df_hist, df_2025_calc], ignore_index=True)
    
    # Deterministic sort: state alphabetical, year ascending
    df_merged = df_merged.sort_values(by=["state", "year"]).reset_index(drop=True)
    
    print(f"  - Total merged rows: {len(df_merged)} (Historical: {len(df_hist)} + 2025: {len(df_2025_calc)})")
    print(f"  - Years span: {df_merged['year'].min()} to {df_merged['year'].max()} ({df_merged['year'].nunique()} distinct years)")
    return df_merged


def validate_merged_dataset(df_merged, df_nat):
    """Run rigorous validation checks on the merged dataset."""
    print("\nStep 5: Validating merged dataset integrity...")
    
    # Check 1: Record counts and dimensions
    expected_rows = 530  # 494 + 36
    if len(df_merged) != expected_rows:
        raise ValueError(f"Expected {expected_rows} rows, got {len(df_merged)}")
    print(f"  ✓ Row count exact: {len(df_merged)} rows")
    
    # Check 2: Duplicate state-year observations
    dup_mask = df_merged.duplicated(subset=["state", "year"])
    if dup_mask.any():
        dups = df_merged[dup_mask]
        raise ValueError(f"Duplicate state-year observations found:\n{dups}")
    print("  ✓ Duplicate check passed: 0 duplicate (state, year) observations")
    
    # Check 3: Check for missing values
    null_counts = df_merged.isnull().sum()
    disallowed_nulls = null_counts.drop(["domestic_yoy_growth_pct", "foreign_2024_estimate_caveat"])
    if disallowed_nulls.any():
        raise ValueError(f"Disallowed null values found:\n{disallowed_nulls[disallowed_nulls > 0]}")
        
    expected_nan_growth = 39  # 36 first-year observations + 3 zero-division years (Lakshadweep 2013, 2014, 2021)
    if null_counts["domestic_yoy_growth_pct"] != expected_nan_growth:
        raise ValueError(f"Expected {expected_nan_growth} NaN growth values, got {null_counts['domestic_yoy_growth_pct']}")
    print(f"  ✓ Missing values check passed: nulls restricted strictly to baseline growth ({expected_nan_growth}) and 2024 estimate caveat")
    
    # Check 4: Numeric ranges and sanity checks
    if (df_merged["domestic_visits"] < 0).any():
        raise ValueError("Negative domestic_visits found!")
    if (df_merged["foreign_visits"] < 0).any():
        raise ValueError("Negative foreign_visits found!")
    if (df_merged["total_visits"] <= 0).any():
        raise ValueError("Non-positive total_visits found!")
    if ((df_merged["foreign_share_pct"] < 0) | (df_merged["foreign_share_pct"] > 100)).any():
        raise ValueError("foreign_share_pct out of [0, 100] bounds!")
    print("  ✓ Numeric ranges valid: all visits >= 0, foreign shares within [0, 100]%")
    
    # Check 5: Preserve documented 2025 discrepancies between state-level sums and national totals
    dtv_2025_state_sum = int(df_merged[df_merged["year"] == 2025]["domestic_visits"].sum())
    ftv_2025_state_sum = int(df_merged[df_merged["year"] == 2025]["foreign_visits"].sum())
    
    dtv_2025_national = int(df_nat[df_nat["year"] == 2025]["domestic_tourist_visits"].iloc[0])
    ftv_2025_national = int(df_nat[df_nat["year"] == 2025]["foreign_tourist_visits"].iloc[0])
    
    dtv_diff = dtv_2025_state_sum - dtv_2025_national
    ftv_diff = ftv_2025_state_sum - ftv_2025_national
    
    print(f"  - 2025 State Sum DTV: {dtv_2025_state_sum:,} | National Table 4.1.1: {dtv_2025_national:,} | Discrepancy: {dtv_diff:+d}")
    print(f"  - 2025 State Sum FTV: {ftv_2025_state_sum:,} | National Table 4.1.1: {ftv_2025_national:,} | Discrepancy: {ftv_diff:+d}")
    
    if dtv_diff != 400 or ftv_diff != -1:
        raise ValueError(f"Documented discrepancy altered! Expected (+400 DTV, -1 FTV), got ({dtv_diff:+d} DTV, {ftv_diff:+d} FTV)")
    print("  ✓ Documented official compendium discrepancy verified and preserved without alteration.")


def check_geojson_compatibility(df_merged, geojson_data):
    """Verify alignment between dataset state names and GeoJSON properties."""
    print("\nStep 6: Checking GeoJSON boundary compatibility...")
    features = geojson_data["features"]
    geojson_states = set(f["properties"]["state"] for f in features)
    merged_states = set(df_merged["state"].unique())
    
    exact_matches = merged_states.intersection(geojson_states)
    dataset_only = merged_states - geojson_states
    geojson_only = geojson_states - merged_states
    
    print(f"  - GeoJSON feature count: {len(features)}")
    print(f"  - Exact state name matches: {len(exact_matches)} / 36")
    print(f"  - Names differing in punctuation/conjunction: {len(dataset_only)}")
    for s in sorted(dataset_only):
        target = CANONICAL_TO_GEOJSON_MAPPING.get(s, "UNKNOWN")
        print(f"    * Dataset: '{s}'  <-->  GeoJSON 'state': '{target}'")
        
    # Check that with mapping applied, 100% match is achieved
    mapped_dataset_states = {CANONICAL_TO_GEOJSON_MAPPING.get(s, s) for s in merged_states}
    if mapped_dataset_states != geojson_states:
        raise ValueError(f"GeoJSON alignment failure after mapping: {mapped_dataset_states ^ geojson_states}")
    print("  ✓ 100% GeoJSON topological coverage verified via documented mapping.")


def main():
    print("="*75)
    print("SUSTAINTOUR INDIA: 2011–2025 TOURISM DATA INTEGRATION")
    print("="*75)
    
    df_hist, df_2025, df_nat, geojson_data = load_and_validate_inputs()
    df_2025_std = standardize_2025_data(df_2025, df_hist)
    df_2025_calc = calculate_2025_derived_metrics(df_2025_std, df_hist)
    df_merged = merge_and_sort(df_hist, df_2025_calc)
    
    validate_merged_dataset(df_merged, df_nat)
    check_geojson_compatibility(df_merged, geojson_data)
    
    print(f"\nStep 7: Writing output to {OUTPUT_CSV}...")
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"  ✓ Successfully wrote {len(df_merged)} rows to {OUTPUT_CSV.name}")
    
    # Verify file on disk
    written_df = pd.read_csv(OUTPUT_CSV)
    if len(written_df) != 530:
        raise IOError(f"Written file verification failed! Expected 530 rows, got {len(written_df)}")
    print(f"  ✓ Output file integrity confirmed on disk: {len(written_df)} records.")
    print("\n" + "="*75)
    print("INTEGRATION COMPLETED SUCCESSFULLY.")
    print("="*75)


if __name__ == "__main__":
    main()
