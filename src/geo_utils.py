"""
geo_utils.py
============
Geospatial alignment utilities for mapping GeoJSON polygons with
tabular state data in SustainTour India.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from .constants import CANONICAL_TO_GEOJSON_NAME, GEOJSON_TO_CANONICAL_NAME, STATE_TO_ISO_CODE


INDIA_MAP_CENTER = {"lat": 22.8, "lon": 82.5}
INDIA_MAP_ZOOM = 3.6


def format_indian_number(n: float, precision: int = 2) -> str:
    """
    Format large numbers into human-readable compact notation (Cr / L / M / K).
    """
    if pd.isna(n) or n is None:
        return "N/A"
    
    abs_n = abs(n)
    sign = "-" if n < 0 else ""
    
    if abs_n >= 10_000_000:  # Crore (10M)
        crores = abs_n / 10_000_000
        return f"{sign}{crores:.{precision}f} Cr ({abs_n/1_000_000:.{precision}f}M)"
    elif abs_n >= 100_000:   # Lakh (100K)
        lakhs = abs_n / 100_000
        return f"{sign}{lakhs:.{precision}f} L ({abs_n/1_000_000:.{precision}f}M)"
    elif abs_n >= 1_000:
        return f"{sign}{abs_n/1_000:.{precision}f}K"
    else:
        return f"{sign}{abs_n:,.0f}"


def format_full_number(n: float) -> str:
    """Format full integer with comma separators."""
    if pd.isna(n) or n is None:
        return "N/A"
    return f"{int(n):,}"


def prepare_geojson_tourism_data(
    df_tourism: pd.DataFrame,
    year: int,
    all_geojson_states: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Filter tourism data for a specific year and merge with all 36 GeoJSON entities.
    Handles historical state non-existence (Telangana pre-2013, Ladakh pre-2019)
    and maps canonical state names to GeoJSON feature keys.
    """
    df_yr = df_tourism[df_tourism["year"] == year].copy()
    
    # Add GeoJSON state name key
    df_yr["geojson_state"] = df_yr["state"].map(
        lambda s: CANONICAL_TO_GEOJSON_NAME.get(s, s)
    )
    df_yr["iso_code"] = df_yr["state"].map(STATE_TO_ISO_CODE)
    
    # If all_geojson_states provided, ensure all 36 features are represented
    if all_geojson_states:
        present_geo_states = set(df_yr["geojson_state"].unique())
        missing_geo_states = set(all_geojson_states) - present_geo_states
        
        if missing_geo_states:
            missing_records = []
            for g_state in missing_geo_states:
                c_state = GEOJSON_TO_CANONICAL_NAME.get(g_state, g_state)
                note = "Data Not Available"
                if c_state == "Telangana" and year < 2013:
                    note = "Not Formed (Prior to 2014 Bifurcation)"
                elif c_state == "Ladakh" and year < 2019:
                    note = "Not Formed (Prior to 2019 Reorganization)"
                    
                missing_records.append({
                    "state": c_state,
                    "year": year,
                    "domestic_visits": np.nan,
                    "foreign_visits": np.nan,
                    "total_visits": np.nan,
                    "foreign_share_pct": np.nan,
                    "domestic_yoy_growth_pct": np.nan,
                    "foreign_2024_estimate_caveat": None,
                    "source_domestic": "N/A",
                    "source_foreign": "N/A",
                    "geojson_state": g_state,
                    "iso_code": STATE_TO_ISO_CODE.get(c_state, "IN-XX"),
                    "data_status": note,
                })
            df_missing = pd.DataFrame(missing_records)
            df_yr["data_status"] = "Available"
            df_yr = pd.concat([df_yr, df_missing], ignore_index=True)
        else:
            df_yr["data_status"] = "Available"
    else:
        df_yr["data_status"] = "Available"
        
    # Build informative hover fields
    def get_caveat(row):
        st_name = row["state"]
        if row["data_status"] != "Available":
            return row["data_status"]
        if year == 2025:
            if st_name in ["Delhi", "Maharashtra"]:
                return "Official Estimate (Ministry of Tourism growth-rate imputation)"
            elif st_name == "Uttar Pradesh":
                return "Exceptional Event: Includes Maha Kumbh Mela visits"
        elif year == 2024:
            if pd.notna(row.get("foreign_2024_estimate_caveat")):
                return "Provisional RBI Estimate"
        if row["domestic_visits"] == 0:
            return "Official Published Zero"
        return "Official Government Record"

    df_yr["annotation"] = df_yr.apply(get_caveat, axis=1)
    
    # Formatted text fields for clean tooltip display
    df_yr["hover_domestic"] = df_yr["domestic_visits"].apply(
        lambda v: f"{format_full_number(v)} ({format_indian_number(v)})" if pd.notna(v) else "Data Not Available"
    )
    df_yr["hover_foreign"] = df_yr["foreign_visits"].apply(
        lambda v: f"{format_full_number(v)} ({format_indian_number(v)})" if pd.notna(v) else "Data Not Available"
    )
    df_yr["hover_total"] = df_yr["total_visits"].apply(
        lambda v: f"{format_full_number(v)} ({format_indian_number(v)})" if pd.notna(v) else "Data Not Available"
    )
    df_yr["hover_growth"] = df_yr["domestic_yoy_growth_pct"].apply(
        lambda g: f"{g:+.2f}%" if pd.notna(g) else "Baseline / Undefined"
    )
    df_yr["hover_share"] = df_yr["foreign_share_pct"].apply(
        lambda s: f"{s:.2f}%" if pd.notna(s) else "N/A"
    )
    
    return df_yr
