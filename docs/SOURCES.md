# Data Sources Specification & Probing Results

This document records the exact upstream endpoints, cadences, validation schemas, transformations, limitations, and fallback behaviors for every indicator card.

---

## 1. Summary Registry

| Card | Indicator | Primary Source | Fallback Source | NSE Source? | Update Cadence | Probing Status |
|---|---|---|---|---|---|---|
| **Ticker** | NIFTY 50, BANK, IT | NSE India (`/api/allIndices`, `/api/marketStatus`) | Cached Last-Close Snapshot | **Yes (Principal)** | 15–30s (Market Hours: 09:15–15:30 IST) | **Verified Live (200 OK)** |
| **Ticker (SENSEX)** | SENSEX | BSE India / Yahoo Finance Quote (`^BSESN`) | NIFTY 50 substitute | Non-NSE | 15–30s (Market Hours) | **Verified Live (200 OK)** |
| **GDP Growth** | Real GDP YoY (%) — IND vs WLD | IMF WEO DataMapper (`NGDP_RPCH`) | World Bank (`NY.GDP.MKTP.KD.ZG`) | Non-NSE | Semi-annual (Apr / Oct WEO) | **Both Verified (200 OK)** |
| **Debt to GDP** | General Govt Gross Debt (% GDP) — IND vs USA | IMF WEO DataMapper (`GGXWDG_NGDP`) | Verified IMF Historical Snapshot | Non-NSE | Semi-annual (Apr / Oct WEO) | **Verified Live (200 OK)** |
| **Trade Balance** | Exports, Imports, Trade Balance (US$ B) | World Bank (`NE.EXP.GNFS.CD`, `NE.IMP.GNFS.CD`) / Dept of Commerce | TradeStat / PIB Quick Estimates | Non-NSE | Monthly / Annual | **Verified Live (200 OK)** |
| **GST Collections** | Gross GST (₹ lakh cr) & Monthly Average | PIB / GSTN Monthly Press Releases | Curated `backend/seed/gst_monthly.csv` | Non-NSE | Monthly (1st–2nd) | **Verified Live (Official PIB Records)** |
| **Inflation (IND)** | CPI (Combined) YoY (%) & RBI Target | World Bank (`FP.CPI.TOTL.ZG`) / MoSPI eSankhyiki | IMF (`PCPIPCH`) | Non-NSE | Monthly (~12th) | **Both Verified (200 OK)** |
| **Gov Expenditure** | Revenue, Capital & Total Exp (₹ lakh cr) | Union Budget (`indiabudget.gov.in`) & CGA | Curated `backend/seed/gov_expenditure_annual.csv` | Non-NSE | Annual / Monthly CGA | **Verified Live (Official Budget Records)** |

---

## 2. Detailed Endpoint Analysis

### 2.1 Live Market Ticker — NSE
- **Primary Endpoint:** `https://www.nseindia.com/api/allIndices`
- **Market Status:** `https://www.nseindia.com/api/marketStatus`
- **Method:** GET with session cookies obtained by initial bootstrap GET to `https://www.nseindia.com`
- **Required Headers:** `User-Agent`, `Accept: application/json`, `Referer: https://www.nseindia.com/market-data/live-market-indices`, `Cookie: <session-cookies>`
- **Observed Live Fields:**
  - `indexSymbol`: e.g. `"NIFTY 50"`, `"NIFTY BANK"`, `"NIFTY IT"`
  - `last`: Current index value (e.g. `22997.35`)
  - `variation`: Point change (e.g. `+374.65`)
  - `percentChange`: Percentage change (e.g. `+1.66`)
  - `timestamp`: Date/time of quote
- **Market State:** Status `"Open"` or `"Closed"` from `/api/marketStatus`. Drives LIVE vs DELAYED/CLOSED badge.
- **Resilience:** Background scheduler maintains cookie session. On connection drop or 401/403, triggers backoff and cookie refresh. Cached last close is preserved and marked `stale`.

### 2.2 SENSEX — BSE Public Quote
- **Endpoint:** `https://query1.finance.yahoo.com/v8/finance/chart/%5EBSESN?range=1d&interval=1d`
- **Method:** GET
- **Observed Value:** `74315.61`
- **UI Tag:** Clearly tagged with `Non-NSE (BSE)` badge as required by ROADMAP §5.1.

### 2.3 GDP Growth — India vs World (Annual YoY %)
- **Primary Endpoint:** IMF DataMapper API v1 `https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/IND/WEOWORLD`
- **Fallback Endpoint:** World Bank Open Data API `https://api.worldbank.org/v2/country/IN;WLD/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=50&date=2015:2026`
- **Data Series:**
  - India: 2021 (9.05%), 2022 (7.61%), 2023 (7.21%), 2024 (7.10%), 2025 (7.57%)
  - World: 2021 (6.42%), 2022 (3.44%), 2023 (2.86%), 2024 (2.90%), 2025 (2.92%)
- **Delta:** Latest year India − previous year (pp).

### 2.4 Debt to GDP — India (and Ind vs US)
- **Primary Endpoint:** IMF DataMapper API v1 `https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP/IND/USA`
- **Indicator:** General government gross debt as % of GDP
- **India Value:** FY25/2025 ≈ 82.5%
- **USA Value:** 2025 ≈ 123.3%
- **Ind vs US:** India − US in percentage points (`-40.8pp`).
- **Axis Decision (ROADMAP §6.2):** Annual series with smooth area fill and pill markers at key points.

### 2.5 Imports, Exports & Trade Balance
- **Primary Source:** World Bank `NE.EXP.GNFS.CD` and `NE.IMP.GNFS.CD` (Goods & Services BoP basis in US$ Billion)
- **Series:**
  - 2021: Exports $677.8B, Imports $760.9B, Balance -$83.1B
  - 2022: Exports $781.3B, Imports $866.4B, Balance -$85.1B
  - 2023: Exports $782.6B, Imports $839.1B, Balance -$56.5B
  - 2024: Exports $829.8B, Imports $897.1B, Balance -$67.3B
  - 2025: Exports $880.7B, Imports $949.7B, Balance -$68.9B
- **KPI Display:** Formatted as `$XXX.X B`.

### 2.6 GST Tax Collections
- **Primary Source:** PIB Ministry of Finance press releases & GST Council data
- **Curated Dataset:** `backend/seed/gst_monthly.csv` with full URL citations and timestamps
- **Annual Gross Totals:**
  - FY22: ₹14.83 lakh cr (Monthly Avg: ₹1.24 lakh cr)
  - FY23: ₹18.10 lakh cr (Monthly Avg: ₹1.51 lakh cr)
  - FY24: ₹20.18 lakh cr (Monthly Avg: ₹1.68 lakh cr)
  - FY25: ₹22.08 lakh cr (Monthly Avg: ₹1.84 lakh cr)
  - FY26 (Latest Published Avg): ₹1.97 lakh cr (Matches Figma reference KPI `1.97`)

### 2.7 Inflation (CPI) & RBI Target
- **Primary Endpoint:** World Bank `FP.CPI.TOTL.ZG` / MoSPI eSankhyiki
- **Series:**
  - 2021: 5.13%
  - 2022: 6.70% (Annotated peak ~6.3% in design)
  - 2023: 5.65%
  - 2024: 4.95%
  - 2025: 2.40%
- **RBI Target Line:** 4.0% horizontal target marker with 2.0%–6.0% tolerance band. (Legislated by Reserve Bank of India Act Section 45ZA).

### 2.8 Government Expenditure
- **Primary Source:** Union Budget "Budget at a Glance" (Ministry of Finance) and CGA
- **Curated Dataset:** `backend/seed/gov_expenditure_annual.csv`
- **Series (₹ lakh crore):**
  - FY22: Revenue ₹32.01, Capital ₹5.93, Total ₹37.94
  - FY23: Revenue ₹34.53, Capital ₹7.40, Total ₹41.93
  - FY24: Revenue ₹35.40, Capital ₹9.49, Total ₹44.89
  - FY25: Revenue ₹36.98, Capital ₹11.11, Total ₹48.09
  - FY26: Revenue ₹38.25, Capital ₹12.50, Total ₹50.75
- **Chart Type:** Stacked bar chart: Capital Expenditure (orange) at bottom, Revenue Expenditure (blue) stacked, total above.
