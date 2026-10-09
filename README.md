# FraudMesh

FraudMesh is an investigation-support workspace for exploring fraud signals as a connected evidence network. It combines deterministic risk and alert rules, graph exploration, evidence review, case workflows, event simulation, audit controls, and optional NVIDIA Nemotron reasoning.

> This project is a prototype for investigation support. It is not an automated enforcement or guilt-determination system.

## What it does

The application helps an investigator move from a suspicious signal to a reviewable explanation:

1. Load the canonical demo dataset.
2. Inspect explainable risk and deterministic alert signals.
3. Explore entities, links, clusters, evidence, and bounded graph paths.
4. Triage alerts and attach or reuse investigation cases.
5. Build findings, hypotheses, action plans, chronology, and contradiction review.
6. Replay held-out events, including invalid, duplicate, and out-of-order events.
7. Optionally request a grounded Nemotron reasoning draft.
8. Validate and persist only grounded reasoning output.
9. Inspect append-only audit history and reason-gated unmasking.

All scoring and alerts are deterministic and explainable. Human review remains required; the application does not automatically take enforcement action.

## Architecture

```text
Browser
  |
  | Vite React frontend :5174 (/api proxy)
  v
FastAPI backend :8000
  |
  +-- SQLite runtime database
  +-- deterministic alert/risk rules
  +-- graph, evidence, case, simulator and audit services
  +-- optional Nemotron client and reasoning validator
```

The frontend is a React/TypeScript single-page application. The backend is FastAPI with SQLite persistence. Deterministic demo workflows work without a live model when cached reasoning fixtures are available.

## Repository layout

```text
backend/app/                 FastAPI application and domain logic
backend/tests/               Backend tests
data/demo/                   Canonical synthetic demo records
data/ground_truth/           Deterministic evaluation labels
config/                      Alert, scoring and language-guard configuration
frontend/src/                React shell, routes and styles
frontend/public/assets/      Static assets and FraudMesh logo
docs/                        PRD, acceptance matrix, reports and logs
artifacts/                   Validation screenshots
Makefile                    Setup, test, build and run shortcuts
```

Runtime databases, local `.env` files, logs, generated test databases, `node_modules`, and build output are ignored by Git.

## Requirements

- Python 3.11+ recommended
- Node.js 18+ recommended
- npm and Git

Nemotron is optional for live reasoning.

## Setup

From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
npm --prefix frontend install
Copy-Item .env.example backend/.env
```

Set private values in `backend/.env`:

```dotenv
APP_ENV=dev
DATABASE_URL=sqlite:///data/runtime/fraudmesh.db
DATA_DIR=data/demo
DEMO_INVESTIGATOR_USER=investigator
DEMO_INVESTIGATOR_PASSWORD=replace-with-12-character-password
DEMO_ADMIN_USER=admin
DEMO_ADMIN_PASSWORD=replace-with-12-character-password
```

For `demo` or `prod`, set a non-placeholder `JWT_SECRET` of at least 32 characters. Never commit `backend/.env` or API keys.

## Run locally

Start the backend:

```powershell
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

```powershell
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5174
```

Open `http://127.0.0.1:5174/?protected=1#dashboard`.

Health check:

```text
GET http://127.0.0.1:8000/api/v1/health
```

The UI shows `API ONLINE` when the backend is available. The frontend proxies `/api` requests to the backend.

## Deploy on Render free tier

The repository includes `render.yaml` with a free API web service and a free static frontend. In Render, choose **New → Blueprint**, connect this GitHub repository, and apply the blueprint. Render will build the two services and provide public `onrender.com` URLs. The frontend build uses the committed pnpm lockfile for deterministic dependency installation.

Before the first deploy, set these private API-service variables in Render:

- `DEMO_INVESTIGATOR_PASSWORD`
- `DEMO_ADMIN_PASSWORD`
- `NEMOTRON_API_KEY` (optional)

The blueprint generates `JWT_SECRET` and keeps secrets out of the repository. If Render assigns different service URLs, update `CORS_ORIGINS` on `fraudmesh-api` and `VITE_API_ORIGIN` on `fraudmesh-ui`, then redeploy the frontend.

The free API service seeds the synthetic demo dataset at startup. Render free services sleep after inactivity and their local filesystem is ephemeral, so SQLite changes, cases, sessions, and audit records can disappear after restart/redeploy. This setup is for a demo, not production persistence. Render documents these free-tier limitations at [Deploy for Free](https://render.com/docs/free).

## Authentication

Demo users are created from the two password environment variables. Default usernames are `investigator` and `admin`; use the private values in your own `backend/.env`.

Protected mode supports signed access tokens, session revocation, expiry, failed-login lockout, role checks, append-only audit records, login throttling, expensive-request throttling, request-size limits, and security response headers. `APP_ENV=dev` permits local iteration; `demo` and `prod` enforce bearer authentication for protected API routes.

## Main UI areas

- **Dashboard** — risk breakdown, alert summary, event simulator, event submission, investigation queue, and safeguards.
- **Live Alerts** — R1–R6 rules, deduplication metadata, severity/status/date/rule filters, evidence, and triage actions.
- **Investigation Cases** — case lifecycle, notes, evidence, subgraphs, chronology, contradictions, findings, hypotheses, plans, and reasoning review.
- **Fraud Network** — entity search, type/link-strength filters, cluster isolation, zoom/pan, labels, paths, edge details, and evidence.
- **Causal Chain** — bounded source-to-target paths and relationship ledger.
- **Evidence Explorer** — searchable evidence index, masking, and reason-gated unmasking.
- **Audit & Access** — audit history and access-control review.

The responsive shell includes a mobile menu, route-aware titles, keyboard focus states, clickable brand navigation, and a custom not-found route.

## Backend capabilities

| Area | Purpose |
|---|---|
| Health/auth | Health, login, current session, logout |
| Dashboard/risk | Summary cards and explainable entity risk profiles |
| Alerts | R1–R6 sequencing, deduplication, filters, and triage |
| Events | Strict ingestion, duplicate detection, invalid outcomes, ordering warnings |
| Simulator | Reset and step the held-out event stream |
| Network | Search/detail, links, clusters, paths, and edge inspection |
| Evidence | Search, filters, masking, and audited unmasking |
| Cases | Lifecycle, notes, evidence, chronology, contradictions, findings, hypotheses, plans |
| Reasoning | Nemotron status, grounded review, validation, and recording |
| Audit/evaluation | Append-only history and ground-truth readiness |

The API entry point is `backend/app/main.py`; persistence and domain operations are in `backend/app/db/database.py`.

## Alerts and risk

Alert rules are deterministic and sequenced. R1 through R6 are covered, including cluster merge, band escalation, and complaint-touch behavior. Responses expose rule sequence, evidence references, stable deduplication keys, occurrence counts, severity, status, and timestamps.

Risk is an explainable investigation-priority signal, not a finding of fraud, guilt, or legal liability. The UI keeps that boundary visible.

## Nemotron integration

Nemotron is optional. Configure the NVIDIA-compatible OpenAI endpoint privately:

```dotenv
NEMOTRON_BASE_URL=https://integrate.api.nvidia.com/v1
NEMOTRON_API_KEY=your-private-key
NEMOTRON_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
NEMOTRON_TIMEOUT_S=90
NEMOTRON_MAX_TOKENS=2048
```

The client accepts a host or `/v1` base URL and never prints the API key. Prompts are bounded and masked before transmission. The validator accepts only grounded findings, hypotheses, and plan steps that refer to available evidence; unsupported output is withheld. Cached reasoning permits deterministic local review without a live model.

## Testing and build

```powershell
python -m pytest backend/tests
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

Or:

```powershell
make setup
make test
make build
```

Acceptance evidence is maintained in `docs/ACCEPTANCE_MATRIX.md`, `docs/ACCEPTANCE_EXECUTION_2026-10-09.md`, and `docs/IMPLEMENTATION_REPORT.md`.

## Safety and data boundaries

The included dataset is synthetic and intended for investigation-support demonstrations. Do not use it as production data. FraudMesh does not perform automatic account blocking, enforcement, or guilt determination.

Never commit `backend/.env`, NVIDIA/Nemotron keys, JWT secrets, real customer data, runtime SQLite databases, server logs, or generated test databases.

The server is the authority for identity, role, entity IDs, case IDs, scores, and action permissions. Frontend values are treated as untrusted input. The API uses parameterized SQLite queries, bounded request bodies, strict event validation, masking before reasoning transmission, and rate limits for login and expensive endpoints. The current prototype has no payment or arbitrary file-upload surface; those capabilities must be server-verified and size/type restricted before being added.

## Troubleshooting

### UI says `API OFFLINE`

Confirm the backend is running on port 8000 and open `http://127.0.0.1:8000/api/v1/health`. Refresh the frontend after it returns HTTP 200.

### Login returns 401

Check the demo password variables in `backend/.env`, restart the backend, and ensure the runtime database is writable.

### Live Nemotron reasoning is unavailable

Verify `NEMOTRON_BASE_URL`, `NEMOTRON_API_KEY`, and `NEMOTRON_MODEL`. Deterministic features and cached reasoning remain available without a live model.

### Port already in use

Use another local port and update the frontend proxy/CORS settings. Defaults are 5174 for Vite and 8000 for FastAPI.

## Project status

The implementation includes protected browser workflows, deterministic alert/risk processing, graph and case review surfaces, audit/masking controls, simulator workflows, Nemotron client/validator, and AC-01 through AC-70 evidence records. See `docs/IMPLEMENTATION_REPORT.md` for verification details and remaining production-hardening items.
