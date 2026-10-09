# FraudMesh PRD acceptance matrix

Status is evidence-based: Verified means covered by current automated tests or deterministic checks; Partially verified means implementation exists but a required UI/live/performance condition remains; Not verified means no qualifying evidence yet.

Latest automated evidence snapshot: backend `24 passed`; frontend Vite production build passed; frontend Vitest passed; live Nemotron connectivity returned `NEMOTRON_OK`; synthetic `record-reasoning` completed with validator withholding. Five clean protected-mode browser rehearsals passed every route check with reset included; latest elapsed times were `2365–2543 ms`. Live API evidence after clean reseed: `138` evidence records, `51` entities, `39` graph edges, ordered R1–R6 alert rules, deduplicated alert records, and four contradiction candidates. See `docs/ACCEPTANCE_EXECUTION_2026-10-09.md` for the individual AC-01 through AC-70 execution record.

| ID | Status | Evidence / gap |
|---|---|---|
| AC-01 | Verified | Ingestion: Backend tests and deterministic implementation checks. |
| AC-02 | Verified | Ingestion: Backend tests and deterministic implementation checks. |
| AC-03 | Verified | Generator: Backend tests and deterministic implementation checks. |
| AC-04 | Verified | Ingestion: Backend tests and deterministic implementation checks. |
| AC-05 | Verified | Normalisation: Backend tests and deterministic implementation checks. |
| AC-06 | Verified | Ingestion: Backend tests and deterministic implementation checks. |
| AC-07 | Verified | Graph: Backend tests and deterministic implementation checks. |
| AC-08 | Verified | Graph: Backend tests and deterministic implementation checks. |
| AC-09 | Verified | Graph: Backend tests and deterministic implementation checks. |
| AC-10 | Verified | Graph: Backend tests and deterministic implementation checks. |
| AC-11 | Verified | Graph: Backend tests and deterministic implementation checks. |
| AC-12 | Verified | Risk: Backend tests and deterministic implementation checks. |
| AC-13 | Verified | Risk: Backend tests and deterministic implementation checks. |
| AC-14 | Verified | Protected dashboard risk inspector live-verified for ACC-D1 with LOW band, mitigation metadata, and the investigation-priority disclaimer. |
| AC-15 | Verified | Explicit risk-band boundary, clamp, and deterministic score tests pass. |
| AC-16 | Verified | Risk: Backend tests and deterministic implementation checks. |
| AC-17 | Verified | Protected grounded review creates evidence-linked findings, hypotheses, and plan steps with review context. |
| AC-18 | Verified | Explainability: Backend tests and deterministic implementation checks. |
| AC-19 | Verified | Explainability: Backend tests and deterministic implementation checks. |
| AC-20 | Verified | Protected graph UI exposes zoom, fit, pointer pan; five protected route rehearsals passed. |
| AC-21 | Verified | Protected graph UI exposes normalized node search. |
| AC-22 | Verified | Protected graph exposes entity type, link-strength, cluster and table filters. |
| AC-23 | Verified | Protected graph exposes node/edge inspector with relationship evidence IDs. |
| AC-24 | Verified | Protected graph cluster isolation control is rendered and stateful. |
| AC-25 | Verified | Protected Causal chain surface queries the bounded path API and renders numbered, ordered hops plus a tested no-path state. |
| AC-26 | Verified | Protected graph legend distinguishes exact/inferred/weak and table fallback renders. |
| AC-27 | Verified | Protected Evidence explorer renders indexed records and opens a selected masked record detail panel. |
| AC-28 | Verified | Protected Evidence explorer exposes text, type, date-range, and cited-by filters. |
| AC-29 | Verified | Protected case timeline renders ordered events, explicit minute gaps, and selectable evidence context. |
| AC-30 | Verified | Five clean reset-and-route rehearsals measured `295–334 ms` dashboard-after-reset readiness. |
| AC-31 | Verified | Four incident groups and the four-cluster protected network view were verified against the loaded dataset. |
| AC-32 | Verified | Case subgraph/evidence/timeline creation path is implemented and protected-browser verified. |
| AC-33 | Verified | Existing-case offer and escalation attachment workflow are implemented and tested. |
| AC-34 | Verified | Protected case contradiction marker click-through was verified live. |
| AC-35 | Verified | Protected case workspace supports Recorded order and Review order with live reordering and gap labels. |
| AC-36 | Verified | Protected simulator step measured 766 ms. |
| AC-37 | Verified | Simulator-driven graph refresh and deterministic alert path are implemented. |
| AC-38 | Verified | Cached review fallback is available and explicitly labelled. |
| AC-39 | Verified | Real-time: Backend tests and deterministic implementation checks. |
| AC-40 | Verified | Live alert API exposes ordered rules, values, evidence IDs and dedup metadata. |
| AC-41 | Verified | Escalation returns and records an attached-or-created case. |
| AC-42 | Verified | Review: Backend tests and deterministic implementation checks. |
| AC-43 | Verified | Review: Backend tests and deterministic implementation checks. |
| AC-44 | Verified | Normalized identifier search maximum measured latency was 2.579 ms. |
| AC-45 | Verified | Search: Backend tests and deterministic implementation checks. |
| AC-46 | Verified | Complaint extraction covers all 13 records with a 1.0 grounded field rate. |
| AC-47 | Verified | Injection-like complaint text is preserved as content and does not execute as an instruction; validator and test coverage pass. |
| AC-48 | Verified | Chronology endpoint and 12-event protected timeline pair check return 1.0 deterministic accuracy. |
| AC-49 | Verified | Live Nemotron recording plus protected bounded causal-chain and grounded-review surfaces are evidence-backed and validator-controlled. |
| AC-50 | Verified | Bounded “Not established” and withheld/gap handling are explicit. |
| AC-51 | Verified | Exact P5 narrative-link matching is implemented and tested. |
| AC-52 | Verified | Evidence-linked ranked plan steps are validator-passed and reviewable. |
| AC-53 | Verified | Hypotheses carry confidence, evidence, and counter-evidence/gap fields. |
| AC-54 | Verified | Protected T3 contradiction panel rendered all four planted candidates X1–X4 with evidence IDs, materiality, and assessments. |
| AC-55 | Verified | Auth: Backend tests and deterministic implementation checks. |
| AC-56 | Verified | Auth: Backend tests and deterministic implementation checks. |
| AC-57 | Verified | Auth: Backend tests and deterministic implementation checks. |
| AC-58 | Verified | Auth: Backend tests and deterministic implementation checks. |
| AC-59 | Verified | Masked evidence boundary covered by backend tests; controlled release UI added. |
| AC-60 | Verified | Masking: Backend tests and deterministic implementation checks. |
| AC-61 | Verified | Prompt masking helper and regression test cover contact/account-like values. |
| AC-62 | Verified | Audit append behavior covered by backend tests; Audit & Access UI added. |
| AC-63 | Verified | Audit: Backend tests and deterministic implementation checks. |
| AC-64 | Verified | Audit-write failure compensation and rollback regression test are covered. |
| AC-65 | Verified | Cached reasoning fallback and non-AI feature continuity are available. |
| AC-66 | Verified | Cached results are labelled “Cached (not live)”. |
| AC-67 | Not verified by design exception | Direct user instruction removed the synthetic-data banner; PRD requires it on every screen. |
| AC-68 | Verified | Protected UI scan found no accusatory user-facing labels; live copy preserves human review, no automatic enforcement, and “not an indicator of guilt.” |
| AC-69 | Verified | Five clean protected-mode rehearsals reset and passed Dashboard, Alerts, Cases, Network, Causal Chain, Evidence, and Audit route checks in `2365–2543 ms`. |
| AC-70 | Verified | Isolated reset-and-seed measurement completed in 480 ms. |
