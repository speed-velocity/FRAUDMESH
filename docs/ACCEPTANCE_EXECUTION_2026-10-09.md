# FraudMesh individual acceptance execution — 2026-10-09

Each criterion was considered individually against the current code, automated suite, live protected browser, and targeted API probes. “Partial” means implementation exists but the PRD’s full proof condition was not completed. “Not verified” is not treated as a pass.

Evidence anchors:

- Backend: pytest with a workspace basetemp → 24 passed.
- Frontend: npm run build and npm test -- --run → build passed; 1 test file passed.
- Protected browser: five clean reset-and-route rehearsals passed; dashboard-after-reset readiness 295–334 ms; complete rehearsal time 676–799 ms.
- Live API: clean reseed loaded 138 evidence records, 51 entities, 39 graph edges; alert API returned ordered R1–R6 rules and deduplicated alerts.
- Direct-user exception: AC-67 conflicts with the user-requested removal of the synthetic-data banner and is recorded honestly below.

| ID | Result | Individual evidence |
|---|---|---|
| AC-01 | Verified | Backend canonical loader and 24-test suite; runtime health reports 138 evidence records after clean reseed. |
| AC-02 | Verified | Synthetic-only loader refusal covered by backend database tests. |
| AC-03 | Verified | Deterministic generator tests cover same-seed output and target counts. |
| AC-04 | Verified | Malformed-record validation covered by ingestion tests. |
| AC-05 | Verified | Phone normalization and entity resolution covered by generator/database tests. |
| AC-06 | Verified | Reload/idempotency behavior covered by database tests. |
| AC-07 | Verified | Graph build check; live graph reports 51 nodes and 39 edges. |
| AC-08 | Verified | Cluster computation covered by graph tests; live UI reports 4 clusters. |
| AC-09 | Verified | Weak-link exclusion covered by graph/link tests. |
| AC-10 | Verified | Bounded network path API and graph tests pass. |
| AC-11 | Verified | Benign allow-list behavior covered by graph/database tests. |
| AC-12 | Verified | Deterministic risk output covered by database tests. |
| AC-13 | Verified | Risk alerts expose reasons and evidence IDs. |
| AC-14 | Verified | Protected dashboard risk inspector was exercised live for ACC-D1: LOW band, mitigation -5, “Funds retained,” and the investigation-priority disclaimer all rendered after protected navigation. |
| AC-15 | Verified | Added explicit low/medium/high/critical boundary tests at 0/24/25/49/50/74/75/100, score clamp coverage, and deterministic seeded-score coverage; backend synth suite passes 11 tests. |
| AC-16 | Verified | Alert score detail now visibly includes the exact disclaimer: “Investigation priority, not an indicator of guilt.” Build and frontend tests pass. |
| AC-17 | Verified | Protected case workspace now offers grounded review; browser run created an evidence-linked finding, hypothesis, and plan step with confidence/gap language and persisted review records. |
| AC-18 | Verified | Validator withholding behavior covered by reasoning tests and prior live recording. |
| AC-19 | Verified | Prohibited/accusatory output handling covered by validator tests. |
| AC-20 | Verified | Protected graph UI exposes zoom, fit, and pointer pan controls. |
| AC-21 | Verified | Protected graph UI exposes normalized node search. |
| AC-22 | Verified | Protected graph exposes entity type, link strength, cluster, and table filters. |
| AC-23 | Verified | Protected graph exposes node/edge inspector with relationship evidence IDs. |
| AC-24 | Verified | Protected graph cluster isolation control is rendered and stateful. |
| AC-25 | Verified | Protected `#chain` surface now traces the bounded path API, renders numbered origin/hop/destination steps, relationship metadata, and an explicit negative result when no path is found; live browser query verified on `ACC-M1 → ACC-M4`. |
| AC-26 | Verified | Protected graph legend distinguishes exact/inferred/weak and table fallback renders. |
| AC-27 | Verified | Protected Evidence explorer renders indexed records and opens a selected record detail panel with masked source context. |
| AC-28 | Verified | Protected Evidence explorer exposes text, type, date-from/date-to, and cited-by filters. |
| AC-29 | Verified | Protected case workspace rendered CASE-001 with 12 events, explicit minute gaps, and selectable evidence context. |
| AC-30 | Verified | Five clean reset-and-route rehearsals: 295–334 ms dashboard-after-reset readiness. |
| AC-31 | Verified | Dashboard runtime reports four incident groups; protected Fraud Network live view reports four connected clusters, including the reviewed M1–M7 network. |
| AC-32 | Verified | Case creation is backed by a case subgraph endpoint and linked evidence/timeline; protected case workspace rendered the created case and its 12-event timeline. |
| AC-33 | Verified | Existing-case offer API returns open cases for an entity; escalation now attaches to the existing case instead of creating a duplicate. |
| AC-34 | Verified | Protected case contradiction marker is a selectable button; live click opened `CON-C-07-UNVERIFIED` in the inspector. |
| AC-35 | Verified | Protected case workspace switched between Recorded order and Review order; ordering and gap labels changed in the live browser. |
| AC-36 | Verified | Protected held-out simulator step completed in 766 ms and returned the accepted-event refresh path, below the 3-second requirement. |
| AC-37 | Verified | Held-out simulator step ingested the next event and refreshes network state; graph refresh now reloads nodes/edges after simulator actions. |
| AC-38 | Verified | Unconfigured-client tests pass and protected case workspace offers explicit cached review mode with “Cached (not live)” labeling. |
| AC-39 | Verified | Duplicate event handling covered by ingestion tests. |
| AC-40 | Verified | Live alert API exposes rules, ordered rule_sequence, values, evidence IDs. |
| AC-41 | Verified | Protected alert escalation was exercised live; backend returns an attached-or-created case and records the escalation action. |
| AC-42 | Verified | Review persistence/reason validation covered by backend tests and case UI. |
| AC-43 | Verified | UI exposes human-review actions only; no enforcement or bulk-accept control. |
| AC-44 | Verified | Five direct normalized-identifier searches measured 2.579 ms maximum, below the 300 ms requirement. |
| AC-45 | Verified | Prefix search minimum-length behavior covered by search implementation/tests. |
| AC-46 | Verified | Complaint extraction endpoint and deterministic test cover all 13 complaints; grounded identifier extraction rate is 1.0. |
| AC-47 | Verified | Injection sentence is treated as complaint content, not executable instruction. |
| AC-48 | Verified | Chronology endpoint compares all ordered case-event pairs; the protected CASE-002 timeline contained 12 events and the deterministic pair check returned 1.0 accuracy. |
| AC-49 | Verified | Live Nemotron recording completed for CASE-001 with validator withholding; protected causal-chain and grounded-review surfaces expose only evidence-backed stages and preserve gaps. |
| AC-50 | Verified | Causal-chain UI explicitly renders bounded negative results as “Not established”; grounded review exposes unsupported claims as withheld/gaps. |
| AC-51 | Verified | Exact narrative-only P5 matching is implemented and tested; returned links include both complaint evidence IDs and a masked identifier. |
| AC-52 | Verified | Grounded review persists a ranked evidence-linked action plan; every generated step is marked validator-passed and reviewable. |
| AC-53 | Verified | Grounded hypotheses persist confidence, cited evidence, and counter-evidence/gap language. |
| AC-54 | Verified | Protected cases surface a dedicated T3 contradiction panel; the live catalog rendered all four planted candidates X1–X4 with evidence IDs, materiality, and assessments. |
| AC-55 | Verified | Protected endpoints returned 401 before login; protected browser login passed. |
| AC-56 | Verified | Role enforcement covered by backend auth tests. |
| AC-57 | Verified | Five-failure lockout covered by backend auth tests. |
| AC-58 | Verified | Repository scan found no committed default password. |
| AC-59 | Verified | Masking boundary covered by backend masking tests. |
| AC-60 | Verified | Unmask requires reason and appends audit event; Audit & Access UI added. |
| AC-61 | Verified | Prompt-record masking helper and test remove phone, account-like, and email values before reasoning transmission; technical evidence IDs remain explicit references. |
| AC-62 | Verified | Audit append behavior covered by backend tests; audit UI added. |
| AC-63 | Verified | Append-only audit triggers and backend tests pass. |
| AC-64 | Verified | Required audit-write failure compensation is implemented and covered by a rollback regression test; the originating alert action is removed when its audit write cannot complete. |
| AC-65 | Verified | Unconfigured Nemotron degrades gracefully; protected case workspace provides cached grounded review while non-AI case/network/evidence features remain available. |
| AC-66 | Verified | Cached review response and protected browser status explicitly render “Cached (not live)” and human-review-required labeling. |
| AC-67 | Not verified by design exception | Direct user instruction removed the synthetic-data banner; PRD requires it on every screen. |
| AC-68 | Verified | Protected UI language scan found no accusatory labels such as guilty/fraudster/thief/convict. Live dashboard and alert copy explicitly preserve human review, “not an indicator of guilt,” and no automatic enforcement. The synthetic-banner literal remaining in app.test.ts is a non-rendered regression fixture. |
| AC-69 | Verified | Five clean protected-mode rehearsals each reset the dashboard and reached Dashboard, Live Alerts, Investigation Cases, Connected Entities, Causal Chain, Evidence Explorer, and Audit & Access. All route checks passed; latest elapsed times were 2365–2543 ms. |
| AC-70 | Verified | Isolated `reset-and-seed` measurement completed in 480 ms using the bundled Python runtime and a temporary database. |
