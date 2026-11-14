"""Task 4 — State Comparison Studio: transparent, descriptive state benchmarks."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from src.data_loader import load_tourism_data, load_sustainability_snapshot

BG, PANEL, FG, MUTED = '#071722', '#102735', '#e7f2f6', '#b4cbd4'
COLORS = ['#4cd2bd', '#ffb454', '#8ca9ff', '#ff7e93']


def style(fig, height=430):
    fig.update_layout(template='plotly_dark', paper_bgcolor=BG, plot_bgcolor=PANEL,
                      font=dict(color=FG, size=12), height=height,
                      margin=dict(l=45, r=30, t=50, b=50),
                      legend=dict(font=dict(color=FG)),
                      hoverlabel=dict(bgcolor=PANEL, font_color=FG))
    fig.update_xaxes(gridcolor='#294451', tickfont=dict(color=MUTED), title_font=dict(color=FG))
    fig.update_yaxes(gridcolor='#294451', tickfont=dict(color=MUTED), title_font=dict(color=FG))
    return fig


def prepare_comparison(tourism, snapshot, states, year):
    """Pure transformation, deliberately never modifies validated source frames."""
    current = tourism.loc[tourism['year'].eq(year)].copy()
    cols = ['state', 'domestic_visits', 'foreign_visits', 'total_visits', 'foreign_share_pct']
    current = current[cols].drop_duplicates('state')
    envcols = ['state', 'forest_cover_sq_km', 'groundwater_extraction_pct', 'sdg_score',
               'forest_assessment_year', 'groundwater_assessment_year', 'sdg_assessment_year']
    merged = current.merge(snapshot[envcols].drop_duplicates('state'), on='state', how='left')
    for col in cols[1:] + envcols[1:]:
        merged[col] = pd.to_numeric(merged[col], errors='coerce')
    # Year-over-year change calculated from raw visit counts, not rounded CSV growth rates.
    prev = tourism.loc[tourism['year'].eq(year - 1), ['state', 'total_visits']].rename(columns={'total_visits':'previous_visits'})
    merged = merged.merge(prev.drop_duplicates('state'), on='state', how='left')
    merged['growth_pct'] = np.where(merged['previous_visits'] > 0,
        100 * (merged['total_visits'] / merged['previous_visits'] - 1), np.nan)
    return merged[merged['state'].isin(states)].copy()


def render_state_comparison():
    st.title('⚖️ State Comparison Studio')
    st.caption('Compare reported tourist visits and contextual sustainability indicators across Indian States and UTs.')
    st.info('Tourism data and environmental indicators are from different reference years. Forest cover is an **area**, not forest density; groundwater extraction is state-wide, not tourism-attributable. No carrying capacity or environmental causality is inferred.')
    try:
        tourism = load_tourism_data().copy()
        snap = load_sustainability_snapshot().copy()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        st.error(f'Unable to load project datasets: {exc}')
        return
    tourism['state'] = tourism['state'].astype(str).str.strip()
    snap['state'] = snap['state'].astype(str).str.strip()
    years = sorted(tourism['year'].dropna().astype(int).unique(), reverse=True)
    if not years:
        st.warning('No tourism data found.')
        return
    options = sorted(set(tourism['state']) & set(snap['state']))
    defaults = [s for s in ['Uttar Pradesh', 'Rajasthan', 'Kerala'] if s in options]
    if len(defaults) < 2:
        defaults = options[:3]
    c1, c2 = st.columns([1, 3])
    with c1:
        year = st.selectbox('Tourism year', years, key='comparison_year')
    with c2:
        selected = st.multiselect('Compare 2–4 States / UTs', options, default=defaults, max_selections=4, key='comparison_states')
    if len(selected) < 2:
        st.warning('Choose at least two states to compare.')
        return
    df = prepare_comparison(tourism, snap, selected, year)
    missing = sorted(set(selected) - set(df['state']))
    if missing:
        st.warning(f'No tourism observations for {year}: {", ".join(missing)}')
    if len(df) < 2:
        st.warning('Choose two states with observations in the selected year.')
        return
    st.subheader('At-a-glance comparison')
    cards = st.columns(len(df))
    for i, (_, r) in enumerate(df.iterrows()):
        with cards[i]:
            st.markdown(f'**{r["state"]}**')
            st.metric('Total tourist visits', f'{r["total_visits"]/1e7:,.2f} Cr')
            st.metric('Foreign visitor share', f'{r["foreign_share_pct"]:.2f}%' if pd.notna(r['foreign_share_pct']) else 'N/A')
            st.metric('Year-on-year growth', f'{r["growth_pct"]:+.1f}%' if pd.notna(r['growth_pct']) else 'N/A')
    st.subheader('Tourism demand benchmark')
    metric_names = {'total_visits':'Total tourist visits', 'domestic_visits':'Domestic visits',
                    'foreign_visits':'Foreign visits', 'foreign_share_pct':'Foreign share (%)',
                    'growth_pct':'Year-on-year total visit growth (%)'}
    metric = st.selectbox('Tourism comparison metric', list(metric_names), format_func=metric_names.get, key='comparison_metric')
    plot = df.dropna(subset=[metric]).sort_values(metric, ascending=True)
    if not plot.empty:
        fig = px.bar(plot, x=metric, y='state', orientation='h', color='state',
                     color_discrete_sequence=COLORS, text=metric,
                     labels={'state':'', metric:metric_names[metric]}, title=f'{metric_names[metric]} · {year}')
        fig.update_traces(texttemplate='%{x:,.2f}' if metric.endswith('pct') else '%{x:,.3s}', textposition='outside', cliponaxis=False)
        fig.update_layout(showlegend=False)
        st.plotly_chart(style(fig), use_container_width=True)
    st.subheader('Environmental and SDG context')
    labels = {'forest_cover_sq_km':'Forest cover area (sq km) · assessment 2023',
              'groundwater_extraction_pct':'Groundwater extraction (%) · assessment 2024',
              'sdg_score':'SDG composite score · assessment 2023'}
    left, right = st.columns([1, 1])
    with left:
        indicator = st.selectbox('Contextual indicator', list(labels), format_func=labels.get, key='comparison_environment')
        available = df.dropna(subset=[indicator]).sort_values(indicator)
        if available.empty:
            st.warning('No comparable observations for this indicator.')
        else:
            fig = px.bar(available, x=indicator, y='state', orientation='h', color='state',
                         color_discrete_sequence=COLORS, text=indicator,
                         labels={'state':'', indicator:labels[indicator]}, title='State-level indicator (not caused by tourism)')
            fig.update_traces(texttemplate='%{x:,.1f}', textposition='outside', cliponaxis=False)
            fig.update_layout(showlegend=False)
            st.plotly_chart(style(fig), use_container_width=True)
    with right:
        st.markdown('**National peer median (states with available data)**')
        full = prepare_comparison(tourism, snap, list(set(tourism['state']) & set(snap['state'])), year)
        median = full[indicator].median()
        st.metric(labels[indicator], f'{median:,.2f}' if pd.notna(median) else 'N/A')
        st.caption('Unweighted median across reporting States/UTs, not a population- or visit-weighted national estimate.')
        st.markdown('**Selected-state values**')
        compare = df[['state', indicator]].copy()
        compare['Difference from peer median'] = compare[indicator] - median
        st.dataframe(compare.rename(columns={indicator:labels[indicator]}).round(2), hide_index=True, use_container_width=True)
    st.subheader('Historical tourism trajectories')
    history = tourism[tourism['state'].isin(selected) & tourism['year'].le(year)].copy()
    history['visits_crore'] = history['total_visits'] / 1e7
    fig = px.line(history, x='year', y='visits_crore', color='state', markers=True,
                  color_discrete_sequence=COLORS,
                  labels={'year':'Year', 'visits_crore':'Total visits (crore)', 'state':'State / UT'},
                  title='Reported total tourist visits over time')
    st.plotly_chart(style(fig, 440), use_container_width=True)
    st.subheader('Cross-indicator profile')
    st.caption('Relative percentile positions among reporting States/UTs for the selected tourism year. Higher percentile means a higher numerical value, **not necessarily better sustainability**. Missing values remain missing.')
    dimensions = {'total_visits':'Tourist visits', 'foreign_share_pct':'Foreign share',
                  'growth_pct':'Visit growth', 'forest_cover_sq_km':'Forest area',
                  'groundwater_extraction_pct':'Groundwater extraction', 'sdg_score':'SDG score'}
    ranked = full.copy()
    for col in dimensions:
        ranked[col] = ranked[col].rank(pct=True, method='average') * 100
    ranked = ranked.set_index('state')
    fig = go.Figure()
    for i, state in enumerate(selected):
        if state not in ranked.index:
            continue
        values = [ranked.loc[state, col] for col in dimensions]
        theta = list(dimensions.values())
        if any(pd.isna(v) for v in values):
            continue  # Do not fabricate missing radar dimensions.
        fig.add_trace(go.Scatterpolar(r=values + values[:1], theta=theta + theta[:1],
                        fill='toself', name=state, line_color=COLORS[i % len(COLORS)], opacity=0.75))
    if fig.data:
        fig.update_layout(polar=dict(bgcolor=PANEL, radialaxis=dict(range=[0, 100], tickfont=dict(color=MUTED), gridcolor='#36515c'),
                                     angularaxis=dict(tickfont=dict(color=FG), gridcolor='#36515c')))
        st.plotly_chart(style(fig, 480), use_container_width=True)
    else:
        st.warning('A complete six-indicator profile is unavailable for these states. Use the comparison table below instead.')
    st.subheader('Download comparison')
    export = df[['state', 'total_visits', 'domestic_visits', 'foreign_visits', 'foreign_share_pct',
                 'growth_pct', 'forest_cover_sq_km', 'groundwater_extraction_pct', 'sdg_score',
                 'forest_assessment_year', 'groundwater_assessment_year', 'sdg_assessment_year']].copy()
    st.dataframe(export.round(2), use_container_width=True, hide_index=True)
    st.download_button('⬇️ Download selected-state comparison (CSV)', export.to_csv(index=False).encode('utf-8'),
                       file_name=f'sustaintour_state_comparison_{year}.csv', mime='text/csv')
    with st.expander('Data sources, interpretation and limitations'):
        st.markdown('''- **Tourism:** validated Ministry of Tourism / RBI state-level panel, selected year (2011–2025).
- **Forest cover:** snapshot assessment year 2023, absolute area (sq km), **not** share of land or tourism impact.
- **Groundwater:** snapshot assessment year 2024, extraction as percentage of assessed resource; not tourism-specific.
- **SDG:** snapshot assessment year 2023, composite score; not a dedicated tourism sustainability index.
- State-level figures are kept as published, including source caveats. Cross-year comparisons are contextual and cannot establish causality.
- Rankings and radar percentiles describe relative magnitudes only; they do not rank sustainability quality.
- Annual visit counts may reflect repeated visits, not unique individuals.''')
