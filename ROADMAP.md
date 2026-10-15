# ROADMAP.md — Economic Indicators Dashboard (Interview Round II)

> **Audience:** AI coding agents (and the human owner) building this project end-to-end.
> **Source of truth order:** (1) Figma frame → (2) this file → (3) assignment text (summarised in §1) → (4) agent judgement, recorded in README.
> **Golden rules for every agent:**
> 1. Never invent a number. Missing → `null` → UI shows `—`. Failed refresh → keep last valid value, flag `stale`.
> 2. The browser talks **only** to our FastAPI. It never calls NSE or any upstream.
> 3. No secrets in the repo or in browser code. Everything via env vars.
> 4. SQL is always parameterized. No string-built SQL.
> 5. Every decision where the design/spec is open goes into `README.md → Assumptions` (see §16).
> 6. Anything that needs the human owner is listed in **§0**. If blocked on it, stop and ask; don't fake it.

---

## 0. WHAT THE OWNER (YOU) MUST PROVIDE

Agents cannot proceed fully without these. Check each off.

### 0.1 Blocking (needed before/while building)
| # | Item | Why | Where it goes |
|---|------|-----|---------------|
| 1 | **Figma access** to `https://www.figma.com/design/brsbeMh0t7dB6ibf3cJN4D/Economic-Indicator-Assignment?node-id=1-2` — either (a) a Figma **Personal Access Token** (read-only, file-content scope) so agents can call the Figma REST API, or (b) exported assets (see 0.2). The Figma link is login-gated; agents could not open it. | Design is the authority for layout, typography, colours, spacing, interactions (25 marks) | `FIGMA_TOKEN` in local `.env` only (never committed) |
| 2 | **Figma asset exports**: flags (India, US), globe icon, 3D illustrations on every KPI card (exports, imports, GST, calendar, inflation basket, RBI target, expenditure ×2), background/header texture, candlestick header art, LIVE badge, fonts used | These are raster/vector assets, not reproducible from code | `frontend/src/assets/` |
| 3 | **Font names/weights** used in Figma (the reference image looks like Segoe UI / Open Sans-style) | Typography fidelity | `frontend/src/styles/fonts.css` |
| 4 | **Hosting accounts** (one for the frontend, a *different* provider/machine for the API+DB). Suggested: frontend on Vercel / Netlify / Cloudflare Pages; API on AWS EC2/Lightsail, Hetzner, DigitalOcean, Oracle Cloud Free, Fly.io or Render | Assignment requires separate sites on different machines/environments, both HTTPS | Deployment phase (§13) |
| 5 | **Domain/subdomain choices** (e.g. `dash.<you>.com` and `api.<you>.com`) or accept provider default HTTPS domains | HTTPS + CORS allow-list needs exact origins | `CORS_ORIGINS`, `VITE_API_BASE_URL` |
| 6 | **Git repository** (GitHub, public or private-with-panel-access) | Submission | — |
| 7 | **JWT signing secret** (generate yourself: `openssl rand -hex 64`) | Auth | `JWT_SECRET` on server only |
| 8 | **Panel evaluation account** username + password (you choose; share *separately* from the repo) | "Test account … shared separately" | Created by `scripts/create_user.py` on the server; credentials sent to panel by email/portal |
| 9 | **Database password** (generate yourself) | DB access | `DATABASE_URL` on server only |

### 0.2 Optional but strongly recommended
| # | Item | Why |
|---|------|-----|
| 10 | **data.gov.in API key** (free; register at https://data.gov.in → My Account → API key) | Optional fallback for Indian trade/other OGD datasets |
| 11 | **MoSPI eSankhyiki** access details (portal https://esankhyiki.mospi.gov.in/ ; check whether an API key/endpoint is needed) | Preferred source for CPI inflation series |
| 12 | A **domain-name/DNS panel** login if using custom domains | TLS + CNAME/A records |
| 13 | **Uptime monitor** account (UptimeRobot/BetterStack free) | Health-check demonstration |

### 0.3 Submission material only you can write
| # | Item |
|---|------|
| 14 | **Portfolio website URL** |
| 15 | **Flagship project links** — for each: your role, main technologies, what you built |
| 16 | **Screen-recorded video** (content outline in §15) — must be in *your own words* |
| 17 | Final live URLs: frontend, API (or `/docs`), health check |
| 18 | Review/edit of README "Assumptions & limitations" so you can defend each item in the interview |

---

## 1. ASSIGNMENT SUMMARY (verbatim requirements, condensed — nothing omitted)

**Deliverable:** A deployed, working replica of the *Economic Indicators Dashboard* (React + FastAPI).

**Evaluation viewport:** **1214 × 2159 CSS px.** Whole screen legible and stable: no unintended horizontal scroll, no clipped content, no disruptive layout shift.

**Visible UI = live market ticker + six panels:**
1. GDP Growth — India and World (YoY, historical comparison)
2. Debt to GDP Ratio — India (comparison + trend as in design)
3. Imports, Exports and Trade Balance
4. GST Tax Collection (monthly average + historical comparison)
5. Inflation — India (RBI target + historical trend)
6. Government Expenditure (total + capital)

Reproduce charts, period labels, summary figures, change-vs-comparison-period values. **Every visible control must work.** Open behaviours → reasonable choice → record in README.

**Data requirements**
- Use **public NSE endpoints/pages as principal source for anything NSE publishes.**
- Browser requests data from **our FastAPI only** — never scrape NSE from the browser.
- Where NSE doesn't publish an indicator, use a **clearly identified public source**. Always document: source, observation date, transformation, limitation.
- UI shows **source + "as of" date per indicator/group**; **non-NSE sources are labelled in the UI and README.**
- **Validate** upstream responses before storing/displaying. **Timeouts, caching, rate-aware refresh.**
- Handle missing values/upstream failure **without inventing figures** or overwriting last valid observation with invalid data.
- States: **loading, empty, error, stale, unavailable.** Retained data after failed refresh = labelled **stale**; missing values = **"—"**.
- **Server-side scheduled collector** (or equivalent) for upstream calls. Document refresh frequency and how the frontend gets updates (**SSE** or documented equivalent).
- **Authentication:** JWT preferred. Protect routes that should need sign-in. Document token handling, expiry, and how panel evaluation access is granted.

**Technical/security**
- React frontend, FastAPI API. API base URL configurable. No upstream credentials in browser code.
- Database for snapshots/history. May be embedded on the API server. Prefer **direct parameterized SQL** (ORM optional). **Never concatenate untrusted input into SQL.**
- **DB must not be publicly reachable** — only backend machine/private network; enforce via **bind address + firewall/security group**.
- If a DB proxy is used: private **TCP** proxy accepting only the backend. A public HTTP reverse proxy is **not** a DB boundary.
- **Frontend and API deployed as separate websites on different machines/hosting environments, both HTTPS, CORS restricted to the deployed frontend origin.**
- **Health-check route.** Document: API routes, request/response formats, auth requirements, env var names, DB setup, local run instructions.

**Submit:** repo (frontend, backend, schema/migrations, README) · live frontend URL · API/docs URL · health URL · portfolio URL + flagship projects (role, tech, what built) · test account/instructions shared separately (no committed passwords/keys/tokens) · short list of assumptions, known limitations, public fallback sources.

**AI & presentation:** AI use is allowed; you must explain and defend all code. Submit a **screen-recorded video** (not promotional) covering: full user flow + how frontend/API/collector/DB fit together; how you built it + challenges + fixes; key technical/design decisions + reasons; **if AI used:** tasks, how output was incorporated, why appropriate, how verified; **if not used:** which tasks done manually and why.

**Marks (100):** Design fidelity 25 · Application behaviour 20 · Backend & data handling 15 · Security & DB access 15 · Performance & code quality 15 · Deployment & documentation 10.

---

## 2. DESIGN ANALYSIS (from the reference image in the docx; verify everything against Figma)

Reference image is only 457×673 px (≈ 0.377× of 1214 px width). Ratio 457:673 ≈ 1214:1788; the evaluation viewport is 1214×2159, so Figma frame likely has extra bottom/top space — **confirm real frame size and spacing in Figma.**

### 2.1 Layout (top → bottom)
1. **Page title** "ECONOMIC INDICATOR" — centred, bold, white caps, over a dark header with faint red/blue candlestick art.
2. **Ticker bar** (full width, blue outline in screenshot is a Figma selection box — *not* part of the design):
   - Red rounded **LIVE** badge with a dot (pulsing recommended)
   - Scrolling items separated by thin dividers: `SENSEX 73,158.24 (+0.42%)` (green), `NIFTY BANK 46,919.80 (-0.12%)` (red), `NIFTY IT 37,842.15 (+1.10%)` (green) … repeats (marquee loop).
3. **2-column × 3-row grid of cards** (dark navy glass cards with a folded/white-triangle top-left corner, gradient header strip, cyan sub-labels in parentheses):

| Row | Left card | Right card |
|-----|-----------|------------|
| 1 | **GDP Growth - India vs World (Y0Y%)** | **Debt to GDP Ratio (IND)** |
| 2 | **Imports, Exports & Trade Balance** | **GST Tax Collection (Y0Y%)** |
| 3 | **Inflation (IND)** | **Government Expenditure** |

### 2.2 Per-card content
**GDP Growth**
- KPI tile "India" (flag) `4.82%` + delta chip `▲ -0.2pp`; KPI tile "World" (globe) `3.82%` + `▲ -0.81pp`
- Legend: India (blue), World (orange)
- **Grouped bar chart**, x = years 2021–2025, y = 0–10% (step 2), value labels above bars, gridlines, rounded plot frame.

**Debt to GDP Ratio (IND)**
- KPI "India (FY25)" `3.82%` `▲ -0.81pp`; KPI "Ind vs US" (US flag) `3.82%` `▲ -0.81pp`
- **Area/line chart** (cyan line, gradient fill), y = 50%–100%, x labels `25 Jul, 1 Aug, 8 Aug, 15 Aug, 22 Aug`, grey pill labels at local points (e.g. peak, troughs), vertical gridlines.

**Imports, Exports & Trade Balance**
- KPI "Exports" `$382.9 B` `▲ -0.81pp`; KPI "Imports" `$382.9 B` `▲ -0.81pp` (illustration on right of each)
- Legend: Imports (blue), Exports (orange), Trade Balance (green line)
- Grouped bars (Imports/Exports) + **green line with dots** for trade balance, pill labels under points.

**GST Tax Collection (Y0Y%)**
- KPI "GST Collections" `3.82%` `▲ -0.81pp`; KPI "Monthly Average" `1.97` `▲ -0.81pp`
- Legend: Imports (blue), Trade Balance (yellow line) *(legend text looks copy-pasted from the trade card — rename to meaningful GST labels; record in README)*
- Blue bars + **yellow line with dots**, pill labels.

**Inflation (IND)**
- KPI "Inflation Rate" `2.1%` `▲ -0.2pp`; KPI "RBI Target" `4%` `▲ -0.2pp`
- **Line chart** (monthly-looking, 2021–2025 labels, y 0–10%), one pill label `6.3%`, fading left/right edges. A flat line near ~2% at the bottom could be the RBI band/target marker — **check Figma**.

**Government Expenditure**
- KPI "Total Expenditure" `4.82%` `▲ -0.2pp`; KPI "Capital Expenditure" `3.82%` `▲ -0.2pp`
- Legend: Revenue Expenditure (blue), Capital Expenditure (orange)
- **Stacked bars** 2021–2025 (orange capital at bottom, blue revenue on top), inner segment labels, total label above (`31.2`).

### 2.3 Visual tokens (approximate — replace with exact Figma values)
- Page bg: near-black `#0A0A0A–#111`; card bg: deep navy gradient `#050B1E → #0B1F3A`; card border/glow: teal-blue
- Accent cyan `#19B5E6`-ish (titles in parentheses, India bars, line); orange/amber `#F5A524`-ish (World/Exports/Capital); positive green `#2BD66A`-ish; negative red `#E5484D`-ish; LIVE badge red `#D93636`
- Text: white; muted labels light-blue-grey. Rounded corners ≈ 10–14 px; KPI tiles have inner glow.
- Export exact values via Figma API → `frontend/src/styles/tokens.css` (CSS variables). **Never hard-code colours in components.**

### 2.4 Inconsistencies in the mock the agent must handle (and log in README)
| Observation in design | Decision (default; override if Figma says otherwise) |
|---|---|
| Delta chips are always **green ▲** even with negative text (`▲ -0.2pp`) | Implement sign-aware chip: positive = green ▲, negative = red ▼, zero/null = grey `—`. If Figma explicitly shows green+▲ regardless, add a note to README and keep visual fidelity for matching states. |
| Chart y-axes are **%** on Imports/Exports and Expenditure charts (placeholder) | Use real units (US$ B, ₹ lakh crore, % of …) with correct axis titles; keep axis *style* identical. |
| Same placeholder numbers (8.7%, 6.3%, 3.82%) everywhere | Replace all with real data. Never keep mock values. |
| Debt/GDP x-axis is **dates (25 Jul–22 Aug)** but debt ratio is an annual/quarterly stat | See §6.2 — decision needed & documented. |
| GST legend says "Imports / Trade Balance" | Use "Gross GST (₹ lakh cr)" and "YoY growth (%)". |
| Header says "Y0Y%" (zero) | Display "YoY%" (letter O). Flag typo in README. |
| Ticker lists **SENSEX** | SENSEX is a **BSE** index, not NSE → see §5.1. |
| "Ind vs US" card meaning undefined | Define = India debt/GDP **minus** US debt/GDP, in pp (or ratio). Record in README. |

### 2.5 Interactions to implement ("every visible control must operate as represented")
- Ticker: continuous marquee; pause on hover/focus; `prefers-reduced-motion` disables scroll (static list). LIVE badge reflects real stream status (LIVE / DELAYED / OFFLINE).
- Chart hover tooltips + legend toggles (click legend item to hide/show series).
- Debt chart: x-axis range behaviour per §6.2; pill labels at annotated points.
- KPI tiles: values and deltas bound to data; tooltips explaining the comparison period.
- Header: **sign-in / sign-out** control (login screen is outside Figma → keep consistent styling).
- Per-card footer/badge: **Source + "as of"** (not in Figma → add unobtrusively; non-NSE sources get a "Non-NSE" tag).
- Check Figma for any additional states (hover, dropdowns, tabs, toggles) and implement all of them.

---

## 3. ARCHITECTURE

```
 Browser (React SPA, Vercel/Netlify/CF Pages, HTTPS)
        │  HTTPS + JWT (CORS locked to this origin)
        ▼
 FastAPI (separate host, HTTPS, e.g. EC2/VPS behind Caddy/Nginx)
   ├─ /auth/*         login, refresh, logout, me
   ├─ /api/v1/*       dashboard data (protected)
   ├─ /api/v1/stream  SSE updates (protected)
   ├─ /health         public
   └─ Collector (APScheduler in-process OR separate worker process)
        │ httpx (timeouts, retries, backoff, cookie-session for NSE)
        ▼
 Upstreams: NSE (ticker)  |  IMF DataMapper  |  World Bank  |  MoSPI/RBI  |  Commerce Ministry  |  GST (PIB/GSTN)  |  CGA/Union Budget
        │ validate (pydantic) → write snapshot
        ▼
 Database (private; Postgres bound to 127.0.0.1/private IP + firewall, or SQLite on API host)
```

**Recommended stack (pin versions in lockfiles):**
- Frontend: React 18 + Vite + TypeScript; charts via **Apache ECharts** (best fit for gradients, rounded bars, pill labels, stacked + combo) or Recharts/visx; TanStack Query for fetching; EventSource/`@microsoft/fetch-event-source` for SSE; CSS Modules or Tailwind with tokens.
- Backend: Python 3.11+, FastAPI, Uvicorn/Gunicorn, `httpx`, `pydantic` v2, `APScheduler`, `python-jose` or `PyJWT`, `argon2-cffi` (or bcrypt), `psycopg` v3 (Postgres) **or** stdlib `sqlite3`; `slowapi` for rate limit; `pytest`, `respx` for mocks.
- DB choice (decide in Phase 1): **Postgres on the same VM bound to `127.0.0.1` (or private IP) with firewall** — best demonstrates the "DB not public" requirement. SQLite on the API host is acceptable ("integrated database") and simpler; if chosen, state clearly in README that DB exposure is nil because there is no network listener, and the DB file is outside web root with `0600` perms.

---

## 4. REPOSITORY LAYOUT

```
/
├─ README.md                  (see §16 for required sections)
├─ ROADMAP.md                 (this file)
├─ docs/
│  ├─ SOURCES.md              (per-indicator source, URL, fields, cadence, transform, limitation)
│  ├─ API.md                  (route reference; mirror of OpenAPI)
│  ├─ DECISIONS.md            (ADR-style log)
│  └─ VIDEO_SCRIPT.md
├─ backend/
│  ├─ app/
│  │  ├─ main.py  config.py  deps.py  security.py
│  │  ├─ routers/ {auth.py, dashboard.py, stream.py, health.py}
│  │  ├─ collectors/ {base.py, nse.py, imf.py, worldbank.py, mospi.py, trade.py, gst.py, cga.py}
│  │  ├─ schemas/   (pydantic models for upstream + API)
│  │  ├─ services/  (snapshot store, staleness calc, derived metrics, SSE broker)
│  │  └─ db/ {pool.py, queries.py}
│  ├─ migrations/ 0001_init.sql …   (plain SQL; run via simple runner)
│  ├─ scripts/ {create_user.py, seed_history.py, run_collector_once.py}
│  ├─ tests/
│  ├─ pyproject.toml / requirements.txt
│  └─ .env.example
├─ frontend/
│  ├─ src/ {main.tsx, App.tsx, api/, auth/, components/{Ticker,Card,KpiTile,DeltaChip,SourceBadge,charts/*,states/*}, hooks/, styles/, assets/}
│  ├─ index.html  vite.config.ts  .env.example
│  └─ tests/ (Vitest + Playwright visual @1214×2159)
├─ deploy/ {Caddyfile or nginx.conf, systemd/*.service, ufw-rules.sh, docker-compose.yml(optional)}
└─ .github/workflows/ci.yml
```

---

## 5. DATA SOURCES — MAP & PROBING PLAN

> **Phase 0 task (mandatory):** before coding collectors, probe each source live from a shell **and from the deployment host's IP range**, save a redacted sample response to `backend/tests/fixtures/<source>.json|html`, and fill `docs/SOURCES.md`. Endpoints below were found in research but **must be verified live** — schemas and availability change, and some official sites block datacenter IPs.

### 5.1 Live market ticker — NSE (principal source)
| Item | Detail |
|---|---|
| Endpoint (unofficial but publicly used by the NSE website) | `https://www.nseindia.com/api/allIndices` → JSON `{ data: [ { index/indexSymbol, last, variation, percentChange, … } ], timestamp }` |
| Related | `https://www.nseindia.com/api/marketStatus` (open/closed → drives LIVE vs "Market closed"); `https://www.nseindia.com/api/equity-stockIndices?index=…`; `https://www.nseindia.com/api/holiday-master?type=trading` |
| Access pattern | NSE requires browser-like headers and **cookies**: first GET `https://www.nseindia.com/` (and e.g. `/market-data/live-market-indices`), reuse the cookie jar for the `/api/*` call. Send `User-Agent`, `Accept`, `Accept-Language`, `Referer: https://www.nseindia.com/`. Refresh cookies on 401/403. |
| Indices to show | **NIFTY 50, NIFTY BANK, NIFTY IT** (+ optionally NIFTY NEXT 50, NIFTY MIDCAP 100 to fill the marquee). |
| **SENSEX** | Design shows SENSEX, but **SENSEX is published by BSE, not NSE.** Options: (A) replace with NIFTY 50 and note the deviation; (B) fetch SENSEX from a **clearly labelled non-NSE source** (BSE India website/API, or another public quote page) and tag it "BSE" in UI + README. Pick (B) only if a stable public source is confirmed in Phase 0; otherwise (A). |
| Cadence | During market hours (09:15–15:30 IST Mon–Fri, excluding holidays): poll every **15–30 s** (rate-aware, single shared fetch, never per-client). Outside hours: poll every 5–15 min or stop, show last close with "Market closed · as of <timestamp>". |
| Risks | NSE blocks/throttles many cloud IPs and may change endpoints. Mitigations: cookie bootstrap, jittered backoff, circuit breaker, serve last valid snapshot flagged `stale`, run collector from a host where it works (test early!). Respect NSE terms of use; keep request volume minimal; document this in README. |
| Validation | pydantic model; `last > 0`, `percentChange` finite, timestamp parseable & not older than N min (else stale). |

NSE does **not** publish macroeconomic indicators (GDP, debt, trade, GST, CPI, expenditure) → those use public non-NSE sources below, each labelled **"Non-NSE"** in the UI.

### 5.2 GDP growth — India vs World (annual, YoY %)
| Priority | Source | Endpoint / notes |
|---|---|---|
| Primary | **IMF DataMapper (WEO)** – free, no key | `https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/IND/WEOWORLD` (also `/api/v1/indicators`, `/api/v1/countries`; v2 exists: `https://www.imf.org/external/datamapper/api/v2/NGDP_RPCH`). Code `NGDP_RPCH` = real GDP growth, annual %. `WEOWORLD` = world aggregate. Values include IMF **projections** for recent/future years — mark estimates vs actuals using the indicator's metadata/projection-start year. |
| Fallback | **World Bank Open Data API** – free, no key, CC BY 4.0 | `https://api.worldbank.org/v2/country/IN;WLD/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=100&date=2015:2026` (response = 2-element array: `[meta, rows]`; handle `null` values; `WLD` = World). |
| Notes | India's fiscal year (Apr–Mar) vs calendar-year labelling differs between IMF and World Bank; show chosen convention on the card and in README. Latest-year KPI = most recent **non-projected** year (or clearly marked estimate). Delta (pp) = latest − previous year. |

### 5.3 Debt-to-GDP — India (and India vs US)
| Priority | Source | Endpoint / notes |
|---|---|---|
| Primary | **IMF DataMapper** | `https://www.imf.org/external/datamapper/api/v1/GGXWDG_NGDP/IND/USA` (general government gross debt, % of GDP). |
| Fallback | World Bank | `https://api.worldbank.org/v2/country/IN;US/indicator/GC.DOD.TOTL.GD.ZS?format=json` (central govt debt, % GDP; sparse). |
| Notes | KPI "India (FY25)" = India value for the latest FY label; "Ind vs US" = India − US (pp) — record the formula. Chart axis: see §6.2. |

### 5.4 Imports, Exports, Trade Balance (US$ B)
| Priority | Source | Notes |
|---|---|---|
| Primary | **Department of Commerce, Ministry of Commerce & Industry** — Foreign Trade statistics (TradeStat: `https://tradestat.commerce.gov.in/`; quick estimates also published via PIB press releases) | Monthly merchandise exports/imports in US$ million; no documented public JSON API → implement a parser for the monthly release/PIB text or the TradeStat export page; aggregate months → fiscal-year totals; trade balance = exports − imports. |
| Alt | **data.gov.in OGD** dataset "Exports and Imports (India)" (HS-level, monthly; needs API key; may lag) | Aggregate `value_dl` (US$ million) by month/FY. Requires **your data.gov.in key (§0 #10)**. |
| Fallback | World Bank annual: `NE.EXP.GNFS.CD`, `NE.IMP.GNFS.CD` (goods & services, BoP basis) | Different definition (goods+services) → label clearly if used. |
| Notes | Goods vs goods+services must be stated. Units: show `$382.9 B` format. Delta = vs previous FY (or previous period — document). |

### 5.5 GST collections
| Priority | Source | Notes |
|---|---|---|
| Primary | **PIB (Ministry of Finance) monthly press releases** and GST portal/GSTN monthly data (e.g. `https://tutorial.gst.gov.in/downloads/news/…monthly_gst_data…pdf`; GST Council archive `https://gstcouncil.gov.in`) | Gross GST revenue per month (₹ crore). Since mid-2024 the Centre mostly shares headline figures rather than detailed releases → parse headline gross figures. No official JSON API found. |
| Implementation | Collector scrapes/parses the latest monthly release; **plus a curated, version-controlled historical seed file** `backend/seed/gst_monthly.csv` with columns `month, gross_inr_crore, source_url, retrieved_on` filled from official releases (agent must cite each URL; no unsourced numbers). | Provenance column is mandatory. |
| Derived | YoY% = (this period / same period last year − 1); **Monthly Average** = FY gross total ÷ months elapsed (in ₹ lakh crore). Bars = FY totals or monthly series (decision §6.3). |
| Sanity-check example (don't hard-code) | A secondary report of the GSTN advisory dated 01-06-2026 lists May 2026 gross GST ≈ ₹1,94,184 crore. Use only to test the parser. |

### 5.6 Inflation (CPI) and RBI target
| Item | Source / notes |
|---|---|
| CPI YoY | **MoSPI** (NSO) monthly press release / **eSankhyiki portal** `https://esankhyiki.mospi.gov.in/` ; press-release PDFs under `https://www.mospi.gov.in/uploads/latestReleases/…`. **Important:** CPI moved to **base 2024=100** from the January 2026 release (released Feb 2026) — series break vs old 2012 base; document and avoid mixing silently. Parse headline "All-India CPI (Combined) YoY". |
| Historical series | World Bank `FP.CPI.TOTL.ZG` (annual) or IMF `PCPIPCH` (`https://www.imf.org/external/datamapper/api/v1/PCPIPCH/IND`) for long history; RBI DBIE `https://data.rbi.org.in/DBIE` for monthly history. Chart shows monthly-looking line 2021–2025 → build monthly series from MoSPI/RBI data, else annual points with a note. |
| RBI target | **4% CPI, tolerance band ±2% (2–6%)**. Research shows the Government retained the 4% target for the period to **31 March 2031** (reported 25 Mar 2026). Store as a constants record with source URL + effective period; verify on RBI/Finance Ministry site in Phase 0. |
| Notes | KPI "Inflation Rate" = latest CPI YoY with release month as "as of"; show "provisional" flag if the release says so. |

### 5.7 Government expenditure
| Item | Source / notes |
|---|---|
| Monthly union accounts | **Controller General of Accounts (CGA)** monthly "Union Government Accounts" HTML: pattern `https://cga.gov.in/writereaddata/MonthAccount/{M}{YYYY}/DTL1{FYcode}.HTM` (observed e.g. `…/MonthAccount/72025/DTL12526.HTM`, `…/62026/DTL12627.HTM`; also `cga.nic.in` mirror). Contains Revenue / Capital / Total expenditure, monthly + year-to-date, current vs previous FY. Pattern must be re-verified; implement discovery by trying the latest month directory. |
| Summary table | **RBI Bulletin – "Union Government Accounts at a Glance"** (e.g. `https://rbi.org.in/SCRIPTs/BS_ViewBulletin.aspx?Id=24476`) lists Revenue Exp, Capital Exp, Total Exp with Budget Estimates and actuals (₹ crore). |
| Annual history (FY21–FY25/26) | **Union Budget documents** (`https://www.indiabudget.gov.in/`) "Expenditure Budget"/"Budget at a Glance", or RBI "Handbook of Statistics on the Indian Economy" for actuals. Seed as `backend/seed/gov_expenditure_annual.csv` with `fy, revenue_exp, capital_exp, total_exp, source_url`. |
| Display | Stacked bars: Capital (orange), Revenue (blue); total label above. KPI "Total Expenditure" / "Capital Expenditure" values and pp/percent change vs previous comparable period — define unit (₹ lakh crore vs % of GDP) after checking Figma; if "%", compute as % of GDP and state denominator. |

### 5.8 Source summary table (to reproduce in `docs/SOURCES.md` and in UI footers)
| Card | Source label in UI | NSE? | Update cadence | Refresh job |
|---|---|---|---|---|
| Ticker | NSE India | **Yes** | 15–30 s market hours | `collect_ticker` |
| GDP | IMF WEO DataMapper (fallback: World Bank) | No | Twice a year (WEO Apr/Oct) → check daily | `collect_gdp` |
| Debt/GDP | IMF WEO (fallback: World Bank) | No | same | `collect_debt` |
| Trade | Dept. of Commerce (fallback: World Bank / data.gov.in) | No | Monthly (~15th) | `collect_trade` |
| GST | PIB / GSTN | No | Monthly (1st–2nd) | `collect_gst` |
| Inflation | MoSPI (RBI target: RBI/MoF) | No | Monthly (~12th) | `collect_cpi` |
| Gov. expenditure | CGA / Union Budget / RBI | No | Monthly (~end of month) | `collect_fiscal` |

---

## 6. OPEN DESIGN/DATA DECISIONS (agents: pick the default, log it, ask owner if Figma contradicts)

### 6.1 Period convention
Latest 5 fiscal years available (x labels like `2021…2025`; if FY26 data is available as of Oct 2026, show the five most recent *complete or latest-estimate* years and label estimates). Axis labels as in Figma.

### 6.2 Debt/GDP chart axis
Figma x-axis = dates (`25 Jul … 22 Aug`) but debt/GDP is annual. **Default:** plot the IMF **annual** series (long history, e.g. 1990–latest) with year ticks, keep the 50–100% y-range and the area-gradient style; add short-range control only if Figma shows one. Document that the date labels in the mock are placeholders. *(Alternative: intramonth values are impossible without inventing data — forbidden.)*

### 6.3 GST chart
Bars = fiscal-year gross GST (₹ lakh crore) for the last 5 FYs; line = YoY growth %; "Monthly Average" = average of the current FY's published months (₹ lakh crore). "GST Collections" KPI = YoY% of latest period vs the same period last year.

### 6.4 Delta chip semantics
`pp` for rates (GDP, debt, inflation); `%` change for levels (trade, GST, expenditure) — match Figma text format where unit is shown as `pp`.

### 6.5 Staleness thresholds (per indicator, stored in config)
Ticker: > 2 min during market hours (or > 1 trading day when closed) · Monthly series: > expected release + 10 days · Annual series (IMF/WB): > 120 days.

---

## 7. DATABASE (direct parameterized SQL)

Plain-SQL migrations under `backend/migrations/`. Example (Postgres syntax; adapt for SQLite):

```sql
-- 0001_init.sql
CREATE TABLE users (
  id            BIGSERIAL PRIMARY KEY,
  username      TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,            -- argon2id
  role          TEXT NOT NULL DEFAULT 'viewer',
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE refresh_tokens (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash  TEXT NOT NULL UNIQUE,       -- store hash, not token
  expires_at  TIMESTAMPTZ NOT NULL,
  revoked_at  TIMESTAMPTZ
);

CREATE TABLE sources (
  id        TEXT PRIMARY KEY,             -- 'nse','imf','worldbank','mospi','commerce','gst','cga'
  name      TEXT NOT NULL,
  url       TEXT NOT NULL,
  is_nse    BOOLEAN NOT NULL DEFAULT FALSE
);

-- one row per (indicator, series, period) observation; append-only history
CREATE TABLE observations (
  id           BIGSERIAL PRIMARY KEY,
  indicator    TEXT NOT NULL,             -- 'gdp_growth','debt_gdp','exports','imports','gst_gross','cpi_yoy','gov_exp_revenue','gov_exp_capital', ...
  series       TEXT NOT NULL,             -- 'IND','WLD','USA','TOTAL', ...
  period       TEXT NOT NULL,             -- '2024','2025-26','2026-06'
  period_start DATE,
  value        DOUBLE PRECISION,          -- NULL allowed => shown as "—"
  unit         TEXT NOT NULL,
  is_estimate  BOOLEAN NOT NULL DEFAULT FALSE,
  source_id    TEXT NOT NULL REFERENCES sources(id),
  as_of        DATE NOT NULL,             -- observation/release date
  fetched_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  raw_ref      TEXT,                      -- URL or checksum of upstream payload
  UNIQUE (indicator, series, period, as_of)
);
CREATE INDEX ix_obs_lookup ON observations (indicator, series, period);

-- last-known-good snapshot per card (what the API serves)
CREATE TABLE snapshots (
  card         TEXT PRIMARY KEY,          -- 'ticker','gdp','debt','trade','gst','inflation','fiscal'
  payload      JSONB NOT NULL,            -- validated, ready-to-render DTO
  as_of        DATE,
  fetched_at   TIMESTAMPTZ NOT NULL,
  status       TEXT NOT NULL CHECK (status IN ('fresh','stale','unavailable')),
  last_error   TEXT,
  version      BIGINT NOT NULL DEFAULT 1
);

CREATE TABLE collector_runs (
  id BIGSERIAL PRIMARY KEY, job TEXT NOT NULL, started_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ, ok BOOLEAN, http_status INT, duration_ms INT, note TEXT
);
```
Rules: **only overwrite `snapshots.payload` after validation passes**; on failure update `status='stale'` + `last_error`, leave payload intact. Use `psycopg` placeholders (`%s`/named) or `sqlite3` `?` — never f-strings with user input. DB role used by the app has least privilege (no DDL at runtime; migrations use a separate role).

---

## 8. BACKEND API CONTRACT

Base: `${API_BASE_URL}`. JSON everywhere. Errors: `{ "error": { "code": "string", "message": "string" } }`.

| Method & path | Auth | Purpose |
|---|---|---|
| `GET /health` | public | `{status:"ok", version, time, db:"ok"\|"down", collector:{lastRun,...}}` — also `/health/ready` for DB check |
| `GET /docs`, `/openapi.json` | public (or protected — document choice) | Swagger UI |
| `POST /auth/login` | public | body `{username,password}` → `{access_token, token_type:"bearer", expires_in}`; sets refresh cookie |
| `POST /auth/refresh` | refresh cookie | rotate refresh token, new access token |
| `POST /auth/logout` | auth | revoke refresh token |
| `GET /auth/me` | auth | `{username, role}` |
| `GET /api/v1/dashboard` | auth | All six cards + ticker in one payload (single request on load) |
| `GET /api/v1/ticker` | auth | Ticker items + market status |
| `GET /api/v1/indicators/{card}` | auth | One of `gdp, debt, trade, gst, inflation, fiscal` |
| `GET /api/v1/indicators/{card}/history?from=&to=` | auth | Time-series (parameterized, validated dates) |
| `GET /api/v1/stream` | auth (see below) | **SSE**: events `ticker`, `card-update`, `status`, `ping` |
| `GET /api/v1/sources` | auth | Source registry (name, URL, NSE flag, cadence) |

**Per-card DTO (all cards share this envelope):**
```json
{
  "card": "gdp",
  "status": "fresh | stale | unavailable",
  "as_of": "2026-04-14",
  "fetched_at": "2026-10-15T06:30:00Z",
  "source": { "id": "imf", "name": "IMF WEO DataMapper", "url": "https://…", "is_nse": false },
  "kpis": [ { "key": "india", "label": "India", "value": 4.82, "unit": "%", "delta": -0.2, "delta_unit": "pp", "delta_basis": "vs 2024" } ],
  "series": [ { "key": "india", "label": "India", "points": [ { "x": "2021", "y": 8.7, "estimate": false } ] } ],
  "notes": ["Fiscal-year basis"],
  "message": null
}
```
Missing values: `"y": null` / `"value": null` — never `0`, never omitted silently.

**SSE auth:** native `EventSource` can't send an `Authorization` header. Use one of: (a) `@microsoft/fetch-event-source` with the Bearer header (preferred), or (b) `POST /auth/stream-ticket` → short-lived (≤60 s), single-use ticket in the query string. Document the choice. Server sends `ping` every 15 s; client auto-reconnects with backoff; on disconnect the UI falls back to polling `/api/v1/dashboard` every 60 s and badge shows "DELAYED".

**Cross-cutting:** CORS allow-list = exact frontend origin(s) only (no `*`); security headers (HSTS, `X-Content-Type-Options`, `Referrer-Policy`); request size limits; per-IP rate limit on `/auth/login` (e.g. 5/min) and general API; structured logging with no secrets/tokens; gzip; ETag/`Cache-Control: private, max-age=…` where safe.

---

## 9. COLLECTOR / SCHEDULER

- **APScheduler** (in the API process for simplicity, or a separate `collector` systemd service — preferred if >1 API worker, to avoid duplicate jobs).
- Jobs & cadence (jittered):
  | Job | Schedule (Asia/Kolkata) |
  |---|---|
  | `collect_ticker` | every 20 s Mon–Fri 09:00–15:45; every 10 min otherwise |
  | `collect_gdp`, `collect_debt` | daily 06:00 (cheap check; data changes ~2×/year) |
  | `collect_trade` | daily; heavier checks 14th–20th each month |
  | `collect_gst` | daily; heavier 1st–3rd each month |
  | `collect_cpi` | daily; heavier 11th–14th each month |
  | `collect_fiscal` | daily; heavier last 3 days / 1st–2nd each month |
- Each job: `fetch (timeout 10 s connect / 20 s read, ≤3 retries, exp. backoff + jitter) → parse → validate (pydantic + range/sanity checks) → compare to previous → upsert observations → rebuild snapshot DTO → write snapshot (single transaction) → publish SSE event`.
- Validation examples: GDP growth ∈ [−30, 30]; debt/GDP ∈ [0, 400]; CPI YoY ∈ [−10, 40]; trade ≥ 0; year/period well-formed; reject payloads whose schema changed; keep last valid.
- **Never** write `NaN`/empty into snapshots. A sudden >X% jump vs last value triggers a "suspect" flag + log (not auto-reject unless schema invalid).
- Circuit breaker per source (open after N consecutive failures; half-open probes).
- Single-flight lock per job; collector writes `collector_runs`.
- Cold start: run all jobs once at boot; if DB empty and upstream down → card status `unavailable` (UI shows unavailable state, no fake data).

---

## 10. AUTHENTICATION & AUTHORIZATION

- Passwords: **argon2id** (or bcrypt cost ≥12). No self-signup (assignment needs a controlled eval account).
- **Access JWT**: HS256 (or RS256), `exp` 15 min, claims `sub`, `role`, `iat`, `jti`; secret from `JWT_SECRET`.
- **Refresh token**: opaque random 256-bit, stored hashed in DB, 7-day expiry, rotation on each use, revoke on logout; delivered as `HttpOnly; Secure; SameSite=None; Path=/auth` cookie (cross-site because frontend/API are on different origins) — CORS `allow_credentials=True` with the exact origin. Access token kept **in memory** (not localStorage).
- Protected: everything under `/api/v1/*` and `/auth/me|logout`. Public: `/health`, `/auth/login`, `/auth/refresh`, (optionally `/docs`).
- Frontend: login page → store token in memory → axios/fetch interceptor attaches Bearer → 401 → one silent refresh attempt → else redirect to login. Route guard on `/`.
- **Granting panel access:** run `python scripts/create_user.py --username <panel> ` on the server (password from prompt/env) → send credentials privately. Optionally create `expires_at` on the user so access auto-lapses after the review window. Document this procedure in README *without* any real credentials.
- Brute-force protection: rate-limit + generic error message + short lockout after repeated failures.

---

## 11. FRONTEND IMPLEMENTATION PLAN

1. **Scaffold** Vite + React + TS; ESLint/Prettier; tokens (`tokens.css`) from Figma; fonts; global reset; `VITE_API_BASE_URL` (no hard-coded URL).
2. **Layout shell** fixed to design: page width target **1214 px** content area; CSS Grid 2 columns × 3 rows with Figma gaps; ensure **no horizontal scroll at 1214×2159** (`overflow-x: hidden` is *not* a fix — fix the cause). Use `min-width:0` on grid children; reserve chart heights to prevent layout shift (CLS ≈ 0); skeletons match final sizes.
3. **Primitives:** `Card` (folded-corner, glow border, header strip with cyan qualifier), `KpiTile` (icon/flag, label, value, delta chip, illustration), `DeltaChip`, `Legend` (toggle), `SourceBadge` (source + as-of + "Non-NSE" tag + stale pill), state components: `Skeleton`, `EmptyState`, `ErrorState` (retry), `StaleBanner`, `UnavailableState`.
4. **Ticker** component: marquee via CSS transform (duplicate list for seamless loop), pause on hover, reduced-motion fallback, LIVE badge states, green/red by sign, fixed number formatting (`en-IN` grouping, 2 dp, `(+0.42%)`).
5. **Charts** (ECharts recommended; wrap in thin `<Chart>` components, tree-shake imports):
   - GDP: grouped bars w/ gradient fills, value labels, rounded plot frame.
   - Debt: smooth area line, gradient fill, pill annotations at max/min/latest.
   - Trade: grouped bars + line with markers and pill labels.
   - GST: bars + line.
   - Inflation: line chart + RBI target reference line (4%) + optional 2–6% band; fade edges.
   - Expenditure: stacked bars, inner segment labels, total label.
   - All: tooltips, legend toggles, `null` points render as gaps with "—" in tooltip, ARIA labels / data-table fallback for accessibility.
6. **Data layer:** TanStack Query `useDashboard()`; SSE hook updates query cache; fallback polling; `stale` derived from server `status` + client clock.
7. **Auth UI:** `/login` page in the same visual language; guarded route; logout in header; session-expiry toast.
8. **States:** every card independently handles `loading | empty | error | stale | unavailable`; missing numbers `—`.
9. **Performance:** code-split charts, lazy-load heavy illustrations (WebP/AVIF, explicit width/height), preconnect to API, memoized option objects, `ResizeObserver` throttling; Lighthouse ≥ 90 perf on desktop target; bundle < ~300 KB gz JS if practical.
10. **Accessibility/QA:** keyboard-focusable legends, contrast checks, `prefers-reduced-motion`, semantic headings.
11. **Visual regression:** Playwright screenshot at **1214×2159** against a Figma export with pixel-diff threshold; iterate card by card until diff is small.

---

## 12. SECURITY CHECKLIST (15 marks — treat as acceptance criteria)

- [ ] No secrets in git (use `.env.example`; add `gitleaks` pre-commit/CI); `.env` in `.gitignore`.
- [ ] Browser bundle contains no upstream URLs requiring credentials/tokens; only `VITE_API_BASE_URL`.
- [ ] All SQL parameterized; lint rule/test grep to forbid f-string SQL.
- [ ] **DB not publicly reachable**: Postgres `listen_addresses='127.0.0.1'` (or private IP only), `pg_hba.conf` restricted to backend, firewall/security group denies 5432 from `0.0.0.0/0`; verify with an external `nmap`/`nc` from a different machine and keep the proof (screenshot/log) for the video & README. If a proxy is used, it is a **private TCP proxy** (e.g. HAProxy/stunnel in TCP mode) allowing only the backend IP.
- [ ] CORS = exact deployed frontend origin; test that other origins fail.
- [ ] HTTPS on both sites (auto-TLS via Caddy/Let's Encrypt or platform TLS); HSTS.
- [ ] JWT: short expiry, refresh rotation, secret ≥ 256 bit, algorithm pinned, `exp/iat` verified.
- [ ] Login rate limit, generic errors, argon2id, no user enumeration.
- [ ] Input validation with pydantic (query params, dates), response models to avoid leaking fields.
- [ ] Outbound requests: fixed allow-listed hosts only (SSRF guard), timeouts everywhere.
- [ ] Dependency scanning (`pip-audit`, `npm audit`) in CI.
- [ ] Logs exclude tokens/passwords.
- [ ] OS hardening on API host: non-root service user, `ufw` allow 22 (restricted), 80, 443 only; fail2ban optional.

---

## 13. DEPLOYMENT PLAN

**Topology (suggested, free/cheap):**
- **Frontend:** Vercel / Netlify / Cloudflare Pages → `https://<frontend-domain>` (env `VITE_API_BASE_URL=https://<api-domain>`).
- **API + collector + DB:** one VPS/VM (AWS EC2/Lightsail, Hetzner, DigitalOcean, Oracle Free) in a **different environment from the frontend host**:
  - Caddy or Nginx terminating TLS → Uvicorn/Gunicorn (`systemd`).
  - Postgres local, bound to loopback/private IP; firewall as per §12. *(Or SQLite file.)*
  - `deploy/` holds `Caddyfile`, `systemd` units, `ufw-rules.sh`.
- Run `migrations`, then `scripts/create_user.py`, then `scripts/run_collector_once.py` to warm data.
- **Test NSE reachability from this host early** (Phase 0/1); if NSE blocks the host IP, try another region/provider before launch.
- CI (GitHub Actions): lint + tests + build; optional auto-deploy.
- **Env vars (names only; document in README + `.env.example`):**

| Var | Where | Purpose |
|---|---|---|
| `APP_ENV` | API | `development`/`production` |
| `DATABASE_URL` | API | DB connection string (private) |
| `JWT_SECRET` | API | JWT signing key |
| `JWT_ACCESS_TTL_MIN` | API | default 15 |
| `JWT_REFRESH_TTL_DAYS` | API | default 7 |
| `CORS_ORIGINS` | API | exact frontend origin(s), comma-separated |
| `COOKIE_DOMAIN` / `COOKIE_SECURE` | API | refresh cookie settings |
| `NSE_BASE_URL` | API | default `https://www.nseindia.com` |
| `NSE_POLL_SECONDS_OPEN` / `_CLOSED` | API | polling cadence |
| `HTTP_TIMEOUT_CONNECT` / `HTTP_TIMEOUT_READ` | API | upstream timeouts |
| `DATA_GOV_IN_API_KEY` | API | optional OGD key |
| `ENABLE_SCHEDULER` | API | enable collector in this process |
| `LOG_LEVEL` | API | logging |
| `VITE_API_BASE_URL` | Frontend (build-time, public) | API base URL |
| `FIGMA_TOKEN` | local dev only | Figma export script (never deployed) |

- **Deliverable URLs to record:** frontend URL · API URL · `/docs` URL · `/health` URL.

---

## 14. PHASED EXECUTION PLAN (for agents)

Each phase ends with its **exit criteria**. Don't skip ahead.

**Phase 0 — Intake & probing (½ day)**
- Obtain Figma access/exports (§0). Extract frame `1-2`: sizes, fonts, colours, spacing, component tree, assets → `docs/DESIGN_SPEC.md` + `tokens.css`.
- Probe every upstream in §5; save fixtures; fill `docs/SOURCES.md` (URL, response shape, cadence, quirks, ToS notes, NSE reachability from your dev machine *and* planned host).
- Decide DB (Postgres vs SQLite) and SENSEX handling (§5.1). Log in `docs/DECISIONS.md`.
- **Exit:** every card has a confirmed primary (+ fallback) source or a documented seed-file plan; Figma tokens captured.

**Phase 1 — Backend foundation (1 day)**
- Project skeleton, config, logging, migrations, DB layer, `/health`, auth (login/refresh/logout/me), users script, CORS, rate limit, tests.
- **Exit:** can log in locally, `/health` OK, tests green, `.env.example` complete.

**Phase 2 — Collectors & snapshots (1–2 days)**
- Implement collectors (§5) with fixtures-based tests (`respx`), validators, snapshot builder, staleness logic, scheduler, `collector_runs`, `/api/v1/*` endpoints, SSE broker.
- Seed historical files with citations (GST, expenditure, any gaps).
- **Exit:** `GET /api/v1/dashboard` returns real validated data for all six cards + ticker; failure-injection test proves stale-keeps-last-valid; no fabricated values.

**Phase 3 — Frontend build (2 days)**
- Layout shell → primitives → ticker → each card/chart → auth flow → states → SSE/polling.
- Card-by-card Playwright diff @ 1214×2159.
- **Exit:** visually matches Figma; all controls work; no horizontal scroll; CLS ≈ 0.

**Phase 4 — Hardening (½–1 day)**
- Security checklist §12; error/loading/stale/unavailable UX test (kill upstream, kill SSE, expire token); performance pass; accessibility pass.

**Phase 5 — Deployment (½ day)**
- Provision hosts, TLS, firewall, DB lockdown proof, env vars, deploy both, warm data, create panel account, uptime monitor.
- **Exit:** all URLs live over HTTPS; CORS verified; DB port unreachable from the internet (evidence saved).

**Phase 6 — Docs & submission (½ day)**
- README (§16), `docs/*`, assumptions/limitations list, fallback sources, portfolio + flagship project write-ups, video (§15), final end-to-end walkthrough from a clean browser.

---

## 15. VIDEO PRESENTATION OUTLINE (owner records in own words)

1. **Flow demo (2–3 min):** open site → login → dashboard → hover/legend interactions → ticker/SSE live updates → show stale/unavailable state (e.g., by stopping the collector) → logout → `/health` and `/docs`.
2. **Architecture:** frontend ↔ API ↔ collector ↔ DB; where validation and caching happen; refresh cadences; how SSE reaches the UI.
3. **How you built it:** phases, main challenges (NSE cookies/blocking, no official APIs for GST/trade, series breaks like CPI base change, design placeholders vs real data, fiscal vs calendar years) and fixes.
4. **Decisions & reasons:** DB choice and lockdown proof, JWT + refresh design, SSE vs polling, chart library, SENSEX handling, Debt/GDP axis choice.
5. **AI usage statement (be specific):** which tasks (e.g., scaffolding, parsers, CSS, tests, docs), how outputs were reviewed/edited, why AI suited them, how verified (tests, fixtures vs live probes, manual diff vs Figma, security checklist). Also name tasks you did yourself and why.
6. Keep it factual, not promotional. Be able to explain *every* file.

---

## 16. README REQUIRED SECTIONS (agents scaffold; owner finalises)

1. Overview + live URLs (frontend, API, `/docs`, `/health`)
2. Architecture diagram + data-flow (browser → API → DB; collector → upstreams)
3. Local setup (backend, DB, migrations, collector, frontend) with copy-paste commands
4. Environment variables (table from §13)
5. Database setup + schema summary + lockdown description (bind address, firewall/SG rules)
6. **API reference:** routes, auth requirements, request/response examples, error format
7. **Authentication:** token types, expiry, refresh/rotation, storage, how panel access is granted (no secrets)
8. **Data sources table:** indicator, source, URL, observation date, transformation, limitation, NSE/Non-NSE
9. Refresh frequency & update delivery (collector schedule, SSE, polling fallback)
10. Stale/unavailable/empty/error behaviour and "—" policy
11. **Assumptions** (all items from §2.4 and §6 that were decided)
12. **Known limitations** and **public fallback sources used**
13. Testing (unit, collector fixtures, visual regression) and CI
14. Security notes
15. AI-use disclosure (short)
16. Portfolio link + flagship projects (role / tech / what built) — owner-written

---

## 17. DEFINITION OF DONE (self-grading against the marks)

| Area (marks) | Done when |
|---|---|
| Design fidelity (25) | Playwright diff vs Figma export is tight at 1214×2159; fonts/colours/spacing from tokens; all illustrations, flags, legends, labels, pill annotations present |
| Behaviour (20) | Login/guard works; ticker marquee + LIVE state; legends/tooltips; live updates via SSE with polling fallback; all states render correctly |
| Backend & data (15) | Validated data for all cards; source + as-of shown; stale keeps last valid; no invented numbers; timeouts/retries/caching/rate-aware jobs; tests with fixtures |
| Security & DB (15) | §12 fully ticked, with evidence for DB non-reachability and CORS restriction |
| Performance & code quality (15) | No CLS, fast initial load, clean modular code, typed, linted, tests pass in CI |
| Deployment & docs (10) | Two HTTPS sites on different hosts; health route; README complete; env/DB/run instructions accurate; panel account delivered privately |

---

## 18. KNOWN RISKS & MITIGATIONS

| Risk | Mitigation |
|---|---|
| NSE blocks cloud/datacenter IPs or changes endpoints | Probe early; cookie bootstrap; retries/backoff; stale-flag; try another host/region; document limitation honestly |
| SENSEX not from NSE | §5.1 options A/B; label non-NSE |
| No official JSON API for GST/trade/fiscal | Parser + cited seed CSVs with provenance; schema checks; stale handling |
| CPI base-year change (2024=100) breaks series continuity | Mark series break in chart/notes; don't splice silently |
| Figma inaccessible to agents | Owner supplies token/assets (§0); otherwise fidelity limited to the low-res reference image |
| Placeholder/contradictory mock values | Decisions in §2.4/§6; log in README |
| Cross-site cookies blocked by browsers | Prefer in-memory access token + `SameSite=None; Secure` refresh cookie; test in Chrome/Safari/Firefox; fallback: refresh token in body w/ rotation |
| Free-tier cold starts/sleep | Use an always-on VPS for API; uptime pinger |

---

## 19. REFERENCE LINKS (all found during research — re-verify before relying on them)

**Assignment / design**
- Figma frame: https://www.figma.com/design/brsbeMh0t7dB6ibf3cJN4D/Economic-Indicator-Assignment?node-id=1-2&t=JZ4vuTKW64IMif4u-1
- Figma REST API (for token-based export): https://www.figma.com/developers/api

**NSE**
- NSE site: https://www.nseindia.com/ · live indices page: https://www.nseindia.com/market-data/live-market-indices
- Endpoints seen used in community clients: `/api/allIndices`, `/api/marketStatus`, `/api/equity-stockIndices?index=…`, `/api/holiday-master?type=trading` (all under `https://www.nseindia.com`)
- Community reference implementation of the cookie/header pattern: https://huggingface.co/spaces/eshan6704/backend/blob/main/nsepython2.py ; Ruby client docs https://rubydoc.info/gems/nse_data

**IMF**
- DataMapper: https://www.imf.org/external/datamapper/ · API v1 indicators list: https://www.imf.org/external/datamapper/api/v1/indicators · v2: https://www.imf.org/external/datamapper/api/v2/NGDP_RPCH · terms: https://www.imf.org/external/terms.htm
- Codes: `NGDP_RPCH` (real GDP growth %), `GGXWDG_NGDP` (gross debt % GDP), `PCPIPCH` (inflation), entities `IND`, `USA`, `WEOWORLD`.

**World Bank**
- API v2 base: https://api.worldbank.org/v2/ · docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392 · browse: https://data.worldbank.org/indicator
- Indicators: `NY.GDP.MKTP.KD.ZG`, `GC.DOD.TOTL.GD.ZS`, `FP.CPI.TOTL.ZG`, `NE.EXP.GNFS.CD`, `NE.IMP.GNFS.CD`; aggregates `WLD`.

**India government sources**
- Trade: https://tradestat.commerce.gov.in/ · OGD dataset page (Exports & Imports India): https://ckandev.indiadataportal.com/dataset/exports-imports-india · data.gov.in: https://data.gov.in
- GST: PIB (https://pib.gov.in) · GST Council (https://gstcouncil.gov.in) · GST portal downloads (https://tutorial.gst.gov.in/downloads/news/)
- CPI: MoSPI https://www.mospi.gov.in · eSankhyiki https://esankhyiki.mospi.gov.in/ · RBI DBIE https://data.rbi.org.in/DBIE · RBI Bulletin https://www.rbi.org.in/Scripts/BS_ViewBulletin.aspx
- Fiscal: CGA https://cga.gov.in (monthly accounts under `/writereaddata/MonthAccount/`) · Union Budget https://www.indiabudget.gov.in/ · RBI Bulletin table "Union Government Accounts at a Glance"

**Tooling**
- FastAPI https://fastapi.tiangolo.com · APScheduler https://apscheduler.readthedocs.io · ECharts https://echarts.apache.org · TanStack Query https://tanstack.com/query · fetch-event-source https://github.com/Azure/fetch-event-source · Playwright https://playwright.dev · argon2-cffi https://argon2-cffi.readthedocs.io

---

### Final note to agents
If anything here conflicts with the Figma frame, **Figma wins** for visuals; this file wins for architecture/security; and the assignment text (§1) wins over both for requirements. When the data is unavailable, **show `—` and say so — never guess.**