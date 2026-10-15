# Data Sources & Probing Matrix

This document registers all primary and fallback upstream sources used across the dashboard, recording verification status, response shape, cadence, and data limitations.

| Card | Indicator | Primary Source | Fallback Source | NSE Status | Update Cadence | Probing Status |
|------|-----------|----------------|-----------------|------------|----------------|----------------|
| **Ticker** | Indices (NIFTY 50, BANK, IT) | NSE `api/allIndices` | Recorded cache snapshot | **Yes (Principal)** | 15–30s market hours | Pending live probe |
| **Ticker (SENSEX)** | SENSEX | BSE India or public quote | NIFTY 50 alternative | Non-NSE | 15–30s market hours | Pending live probe |
| **GDP Growth** | Real GDP Growth YoY (%) | IMF DataMapper `NGDP_RPCH` | World Bank `NY.GDP.MKTP.KD.ZG` | Non-NSE | Semi-annual (Apr/Oct) | Pending live probe |
| **Debt to GDP** | General Govt Gross Debt (% of GDP) | IMF DataMapper `GGXWDG_NGDP` | World Bank `GC.DOD.TOTL.GD.ZS` | Non-NSE | Semi-annual (Apr/Oct) | Pending live probe |
| **Trade Balance** | Merchandise Exports, Imports, Balance | Dept of Commerce / PIB | data.gov.in / World Bank | Non-NSE | Monthly (~15th) | Pending live probe |
| **GST Collections** | Gross GST Collections & Monthly Avg | PIB / GST Council press releases | Verified seed dataset (`seed/gst_monthly.csv`) | Non-NSE | Monthly (1st) | Pending live probe |
| **Inflation (IND)** | CPI (Combined) YoY & RBI Target | MoSPI / RBI | World Bank `FP.CPI.TOTL.ZG` | Non-NSE | Monthly (~12th) | Pending live probe |
| **Gov Expenditure** | Revenue, Capital & Total Expenditure | CGA / Union Budget / RBI | Verified seed dataset (`seed/gov_expenditure_annual.csv`) | Non-NSE | Monthly / Annual | Pending live probe |

Detailed endpoint schemas and probing results will be recorded following Phase 0 probes.
