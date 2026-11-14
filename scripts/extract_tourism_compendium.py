#!/usr/bin/env python3
"""Reproducible extraction of selected tables from India Tourism Data Compendium 2026.
Dependency: pip install pymupdf pandas
Usage: python scripts/extract_tourism_compendium.py [PDF_PATH] [OUTPUT_DIR]
PDF page numbers are 1-based, not printed page numbers.
"""
import sys,re,csv
from pathlib import Path
import fitz
import pandas as pd
PDF=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/india_tourism_compendium_2026.pdf')
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/mnt/data/data/extracted_2026_compendium')
if not PDF.is_file(): sys.exit(f'ERROR: PDF not found: {PDF}')
OUT.mkdir(parents=True,exist_ok=True)
doc=fitz.open(PDF)
if len(doc)<95: sys.exit('ERROR: PDF unexpectedly short; verify edition and pagination')
def lines(n):return [s.strip() for s in doc[n-1].get_text().splitlines() if s.strip()]
def num(s):
 s=s.strip().replace(',','').replace(' ','')
 return int(s) if re.fullmatch(r'\d+',s) else None
states=['Andaman & Nicobar Islands','Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chandigarh','Chhattisgarh','Dadra Nagar Haveli & Daman & Diu','Delhi','Goa','Gujarat','Haryana','Himachal Pradesh','Jammu & Kashmir','Jharkhand','Karnataka','Kerala','Lakshadweep','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Puducherry','Punjab','Rajasthan','Sikkim','Tamil Nadu','Tripura','Telangana','Uttar Pradesh','Uttarakhand','West Bengal','Ladakh']
# The printed table uses "Telengana"; normalize to Telangana, retain original in audit.
alias={'Andaman & Nicobar Islands':'Andaman & Nicobar Islands','Andhra Pradesh ®':'Andhra Pradesh','Delhi2':'Delhi','Maharashtra2':'Maharashtra','Uttar Pradesh5':'Uttar Pradesh','Telengana':'Telangana'}
# Text on PDF pages 94-95 is linearized in reading order: state label, 2024 DTV, 2024 FTV, 2025 DTV, 2025 FTV, growth, shares.
raw=lines(94)+lines(95)
starts={'Andaman & Nicobar':'Andaman & Nicobar Islands','Andhra Pradesh ®':'Andhra Pradesh','Arunachal Pradesh':'Arunachal Pradesh','Assam':'Assam','Bihar':'Bihar','Chandigarh':'Chandigarh','Chhattisgarh':'Chhattisgarh','Dadra Nagar Haveli &':'Dadra Nagar Haveli & Daman & Diu','Delhi2':'Delhi','Goa':'Goa','Gujarat':'Gujarat','Haryana':'Haryana','Himachal Pradesh':'Himachal Pradesh','Jammu & Kashmir':'Jammu & Kashmir','Jharkhand':'Jharkhand','Karnataka':'Karnataka','Kerala':'Kerala','Lakshadweep':'Lakshadweep','Madhya Pradesh':'Madhya Pradesh','Maharashtra2':'Maharashtra','Manipur':'Manipur','Meghalaya':'Meghalaya','Mizoram':'Mizoram','Nagaland':'Nagaland','Odisha':'Odisha','Puducherry':'Puducherry','Punjab':'Punjab','Rajasthan':'Rajasthan','Sikkim':'Sikkim','Tamil Nadu':'Tamil Nadu','Tripura':'Tripura','Telengana':'Telangana','Uttar Pradesh5':'Uttar Pradesh','Uttarakhand':'Uttarakhand','West Bengal':'West Bengal','Ladakh':'Ladakh'}
rows=[]; audits=[]
for i,s in enumerate(raw):
 if s not in starts:continue
 name=starts[s]
 # Search the following 5 lines for 4 comma-separated integer values; skip line-wrapped state labels.
 vals=[]
 for v in raw[i+1:i+9]:
  if num(v) is not None:vals.append(num(v))
  if len(vals)==4:break
 if len(vals)!=4:raise ValueError(f'Failed to extract four integer visit values for {name} at line {i}: {raw[i:i+10]}')
 pg=94 if i<len(lines(94)) else 95
 rows.append({'state':name,'year':2025,'domestic_visits':vals[2],'foreign_visits':vals[3]})
 audits.append({'state':name,'original_state_label':s,'pdf_page':pg,'printed_page':pg-12,'domestic_visits_2024':vals[0],'foreign_visits_2024':vals[1],'domestic_visits_2025':vals[2],'foreign_visits_2025':vals[3],'extraction_method':'PyMuPDF text layout / numeric tokens'})
state=pd.DataFrame(rows)
if len(state)!=36 or state.state.nunique()!=36:raise ValueError(f'Expected 36 distinct States/UTs; found {len(state)} rows / {state.state.nunique()} unique')
state.to_csv(OUT/'tourism_2025_statewise.csv',index=False,encoding='utf-8')
pd.DataFrame(audits).to_csv(OUT/'statewise_extraction_audit.csv',index=False,encoding='utf-8')
# National DTV and FTV (not FTA) from Table 4.1.1, PDF p93.
lt=lines(93); visits={}
for i,s in enumerate(lt):
 m=re.fullmatch(r'(1991|2001|20\d{2})(?:\s*\(R\)|\s*\d)?',s)
 if m and i+2<len(lt) and num(lt[i+1]) is not None and num(lt[i+2]) is not None:
  yr=int(m.group(1));visits[yr]={'domestic_tourist_visits':num(lt[i+1]),'foreign_tourist_visits':num(lt[i+2])}
# FTA in lakh (one decimal precision) from Table 2.1.1, PDF p27. Preserve precision limitation in metadata.
fta={};l=lines(27)
for i,s in enumerate(l):
 if re.fullmatch(r'(1991|2001|20\d{2})',s) and i+1<len(l) and re.fullmatch(r'\d+(?:\.\d+)?',l[i+1]):
  yr=int(s)
  if yr in visits:fta[yr]=int(round(float(l[i+1])*100000))
# FEE in INR crore from Table 2.10.1, PDF p55.
fee={};l=lines(55)
for i,s in enumerate(l):
 if re.fullmatch(r'(1991|2001|20\d{2})',s) and i+1<len(l) and num(l[i+1]) is not None:
  yr=int(s)
  if yr in visits:fee[yr]=num(l[i+1])
national=pd.DataFrame([{'year':y,'domestic_tourist_visits':v['domestic_tourist_visits'],'foreign_tourist_arrivals':fta.get(y),'foreign_tourist_visits':v['foreign_tourist_visits'],'foreign_exchange_earnings_inr_crore':fee.get(y)} for y,v in sorted(visits.items())])
national.to_csv(OUT/'national_tourism_statistics.csv',index=False,encoding='utf-8')
# Traceability for every column, including state-specific source page.
sources=[]
def src(dataset,indicator,yr,pdfpg,table,original,output,notes='',status='extracted_checked_totals_discrepancy'):
 sources.append({'dataset':dataset,'indicator':indicator,'reference_year':yr,'pdf_page':pdfpg,'printed_page':pdfpg-12,'source_table':table,'original_unit':original,'output_unit':output,'extraction_method':'PyMuPDF text extraction + deterministic token parser','verification_status':status,'notes':notes})
for pg in [94,95]:
 for ind in ['domestic_visits','foreign_visits']:
  src('tourism_2025_statewise.csv',ind,2025,pg,'4.1.2','visits (numbers)','visits (numbers)','2025 Delhi and Maharashtra figures estimated by applying all-India growth rate; UP includes Kumbh Mela; consult statewise_extraction_audit.csv for state page.')
for ind in ['domestic_tourist_visits','foreign_tourist_visits']:
 src('national_tourism_statistics.csv',ind,'1991, 2001, 2011–2025',93,'4.1.1','visits (numbers)','visits (numbers)','2024 revised; 2025 includes Kumbh Mela.')
src('national_tourism_statistics.csv','foreign_tourist_arrivals','1991, 2001, 2011–2025',27,'2.1.1','lakh arrivals (rounded to 0.1 lakh)','arrivals (rounded to nearest 10,000)','Original one-decimal lakh values have limited precision; do not treat as exact counts.',status='verified_source_precision_limited')
src('national_tourism_statistics.csv','foreign_exchange_earnings_inr_crore','1991, 2001, 2011–2025',55,'2.10.1','INR crore','INR crore','RBI balance of payments tourism receipts.')
pd.DataFrame(sources).to_csv(OUT/'data_sources.csv',index=False,encoding='utf-8')
# Published totals from Table 4.1.2 and Table 4.1.1.
expected_dtv=4285530210;expected_ftv=25326622
sd=int(state.domestic_visits.sum());sf=int(state.foreign_visits.sum())
assert int(national.loc[national.year==2025,'domestic_tourist_visits'].iloc[0])==expected_dtv
assert int(national.loc[national.year==2025,'foreign_tourist_visits'].iloc[0])==expected_ftv
issues=[]
if sd!=expected_dtv:issues.append(f'DTV state sum differs from published total by {sd-expected_dtv:,}')
if sf!=expected_ftv:issues.append(f'FTV state sum differs from published total by {sf-expected_ftv:,}')
assert not state.duplicated(['state','year']).any()
assert not state[['domestic_visits','foreign_visits']].isna().any().any()
assert (state[['domestic_visits','foreign_visits']]>=0).all().all()
report=f'''# India Tourism Data Compendium 2026 — extraction report

- **Publication:** India Tourism Statistics 2026 / India Tourism Data Compendium 2026, Ministry of Tourism, Government of India, 67th edition (2026).
- **PDF:** `{PDF.name}`; **{len(doc)} pages**. Printed page = PDF page minus 12 in relevant sections.
- **2025 state-wise data found:** YES. Table 4.1.2, PDF pp. 94–95, printed pp. 82–83.
- **State/UT records:** {len(state)} (36 unique); 2025; 0 missing DTV/FTV; 0 duplicate state-year rows.
- **National series:** Table 4.1.1, PDF p. 93 / printed p. 81 (DTV/FTV); Table 2.1.1, PDF p. 27 / printed p. 15 (FTA); Table 2.10.1, PDF p. 55 / printed p. 43 (INR crore FEE).
- **National years:** {', '.join(map(str,national.year.tolist()))}.
- **Published 2025 DTV total:** {expected_dtv:,}; **sum of extracted state DTV:** {sd:,}; difference: {sd-expected_dtv:,}.
- **Published 2025 FTV total:** {expected_ftv:,}; **sum of extracted state FTV:** {sf:,}; difference: {sf-expected_ftv:,}.
- **Data-quality flags:** 2025 Delhi and Maharashtra DTV/FTV values estimated by applying all-India 2025/24 growth rate to 2024 figures (footnote 2, PDF p. 95); Uttar Pradesh includes Kumbh Mela visits (footnote 5, PDF p. 95). 2024 figures revised (R). Do not label all 2025 state figures as independently observed or final.
- **Precision:** Table 2.1.1 national FTAs are published to 0.1 lakh; conversion to absolute arrivals produces rounded counts, not exact arrival totals. For precise FTAs, another table with exact figures would be preferable.
- **Unit conversion:** state visits already reported in absolute numbers, no scaling; national FTAs multiplied by 100,000 per lakh; FEE already INR crore.
- **Extraction method:** PyMuPDF text parsing; relevant pages are text-selectable; no OCR required.
- **Files:** `tourism_2025_statewise.csv` (separate dataset; merge only with the 400/-1 reconciliation caveat), `national_tourism_statistics.csv`, `data_sources.csv`, `statewise_extraction_audit.csv` (extra provenance).
- **Optional indicators:** State-level hotel capacity and infrastructure not extracted; no verified comparable state-level tables identified within targeted scope. `additional_tourism_indicators.csv` intentionally not created.
- **Manual review:** Check estimated Delhi and Maharashtra values and the Kumbh Mela discontinuity before modeling; verify national FTA precision requirements. State-level sums differ from the official total by 400 domestic visits and -1 foreign visit. Do not silently adjust any state values; manual verification of printed totals and state rows is recommended.

## Validation issues
{chr(10).join('- '+x for x in issues) if issues else '- No numeric sum discrepancies.'}
'''
(OUT/'extraction_report.md').write_text(report,encoding='utf-8')
print('PDF pages:',len(doc),'states:',len(state),'national years:',len(national))
print('2025 totals DTV:',sd,'expected:',expected_dtv,'difference:',sd-expected_dtv)
print('2025 totals FTV:',sf,'expected:',expected_ftv,'difference:',sf-expected_ftv)
print('Issues:',issues)
print(state.head().to_string(index=False))
