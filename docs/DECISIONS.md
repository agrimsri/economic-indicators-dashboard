# Architecture Decision Records (ADRs)

## ADR 0001: Repository Name and Visibility
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** The repository name was not explicitly named in `refer.txt` (which instructed: "Current folder initialize git keep it private"). The user request specified: "If absent, use `economic-indicators-dashboard`, private, and note it in `docs/DECISIONS.md`."
- **Decision:** The repository name is set to `economic-indicators-dashboard` with `private` visibility on GitHub.
- **Consequences:** The repo will be managed via `gh` CLI with private access, allowing collaboration and private panel evaluation.

## ADR 0002: Database Engine Choice
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** ROADMAP §3 gives the choice of PostgreSQL or SQLite. Section 0.1 #9 and `refer.txt` item 9 specify "Use postgresql, database is not created".
- **Decision:** Use PostgreSQL as the snapshot and history database, bound strictly to loopback (`127.0.0.1`) or private network interface to guarantee no public access.
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
- **Decision:** Implement Python collectors using `httpx` with HTTP/2 support, full browser header mimicry, cookie jar persistence, and fallback to pre-recorded verified snapshots upon repeated upstream failure.
- **Consequences:** Maximizes upstream fetch success while ensuring zero downtime: if upstream throttles or fails, the last-known-good observation is preserved and flagged `stale`.

## ADR 0005: Macroeconomic Period Representation (Fiscal vs Calendar)
- **Date:** 2026-10-15
- **Status:** Accepted
- **Context:** Indian macroeconomic data (GDP, GST, Expenditure) follows the Indian Fiscal Year (April to March, e.g. FY2024-25), while international aggregators (World Bank, IMF) report in annual calendar conventions.
- **Decision:** Align labels to the Figma mock (5-period horizon: 2021–2025 / FY21–FY25), explicitly noting in the per-card footer and README whether figures represent FY or CY.
- **Consequences:** Maintains exact visual match to Figma charts while remaining technically honest and transparent.
