# FRAUDMESH — CODEX MASTER PROMPT

**Cross-Bank Financial Crime Reconstruction & Recovery Agent**

| Field | Value |
|---|---|
| Document | FRAUDMESH_CODEX_MASTER_PROMPT.md |
| Version | 1.0 (Final implementation instruction) |
| Date | 2026-10-07 |
| Position in chain | Document 4 of 4 (Project Plan -> PRD -> Technical Documentation -> Codex Master Prompt) |
| Addressed to | OpenAI Codex (the only coding and building agent) |
| Authored by | Claude (planning, architecture and documentation role; no application code is written in this document) |
| Source documents | FRAUDMESH_PROJECT_KNOWLEDGE.md, Original FraudMesh Problem Statement.pdf, FRAUDMESH_PROJECT_PLAN.md, FRAUDMESH_PRD.md, FRAUDMESH_TECHNICAL_DOCUMENTATION.md |
| Primary AI model | NVIDIA Nemotron (endpoint, key and model name are configuration) |
| Data policy | Synthetic or authorized data only |

> **Positioning:** Normal systems see suspicious transactions. FraudMesh sees the fraud network.

---

## 0. Your Role and Mission

You are Codex. You are the **only** agent that writes, runs, tests and fixes code for this project. Your mission is to build **FraudMesh**, a working hackathon prototype that helps financial-crime investigators reconstruct fragmented fraud evidence into an explainable network, chronology, causal chain and investigation plan, with a human investigator in control.

This document tells you **how to work** and **what must be true when you finish**. The documents listed below tell you **what to build in detail**. Together they are complete; if something is still ambiguous, follow Section 3.3 (conflict and ambiguity protocol) rather than guessing silently.

**The result must be a functional prototype, not a collection of UI screens.** A feature that was not implemented and tested is not complete and must not be reported as complete.

---

## 1. Reading Order and Precedence

### 1.1 Documents and where to find them

The project folder contains:

```
FraudMesh Project/
  FRAUDMESH_PROJECT_KNOWLEDGE.md
  Original FraudMesh Problem Statement.pdf
  FRAUDMESH_PROJECT_PLAN.md          (+ .pdf)
  FRAUDMESH_PRD.md                   (+ .pdf)
  FRAUDMESH_TECHNICAL_DOCUMENTATION.md (+ .pdf)
  FRAUDMESH_CODEX_MASTER_PROMPT.md   (+ .pdf)   <- this document
```

Copy the Markdown versions into `docs/` of the repository (create it if needed) in Stage 1, so they stay available during the build. If you cannot find the documents, search the repository and its parent directory. If they are still missing, stop and report exactly which are missing; do not invent their contents.

### 1.2 Mandatory reading order (before any code change)

| Order | Document | What you take from it |
|---|---|---|
| 1 | FRAUDMESH_PROJECT_KNOWLEDGE.md | Project identity, constraints, positioning |
| 2 | Original FraudMesh Problem Statement.pdf | The original problem the product must solve |
| 3 | FRAUDMESH_PROJECT_PLAN.md | Scope, priorities (MUST, SHOULD, NICE), phases, fallback strategy |
| 4 | FRAUDMESH_PRD.md | Product requirements, feature specifications (F-xx), functional requirements (FR-xxx), acceptance criteria (AC-xx), demo specification |
| 5 | FRAUDMESH_TECHNICAL_DOCUMENTATION.md | Architecture, schemas, API contracts, prompt architecture, security design, folder structure, canonical dataset, test architecture |
| 6 | This document | Working protocol, stage gates, prohibitions, final report format |

Read each document completely. Do not skim the PRD acceptance criteria (Section 33) or the Technical Documentation canonical dataset (Section 37); they define what "done" and "correct" mean.

### 1.3 Precedence

1. Safety and honesty rules (Section 2) override everything.
2. The PRD defines product behaviour and acceptance criteria.
3. The Technical Documentation defines how to build it (names, routes, schemas, defaults).
4. The Project Plan defines scope and priority.
5. This document defines process, gates and reporting.

If two documents conflict, follow the higher item and record the conflict in `docs/DISCREPANCIES.md` (Section 3.3).

---

## 2. Non-Negotiable Rules

These rules apply for the entire build. Violating any one of them is a failure even if all tests pass.

### 2.1 Safety and ethics

1. The application never states or implies that a person or entity is guilty or criminal. Use: risk indicator, investigation priority, suspicion indicators, potential relationship, investigative hypothesis, evidence-backed finding.
2. The risk score is a **Risk Score / Investigation Priority**. It is never described as a probability of guilt. The disclaimer "Investigation priority, not an indicator of guilt." appears wherever a score is shown.
3. There is no autonomous accusation, account freezing, fund seizure, reporting to authorities or any enforcement action. Do not create buttons, routes, scripts or functions for such actions. Plan steps are suggestions a human performs outside the system.
4. A human investigator makes every decision, and every decision is audit-logged.

### 2.2 Data

5. Use **synthetic data only**. Never use, request or embed real banking credentials, real accounts, real phone numbers, real people or real financial information.
6. Do not claim or simulate integration with real banks, UPI networks, telecom operators, government systems or law enforcement. Do not build fake integrations.
7. The dataset manifest must carry `synthetic: true`; the loader and the database must refuse anything else.

### 2.3 Honesty of the build

8. **Never assume something works. Test it.** Run it, look at the output, and record the evidence.
9. **Do not fake features.** No placeholder buttons that do nothing. No screens backed by hardcoded data. No stub endpoints that return constants. No `TODO` left in delivered paths. If a feature cannot be completed, remove its control from the UI and list it under known limitations.
10. **Do not fake AI.** Nemotron integration must be a real client calling a configurable OpenAI-compatible endpoint. Mock responses are allowed **only inside automated tests** (the fake Nemotron test double) and never in application code paths served to users.
11. **Do not hardcode demo results.** The canonical dataset is deterministic, but the system must compute clusters, paths, scores, alerts, timelines and reasoning from it. No code may reference canonical IDs (such as `ACC-M6` or `PHN-P5`) to produce an expected outcome. Canonical IDs may appear only in the dataset generator, test fixtures, golden files and ground truth.
12. **Cached reasoning fixtures must come from a real, live Nemotron run** recorded through the application's own recording command (Section 4, Stage 15). You must never write cached reasoning outputs by hand.
13. **Do not weaken tests to make them pass.** Do not delete failing tests, loosen assertions without a documented reason, mark tests skipped or expected-to-fail to hide problems, or disable validation. If a test is wrong, fix it and explain why in the implementation log.
14. **Do not claim completion without verification.** The final report distinguishes Verified, Partially verified and Not verified for every acceptance criterion.

### 2.4 Secrets

15. No secret appears in source, tests, fixtures, logs, documentation or the final report. Secrets come from environment variables. `.env` is git-ignored; `.env.example` contains placeholders only. Run the secret scan in Section 9.3 before every commit.

---

## 3. Working Protocol

### 3.1 The stage loop (applies to every stage)

For each stage in Section 4:

```
1. Re-read the relevant sections of the PRD and Technical Documentation.
2. IMPLEMENT the stage's deliverables.
3. TEST: write and run automated tests for the new logic.
4. RUN: start the application (or the relevant part) for real.
5. INSPECT: look at actual outputs (API responses, logs, database rows, screens).
6. FIX: correct errors and re-run until the stage gate passes.
7. RECORD: update docs/IMPLEMENTATION_LOG.md and commit.
8. CONTINUE only when the stage gate is fully satisfied.
```

**Do not proceed while a critical previous stage is broken.** A stage gate failure blocks later stages. The only permitted exception is Stage 8 live Nemotron verification when no network access or credentials exist (Section 3.4).

### 3.2 Implementation log and commits

- Maintain `docs/IMPLEMENTATION_LOG.md`. After every stage append: stage name, what was done, files created or changed, commands run, test results (counts of passed, failed, skipped), problems found and how they were fixed, open issues.
- Commit after each stage with the message prefix `Stage N:` and a one-line summary. Keep commits small enough to review. Do not commit secrets, `data/runtime/`, `.env` or `node_modules`.
- Never rewrite history of earlier stages unless required to remove a leaked secret.

### 3.3 Conflict and ambiguity protocol

| Situation | Action |
|---|---|
| Two documents conflict | Follow the precedence in Section 1.3; log in `docs/DISCREPANCIES.md` with document names, section numbers, what you chose and why |
| A requirement is ambiguous | Choose the simplest option that satisfies the PRD acceptance criteria and the safety rules; log it |
| An expected value in the documents does not match what correct code computes | Do **not** silently change code or data to match. Verify by an independent hand or script calculation. If the documents are wrong, fix the expectation and log the correction with the calculation. If the code is wrong, fix the code |
| A scoring expectation fails (for example a risk band assertion) | Print the computed breakdown. Scoring weights and thresholds are configuration that the Plan allows to be tuned on synthetic data. You may tune values in `config/scoring.v1.json` (bump the config version and log the change and reason). You may not change the formula structure, remove factors, hardcode scores, or tune in a way that makes the decoy account (ACC-D1) rank above network accounts |
| Illustrative numbers appear in Technical Documentation examples (for example cluster sizes in sample payloads) | Treat them as illustrations only. Real values come from computation on the dataset |
| A library or tool choice fails in this environment | Use the closest equivalent that preserves the architecture; log it |
| You are tempted to cut scope | Use the cut order in Section 10; never cut a MUST item silently |

### 3.4 Nemotron access protocol

Live Nemotron access needs a reachable endpoint and credentials (`NEMOTRON_BASE_URL`, `NEMOTRON_API_KEY`, `NEMOTRON_MODEL`).

1. **If credentials and network are available:** complete live integration and verification as specified.
2. **If they are not available in your environment:** still implement the complete real client, orchestrator, validator, cache and recording command. Test everything with the fake test double. Mark every live-dependent acceptance criterion as **Not verified (no live access)** in the final report, and give the human the exact commands to run live verification and cache recording (Section 4, Stage 15, and Section 12 report template). Do **not** fabricate recorded outputs and do **not** present fake-client results as live results.
3. Never hardcode a Nemotron model name or vendor-specific behaviour. If the endpoint rejects JSON mode or other options, degrade gracefully (the validator handles unstructured output).

### 3.5 Environment assumptions

- Python 3.11 or newer and Node.js 20 or newer. Verify versions in Stage 1 and log them.
- Single machine, single backend worker, SQLite. No Docker is required; an optional Dockerfile is allowed only after all MUST items pass.
- If a browser automation tool (Playwright) can be installed, use it for frontend verification. If not, verify the frontend by building it, serving it, checking API integration with real HTTP calls, and using the structured test hooks in Section 6.4; state in the report exactly what could not be visually verified.

---

## 4. Build Stages

The sixteen stages follow your required order. Each stage lists deliverables, the documents to consult, and a **gate**: checks that must pass before moving on.

**Stage ordering note (important):** authentication, role checks, audit logging and masking are *foundations* of every API route. Build their core in **Stage 4** together with the backend API framework so that no route is ever written without them. **Stage 13** then hardens and verifies them (lockout, rate limits, security headers, audit hash chain, route self-check, masking audit, secret scan).

### 4.0 Stage-to-milestone map

| Stage | Name | Technical Documentation milestone |
|---|---|---|
| 1 | Repository inspection and setup | M0 |
| 2 | Database and data models | M1 (part) |
| 3 | Synthetic data generator | M1 (part) |
| 4 | Backend APIs (with auth, RBAC, audit and masking core) | M4, M5 (part) |
| 5 | Graph construction and relationship engine | M2 |
| 6 | Risk scoring | M3 (risk) |
| 7 | Real-time event detection | M3 (alerts), M11 |
| 8 | Nemotron integration | M8, M9 (connectivity) |
| 9 | Investigation reasoning and explainability | M9, M10 (backend) |
| 10 | Frontend dashboard | M6 |
| 11 | Interactive fraud network visualization | M7 |
| 12 | Investigation workspace | M10 (UI), M12 |
| 13 | Security, authentication and audit hardening | M4 hardening, M13 (part) |
| 14 | Testing, evaluation and performance | M13 |
| 15 | End-to-end demo validation | M14 (part) |
| 16 | UI polish and hackathon readiness | M14 |

---

### Stage 1 — Repository inspection and project setup

**Goal:** understand the starting point and create a clean, runnable skeleton.

**Tasks**

1. Inspect before changing anything: list the repository tree, read `README` and any existing configuration, run `git status` and `git log` (if a repository exists), detect existing code, languages, package files and tests. Log what you found.
2. Read the documents in the order of Section 1.2. Copy Markdown documents into `docs/`.
3. If existing code is present, decide per component whether to reuse, adapt or replace; prefer adapting code that already matches the Technical Documentation. Do not delete existing user work without logging the reason.
4. Create the folder structure of Technical Documentation Section 33 (create only directories you will use; keep it tidy).
5. Backend skeleton (FastAPI app factory, configuration loader with schema validation, structured logging with request ID, health route, error envelope, security headers middleware stub that is implemented for real in Stage 13, `cli.py`).
6. Frontend skeleton (Vite, React, TypeScript, Tailwind, router, API client, auth store shell, banner component).
7. Create `.env.example` with every variable from Technical Documentation Section 32 (placeholders only), `.gitignore`, `Makefile` (setup, seed, run, test, eval, build), and `docs/IMPLEMENTATION_LOG.md`.
8. Create `docs/DISCREPANCIES.md` (initially empty with a header).
9. Create `config/scoring.v1.json` and `config/thresholds.json` containing the PRD Section 15 and Appendix B values, and `config/language_guard.json` with the Technical Documentation Section 20.3 lists.

**Gate (all must pass)**

- Backend starts; `GET /api/v1/health` returns a valid response (dataset not loaded is acceptable now).
- Frontend dev server starts and renders the shell with the synthetic-data banner.
- Startup refuses to run in `demo` or `prod` mode with the placeholder `JWT_SECRET`.
- `pytest` runs (at least a health test and a config test pass); `npm test` runs.
- Tool versions and the repository findings are logged.

---

### Stage 2 — Database and data models

**Consult:** Technical Documentation Sections 9, 13, 14, 15, 27; PRD Section 22.

**Tasks**

1. SQLAlchemy models and session management for every table in Technical Documentation Section 13 (SQLite, WAL, foreign keys on, CHECK `synthetic = 1` on datasets).
2. Repository layer using parameterised queries only.
3. Normalisation module (phone, account, UPI, timestamp, amount) per Section 15 contract.
4. Evidence ID assignment in the deterministic order of Section 13.3.
5. Ingestion loader: manifest check, per-file schema validation, per-record validation, referential integrity checks, strict-mode unknown-field rejection, duplicate handling by content hash, ingestion report with accepted and rejected counts and reasons.
6. Entity and exact-link extraction from structured records, honouring the benign-identifier allow-list; confirmation module skeleton for T1 identifiers (completed in Stage 9).
7. `reset` operation (clears data tables in one transaction and records an audit entry later when audit exists).

**Gate**

- Unit tests cover: each normaliser with format variants (for example the same phone written as `+91 90000 00105`, `0091-90000-00105`, `090000-00105`, `90000 00105`), invalid inputs rejected, amount to paise conversion, timestamp parsing and UTC conversion, evidence ID determinism (load twice, identical IDs), duplicate idempotency, manifest refusal when `synthetic` is not true, malformed records rejected while others load.
- A hand-made small fixture loads end to end into a temporary database with expected row counts.
- PRD AC-01, AC-02, AC-04, AC-05, AC-06 are covered by passing tests.

---

### Stage 3 — Synthetic data generator

**Consult:** Technical Documentation Section 37 (the canonical dataset is binding), PRD Section 23.

**Tasks**

1. Implement the seeded generator producing the full dataset package (all files in Section 37.1) for seed `S1` and base date `2026-09-01`: 8 investigated accounts, victim source accounts, external accounts, 20 victims, 6 phones, 5 devices, 56 transactions exactly as tabulated in Section 37.4, 13 complaints, 9 communications, 9 device logs, flags, benign identifiers, held-out events, and the separate ground-truth file.
2. Complaint narratives: 80 to 250 words, first person, informal, neutral, non-graphic, containing the embedded facts, traps and the harmless injection sentence exactly as specified in Section 37.5. Store the generated canonical narratives in `data/demo/complaints.json` and commit them; tests must not depend on regenerating them.
3. Implement `reset-and-seed` in `cli.py`: reset, load dataset, create demo users from environment variables (`DEMO_*_PASSWORD`, minimum 12 characters; no passwords in the repository), build initial state.
4. Generator safety: only synthetic patterns (phones `+91 90000 001NN`, account prefixes `9900`, `9800`, `9700`, fictional bank names); output a generation report.

**Gate**

- Running the generator twice with the same seed produces byte-identical output (test compares hashes).
- Counts match Section 23.2 of the PRD and Section 37 of the Technical Documentation (verify by script, not by eye): 20 victims, 56 transactions, 8 investigated accounts, 6 phones, 13 complaints, 9 communications, 9 device logs, 5 devices.
- **Independent arithmetic check:** write a small verification script that recomputes from the generated files (a) the sum of T-001 to T-020 (expected 913,000 INR), (b) each forward gap and ratio in the layer tables, (c) the pass-through event list in Section 37.6. Any mismatch with the documents is logged in `docs/DISCREPANCIES.md` and resolved per Section 3.3.
- `reset-and-seed` completes in under 60 seconds and leaves a loaded database. The ground-truth file exists and is **not** copied into any directory the application reads.
- PRD AC-01, AC-03, AC-70 covered.

---

### Stage 4 — Backend APIs (with authentication, RBAC, audit and masking core)

**Consult:** Technical Documentation Sections 4, 10, 12, 23 to 28, 35, 36; PRD Sections 26 to 30.

**Tasks**

1. API conventions: `/api/v1` base, error envelope, pagination, request ID, Pydantic schemas with `extra=forbid`, provenance block helper.
2. Authentication: argon2id hashing, JWT HS256 with `jti`, expiry, revocation on logout, lockout counters, generic login errors.
3. Authorization: `require_role` dependency on every route; startup self-check test that fails if a route lacks a declared role set.
4. Audit writer (same-transaction write, failure aborts the action) and the audit event catalogue (Section 26.2). Hash chaining may be added in Stage 13.
5. Masking module (Section 23.2) applied in one central serialisation layer, log formatter and (later) prompt builder; unmask endpoint with required reason and audit event.
6. Implement now: `auth/*`, `health`, `meta/limitations`, `datasets/*`, `settings/mode`, `dashboard/summary` (initially data-driven from what exists), `evidence` (list, detail, unmask), `entities`, `search` (normalising query, prefix matching, 4-character minimum), `audit`, `users` (list). Routes for graph, risk, cases, reasoning, findings, plan, alerts, events and simulator are added in their own stages.
7. Limitations content endpoint rendering the Section 23 control table including "Not implemented" rows.

**Gate**

- API tests: protected routes return 401 without a token; Admin-only routes return 403 for an Investigator; login errors are generic; five failed logins lock the account for the configured time; expired and revoked tokens are rejected; validation errors return the envelope; pagination limits enforced.
- Masking test: no raw phone, account number or UPI appears in any API response or log line by default; unmask requires a reason and writes an audit record.
- Audit test: every action in the catalogue implemented so far writes a record; no route can update or delete audit rows; a simulated audit write failure aborts the action.
- Search test: the same phone typed in different formats finds the same entity.
- Run the server for real, log in with `curl` using the demo user, and capture sample responses in the log.
- PRD AC-44, AC-45, AC-55 to AC-60, AC-62 to AC-64 covered (those relevant so far).

---

### Stage 5 — Graph construction and relationship engine

**Consult:** Technical Documentation Sections 8, 14, 15, 16; PRD Section 24.

**Tasks**

1. Build the in-memory MultiDiGraph from the database (nodes keyed by normalised identifier, edges with strength, evidence IDs, timestamps and amounts).
2. Link strengths and cluster-forming rule exactly as in Section 14.3. Benign allow-list produces no links. Weak and unconfirmed links never form clusters.
3. Cluster computation with stable IDs (`CL-n`), cross-case flag, persistence of membership and versions.
4. Time-ordered money-flow path search with cycle safety and `PATH_MAX_HOPS`.
5. Shared-identifier detection, fan-in and fan-out, transaction aggregation helpers, pass-through detection per the definition in Section 18.5 (cumulative outbound allocated chronologically), betweenness centrality.
6. Case subgraph extraction with hop and node caps and a truncation notice.
7. Incremental update function and a rebuild-equivalence test (incremental result equals full rebuild).
8. Routes: `GET /graph`, `GET /graph/clusters`, `GET /graph/paths`, `POST /links/{id}/promote`, `POST /links/{id}/demote`, `GET /entities/{id}` enrichment. Link promote and demote recompute clusters and write audit records.

**Gate**

- On the canonical dataset (after Stage 3), tests assert the graph expectations of Technical Documentation Section 37.6: one cross-case cluster containing the network accounts, victims, phones P1 to P4, devices DEV-1 to DEV-4 and incidents; ACC-D1, DEV-5, the helpline identifier and the coincidence-pair accounts excluded; PHN-P6 present only as weak (excluded); PHN-P5 present with no link before T1 confirmation; DEV-1 linking M1, M2 and M7; DEV-2 linking M3 and M4.
- Money-flow path from victim V02 to the cash-out withdrawal returns the expected hop sequence with gap minutes.
- Tests: weak and unconfirmed links do not merge clusters; allow-list identifier creates no edge; cycle input terminates; incremental equals rebuild; deterministic output across runs.
- Graph build completes in under 5 seconds (measure and log).
- Call the live endpoints with `curl` and inspect the JSON.
- PRD AC-07 to AC-11 covered.

---

### Stage 6 — Risk scoring

**Consult:** PRD Section 15; Technical Documentation Section 18.

**Tasks**

1. Feature extractor, one pure function per factor, aggregator, explainer, storage (`risk_scores`), config versioning, recompute-on-affected-set logic.
2. Implement all nine factors and the mitigation factor with the exact point tables of PRD Section 15.2, the formula `clamp(round(raw * 100 / 110) + mitigation, 0, 100)` and the bands.
3. Breakdown JSON with values used, evidence IDs and the disclaimer. Scoreable entity types as in the PRD (accounts full; phones, devices and UPI subset).
4. Route `GET /risk/{entity_id}`; dashboard summary now uses real scores.

**Gate**

- Boundary tests for every factor threshold (each threshold value and the value just below it).
- Determinism test: two computations give identical scores and breakdowns.
- On the canonical dataset: the R1-definition pass-through counts of Section 37.6 are reproduced exactly; ACC-D1 scores below every network account and shows mitigation; network accounts reach at least the bands stated in Section 37.6. If a band expectation fails, follow Section 3.3 (print breakdowns, tune configuration only, log it).
- Freeze computed breakdowns into `tests/golden/risk_breakdowns.json` after a human-readable review of the numbers recorded in the log.
- PRD AC-12 to AC-16 covered.

---

### Stage 7 — Real-time event detection

**Consult:** Technical Documentation Sections 5, 17, 19; PRD Sections 17, 18.

**Tasks**

1. The pipeline: validate, persist and normalise, extract features, update graph (under the graph lock), recompute risk for the affected set, evaluate alert rules R1 to R6 with deduplication, publish `state_version`, optional non-blocking reasoning enqueue (hook completed in Stage 9).
2. Idempotency by `event_id`; invalid events rejected with audit entries.
3. Alert store, alert detail "why this fired" data (rule values and evidence IDs), actions (acknowledge, dismiss with reason, escalate; escalate creates or attaches a case once Stage 9 cases exist, so implement the case service minimally here if needed).
4. Simulator: queue from `events_heldout.json`, controls play, pause, step, reset, inject; same `Pipeline.process` function as `POST /events`.
5. Routes: `POST /events`, `POST /simulator/{action}`, `GET /alerts`, `GET /alerts/{id}`, `POST /alerts/{id}/action`.

**Gate**

- Replay the seven held-out events through the real pipeline in a test and assert the alert sequence in Section 37.6 (T-020 raises R2 Critical; T-026, T-035, T-038 raise R1; T-044 and T-045 raise R4; complaint C-13 raises R6), and that scores update. If an assertion fails, follow Section 3.3.
- A unit test with a small purpose-built fixture proves rule R3 (cluster merge) fires, since the canonical sequence does not trigger it.
- Duplicate event is a no-op; invalid event rejected; out-of-order timestamp handled.
- Event-to-alert latency for steps 1 to 6 is under 3 seconds (measure over several events and log).
- Run the server, inject events via `curl` or the simulator route, and inspect alerts.
- PRD AC-36 to AC-41 covered (UI parts later).

---

### Stage 8 — Nemotron integration

**Consult:** Technical Documentation Sections 7, 21, 22; PRD Section 25.

**Tasks**

1. Real Nemotron client: OpenAI-compatible chat completions via `httpx`, configuration from environment, timeouts, retries with backoff, 429 handling, concurrency semaphore, circuit breaker, masked request and response logging, key redaction.
2. Context builder: evidence digest lines, software facts, allowed ID lists, numeric fact set, token budget with overflow policy, narrative truncation, delimiter escaping.
3. Prompt templates as versioned files (`system.v1.txt`, `t1.v1.txt` ... `t9.v1.txt`) following Section 22 exactly (system rules, data blocks, allowed IDs, schema, reminders).
4. Output schemas for T1 to T9 (Pydantic models) per Section 21.4.
5. Job runner (thread pool, task DAG per Section 7), job persistence, cache layer (keys and staleness rules per Section 21.6), mode switching.
6. Fake Nemotron test double with the fixture set listed in Section 29.2 (valid per task, invalid IDs, invalid numbers, accusatory text, malformed text, timeout, rate limit, injection-followed output).
7. `GET /health` reports Nemotron configured and reachable (probe cached for 30 seconds).
8. Connectivity smoke command (`cli` command) that makes one minimal real call and prints status, latency and a short success or failure message without printing secrets.

**Gate**

- Orchestrator tests with the fake client: valid output accepted; malformed output triggers one repair attempt then fails gracefully; timeout and 429 paths produce `unavailable`; circuit breaker opens after three consecutive failures and closes after the cooldown; cache hit and miss behaviour correct.
- Prompt tests: allowed-ID list always present; narrative containing the delimiter strings is escaped; no raw identifiers outside the documented T1 exception (assert by scanning built prompts for unmasked phone and account patterns in non-T1 prompts).
- **If live access exists:** run the connectivity smoke command and one real T1 call on a canonical complaint; log latency and validity. **If not:** record "live access unavailable" per Section 3.4 and continue.
- PRD AC-61, AC-65 covered with mocks.

---

### Stage 9 — Investigation reasoning and explainability

**Consult:** Technical Documentation Sections 6, 7, 16, 20, 21, 22; PRD Sections 16, 19, 20, 25.

**Tasks**

1. Case service (create from cluster, alert or entities; snapshot; refresh; notes; status; closure with note and label), case routes, duplicate-seed conflict handling.
2. Chronology service: software-ordered timeline, gap computation, stable secondary sort, unplaced lane, phase data; conflict candidate generator with the four rule families (amount, time, bank, identifier-form) using the configured tolerances.
3. Confirmation step for T1 results: normalise extracted identifiers, exact-match against entities, apply the role-based strength rule (callback, caller and agent roles give `inferred_confirmed`; victim contact and unknown roles give `weak`), create links, trigger cluster and risk recomputation. Nemotron can never create an `exact` link.
4. Validator and language guard exactly as in Section 20.2 and 20.3, including canonicalisation of ID variants, numeric consistency, entity existence, T5 chain-to-edge mapping, rewrite or withhold behaviour and withheld counts.
5. Findings store, citation index, plan steps, contradictions store, review state machines, review routes with reasons, dependent-step flagging ("basis rejected").
6. Run-reasoning route (`POST /cases/{id}/reasoning`), job status route, findings, plan, contradictions and timeline routes, live and cached modes, "possibly out of date" detection via input hash.
7. `record-reasoning` CLI command: runs the full live reasoning on a given case and saves validated outputs into the cache and into `data/demo/cached_reasoning/` as fixtures, printing a summary. It refuses to run in cached mode.

**Gate**

- Validator tests (all must pass): fabricated evidence ID dropped; finding with no evidence dropped; evidence ID alias `E12` canonicalised only if it exists; numeric mismatch dropped; nonexistent entity dropped; accusatory phrasing rewritten or withheld; T5 movement step without a matching edge marked or dropped; injected-instruction output (from the fake double) does not alter results and is flagged.
- T1 confirmation tests using fixture outputs: callback-role mention of P5 in C-05, C-09, C-10 (as `090000-00105`) and C-13 yields `inferred_confirmed` links and P5 joins the cluster; P6 mentions with victim-contact role stay weak; the helpline never links.
- Timeline test: events ordered correctly; gaps correct; conflict candidates X1 to X4 generated deterministically from the canonical data.
- End-to-end with the fake client: create case, run reasoning, receive validated findings with provenance, plan and contradictions; review a finding with a reason; dependent step flagged; audit entries written.
- **If live access exists:** run the full reasoning on the canonical case live. Inspect the outputs yourself: every cited ID must exist, stages and chain must correspond to real transfers, language must be hedged. Log any model weaknesses you observe and tune prompts (bumping the prompt version) rather than loosening the validator.
- PRD AC-17 to AC-19, AC-42, AC-43, AC-46 to AC-54 covered (live ones only if verified live).

---

### Stage 10 — Frontend dashboard

**Consult:** Technical Documentation Sections 11.1 to 11.4; PRD Sections 10, 18, 20, 27.

**Tasks**

1. Design system implementation (Section 6 of this document and Technical Documentation 11.2): tokens, typography with bundled fonts (no CDN), badges for risk band, link strength and source type, drawers, tables, empty states, toasts, banner.
2. Screens: Login, Dashboard (KPI tiles, alert feed with polling, priority list, cases table, daily value chart, simulator strip), Live alerts (list, detail drawer, actions), Investigation cases (list, create, filters), Settings and security (user, session, mode toggle, config summary, links), Limitations.
3. Auth guard, token handling in `sessionStorage`, 401 handling with redirect preserving target route, role-aware navigation.
4. Polling on `state_version` every 2 seconds with backoff.

**Gate**

- Frontend builds without errors or type errors; unit tests for badges, API client error mapping and filters pass.
- Real integration: run backend and frontend, log in through the UI (browser automation if available), see real dashboard numbers equal to values from the API, trigger the simulator inject control and watch the alert appear.
- Every visible control performs a real action. List all controls on each screen in the log with the action they trigger; remove any that do nothing.
- PRD AC-30, AC-31, AC-40, AC-41 covered (UI parts).

---

### Stage 11 — Interactive fraud network visualization

**Consult:** Technical Documentation Section 11.5; PRD Section 12.

**Tasks**

1. Cytoscape.js wrapper with fcose layout, node and edge styling per the tables in Section 11.5 (shapes, colours, sizes, link-strength styles, risk borders, cluster overlay, cross-case badge).
2. Interactions: zoom, pan, fit, search with format-insensitive focus, filters (entity type, link strength, cluster; SHOULD: risk band, time window, amount range), node and edge inspector, transaction details, evidence ID links opening the evidence drawer, cluster isolation and restore, fraud-chain highlighting with numbered steps (from `/graph/paths` and from the T5 result), legend, labels toggle, table-view fallback with automatic switch on render error, summary nodes above 300 nodes, new-node animation.
3. Timeline component (SVG): lanes, events, gap labels, conflict markers, phase bands, software versus reconstructed toggle, click-through synchronisation with the graph in both directions.
4. Test hooks (Section 6.4) so automated tests can verify the graph actually rendered the expected nodes.

**Gate**

- With the canonical dataset loaded, the network view renders the cluster with the expected node and edge counts (read from the test hooks, compared with the API response).
- Each interaction is verified (browser automation preferred): zoom and pan change the viewport; search for the callback number written as `0091-90000-00105` focuses the P5 node (after confirmation) or reports not found before confirmation; filters hide and show the correct element counts; clicking a node and an edge opens the inspector with evidence IDs; isolating a cluster hides non-members; chain highlighting numbers steps in time order; table fallback works when the graph is forced to fail.
- Timeline order and gaps equal the API values; clicking an event focuses the graph.
- PRD AC-20 to AC-26, AC-29 covered.

---

### Stage 12 — Investigation workspace

**Consult:** Technical Documentation Sections 11.4.5 to 11.4.10; PRD Sections 11, 13, 14, 16, 19, 20.

**Tasks**

1. Case detail with tabs: Summary, Network, Timeline, Evidence, Findings, Plan, Contradictions, Notes, History, Report; header with status, band, reasoning state, live and cached toggle, Run reasoning with per-task progress, "possibly out of date" banner, refresh subgraph, close with note and label.
2. Findings panel in the standard format (Finding, Evidence, Reasoning, Confidence, counter-evidence, Next step, source tag, provenance, review state) with evidence IDs that open details and highlight graph elements; review controls with required reasons; withheld count message; no bulk accept.
3. Plan tab with review states and "basis rejected" flags; Contradictions tab with side-by-side sources and assessments; Evidence explorer (list, filters, detail with raw text block, interpretation tab with T1 claims and confirmation status, "cited by", reveal with reason); Risk explanation drawer and page; AI investigation report tab composed only from validated, non-rejected items with print stylesheet; Audit view for Admin; History tab.
4. Language: audit all UI text against the required and prohibited vocabulary (PRD Appendix D).

**Gate**

- Using the fake Nemotron client in an integration environment (and live if available), run reasoning from the UI and inspect: progress updates, findings with evidence, review actions persist, audit entries appear in the Admin audit view.
- Every control wired (repeat the control inventory).
- A text-review script scans frontend and backend strings for prohibited terms and fails on any assertion about a specific entity.
- PRD AC-27, AC-28, AC-32 to AC-35, AC-42, AC-43, AC-54, AC-66, AC-67 covered.

---

### Stage 13 — Security, authentication and audit hardening

**Consult:** Technical Documentation Sections 23 to 28; PRD Sections 27 to 30.

**Tasks and checks**

1. Security headers (CSP, nosniff, frame deny, referrer policy, no-store on API); CORS allow-list; rate limiting on login and reasoning creation; lockout verified.
2. Audit hash chain (SHOULD) with a verification command; confirm no update or delete paths; confirm audit failure aborts actions.
3. Route self-check test covers every route; RBAC matrix test covers every row of Technical Documentation Section 25.1 for both roles.
4. Masking audit: scan API responses for all entity types, logs and prompts for unmasked identifiers; verify unmask reasons and audit.
5. Secrets: run the secret scan (Section 9.3); confirm no default passwords or keys in the repository; confirm startup checks in `demo` and `prod` modes.
6. Prompt-injection tests with C-07 and additional adversarial strings; evidence rendering as text only (no HTML injection) verified with a test narrative containing markup.
7. Dependency review: pinned lockfiles; remove unused dependencies.

**Gate**

- All security tests pass; the secret scan reports nothing; the Limitations page matches reality (every "Implemented" row is true and tested; every "Not implemented" row is stated).
- PRD AC-55 to AC-64, AC-47, AC-58 covered.

---

### Stage 14 — Testing, evaluation and performance

**Consult:** PRD Sections 31 to 33; Technical Documentation Section 29.

**Tasks**

1. Complete the test suites listed in Technical Documentation Section 29 (unit, integration, API, graph, risk, AI validation, frontend unit, end-to-end).
2. Evaluation harness (`python -m eval.run`): compare system output with `ground_truth.json` and print the metrics of PRD Section 33.3 (entity recall, link recall, exact-link precision, inferred-link precision, cluster coverage and purity, decoy rejection, chain accuracy, chronology accuracy, contradiction recall, evidence-ID validity, invented evidence shown, complaint extraction accuracy, score reproducibility, latency). Live-dependent metrics are computed only from real runs.
3. Performance measurements for PERF-01 to PERF-12 on this machine; record the numbers.
4. Coverage report for backend (target: critical modules graph, risk, explain, ingest, auth above 85 percent line coverage; do not game coverage).

**Gate**

- `pytest -m "not live"` passes completely (no skipped tests without a documented reason); frontend tests pass; evaluation report generated and saved to `docs/evaluation_report.md` with honest notes on failures and caveats.
- Performance table recorded; any target missed is reported, not hidden.

---

### Stage 15 — End-to-end demo validation

**Consult:** PRD Appendix A; Technical Documentation Section 38.

**Tasks**

1. Reset to a clean state with `reset-and-seed`. Run the entire demo script (Section 8 of this document) against the real running application, step by step, using browser automation where available.
2. **Record live reasoning (if Nemotron access exists):** run `record-reasoning` on the demo case; inspect and validate the saved outputs; confirm cached mode reproduces them with the "Cached (not live)" label. **If access does not exist:** do not create fixtures; state in the report that cached mode is implemented but has no recorded fixtures, and give the human the exact command sequence.
3. Failure drills (Section 9.5): induce each failure once and confirm graceful degradation and honest labelling.
4. Run the full demo at least five times from a clean start (automation or scripted API plus UI checks), recording pass or fail and any flakiness.

**Gate**

- Demo script passes end to end in at least five of five clean runs (or the report states precisely which steps could not be automated and how they were checked).
- Failure drills pass.
- PRD AC-36 to AC-39, AC-65, AC-66, AC-69, AC-70 covered.

---

### Stage 16 — UI polish and hackathon presentation readiness

**Tasks**

1. UI polish within the principles in Section 6: spacing, hierarchy, empty states, loading states, error states, consistent badges, readable evidence, keyboard focus, contrast. No gratuitous animation.
2. Write `docs/runbook.md` (start, reset, demo order, recovery steps for each failure, credentials source), `docs/limitations.md` (mirrors the Limitations page) and a root `README.md` (what it is, how to run, how to demo, architecture overview, safety statement).
3. Capture screenshots for key screens if a browser tool is available (dashboard, network, timeline, findings, risk breakdown, audit) into `docs/screenshots/`.
4. Final full regression: all tests, evaluation, demo script, secret scan.
5. Produce the final implementation report (Section 12).

**Gate**

- All final acceptance criteria in Section 11 are checked with evidence; the report is complete and honest.

---

## 5. Critical Invariants (Check These Repeatedly)

| # | Invariant | Where verified |
|---|---|---|
| I1 | Deterministic code does exact matching, aggregation, sorting, graph build, scoring and alert rules; Nemotron does interpretation and reasoning only | Code review, tests |
| I2 | Nemotron never creates an `exact` link; model-proposed links become cluster-forming only after exact confirmation with an allowed role or investigator promotion | Stage 9 tests |
| I3 | Every AI item shown to users has at least one valid evidence ID, required fields, hedged language, provenance and source tag; invalid items are withheld and counted | Validator tests |
| I4 | The model never computes amounts, counts, gaps or scores; software facts are supplied and verified | Validator numeric test |
| I5 | Evidence IDs are assigned only by ingestion in the documented order | Determinism test |
| I6 | Weak and unconfirmed links never merge clusters | Graph tests |
| I7 | Risk score is reproducible and fully explained; the disclaimer is attached | Risk tests |
| I8 | Alerts fire from deterministic rules without waiting for Nemotron | Pipeline test with Nemotron down |
| I9 | Identifiers are masked in API, UI, logs and prompts except the documented T1 exception and logged reveals | Masking audit |
| I10 | Every state-changing action and security event is audited in the same transaction | Audit tests |
| I11 | No endpoint or control performs freezing, seizing, blocking or reporting | Route inventory test |
| I12 | The ground-truth file is never read by the application | Test and file-access review |
| I13 | Cached outputs are labelled "Cached (not live)" and are produced only from real recorded runs | UI test, fixture provenance |
| I14 | The application refuses datasets not flagged synthetic | Ingestion and DB tests |
| I15 | Recorded timestamps are never altered by reasoning; reconstructed order is displayed separately | Timeline tests |

---

## 6. Interface Principles

### 6.1 Intent

The application must feel like a **professional cybersecurity and financial-intelligence investigation platform**, not a generic AI dashboard or marketing page. Investigation-first workflow, clear hierarchy, readable evidence, an interactive network graph, a timeline, risk indicators, an AI reasoning panel with evidence links, and live alerts.

### 6.2 Visual direction

- Dark neutral theme by default with layered surfaces and subtle borders; restrained teal accent; risk colours (neutral, amber, orange, red) always paired with text labels.
- Minimal, breathable layouts: generous spacing, one clear focus per screen, no clutter. Premium and calm rather than flashy.
- Typography: bundled Inter (no CDN), tabular numerals for amounts and times, monospace for IDs.
- Avoid excessive animation and decorative effects. Permitted motion: short transitions, new-node animation in the graph, chain highlight.
- Persistent banner: "Synthetic data. Investigation-support prototype. Not for enforcement decisions."

### 6.3 UI rules

1. Every control must be wired to real behaviour. No dead buttons, no placeholder pages in navigation.
2. Every number on the dashboard leads somewhere meaningful.
3. Every AI-derived element shows its source tag (Deterministic, Graph, Nemotron-live, Nemotron-cached), confidence, and an evidence list reachable in one click.
4. Loading, empty and error states exist for every data view.
5. The UI never shows an accusation. Use role tags such as "reported as caller" and "pass-through pattern indicator".
6. Labels: "Risk Score", "Investigation Priority", "Suspicion Indicators" (the factor list); the disclaimer is always visible with scores.
7. Layouts target desktop Chrome and Edge at 1440 by 900 and above.

### 6.4 Test hooks (so claims can be verified)

Expose stable `data-testid` attributes on key controls and regions. For the graph, expose in the DOM (for example on the container as data attributes) the current node count, edge count, selected element ID, visible cluster ID and highlight chain length. For the timeline, expose event count and order IDs. These hooks must be harmless in production and must not alter behaviour.

---

## 7. Coding Principles

1. Keep the architecture understandable; follow the Technical Documentation folder structure and module responsibilities.
2. Prefer reliability over cleverness. Do not over-engineer. No microservices, brokers or graph databases.
3. Keep modules small and pure where possible; domain modules (`graph`, `risk`, `chronology`, `explain`) are unit-testable without HTTP.
4. Validate all external input (HTTP, files, events, model output) at the boundary.
5. Use parameterised queries only. No string-built SQL.
6. Handle errors explicitly; no silent exception swallowing; use the error envelope and structured logs with request IDs.
7. Write useful logs: pipeline timings, graph rebuilds, risk recomputations, reasoning calls (masked), validator outcomes, breaker state. Never log secrets or unmasked identifiers.
8. Configuration in files and environment, not scattered constants. Thresholds and weights live in `config/`.
9. Comment intent where logic is non-obvious (for example the pass-through allocation rule), keep code readable, keep functions short.
10. Add tests for every important behaviour as you build it, not at the end.
11. Pin dependencies; keep the dependency list minimal.

---

## 8. Demo Validation Script (Stage 15)

Run against the real application after `reset-and-seed` with seed `S1`. Record Pass or Fail and evidence (response excerpt, screenshot or hook value) for each step.

| Step | Action | Expected observation |
|---|---|---|
| 1 | Log in as the demo Investigator | Dashboard loads in under 2 seconds; banner visible |
| 2 | Review dashboard | Four incidents (INC-A to INC-D), initial alerts, a priority list in which the decoy account is not near the top |
| 3 | Inject the next held-out event (T-020) | R2 Critical alert appears within 3 seconds with explanation and evidence IDs; the recipient account's score changes |
| 4 | Open the alert | "Why this fired" shows rule, actual values, evidence IDs |
| 5 | Open the risk breakdown for the recipient account | Factor bars, values, evidence IDs, disclaimer |
| 6 | Open the network view | New edge present; cross-case cluster visible with badge; related victims, accounts, phones, devices visible |
| 7 | Isolate the cluster; search the callback number written as `0091-90000-00105` | Before reasoning: not found as a linked node (or isolated without cluster link); after reasoning confirmation: focuses the P5 node |
| 8 | Create a case from the cluster | Case workspace with subgraph, evidence set, timeline |
| 9 | Open the timeline | Ordered events, gap labels in minutes, conflict markers for X1 to X4 |
| 10 | Open evidence for complaint C-07 | Raw text shown as plain text; injection sentence visible as text and not obeyed |
| 11 | Run reasoning | Per-task progress; completion; withheld count shown if any |
| 12 | View the causal chain; highlight it in the graph | Five stages with evidence and gaps; numbered chain on real edges |
| 13 | View the narrative-only link to P5 | Inferred and confirmed badge with evidence IDs from C-05, C-09, C-10 and C-13 |
| 14 | Open Contradictions | X1 to X4 listed with assessments (live or cached) |
| 15 | Read the plan; accept two steps; reject one finding with a reason | States saved; dependent step flagged "basis rejected" |
| 16 | Switch to cached mode and re-run | Results labelled "Cached (not live)" (only if fixtures were recorded) |
| 17 | Log in as Admin; open the audit log | Entries for login, case creation, reasoning, review, mode change |
| 18 | Open the Limitations page | Implemented and not-implemented controls listed truthfully |

---

## 9. Verification Practices

### 9.1 What counts as verification

A claim of "works" requires at least one of: an automated test that ran and passed, a real HTTP call whose output you inspected, a browser interaction (automation or hook values), or database inspection. "The code looks right" is not verification.

### 9.2 Commands you should expect to use

```
# Setup and data
make setup
python -m app.synth.generate --seed S1 --out ../data/demo
python -m app.cli reset-and-seed --dataset ../data/demo
python -m app.cli nemotron-smoke
python -m app.cli record-reasoning --case CASE-001

# Run
uvicorn app.main:app --port 8000
npm run dev          # frontend

# Test and evaluate
pytest -m "not live" --maxfail=1
pytest -m live
npm test
python -m eval.run
```

Adjust paths to the repository layout you created; log the final command set.

### 9.3 Secret scan (run before every commit and at the end)

Search the repository (excluding `node_modules`, `.venv`, `data/runtime`) for: the literal values of any configured key, strings matching `api_key`, `secret`, `password`, `token` followed by an assignment of a non-placeholder value, and long random-looking strings. Confirm `.env` is ignored by git. The scan must report nothing; log the command and result.

### 9.4 Route and control inventories

Maintain a generated route inventory (method, path, role set) and a UI control inventory (screen, control, action, endpoint). Include both in the final report. Any route without a role declaration or control without an action is a defect.

### 9.5 Failure drills (Stage 15)

| Drill | How to induce | Expected result |
|---|---|---|
| Nemotron unreachable | Point `NEMOTRON_BASE_URL` at an unreachable host | Alerts still fire; reasoning shows "unavailable"; cached mode offered; non-AI features work |
| Invalid JSON from model | Fake double returning malformed text (test environment) | One repair attempt; then "could not be validated"; no crash |
| Fabricated evidence ID | Fake double | Statement withheld; count shown; no invented ID in UI |
| Accusatory output | Fake double | Rewritten or withheld |
| 429 rate limit | Fake double | Cached fallback or clear message |
| Graph render failure | Force an exception in the graph wrapper | Table view with the same data |
| Missing database | Remove the database file | Clear startup message; `reset-and-seed` restores |
| Audit failure | Force a write failure in test | The action fails with a clear message |
| Expired token | Wait or shorten expiry in test | Redirect to login preserving target |
| Non-synthetic dataset | Load a manifest with `synthetic: false` | Refused |

---

## 10. Scope Control and Cut Order

Priority follows the Project Plan. Complete all MUST items before any SHOULD item, and all SHOULD items before NICE items.

If time is short, cut in this order (cut from the top first):

1. NICE TO HAVE items (case export, counterfactual check, community detection, role extras).
2. Advanced graph analytics beyond degree and betweenness.
3. Audit view polish and evidence explorer extras (keep audit recording and evidence detail).
4. Contradictions UI (keep deterministic candidate generation and the timeline markers).
5. Continuous simulator playback (keep the single "inject next event" control).
6. Time slider and risk-based node sizing.

**Never cut:** synthetic data, evidence IDs, graph, risk explanation, timeline, Nemotron causal reconstruction with validation, authentication, audit logging, masking, the end-to-end demo, the Limitations page, and graceful degradation. If something is cut, remove its controls and list it under known limitations; do not leave it half-built.

---

## 11. Final Acceptance Checklist

The project is **not complete** until each item is checked with evidence recorded in the implementation report.

| # | Requirement | Evidence required |
|---|---|---|
| 1 | Frontend runs | Build output and a running session |
| 2 | Backend runs | Server log and health response |
| 3 | Database works | Row counts after seed; schema created |
| 4 | Synthetic data loads | Ingestion report matching the canonical counts |
| 5 | Graph works | Cluster and path assertions passing; network view rendering |
| 6 | Risk scoring works | Breakdowns, determinism and golden test |
| 7 | Real-time detection works | Held-out replay alerts and latency numbers |
| 8 | Nemotron integration works | Live smoke and live reasoning results, or an explicit "Not verified (no live access)" with the human run commands |
| 9 | Explainability works | Findings in the standard format with provenance |
| 10 | Evidence references work | Validator tests; clickable IDs; zero invented IDs shown |
| 11 | Authentication works | Login, lockout, expiry, revocation tests |
| 12 | Authorization works | RBAC matrix test |
| 13 | Audit logging works | Audit tests and the Admin view |
| 14 | Masking works | Masking audit |
| 15 | Tests pass | Test run summary with counts |
| 16 | Complete demo flow works | Section 8 results table |
| 17 | Evaluation report produced | `docs/evaluation_report.md` |
| 18 | Safety language verified | Text-review script result |
| 19 | No secrets in the repository | Secret scan result |
| 20 | Failure drills passed | Drill results |

---

## 12. Final Implementation Report (required output)

When all stages are complete (or when you must stop), produce a **concise** report at `docs/IMPLEMENTATION_REPORT.md` and print a summary in your final message. It must contain these sections in this order:

1. **What was built:** a short description and a feature list mapped to MUST, SHOULD and NICE items, each marked Implemented, Partially implemented or Not implemented.
2. **Architecture used:** a brief diagram or description matching the Technical Documentation, and any deviations with reasons (link to `docs/DISCREPANCIES.md`).
3. **Files created and modified:** grouped by directory (not an exhaustive dump if very long; list directories and key files).
4. **Commands used:** setup, seed, run, test, evaluate, record.
5. **Tests executed:** suites run with counts of passed, failed and skipped, plus the coverage figures.
6. **Test results:** the outcome and any failing items with explanations.
7. **Evaluation metrics:** the table from the evaluation run with honest notes.
8. **Performance measurements:** PERF-01 to PERF-12 results.
9. **Environment variables required:** the table (names and meanings only, no values).
10. **How to run locally:** exact steps from a clean clone.
11. **How to run the demo:** exact steps including reset, login, and the order from Section 8; plus the cached-mode procedure.
12. **Acceptance verification matrix:** every PRD acceptance criterion (AC-01 to AC-70) with status Verified, Partially verified or Not verified, and the evidence (test name, command, hook value or log line).
13. **Route inventory and UI control inventory.**
14. **Known limitations:** including security controls not implemented, scale limits, model behaviour caveats, anything cut, and anything Not verified (for example live Nemotron access).
15. **Remaining optional improvements:** ordered by value.
16. **Human follow-up actions:** anything the human must do (for example run live Nemotron verification and cache recording with their credentials).

**Honesty rule for the report:** do not claim completion of anything that was not implemented and tested. Distinguish clearly between "implemented and verified", "implemented but not verified", and "not implemented". If you could not verify live Nemotron behaviour, say so in the first paragraph of the report.

---

## 13. When You Are Blocked

| Blocker | What to do |
|---|---|
| No network or no Nemotron credentials | Follow Section 3.4; build everything else; mark live items Not verified |
| A dependency will not install | Try the nearest equivalent; log; keep the architecture |
| A document is contradictory or wrong | Section 3.3; never silently diverge |
| A stage gate keeps failing | Fix the root cause. Do not skip the gate. If after substantial effort it remains blocked, stop, write the blocker, evidence and what you tried into the log and the report, and do not proceed to dependent stages as if it passed |
| Time is running out | Apply the cut order in Section 10, finish and verify the MUST path (demo flow) first, then produce an honest report |
| You are unsure whether something is allowed | If it touches safety, honesty or data rules in Section 2, the answer is no unless the documents explicitly allow it |

---

## 14. Quick Reference (Pointers, Not Substitutes)

| Need | Go to |
|---|---|
| Product behaviour, acceptance criteria | PRD Sections 10 to 33 |
| Scoring factors, thresholds, bands | PRD Section 15; Technical Documentation Section 18 |
| Link strengths and cluster rule | Technical Documentation Sections 8, 14.3, 16 |
| Alert rules R1 to R6 | PRD Section 18.1; Technical Documentation Section 19.2 |
| Nemotron tasks, schemas, prompts | Technical Documentation Sections 21 and 22 |
| Validator and language guard | Technical Documentation Sections 20.2 and 20.3 |
| Database tables | Technical Documentation Section 13 |
| API routes and payloads | Technical Documentation Sections 35 and 36 |
| Canonical dataset and expected results | Technical Documentation Section 37 |
| Environment variables | Technical Documentation Section 32 |
| Folder structure | Technical Documentation Section 33 |
| Demo script | Section 8 of this document; PRD Appendix A |

---

## 15. Start Now

Begin with **Stage 1**. Inspect the repository, read the documents in order, record what you find, and only then create or change files. Work stage by stage, run everything you build, inspect real outputs, fix what breaks, and keep the implementation log current.

Build it honestly: a prototype that really processes synthetic evidence, really reasons with Nemotron over validated context, really shows its evidence, and really keeps a human in control.

**— End of FRAUDMESH_CODEX_MASTER_PROMPT —**
