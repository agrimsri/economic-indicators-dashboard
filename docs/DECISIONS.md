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

## ADR 0003: SENSEX Ticker Data Source
- **Date:** 2026-10-15
- **Status:** Proposed / Under Verification (Phase 0)
- **Context:** Design shows SENSEX in the ticker, but SENSEX is published by BSE, not NSE. ROADMAP §5.1 allows option (A) replace with NIFTY 50 and note deviation, or option (B) fetch SENSEX from a clearly labelled non-NSE public source and tag as "BSE".
- **Decision:** Test live reachability in Phase 0. If a resilient public quote source for SENSEX is verified, provide SENSEX clearly tagged "BSE". Otherwise, default to NIFTY 50 and document the choice.
