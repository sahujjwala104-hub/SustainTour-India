"""
tourism_intelligence.py
=======================
Full implementation of Task 2: Tourism Intelligence Dashboard.
Integrates Overview KPIs, Choropleth GeoJSON Map, Rankings, Historical Trends,
Explainable Anomaly Detection, and Data Quality Transparency disclosures.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
import streamlit as st

from ..constants import CANONICAL_TO_GEOJSON_NAME, THEME_COLORS
from ..data_loader import (
    load_tourism_data,
    load_national_statistics,
    load_geojson,
    get_available_years,
    get_available_states
)
from ..geo_utils import (
    prepare_geojson_tourism_data,
    format_indian_number,
    format_full_number
)
from ..metrics import (
    compute_overview_kpis,
    get_rankings,
    get_national_timeseries,
    get_state_timeseries,
    calculate_cagr
)
from ..anomaly_detection import detect_tourism_anomalies
from ..charts import (
    create_india_choropleth,
    create_rankings_bar_chart,
    create_national_trend_chart,
    create_state_comparison_chart,
    create_growth_waterfall_chart,
    create_anomaly_scatter_chart
)


def render_tourism_intelligence():
    """Main renderer for the Tourism Intelligence module."""
    
    # Load validated datasets via cached loaders
    df_tourism = load_tourism_data()
    df_national = load_national_statistics()
    geojson_data = load_geojson()
    available_years = get_available_years(df_tourism)
    available_states = get_available_states(df_tourism)
    geojson_states = [f["properties"]["state"] for f in geojson_data["features"]]
    
    # -------------------------------------------------------------------------
    # Top Control Bar (Year & Global Metric Selection)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 800; color: #0F172A; margin-bottom: 0.25rem;">
             Tourism Intelligence Dashboard
        </h1>
        <p style="color: #64748B; font-size: 1rem; margin: 0;">
            Comprehensive empirical analytics, spatial mapping, and longitudinal dynamics across India's 36 States and Union Territories (2011–2025).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 2, 2.5])
    
    with ctrl_col1:
        selected_year = st.selectbox(
            "📅 Select Reference Year",
            options=sorted(available_years, reverse=True),
            index=0,
            help="Select calendar year for cross-sectional analysis (2011–2025)."
        )
        
    with ctrl_col2:
        metric_choice = st.selectbox(
            "Primary Analysis Metric",
            options=[
                ("domestic_visits", "Domestic Tourist Visits (DTV)"),
                ("foreign_visits", "Foreign Tourist Visits (FTV)"),
                ("total_visits", "Total Tourist Visits (DTV + FTV)"),
                ("foreign_share_pct", "Foreign Tourist Share (%)"),
                ("domestic_yoy_growth_pct", "Domestic YoY Growth Rate (%)")
            ],
            format_func=lambda x: x[1],
            index=0,
            help="Select indicator for map layer and rankings."
        )[0]
        
    with ctrl_col3:
        st.markdown(f"""
        <div style="background: #F1F5F9; border-radius: 10px; padding: 0.65rem 1rem; margin-top: 1.4rem; font-size: 0.85rem; color: #334155;">
            <b>Active Panel:</b> 36 States/UTs • <b>Range:</b> 2011–2025 (15 Yrs) • <b>Records:</b> 530 Panel Observations
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='margin: 1.25rem 0 1.75rem 0; border: none; border-top: 1px solid #E2E8F0;' />", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION A: Tourism Overview (KPI Cards)
    # -------------------------------------------------------------------------
    kpis = compute_overview_kpis(df_tourism, df_national, selected_year)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        growth_str = ""
        delta_class = "delta-neutral"
        if kpis["dtv_growth_pct"] is not None:
            g = kpis["dtv_growth_pct"]
            growth_str = f"{g:+.2f}% YoY"
            delta_class = "delta-positive" if g >= 0 else "delta-negative"
        else:
            growth_str = "Baseline Year"
            
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Domestic Visits (DTV)</div>
            <div class="kpi-value">{format_indian_number(kpis["domestic_visits"])}</div>
            <div class="kpi-subvalue">{kpis["domestic_visits"]:,} visits</div>
            <div class="kpi-delta {delta_class}">▲ {growth_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        ftv_growth_str = ""
        ftv_delta_class = "delta-neutral"
        if kpis["ftv_growth_pct"] is not None:
            g = kpis["ftv_growth_pct"]
            ftv_growth_str = f"{g:+.2f}% YoY"
            ftv_delta_class = "delta-positive" if g >= 0 else "delta-negative"
        else:
            ftv_growth_str = "Baseline Year"
            
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Foreign Visits (FTV)</div>
            <div class="kpi-value">{format_indian_number(kpis["foreign_visits"])}</div>
            <div class="kpi-subvalue">{kpis["foreign_visits"]:,} visits</div>
            <div class="kpi-delta {ftv_delta_class}">▲ {ftv_growth_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Foreign Visitor Share</div>
            <div class="kpi-value">{kpis["foreign_share_pct"]:.2f}%</div>
            <div class="kpi-subvalue">Of total {format_indian_number(kpis["total_visits"])} visits</div>
            <div class="kpi-delta delta-neutral">Domestic Share: {100 - kpis["foreign_share_pct"]:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        reporting_text = f"{kpis['states_reporting']} of 36 States/UTs"
        note = "100% Pan-India Coverage"
        if selected_year < 2014:
            note = "Pre-Telangana bifurcation"
        elif selected_year < 2019:
            note = "Pre-Ladakh reorganization"
            
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Reporting Jurisdictions</div>
            <div class="kpi-value">{reporting_text}</div>
            <div class="kpi-subvalue">{note}</div>
            <div class="kpi-delta delta-neutral">ADM1 Level Panels</div>
        </div>
        """, unsafe_allow_html=True)

    # Keep reconciliation details available without dominating the dashboard.
    if kpis.get("discrepancy_info"):
        disc = kpis["discrepancy_info"]
        with st.expander("ℹ️ Data Sources & Methodology (2025 reconciliation)", expanded=False):
            st.markdown(
                f"**Domestic visits:** State total {disc['state_sum_dtv']:,}; "
                f"published national total {disc['published_dtv']:,}; "
                f"difference {disc['dtv_diff']:+,} visits.\n\n"
                f"**Foreign visits:** State total {disc['state_sum_ftv']:,}; "
                f"published national total {disc['published_ftv']:,}; "
                f"difference {disc['ftv_diff']:+,} visits.\n\n"
                "State-level source values are retained without adjustment."
            )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION B: Interactive India Tourism Map
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div class="section-title">Geographic Distribution — India Tourism Map ({selected_year})</div>
    <div class="section-desc">Interactive state-level choropleth rendering spatial footfall patterns across India. Hover over any polygon to inspect visits, growth, and official status caveats.</div>
    """, unsafe_allow_html=True)
    
    df_prepared = prepare_geojson_tourism_data(df_tourism, selected_year, geojson_states)
    choropleth_fig = create_india_choropleth(df_prepared, geojson_data, metric=metric_choice, year=selected_year)
    st.plotly_chart(choropleth_fig, use_container_width=True)

    # -------------------------------------------------------------------------
    # SECTION C: Tourism Rankings (Top 10 & Bottom 10)
    # -------------------------------------------------------------------------
    st.markdown(f"""
    <div class="section-title">State Rankings ({selected_year})</div>
    <div class="section-desc">Comparative leaderboards identifying high-volume hubs and low-volume destinations for {metric_choice.replace('_', ' ').title()}.</div>
    """, unsafe_allow_html=True)
    
    rank_col1, rank_col2 = st.columns(2)
    
    with rank_col1:
        df_top = get_rankings(df_tourism, selected_year, metric=metric_choice, top_n=10, ascending=False)
        top_fig = create_rankings_bar_chart(
            df_top,
            metric=metric_choice,
            title=f"🥇 Top 10 States/UTs ({selected_year})",
            ascending=False,
            color_scale="Teal"
        )
        st.plotly_chart(top_fig, use_container_width=True)
        
        with st.expander("📋 View Top 10 Data Table"):
            st.dataframe(
                df_top[["rank", "state", "domestic_visits", "foreign_visits", "total_visits", "foreign_share_pct"]].rename(
                    columns={
                        "rank": "Rank",
                        "state": "State / UT",
                        "domestic_visits": "Domestic Visits",
                        "foreign_visits": "Foreign Visits",
                        "total_visits": "Total Visits",
                        "foreign_share_pct": "Foreign Share (%)"
                    }
                ),
                hide_index=True,
                use_container_width=True
            )
            
    with rank_col2:
        df_bottom = get_rankings(df_tourism, selected_year, metric=metric_choice, top_n=10, ascending=True)
        bottom_fig = create_rankings_bar_chart(
            df_bottom,
            metric=metric_choice,
            title=f"📉 Bottom 10 States/UTs ({selected_year})",
            ascending=True,
            color_scale="Coral"
        )
        st.plotly_chart(bottom_fig, use_container_width=True)
        
        with st.expander("📋 View Bottom 10 Data Table & Availability Context"):
            st.dataframe(
                df_bottom[["rank", "state", "domestic_visits", "foreign_visits", "total_visits", "foreign_share_pct"]].rename(
                    columns={
                        "rank": "Rank",
                        "state": "State / UT",
                        "domestic_visits": "Domestic Visits",
                        "foreign_visits": "Foreign Visits",
                        "total_visits": "Total Visits",
                        "foreign_share_pct": "Foreign Share (%)"
                    }
                ),
                hide_index=True,
                use_container_width=True
            )
            st.caption("ℹ️ *Bottom rankings typically comprise island territories (e.g. Lakshadweep), small northeastern states, and specialized high-altitude UTs (Ladakh) reflecting physical carrying limits and low baseline resident populations.*")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION D: Historical Tourism Trends (2011–2025)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="section-title">Longitudinal Tourism Trends (2011–2025)</div>
    <div class="section-desc">Multi-year trajectory analysis covering national expansion, pandemic contraction (2020), subsequent recovery, and state-level comparative dynamics.</div>
    """, unsafe_allow_html=True)
    
    trend_tab1, trend_tab2, trend_tab3, trend_tab4 = st.tabs([
        "🇮🇳 All-India National Trajectory",
        "National Year-on-Year Growth",
        "🏛️ State-Specific Deep Dive",
        "⚖️ Multi-State Comparison"
    ])
    
    df_nat_ts = get_national_timeseries(df_tourism)
    
    with trend_tab1:
        st.plotly_chart(create_national_trend_chart(df_nat_ts, metric="both"), use_container_width=True)
        st.markdown("""
        <div style="font-size: 0.88rem; color: #475569; background: #F8FAFC; padding: 0.8rem 1rem; border-radius: 8px;">
            <b>Key Longitudinal Insights:</b> All-India domestic tourist visits grew from <b>86.45 Cr (864.5M)</b> in 2011 to <b>428.55 Cr (4,285.5M)</b> in 2025. The shaded region denotes the sharp 2020 COVID-19 contraction (-73.7% nationwide decline), followed by rapid compensatory recovery in 2022–2024 and an event-driven surge in 2025.
        </div>
        """, unsafe_allow_html=True)
        
    with trend_tab2:
        st.plotly_chart(create_growth_waterfall_chart(df_nat_ts), use_container_width=True)
        
    with trend_tab3:
        sel_state = st.selectbox(
            "Select State or Union Territory for Historical Breakdown:",
            options=available_states,
            index=available_states.index("Uttar Pradesh") if "Uttar Pradesh" in available_states else 0
        )
        df_single_st = get_state_timeseries(df_tourism, sel_state)
        
        st_metric_col1, st_metric_col2, st_metric_col3 = st.columns(3)
        with st_metric_col1:
            first_val = df_single_st["domestic_visits"].iloc[0]
            last_val = df_single_st["domestic_visits"].iloc[-1]
            st.metric("2011 Visits", format_indian_number(first_val), f"{first_val:,}")
        with st_metric_col2:
            st.metric("2025 Visits", format_indian_number(last_val), f"{last_val:,}")
        with st_metric_col3:
            cagr = calculate_cagr(first_val, last_val, len(df_single_st) - 1)
            cagr_str = f"{cagr:.2f}% p.a." if cagr else "N/A"
            st.metric("15-Year Compound Growth (CAGR)", cagr_str)
            
        st.plotly_chart(create_state_comparison_chart(df_tourism, [sel_state], metric="domestic_visits"), use_container_width=True)
        
    with trend_tab4:
        multi_states = st.multiselect(
            "Select 2 to 6 States/UTs to Compare Trajectories:",
            options=available_states,
            default=["Uttar Pradesh", "Tamil Nadu", "Maharashtra", "Kerala", "Rajasthan"]
        )
        if multi_states:
            st.plotly_chart(create_state_comparison_chart(df_tourism, multi_states, metric=metric_choice), use_container_width=True)
        else:
            st.warning("Please select at least one State or UT to display comparison.")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION E: Tourism Anomaly Detection
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="section-title">Tourism Anomaly Detection</div>
    <div class="section-desc">Defensible, explainable statistical anomaly detection based on robust Median Absolute Deviation (MAD) of year-on-year growth and verified historical event flags.</div>
    """, unsafe_allow_html=True)
    
    df_anomalies = detect_tourism_anomalies(df_tourism)
    
    anom_kpi1, anom_kpi2, anom_kpi3, anom_kpi4 = st.columns(4)
    with anom_kpi1:
        st.metric("Total Flagged Shifts", len(df_anomalies), "Out of 530 Panel Rows")
    with anom_kpi2:
        high_sev = len(df_anomalies[df_anomalies["severity"] == "High"])
        st.metric("High Severity Events", high_sev, "Extreme Deviations")
    with anom_kpi3:
        unique_states_flagged = df_anomalies["state"].nunique()
        st.metric("States Affected", unique_states_flagged, "Across 15 Years")
    with anom_kpi4:
        covid_flags = len(df_anomalies[df_anomalies["category"].str.contains("COVID|Pandemic", na=False)])
        st.metric("Pandemic Related Flags", covid_flags, "2020–2023 Shock & Rebound")
        
    st.plotly_chart(create_anomaly_scatter_chart(df_anomalies, df_tourism), use_container_width=True)
    
    # Filter anomalies table
    anom_filter_cat = st.selectbox(
        "Filter Anomalies by Category:",
        options=["All Categories"] + sorted(df_anomalies["category"].unique().tolist())
    )
    df_anom_display = df_anomalies if anom_filter_cat == "All Categories" else df_anomalies[df_anomalies["category"] == anom_filter_cat]
    
    with st.expander("🔎 View Full Explainable Anomaly Audit Table", expanded=True):
        st.dataframe(
            df_anom_display[[
                "year", "state", "domestic_visits", "domestic_yoy_growth_pct",
                "modified_z_score", "category", "severity", "explanation"
            ]].rename(columns={
                "year": "Year",
                "state": "State / UT",
                "domestic_visits": "Domestic Visits",
                "domestic_yoy_growth_pct": "YoY Growth (%)",
                "modified_z_score": "Modified Z-Score",
                "category": "Classification",
                "severity": "Severity",
                "explanation": "Auditable Explanation & Context"
            }),
            hide_index=True,
            use_container_width=True
        )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SECTION F: Data Quality, Integrity & Transparency Disclosures
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="section-title">Data Quality and Sources</div>
    <div class="section-desc">Transparent documentation of official definitions, estimation flags, boundary adjustments, and data source citations.</div>
    """, unsafe_allow_html=True)
    
    disc_col1, disc_col2 = st.columns(2)
    
    with disc_col1:
        st.markdown("""
        <div class="callout-box callout-info" style="height: 100%;">
            <h4 style="margin: 0 0 0.5rem 0; color: #0284C7;">📌 "Tourist Visits" vs. "Unique Tourists"</h4>
            <p style="margin: 0; font-size: 0.92rem; color: #334155; line-height: 1.6;">
                In official Indian tourism reporting, <b>Domestic Tourist Visits (DTV)</b> and <b>Foreign Tourist Visits (FTV)</b> reflect aggregate arrivals registered at state accommodation establishments, monuments, and checkpoints. A single traveler visiting three different states or returning to a pilgrimage site twice in one year is counted as three separate visits. These figures measure <b>footfall volume and demographic pressure</b>, not individual headcounts.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with disc_col2:
        st.markdown("""
        <div class="callout-box callout-warning" style="height: 100%;">
            <h4 style="margin: 0 0 0.5rem 0; color: #B45309;">⚠️ Documented Official Estimates & Outliers</h4>
            <p style="margin: 0; font-size: 0.92rem; color: #334155; line-height: 1.6;">
                <b>Delhi & Maharashtra (2025):</b> Primary survey figures were unavailable prior to publication; Ministry of Tourism applied the all-India 2025/2024 growth rate.<br>
                <b>Uttar Pradesh (2025):</b> The surge to 1.557 billion visits is driven by the once-in-12-years Maha Kumbh Mela at Prayagraj.<br>
                <b>2024 Revisions:</b> 2024 state figures in the 2026 Compendium reflect revised figures superseding provisional RBI Handbook releases.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.5rem; margin-top: 1.25rem;">
        <h4 style="margin: 0 0 0.6rem 0; color: #0F172A; font-size: 1rem;">📚 Official Primary Sources & Citation Authority</h4>
        <div style="font-size: 0.88rem; color: #475569; line-height: 1.7;">
            • <b>Historical Series (2011–2024):</b> Reserve Bank of India (RBI) <i>Handbook of Statistics on Indian States</i>, Table 13 (Domestic Visits) and Table 182 (Foreign Visits).<br>
            • <b>Compendium Series (2025):</b> Ministry of Tourism, Government of India, <i>India Tourism Data Compendium 2026</i> (67th Edition), Table 4.1.2 (State-wise Visits), Table 4.1.1 (National Series), Table 2.1.1 (FTAs), and Table 2.10.1 (FEE).<br>
            • <b>Spatial Boundaries:</b> ADM1 India States & UTs GeoJSON aligned with Survey of India administrative borders.<br>
            • <b>Preservation Rule:</b> Zero fabricated values; published zeros (e.g. Lakshadweep 2012, 2013, 2020) are distinguished from structural non-reporting (e.g. pre-bifurcation Telangana or pre-reorganization Ladakh).
        </div>
    </div>
    """, unsafe_allow_html=True)
