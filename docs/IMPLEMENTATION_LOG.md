# FraudMesh implementation log

## Nimbus token factory

- Added `backend/app/auth/token_factory.py` with a dependency-free Nimbus-style HS256 access-token factory. Tokens include `kid`, `sub`, `username`, `role`, `jti`, `iat`, `exp`, `iss`, and `aud` claims.
- Login now issues signed access tokens when `JWT_SECRET` is configured; the SQLite session table remains authoritative for expiry, active-user checks, and logout revocation.
- Verification rejects tampered, expired, wrong-key, wrong-issuer, and wrong-audience tokens before database lookup. `TOKEN_KEY_ID`, `TOKEN_ISSUER`, and `TOKEN_AUDIENCE` are configurable.
- Added round-trip and tamper/expiry tests. Backend suite: `12 passed`.

## R5 band escalation

- Added deterministic Low/Medium/High/Critical band helpers using the PRD thresholds (0–24, 25–49, 50–74, 75–100).
- Alert scoring compares the current snapshot with the state immediately before each entity's latest victim-payment event. When the band rises, R5 fires and the latest event evidence ID is included.
- Alerts now expose `band`, `previous_band`, and `previous_score`; R5 severity is Warning unless the new band is Critical, which is Critical. Backend suite remains `12 passed`.

## Alert deduplication and filters

- Added stable `alert_id`, `dedup_key`, `occurrences`, and `created_at` metadata to deterministic alert responses. The current snapshot emits one canonical alert per entity/rule set; repeated triage actions update the derived status instead of creating duplicate UI rows.
- Added `/api/v1/alerts` filters for severity, status, rule, `date_from`, and `date_to`, with validation for unsupported severities.
- Added matching Live Alerts controls and detail display for filters, status, band transition, and occurrence context. Frontend build and Vitest pass; backend suite remains `12 passed`.

## Graph inspection workflows

- Network edges now include grouped evidence IDs and a dedicated `/api/v1/network/edge` inspection endpoint returning transaction evidence, timestamps, channels, and amounts.
- Network UI now supports entity-type filtering, selected-cluster isolation, clickable edge inspection, evidence IDs, and transaction detail alongside existing bounded path search.
- Backend suite remains `12 passed`; frontend Vite build and Vitest pass.

## Timeline contradiction workflow

- Added deterministic `GET /api/v1/cases/{case_id}/contradictions` output for amount-mismatch candidates and explicit unverified claims.
- The case workspace now displays contradiction candidates beside the software-ordered timeline. Ledger/timestamp values remain authoritative; narrative claims are never silently substituted into the timeline.
- Backend suite remains `12 passed`; frontend Vite build and Vitest pass.

## Nemotron verification status

- Confirmed the client has graceful unconfigured behavior and the validator withholds fabricated evidence and hedges accusatory language; backend suite remains `12 passed`.
- Before local configuration, a real live Nemotron call was unavailable because the endpoint settings were absent; the recording CLI correctly refused safely.

## Nemotron live verification

- Local `backend/.env` was corrected from Windows' accidental `.env.txt` filename so pydantic-settings loads it.
- Fixed the client URL join so both `https://integrate.api.nvidia.com` and `https://integrate.api.nvidia.com/v1` are supported without producing `/v1/v1/chat/completions`.
- Live request to `nvidia/nemotron-3.5-lightning-30b-a3b` completed successfully and returned `NEMOTRON_OK`.
- Backend suite after the fix: `13 passed`. No local case currently exists in the runtime database, so end-to-end `record-reasoning` recording still needs a case to be seeded/created.
- Full synthetic recording verification completed in a temporary isolated database: `record-reasoning` returned `recorded` for `CASE-001`, the validator withheld one unsupported claim, and the temporary database/output were removed.

## Sentry-inspired UI language

- Added the generated Sentry design reference at `frontend/sentry/DESIGN.md`.
- Applied its midnight-violet canvas, lime signal accent, violet hairlines, rounded console cards, dark/light CTA hierarchy, and Rubik-style UI typography as a product-theme override in `frontend/src/styles.css`.
- Preserved FraudMesh’s alert severity semantics and synthetic-data safeguards. Frontend Vite build and Vitest pass.

## Stage 1 — Repository inspection and project setup

- Status: partially verified; blocked from full gate by local process/network restrictions.
- Findings: repository was empty and had no Git metadata; source documents are now present and copied into `docs/`.
- Tooling: Node.js v26.7.0 and npm 11.19.0 detected. The bundled Python 3.12.14 runtime was used because the normal Python launcher was unavailable.
- Changes: initial backend/frontend skeleton, environment template, ignore rules, config placeholders, and discrepancy log created.
- Verification: backend pytest passed (3 passed); frontend Vite production build passed; frontend Vitest passed (1 passed) with `--pool=threads --maxWorkers=1`.
- Live health request: not verified. The uvicorn process did not remain reachable from the separate shell, and local socket access was denied/refused by the managed environment.
- Dependency setup: completed using the bundled Python runtime and pnpm after elevated network/filesystem approval. `node_modules/` and `frontend/dist/` remain local build artifacts and are ignored.
- Git: no repository existed at Stage 1 start, so no Stage 1 commit was possible.

## UI design update — BMW corporate system

- Installed `getdesign@0.6.25` preset `bmw`; active reference is `frontend/DESIGN.md`.
- Replaced the BMW M dark language with the corporate BMW system: white canvas, BMW blue, dark navy hero band, rectangular controls, lighter density, and no persistent M stripe.
- Preserved FraudMesh-specific safety language and honest empty states; no automotive imagery or brand claims were added.
- Verification: Vite production build passed after the redesign; browser preview showed the updated corporate layout.

## Stage 2–3 — Synthetic data and persistence foundation

- Status: completed and verified for canonical seed `S1`.
- Generated deterministic synthetic dataset under `data/demo/` with manifest, victims, accounts, entities, UPI identifiers, phones, devices, transactions, complaints, communications, flags, benign identifiers, held-out events, and evaluation ground truth.
- Canonical dataset counts: 20 victims, 43 accounts, 8 holder entities, 56 transactions, 13 complaints, 9 communications, 5 devices, 6 phones, and 6 UPI identifiers.
- Loaded dataset into SQLite with `backend/app/cli.py reset-and-seed`; verified load result: 138 evidence records, 51 entities, 56 transactions, 13 complaints, and 9 communications.
- Added deterministic generator tests and loader safety tests. Verification: `6 passed` with `pytest tests -q`.
- Safety gate: loader rejects datasets whose manifest is not explicitly marked synthetic.
- Discrepancy D-001 records the intentional stdlib `sqlite3` implementation choice.

## Live verification — local demo runtime

- Started Vite on port 5173 and Uvicorn on port 8000.
- Reloaded the browser dashboard at `http://127.0.0.1:5173/#alerts` and verified `API ONLINE` plus live dataset metrics: 4 active investigations, 51 connected entities, and 138 evidence records.
- Reloaded the canonical seed into `data/runtime/fraudmesh.db`, the database path used when the API is started from the project root.
- Frontend verification: Vite production build passed; Vitest passed (`1` test file, `1` test).

## Navigation wiring fix

- Replaced the dashboard-only shell with hash-routed views for Dashboard, Live Alerts, Investigation Cases, Fraud Network, and Evidence Explorer.
- Navigation now updates the active state and page content on every click while preserving live API counts.
- Browser verification: Evidence Explorer rendered 138 indexed records; Fraud Network rendered 51 loaded entities; API remained ONLINE.

## Risk and evidence endpoints

- Added deterministic explainable risk aggregation over victim-payment patterns, distinct senders, aggregate value, and the synthetic seeded-flag table.
- Added live API routes: `/api/v1/alerts`, `/api/v1/network`, and `/api/v1/evidence`.
- Connected dashboard, alerts, network, and evidence views to live endpoint responses.
- Browser verification: Live Alerts rendered 3 priority signals with derived scores and reasons; API remained ONLINE.
- Verification: backend `6 passed`; frontend build passed; frontend Vitest passed (`1` test file, `1` test).

## Alert review interaction

- Added selectable alert rows with active-state styling and an explanation pane.
- Each selected signal exposes its derived score, reasons, synthetic amount context, and the human-review safety boundary.
- Verification: frontend production build and Vitest passed after the interaction update.

## Persistent investigation cases

- Added SQLite-backed `investigation_cases` storage and `/api/v1/cases` GET/POST routes.
- Added an `Open investigation case` action to the selected alert detail view.
- Cases preserve the source entity, derived score, status, creation timestamp, and explainable signal notes; they are reset when a new synthetic dataset is seeded.
- Cases page now renders saved open investigations and review protocol context.
- Verification: backend `6 passed`; frontend build and Vitest passed.

## Case detail and investigator notes

- Added selectable case rows and a case detail pane.
- Added editable investigator notes with persisted `PUT /api/v1/cases/{case_id}/notes` updates.
- The UI confirms when notes are saved to the local synthetic case record.
- Verification: backend `6 passed`; frontend build and Vitest passed; backend restarted with the notes endpoint active.

## Case evidence timeline

- Added `GET /api/v1/cases/{case_id}/evidence` to retrieve linked transaction evidence for the selected case entity.
- Case detail now renders a chronological evidence timeline with transaction ID, type, timestamp, channel, amount, direction, and reference.
- Verification: backend `6 passed`; frontend build and Vitest passed; backend restarted with the timeline endpoint active.

## Interactive fraud network graph

- Replaced the network placeholder with a deterministic SVG graph derived from live API nodes and edges.
- Nodes are selectable; the selected entity highlights connected paths and populates a path inspector with relationship counts and human-review context.
- Browser verification: 51 entities loaded, 24 linked entities rendered, and ACC-D1 selected with 9 connected relationship groups.
- Verification: frontend build and Vitest passed.

## Evidence Explorer search and filters

- Replaced the evidence placeholder with a searchable, filterable evidence index.
- Search submits to the backend evidence endpoint; type filtering is applied to returned records and can be cleared without a reload.
- Browser verification: searched `complaint` and received 13 complaint records from `complaints.json`, including timestamps and source rows.
- Verification: frontend build and Vitest passed.

## Case status workflow

- Added persistent case status transitions: `open`, `in_review`, and `resolved`.
- Added `PUT /api/v1/cases/{case_id}/status` and a status selector in the case detail view.
- Verification: backend `6 passed`; frontend build and Vitest passed; backend restarted with status updates active.

## Verification hardening

- Added reseed cleanup for flags, settings, and investigation cases so repeated synthetic dataset loads are idempotent.
- Extended database tests to verify a second load returns the same 138 evidence records without UNIQUE constraint failures.
- An in-process ASGI integration test was attempted but removed because the managed Windows runtime hangs on this app's middleware/ASGI transport; live browser/API verification remains the reliable integration check in this environment.
- Verification: backend `6 passed`.

## Evaluation readiness

- Added `GET /api/v1/evaluation` for a deterministic held-out synthetic-data check against `data/ground_truth/ground_truth.json` and `data/demo/events_heldout.json`.
- Added a dashboard readiness panel showing surfaced entities and transaction-event coverage without presenting it as a production model metric.
- Current baseline result: `2 / 6` held-out transaction events covered (`33.3%`); narrative-only events remain explicitly separated from transaction coverage.
- Limitation: this is an honest deterministic evaluation signal for the seeded prototype, not a calibrated fraud-model accuracy or recall score.
- Hardened dataset-path resolution so evaluation works when the loader stores a backend-relative path such as `..\\data\\demo`.
- Verification: backend `6 passed`; frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## Entity search slice

- Added `GET /api/v1/search?q=...` backed by normalized entity-key prefix matching.
- Search removes formatting characters before matching, enforces a four-character minimum, caps result size at 100, and returns a structured validation error for short queries.
- Added a database test covering formatted account lookup and short-query rejection.
- Verification: backend `6 passed`.
- Evidence Explorer now includes a live Entity lookup form that calls the search route and renders matching entity IDs, types, and display labels with short-query/no-result feedback.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## Interaction verification hooks

- Added stable graph hooks: `data-testid="network-graph"`, node/edge counts, and selected entity state.
- Added timeline hooks with event count and keyboard activation for SVG graph nodes using Enter or Space.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## Prototype limitations and control boundaries

- Added `GET /api/v1/meta/limitations` with live control-status data for synthetic-only ingestion, human review, explainable scoring, Nemotron reasoning, and authentication/audit hardening.
- Dashboard now renders these safeguards and explicitly labels not-yet-implemented controls instead of implying production readiness.
- Verification: backend `6 passed`; frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## Authentication and audit foundation

- Added SQLite-backed users, sessions, lockout counters, revocation, login/logout/me routes, admin-only audit and user listing routes, and append-only audit records.
- Passwords use a salted memory-hard `scrypt` implementation available in the bundled runtime; production Argon2id migration and complete bearer enforcement across legacy routes remain open.
- Added tests for session lifecycle, revocation, audit creation, and five-failure lockout.
- Added `setup-demo-users` CLI command so passwords are supplied at setup time and never committed to the repository.
- Verification: backend `8 passed` using a workspace-local pytest temp directory.
- Added API-boundary masking for common phone, account-number, and email/UPI-like patterns in evidence text; raw database search remains server-side.
- Verification after masking fix: backend `8 passed`.
- Added `POST /api/v1/evidence/{evidence_id}/unmask`; it requires a bearer session and an 8-character reason, returns the selected raw record, and writes an `evidence_unmask` audit event.
- Default evidence listing remains masked; unmasking is explicit and attributable.

## Real-time event ingestion slice

- Added `POST /api/v1/events` for validated transaction events.
- Valid events persist as live evidence and transactions, so the existing network and risk calculations can include them.
- Duplicate `event_id` submissions are idempotent and return `duplicate`; invalid kinds, missing fields, and non-positive amounts return structured `400` errors.
- Re-seeding clears ingested runtime events.
- Verification: backend `8 passed`.

## Event kind validation correction

- Updated ingestion validation so `cash_withdrawal` events may omit `to_account`, while victim payments and transfers still require it.
- Added regression coverage for accepted withdrawal events.
- Verification: backend `8 passed`.

## Case audit coverage

- Case creation, investigator-note updates, and case-status transitions now write audit records with action, target case, request ID, and outcome.
- Verification: backend `8 passed`.

## Protected-mode frontend login

- Added a login screen that appears when protected API routes return `401`.
- Access tokens persist in browser storage and are automatically attached to existing API requests; logout/revocation remains server-controlled.
- Development mode continues to open directly without configured credentials.
- Verification: backend `8 passed`; frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).
- Authenticated requests now populate the audit actor ID and role for those case actions; dev-mode actions remain explicitly attributable as local anonymous prototype actions.
- Verification: backend `8 passed`.
- Added global bearer enforcement for `demo` and `prod` modes while keeping only health and login public; development mode remains usable without credentials for local iteration.
- Verification: backend `8 passed`.

## Live event visibility

- Added `GET /api/v1/events` for recent ingested-event status.
- Live Alerts now renders a recent event stream with accepted/duplicate status and an empty state when no runtime events exist.
- Verification: backend `8 passed`; frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).
- Added a 10-second live refresh for alert counts and event-stream state, with transient poll failures retaining the last known state.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).
- Hardened the event contract to reject unknown fields, matching the strict-schema requirement.
- Verification: backend `8 passed`.

## Audit append-only hardening

- Added SQLite triggers that reject updates and deletes against `audit_log`.
- Added regression coverage proving audit records remain immutable after creation.
- Verification: backend `8 passed`.

## API validation envelope

- Added a FastAPI validation handler returning a stable `validation_error` code, request ID, and structured field errors for malformed payloads.
- Verification: backend `8 passed`.

## Bounded API pagination

- Added bounded `limit`/`offset` pagination metadata to evidence, audit, and runtime-event feeds.
- Limits are capped server-side and responses expose `next_offset` when another page is available.
- Verification: backend `8 passed`.

## Bounded network path search

- Added `GET /api/v1/network/path?source=...&target=...` using real transaction edges and breadth-first traversal.
- Traversal is cycle-safe and capped at 12 hops; missing endpoints return an explicit `found: false` result.
- Verification: backend `8 passed`.

## Network path inspection UI

- Connected the path endpoint to Fraud Network with a target selector and path result panel.
- Investigators can inspect a real directed path from the selected node and receive either the hop sequence or an explicit no-path result.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## Deterministic graph clusters

- Network responses now include stable connected-component clusters derived from live transaction edges.
- Cluster IDs are assigned from sorted traversal order; no canonical entity IDs are used in the algorithm.
- Verification: backend `8 passed`.

## Nemotron client and reasoning validator foundation

- Added configurable OpenAI-compatible Nemotron chat client with endpoint/key/model settings, timeout, retry/backoff, rate-limit/server-error handling, and graceful unavailable state when unconfigured.
- Added deterministic reasoning validator that filters fabricated evidence/entity IDs, withholds evidence-free findings, and rewrites accusatory language into hedged investigation language.
- Added regression tests for unconfigured-client behavior and validator safety checks.
- Live Nemotron connectivity and recorded reasoning fixtures remain unverified because no endpoint credentials are configured.
- Verification: backend `10 passed`.
- Added `python -m app.cli record-reasoning --case CASE-001`; it refuses without configured live credentials and only writes validated cache output after a real Nemotron response.
- Verified the refusal path with no credentials; no fabricated reasoning fixture was created.

## Enriched entity detail

- Added `GET /api/v1/entities/{entity_id}` with entity metadata, degree, inbound/outbound totals, and recent linked transactions.
- Added database coverage proving detail is derived from loaded transaction edges.
- Verification: backend `10 passed`.

## Findings and review state machine

- Added persistent findings, hypotheses, plan-step, and review-history tables with dataset-reset cleanup.
- Added finding creation/list/review APIs; evidence IDs must exist, evidence-free findings are rejected, and non-accept review states require an 8-character reason.
- Finding reviews are audit-recorded and preserve previous/new state history.
- Verification: backend `10 passed`.

## Hypotheses and action-plan review

- Added persistent hypothesis and plan-step APIs with evidence validation and linked-hypothesis checks.
- Added review endpoints for hypotheses and plan steps; accepted/done states and reason-required alternatives are preserved in review history.
- Plan steps expose `basis_rejected` when linked findings are rejected.
- Verification: backend `10 passed`.

## Weak-link promotion and demotion

- Added persisted weak/inferred links with evidence validation and cluster-forming state.
- Added `GET/POST /api/v1/links` and `POST /api/v1/links/{link_id}/promote|demote` review routes.
- Promotion requires an investigator reason and marks the link cluster-forming; demotion removes that state while preserving review history.
- Verification: backend `10 passed`.

## Held-out event simulator

- Added simulator status, reset, and step routes: `/api/v1/simulator/status`, `/reset`, and `/step`.
- The simulator replays held-out transactions through the same ingestion path, converts withdrawals to cash-withdrawal events, and exposes narrative-only complaints without fabricating transactions.
- Replayed held-out transaction IDs are marked live instead of duplicated.
- Verification: backend `10 passed`.

## Alert action workflow

- Added persisted acknowledge, dismiss, and escalate actions with dismiss-reason validation.
- Added alert action history and audit records for investigator actions.
- Verification: backend `10 passed`.

## Alert actions and simulator UI

- Connected alert detail to acknowledge, escalate, and dismiss actions with inline reason capture and visible action history.
- Added dashboard held-out replay controls for simulator reset and one-event step; successful steps refresh the alert queue and live event stream.
- Verification: frontend Vite production build passed; frontend Vitest passed (`1` test file, `1` test); backend `10 passed`.

## Case reasoning review UI

- Mounted the case workspace review panel for persisted findings, hypotheses, and action-plan steps.
- Added visible evidence references, confidence/state display, accept/reject controls for findings and hypotheses, and done/rejected-basis indicators for plan steps.
- Review changes call the existing audit-backed review endpoints and refresh the panel after each action.
- Verification: frontend Vite production build passed; frontend Vitest passed (`1` test file, `1` test).

## Event validation workflow UI

- Added a live-event submission panel beside the held-out simulator.
- Investigators can submit valid JSON, load an intentionally invalid example, see backend validation errors, and receive a visible out-of-order timestamp warning before submission.
- The panel preserves the prototype boundary: rejected or out-of-order events are review outcomes, not enforcement actions.
- Verification: frontend Vite production build passed; frontend Vitest passed (`1` test file, `1` test); backend `10 passed`.

## PRD acceptance matrix

- Added `docs/ACCEPTANCE_MATRIX.md` covering AC-01 through AC-70 with evidence-based Verified, Partially verified, and Not verified statuses.
- The matrix explicitly preserves the remaining gaps around live Nemotron access, exhaustive alert-rule sequencing, performance targets, and protected browser E2E.

## Protected-mode browser check

- Started the local backend in demo mode with temporary local test credentials and confirmed the unauthenticated dashboard endpoint returns `401`.
- Browser inspection caught and repaired a missing `Network` component reference that caused a blank UI.
- Added deterministic `?protected=1` login mode and fixed session-token propagation across reloads.
- Protected browser validation verified login, dashboard data loading, Live Alerts, Investigation Cases, Fraud Network, Evidence Explorer, and an acknowledge action with visible audit-history feedback.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test); backend `10 passed`.

## Invalid and out-of-order browser workflows

- Protected browser validation loaded the invalid-event fixture and displayed the backend rejection reason.
- Submitted a valid event followed by an older timestamp and verified the UI preserves both the out-of-order warning and the accepted result.
- Fixed the prior message-overwrite bug so an accepted out-of-order event cannot hide the warning.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test); backend `10 passed`.

## Deterministic alert rule metadata

- Alert responses now expose `rules_fired` and linked `evidence_ids`.
- Added deterministic R1 forwarding and R4 fast-cash-out detection for qualifying account flows, with R2 elevated-account signals retained.
- Alert detail now shows fired rules and evidence IDs to investigators.
- Verification: backend `10 passed`; frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## R3 cluster-merge alert coverage

- Promoted cluster-forming links now add `R3` to affected alert metadata and preserve the linked evidence IDs.
- Added a regression test covering promotion followed by R3 alert surfacing.
- Verification: backend `10 passed`.

## R6 complaint-touch alert coverage

- Alert generation now checks complaint victim references against alerted network entities and adds `R6` with an explainable reason when matched.
- Verification: backend `10 passed`.

## NVIDIA visual language

- Replaced the visible Sentry-inspired palette with the generated NVIDIA design reference.
- Applied NVIDIA black/white structure, NVIDIA green action states, angular 2px geometry, monochrome surfaces, and accessibility focus treatment across navigation, dashboard, alerts, cases, network, evidence, and login states.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## NVIDIA responsive console refinement

- Tightened dashboard hierarchy, hero sizing, panel density, navigation spacing, action controls, and review-column layout.
- Added responsive breakpoints for compact desktop, tablet, and mobile widths, including stacked controls and full-width mobile actions.
- Removed the remaining dark-purple user-chip artifact from the prior theme.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## Clean NVIDIA masthead

- Removed the visible synthetic-data disclaimer strip from the main console and login surface.
- Removed the synthetic-data mode badge from the hero area.
- Refined the FraudMesh masthead with an FM mark, product name, and compact platform label while preserving the NVIDIA green accent system.
- Verification: frontend Vite build passed; frontend Vitest passed (`1` test file, `1` test).

## Protected acceptance and investigation-surface refinement

- Added same-origin Vite proxying for local protected API calls, then completed five protected browser rehearsals.
- Measured five clean reset-and-route rehearsals: dashboard-after-reset readiness `295–334 ms`, complete Dashboard → Alerts → Cases → Network → Evidence → Audit runs `676–799 ms`.
- Added the protected interactive graph surface: normalized search, entity/link filters, cluster isolation, zoom, pan, fit, labels toggle, relationship inspector, evidence IDs, and table fallback.
- Added Audit & Access UI for append-only history and reason-gated evidence unmasking.
- Added a dedicated case timeline surface with recorded/review ordering, gap labels, selectable events, stable order hooks, and contradiction context.
- Added a protected causal-chain review surface with live path API lookup, numbered hops, ordered relationship metadata, and negative-result handling. Browser verification covered a live `ACC-M1 → ACC-M4` path and a no-path query.
- Added protected Evidence explorer filters for text, type, date range, and cited-by context, plus clickable record detail with masked source text. Browser verification opened `E-0061` successfully.
- Validated CASE-001 in protected mode: 12 timeline events, explicit gaps, selectable evidence, contradiction context, and live Recorded/Review ordering were exercised in-browser.
- Added `nemotron-smoke` to the CLI for a minimal OpenAI-compatible reachability probe. The command reads credentials from `backend/.env` without exposing them.
- Corrected the runtime configuration path: credentials were present in `backend/.env`. Live smoke succeeded against the configured Nemotron model, and CASE-001 recording completed with one validator-withheld item; the validated fixture was written to `backend/data/demo/cached_reasoning/CASE-001.json`.
- Added generic risk-profile computation and a protected dashboard inspector. The D1 runtime profile now exposes factor values, retained-funds mitigation, low band, and the investigation-priority disclaimer.
- Added AC-15 boundary coverage for 0/24/25/49/50/74/75/100, maximum-score clamping, and seeded-score determinism; backend synth tests pass 11/11.
- Made alert rule output deterministic in `R1`→`R6` order and added deduplication metadata, trigger counts, and dashboard triage status.
- Executed AC-01 through AC-70 individually; evidence is recorded in `docs/ACCEPTANCE_EXECUTION_2026-10-09.md`.
- Verification: backend `13 passed`; frontend Vite build passed; frontend Vitest `1` test file passed.

## Final acceptance completion pass

- Added case reuse/offer and escalation attachment, case subgraph and chronology APIs, grounded cached reasoning, exact P5 narrative-link matching, complaint extraction, and the X1–X4 contradiction catalog.
- Added prompt-record masking, audit-write compensation, simulator-driven graph refresh, and explicit cached-mode labeling.
- Protected browser verification exercised four contradiction candidates, cached review, persisted finding/hypothesis/plan output, alert escalation, and the full route set.
- Verification: backend `24 passed`; frontend build and Vitest passed; simulator step measured `766 ms`; reset-and-seed measured `480 ms`; identifier search measured `2.579 ms` maximum.
