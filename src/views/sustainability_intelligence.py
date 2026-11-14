"""Task 3: Sustainability intelligence from validated, non-synchronous indicators.

Environmental measures are contextual indicators, NOT tourism-caused impacts.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_sustainability_snapshot, load_tourism_data, load_environmental_data

BG = '#071722'
PANEL = '#102735'
FONT = '#e7f2f6'
MUTED = '#b4cbd4'
TEAL = '#4cd2bd'


def _style(fig, height=420):
    fig.update_layout(
        template='plotly_dark', paper_bgcolor=BG, plot_bgcolor=PANEL,
        font=dict(color=FONT, size=12), height=height,
        margin=dict(l=20, r=30, t=45, b=30),
        legend=dict(font=dict(color=FONT)),
        hoverlabel=dict(bgcolor=PANEL, font_color=FONT),
    )
    fig.update_xaxes(tickfont=dict(color=MUTED), title_font=dict(color=FONT), gridcolor='#2a4450')
    fig.update_yaxes(tickfont=dict(color=MUTED), title_font=dict(color=FONT), gridcolor='#2a4450')
    return fig


def _latest_frame():
    snap = load_sustainability_snapshot().copy()
    tourism = load_tourism_data().copy()
    snap['state'] = snap['state'].astype(str).str.strip()
    tourism['state'] = tourism['state'].astype(str).str.strip()
    for col in ['forest_cover_sq_km', 'groundwater_extraction_pct', 'sdg_score', 'completeness_count']:
        snap[col] = pd.to_numeric(snap[col], errors='coerce')
    for col in ['total_visits', 'domestic_visits', 'foreign_visits']:
        tourism[col] = pd.to_numeric(tourism[col], errors='coerce')
    # One row per state for selected tourism year; environment remains snapshot-year.
    return snap, tourism


def render_sustainability_intelligence():
    st.title('🌿 Sustainability Intelligence')
    st.caption('Tourism demand in context with forest cover, groundwater extraction and SDG performance')
    st.info('Environmental indicators are **state-level contextual measures**, not measured impacts of tourism. '
            'The source years differ: tourism 2011–2025, forest 2023, groundwater 2024 and SDG 2023. '
            'Comparisons show associations only; they do not establish causation or carrying capacity.')
    try:
        snap, tourism = _latest_frame()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        st.error(f'Unable to load validated sustainability datasets: {exc}')
        return

    years = sorted(tourism['year'].dropna().astype(int).unique().tolist(), reverse=True)
    if not years:
        st.warning('No tourism years available.')
        return
    c1, c2 = st.columns([1, 2])
    with c1:
        year = st.selectbox('Tourism reference year', years, index=0, key='sustain_year')
    with c2:
        states = sorted(set(snap['state']) & set(tourism['state']))
        chosen = st.multiselect('States / UTs', states, default=states, key='sustain_states')
    if not chosen:
        st.warning('Select at least one state to continue.')
        return

    current = tourism.loc[tourism['year'].eq(year), ['state', 'total_visits', 'domestic_visits', 'foreign_visits']].drop_duplicates('state')
    df = snap.merge(current, on='state', how='left', suffixes=('_snapshot', ''))
    df = df[df['state'].isin(chosen)].copy()
    df['total_visits'] = pd.to_numeric(df['total_visits'], errors='coerce')
    available = df.dropna(subset=['total_visits'])
    if available.empty:
        st.warning('No tourism observations for these states in the selected year.')
        return

    a,b,c,d = st.columns(4)
    a.metric('Tourism visits', f"{available['total_visits'].sum()/1e7:,.2f} Cr")
    b.metric('States with tourism data', f'{len(available)} / {len(df)}')
    c.metric('Median groundwater extraction', f"{df['groundwater_extraction_pct'].median():.1f}%" if df['groundwater_extraction_pct'].notna().any() else 'N/A')
    d.metric('Median SDG score', f"{df['sdg_score'].median():.0f}" if df['sdg_score'].notna().any() else 'N/A')
    st.caption('Metrics summarize the selected states, not the entire country unless all states are selected. '
               'Medians are unweighted across states; environmental data use their own assessment years.')

    st.subheader('Tourism demand and environmental context')
    left, right = st.columns(2)
    with left:
        x_metric = st.selectbox('Contextual indicator',
            ['groundwater_extraction_pct', 'sdg_score', 'forest_cover_sq_km'],
            format_func=lambda s: {'groundwater_extraction_pct':'Groundwater extraction (%)',
                                    'sdg_score':'SDG score', 'forest_cover_sq_km':'Forest cover (sq km)'}[s])
        points = available.dropna(subset=[x_metric]).copy()
        if points.empty:
            st.warning('No matched observations for this indicator.')
        else:
            fig = px.scatter(points, x=x_metric, y='total_visits', hover_name='state',
                color='sdg_score' if points['sdg_score'].notna().any() else None,
                color_continuous_scale='Teal',
                labels={'total_visits':'Tourist visits', 'groundwater_extraction_pct':'Groundwater extraction (%)',
                        'sdg_score':'SDG score', 'forest_cover_sq_km':'Forest cover (sq km)'},
                title=f'Tourism visits ({year}) vs contextual indicator')
            st.plotly_chart(_style(fig), use_container_width=True)
    with right:
        rank = available.nlargest(12, 'total_visits').sort_values('total_visits')
        fig = px.bar(rank, x='total_visits', y='state', orientation='h',
                     color_discrete_sequence=[TEAL], title=f'Highest reported tourism demand ({year})',
                     labels={'total_visits':'Total tourist visits', 'state':''})
        st.plotly_chart(_style(fig), use_container_width=True)

    st.subheader('State sustainability indicator comparison')
    indicator = st.selectbox('Compare states by',
        ['groundwater_extraction_pct', 'sdg_score', 'forest_cover_sq_km'],
        format_func=lambda s: {'groundwater_extraction_pct':'Groundwater extraction (%) · 2024',
                                'sdg_score':'SDG score · 2023',
                                'forest_cover_sq_km':'Forest cover (sq km) · 2023'}[s], key='sustain_compare')
    ranked = df.dropna(subset=[indicator]).sort_values(indicator, ascending=False)
    if not ranked.empty:
        fig = px.bar(ranked, x='state', y=indicator, color=indicator, color_continuous_scale='Teal',
            title='State-level indicator (not attributable to tourism)', labels={'state':'State / UT'})
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(_style(fig, 450), use_container_width=True)
    else:
        st.warning('No data available for this indicator.')

    st.subheader('Historical environmental indicator trends')
    forest, groundwater, sdg = load_environmental_data()
    history_choice = st.radio('Indicator history', ['Forest cover', 'Groundwater extraction', 'SDG score'], horizontal=True)
    source = {'Forest cover':(forest,'forest_cover_sq_km','Forest cover (sq km)'),
              'Groundwater extraction':(groundwater,'groundwater_extraction_pct','Groundwater extraction (%)'),
              'SDG score':(sdg,'sdg_score','SDG score')}[history_choice]
    historical, val, label = source
    historical = historical[historical['state'].isin(chosen)].copy()
    historical['year'] = pd.to_numeric(historical['year'], errors='coerce')
    historical[val] = pd.to_numeric(historical[val], errors='coerce')
    historical = historical.dropna(subset=['year', val])
    if not historical.empty:
        fig = px.line(historical, x='year', y=val, color='state', markers=True,
                      title=f'{history_choice} — available assessment years', labels={val:label, 'year':'Assessment year'})
        st.plotly_chart(_style(fig, 450), use_container_width=True)
    else:
        st.warning('No historical observations for the selected states.')

    st.subheader('Tourism demand concentration')
    all_year = tourism[tourism['year'].eq(year)].dropna(subset=['total_visits']).copy()
    national = all_year['total_visits'].sum()
    top5_share = 100 * all_year.nlargest(5, 'total_visits')['total_visits'].sum() / national if national else float('nan')
    st.metric(f'Top 5 states’ share of reported visits ({year})', f'{top5_share:.1f}%' if pd.notna(top5_share) else 'N/A')
    st.caption('Computed across all states available in the selected year, regardless of the state filter. '
               'This measures geographic concentration of reported visits, not congestion at destinations.')

    st.subheader('Planning evidence table')
    display = df[['state','total_visits','forest_cover_sq_km','groundwater_extraction_pct','sdg_score',
                  'forest_assessment_year','groundwater_assessment_year','sdg_assessment_year','data_caveat']].copy()
    st.dataframe(display.sort_values('total_visits', ascending=False), use_container_width=True, hide_index=True)
    st.download_button('Download selected indicators (CSV)', display.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f'sustaintour_context_{year}.csv', mime='text/csv')

    with st.expander('Methodology, limitations and data sources'):
        st.markdown('''**Data sources:** Ministry of Tourism tourism panel; Forest Survey of India forest-cover data;
Central Ground Water Board groundwater extraction; NITI Aayog SDG India Index.

**Interpretation:** High groundwater extraction is a statewide resource-use context; it cannot be attributed
specifically to visitors. Forest-cover area is not forest-cover percentage, and larger states naturally tend
to have more forest area. SDG score is a broad development measure, not a tourism-specific score.

**Time alignment:** Tourism year is selectable; the sustainability snapshot uses source years recorded in
the evidence table. Do not interpret the cross-sectional scatter as a same-year causal relationship.

**Data quality:** Missing values are not replaced with zeros. State coverage may differ by year. Original
validated CSV files are never modified by this dashboard. The project does not estimate carbon footprint,
carrying capacity, destination overcrowding, or a scientifically validated sustainability index.''')
