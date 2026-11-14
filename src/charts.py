"""
charts.py
=========
Interactive, publication-quality Plotly chart builders for SustainTour India.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from .constants import THEME_COLORS
from .geo_utils import format_indian_number, format_full_number, INDIA_MAP_CENTER, INDIA_MAP_ZOOM


def create_india_choropleth(
    df_prepared: pd.DataFrame,
    geojson_data: Dict[str, Any],
    metric: str = "domestic_visits",
    year: int = 2025
) -> go.Figure:
    """
    Build interactive choropleth map of India at State/UT level.
    Uses 'open-street-map' or 'carto-positron' basemap (tokenless).
    """
    metric_labels = {
        "domestic_visits": "Domestic Tourist Visits",
        "foreign_visits": "Foreign Tourist Visits",
        "total_visits": "Total Tourist Visits",
        "foreign_share_pct": "Foreign Tourist Share (%)",
        "domestic_yoy_growth_pct": "Domestic YoY Growth (%)"
    }
    
    label = metric_labels.get(metric, metric)
    
    # Choose color scale
    if metric == "foreign_visits":
        color_scale = "Blues"
    elif metric == "foreign_share_pct":
        color_scale = "Purples"
    elif metric == "domestic_yoy_growth_pct":
        color_scale = "RdYlGn"
    else:
        color_scale = "Tealgrn"
        
    fig = px.choropleth_map(
        df_prepared,
        geojson=geojson_data,
        featureidkey="properties.state",
        locations="geojson_state",
        color=metric,
        color_continuous_scale=color_scale,
        map_style="carto-positron",
        center=INDIA_MAP_CENTER,
        zoom=INDIA_MAP_ZOOM,
        opacity=0.82,
        custom_data=[
            "state",
            "hover_domestic",
            "hover_foreign",
            "hover_total",
            "hover_share",
            "hover_growth",
            "annotation",
            "iso_code"
        ]
    )
    
    # Custom hover template
    hovertemplate = (
        "<b>%{customdata[0]}</b> (%{customdata[7]})<br>"
        "<b>Year:</b> " + str(year) + "<br>"
        "------------------------------------<br>"
        "<b>" + label + ":</b> %{z}<br>"
        "<b>Domestic Visits:</b> %{customdata[1]}<br>"
        "<b>Foreign Visits:</b> %{customdata[2]}<br>"
        "<b>Total Visits:</b> %{customdata[3]}<br>"
        "<b>Foreign Share:</b> %{customdata[4]}<br>"
        "<b>Domestic YoY Growth:</b> %{customdata[5]}<br>"
        "<b>Status / Caveat:</b> <i>%{customdata[6]}</i>"
        "<extra></extra>"
    )
    fig.update_traces(hovertemplate=hovertemplate)
    
    fig.update_layout(
        margin={"r": 0, "t": 10, "l": 0, "b": 0},
        height=620,
        coloraxis_colorbar=dict(
            title=dict(text=label, font=dict(size=12, family="Plus Jakarta Sans")),
            thickness=16,
            len=0.75,
            x=0.02,
            y=0.5,
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#CBD5E1",
            borderwidth=1
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_rankings_bar_chart(
    df_rankings: pd.DataFrame,
    metric: str = "domestic_visits",
    title: str = "Top 10 States",
    ascending: bool = False,
    color_scale: str = "Teal"
) -> go.Figure:
    """High-contrast state ranking bars for the dark SustainTour theme."""
    metric_labels = {
        "domestic_visits": "Domestic Visits",
        "foreign_visits": "Foreign Visits",
        "total_visits": "Total Visits",
        "foreign_share_pct": "Foreign Share (%)"
    }
    label = metric_labels.get(metric, metric)
    # Largest at top for Top 10, smallest at top for Bottom 10.
    df_plot = df_rankings.sort_values(metric, ascending=not ascending).copy()
    if metric == "foreign_share_pct":
        labels = df_plot[metric].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
    else:
        labels = df_plot[metric].apply(format_indian_number)

    bar_color = "#38BDB2" if not ascending else "#F2A66A"
    fig = go.Figure(go.Bar(
        y=df_plot["state"], x=df_plot[metric], orientation="h",
        text=labels, textposition="outside", cliponaxis=False,
        textfont=dict(size=12, color="#F2F8FC"),
        marker=dict(color=bar_color, line=dict(color="rgba(255,255,255,0.18)", width=0.5)),
        hovertemplate="<b>%{y}</b><br>" + label + ": %{x:,.2f}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=17, color="#F4FAFF"), x=0.01),
        height=440,
        margin=dict(l=10, r=95, t=55, b=55),
        font=dict(family="Arial, sans-serif", color="#DCEAF2"),
        xaxis=dict(title=dict(text=label, font=dict(color="#C7D9E4", size=12)),
                   tickfont=dict(color="#BFD3DF", size=11),
                   showgrid=True, gridcolor="rgba(184,214,231,0.15)",
                   zeroline=False, rangemode="tozero", automargin=True),
        yaxis=dict(tickfont=dict(color="#E4F0F7", size=12),
                   showgrid=False, automargin=True),
        bargap=0.27,
        paper_bgcolor="#071722", plot_bgcolor="#071722",
        showlegend=False,
        uniformtext=dict(mode="show", minsize=10)
    )
    return fig


def create_national_trend_chart(
    df_national: pd.DataFrame,
    metric: str = "both"
) -> go.Figure:
    """
    National trendline chart for domestic and/or foreign tourist visits (2011–2025).
    """
    fig = go.Figure()
    
    if metric in ["both", "domestic"]:
        fig.add_trace(go.Scatter(
            x=df_national["year"],
            y=df_national["domestic_visits"],
            name="Domestic Tourist Visits",
            mode="lines+markers",
            line=dict(color="#0F766E", width=3.2),
            marker=dict(size=7, color="#0F766E", symbol="circle"),
            hovertemplate="<b>Year %{x}</b><br>Domestic Visits: %{y:,}<extra></extra>"
        ))
        
    if metric in ["both", "foreign"]:
        fig.add_trace(go.Scatter(
            x=df_national["year"],
            y=df_national["foreign_visits"],
            name="Foreign Tourist Visits",
            mode="lines+markers",
            line=dict(color="#0284C7", width=2.8, dash="dot"),
            marker=dict(size=6, color="#0284C7", symbol="square"),
            yaxis="y2" if metric == "both" else "y",
            hovertemplate="<b>Year %{x}</b><br>Foreign Visits: %{y:,}<extra></extra>"
        ))
        
    # Annotate COVID-19 dip and Kumbh Mela
    fig.add_vrect(
        x0=2019.8, x1=2021.2,
        fillcolor="#FEE2E2", opacity=0.45,
        layer="below", line_width=0,
        annotation_text="COVID-19 Disruption",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#991B1B")
    )
    
    layout_args = dict(
        title=dict(
            text="All-India Annual Tourism Trajectory (2011–2025)",
            font=dict(size=15, family="Plus Jakarta Sans", color="#0F172A")
        ),
        margin=dict(l=10, r=20, t=50, b=10),
        height=380,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, family="Plus Jakarta Sans")
        ),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=12, color="#64748B")),
            tickmode="linear",
            tick0=2011,
            dtick=1,
            showgrid=True,
            gridcolor="#F1F5F9"
        ),
        yaxis=dict(
            title=dict(text="Domestic Visits", font=dict(size=12, color="#0F766E")),
            showgrid=True,
            gridcolor="#F1F5F9"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    if metric == "both":
        layout_args["yaxis2"] = dict(
            title=dict(text="Foreign Visits", font=dict(size=12, color="#0284C7")),
            overlaying="y",
            side="right",
            showgrid=False
        )
        
    fig.update_layout(**layout_args)
    return fig


def create_state_comparison_chart(
    df_tourism: pd.DataFrame,
    selected_states: List[str],
    metric: str = "domestic_visits"
) -> go.Figure:
    """
    Multi-state comparative trajectory chart over 2011–2025.
    """
    metric_labels = {
        "domestic_visits": "Domestic Tourist Visits",
        "foreign_visits": "Foreign Tourist Visits",
        "total_visits": "Total Visits",
        "domestic_yoy_growth_pct": "Domestic YoY Growth (%)"
    }
    label = metric_labels.get(metric, metric)
    
    fig = go.Figure()
    palette = ["#0F766E", "#0284C7", "#D97706", "#7C3AED", "#DC2626", "#059669"]
    
    for idx, state in enumerate(selected_states):
        df_st = df_tourism[df_tourism["state"] == state].sort_values("year")
        color = palette[idx % len(palette)]
        
        fig.add_trace(go.Scatter(
            x=df_st["year"],
            y=df_st[metric],
            name=state,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            hovertemplate=f"<b>{state} (%{{x}})</b><br>{label}: %{{y:,.1f}}<extra></extra>"
        ))
        
    fig.update_layout(
        title=dict(
            text=f"Comparative Trajectory: {label}",
            font=dict(size=14, family="Plus Jakarta Sans", color="#0F172A")
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=380,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=11, color="#64748B")),
            tickmode="linear",
            tick0=2011,
            dtick=1,
            showgrid=True,
            gridcolor="#F1F5F9"
        ),
        yaxis=dict(
            title=dict(text=label, font=dict(size=11, color="#64748B")),
            showgrid=True,
            gridcolor="#F1F5F9"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_growth_waterfall_chart(
    df_national: pd.DataFrame
) -> go.Figure:
    """
    Year-on-year domestic tourism growth rates national bar chart.
    """
    df_plot = df_national.dropna(subset=["domestic_yoy_growth_pct"]).copy()
    
    colors = ["#047857" if g >= 0 else "#B91C1C" for g in df_plot["domestic_yoy_growth_pct"]]
    
    fig = go.Figure(go.Bar(
        x=df_plot["year"],
        y=df_plot["domestic_yoy_growth_pct"],
        marker_color=colors,
        text=[f"{g:+.1f}%" for g in df_plot["domestic_yoy_growth_pct"]],
        textposition="outside",
        textfont=dict(size=10, family="Plus Jakarta Sans"),
        hovertemplate="<b>Year %{x}</b><br>YoY Growth: %{y:+.2f}%<extra></extra>"
    ))
    
    fig.add_hline(y=0, line_width=1.2, line_color="#475569")
    
    fig.update_layout(
        title=dict(
            text="National Domestic Visits Year-on-Year Growth Dynamics (%)",
            font=dict(size=14, family="Plus Jakarta Sans", color="#0F172A")
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        xaxis=dict(
            tickmode="linear",
            tick0=2012,
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text="Annual Growth (%)", font=dict(size=11, color="#64748B")),
            showgrid=True,
            gridcolor="#F1F5F9"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_anomaly_scatter_chart(
    df_anomalies: pd.DataFrame,
    df_tourism: pd.DataFrame
) -> go.Figure:
    """
    Interactive scatter chart displaying flagged anomalies against YoY growth.
    """
    fig = px.scatter(
        df_anomalies,
        x="domestic_yoy_growth_pct",
        y="domestic_visits",
        color="category",
        size="total_visits",
        size_max=28,
        hover_name="state",
        hover_data={
            "year": True,
            "domestic_yoy_growth_pct": ":.2f",
            "domestic_visits": ":,",
            "severity": True,
            "category": False,
            "total_visits": False
        },
        color_discrete_map={
            "Exceptional Event: Maha Kumbh Mela": "#B45309",
            "COVID-19 Pandemic Disruption": "#DC2626",
            "Post-Pandemic Tourism Rebound": "#059669",
            "Imputed Official Estimate": "#0284C7",
            "Zero-Division Baseline Discontinuity": "#7C3AED",
            "Published Zero Observation": "#6B7280",
            "Statistical Growth Surge": "#10B981",
            "Statistical Growth Decline": "#F43F5E"
        }
    )
    
    fig.update_layout(
        title=dict(
            text="Detected Tourism Shifts: Domestic Visits vs. YoY Growth (%)",
            font=dict(size=14, family="Plus Jakarta Sans", color="#0F172A")
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        height=420,
        xaxis=dict(
            title=dict(text="Domestic YoY Growth Rate (%)", font=dict(size=11, color="#64748B")),
            showgrid=True,
            gridcolor="#F1F5F9"
        ),
        yaxis=dict(
            title=dict(text="Domestic Tourist Visits", font=dict(size=11, color="#64748B")),
            type="log",
            showgrid=True,
            gridcolor="#F1F5F9"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, family="Plus Jakarta Sans")
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig
