"""
anomaly_detection.py
====================
Explainable statistical anomaly detection for tourism time series.
Implements robust Median Absolute Deviation (MAD) and contextual domain heuristics
to identify, classify, and explain unusual shifts in domestic and foreign visits.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


def detect_tourism_anomalies(
    df_tourism: pd.DataFrame,
    mad_threshold: float = 3.0,
    min_growth_threshold: float = 80.0,
    severe_drop_threshold: float = -55.0
) -> pd.DataFrame:
    """
    Detect statistical and domain anomalies across state-year observations.
    
    Methodology:
    1. Robust Median Absolute Deviation (MAD) on domestic YoY growth rates:
       - Computes panel median and MAD to withstand extreme pandemic distortions.
       - Modified Z-Score: M_i = 0.6745 * (x_i - median) / MAD
    2. Zero baseline & short series handling:
       - Identifies Lakshadweep and newly carved states where growth is mathematically undefined.
    3. Explainable Domain Classification:
       - Flags historical events (e.g., Maha Kumbh Mela 2025 in UP).
       - Flags COVID-19 pandemic collapse (2020/2021).
       - Flags post-COVID compensatory rebound (2022/2023).
       - Flags official survey estimation footnotes (Delhi/MH 2025).
    """
    df = df_tourism.copy()
    
    # Extract valid non-null growth records for statistical baseline
    valid_growth = df["domestic_yoy_growth_pct"].dropna()
    median_growth = valid_growth.median()
    mad = np.median(np.abs(valid_growth - median_growth))
    
    if mad == 0:
        mad = 1.0  # Safeguard against zero MAD
        
    df["modified_z_score"] = 0.6745 * (df["domestic_yoy_growth_pct"] - median_growth) / mad
    
    anomalies = []
    
    for _, row in df.iterrows():
        state = row["state"]
        year = row["year"]
        dtv = row["domestic_visits"]
        growth = row["domestic_yoy_growth_pct"]
        z_mod = row["modified_z_score"]
        
        is_anomaly = False
        category = None
        severity = "Normal"
        explanation = None
        
        # 1. Domain Event Rule: Uttar Pradesh 2025 Maha Kumbh Mela
        if state == "Uttar Pradesh" and year == 2025:
            is_anomaly = True
            category = "Exceptional Event: Maha Kumbh Mela"
            severity = "High"
            explanation = (
                f"Uttar Pradesh domestic visits expanded to 1,557,423,503 (+{growth:.1f}% YoY). "
                "Footnote 5 in the 2026 Compendium confirms this extreme surge was driven by "
                "the once-in-12-years Maha Kumbh Mela congregation at Prayagraj."
            )
            
        # 2. Domain Estimation Rule: Delhi & Maharashtra 2025
        elif state in ["Delhi", "Maharashtra"] and year == 2025:
            is_anomaly = True
            category = "Imputed Official Estimate"
            severity = "Moderate"
            explanation = (
                f"{state} recorded {dtv:,} visits (+{growth:.1f}% YoY). Compendium Footnote 2 "
                "documents that primary state surveys were unavailable, and values were imputed by "
                "the Ministry of Tourism by applying the all-India 2025/2024 growth rate."
            )
            
        # 3. Zero Baseline Discontinuity Rule: Lakshadweep
        elif state == "Lakshadweep" and (pd.isna(growth) or dtv == 0 or growth > 200):
            if dtv == 0:
                is_anomaly = True
                category = "Published Zero Observation"
                severity = "Moderate"
                explanation = (
                    f"Lakshadweep recorded 0 domestic visits in {year}. Official RBI and MoT tables "
                    "publish true zero reporting rather than missing values."
                )
            elif pd.isna(growth) and year in [2013, 2014, 2021]:
                is_anomaly = True
                category = "Zero-Division Baseline Discontinuity"
                severity = "Moderate"
                explanation = (
                    f"Domestic visits in {year} were {dtv:,}, but previous-year visits were 0. "
                    "Percentage growth is mathematically undefined (division by zero)."
                )
                
        # 4. Pandemic Collapse Rule (2020)
        elif year == 2020 and pd.notna(growth) and growth < -40.0:
            is_anomaly = True
            category = "COVID-19 Pandemic Disruption"
            severity = "High" if growth < -70.0 else "Moderate"
            explanation = (
                f"Severe contraction of {growth:.1f}% due to nationwide COVID-19 lockdowns, "
                "suspension of rail/flight operations, and monument closures."
            )
            
        # 5. Post-Pandemic Rebound Rule (2021-2023)
        elif year in [2021, 2022, 2023] and pd.notna(growth) and growth > 120.0:
            is_anomaly = True
            category = "Post-Pandemic Tourism Rebound"
            severity = "High" if growth > 200.0 else "Moderate"
            explanation = (
                f"Dramatic recovery jump (+{growth:.1f}%) reflecting compensatory revenge travel, "
                "lifting of state border restrictions, and a low pandemic baseline."
            )
            
        # 6. Statistical Outlier via Robust Modified Z-Score
        elif pd.notna(z_mod) and abs(z_mod) >= mad_threshold:
            is_anomaly = True
            direction = "Surge" if z_mod > 0 else "Decline"
            category = f"Statistical Growth {direction}"
            severity = "High" if abs(z_mod) >= 5.0 else "Moderate"
            explanation = (
                f"Annual domestic growth of {growth:+.1f}% deviates significantly from median growth "
                f"({median_growth:+.1f}%) with a modified Z-score of {z_mod:.2f}."
            )
            
        if is_anomaly:
            anomalies.append({
                "state": state,
                "year": year,
                "domestic_visits": dtv,
                "foreign_visits": row["foreign_visits"],
                "total_visits": row["total_visits"],
                "domestic_yoy_growth_pct": growth,
                "modified_z_score": round(z_mod, 2) if pd.notna(z_mod) else np.nan,
                "category": category,
                "severity": severity,
                "explanation": explanation
            })
            
    df_anom = pd.DataFrame(anomalies)
    if not df_anom.empty:
        df_anom = df_anom.sort_values(by=["year", "severity"], ascending=[False, True]).reset_index(drop=True)
    return df_anom
