"""
placeholders.py
===============
Polished architectural placeholders for planned application sections
(Tasks 3 through 8) in SustainTour India.
"""

import streamlit as st


def render_placeholder(
    section_name: str,
    icon: str,
    planned_task: str,
    overview: str,
    planned_features: list,
    data_inputs: list
):
    """Generic template for non-active module previews."""
    st.markdown(f"""
    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 16px; padding: 2rem; margin-top: 1rem; box-shadow: 0 4px 15px -3px rgba(0,0,0,0.05);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 2.2rem;">{icon}</span>
                <div>
                    <h2 style="margin: 0; font-size: 1.6rem; color: #0F172A; font-weight: 700;">{section_name}</h2>
                    <span style="color: #64748B; font-size: 0.9rem;">SustainTour India Architecture</span>
                </div>
            </div>
            <span style="background: #FEF3C7; color: #92400E; font-size: 0.8rem; font-weight: 700; padding: 0.35rem 0.85rem; border-radius: 9999px; border: 1px solid #FDE68A;">
                ⏳ {planned_task} — In Roadmap
            </span>
        </div>
        <p style="color: #334155; font-size: 1rem; line-height: 1.6; margin-bottom: 1.5rem;">
            {overview}
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.4rem; height: 100%;">
            <h4 style="margin: 0 0 0.8rem 0; color: #0F766E; font-size: 1.05rem;">🎯 Planned Core Capabilities</h4>
            <ul style="color: #475569; font-size: 0.92rem; line-height: 1.7; padding-left: 1.2rem; margin: 0;">
        """ + "".join(f"<li>{feat}</li>" for feat in planned_features) + """
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.4rem; height: 100%;">
            <h4 style="margin: 0 0 0.8rem 0; color: #0284C7; font-size: 1.05rem;">📂 Harmonized Data Pipelines</h4>
            <ul style="color: #475569; font-size: 0.92rem; line-height: 1.7; padding-left: 1.2rem; margin: 0;">
        """ + "".join(f"<li>{inp}</li>" for inp in data_inputs) + """
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.info("ℹ️ Task 1 (Data Validation and Integration) and Task 2 (Tourism Intelligence) are active. This module will be populated in subsequent milestones according to project specifications.")


def render_sustainability_intelligence():
    render_placeholder(
        section_name="Sustainability Intelligence",
        icon="🌿",
        planned_task="Task 3",
        overview="Multi-dimensional environmental sustainability dashboard integrating forest canopy coverage (FSI ISFR 1987–2023), aquifer extraction stress (CGWB 2017–2024), and composite SDG progress indices (NITI Aayog 2018–2023).",
        planned_features=[
            "Tourism-to-Forest Pressure Ratio (annual visitors per sq. km forest)",
            "Groundwater Depletion & Stage of Extraction tracking (over-exploited aquifers)",
            "SDG 8 & 12 progress alignment indicators across Indian States",
            "Composite Carrying Capacity Stress Score across ecological zones"
        ],
        data_inputs=[
            "data/processed/forest_cover_long.csv (693 records, 19 biennial cycles)",
            "data/processed/groundwater_long.csv (185 records, CGWB dynamic assessments)",
            "data/processed/sdg_scores_long.csv (148 records, NITI Aayog SDG Index 1.0–4.0)",
            "data/processed/state_sustainability_snapshot.csv (Harmonized baseline)"
        ]
    )


def render_state_comparison():
    render_placeholder(
        section_name="State Comparison Studio",
        icon="⚖️",
        planned_task="Task 4",
        overview="Side-by-side comparative benchmarking engine enabling policymakers to evaluate two or more States/UTs across demographic load, foreign visitor pull, forest density, and aquifer vulnerability.",
        planned_features=[
            "Side-by-side dual-state and tri-state comparative scorecard",
            "Radar / Spider charts across 6 standardized sustainability dimensions",
            "Decoupling Analysis: Economic/Visitor growth vs. Environmental footprint",
            "Normalized peer group indexing against national median benchmarks"
        ],
        data_inputs=[
            "data/processed/tourism_timeseries_2011_2025.csv",
            "data/processed/state_sustainability_snapshot.csv",
            "National aggregates from data/extracted_2026_compendium/national_tourism_statistics.csv"
        ]
    )


def render_ml_intelligence():
    render_placeholder(
        section_name="Machine Learning Intelligence",
        icon="🤖",
        planned_task="Task 5",
        overview="Predictive modeling, state clustering, and destination lifecycle classification using time series forecasting (Prophet/ARIMA), unsupervised clustering (K-Means/DBSCAN), and feature importance analysis.",
        planned_features=[
            "Unsupervised state typology clustering (Mass Tourism vs. Eco-Sensitive vs. Emerging)",
            "5-Year forward forecasting of domestic and foreign visits with uncertainty intervals",
            "Butler Destination Life Cycle stage classification (Exploration to Rejuvenation)",
            "Over-tourism vulnerability risk scoring and early warning signals"
        ],
        data_inputs=[
            "Full longitudinal panel (tourism 2011–2025 + environmental features)",
            "Calculated growth dynamics, foreign shares, and volatility indices",
            "Trained Scikit-Learn / Prophet pipeline artifacts"
        ]
    )


def render_planning_studio():
    render_placeholder(
        section_name="Sustainable Planning Studio",
        icon="🗺️",
        planned_task="Task 6",
        overview="Interactive scenario simulation and decision-support workspace allowing state tourism boards to simulate policy levers, tariff interventions, seasonal dispersal, and capacity constraints.",
        planned_features=[
            "Interactive 'What-If' policy levers: Footfall caps, green levies, seasonal subsidies",
            "Carrying capacity threshold alerts for ecologically sensitive hill/island states",
            "Visitor dispersal recommendation engine for crowded pilgrimage & leisure corridors",
            "Infrastructure strain index (water demand, waste generation per peak day)"
        ],
        data_inputs=[
            "State sustainability snapshot carrying capacity parameters",
            "Historical seasonal distribution coefficients",
            "Predictive elasticity estimates from ML models"
        ]
    )


def render_ai_policy_assistant():
    render_placeholder(
        section_name="AI Policy Assistant",
        icon="💡",
        planned_task="Task 8",
        overview="Context-aware conversational agent equipped with Retrieval-Augmented Generation (RAG) over official Indian tourism policies, responsible tourism guidelines, and state sustainability reports.",
        planned_features=[
            "Domain-specific RAG grounded in National & Kerala Sustainable Tourism Policies",
            "Natural language query interface for quantitative data extraction",
            "Automated citation of Ministry of Tourism guidelines and NITI Aayog frameworks",
            "Strategic gap analysis between state actions and national sustainability targets"
        ],
        data_inputs=[
            "research/policies/national_sustainable_tourism.pdf",
            "research/policies/kerala_responsible_tourism_2023.pdf",
            "Ministry of Tourism Compendium 2026 data footnotes & governance guidelines"
        ]
    )
