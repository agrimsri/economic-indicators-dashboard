# Video Presentation Script & Interview Walkthrough Guide

> **Presenter Note:** This script outlines the 5-minute technical presentation for the Aditya Birla evaluation panel. Use these talking points to present in your own authentic voice while demonstrating the live application.

---

## Part 1: Live Application Walkthrough (2.5 minutes)

### 1.1 Landing & Security Verification
- **Visual:** Open a clean browser window at the dashboard URL.
- **Talking Point:**
  > "Welcome. This is the Economic Indicators Dashboard built for the Aditya Birla interview assignment. As you can see, the application immediately protects sensitive macroeconomic data behind an evaluation authentication barrier. Access tokens are held exclusively in JavaScript memory—never in `localStorage`—and refresh tokens use rotating, secure HTTP-only cookies to eliminate XSS and CSRF vectors."
- **Action:** Open the **Evaluation Access** modal, sign in with the evaluation reviewer credentials (`agrim`), and submit.

### 1.2 Layout & 1214 × 2159 Fidelity
- **Visual:** Full dashboard loads at the target 1214 × 2159 viewport.
- **Talking Point:**
  > "Upon signing in, the dashboard loads instantly into the exact 1214 by 2159 pixel evaluation viewport requested in the specification. Notice that there is zero horizontal scroll, zero layout shift (CLS ≈ 0) due to pre-sized skeleton placeholders, and the design tokens directly reproduce the Figma dark navy aesthetic with cyan glowing borders and the distinctive folded-corner visual accent on every card."

### 1.3 Real-Time Ticker & Non-NSE Transparency
- **Visual:** Focus on the market ticker banner.
- **Talking Point:**
  > "At the top, our market ticker streams real-time index values for NIFTY 50, NIFTY BANK, NIFTY IT, and SENSEX. Notice the pulsing red 'LIVE' badge indicating our Server-Sent Events stream is active. If I hover or focus on the ticker, the continuous CSS marquee pauses for readability, and `prefers-reduced-motion` is fully supported.
  > Importantly, adhering to our source-of-truth policy, SENSEX is explicitly tagged with an orange 'BSE' pill, because SENSEX is published by the Bombay Stock Exchange, not the National Stock Exchange."

### 1.4 Interactive Indicator Cards & ECharts Interactivity
- **Visual:** Hover over each of the 6 cards and click legend toggles:
  1. **GDP Growth (India vs World):** Grouped gradient bars with rounded tops and data labels.
  2. **Debt to GDP (India vs US):** Smooth cyan area curve with annotated pill markpoints at extremes.
  3. **Exports & Imports (India):** Grouped bars in US$ B with green Trade Balance line.
  4. **GST Collections:** Dual y-axis chart with gross GST bars and YoY% growth line.
  5. **Inflation Rate (CPI):** CPI line chart with RBI 4.0% dashed target reference line and 2%–6% shaded tolerance band.
  6. **Government Expenditure:** Stacked bars for Capital and Revenue expenditure in ₹ Lakh Crore with total sum labels.
- **Talking Point:**
  > "Every card features interactive Apache ECharts visualizations. Clicking any legend item dynamically toggles that series. All units are technically correct—US$ Billion, ₹ Lakh Crore, and percentage points—replacing the placeholder '%' from the design mock."

### 1.5 The Zero Hallucination & Staleness Policy
- **Talking Point:**
  > "One of our core engineering rules is zero hallucinated data. If an upstream release is pending, values render as an em-dash ('—'), never fabricated. If an upstream collector experiences a temporary network disruption or rate-limit, our backend circuit breaker trips, and the API serves the last-known-good observation flagged with a visible amber 'Stale' banner. We never drop valid historical data."

### 1.6 Health & Interactive API Documentation
- **Visual:** Open `/health` and `/docs` in new tabs.
- **Talking Point:**
  > "The public `/health` endpoint reports real-time system liveness, database pool readiness, and collector job telemetry. The OpenAPI specification at `/docs` documents every endpoint, schema model, and error envelope."

---

## Part 2: Architecture & Data Flow (1.5 minutes)

### 2.1 Decoupled Full-Stack Architecture
- **Talking Point:**
  > "Architecturally, the application is strictly decoupled:
  > - The frontend is a React 19 + TypeScript SPA built with Vite. The browser communicates exclusively with our FastAPI backend. The browser never touches NSE or external APIs directly.
  > - The FastAPI backend runs on Python 3.12 with asynchronous endpoints and Pydantic v2 schemas validating every input and upstream payload.
  > - Collectors run in the background with single-flight locks, exponential backoff with jitter, and an automatic circuit breaker.
  > - Real-time push is handled via Server-Sent Events (SSE) at `/api/v1/stream` with a 15-second keepalive ping. If disconnected, the frontend automatically falls back to periodic polling."

---

## Part 3: Security & Database Lockdown (1 minute)

### 3.1 Database Port Lockdown Evidence
- **Visual:** Show terminal or `deploy/evidence_db_lockdown.txt`.
- **Talking Point:**
  > "Security was treated as a first-class acceptance criterion:
  > - All database queries are 100% static, parameterized SQL. We wrote an AST parser test (`test_sql_safety.py`) in our test suite that fails CI if any f-string or string formatting is detected in the database layer.
  > - The PostgreSQL database is bound strictly to `127.0.0.1`. We executed an automated network audit script (`deploy/verify_db_lockdown.sh`) confirming that local loopback connections succeed, while external connection attempts to port 5434 are refused.
  > - Host UFW firewall rules drop all public database traffic.
  > - Automated CI pipelines enforce Gitleaks secret scanning, `ruff` linting, `pip-audit`, and `npm audit` with zero vulnerabilities across all dependencies."

### 3.2 Closing Summary
- **Talking Point:**
  > "In summary, the project was built following modular phases, tracked with GitHub issues, short-lived PRs, and strict Exit Criteria. It delivers visual fidelity, live data reliability, zero fabricated data, and an audited security boundary. Thank you, and I look forward to your questions."
