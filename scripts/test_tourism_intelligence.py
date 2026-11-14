"""
test_tourism_intelligence.py
=============================
Automated test suite verifying the integrity of the data loader,
geospatial alignment, KPI metrics, chart builders, and anomaly detection.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np

from src.constants import (
    TOURISM_PANEL_PATH,
    GEOJSON_PATH,
    NATIONAL_STATISTICS_PATH,
    CANONICAL_TO_GEOJSON_NAME,
    NAV_SECTIONS
)
from src.data_loader import (
    load_tourism_data,
    load_national_statistics,
    load_geojson,
    get_available_years,
    get_available_states
)
from src.geo_utils import (
    prepare_geojson_tourism_data,
    format_indian_number,
    format_full_number
)
from src.metrics import (
    compute_overview_kpis,
    get_rankings,
    get_national_timeseries,
    get_state_timeseries,
    calculate_cagr
)
from src.anomaly_detection import detect_tourism_anomalies
from src.charts import (
    create_india_choropleth,
    create_rankings_bar_chart,
    create_national_trend_chart,
    create_state_comparison_chart,
    create_growth_waterfall_chart,
    create_anomaly_scatter_chart
)


def run_tests():
    print("="*75)
    print("SUSTAINTOUR INDIA: TASK 2 TEST SUITE")
    print("="*75)
    
    # -------------------------------------------------------------------------
    # TEST 1: Data Loading & Panel Integrity
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Testing Data Loading & Panel Integrity...")
    df_tourism = load_tourism_data()
    df_national = load_national_statistics()
    geojson_data = load_geojson()
    
    assert len(df_tourism) == 530, f"Expected 530 rows, got {len(df_tourism)}"
    assert df_tourism["state"].nunique() == 36, f"Expected 36 states, got {df_tourism['state'].nunique()}"
    assert sorted(df_tourism["year"].unique()) == list(range(2011, 2026)), "Years mismatch"
    assert len(geojson_data["features"]) == 36, "GeoJSON feature count mismatch"
    assert len(df_national) == 17, "National statistics years mismatch"
    print("  ✓ Test 1 Passed: 530 rows, 36 states, 15 years, 36 GeoJSON features verified.")
    
    # -------------------------------------------------------------------------
    # TEST 2: Number Formatting & KPI Computations
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing Number Formatting & KPI Computations...")
    assert format_indian_number(1557423503) == "155.74 Cr (1557.42M)"
    assert format_indian_number(802017) == "8.02 L (0.80M)"
    assert format_indian_number(1500) == "1.50K"
    assert format_full_number(1557423503) == "1,557,423,503"
    
    # Test 2025 KPIs
    kpis_2025 = compute_overview_kpis(df_tourism, df_national, 2025)
    assert kpis_2025["domestic_visits"] == 4285530610
    assert kpis_2025["foreign_visits"] == 25326621
    assert kpis_2025["states_reporting"] == 36
    assert kpis_2025["discrepancy_info"]["dtv_diff"] == 400
    assert kpis_2025["discrepancy_info"]["ftv_diff"] == -1
    print("  ✓ Test 2 Passed: 2025 state sums and official discrepancies (+400 DTV, -1 FTV) verified.")
    
    # Test 2011 baseline KPIs (growth should be None)
    kpis_2011 = compute_overview_kpis(df_tourism, df_national, 2011)
    assert kpis_2011["dtv_growth_pct"] is None
    print("  ✓ Test 2 Passed: 2011 baseline growth gracefully handled as None.")
    
    # -------------------------------------------------------------------------
    # TEST 3: GeoJSON Alignment & Pre-Bifurcation Handling
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing GeoJSON Spatial Alignment...")
    geojson_states = [f["properties"]["state"] for f in geojson_data["features"]]
    
    # Test 2025: all 36 states available
    df_prep_2025 = prepare_geojson_tourism_data(df_tourism, 2025, geojson_states)
    assert len(df_prep_2025) == 36
    assert set(df_prep_2025["geojson_state"]) == set(geojson_states)
    assert (df_prep_2025["data_status"] == "Available").all()
    
    # Test 2012: Telangana and Ladakh did not exist as reporting entities yet
    df_prep_2012 = prepare_geojson_tourism_data(df_tourism, 2012, geojson_states)
    assert len(df_prep_2012) == 36
    telangana_row = df_prep_2012[df_prep_2012["state"] == "Telangana"].iloc[0]
    ladakh_row = df_prep_2012[df_prep_2012["state"] == "Ladakh"].iloc[0]
    assert "Not Formed" in telangana_row["data_status"]
    assert "Not Formed" in ladakh_row["data_status"]
    assert pd.isna(telangana_row["domestic_visits"])
    print("  ✓ Test 3 Passed: 100% GeoJSON feature mapping verified, pre-formation entities correctly flagged.")
    
    # -------------------------------------------------------------------------
    # TEST 4: Rankings & Data Availability
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Testing State Rankings...")
    top_10 = get_rankings(df_tourism, 2025, metric="domestic_visits", top_n=10, ascending=False)
    assert len(top_10) == 10
    assert top_10.iloc[0]["state"] == "Uttar Pradesh"
    assert top_10.iloc[0]["domestic_visits"] == 1557423503
    
    bottom_10 = get_rankings(df_tourism, 2025, metric="domestic_visits", top_n=10, ascending=True)
    assert len(bottom_10) == 10
    assert bottom_10.iloc[0]["state"] == "Manipur"  # 25,281 visits in 2025
    print("  ✓ Test 4 Passed: Top 10 and Bottom 10 rankings validated.")
    
    # -------------------------------------------------------------------------
    # TEST 5: Longitudinal Aggregations & CAGR
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Testing Historical Aggregations & CAGR...")
    df_nat_ts = get_national_timeseries(df_tourism)
    assert len(df_nat_ts) == 15
    assert df_nat_ts.iloc[0]["year"] == 2011
    assert df_nat_ts.iloc[-1]["year"] == 2025
    
    df_kerala = get_state_timeseries(df_tourism, "Kerala")
    assert len(df_kerala) == 15
    cagr_kerala = calculate_cagr(df_kerala["domestic_visits"].iloc[0], df_kerala["domestic_visits"].iloc[-1], 14)
    assert cagr_kerala > 0
    print(f"  ✓ Test 5 Passed: National series and state series (Kerala 14-yr CAGR = {cagr_kerala:.2f}%) validated.")
    
    # -------------------------------------------------------------------------
    # TEST 6: Anomaly Detection Engine
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Testing Anomaly Detection Engine...")
    df_anom = detect_tourism_anomalies(df_tourism)
    assert not df_anom.empty
    
    # Check UP 2025 Kumbh Mela flag
    up_2025 = df_anom[(df_anom["state"] == "Uttar Pradesh") & (df_anom["year"] == 2025)]
    assert len(up_2025) == 1
    assert "Maha Kumbh Mela" in up_2025.iloc[0]["category"]
    assert up_2025.iloc[0]["severity"] == "High"
    
    # Check Delhi and Maharashtra 2025 estimation flag
    delhi_2025 = df_anom[(df_anom["state"] == "Delhi") & (df_anom["year"] == 2025)]
    assert len(delhi_2025) == 1
    assert "Imputed" in delhi_2025.iloc[0]["category"]
    
    # Check Lakshadweep zero baselines
    lak_flags = df_anom[df_anom["state"] == "Lakshadweep"]
    assert len(lak_flags) > 0
    
    # Check COVID-19 flags in 2020
    covid_2020 = df_anom[(df_anom["year"] == 2020) & (df_anom["category"].str.contains("COVID"))]
    assert len(covid_2020) > 15
    print(f"  ✓ Test 6 Passed: Anomaly detector identified {len(df_anom)} auditable shifts with correct domain classifications.")
    
    # -------------------------------------------------------------------------
    # TEST 7: Plotly Chart Builders
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Testing Plotly Visualization Builders...")
    ch_fig = create_india_choropleth(df_prep_2025, geojson_data, "domestic_visits", 2025)
    assert ch_fig is not None
    
    rk_fig = create_rankings_bar_chart(top_10, "domestic_visits", "Top 10")
    assert rk_fig is not None
    
    ts_fig = create_national_trend_chart(df_nat_ts, "both")
    assert ts_fig is not None
    
    cmp_fig = create_state_comparison_chart(df_tourism, ["Kerala", "Goa"], "domestic_visits")
    assert cmp_fig is not None
    
    wf_fig = create_growth_waterfall_chart(df_nat_ts)
    assert wf_fig is not None
    
    anom_fig = create_anomaly_scatter_chart(df_anom, df_tourism)
    assert anom_fig is not None
    print("  ✓ Test 7 Passed: All 6 Plotly chart generation routines executed without error.")
    
    print("\n" + "="*75)
    print("ALL 7 TEST SUITES PASSED CLEANLY (100% SUCCESS)")
    print("="*75)


if __name__ == "__main__":
    run_tests()
