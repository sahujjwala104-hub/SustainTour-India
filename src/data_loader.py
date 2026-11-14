"""
data_loader.py
==============
Centralized cached data loading routines for SustainTour India.
Utilizes Streamlit caching for responsive dashboard performance.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd

try:
    import streamlit as st
except ImportError:
    class DummySt:
        @staticmethod
        def cache_data(*args, **kwargs):
            def decorator(f):
                return f
            return decorator
    st = DummySt()

from .constants import (
    TOURISM_PANEL_PATH,
    NATIONAL_STATISTICS_PATH,
    SUSTAINABILITY_SNAPSHOT_PATH,
    FOREST_COVER_PATH,
    GROUNDWATER_PATH,
    SDG_SCORES_PATH,
    GEOJSON_PATH,
    CANONICAL_TO_GEOJSON_NAME,
    GEOJSON_TO_CANONICAL_NAME,
)


@st.cache_data(show_spinner="Loading tourism time series panel...")
def load_tourism_data() -> pd.DataFrame:
    """
    Load the validated 2011-2025 merged tourism time series panel.
    Returns:
        pd.DataFrame: 530 rows across 36 States/UTs.
    """
    if not TOURISM_PANEL_PATH.is_file():
        raise FileNotFoundError(f"Tourism time series file missing at {TOURISM_PANEL_PATH}")
    
    df = pd.read_csv(TOURISM_PANEL_PATH)
    # Ensure correct types
    df["year"] = df["year"].astype(int)
    df["domestic_visits"] = df["domestic_visits"].astype(int)
    df["foreign_visits"] = df["foreign_visits"].astype(int)
    df["total_visits"] = df["total_visits"].astype(int)
    df["foreign_share_pct"] = df["foreign_share_pct"].astype(float)
    df["domestic_yoy_growth_pct"] = pd.to_numeric(df["domestic_yoy_growth_pct"], errors="coerce")
    return df


@st.cache_data(show_spinner="Loading national benchmark statistics...")
def load_national_statistics() -> pd.DataFrame:
    """
    Load official national tourism aggregates (1991, 2001, 2011-2025).
    """
    if not NATIONAL_STATISTICS_PATH.is_file():
        raise FileNotFoundError(f"National statistics file missing at {NATIONAL_STATISTICS_PATH}")
    
    df = pd.read_csv(NATIONAL_STATISTICS_PATH)
    df["year"] = df["year"].astype(int)
    return df


@st.cache_data(show_spinner="Loading sustainability snapshot...")
def load_sustainability_snapshot() -> pd.DataFrame:
    """
    Load the cross-domain sustainability snapshot (2023-2024 baseline).
    """
    if not SUSTAINABILITY_SNAPSHOT_PATH.is_file():
        raise FileNotFoundError(f"Snapshot file missing at {SUSTAINABILITY_SNAPSHOT_PATH}")
    return pd.read_csv(SUSTAINABILITY_SNAPSHOT_PATH)


@st.cache_data(show_spinner="Loading India State boundaries GeoJSON...")
def load_geojson() -> Dict[str, Any]:
    """
    Load the official 36-feature India states boundary GeoJSON.
    """
    if not GEOJSON_PATH.is_file():
        raise FileNotFoundError(f"GeoJSON boundary file missing at {GEOJSON_PATH}")
        
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson_dict = json.load(f)
    return geojson_dict


@st.cache_data(show_spinner="Loading environmental indicators...")
def load_environmental_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load forest cover, groundwater, and SDG long-format datasets.
    """
    df_forest = pd.read_csv(FOREST_COVER_PATH) if FOREST_COVER_PATH.is_file() else pd.DataFrame()
    df_gw = pd.read_csv(GROUNDWATER_PATH) if GROUNDWATER_PATH.is_file() else pd.DataFrame()
    df_sdg = pd.read_csv(SDG_SCORES_PATH) if SDG_SCORES_PATH.is_file() else pd.DataFrame()
    return df_forest, df_gw, df_sdg


def get_available_years(df: Optional[pd.DataFrame] = None) -> List[int]:
    """Return sorted unique years in the tourism panel."""
    if df is None:
        df = load_tourism_data()
    return sorted(df["year"].unique().tolist())


def get_available_states(df: Optional[pd.DataFrame] = None) -> List[str]:
    """Return sorted unique canonical state names in the tourism panel."""
    if df is None:
        df = load_tourism_data()
    return sorted(df["state"].unique().tolist())
