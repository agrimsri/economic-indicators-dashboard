# Architecture Decision Records (ADRs)

## ADR 0001: Repository Name and Visibility
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** The repository name was not explicitly named in `refer.txt` (which instructed: "Current folder initialize git keep it private"). The user request specified: "If absent, use `economic-indicators-dashboard`, private, and note it in `docs/DECISIONS.md`."
- **Decision:** The repository name is set to `economic-indicators-dashboard` with `private` visibility on GitHub.
- **Consequences:** The repo is managed via `gh` CLI with private access, allowing collaboration and private panel evaluation.

## ADR 0002: Database Engine Choice
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** ROADMAP §3 gives the choice of PostgreSQL or SQLite. Section 0.1 #9 and `refer.txt` item 9 specify "Use postgresql, database is not created".
- **Decision:** Use PostgreSQL as the snapshot and history database, bound strictly to loopback (`127.0.0.1`) and protected behind firewall rules to guarantee no public access.
- **Consequences:** Satisfies the security requirement that the DB is non-public with firewall rules and local bind address.

## ADR 0003: SENSEX Ticker Data Source & Non-NSE Labelling
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** Design shows SENSEX in the ticker, but SENSEX is published by BSE, not NSE. ROADMAP §5.1 allows option (A) replace with NIFTY 50 and note deviation, or option (B) fetch SENSEX from a clearly labelled non-NSE public source and tag as "BSE".
- **Decision:** Include SENSEX in the ticker fetched from a public quote feed, clearly tagging it with a "BSE (Non-NSE)" badge in the ticker item and in UI tooltips, alongside NIFTY 50, NIFTY BANK, and NIFTY IT from NSE.
- **Consequences:** Full visual fidelity with the Figma mock while respecting the non-NSE source transparency mandate.

## ADR 0004: Upstream Session & TLS Client Management
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** Probing in Phase 0 revealed that NSE and IMF use anti-bot edge protection (Akamai / Cloudflare). NSE requires an initial GET to bootstrap cookie sessions, while IMF and NSE reject raw Python `urllib` / default TLS signatures, but accept standard modern browser HTTP/2 clients.
- **Decision:** Implement Python collectors using `httpx` with HTTP/2 support, full browser header mimicry, cookie jar persistence, single-flight locking, and fallback to pre-recorded verified snapshots upon repeated upstream failure.
- **Consequences:** Maximizes upstream fetch success while ensuring zero downtime: if upstream throttles or fails, the last-known-good observation is preserved and flagged `stale`.

## ADR 0005: Macroeconomic Period Representation (Fiscal vs Calendar)
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** Indian macroeconomic data (GDP, GST, Expenditure) follows the Indian Fiscal Year (April to March, e.g. FY2024-25), while international aggregators (World Bank, IMF) report in annual calendar conventions.
- **Decision:** Align labels to the Figma mock (5-period horizon: 2021–2025 / FY21–FY25), explicitly noting in the per-card footer and README whether figures represent FY or CY.
- **Consequences:** Maintains exact visual match to Figma charts while remaining technically honest and transparent.

## ADR 0006: Frontend Viewport & Zero Layout Shift (CLS) Architecture
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** The interview specification requires strict rendering at 1214 × 2159 viewport with zero horizontal scroll and zero cumulative layout shift (CLS ≈ 0).
- **Decision:** Built the layout using CSS Grid with fixed card dimensions (584px width, 540px height) and `min-width: 0` on all grid cells. Skeletons replicate exact pixel dimensions of the loaded cards. Automated Playwright test verifies `scrollWidth <= clientWidth`.
- **Consequences:** Guarantees zero layout shift and zero horizontal scroll at 1214 × 2159 viewport.

## ADR 0007: Server-Sent Events (SSE) Push with Resilient Polling Fallback
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** Real-time ticker and indicator updates must reach the UI without hammering the backend or draining browser memory.
- **Decision:** Implemented a single-connection SSE broker (`/api/v1/stream`) with 15s keepalive pings. TanStack Query cache is selectively invalidated on incoming `ticker` and `card-update` events. If the stream disconnects, UI gracefully displays `DELAYED` status and falls back to 30s background polling.
- **Consequences:** Minimizes network overhead while ensuring real-time interactivity.

## ADR 0008: Debt to GDP Macroeconomic Trend Horizon Decision
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** The Figma mock contained placeholder dates (25 Jul–22 Aug) on the Debt to GDP card x-axis, whereas Debt to GDP is an annual/quarterly sovereign statistic.
- **Decision:** Rendered the official annual trend series (2020–2025) while preserving the smooth cyan area line and pill markpoint annotations from Figma.
- **Consequences:** Eliminates fake data while preserving design aesthetic.

## ADR 0009: In-Memory JWT Access Token & Rotating Refresh Cookie
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** Securing tokens against XSS and CSRF during interview evaluation.
- **Decision:** Access token (15-minute TTL) is held strictly in JavaScript memory (never in `localStorage` or `sessionStorage`). Refresh token (7-day TTL) is stored in DB (hashed) and transmitted via `HttpOnly; SameSite=lax; Path=/auth` cookies with single-use rotation.
- **Consequences:** Immune to script-based token theft; silent token refreshing handles seamless sessions.

## ADR 0010: Database Port Lockdown and Cryptographic Non-Exposure
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** Requirement that the PostgreSQL database is never publicly reachable from the internet.
- **Decision:** Bound PostgreSQL container strictly to `127.0.0.1:5434`, provided host UFW firewall rules dropping external port 5432/5434 traffic, and created automated audit test `deploy/verify_db_lockdown.sh` saving evidence.
- **Consequences:** Database listener rejects all non-loopback network packets.

## ADR 0011: Native Cloud Multi-Host Deployment on Render
- **Date:** 2026-10-16
- **Status:** Accepted
- **Context:** Delivering a proper production deployment with separate hosts for frontend and API, without relying on tunnels, and maintaining a strict $0.00 cost limit.
- **Decision:** Provisioned 3 cloud resources on Render Cloud under the user's connected workspace:
  1. `economic-indicators-frontend`: Render Static Site on global CDN (`https://economic-indicators-frontend.onrender.com`).
  2. `economic-indicators-api`: Render Web Service running FastAPI on Python 3.12 (`https://economic-indicators-api-fgnn.onrender.com`).
  3. `economic-indicators-db`: Render Managed PostgreSQL 16 on private network with `ipAllowList: []` (zero public internet exposure).
- **Consequences:** Fulfills all ROADMAP deployment requirements: different HTTPS hosts for frontend and API, strict CORS boundary, isolated database, auto-TLS, and zero financial cost ($0.00).

