"""Task 5: Transparent, small-sample tourism forecasting and state clustering."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from src.data_loader import load_tourism_data

BG = '#071722'
FG = '#e7f2f6'
TEAL = '#4cd2bd'
ORANGE = '#ffb454'


def decorate(fig, height=430):
    fig.update_layout(template='plotly_dark', paper_bgcolor=BG, plot_bgcolor='#102735',
                      font=dict(color=FG), height=height, margin=dict(l=40,r=20,t=45,b=45),
                      hoverlabel=dict(bgcolor='#102735', font_color=FG))
    fig.update_xaxes(gridcolor='#294451')
    fig.update_yaxes(gridcolor='#294451')
    return fig


def forecast_logtrend(values, horizon, damp=0.8):
    """Damped log-linear forecast, robust to changing order-of-magnitude volumes."""
    y = np.asarray(values, dtype=float)
    if len(y) < 4 or not np.all(np.isfinite(y)) or np.any(y < 0):
        raise ValueError('At least four nonnegative annual observations are required.')
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, np.log1p(y), 1)
    slope = float(np.clip(slope, -0.20, 0.20))
    last = float(np.log1p(y[-1]))
    steps = np.arange(1, horizon + 1, dtype=float)
    # A damped extrapolation; not a confidence interval or causal projection.
    predicted = np.expm1(last + slope * np.cumsum(damp ** (steps - 1)))
    return np.maximum(predicted, 0)


def rolling_evaluation(frame):
    """One-year-ahead expanding-window backtest, no future leakage."""
    values = frame['total_visits'].to_numpy(dtype=float)
    if len(values) < 7:
        return pd.DataFrame()
    records = []
    for i in range(5, len(values)):
        actual = values[i]
        naive = values[i-1]
        trend = forecast_logtrend(values[:i], 1)[0]
        records.extend([{'year': int(frame.iloc[i]['year']), 'model':'Last-year baseline', 'actual':actual, 'predicted':naive},
                        {'year': int(frame.iloc[i]['year']), 'model':'Damped log trend', 'actual':actual, 'predicted':trend}])
    return pd.DataFrame(records)


def build_features(df):
    rows = []
    for state, part in df.groupby('state'):
        part = part.sort_values('year')
        # Require enough history; exclude extreme zero baselines from growth calculations.
        if len(part) < 8:
            continue
        last = part.iloc[-1]
        vals = part['total_visits'].to_numpy(dtype=float)
        rates = np.diff(np.log1p(vals))
        recent = rates[-5:]
        rows.append({'state':state, 'latest_year':int(last['year']),
                     'latest_visits':float(last['total_visits']),
                     'log_volume':float(np.log1p(last['total_visits'])),
                     'mean_log_growth':float(np.clip(np.mean(recent), -0.8, 0.8)),
                     'growth_volatility':float(np.clip(np.std(recent), 0, 1.5)),
                     'foreign_share_pct':float(last['foreign_share_pct'])})
    return pd.DataFrame(rows)


def render_ml_intelligence():
    st.title('Machine Learning Intelligence')
    st.caption('State-level tourism forecasting, historical backtesting and unsupervised tourism-profile clustering.')
    st.info('These are exploratory statistical models of **reported tourist visits**, not unique people, carrying capacity, environmental impact or guaranteed future demand. The short annual histories and exceptional pandemic/event years limit predictive reliability.')
    try:
        df = load_tourism_data().copy()
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df['total_visits'] = pd.to_numeric(df['total_visits'], errors='coerce')
        df['foreign_share_pct'] = pd.to_numeric(df['foreign_share_pct'], errors='coerce')
        df = df.dropna(subset=['state','year','total_visits']).sort_values(['state','year'])
    except Exception as exc:
        st.error(f'Could not load tourism data: {exc}')
        return
    tab_forecast, tab_cluster = st.tabs(['📈 Demand Forecasting', '🧩 State Clustering'])
    with tab_forecast:
        states = sorted(df['state'].unique())
        default = states.index('Uttar Pradesh') if 'Uttar Pradesh' in states else 0
        a,b = st.columns([2,1])
        state = a.selectbox('Choose a State or UT', states, index=default)
        horizon = b.slider('Forecast horizon (years)', 1, 5, 3)
        part = df[df['state'].eq(state)].sort_values('year').drop_duplicates('year')
        if len(part) < 7:
            st.warning('Insufficient historical observations for a useful backtest.')
        else:
            y = part['total_visits'].to_numpy(dtype=float)
            future_years = np.arange(int(part['year'].max())+1, int(part['year'].max())+1+horizon)
            forecasts = forecast_logtrend(y, horizon)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=part['year'], y=y, mode='lines+markers', name='Reported visits', line_color=TEAL))
            fig.add_trace(go.Scatter(x=np.r_[part['year'].iloc[-1], future_years], y=np.r_[y[-1],forecasts], mode='lines+markers', name='Exploratory forecast', line=dict(color=ORANGE,dash='dash')))
            fig.update_layout(title=f'{state}: historical visits and indicative forecast', xaxis_title='Year', yaxis_title='Reported tourist visits', hovermode='x unified')
            st.plotly_chart(decorate(fig), use_container_width=True)
            fc = pd.DataFrame({'Year':future_years, 'Forecast visits (rounded)':np.rint(forecasts).astype('int64')})
            st.dataframe(fc, hide_index=True, use_container_width=True)
            st.download_button('Download forecast CSV', fc.to_csv(index=False), file_name='tourism_forecast.csv', mime='text/csv')
            backtest = rolling_evaluation(part)
            if not backtest.empty:
                summary = backtest.assign(abs_error=lambda d:abs(d.actual-d.predicted), squared_error=lambda d:(d.actual-d.predicted)**2)
                scores = summary.groupby('model').agg(MAE=('abs_error','mean'), MSE=('squared_error','mean')).reset_index()
                scores['RMSE'] = np.sqrt(scores.pop('MSE'))
                st.subheader('Historical one-year-ahead evaluation')
                st.dataframe(scores.style.format({'MAE':'{:,.0f}','RMSE':'{:,.0f}'}), hide_index=True, use_container_width=True)
                st.caption(f'Expanding-window evaluation over {backtest.year.nunique()} years. Both models are evaluated on the same held-out years; smaller MAE/RMSE is better. No uncertainty interval is claimed.')
                plot = px.line(backtest, x='year', y='predicted', color='model', markers=True, title='Backtested predictions vs actual visits')
                plot.add_trace(go.Scatter(x=part['year'],y=part['total_visits'],name='Actual',line=dict(color=TEAL,width=3)))
                st.plotly_chart(decorate(plot), use_container_width=True)
            with st.expander('Forecast methodology and limitations'):
                st.write('The last-year baseline predicts the previous observed count. The alternative fits a log-linear trend to available training history, caps extreme annual growth and damps future changes. Forecasts are scenarios, not official projections. Structural breaks, COVID-19, reporting differences and major events can produce large errors. Model evaluation uses strictly earlier years to predict each subsequent year.')
    with tab_cluster:
        st.subheader('Tourism profile clustering')
        st.caption('Groups states by visit scale, recent log growth, growth volatility and foreign visitor share. Cluster numbers are arbitrary descriptive labels, not sustainability ratings.')
        features = build_features(df)
        cols = ['log_volume','mean_log_growth','growth_volatility','foreign_share_pct']
        features = features.replace([np.inf,-np.inf], np.nan).dropna(subset=cols)
        if len(features) < 6:
            st.warning('Not enough complete state histories for clustering.')
        else:
            k = st.slider('Number of clusters',2,min(6,len(features)-1),3)
            X = StandardScaler().fit_transform(features[cols])
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            features['cluster'] = ['Cluster '+str(v+1) for v in model.fit_predict(X)]
            silhouette = silhouette_score(X, model.labels_) if k < len(features) else float('nan')
            c1,c2 = st.columns(2)
            c1.metric('States clustered', len(features))
            c2.metric('Silhouette score', f'{silhouette:.2f}')
            fig = px.scatter(features, x='log_volume', y='mean_log_growth', color='cluster', size='latest_visits',
                             hover_name='state', hover_data=['foreign_share_pct','growth_volatility','latest_year'],
                             title='Tourism profiles: scale vs recent growth', size_max=28)
            st.plotly_chart(decorate(fig,500), use_container_width=True)
            st.subheader('Cluster membership')
            display = features[['state','cluster','latest_year','latest_visits','mean_log_growth','growth_volatility','foreign_share_pct']].sort_values(['cluster','state']).copy()
            display['recent_growth_pct_approx'] = np.expm1(display.pop('mean_log_growth'))*100
            st.dataframe(display, hide_index=True, use_container_width=True)
            st.download_button('Download cluster assignments CSV', display.to_csv(index=False), file_name='tourism_clusters.csv',mime='text/csv')
            with st.expander('Clustering methodology and limitations'):
                st.write('K-Means is fitted to standardized features; a fixed random seed ensures reproducibility. Recent growth is the mean of up to five year-over-year log changes; volatility is their standard deviation. The silhouette score describes geometric separation, not policy quality. Cluster membership depends on the chosen k, feature choices and reporting inconsistencies. No ecological capacity or tourism causation is inferred.')
