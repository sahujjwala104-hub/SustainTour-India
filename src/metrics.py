"""
metrics.py
==========
KPI calculations, statistical aggregations, rankings, and historical metrics
for SustainTour India.
"""

from typing import Dict, Any, Tuple, List, Optional
import pandas as pd
import numpy as np


def compute_overview_kpis(
    df_tourism: pd.DataFrame,
    df_national: pd.DataFrame,
    year: int
) -> Dict[str, Any]:
    """
    Calculate summary KPIs for the selected year, including aggregate totals,
    reporting states count, and YoY comparisons.
    """
    df_yr = df_tourism[df_tourism["year"] == year]
    
    # Current year aggregates from state sum
    dtv_sum = df_yr["domestic_visits"].sum()
    ftv_sum = df_yr["foreign_visits"].sum()
    total_sum = df_yr["total_visits"].sum()
    states_count = df_yr["state"].nunique()
    
    # Previous year comparison
    prev_year = year - 1
    df_prev = df_tourism[df_tourism["year"] == prev_year]
    
    dtv_growth = None
    ftv_growth = None
    total_growth = None
    
    if not df_prev.empty:
        prev_dtv = df_prev["domestic_visits"].sum()
        prev_ftv = df_prev["foreign_visits"].sum()
        prev_total = df_prev["total_visits"].sum()
        
        if prev_dtv > 0:
            dtv_growth = ((dtv_sum - prev_dtv) / prev_dtv) * 100
        if prev_ftv > 0:
            ftv_growth = ((ftv_sum - prev_ftv) / prev_ftv) * 100
        if prev_total > 0:
            total_growth = ((total_sum - prev_total) / prev_total) * 100
            
    # Foreign visitor share
    foreign_share = (ftv_sum / total_sum * 100) if total_sum > 0 else 0.0
    
    # Discrepancy info for 2025
    discrepancy_info = None
    if year == 2025 and not df_national.empty:
        nat_row = df_national[df_national["year"] == 2025]
        if not nat_row.empty:
            nat_dtv = int(nat_row["domestic_tourist_visits"].iloc[0])
            nat_ftv = int(nat_row["foreign_tourist_visits"].iloc[0])
            discrepancy_info = {
                "published_dtv": nat_dtv,
                "state_sum_dtv": int(dtv_sum),
                "dtv_diff": int(dtv_sum - nat_dtv),
                "published_ftv": nat_ftv,
                "state_sum_ftv": int(ftv_sum),
                "ftv_diff": int(ftv_sum - nat_ftv),
            }
            
    return {
        "year": year,
        "domestic_visits": int(dtv_sum),
        "foreign_visits": int(ftv_sum),
        "total_visits": int(total_sum),
        "foreign_share_pct": foreign_share,
        "states_reporting": states_count,
        "dtv_growth_pct": dtv_growth,
        "ftv_growth_pct": ftv_growth,
        "total_growth_pct": total_growth,
        "discrepancy_info": discrepancy_info,
    }


def get_rankings(
    df_tourism: pd.DataFrame,
    year: int,
    metric: str = "domestic_visits",
    top_n: int = 10,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Get top or bottom states for a specific metric in a given year.
    metric: 'domestic_visits', 'foreign_visits', 'total_visits', or 'foreign_share_pct'
    """
    df_yr = df_tourism[df_tourism["year"] == year].copy()
    df_sorted = df_yr.sort_values(by=metric, ascending=ascending).reset_index(drop=True)
    
    df_result = df_sorted.head(top_n).copy()
    df_result["rank"] = range(1, len(df_result) + 1)
    return df_result


def get_national_timeseries(df_tourism: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate domestic and foreign visits nationwide by year.
    """
    agg = df_tourism.groupby("year").agg(
        domestic_visits=("domestic_visits", "sum"),
        foreign_visits=("foreign_visits", "sum"),
        total_visits=("total_visits", "sum"),
        reporting_states=("state", "nunique")
    ).reset_index()
    
    agg["foreign_share_pct"] = (agg["foreign_visits"] / agg["total_visits"] * 100).round(2)
    agg["domestic_yoy_growth_pct"] = (agg["domestic_visits"].pct_change() * 100).round(2)
    agg["foreign_yoy_growth_pct"] = (agg["foreign_visits"].pct_change() * 100).round(2)
    return agg


def get_state_timeseries(df_tourism: pd.DataFrame, state_name: str) -> pd.DataFrame:
    """
    Filter historical trajectory for a single state.
    """
    df_st = df_tourism[df_tourism["state"] == state_name].sort_values("year").copy()
    return df_st.reset_index(drop=True)


def calculate_cagr(start_val: float, end_val: float, num_years: int) -> Optional[float]:
    """Calculate Compound Annual Growth Rate (CAGR)."""
    if start_val <= 0 or end_val <= 0 or num_years <= 0:
        return None
    return ((end_val / start_val) ** (1 / num_years) - 1) * 100
