# India Tourism Data Compendium 2026 — extraction report

- **Publication:** India Tourism Statistics 2026 / India Tourism Data Compendium 2026, Ministry of Tourism, Government of India, 67th edition (2026).
- **PDF:** `india_tourism_compendium_2026.pdf`; **216 pages**. Printed page = PDF page minus 12 in relevant sections.
- **2025 state-wise data found:** YES. Table 4.1.2, PDF pp. 94–95, printed pp. 82–83.
- **State/UT records:** 36 (36 unique); 2025; 0 missing DTV/FTV; 0 duplicate state-year rows.
- **National series:** Table 4.1.1, PDF p. 93 / printed p. 81 (DTV/FTV); Table 2.1.1, PDF p. 27 / printed p. 15 (FTA); Table 2.10.1, PDF p. 55 / printed p. 43 (INR crore FEE).
- **National years:** 1991, 2001, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025.
- **Published 2025 DTV total:** 4,285,530,210; **sum of extracted state DTV:** 4,285,530,610; difference: 400.
- **Published 2025 FTV total:** 25,326,622; **sum of extracted state FTV:** 25,326,621; difference: -1.
- **Data-quality flags:** 2025 Delhi and Maharashtra DTV/FTV values estimated by applying all-India 2025/24 growth rate to 2024 figures (footnote 2, PDF p. 95); Uttar Pradesh includes Kumbh Mela visits (footnote 5, PDF p. 95). 2024 figures revised (R). Do not label all 2025 state figures as independently observed or final.
- **Precision:** Table 2.1.1 national FTAs are published to 0.1 lakh; conversion to absolute arrivals produces rounded counts, not exact arrival totals. For precise FTAs, another table with exact figures would be preferable.
- **Unit conversion:** state visits already reported in absolute numbers, no scaling; national FTAs multiplied by 100,000 per lakh; FEE already INR crore.
- **Extraction method:** PyMuPDF text parsing; relevant pages are text-selectable; no OCR required.
- **Files:** `tourism_2025_statewise.csv` (separate dataset; merge only with the 400/-1 reconciliation caveat), `national_tourism_statistics.csv`, `data_sources.csv`, `statewise_extraction_audit.csv` (extra provenance).
- **Optional indicators:** State-level hotel capacity and infrastructure not extracted; no verified comparable state-level tables identified within targeted scope. `additional_tourism_indicators.csv` intentionally not created.
- **Manual review:** Check estimated Delhi and Maharashtra values and the Kumbh Mela discontinuity before modeling; verify national FTA precision requirements. State-level sums differ from the official total by 400 domestic visits and -1 foreign visit. Do not silently adjust any state values; manual verification of printed totals and state rows is recommended.

## Validation issues
- DTV state sum differs from published total by 400
- FTV state sum differs from published total by -1
