# Project Blockers & Gaps Tracker

This document tracks items from ROADMAP Section 0 and their resolution status across the project lifecycle.

| # | Item | Status | Resolution Detail |
|---|------|--------|-------------------|
| 1 | **Figma Personal Access Token** | Resolved | Token supplied via `.env` (`FIGMA_TOKEN`); extracted document tree, color tokens, and frame geometry in Phase 0. |
| 2 | **Figma Pre-exported Assets** | Resolved | Extracted 25 vector and 3D PNG card illustrations directly via Figma REST API into `docs/reference/assets/` and `frontend/src/assets/`. |
| 3 | **Figma Font Names/Weights** | Resolved | Parsed Segoe UI typography tokens from frame nodes into `docs/DESIGN_SPEC.md` and `frontend/src/styles/tokens.css`. |
| 4 | **Hosting Accounts** | Resolved | Render CLI authenticated (`whoami: Agrim Srivastava`) and Cloudflared installed; infrastructure as code created in `deploy/render.yaml`. |
| 5 | **Domain / Subdomain Choices** | Resolved | Used default provider HTTPS domains with reverse proxy manifests (`deploy/Caddyfile`, `deploy/nginx.conf`). |
| 6 | **Git Repository** | Resolved | Initialized on branch `main` as private GitHub repository `agrimsri/economic-indicators-dashboard` via `gh`. |
| 7 | **JWT Signing Secret** | Resolved | Configured in GitHub Actions secrets and local `.env` (`JWT_SECRET`). |
| 8 | **Panel Evaluation Account** | Resolved | Reviewer account `agrim` provisioned via `backend/scripts/create_user.py` with Argon2id password hashing. |
| 9 | **PostgreSQL Database** | Resolved | PostgreSQL 16 container running locally on `127.0.0.1:5434` with migrations applied; verified 100% closed to public internet. |
| 10 | **data.gov.in API Key** | Resolved | Key stored in GitHub Actions secrets and `.env` (`DATA_GOV_IN_API_KEY`). |
| 11 | **MoSPI eSankhyiki Direct API** | Handled | Replaced with verified official public MoSPI CPI releases and World Bank Open Data CPI feeds (ADR 0004). |
| 12 | **Database Lockdown Proof** | Resolved | Verified via `deploy/verify_db_lockdown.sh` with evidence saved in `deploy/evidence_db_lockdown.txt`. |
| 13 | **Video Script** | Resolved | Talking points and walkthrough draft completed in `docs/VIDEO_SCRIPT.md`. |
