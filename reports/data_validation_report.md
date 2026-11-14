# SustainTour India: Data Validation and Integration Report

**Task 1 Deliverable:** Data Validation, Harmonization, and Historical Integration  
**Date:** November 13, 2026  
**Project Workspace:** `c:\Projects\SustainTour_India`  
**Generated Files:**
- `scripts/merge_tourism_data.py` (Integration & validation pipeline)
- `data/processed/tourism_timeseries_2011_2025.csv` (Merged 15-year tourism panel dataset)
- `reports/data_validation_report.md` (Comprehensive data audit and validation report)

---

## 1. Executive Summary

As part of **Task 1: Data Validation and Integration** for **SustainTour India**, a rigorous audit, validation, and integration pipeline was executed across historical datasets (2011–2024), newly extracted 2025 tourism statistics, national benchmarks, environmental indicators, and official GeoJSON state boundaries.

### Key Milestones Achieved:
1. **Full Data Inventory:** Systematically profiled 9 tabular datasets and the boundary GeoJSON, cataloging row counts, column types, physical units, reference periods, and data sources.
2. **Standardization Mapping:** Designed and implemented an explicit, documented mapping aligning newly extracted 2025 compendium labels and environmental series to canonical state identifiers.
3. **Integration Pipeline:** Developed and verified `scripts/merge_tourism_data.py`. The historical series (494 rows, 2011–2024) was merged with the 2025 state data (36 rows) to create `data/processed/tourism_timeseries_2011_2025.csv` (530 rows, 15 years, 36 states/UTs).
4. **Data Integrity Verification:** Confirmed zero duplicate observations, zero fabricated values, and verified that null values are strictly confined to expected baseline growth calculations and historical reorganization boundaries.
5. **GeoJSON Boundary Alignment:** Established 100% topological alignment between the 36 dataset entities and the 36 features in `data/geo/india_states.geojson` via explicit state name and ISO 3166-2:IN code bridges.
6. **Preservation of Official Discrepancies:** Fully preserved and documented the official government source discrepancy between 2025 state sums and national totals (+400 domestic visits, -1 foreign visit). Original CSVs were preserved without in-place alterations.
7. **Snapshot Temporal Integrity:** Audited `data/processed/state_sustainability_snapshot.csv`, validating its multi-year baseline (2023–2024) and preserving it without premature substitution of 2025 tourism values.

---

## 2. Comprehensive Data Inventory & Profiling

All 9 tabular data files and the geospatial boundary file were inspected. The table below details their schema, record counts, dimensions, units, and source authorities:

| # | File Path | Shape (Rows x Cols) | Temporal Range | Key Indicators & Units | Missing Values | Primary Source Authority |
|---|-----------|---------------------|----------------|------------------------|----------------|--------------------------|
| 1 | `data/extracted_2026_compendium/tourism_2025_statewise.csv` | 36 × 4 | 2025 | `domestic_visits`, `foreign_visits` (Absolute counts) | 0 (0.0%) | Ministry of Tourism (MoT), Compendium 2026 Table 4.1.2 |
| 2 | `data/extracted_2026_compendium/national_tourism_statistics.csv` | 17 × 5 | 1991, 2001, 2011–2025 | DTV, FTV (Counts), FTA (10,000 rounded), FEE (INR Crore) | 0 (0.0%) | MoT Compendium 2026 Tables 4.1.1, 2.1.1, 2.10.1 |
| 3 | `data/extracted_2026_compendium/statewise_extraction_audit.csv` | 36 × 9 | 2024–2025 | Audit trail of raw PDF labels, page numbers, extracted values | 0 (0.0%) | MoT Compendium 2026 (pp. 94–95 / printed pp. 82–83) |
| 4 | `data/extracted_2026_compendium/data_sources.csv` | 8 × 11 | 1991–2025 | Extraction metadata, verification status, and footnote flags | 0 (0.0%) | MoT Compendium 2026 metadata tracking |
| 5 | `data/processed/tourism_timeseries.csv` | 494 × 10 | 2011–2024 | DTV, FTV, Total Visits, Foreign Share (%), YoY Growth (%) | 39 growth, 458 caveat | RBI Handbook of Statistics Tables 13 & 182 |
| 6 | `data/processed/tourism_timeseries_2011_2025.csv` | 530 × 10 | 2011–2025 | DTV, FTV, Total Visits, Foreign Share (%), YoY Growth (%) | 39 growth, 494 caveat | Integrated Panel (RBI Handbook + MoT Compendium 2026) |
| 7 | `data/processed/forest_cover_long.csv` | 693 × 4 | 1987–2023 (19 cycles) | `forest_cover_sq_km` (Square kilometers) | 56 (8.1%) | Forest Survey of India (FSI) / India State of Forest Reports |
| 8 | `data/processed/groundwater_long.csv` | 185 × 5 | 2017, 2020, 2022–2024 | Extractable Resource (BCM), Extraction (BCM), Stage (%) | 2 (1.1%) | Central Ground Water Board (CGWB) Dynamic Assessment |
| 9 | `data/processed/sdg_scores_long.csv` | 148 × 3 | 2018–2020, 2023 | Composite `sdg_score` (Index scale 0–100) | 3 (2.0%) | NITI Aayog SDG India Index reports (1.0 to 4.0) |
| 10 | `data/processed/state_sustainability_snapshot.csv` | 36 × 17 | 2023–2024 | Composite cross-sectional table across tourism, forest, GW, SDG | 1 state (8 cols) | Integrated multi-domain baseline |
| 11 | `data/geo/india_states.geojson` | 36 features | Current | Polygons/MultiPolygons; properties: `state`, `shapeName`, `shapeISO` | 0 (0.0%) | Official ADM1 administrative boundary GeoJSON |

---

## 3. State and Union Territory Name Standardization

India's administrative geography underwent structural reorganizations between 2011 and 2025. Furthermore, differing government agencies utilize varying naming formats, conjunctions, and punctuation.

### 3.1 Standardization Mapping Dictionary
To integrate 2025 compendium data into the historical time series without data loss or duplication, the following explicit mapping is codified in `scripts/merge_tourism_data.py`:

```python
# 2025 Compendium to Canonical Project Name
STATE_NAME_MAPPING_2025 = {
    "Dadra Nagar Haveli & Daman & Diu": "Dadra & Nagar Haveli and Daman & Diu",
    "Jammu & Kashmir": "Jammu and Kashmir"
}
```

- **Dadra Nagar Haveli & Daman & Diu:** In `tourism_2025_statewise.csv`, the label lacked the initial ampersand (`&`). Mapping it to `"Dadra & Nagar Haveli and Daman & Diu"` ensures perfect continuity with the historical time series and sustainability snapshot.
- **Jammu & Kashmir:** The compendium table used `"Jammu & Kashmir"` with an ampersand, whereas the historical series used `"Jammu and Kashmir"`. Standardized to `"Jammu and Kashmir"`.
- **All other 34 States/UTs:** Identical between 2025 compendium and historical time series.

### 3.2 Historical Boundary Reorganizations & Environmental Datasets
In the environmental time series (`forest_cover_long.csv`, `groundwater_long.csv`, `sdg_scores_long.csv`), **37 entities** are present because Dadra & Nagar Haveli and Daman & Diu were separate Union Territories prior to their January 26, 2020 merger:
- `Dadra & Nagar Haveli` (pre-2020)
- `Daman & Diu` (pre-2020)
- In the merged tourism panel and snapshot, these entities are treated as a single unified UT: `Dadra & Nagar Haveli and Daman & Diu`.

### 3.3 GeoJSON Boundary Alignment
The official boundary file `data/geo/india_states.geojson` contains exactly 36 features. When comparing the merged dataset's canonical state names against GeoJSON properties:
- **34 States/UTs match identically** on the `state` property.
- **2 Union Territories differ only in ampersand (`&`) vs. word (`and`) conjunction:**

| Canonical Dataset Name | GeoJSON `state` Property | GeoJSON `shapeName` | ISO 3166-2:IN (`shapeISO`) |
|------------------------|--------------------------|---------------------|----------------------------|
| `Andaman & Nicobar Islands` | `Andaman and Nicobar Islands` | `Andaman and Nicobar Islands` | `IN-AN` |
| `Dadra & Nagar Haveli and Daman & Diu` | `Dadra and Nagar Haveli and Daman and Diu` | `Dādra and Nagar Haveli and Damān and Diu` | `IN-DH` |

**GeoJSON Bridge Mapping for Downstream Visualizations (Streamlit / Folium / Plotly):**
```python
CANONICAL_TO_GEOJSON_MAPPING = {
    "Andaman & Nicobar Islands": "Andaman and Nicobar Islands",
    "Dadra & Nagar Haveli and Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu"
}
```
Alternatively, developers can bind choropleths directly via `shapeISO`, where all 36 codes (`IN-AP`, `IN-AR`, ..., `IN-WB`) are 100% invariant across geographical conventions.

---

## 4. Tourism Time Series Integration (2011–2025)

The script `scripts/merge_tourism_data.py` was executed to merge the 2025 data into the historical time series. The resulting dataset `data/processed/tourism_timeseries_2011_2025.csv` was written and verified.

### 4.1 Formulae for Derived Indicators (2025)
1. **Total Visits:**
   $$\text{total\_visits} = \text{domestic\_visits} + \text{foreign\_visits}$$
2. **Foreign Visitor Share Percentage:**
   $$\text{foreign\_share\_pct} = \operatorname{round}\left(\frac{\text{foreign\_visits}}{\text{total\_visits}} \times 100, 4\right)$$
3. **Domestic YoY Growth Rate:**
   $$\text{domestic\_yoy\_growth\_pct}_{2025} = \operatorname{round}\left(\frac{\text{domestic\_visits}_{2025} - \text{domestic\_visits}_{2024}}{\text{domestic\_visits}_{2024}} \times 100, 4\right)$$
   *(Computed against the 2024 baseline domestic visits for each state in the panel)*
4. **Metadata & Caveats:**
   - `foreign_2024_estimate_caveat`: Preserved as `NaN` for 2025, maintaining strict column semantic targeting for the 2024 RBI estimates.
   - `source_domestic`: `"India Tourism Data Compendium 2026 Table 4.1.2"`
   - `source_foreign`: `"India Tourism Data Compendium 2026 Table 4.1.2"`

### 4.2 Record Structure & Panel Completeness
The merged dataset contains exactly **530 rows** across 15 calendar years (2011–2025):
- **34 States/UTs with 15 complete annual records (2011–2025):** 510 rows.
- **Telangana:** 13 annual records (2013–2025; state bifurcated from Andhra Pradesh in 2014; RBI time series begins in 2013).
- **Ladakh:** 7 annual records (2019–2025; Union Territory created on October 31, 2019).
- **Total records:** $510 + 13 + 7 = 530\text{ observations}$.

---

## 5. Data Quality, Completeness & Sanity Checks

### 5.1 Duplicate Observations
- **Tourism Time Series (Historical):** 0 duplicates on `(state, year)`.
- **2025 Extracted Compendium:** 0 duplicates on `(state, year)`.
- **Merged Time Series (2011–2025):** 0 duplicates on `(state, year)`.
- **Environmental Datasets:** 0 duplicates on `(state, year)` across forest cover, groundwater, and SDG scores.

### 5.2 Missing Value Audit & Zero-Fabrication Rule
Under the strict requirement that **no missing values may be fabricated or arbitrarily imputed**, all missing values were traced to their structural or mathematical origins:

1. **Merged Tourism Time Series (`domestic_yoy_growth_pct`):** Exactly 39 missing values:
   - 34 states for baseline year 2011 (no $t-1$ data available in time series).
   - Telangana for baseline year 2013.
   - Ladakh for baseline year 2019.
   - Lakshadweep in 2013, 2014, and 2021: In 2012, 2013, and 2020, domestic visits for Lakshadweep were recorded as 0 in official tables; division by zero produces mathematically undefined (`NaN`) growth rates.
2. **Forest Cover (`forest_cover_sq_km`):** 56 missing values out of 693 records:
   - Chhattisgarh, Jharkhand, and Uttarakhand have `NaN` from 1987 to 1995 (formed in Nov 2000).
   - Telangana has `NaN` from 1987 to 2011 (formed in 2014).
   - Ladakh has `NaN` from 2007 to 2019 (formed in 2019).
   - Daman & Diu, Lakshadweep, and Puducherry have missing assessments during early ISFR cycles.
3. **Groundwater Extraction (`groundwater_extraction_pct`):** 2 missing values out of 185 records:
   - Ladakh (2017): Pre-UT formation.
   - Daman & Diu (2024): Reported post-merger under combined UT.
4. **SDG India Index (`sdg_score`):** 3 missing values out of 148 records:
   - Ladakh (2018, 2019): Pre-UT formation.
   - Daman & Diu (2023): Assessed jointly with Dadra & Nagar Haveli.

### 5.3 Numeric Value Sanity Checks
- All visit metrics (`domestic_visits`, `foreign_visits`, `total_visits`) are strictly $\ge 0$.
- `foreign_share_pct` is strictly bounded between $0.0\%$ and $100.0\%$.
- `extractable_groundwater_bcm` ranges from $0.004$ to $66.88$ BCM.
- `groundwater_extraction_pct` ranges from $0.06\%$ to $170.7\%$. Values exceeding $100\%$ (e.g., Punjab at $156.9\%–170.7\%$, Rajasthan, Haryana) correctly capture critically over-exploited aquifers where extraction exceeds annual natural recharge.
- `sdg_score` ranges from $42.0$ (Bihar 2018) to $79.0$ (Kerala and Uttarakhand 2023), adhering to NITI Aayog's 0–100 index methodology.

---

## 6. Official Discrepancy & Footnote Analysis

### 6.1 Preserving the 2025 Compendium Source Discrepancy
In the Ministry of Tourism's *India Tourism Data Compendium 2026*, an inherent arithmetic discrepancy exists between the state-level figures in Table 4.1.2 and the published national aggregates in Table 4.1.1:

| Indicator | Sum of 36 State Records (Table 4.1.2) | Published National Total (Table 4.1.1) | Official Discrepancy (State Sum – National) |
|-----------|---------------------------------------|----------------------------------------|---------------------------------------------|
| **Domestic Tourist Visits (DTV)** | **4,285,530,610** | **4,285,530,210** | **+400 visits** |
| **Foreign Tourist Visits (FTV)** | **25,326,621** | **25,326,622** | **-1 visit** |

**Action Taken:**
In compliance with project guidelines, **no state figures were altered or forced to reconcile with national totals**. The state-wise figures reflect the true, unadulterated primary text of Table 4.1.2. The discrepancy (+400 DTV, -1 FTV) is preserved and logged as an official government compendium artifact.

### 6.2 Key Data Quality Flags in 2025 Data
Downstream models and visualizations must account for the following official footnotes (PDF pp. 94–95, Table 4.1.2):
1. **Delhi and Maharashtra Estimates (Footnote 2):** Due to delayed primary reporting, 2025 domestic and foreign visit figures for Delhi and Maharashtra were estimated by the Ministry of Tourism by applying the all-India 2025/2024 growth rate to their 2024 totals.
   - *Delhi 2025:* 67,308,561 DTV | 2,431,882 FTV
   - *Maharashtra 2025:* 275,554,929 DTV | 4,506,598 FTV
2. **Uttar Pradesh Maha Kumbh Mela Discontinuity (Footnote 5):** Uttar Pradesh's domestic visits surged to **1,557,423,503** in 2025 (up from 646.8 million in 2024). This reflects the once-in-12-years Maha Kumbh Mela congregation at Prayagraj. This surge is an extreme outlier and should be flagged in trend analysis.
3. **National Foreign Tourist Arrivals (FTA) Precision Limitation:** National FTAs in Table 2.1.1 are published rounded to the nearest 0.1 lakh (e.g., 109.3 lakh in 2025 $\rightarrow$ 10,930,000). They should not be interpreted as unit-level arrival counts.
4. **2024 Revisions (R):** State figures for 2024 were revised in the 2026 Compendium compared to provisional 2024 estimates previously released in the RBI Handbook.

---

## 7. Sustainability Snapshot Reference Years & Baseline Integrity

An audit of `data/processed/state_sustainability_snapshot.csv` confirms that it serves as a synchronized **cross-domain baseline snapshot**:

| Column Name | Indicator | Reference Year | Notes & Source |
|-------------|-----------|----------------|----------------|
| `tourism_year` | Tourism Baseline | **2024** | Historical baseline visits and foreign share |
| `domestic_growth_2023_2024_pct` | Tourism Dynamics | **2023–2024** | Annual domestic growth preceding 2025 compendium |
| `forest_assessment_year` | Forest Cover | **2023** | FSI India State of Forest Report (ISFR 2023) |
| `groundwater_assessment_year` | Groundwater Status | **2024** | CGWB Dynamic Groundwater Resource Assessment 2024 |
| `sdg_assessment_year` | Sustainable Development | **2023** | NITI Aayog SDG India Index 2023–24 (Edition 4.0) |

### Non-Substitution Decision
Per project instructions, **2025 tourism values were NOT substituted into `state_sustainability_snapshot.csv`**. 
- *Rationale:* Substituting 2025 tourism data into a table where environmental indicators reflect 2023/2024 would introduce temporal dissonance and distort composite sustainability indices (e.g., tourism pressure per forest area or aquifer stress).
- *Missing Entity Note:* In `state_sustainability_snapshot.csv`, row 7 (`Dadra & Nagar Haveli and Daman & Diu`) contains null values for environmental metrics because the underlying source reports had separate data for Dadra & Nagar Haveli and Daman & Diu. This is documented under `data_caveat`.

---

## 8. Dataset Readiness Assessment

The validation and harmonization steps confirm that the datasets are ready for downstream tasks:

| Component | Status | Readiness Notes & Guidance for Task 2 |
|-----------|--------|---------------------------------------|
| **Merged Tourism Time Series** | **READY** | Full 15-year panel (530 rows) ready for temporal trends, state comparisons, and growth analysis. |
| **National Benchmark Series** | **READY** | 17 benchmark years (1991–2025) available for national vs. state share metrics. |
| **GeoJSON Spatial Layer** | **READY** | 36 features ready for Choropleth maps. Use `CANONICAL_TO_GEOJSON_MAPPING` or `shapeISO`. |
| **Environmental Time Series** | **READY** | Long-format tables for forest cover, groundwater, and SDG scores ready for multi-indicator dashboards. |
| **Sustainability Snapshot** | **READY** | Synchronized 2023–2024 multi-domain baseline ready for cross-sectional state rankings and cluster analysis. |

---

## 9. Deliverables Summary

1. **`scripts/merge_tourism_data.py`**: Automated script that loads, standardizes, calculates, validates, and exports the merged time series. Exits cleanly with code 0.
2. **`data/processed/tourism_timeseries_2011_2025.csv`**: Clean 530-record CSV containing all 36 States/UTs from 2011 to 2025 with complete audit citations.
3. **`reports/data_validation_report.md`**: This report, detailing methodology, mappings, mathematical checks, and findings.
