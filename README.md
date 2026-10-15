# Economic Indicators Dashboard (Round II Interview Assignment)

A high-fidelity, real-time macroeconomic dashboard built with **React, TypeScript, FastAPI, and PostgreSQL**, faithfully reproducing the design specification for Indian economic indicators.

## 1. Overview & Live URLs
- **Frontend URL:** Deployed via Cloudflare Pages / Render (Configured in Phase 5)
- **Backend API URL:** Deployed via Render / Cloudflare Tunnel
- **Interactive Documentation:** `${API_URL}/docs`
- **Health Check:** `${API_URL}/health`

## 2. Architecture & Data Flow
```
Browser (React SPA, HTTPS)
       │  HTTPS + JWT / Refresh Cookie (CORS locked to frontend origin)
       ▼
FastAPI Backend (Separate Host, HTTPS)
  ├─ /auth/*        (login, refresh, logout, me)
  ├─ /api/v1/*      (dashboard indicators, ticker, history)
  ├─ /api/v1/stream (SSE real-time push)
  ├─ /health        (liveness & database readiness)
  └─ Background Collector (APScheduler)
       │ HTTP client with cookie management, backoff, and circuit breaker
       ▼
Upstream Data Sources (NSE, IMF DataMapper, World Bank, MoSPI, CGA, GSTN)
       │ Pydantic v2 validation → parameterized SQL
       ▼
PostgreSQL Database (Bound strictly to 127.0.0.1 / private network; port 5432 closed to public)
```

## 3. Local Setup & Run Instructions
*(To be detailed in Phase 1)*

## 4. Environment Variables
See `.env.example` for the full reference table.

## 5. Database Setup & Security Lockdown
- Direct parameterized SQL statements (no dynamic string concatenation).
- Database is strictly bound to `127.0.0.1` and unreachable from the public internet.

## 6. API Reference
See [docs/API.md](docs/API.md) for endpoint contracts and schema models.

## 7. Authentication & Panel Access
- In-memory JWT access token with 15-minute expiration.
- HTTP-only, secure, `SameSite=None` refresh token with automatic rotation.
- Panel evaluation user provisioned via `scripts/create_user.py` without committing credentials.

## 8. Data Sources Summary
See [docs/SOURCES.md](docs/SOURCES.md) for per-card upstream source mappings, cadences, and transformations.

## 9. Refresh Frequency & Real-Time Delivery
- Ticker polled every 20 seconds during trading hours (09:00–15:45 IST); every 10 minutes when closed.
- Macroeconomic indicators polled according to publication schedules.
- Updates pushed to the frontend via Server-Sent Events (SSE) with fallback to periodic polling.

## 10. Staleness & "—" Policy
- Zero hallucination policy: missing values are rendered as `—` (null).
- Upstream refresh failures retain the last-known-good observation and mark the indicator status as `stale`.

## 11. Assumptions
See [docs/DECISIONS.md](docs/DECISIONS.md) for architectural and design assumptions.

## 12. Known Limitations & Public Fallback Sources
- Non-NSE macroeconomic data relies on official public releases and verified historical seed series where automated machine APIs are not provided by governmental bodies.

## 13. Testing & CI
- Backend unit and integration tests with `pytest` and `respx`.
- Frontend linting, type checks, and Playwright visual regression at 1214×2159 viewport.
- Automated GitHub Actions workflow running tests, dependency audits (`pip-audit`, `npm audit`), and `gitleaks`.

## 14. Security Notes
- Zero secrets committed.
- Gitleaks automated scanning.
- Public database ports strictly blocked.

## 15. AI Usage Disclosure
- AI utilized for scaffolding, test generation, and CSS token parsing. Core architecture, security boundaries, and data validations verified manually.

## 16. Portfolio & Flagship Projects
*(To be provided by candidate for submission)*
