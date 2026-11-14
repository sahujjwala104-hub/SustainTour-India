"""Task 6: hypothetical state-level demand redistribution planning simulator."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.data_loader import load_tourism_data

BG, PANEL, FG, TEAL, ORANGE = '#071722', '#102735', '#e7f2f6', '#4cd2bd', '#ffb454'


def simulate_redistribution(frame, source, destinations, fraction, weights=None):
    """Return a new scenario; never mutate source data. Integer visits conserved exactly."""
    if not 0 <= fraction <= 1:
        raise ValueError('Redistribution fraction must be between 0 and 1.')
    if source in destinations or not destinations or len(set(destinations)) != len(destinations):
        raise ValueError('Choose distinct destination states excluding the source.')
    result = frame.copy(deep=True).reset_index(drop=True)
    if result['state'].duplicated().any():
        raise ValueError('Expected one record per state for the selected year.')
    if source not in set(result['state']) or not set(destinations).issubset(set(result['state'])):
        raise ValueError('A selected state has no record in this year.')
    original = result['domestic_visits'].astype('int64').to_numpy()
    source_idx = result.index[result['state'].eq(source)][0]
    moved = int(round(int(original[source_idx]) * fraction))
    if weights is None:
        weights = np.ones(len(destinations), dtype=float)
    weights = np.asarray(weights, dtype=float)
    if len(weights) != len(destinations) or not np.all(np.isfinite(weights)) or np.any(weights < 0) or weights.sum() <= 0:
        raise ValueError('Allocation weights must be finite, nonnegative and nonzero.')
    shares = moved * weights / weights.sum()
    allocations = np.floor(shares).astype('int64')
    remainder = moved - int(allocations.sum())
    order = np.argsort(-(shares - allocations), kind='stable')
    allocations[order[:remainder]] += 1
    revised = original.copy()
    revised[source_idx] -= moved
    for dest, count in zip(destinations, allocations):
        revised[result.index[result['state'].eq(dest)][0]] += int(count)
    result['baseline_domestic_visits'] = original
    result['scenario_domestic_visits'] = revised
    result['change_visits'] = revised - original
    result['baseline_total_visits'] = original + result['foreign_visits'].astype('int64').to_numpy()
    result['scenario_total_visits'] = revised + result['foreign_visits'].astype('int64').to_numpy()
    assert int(revised.sum()) == int(original.sum())
    return result, moved


def concentration(values):
    """HHI on state shares; 0-10000 scale, higher means more concentrated."""
    x = np.asarray(values, dtype=float)
    total = x.sum()
    return float(10000 * np.square(x / total).sum()) if total > 0 else 0.0


def chart_style(fig, height=420):
    fig.update_layout(template='plotly_dark', paper_bgcolor=BG, plot_bgcolor=PANEL,
                      font=dict(color=FG), height=height, margin=dict(l=25, r=20, t=55, b=45),
                      hoverlabel=dict(bgcolor=PANEL, font_color=FG),
                      legend=dict(font=dict(color=FG)))
    fig.update_xaxes(gridcolor='#294451', tickfont=dict(color=FG), title_font=dict(color=FG))
    fig.update_yaxes(gridcolor='#294451', tickfont=dict(color=FG), title_font=dict(color=FG))
    return fig


def render_planning_studio():
    st.title('🗺️ Sustainable Planning Studio')
    st.caption('Task 6 · Interactive, hypothetical tourism demand redistribution across Indian States and UTs')
    st.info('**Scenario, not forecast:** This tool reallocates reported domestic tourist visits mathematically. It does not model actual traveler decisions, destination capacity, carbon emissions, infrastructure, or environmental impacts. No destination is assumed able to absorb the simulated demand.')
    try:
        data = load_tourism_data().copy()
    except (FileNotFoundError, ValueError, KeyError) as exc:
        st.error(f'Could not load tourism data: {exc}')
        return
    years = sorted(data['year'].dropna().astype(int).unique(), reverse=True)
    year = st.selectbox('Select tourism year', years, key='planning_year')
    frame = data.loc[data['year'].eq(year), ['state', 'domestic_visits', 'foreign_visits']].copy()
    frame = frame.dropna(subset=['state', 'domestic_visits', 'foreign_visits']).sort_values('state')
    options = frame['state'].tolist()
    if len(options) < 2:
        st.warning('Not enough states are available for the selected year.')
        return
    left, right = st.columns(2)
    default_source = options.index('Uttar Pradesh') if 'Uttar Pradesh' in options else 0
    with left:
        source = st.selectbox('Source state (reduce visits)', options, index=default_source, key='planning_source')
        fraction_pct = st.slider('Domestic visits to redistribute (%)', min_value=0, max_value=30, value=10, step=1, key='planning_fraction')
    destinations_available = [s for s in options if s != source]
    defaults = [s for s in ['Rajasthan', 'Madhya Pradesh', 'Uttarakhand'] if s in destinations_available]
    if not defaults:
        defaults = destinations_available[:2]
    with right:
        destinations = st.multiselect('Receiving states / UTs', destinations_available,
                                      default=defaults, key='planning_destinations')
        allocation = st.radio('Distribution method', ['Equal share', 'Custom shares'], horizontal=True, key='planning_method')
    if not destinations:
        st.warning('Select at least one receiving state.')
        return
    weights = None
    if allocation == 'Custom shares':
        st.caption('Set relative allocation weights. They are normalized automatically to 100%.')
        cols = st.columns(min(len(destinations), 4))
        weights = []
        for i, dest in enumerate(destinations):
            with cols[i % len(cols)]:
                weights.append(st.number_input(f'{dest} weight', min_value=0.0, max_value=100.0,
                                               value=1.0, step=0.5, key=f'planning_weight_{dest}'))
    try:
        scenario, moved = simulate_redistribution(frame, source, destinations, fraction_pct / 100, weights)
    except ValueError as exc:
        st.warning(str(exc))
        return
    before_hhi = concentration(scenario['baseline_domestic_visits'])
    after_hhi = concentration(scenario['scenario_domestic_visits'])
    national = int(scenario['baseline_domestic_visits'].sum())
    top_before = float(scenario['baseline_domestic_visits'].max() / national * 100) if national else 0
    top_after = float(scenario['scenario_domestic_visits'].max() / national * 100) if national else 0
    st.subheader('Scenario overview')
    k1, k2, k3, k4 = st.columns(4)
    k1.metric('Visits redistributed', f'{moved:,.0f}')
    k2.metric('National domestic visits', f'{national:,.0f}', help='Conserved exactly in the simulation')
    k3.metric('Concentration (HHI)', f'{after_hhi:,.1f}', delta=f'{after_hhi - before_hhi:+,.1f}', delta_color='inverse')
    k4.metric('Largest state share', f'{top_after:.2f}%', delta=f'{top_after-top_before:+.2f} pp', delta_color='inverse')
    st.caption('HHI = sum of squared state-level domestic visit shares × 10,000. Lower HHI means visits are more evenly distributed across states, not necessarily more environmentally sustainable.')
    changed = scenario.loc[scenario['change_visits'].ne(0)].copy()
    changed = changed.sort_values('baseline_domestic_visits', ascending=True)
    if not changed.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(y=changed['state'], x=changed['baseline_domestic_visits'], orientation='h', name='Baseline', marker_color=ORANGE))
        fig.add_trace(go.Bar(y=changed['state'], x=changed['scenario_domestic_visits'], orientation='h', name='Scenario', marker_color=TEAL))
        fig.update_layout(barmode='group', title='Affected states · before vs after', xaxis_title='Domestic tourist visits', yaxis_title='', height=max(370, 90 * len(changed)))
        st.plotly_chart(chart_style(fig, max(370, 90 * len(changed))), use_container_width=True)
    a, b = st.columns(2)
    with a:
        fig = go.Figure(go.Bar(x=['Baseline', 'Scenario'], y=[before_hhi, after_hhi], marker_color=[ORANGE, TEAL], text=[f'{before_hhi:,.1f}', f'{after_hhi:,.1f}'], textposition='outside'))
        fig.update_layout(title='Tourism concentration (HHI)', yaxis_title='HHI', showlegend=False)
        st.plotly_chart(chart_style(fig), use_container_width=True)
    with b:
        fig = go.Figure(go.Bar(x=['Baseline', 'Scenario'], y=[top_before, top_after], marker_color=[ORANGE, TEAL], text=[f'{top_before:.2f}%', f'{top_after:.2f}%'], textposition='outside'))
        fig.update_layout(title='Largest state share of domestic visits', yaxis_title='Share (%)', showlegend=False)
        st.plotly_chart(chart_style(fig), use_container_width=True)
    st.subheader('Planning interpretation')
    if after_hhi < before_hhi - 1e-8:
        st.success(f'This hypothetical allocation reduces state-level concentration by {before_hhi - after_hhi:,.1f} HHI points. It may be worth investigating receiving states for infrastructure and ecological feasibility before considering such a policy.')
    elif after_hhi > before_hhi + 1e-8:
        st.warning(f'This hypothetical allocation increases state-level concentration by {after_hhi - before_hhi:,.1f} HHI points. It does not achieve a more even state-level distribution.')
    else:
        st.info('This allocation leaves the concentration indicator effectively unchanged.')
    st.markdown('**Planning checks before real-world action:** visitor carrying capacity, transport accessibility, local livelihoods, protected areas, seasonality, accommodation, water availability, and community consent. These are not measured by this simulator.')
    st.subheader('Scenario data')
    st.dataframe(scenario.sort_values('change_visits', ascending=False), use_container_width=True, hide_index=True)
    st.download_button('⬇️ Download scenario CSV', data=scenario.to_csv(index=False).encode('utf-8'),
                       file_name=f'sustaintour_scenario_{year}.csv', mime='text/csv')
    with st.expander('Methodology & limitations'):
        st.markdown('''The simulation subtracts a user-selected percentage of **domestic tourist visits** from one source state and distributes the same integer number of visits to selected states. Equal or custom proportional allocations are supported. Rounding remainders are allocated deterministically, so the national sum is conserved. Foreign visits remain unchanged. Baseline values are read from the validated tourism panel and are never overwritten.\n\nThis is a **static counterfactual**, not an econometric causal model, policy impact estimate, forecast, recommendation engine, or verified sustainability score. A lower concentration index alone does not establish improved environmental outcomes. National totals are calculated from the state-level dataset and may differ slightly from published national aggregates.''')
