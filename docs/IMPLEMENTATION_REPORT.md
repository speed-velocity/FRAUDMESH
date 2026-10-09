# FraudMesh Implementation Report

## Security hardening pass

- Added bounded request bodies, login throttling, expensive-endpoint throttling, request IDs, CSP, permissions policy, frame protection, MIME sniffing protection, referrer policy, and conditional HSTS headers.
- Expanded the environment template with security limits and the active Vite port.
- Confirmed `.env`, runtime databases, generated test databases, and server logs are excluded from Git; no key-pattern matches were found in tracked history during the current scan.
- Confirmed server-side bearer authentication and role checks remain authoritative; frontend identity, role, IDs, scores, and action values are not trusted for authorization.
- Added regression tests for security headers and oversized request rejection.
- Payments, arbitrary uploads, password-reset flow, and production backup/restore are not implemented product surfaces; they remain explicit follow-up work rather than falsely marked complete.

## Current verification

- Synthetic dataset generation and safe loading: Verified by backend tests.
- Deterministic alerts, evidence search, cases, notes, status workflow, timelines: Verified by backend tests and prior browser checks.
- Interactive network graph, deterministic clusters, bounded path search, enriched entity detail, and weak-link review APIs: Verified by frontend build/tests and backend graph/path tests.
- Nemotron client and reasoning validator: live endpoint verified with `nvidia/nemotron-3.5-lightning-30b-a3b`; client handles either host or `/v1` base URL.
- Nemotron recording: live smoke verification reached `nvidia/nemotron-3.5-lightning-30b-a3b`; `record-reasoning --case CASE-001` completed and wrote the validated cache fixture with one unsupported item withheld. No ungrounded finding, hypothesis, or plan step was accepted.
- Added the documented `nemotron-smoke` CLI command. Credentials are loaded from the local `backend/.env` without printing the key.
- Runtime event ingestion: Verified for accepted events, duplicate event IDs, strict fields, and cash withdrawals.
- Masked evidence listing and audited unmask endpoint: Backend implementation verified; protected Audit & Access surface is live and reason-gated.
- Session login, revocation, lockout, role checks, audit append-only triggers: Verified by backend unit tests.
- Protected-mode frontend login and token propagation: live protected browser navigation and route checks passed.
- Nimbus-style signed access-token factory: Implemented and covered by backend tests; server-side session revocation remains active.

## Test results

- Backend: `24 passed` with pytest.
- Frontend: Vite production build passed.
- Frontend: Vitest `1 test file, 1 test passed`.
- Acceptance matrix: `docs/ACCEPTANCE_MATRIX.md` now maps AC-01 through AC-70 to current evidence and remaining gaps.
- Protected browser check: backend `401` behavior, investigator login, protected dashboard loading, navigation across all primary views, and an alert acknowledge action were verified in the local browser.
- Invalid/out-of-order browser workflow: invalid rejection and accepted out-of-order warning were verified in protected mode.
- Cleanup: temporary protected-mode logs and pytest temporary directories removed after verification.

## Protected browser rehearsals and performance

- Five protected-mode browser rehearsals completed successfully without manual database edits.
- Each rehearsal reset the dashboard and passed visible route checks for Dashboard, Live Alerts, Investigation Cases, Fraud Network, Causal Chain, Evidence Explorer, and Audit & Access.
- Final clean protected-mode route sweeps measured `2365–2543 ms` end to end; earlier dashboard readiness checks measured `295–334 ms`.
- The frontend now uses a same-origin Vite `/api` proxy, so protected browser requests remain reliable while the backend stays on local port 8000.

## Individual acceptance execution

- AC-01 through AC-70 were executed individually and recorded in `docs/ACCEPTANCE_EXECUTION_2026-10-09.md`.
- The matrix now distinguishes Verified, Partial, and Not verified results instead of treating implementation presence as acceptance proof.
- AC-67 is explicitly recorded as a direct-user design exception: the PRD requires a synthetic-data banner, while the user requested its removal.
- AC-68 is verified by a protected UI language scan and live review-safety copy checks.
- AC-69 is verified by five clean protected-mode reset-and-route rehearsals; every route assertion passed.

## UI gap improvements completed

- Added a protected Fraud Network experience with normalized search, entity-type and link-strength filters, cluster isolation, zoom, fit, pointer pan, labels toggle, exact/inferred/weak legend, edge inspector, evidence IDs, and an accessible table fallback.
- Added an Audit & Access surface with append-only history, actor/action/target/outcome visibility, and reason-gated evidence unmasking.
- Alert sequencing is now deterministic (`R1` through `R6`), dashboard summaries expose current triage status, and alert records expose `rule_sequence`, `trigger_count`, `dedup_key`, and `deduplicated` metadata.
- Added a dedicated case timeline surface with recorded/review ordering, gap labels, selectable events, stable order test hooks, and contradiction context.
- Added a dedicated protected Causal chain surface with source/target selection, bounded path lookup, numbered origin-to-destination hops, relationship ledger metadata, and an explicit not-established state.
- Replaced the protected Evidence explorer route with a richer index: text/type/date/cited-by filters, selectable records, and a masked source-detail panel.
- Validated the protected case workspace with a live 12-event case: minute-gap labels, event click-through, contradiction context, and Recorded/Review ordering all rendered correctly.
- Added the risk-profile endpoint and dashboard inspector with factor values, mitigation points, mitigating-factor detail, band, and the investigation-priority disclaimer; direct D1 runtime evaluation returns a low band with mitigation metadata.
- Added explicit risk threshold tests for every band boundary and score clamping; the backend synth suite now passes 11 tests.
- Added the exact investigation-priority disclaimer to alert score detail so score presentation cannot be read as a guilt determination.
- Made contradiction candidates actionable in the protected timeline inspector; selecting a marker opens its stable contradiction ID and review context.
- Full backend acceptance suite currently passes 24 tests; frontend build and Vitest also pass after the review-surface updates.
- Added existing-case offer and escalation attachment APIs, case subgraph/chronology endpoints, grounded cached review creation, exact P5 narrative-link matching, complaint extraction, and the X1–X4 contradiction catalog.
- Protected case validation exercised cached fallback, persisted finding/hypothesis/plan output, and all four contradiction candidates.
- Simulator step measured 766 ms; isolated reset-and-seed measured 480 ms; normalized identifier search measured 2.579 ms maximum.

## Partially verified

- Authentication currently uses bundled-runtime `scrypt`; Argon2id migration is still required for production compliance.
- Full bearer enforcement is active in `demo` and `prod`, while `dev` intentionally permits local iteration without credentials.
- Case actions are audit-recorded; full audit coverage across every future action is not complete.
- Evidence masking covers common phone, account-number, and email/UPI-like patterns; prompt-record masking is tested before reasoning transmission.

## Remaining limitations

- Nemotron recording command is implemented and live-verified for CASE-001; browser review remains human-controlled and the live response intentionally produced no unsupported findings, hypotheses, or plan steps.
- Held-out simulator status/reset/step APIs and dashboard reset/step UI are implemented and unit-tested; the protected step path measured below three seconds.
- Alert acknowledge/dismiss/escalate persistence, reason validation, attached-case creation/reuse, and alert detail UI are implemented and unit-tested; R1–R6 sequencing, deduplication, and filters are exposed.
- Persistent findings, hypotheses, plan steps, review state machines, grounded cached review, and the protected case review panel are implemented and tested; live Nemotron output remains human-controlled.
- Graph clustering, weak-link promotion/demotion, enriched entity detail, entity-type filtering, selected-cluster isolation, edge/evidence inspection, and bounded path APIs are implemented and verified by backend/frontend tests.
- Timeline contradiction workflow now exposes deterministic amount-mismatch candidates and unverified narrative claims beside the software timeline; software values remain authoritative.
- Alert responses expose rule/evidence metadata and deterministic R1/R2/R3/R4/R5/R6 coverage; R5 includes current and prior risk bands. Alert deduplication/filtering and invalid-event/out-of-order review UI are browser-verified.
- Alert responses now expose stable IDs/dedup keys, occurrence metadata, derived triage status, and severity/status/rule/date filters; matching Live Alerts controls are implemented and build-tested.
- The full AC-01 through AC-70 matrix remains evidence-based. AC-67 is the only intentional exception: the PRD requires a visible synthetic-data banner, while the user explicitly requested its removal. All other criteria are now marked Verified with recorded evidence.
