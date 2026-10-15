# Project Blockers & Gaps Tracker

This document tracks items from ROADMAP Section 0 that were missing or require owner input.

| # | Item | Status | Impact / Workaround | Owner Action Required |
|---|------|--------|---------------------|-----------------------|
| 1 | **Figma Personal Access Token** | Available | Token provided in `.env` (`FIGMA_TOKEN`). Allows extraction of nodes, styles, and assets via Figma API. | None currently. |
| 2 | **Figma Pre-exported Assets** | Resolved via Figma API | `refer.txt` noted: "I don't have currently, look for sources or wait till end". We will extract SVG/PNG assets directly using Figma REST API. | Will request assistance only if specific assets fail export. |
| 3 | **Figma Font Names/Weights** | Extracted via API | Can be read directly from the Figma document typography nodes via Figma REST API. | None currently. |
| 4 | **Hosting Accounts** | Configured | Render CLI and Cloudflared are available and authenticated in environment. | Deployment plan will target these environments. |
| 5 | **Domain / Subdomain Choices** | Resolved | `refer.txt` specified "Provider default". Will use Render/Cloudflare default HTTPS domains. | None. |
| 6 | **Git Repository** | Initializing | Initializing `economic-indicators-dashboard` as private GitHub repository. | None. |
| 7 | **JWT Signing Secret** | Available | Provided in `.env` (`JWT_SECRET`). | None. |
| 8 | **Panel Evaluation Account** | Available | Credentials specified in `refer.txt`. Will be seeded via `scripts/create_user.py`. | Never commit credentials. Share privately with panel. |
| 9 | **PostgreSQL Database** | In Progress | PostgreSQL service available locally; database needs creation and user provisioning. | Handled in Phase 1 setup. |
| 10 | **data.gov.in API Key** | Available | API key provided in `refer.txt`. | Configured in backend environment. |
| 11 | **MoSPI eSankhyiki Details** | Open / Non-blocking | Not provided in `refer.txt`. | MoSPI public releases and fallback sources (IMF/World Bank) will be probed. |
| 12 | **Custom Domain DNS** | Not needed | Provider default HTTPS domains used. | None. |
| 13 | **Uptime Monitor Account** | Optional | Pending setup if required for final deliverable demonstration. | Optional. |
| 14-16 | **Portfolio URL, Flagship Links, Video** | Submission stage | Belongs to submission deliverables (Phase 6). | Owner to provide for final submission. |
