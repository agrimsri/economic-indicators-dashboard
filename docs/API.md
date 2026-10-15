# Economic Indicators Dashboard — API Specification

The FastAPI backend exposes endpoints for authentication, real-time dashboard data, historical metrics, server-sent events (SSE), and system health monitoring.

## Base URL
`${API_BASE_URL}` (configured via `VITE_API_BASE_URL` on frontend)

## Authentication
JWT-based authentication using HTTP-only secure refresh cookie and short-lived in-memory bearer access token.

## Endpoints Summary

| Method | Path | Auth Required | Description |
|--------|------|---------------|-------------|
| `GET` | `/health` | Public | System liveness, database status, and collector status |
| `GET` | `/health/ready` | Public | Database readiness check |
| `GET` | `/docs` | Public | OpenAPI / Swagger interactive documentation |
| `POST` | `/auth/login` | Public | Authenticate user, return access token and set refresh cookie |
| `POST` | `/auth/refresh` | Refresh Cookie | Rotate refresh token and issue new access token |
| `POST` | `/auth/logout` | Bearer Token | Revoke active refresh token |
| `GET` | `/auth/me` | Bearer Token | Retrieve authenticated user profile and role |
| `GET` | `/api/v1/dashboard` | Bearer Token | Unified snapshot of all 6 indicator cards and ticker |
| `GET` | `/api/v1/ticker` | Bearer Token | Real-time market indices and market status |
| `GET` | `/api/v1/indicators/{card}` | Bearer Token | Single indicator payload (`gdp`, `debt`, `trade`, `gst`, `inflation`, `fiscal`) |
| `GET` | `/api/v1/indicators/{card}/history` | Bearer Token | Historical observation series with parameterized date filtering |
| `GET` | `/api/v1/stream` | Bearer Token | SSE stream for real-time ticker and indicator updates |
| `GET` | `/api/v1/sources` | Bearer Token | Complete registry of data sources, URLs, and update cadence |
