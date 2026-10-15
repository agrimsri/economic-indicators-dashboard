# Video Presentation Script & Talking Points

> **Note for the presenter:** This document provides draft bullet points and outline. Present the walk-through in your own authentic words. Target length: ~5 minutes.

## 1. Flow Demo (2–3 minutes)
- **Landing & Security Guard:** Show the unauthenticated state redirecting to `/login`.
- **Login Flow:** Log in with the review panel account. Emphasize in-memory access token storage and secure HTTP-only refresh cookie rotation.
- **Dashboard Overview:** Walk through the 1214×2159 viewport layout:
  - Header & Real-time Ticker: Live market badge, index movements, hover-to-pause interaction, accessibility reduced-motion support.
  - Six Indicator Cards: GDP Growth, Debt to GDP, Trade Balance, GST Collections, Inflation, Government Expenditure.
- **Interactions:**
  - Hover tooltips and ECharts interactivity.
  - Legend toggle (clicking series hides/shows).
  - Source citations ("as of" date, primary publisher, Non-NSE badge).
- **State Handling Demonstration:**
  - Show simulated stale data retention when upstream refresh fails (never wiping valid data).
  - Show unavailable state ("—" indicator) when data is missing.
- **Public Endpoints:**
  - Demonstrate `/health` returning service and database status.
  - Demonstrate OpenAPI documentation at `/docs`.

## 2. Architecture & Data Flow (1 minute)
- **Component Breakdown:**
  - Frontend: React + TypeScript + Vite + Apache ECharts + TanStack Query.
  - Backend: FastAPI + Uvicorn + Pydantic v2 validation + APScheduler collector.
  - Database: PostgreSQL with parameterized queries, strictly bound to private localhost/firewall.
- **Collector & Streaming:**
  - Scheduled background collectors polling at disciplined intervals.
  - Real-time updates delivered via Server-Sent Events (SSE).

## 3. Key Technical & Security Decisions (1 minute)
- **Strict Database Boundary:** Proof that port 5432 is closed to the public internet and accessible solely by the API.
- **Zero Hallucination Policy:** Strict rule that no numbers are manufactured; failed updates mark data as stale with last-known good values.
- **NSE Scraper Resilience:** Browser never hits NSE; backend manages sessions with cookie jars, backoff, and circuit breaking.
- **AI Usage Transparency:** Clarify where AI was leveraged (boilerplate, CSS tokens extraction, unit test coverage) vs. core architecture, validation rules, and security enforcement.
