# FRAUDMESH — PRODUCT REQUIREMENTS DOCUMENT

**Cross-Bank Financial Crime Reconstruction & Recovery Agent**

| Field | Value |
|---|---|
| Document | FRAUDMESH_PRD.md |
| Version | 1.0 (Draft for approval) |
| Date | 2026-10-07 |
| Position in chain | Document 2 of 4 (Project Plan -> PRD -> Technical Documentation -> Codex Master Prompt) |
| Source of truth | FRAUDMESH_PROJECT_PLAN.md v1.0 |
| Primary AI model | NVIDIA Nemotron |
| Implementation agent | OpenAI Codex |
| Data policy | Synthetic or authorized data only |
| Audience | Development team (Codex), mentors, judges |

> **Positioning:** Normal systems see suspicious transactions. FraudMesh sees the fraud network.

---

## 0. How to Read This Document

This PRD converts the Project Plan into testable product requirements. It defines WHAT the product does and how it behaves; the Technical Documentation will define HOW (schemas, module design, prompts). Where this PRD gives named parameters (for example `PASS_THROUGH_WINDOW_MIN`), their defaults are binding unless the Technical Documentation records a justified change.

**Conventions**

| Convention | Meaning |
|---|---|
| MUST / SHOULD / NICE | Priority, identical to the Project Plan: MUST HAVE (MVP), SHOULD HAVE, NICE TO HAVE |
| [DET] / [GRAPH] / [LLM] / [NEM] | Logic type: deterministic software, graph algorithm, generic language-model capability, Nemotron-specific reasoning |
| FR-xxx | Functional requirement ID |
| NFR-xxx | Non-functional requirement ID |
| AC-xx | Acceptance criterion ID (Section 33) |
| E-0001 | Evidence ID format (assigned by software only) |
| F-xx | Feature specification ID (Sections 10 to 25) |

**Hard product constraints (inherited, non-negotiable)**

1. Synthetic or authorized data only. No real bank, UPI, telecom, government or law-enforcement integration is simulated or claimed.
2. No output states or implies guilt. Allowed vocabulary: risk indicator, investigation priority, potential relationship, investigative hypothesis, evidence-backed finding.
3. No autonomous account freezing, fund seizure, reporting to authorities or any enforcement action.
4. The risk score is an investigation priority, never a probability of guilt.
5. Every AI-generated statement carries valid evidence IDs or is withheld.
6. A human investigator makes every decision; every decision is audit-logged.

---

## 1. Product Overview

### 1.1 Summary

FraudMesh is an investigation-support platform for financial-crime investigators. It ingests fragmented evidence (transactions, complaints, communications, device and account records), builds a relationship graph, reconstructs chronology and potential causal chains, computes an explainable investigation priority, and produces an evidence-backed investigation plan for human review.

### 1.2 Value proposition

| For | Who need | FraudMesh provides | Unlike |
|---|---|---|---|
| Financial-crime investigators and fraud analysts | To know whether apparently separate cases belong to one operation, and what to examine next | Network reconstruction, chronology, causal explanation and a ranked plan, each tied to evidence | Transaction flaggers, which identify suspicious items but leave the connecting work to the investigator |

### 1.3 Product pipeline

```
Evidence Ingest
   -> Entity & Link Extraction
   -> Chronology Build
   -> Causal Reconstruction
   -> Risk / Investigation Priority
   -> Investigation Plan
   -> Human Investigator Review
```

### 1.4 Architectural principle

```
Deterministic Systems + Graph Analysis + Nemotron Reasoning + Human Investigation
```

### 1.5 Product type and exclusions

FraudMesh is a professional investigation workbench. It is NOT a consumer banking app, a chatbot, a transaction classifier, a generic dashboard or a generic RAG application. There is no end-customer interface and no free-form chat box; AI output is produced only through defined reasoning tasks (Section 25) and shown in structured form.

### 1.6 Prototype boundaries

| Statement | Requirement |
|---|---|
| The prototype uses synthetic data | A persistent banner "Synthetic data. Investigation-support prototype. Not for enforcement decisions." appears on every screen after login and on the login screen |
| It has no real cross-bank access | The "Limitations and Safeguards" page states this explicitly |
| It is not enterprise-secure | The same page lists which controls are implemented and which are not |

---

## 2. Problem Statement

Modern fraud is a network problem. A single scam operation can involve multiple victims, bank accounts, UPI IDs, phone numbers, devices, mule-like pass-through accounts, transfers, cash withdrawals, communications and earlier complaints. Each victim files a separate complaint; each case is worked separately.

**The gap:** existing systems flag suspicious transactions or identifiers, but investigators must still manually reconstruct the full chain across fragmented incidents and decide whether apparently unrelated cases are connected.

**Investigator questions the product must answer**

| # | Question | Answered by |
|---|---|---|
| Q1 | Who or what is connected? | Graph, shared identifiers, clusters |
| Q2 | How are they connected? | Link strength, link evidence, paths |
| Q3 | When did events happen, and in what order? | Timeline, chronology reconstruction |
| Q4 | What money-flow relationships exist? | Money-flow paths, transaction analysis |
| Q5 | Which incidents may belong to the same network? | Cluster view, cross-case links |
| Q6 | What evidence supports each finding? | Evidence IDs, evidence explorer |
| Q7 | What should be examined next? | Investigation plan |

---

## 3. User Personas

### 3.1 Primary: Financial-Crime Investigator ("Asha")

| Attribute | Detail |
|---|---|
| Role | Investigator or fraud analyst handling complaints and suspicious-activity cases |
| Goals | Connect scattered incidents; build a defensible chain; decide next steps |
| Pain points | Evidence scattered across systems; narratives that conflict with ledgers; no view of the whole operation; time spent on manual linking |
| Skills | Domain expert; comfortable with tables and timelines; not a data scientist |
| Needs from FraudMesh | Visible reasoning, evidence IDs, control over every conclusion, fast navigation |
| Role in system | Investigator role |
| Distrusts | Black-box scores, unsupported accusations, tools that act on their own |

### 3.2 Secondary personas

| Persona | Needs | MVP mapping |
|---|---|---|
| Investigation Supervisor ("Vikram") | See case status, which findings were accepted or rejected and by whom; check quality of review | Admin role (read all cases and audit); supervisor sign-off is NICE |
| Fraud Operations Analyst ("Meera") | Monitor alerts and trends; triage the alert feed; escalate to cases | Investigator role (alert triage features) |
| Security/Compliance Reviewer ("Dev") | Verify audit trail, masking, access control and that no autonomous action exists | Admin role (audit log view, limitations page) |

### 3.3 Non-users

Bank customers, victims and the public never access FraudMesh. There is no victim-facing interface.

---

## 4. User Journeys

### 4.1 Journey J1 — Alert to understanding (core demo journey)

| Step | Investigator action | System response | Features |
|---|---|---|---|
| 1 | Logs in | Authenticates; shows synthetic-data banner and dashboard | F-20, F-01 |
| 2 | Reviews dashboard | Shows four apparently separate cases, alert feed, priority list | F-01 |
| 3 | A new event arrives (simulated) | Alert appears from deterministic rules within 3 seconds | F-08, F-09 |
| 4 | Opens the alert | Sees triggered rules, risk score and factors | F-09, F-06 |
| 5 | Opens network view | Graph has updated; related entities and a cross-case cluster are visible | F-03, F-15 |
| 6 | Creates a case from the cluster | Case workspace opens with subgraph, evidence and timeline | F-11, F-02 |
| 7 | Inspects timeline | Software-ordered events with evidence IDs and flagged conflicts | F-05 |
| 8 | Runs reasoning | Progress shown; structured result with chronology, causal chain, findings | F-16, F-17 |
| 9 | Checks evidence for a finding | Clicks evidence IDs; sees source records | F-04, F-07 |
| 10 | Reviews risk factors | Per-factor breakdown | F-06 |
| 11 | Reads investigation plan | Ranked steps with rationale and evidence | F-18 |
| 12 | Accepts, rejects or annotates | Review states recorded | F-10 |
| 13 | Checks audit log | Own actions visible | F-21 |

### 4.2 Journey J2 — Triage alerts (Fraud Operations Analyst)

Open alert feed -> filter by severity -> open alert -> read triggered rules and evidence -> acknowledge, dismiss with reason, or escalate to case.

### 4.3 Journey J3 — Resolve a conflicting narrative

Open case -> timeline shows conflict marker (for example complaint amount differs from ledger) -> open contradiction panel -> read software-detected conflict and Nemotron's materiality assessment -> accept or reject assessment -> timeline updates its confidence notes.

### 4.4 Journey J4 — Supervisor oversight

Admin logs in -> opens case list -> filters by review state -> opens case -> sees review history and reasons -> opens audit log filtered by case.

### 4.5 Journey J5 — Degraded operation

Nemotron unavailable -> UI shows "Reasoning unavailable" -> investigator continues with deterministic graph, risk and timeline -> may switch to cached mode (labelled) -> results marked "Cached (not live)".

---

## 5. User Stories

| ID | As a... | I want to... | So that... | Priority | Feature |
|---|---|---|---|---|---|
| US-01 | Investigator | see all active alerts ranked by priority | I look at the riskiest items first | MUST | F-01, F-09 |
| US-02 | Investigator | see why an alert fired | I can judge whether it deserves attention | MUST | F-09, F-06 |
| US-03 | Investigator | open a visual network of related entities | I understand connections at a glance | MUST | F-03 |
| US-04 | Investigator | inspect any node or edge and its evidence | I can verify connections myself | MUST | F-03, F-04 |
| US-05 | Investigator | see which apparently separate cases connect | I find the larger operation | MUST | F-03, F-15 |
| US-06 | Investigator | view an ordered timeline of events | I understand the sequence | MUST | F-05 |
| US-07 | Investigator | see an explainable risk score with factors | I trust or challenge the priority | MUST | F-06 |
| US-08 | Investigator | have complaints interpreted into structured facts | I do not read every narrative manually | MUST | F-16 |
| US-09 | Investigator | get a reconstructed causal chain with cited evidence | I can explain the operation | MUST | F-17 |
| US-10 | Investigator | get ranked next steps | I know what to do next | MUST | F-18 |
| US-11 | Investigator | accept, reject or annotate each finding | I stay in control | MUST | F-10 |
| US-12 | Investigator | create and manage cases | I organise my work | MUST | F-11 |
| US-13 | Investigator | search by identifier, filter by type, time and amount | I find things quickly | MUST (search); SHOULD (advanced filters) | F-12 |
| US-14 | Investigator | browse all evidence and see which findings cite it | I verify grounding | SHOULD | F-04 |
| US-15 | Investigator | see contradictions between narrative and records | I do not miss inconsistencies | SHOULD | F-19 |
| US-16 | Investigator | watch a new event update the graph and score live | I see real-time detection | SHOULD | F-08 |
| US-17 | Investigator | have identifiers masked by default | PII exposure is minimised | MUST | F-22 |
| US-18 | Investigator | continue working if the AI is unavailable | the tool stays usable | MUST | F-16 to F-18, Section 30 |
| US-19 | Supervisor | see who accepted or rejected which finding and why | I can review quality | MUST (audit), SHOULD (review report) | F-10, F-21 |
| US-20 | Compliance reviewer | view an append-only audit log | I can verify accountability | MUST | F-21 |
| US-21 | Compliance reviewer | read what the prototype does not do | no overstated claims are made | MUST | Section 1.6 |
| US-22 | Investigator | compare the AI's statements with the evidence list | I can detect unsupported claims | MUST | F-07 |
| US-23 | Admin | manage demo users | the demo roles work | SHOULD | F-20 |

---

## 6. Functional Requirements Catalogue

Each requirement is detailed in the feature specification sections referenced. Priorities follow the Project Plan.

### 6.1 Evidence and data

| ID | Requirement | Priority | Logic | Spec |
|---|---|---|---|---|
| FR-001 | Ingest structured records (transactions, accounts, devices, phone/UPI mappings, device logs, complaints metadata) from files | MUST | [DET] | F-13 |
| FR-002 | Ingest unstructured text (complaint narratives, communication snippets) from files | MUST | [DET] | F-13 |
| FR-003 | Validate every record against schema; reject invalid with reason codes | MUST | [DET] | F-13 |
| FR-004 | Normalise identifiers (phone, account, UPI, device, timestamps) | MUST | [DET] | F-13 |
| FR-005 | Assign stable software-generated evidence IDs (E-0001 format) | MUST | [DET] | F-13 |
| FR-006 | Refuse any dataset not flagged `synthetic: true` | MUST | [DET] | F-13, F-14 |
| FR-007 | Generate the seeded synthetic dataset and separate ground-truth file | MUST | [DET] | F-14 |

### 6.2 Graph and analysis

| ID | Requirement | Priority | Logic | Spec |
|---|---|---|---|---|
| FR-010 | Extract entities and exact links from structured records | MUST | [DET] | F-15 |
| FR-011 | Build the graph deterministically from stored records | MUST | [GRAPH] | F-15 |
| FR-012 | Detect clusters using exact and promoted/inferred links; weak links excluded unless promoted | MUST | [GRAPH] | F-15 |
| FR-013 | Find time-ordered money-flow paths | MUST | [GRAPH] | F-15 |
| FR-014 | Detect shared identifiers across cases | MUST | [DET] | F-15 |
| FR-015 | Compute transaction aggregates and pass-through metrics | MUST | [DET] | F-15, F-06 |
| FR-016 | Incrementally update graph for a new event | SHOULD | [GRAPH] | F-08 |
| FR-017 | Compute centrality (degree, betweenness) | SHOULD | [GRAPH] | F-15 |
| FR-018 | Extract bounded case subgraph for reasoning | MUST | [GRAPH] | F-15, F-11 |

### 6.3 Risk, alerts, real-time

| ID | Requirement | Priority | Logic | Spec |
|---|---|---|---|---|
| FR-020 | Compute explainable risk score and band per scoreable entity | MUST | [DET]+[GRAPH] | F-06 |
| FR-021 | Display factor breakdown with evidence IDs and mitigating factors | MUST | [DET] | F-06 |
| FR-022 | Rule-based alert generation from new events | SHOULD | [DET] | F-08, F-09 |
| FR-023 | Alert triage (acknowledge, dismiss with reason, escalate to case) | SHOULD | [DET] | F-09 |
| FR-024 | Event simulator with play, pause, step, reset | SHOULD | [DET] | F-08 |
| FR-025 | Scripted single "inject next event" control as MUST-level fallback for demo | MUST | [DET] | F-08 |

### 6.4 Reasoning

| ID | Requirement | Priority | Logic | Spec |
|---|---|---|---|---|
| FR-030 | Interpret complaints into structured facts (T1) | MUST | [NEM] | F-16 |
| FR-031 | Cross-evidence relationship reasoning (T2) | MUST | [NEM] | F-17 |
| FR-032 | Chronology reconstruction with uncertainty (T4) | MUST | [DET]+[NEM] | F-17 |
| FR-033 | Causal reconstruction Precursor -> Trigger -> Movement -> Amplification -> Outcome (T5) | MUST | [NEM] | F-17 |
| FR-034 | Investigative hypotheses with confidence and counter-evidence (T6) | MUST | [NEM] | F-18 |
| FR-035 | Ranked investigation plan (T7) | MUST | [NEM] | F-18 |
| FR-036 | Contradiction candidates by software, materiality by Nemotron (T3) | SHOULD | [DET]+[NEM] | F-19 |
| FR-037 | Relationship explanation (T8) and case summary (T9) | SHOULD | [NEM] | F-07 |
| FR-038 | Evidence validator rejects invalid IDs and evidence-less findings | MUST | [DET] | F-07 |
| FR-039 | Language guard blocks accusatory phrasing | MUST | [DET] | F-07 |
| FR-040 | Cached-reasoning mode | MUST | [DET] | Section 30 |

### 6.5 Workflow, security, platform

| ID | Requirement | Priority | Logic | Spec |
|---|---|---|---|---|
| FR-050 | Case create, view, update status, annotate, close | MUST | [DET] | F-11 |
| FR-051 | Finding and plan-step review (accept, reject with reason, needs evidence, annotate) | MUST | [DET] | F-10 |
| FR-052 | Authentication with expiring sessions | MUST | [DET] | F-20 |
| FR-053 | Role-based authorization (Investigator, Admin) | MUST | [DET] | F-20 |
| FR-054 | Audit log of defined events | MUST | [DET] | F-21 |
| FR-055 | PII masking by default with logged unmask | MUST | [DET] | F-22 |
| FR-056 | Search by identifier; filters by entity type, time, amount, link strength | MUST (search), SHOULD (filters) | [DET] | F-12 |
| FR-057 | Limitations and Safeguards page | MUST | UI | Section 1.6 |
| FR-058 | Reset-and-seed command restores demo state | MUST | [DET] | F-14 |

---

## 7. Non-Functional Requirements

| ID | Category | Requirement | Target | Priority |
|---|---|---|---|---|
| NFR-001 | Performance | Build full graph from seeded database | < 5 s | MUST |
| NFR-002 | Performance | Event to alert (deterministic path, excluding Nemotron) | < 3 s | MUST (for fallback inject), SHOULD (for stream) |
| NFR-003 | Performance | API read endpoints (non-reasoning), 95th percentile | < 500 ms on demo dataset | MUST |
| NFR-004 | Performance | Graph render of case subgraph (up to 300 nodes, 600 edges) | < 2 s initial; interactions < 200 ms | MUST |
| NFR-005 | Performance | Nemotron task latency | Target < 60 s; progress state visible after 1 s | MUST |
| NFR-006 | Reliability | Demo end-to-end success on clean start | >= 5 of 5 rehearsal runs | MUST |
| NFR-007 | Reliability | Application usable (deterministic features) with Nemotron unreachable | 100% of non-AI features work | MUST |
| NFR-008 | Reproducibility | Seeded generator and risk scores | Identical output across runs | MUST |
| NFR-009 | Security | No hardcoded secrets; secrets via environment | Zero secrets in repository | MUST |
| NFR-010 | Security | Passwords hashed; sessions expire | Default expiry 60 min, configurable | MUST |
| NFR-011 | Privacy | PII masked in UI, API, logs and prompts by default | 100% of identifier fields | MUST |
| NFR-012 | Auditability | Every defined event writes an audit record | 100% coverage of the audit event list | MUST |
| NFR-013 | Usability | Core flows reachable in <= 3 clicks from dashboard (open case, open graph, open timeline, open evidence) | Verified by checklist | MUST |
| NFR-014 | Accessibility | Keyboard focus visible; colour not the sole carrier of meaning; text contrast >= 4.5:1 | Manual check | SHOULD |
| NFR-015 | Portability | Runs on a single laptop from a clean clone with documented steps | <= 15 min setup | MUST |
| NFR-016 | Maintainability | Thresholds and weights are configuration, not scattered constants | Config file | MUST |
| NFR-017 | Observability | Structured logs with request ID; Nemotron call log (masked) | Present | MUST |
| NFR-018 | Honesty | No UI or doc text claims real data, guilt, certainty or enterprise security | Text review checklist | MUST |
| NFR-019 | Compatibility | Latest desktop Chrome and Edge; 1440x900 minimum design target | Manual check | MUST |
| NFR-020 | Scalability (prototype) | Correct behaviour up to 5,000 records without redesign | Load check | NICE |

---

## 8. MVP Requirements

The MVP equals all MUST items. It is complete when all acceptance criteria marked MUST in Section 33 pass.

| # | MVP capability | Features |
|---|---|---|
| 1 | Synthetic dataset with hidden network, decoys, planted contradictions | F-14 |
| 2 | Evidence ingestion with stable IDs | F-13 |
| 3 | Entity and exact link extraction | F-15 |
| 4 | Graph, clusters, money-flow paths | F-15 |
| 5 | Transaction analysis and explainable risk score | F-06 |
| 6 | Dashboard, case workspace, network view, timeline | F-01, F-02, F-03, F-05 |
| 7 | Nemotron T1, T2, T4, T5, T6, T7 with validator | F-16, F-17, F-18, F-07 |
| 8 | Review workflow | F-10 |
| 9 | Cases | F-11 |
| 10 | Authentication, roles, audit log, masking | F-20, F-21, F-22 |
| 11 | Search by identifier | F-12 |
| 12 | Scripted "inject next event" with alert | F-08, F-09 (minimal) |
| 13 | Cached-reasoning mode and failure handling | Section 30 |
| 14 | Limitations and Safeguards page | Section 1.6 |

**MVP cut rule:** if time is short, cut from the bottom of Section 9 first, then SHOULD features in the order listed in the Project Plan Section 29; never cut an MVP capability.

---

## 9. Advanced Requirements

| # | Requirement | Priority | Notes |
|---|---|---|---|
| A1 | Continuous event simulator (play, pause, step, speed) | SHOULD | Replaces scripted inject as the headline demo |
| A2 | Contradiction detection panel (T3) | SHOULD | Four planted contradictions must surface |
| A3 | Evidence explorer with citation back-links | SHOULD | |
| A4 | Advanced filters (time window, amount range, link strength, risk band) | SHOULD | |
| A5 | Betweenness centrality and richer risk factors | SHOULD | |
| A6 | Plan refinement after investigator feedback (re-run T7 with reviewed state) | SHOULD | |
| A7 | Audit log hash chaining (tamper evidence) | SHOULD | Not claimed as immutability |
| A8 | Timeline-to-graph synchronisation (time slider filters graph) | SHOULD | |
| A9 | Counterfactual check ("which single link, if wrong, collapses this finding?") | NICE | |
| A10 | Case report export | NICE | |
| A11 | Supervisor sign-off role | NICE | |
| A12 | Community detection | NICE | |
| A13 | Streaming infrastructure, production scale | NICE | Explicitly not required |

---

## 10. Dashboard Requirements

### F-01 — Investigation Dashboard

| Item | Specification |
|---|---|
| Feature name | Investigation Dashboard |
| User problem | The investigator needs to know instantly what is happening and what to look at first |
| Description | Landing screen after login summarising fraud activity, alerts and priority cases |
| User interaction | Click a KPI tile to filter; click an alert to open it; click a case card to open the workspace; click "Open network" to jump to the graph; dataset banner always visible |
| Inputs | Cases, alerts, risk scores, transactions, simulator state |
| Processing | [DET] aggregation of counts and sums; ranking by score and recency; no Nemotron calls |
| Outputs | (1) KPI tiles: open cases, new alerts, accounts in High/Critical band, total value of flagged transfers (INR), cross-case clusters detected. (2) Alert feed (newest first, severity-coloured, max 20 with "view all"). (3) Priority list: top 10 accounts or clusters by score with band. (4) Cases table with status. (5) Activity chart: transaction value per day (last 21 days). (6) Simulator control strip (play, pause, step, reset). (7) Dataset and prototype banner |
| Edge cases | No alerts (empty-state message); no cases; simulator at end of queue (disable step, show "no more events"); stale data after reset (refresh automatically) |
| Acceptance criteria | AC-30, AC-31 |
| Priority | MUST (tiles, alert feed, priority list, cases); SHOULD (activity chart, simulator strip) |

**Dashboard layout rules**

- Calm, dense, professional workspace; restrained palette; accent colours reserved for risk band and link strength.
- Risk band colours: Low (neutral), Medium (amber), High (orange), Critical (red). Colour is always accompanied by the band text.
- Every number is clickable and leads to the records behind it.

---

## 11. Investigation Workspace Requirements

### F-02 — Case Workspace

| Item | Specification |
|---|---|
| Feature name | Case Workspace |
| User problem | The investigator needs one place that brings together graph, timeline, evidence, findings and decisions for one investigation |
| Description | A tabbed workspace for a single case |
| User interaction | Tabs: Summary, Network, Timeline, Evidence, Findings, Plan, Contradictions (SHOULD), Notes, History. Header shows case title, status, priority band, owner, last updated, dataset banner. Actions: Run reasoning, Switch live/cached mode, Change status, Add note |
| Inputs | Case record, case subgraph, evidence set, timeline, findings, plan, review history |
| Processing | [DET] assembly of case data; reasoning jobs through Section 25 |
| Outputs | Summary tab: case title, cluster size, victims, accounts, total value moved, priority band with top three factors, top finding statements (labelled by source), reasoning status. Other tabs per their features |
| Edge cases | Case with no reasoning yet (empty-state with "Run reasoning"); reasoning unavailable; cluster changes after new events (banner "Cluster has grown: refresh case subgraph"; subgraph not silently changed); two investigators editing (last write wins, history records both) |
| Acceptance criteria | AC-32, AC-33 |
| Priority | MUST (Summary, Network, Timeline, Evidence list, Findings, Plan, Notes, History); SHOULD (Contradictions tab) |

**Workspace rules**

- Every AI-derived element shows a source tag: Deterministic, Graph, Nemotron-live, Nemotron-cached.
- The Summary tab never displays an AI statement without its evidence list reachable in one click.
- Case-level "what changed" notice appears when new events touch the case after reasoning was run (results marked "Possibly out of date").

---

## 12. Fraud-Network Visualization Requirements

### F-03 — Interactive Network View

| Item | Specification |
|---|---|
| Feature name | Interactive Network View |
| User problem | Complex relationships across many entities are not understandable in tables |
| Description | Interactive node-link visualisation of the fraud graph (global view with cluster filter, and case view) |
| User interaction | Zoom, pan, drag nodes, click to inspect node or edge, hover for tooltip, search box to focus an entity, filter panel, "Isolate cluster", "Highlight chain" (select chain from causal result or choose start and end nodes), time slider (SHOULD), legend toggle, "Table view" fallback |
| Inputs | Graph nodes and edges with metadata; clusters; risk scores; chain definitions; filters |
| Processing | [GRAPH] layout input and clustering from the backend; client-side rendering and layout; no Nemotron |
| Outputs | Rendered graph; inspector panel with metadata, evidence IDs and links to Evidence and Timeline; highlighted chain |
| Edge cases | Empty graph; very large cluster (more than 300 nodes: show cluster summary nodes with expand); disconnected nodes; overlapping labels (labels shown on hover or zoom); rendering failure (automatic fallback to table view); selected node absent after filter (selection cleared with message) |
| Acceptance criteria | AC-20 to AC-26 |
| Priority | MUST (all except time slider and risk-based sizing); SHOULD (time slider, risk sizing) |

### 12.1 Node categories

| Node type | Shape | Colour family | Icon label | Key metadata shown in inspector |
|---|---|---|---|---|
| Victim | Circle | Blue | V | victim ID (masked name), case, complaint IDs, total reported loss |
| Person/Entity | Circle | Slate | P | entity ID, role tag, linked accounts |
| Bank Account | Rounded square | Teal | A | masked account, bank, risk band, inflow and outflow totals, degree |
| UPI ID | Rounded square (small) | Teal (light) | U | masked UPI, mapped account |
| Phone Number | Hexagon | Purple | T | masked phone, role tag (for example "reported as caller"), complaint IDs |
| Device | Diamond | Brown | D | device ID, accounts or logins using it, first and last seen |
| Transaction | Small dot on an edge (or small node when expanded) | Grey | Rs | amount (INR), timestamp, evidence ID |
| Withdrawal | Triangle | Orange | W | amount, location label (synthetic), timestamp, evidence ID |
| Complaint | Document glyph | Light blue | C | complaint ID, date, interpretation status, extracted claims |
| Incident | Square outline (grouping node) | Navy outline | I | incident ID, cases and complaints grouped |

Notes: Transactions render as edges between accounts by default (arrow weight by amount); they are expandable into nodes when the user inspects an edge or enables "Show transactions as nodes". Incident nodes group complaints and may be collapsed.

### 12.2 Edge categories and labels

| Relationship | Label shown | Direction | Style | Metadata |
|---|---|---|---|---|
| OWNS | owns | Entity -> Account/Phone/UPI | thin solid | source, evidence ID |
| USES | uses | Entity/Account -> UPI/Phone | thin solid | source, evidence ID |
| LINKED_TO | linked to | Undirected | dashed (colour by strength) | strength, basis, evidence IDs |
| TRANSFERRED_TO | transferred | Directed account -> account | solid arrow, width by amount | amount, timestamp, evidence ID |
| REPORTED_IN | reported in | Victim/Phone/Account -> Complaint | dotted | complaint ID, extraction source |
| WITHDREW_FROM | withdrew from | Withdrawal -> Account | solid arrow | amount, timestamp, location label |
| USED_DEVICE | used device | Account/Login -> Device | thin solid, brown | first and last seen, evidence ID |
| USED_PHONE | used phone | Account/Entity -> Phone | thin solid, purple | evidence ID |
| CONNECTED_TO | connected | Undirected | dashed | basis, strength |
| PRECEDES | precedes | Event -> Event (timeline only) | thin grey arrow | time gap |
| PART_OF_CASE | part of case | Entity -> Incident/Case | very light | case ID |

### 12.3 Link strength styling

| Strength | Visual | Cluster-forming? |
|---|---|---|
| Exact | Solid line | Yes |
| Inferred (Nemotron-proposed, confirmed by deterministic check) | Dashed line with "inferred" badge | Yes |
| Inferred (not confirmed) | Dashed line, pale, "unconfirmed" badge | No, until investigator promotes |
| Weak | Dotted line, grey | No, until investigator promotes |

### 12.4 Filtering

| Filter | Options | Priority |
|---|---|---|
| Entity type | Toggle each node category | MUST |
| Link strength | Exact, Inferred, Weak | MUST |
| Cluster / case | Select one or more | MUST |
| Risk band | Low to Critical | SHOULD |
| Time window | Start and end datetime | SHOULD |
| Amount range | Min and max INR for transfer edges | SHOULD |
| Show only money-flow edges | Toggle | SHOULD |

### 12.5 Timeline interaction

| Interaction | Behaviour | Priority |
|---|---|---|
| Click event in timeline | Network view focuses and highlights the related nodes and edges | MUST |
| Click node in graph | Timeline scrolls to and highlights that entity's events | MUST |
| Time slider on graph | Shows only edges with timestamps up to the chosen time; nodes with no visible edges fade | SHOULD |
| Play-through | Animates the chain step by step in time order | NICE |

### 12.6 Case highlighting and suspicious clusters

- Selecting a case dims everything except its subgraph and draws a soft outline around cluster members.
- Cluster badge shows cluster ID, member counts, and priority band (highest member score).
- "Cross-case" badge appears when a cluster contains records from two or more originally separate cases or incidents.
- Fraud-chain highlighting draws the selected chain in a distinct accent with step numbers 1..n and arrows in time order.
- Labels never use accusatory words; node tooltips use role tags such as "reported as caller by 3 complaints" or "pass-through pattern indicator".

### 12.7 Visualization acceptance summary

Visual operations (zoom, pan, search, filter, node inspect, edge inspect, transaction inspect, evidence inspect, timeline inspect, cluster isolation, chain highlighting) must each pass an acceptance criterion (AC-20 to AC-26).

---

## 13. Evidence Explorer

### F-04 — Evidence Explorer

| Item | Specification |
|---|---|
| Feature name | Evidence Explorer |
| User problem | The investigator must verify what supports any claim and see all raw evidence |
| Description | Searchable, filterable list of every evidence record with detail view and "cited by" back-links |
| User interaction | Search box; filters (type, date range, case, entity); click row for detail; click "Cited by" to open the finding; click linked entity to focus on graph; "Unmask" action with reason |
| Inputs | Evidence records, entities, findings, citations |
| Processing | [DET] queries and pagination |
| Outputs | List columns: evidence ID, type, timestamp, source, short summary, linked entities, citation count. Detail: normalised fields, raw original text (for narratives, shown in a delimited read-only block), extraction results, citing findings |
| Edge cases | Evidence cited but later re-ingested (ID stays stable; version note); narrative containing adversarial text (displayed as plain text, never executed or interpreted by the UI); very long narrative (collapsible); no results (empty state) |
| Acceptance criteria | AC-27, AC-28 |
| Priority | MUST (evidence detail via ID from any finding); SHOULD (full explorer list and filters) |

**Evidence types:** Transaction, Withdrawal, Complaint, Communication, Device log, Account record, Phone/UPI mapping.

---

## 14. Timeline / Chronology Interface

### F-05 — Case Timeline

| Item | Specification |
|---|---|
| Feature name | Case Timeline |
| User problem | Investigators must understand the order and spacing of events across incidents |
| Description | Vertical or horizontal timeline of all events in a case, sorted by software, optionally enriched by Nemotron's reconstructed chronology |
| User interaction | Scroll, zoom time scale, filter by event type and entity, click event for detail, toggle "Software order" and "Reconstructed order (Nemotron)", click conflict marker to open contradiction panel, click time gap to see elapsed time, synchronise with network view |
| Inputs | Evidence with timestamps; chronology job result; conflict candidates |
| Processing | [DET] timestamp normalisation (UTC storage, configurable display zone, default Asia/Kolkata), sorting, gap computation, lane assignment per entity or per case. [NEM] T4 resolves missing or conflicting timestamps |
| Outputs | Events with timestamp, type icon, summary, evidence IDs, case lane; gaps between consecutive transfers in a chain labelled (for example "7 min"); markers: conflict, estimated time, reconstructed-order difference; phase bands for causal stages when T5 has run |
| Edge cases | Missing time (event shown in an "Unplaced" lane until placed by T4 or the investigator); identical timestamps (stable secondary sort by evidence ID); time zone mismatch in source (normalised, original preserved and visible); events months apart (time axis compresses with break markers); Nemotron order differing from software order (both shown; differences highlighted; software timestamps are never overwritten) |
| Acceptance criteria | AC-29, AC-34, AC-35 |
| Priority | MUST (software order, gaps, evidence links, graph sync); SHOULD (reconstructed order toggle, phase bands) |

**Rule:** Reconstructed order from Nemotron is displayed as an estimate with a confidence and rationale. Recorded timestamps always remain visible.

---

## 15. Risk Score Interface

### F-06 — Explainable Risk Score / Investigation Priority

| Item | Specification |
|---|---|
| Feature name | Explainable Risk Score / Investigation Priority |
| User problem | The investigator needs a defensible ranking of where to look, and must see why |
| Description | Deterministic scoring of accounts (full factors) and of phones, devices and UPI IDs (subset), with band and full breakdown. Cluster/case priority is the highest member account score |
| User interaction | Click any score badge to open the breakdown drawer; expand each factor to see input data and evidence IDs; compare two entities (SHOULD); view mitigating factors; read disclaimer |
| Inputs | Transactions, graph features, complaints, flags, configuration weights |
| Processing | [DET]+[GRAPH]; formula in Section 15.2; no Nemotron participation in computation; Nemotron may describe the score in words only when given the computed breakdown |
| Outputs | Total 0 to 100, band (Low, Medium, High, Critical), per-factor points and maximum, supporting values, evidence IDs, mitigating adjustments, calculation timestamp, configuration version, disclaimer "Investigation priority, not an indicator of guilt." |
| Edge cases | Entity with no activity (score 0, band Low, "insufficient activity"); missing timestamps (time-based factors scored 0 with "insufficient data" label); decoy with high volume (mitigation applied and displayed); config change (scores recomputed, version shown); ties (ordered by victim count then total value) |
| Acceptance criteria | AC-12 to AC-16 |
| Priority | MUST |

### 15.1 Factor list (initial weights, configurable)

| Factor | Key | Max points | Priority | Applies to |
|---|---|---|---|---|
| Rapid movement of funds | RAPID_MOVEMENT | 20 | MUST | Account |
| Account hopping | ACCOUNT_HOPPING | 15 | MUST | Account |
| Shared identifiers | SHARED_IDENTIFIERS | 20 | MUST | Account, Phone, Device, UPI |
| Multiple victims | MULTIPLE_VICTIMS | 15 | MUST | Account, UPI, Phone |
| Multiple linked complaints | LINKED_COMPLAINTS | 10 | MUST | All scoreable |
| Unusual transaction pattern | UNUSUAL_PATTERN | 10 | SHOULD | Account |
| Suspicious temporal relationship | SUSPICIOUS_TIMING | 5 | SHOULD | Account |
| Connection to known suspicious synthetic entity | FLAGGED_PROXIMITY | 10 | SHOULD | All scoreable |
| Repeated entity connections / graph centrality | CENTRALITY | 5 | SHOULD | Account |
| Mitigating factors | MITIGATION | up to -15 | SHOULD | Account |

Raw maximum = 110.

### 15.2 Scoring definitions (default parameters)

| Factor | Rule (points) |
|---|---|
| RAPID_MOVEMENT | A pass-through event = an inbound transfer of which at least `FORWARD_RATIO` (0.80) is sent onward within `PASS_THROUGH_WINDOW_MIN` (30) minutes. Count n of events: 0 -> 0; 1 -> 8; 2 -> 12; 3 -> 16; 4 or more -> 20 |
| ACCOUNT_HOPPING | Longest time-ordered chain depth (transfer hops) passing through the account in its cluster: 2 -> 5; 3 -> 10; 4 or more -> 15 |
| SHARED_IDENTIFIERS | Distinct exact shared identifiers (phone, device, UPI) connecting the entity to entities that belong to other originally separate cases: 1 -> 10; 2 -> 15; 3 or more -> 20. Weak links do not count |
| MULTIPLE_VICTIMS | Distinct victims paying the entity: 2 -> 5; 3 to 4 -> 10; 5 or more -> 15 |
| LINKED_COMPLAINTS | Complaints referencing the entity or its exact identifiers: 1 -> 3; 2 -> 6; 3 or more -> 10 |
| UNUSUAL_PATTERN | Inbound transfer count in any 24-hour window: 3 to 4 -> 6; 5 or more -> 10 |
| SUSPICIOUS_TIMING | At least 50% of outbound value leaves within `TIMING_WINDOW_MIN` (60) minutes of inbound, or at least 3 transactions between 00:00 and 05:00 local time -> 5; one of the two partial conditions -> 2 |
| FLAGGED_PROXIMITY | Within 1 hop of an entity carrying a flag (seeded synthetic flag or investigator flag) -> 10; within 2 hops -> 5 |
| CENTRALITY | Account in the top decile of betweenness within a cluster of at least 5 nodes -> 5 |
| MITIGATION | Subtract 5 each (max -15): (a) at least `BASELINE_DAYS` (14) days of regular activity before the first suspicious event; (b) inflows from at least 10 distinct counterparties without pass-through behaviour; (c) outflows not forwarded within 24 hours (funds retained) |

**Total:** `score = clamp(round(sum_of_factor_points * 100 / 110) + mitigation_points, 0, 100)` where mitigation points are zero or negative.

**Bands:** Low 0 to 24; Medium 25 to 49; High 50 to 74; Critical 75 to 100.

**Reproducibility:** identical inputs and configuration always produce identical score and breakdown. Weights live in a versioned configuration file.

### 15.3 Risk breakdown drawer layout

1. Header: entity label (masked), score, band, disclaimer.
2. Horizontal bars per factor: points / max.
3. Expandable rows: description, values used, evidence IDs (clickable).
4. Mitigating factors section.
5. Footer: computed at, configuration version, "How is this calculated?" link to the factor definitions.

---

## 16. Explainability Interface

### F-07 — Findings and Explanation Panel

| Item | Specification |
|---|---|
| Feature name | Findings and Explanation Panel |
| User problem | The investigator must see why the system believes something and be able to challenge it |
| Description | Standardised display of every finding, with evidence, reasoning, counter-evidence, confidence and review state |
| User interaction | Expand a finding; click evidence IDs to open details; hover to highlight the evidence nodes on the graph; filter findings by source and review state; open "Why related?" for an entity pair (T8); accept, reject, annotate (F-10) |
| Inputs | Findings from deterministic analysis, graph analysis and Nemotron tasks; evidence records |
| Processing | [DET] evidence validator and language guard; [NEM] generates findings and explanations |
| Outputs | Finding cards in the format below; count of withheld statements |
| Edge cases | All statements withheld (show "No validated findings. N statements withheld for invalid evidence." with the deterministic summary still shown); very many findings (grouped by hypothesis, sorted by confidence); finding referring to an evidence record later updated (marked "Evidence changed") |
| Acceptance criteria | AC-17 to AC-19 |
| Priority | MUST |

### 16.1 Standard finding card

| Field | Content | Rule |
|---|---|---|
| Finding ID | F-nnn within case | Software generated |
| Statement | One plain sentence framed as a potential relationship or hypothesis | Must pass language guard |
| Source type | Deterministic, Graph, Nemotron-live, Nemotron-cached | Always shown |
| Evidence | List of evidence IDs, each with a one-line description | At least one valid ID required |
| Reasoning | Short explanation connecting evidence to statement | Required |
| Counter-evidence / gaps | What weakens the finding or is missing | Required (may state "none identified") |
| Confidence | Low, Medium or High, with rationale | Required |
| Recommended next step | One concrete, human-executed action | Required |
| Review state | Pending, Accepted, Rejected, Needs more evidence | Default Pending |

### 16.2 Reference example (must be reproducible in the demo form)

> **Finding:** Accounts B and C may belong to the same fraud chain (potential relationship).
> **Evidence:** E-0012 (shared phone identifier), E-0019 (transfer within 7 minutes), E-0024 (common device), E-0027 (linked complaint), E-0031 (repeated transaction pattern).
> **Confidence:** Medium.
> **Recommended next step:** Review Account C's outgoing transactions.

### 16.3 Grounding guardrails

1. **Allowed-ID list:** every Nemotron prompt includes the exact set of permitted evidence IDs for the task.
2. **Structured output:** every task has a defined output schema (Section 25.4).
3. **Validator:** a finding is rejected if it cites an unknown ID, cites no ID, lacks required fields, or states a numeric value that does not match software values (amount, count, time gap).
4. **Withheld statements:** rejected statements are logged and counted; the UI shows the count but not the rejected text by default (Admin may view for debugging).
5. **Language guard:** statements containing prohibited terms (Appendix D) are rewritten by template or withheld.
6. **Uncertainty:** the model is instructed to answer "insufficient evidence" instead of guessing; such answers are shown as gaps.
7. **Provenance:** every AI element shows source type and the task and job ID.

### 16.4 "Why related?" explanation (T8, SHOULD)

Select two entities -> backend assembles the connecting exact and inferred links and paths -> Nemotron produces a plain-language explanation with the same evidence rules -> shown in a side panel.

---

## 17. Real-Time Detection Interface

### F-08 — Real-Time Event Detection (Prototype)

| Item | Specification |
|---|---|
| Feature name | Real-Time Event Detection (lightweight simulation) |
| User problem | Investigators need to see how a new event changes the picture without waiting for batch analysis |
| Description | A simulator replays held-out events through the same pipeline used for ingestion; the UI shows alerts, graph growth and re-scoring as they occur |
| User interaction | Simulator strip: Play, Pause, Step, Speed (1x, 5x, 20x), Reset; "Inject next event" button (MUST fallback); live toast and alert-feed entry; "Affected entities" list; graph animates new nodes and edges; optional "Run reasoning on this alert" |
| Inputs | Held-out event queue (6 transactions and 1 complaint in the demo dataset), pipeline configuration |
| Processing | Pipeline in Section 17.1. [DET] and [GRAPH] only up to alert; [NEM] optional afterwards |
| Outputs | Alert records; updated graph and scores; "affected entities" list; Nemotron status chip (Not requested, Queued, Running, Done, Unavailable, Cached) |
| Edge cases | Duplicate event (rejected with reason, idempotent by event ID); out-of-order timestamp (accepted; timeline re-sorted; alert text notes late arrival); invalid event (rejected, audit entry, UI notice); event that merges two clusters (cluster-merge alert R3); rapid repeated events (processed sequentially; queue indicator); Nemotron unavailable (alert still fires) |
| Acceptance criteria | AC-36 to AC-39 |
| Priority | MUST (inject next event with alert and graph update); SHOULD (continuous playback, speed, affected-entity list) |

### 17.1 Prototype real-time architecture

```
Event source (simulator queue, or POST /api/v1/events)
        |
        v
+------------------+   invalid   +---------------------------+
| 1. Validate      |------------>| Reject + audit + UI notice|
|    (schema, ID,  |             +---------------------------+
|     synthetic)   |
+--------+---------+
         | valid
         v
+------------------+
| 2. Persist +     |  assign evidence ID, normalise identifiers
|    normalise     |
+--------+---------+
         v
+------------------+
| 3. Feature       |  amounts, gaps vs prior inbound, counterparties,
|    extraction    |  shared-identifier lookups
+--------+---------+
         v
+------------------+
| 4. Graph update  |  add nodes/edges, update clusters (incremental)
+--------+---------+
         v
+------------------+
| 5. Risk evaluate |  re-score affected entities only
+--------+---------+
         v
+------------------+   rules R1..R6 (Section 18)
| 6. Alert         |--------------------> Alert feed + UI push
+--------+---------+
         | (optional, non-blocking)
         v
+------------------+
| 7. Nemotron      |  queued job; result marked pending/complete/unavailable
|    reasoning     |
+--------+---------+
         v
+------------------+
| 8. Investigator  |  acknowledge / dismiss / escalate / review
|    review        |
+------------------+
```

**Architecture rules**

- Steps 1 to 6 run in a single in-process pipeline call; no message broker is required.
- UI updates via polling every 2 seconds (MUST) or server-sent events (SHOULD).
- Step 7 never blocks steps 1 to 6; alerts must not depend on Nemotron.
- Steps are idempotent by event ID.
- Nemotron auto-queue (SHOULD) triggers only when the alert severity is Critical and rate limits allow; otherwise the investigator requests reasoning manually.
- The simulator is a developer/demo control and is clearly labelled "Simulation" on screen.

---

## 18. Alert Management

### F-09 — Alert Management

| Item | Specification |
|---|---|
| Feature name | Alert Management |
| User problem | Analysts must triage events quickly and not lose important ones |
| Description | Rule-triggered alerts with severity, explanation and a triage workflow |
| User interaction | Alert feed with filters (severity, status, rule, date); open alert detail; actions: Acknowledge, Dismiss (reason required), Escalate to case (creates or attaches to a case), Request reasoning; bulk acknowledge (SHOULD) |
| Inputs | Pipeline outputs, rule configuration |
| Processing | [DET] rules R1 to R6; severity mapping; deduplication window (same rule and entity within `ALERT_DEDUP_MIN` = 15 minutes is merged into one alert with a counter) |
| Outputs | Alert record: ID, created at, rule(s) fired, severity, affected entities, triggering evidence IDs, risk score before and after, status, handler, dispositions |
| Edge cases | Alert for entity already in a case (offer "Attach to case"); alert storm (deduplication and per-minute display cap with "N more"); dismissed alert re-fires with materially new evidence (new alert, linked to previous); alert on entity that later turns out weak-linked (retained; annotation allowed) |
| Acceptance criteria | AC-40, AC-41 |
| Priority | SHOULD (full triage); MUST (alert from injected event with explanation and escalate to case) |

### 18.1 Alert rules (deterministic)

| Rule | Name | Condition (defaults) | Base severity |
|---|---|---|---|
| R1 | Pass-through | Inbound transfer at least `ALERT_MIN_AMOUNT` (INR 10,000 in demo data) is forwarded at least `FORWARD_RATIO` within `PASS_THROUGH_WINDOW_MIN` | Warning |
| R2 | New victim payment to elevated account | A new victim pays an account whose band is High or Critical | Critical |
| R3 | Cluster merge | A new exact link connects two previously separate clusters | Critical |
| R4 | Fast cash-out | A withdrawal occurs within `TIMING_WINDOW_MIN` of an inflow of at least `ALERT_MIN_AMOUNT` | Warning |
| R5 | Band escalation | An entity's band rises by at least one level | Warning (Critical if new band is Critical) |
| R6 | Complaint touches known cluster | New complaint references an identifier already in a cluster | Info (Warning if cluster is High or above) |

### 18.2 Alert states

New -> Acknowledged -> (Escalated to case or Dismissed). Dismissed requires a reason from a list (False positive, Already handled, Insufficient evidence, Other with text).

### 18.3 Alert detail layout

Header (severity, rule names, time) -> "Why this fired" (conditions with actual values and evidence IDs) -> affected entities (clickable) -> risk before and after -> actions -> Nemotron status and result (if any).

---

## 19. Investigator Review Workflow

### F-10 — Review Workflow

| Item | Specification |
|---|---|
| Feature name | Investigator Review Workflow |
| User problem | The investigator must stay accountable and record decisions on AI and software conclusions |
| Description | Per-item review of findings, hypotheses, plan steps and inferred links; every decision recorded with reason and audit entry |
| User interaction | On each reviewable item: Accept, Reject (reason required), Needs more evidence (note required), Annotate; "Promote link" or "Demote link" for weak and inferred links; bulk accept is NOT allowed |
| Inputs | Reviewable items; investigator input |
| Processing | [DET] state machine; audit write; effect propagation (rejected findings are excluded from case summary; promoted links become cluster-forming and trigger cluster recomputation) |
| Outputs | Review record: item, previous state, new state, reason, reviewer, timestamp; updated case summary counts; audit event |
| Edge cases | Re-reviewing an item (allowed; history preserved); reviewing an item citing evidence that changed since generation (warning banner); conflicting reviews by two users (latest wins; both visible in history); rejecting a finding that supports a plan step (dependent steps flagged "Basis rejected") |
| Acceptance criteria | AC-42, AC-43 |
| Priority | MUST |

### 19.1 Reviewable item states

| Item | States |
|---|---|
| Finding / hypothesis | Pending, Accepted, Rejected, Needs more evidence |
| Plan step | Pending, Accepted, Declined, Done (investigator marks completed by their own action outside the system) |
| Inferred or weak link | Unreviewed, Promoted, Demoted |
| Alert | New, Acknowledged, Escalated, Dismissed |
| Case | Open, In review, Closed |

### 19.2 Human-in-the-loop rules

- FraudMesh performs no external actions. Plan steps are suggestions for the investigator to perform outside the system.
- A "Done" mark records only that the investigator did the step; the system does not verify or execute it.
- The UI contains no control labelled freeze, seize, block, report or arrest, and the API has no such endpoints.
- Case closure requires a closing note. Closure labels: "Review complete" or "Review complete, escalated for external review (record only)". The second label is a recorded note; FraudMesh sends nothing.

---

## 20. Case Creation and Management

### F-11 — Case Management

| Item | Specification |
|---|---|
| Feature name | Case Management |
| User problem | Investigators need a persistent container for each investigation |
| Description | Create cases from a cluster, an alert or a selected set of entities; manage status, notes and history |
| User interaction | "Create case" from graph selection, cluster badge or alert; case list with filters (status, priority band, owner, date); open case; edit title; add note; change status; attach entities; refresh subgraph; close with note |
| Inputs | Seed entities or cluster ID or alert ID; investigator input |
| Processing | [DET]+[GRAPH] case subgraph extraction (seed entities plus exact and promoted links up to `CASE_MAX_HOPS` = 3 hops, capped at `CASE_MAX_NODES` = 300), evidence collection, snapshot of the cluster at creation, owner assignment |
| Outputs | Case record: ID (CASE-nnn), title, status, owner, created at, seed, subgraph snapshot ID, evidence IDs, priority band at creation and now, review summary, notes, history |
| Edge cases | Seed already in an open case (offer attach or open existing); subgraph exceeds cap (truncate by risk and recency, show "Truncated" notice with count); entity deleted from dataset on reset (cases are cleared on reset and the user is told); concurrent creation (unique IDs); empty seed (validation error) |
| Acceptance criteria | AC-32, AC-33 |
| Priority | MUST |

**Case fields**

| Field | Description |
|---|---|
| id | CASE-001 etc. |
| title | Editable; default "Cluster {id}: {top entity label}" |
| status | Open, In review, Closed |
| owner | User ID |
| seed | Entities, cluster or alert that started the case |
| snapshot_version / refreshed_at | Subgraph version and last refresh time |
| priority_band | Highest member band, with computed-at time |
| evidence_ids | Set of evidence in scope |
| reasoning_state | Not run, Running, Complete, Unavailable, Cached, Possibly out of date |
| notes, history | Append-only entries |

---

## 21. Search and Filter Requirements

### F-12 — Search and Filtering

| Item | Specification |
|---|---|
| Feature name | Search and Filtering |
| User problem | Investigators must locate any entity or record from any identifier |
| Description | Global search bar and contextual filters |
| User interaction | Type an identifier or ID; results grouped by type; choose a result to open the entity page or focus it on the graph; contextual filters in graph, evidence, alerts and case list |
| Inputs | Query string; filters |
| Processing | [DET] normalisation of the query (phone formats, case, spacing) then exact and prefix matching on normalised and masked-display forms; no fuzzy ML search required |
| Outputs | Result list with type, label, masked identifier, cluster, band; "no results" message |
| Edge cases | Phone typed in a different format (normalisation finds it); partial identifier (prefix, minimum 4 characters); same identifier appearing as phone in one record and in text in another (both listed); very broad query (paginate, cap at 200); query containing injection-like text (treated as literal) |
| Acceptance criteria | AC-44, AC-45 |
| Priority | MUST (global identifier search); SHOULD (contextual filters beyond the graph) |

**Searchable keys:** evidence ID, entity ID, account number (full or last 4), UPI ID, phone number (any format), device ID, complaint ID, case ID, alert ID.

---

## 22. Data Ingestion Requirements

### F-13 — Evidence Ingestion

| Item | Specification |
|---|---|
| Feature name | Evidence Ingestion |
| User problem | Fragmented records must become a consistent, citable evidence base |
| Description | Loads synthetic files into the database, validating, normalising and assigning evidence IDs |
| User interaction | Admin command or UI "Load dataset" (SHOULD); Investigator sees only results (dataset name, counts, rejected count); rejected-record report viewable by Admin |
| Inputs | Dataset package: JSON or CSV files (format in Section 22.1) with `synthetic: true` in the manifest |
| Processing | [DET]: manifest check -> schema validation -> normalisation -> duplicate detection -> ID assignment -> persistence -> entity and exact-link extraction -> graph build trigger |
| Outputs | Evidence records with IDs; ingestion report (counts accepted, rejected, reasons); entities and links |
| Edge cases | Missing manifest or `synthetic` flag (refuse entire dataset); malformed record (reject that record, continue); duplicate record (idempotent; same ID not reassigned); unknown field (reject record when strict mode on, default on); timestamp in future relative to dataset end (accept with warning); mixed time zones (normalise to UTC); oversize file (reject over `MAX_FILE_MB` = 10); character encoding errors (reject record); narrative containing very long text (truncate at `MAX_NARRATIVE_CHARS` = 8,000 for prompts, store full) |
| Acceptance criteria | AC-01 to AC-06 |
| Priority | MUST |

### 22.1 Dataset package files

| File | Contents |
|---|---|
| manifest.json | dataset name, version, seed, `synthetic: true`, generator version, counts, base date |
| victims.json | victim ID, synthetic name, case label, source account reference (masked synthetic) |
| accounts.json | account ID, bank (fictional), holder entity ID, account number (synthetic), open date |
| upi.json | UPI ID, mapped account ID |
| phones.json | phone ID, number (synthetic format), holder entity (if any), label |
| devices.json | device ID, fingerprint label, device log entries (account or login, timestamp) |
| transactions.json | transaction ID, from account, to account, amount (INR), timestamp, channel, reference text |
| withdrawals.json | withdrawal ID, account, amount, timestamp, location label (synthetic), channel |
| complaints.json | complaint ID, victim ID, filed at, narrative text |
| communications.json | communication ID, type (call log summary or message text), parties (phone IDs), timestamp, text or summary |
| events_heldout.json | queued events for the simulator |
| flags.json | seeded synthetic flags on entities (for FLAGGED_PROXIMITY) |
| benign_identifiers.json | allow-list of known benign identifiers (for example a public helpline) that must not create links |

`ground_truth.json` is generated separately and is never loaded by the application at runtime (Section 23).

### 22.2 Normalisation rules

| Field | Rule |
|---|---|
| Phone | Strip spaces, hyphens, parentheses; convert "0091", "+91", leading "0" forms to a canonical "+91XXXXXXXXXX"; keep original string in the raw field |
| Account number | Digits only; mask for display (last 4) |
| UPI ID | Lowercase; trim |
| Timestamps | Parse to ISO 8601 UTC; store original and parsed |
| Amount | Decimal with two places; currency INR only; reject negative |
| Names | Display-only; never used for matching in MVP |

### 22.3 Evidence record (logical)

| Field | Description |
|---|---|
| evidence_id | E-0001 style; stable; software assigned |
| type | Transaction, Withdrawal, Complaint, Communication, Device log, Account record, Mapping |
| source_file / source_row | Provenance |
| timestamp | UTC; may be null for undated evidence |
| content | Normalised structured fields and raw text |
| entities | Linked entity IDs |
| ingested_at / dataset_id | Provenance |

### 22.4 Extraction requirements

- **Structured extraction [DET]:** entities and links from structured fields (account to UPI, account to device, transfer edges, withdrawals, complaint to victim, phone to complaint where structured).
- **Narrative extraction [NEM] (T1):** claimed identifiers, amounts, times, narrative events, mentioned names or roles, and uncertainty from complaint and communication text.
- **Confirmation [DET]:** every identifier Nemotron extracts is normalised and matched exactly against the entity table; matches create Inferred links (confirmed); non-matches create new "unconfirmed mention" records that do not form clusters.

---

## 23. Synthetic-Data Requirements

### F-14 — Synthetic Data Generator and Ground Truth

| Item | Specification |
|---|---|
| Feature name | Synthetic Data Generator and Ground Truth |
| User problem | The prototype needs realistic yet fully safe data with a known answer for evaluation |
| Description | A seeded, reproducible generator that produces the dataset package (Section 22.1), the held-out event queue and a separate ground-truth file |
| User interaction | Developer/admin command: generate with a seed; reset-and-seed command (one command restores the demo state) |
| Inputs | Seed value; scenario configuration file |
| Processing | [DET] generation by script. Complaint narrative text is produced from reviewed templates with controlled variation. Optionally, narrative drafts may be produced offline by an LLM and saved as static fixtures; the application never generates data live |
| Outputs | Dataset package; `ground_truth.json`; generation report with counts |
| Edge cases | Same seed (identical output byte for byte); seed change (valid, structure preserved, counts preserved); generator run without scenario config (default scenario); output directory contains data not flagged synthetic (abort) |
| Acceptance criteria | AC-01, AC-02, AC-03 |
| Priority | MUST |

### 23.1 Synthetic-data safety rules

- All names, numbers and identifiers are fabricated and use obviously synthetic patterns: phone numbers from a reserved fictional pattern (for example `+91 90000 0xxxx`), fictional bank names ("Bank Alpha", "Bank Beta", "Bank Gamma"), account numbers in a fictional prefix range, device IDs prefixed `DEV-`.
- No real person, institution or number is used.
- Dataset manifest carries `synthetic: true`; the application refuses anything else.
- Demo data lives in `data/demo/`; any authorised data would live in a separate directory and database; the application never merges them.
- Complaint text is neutral and non-graphic.

### 23.2 Dataset targets

| Element | Count | Notes |
|---|---|---|
| Victims | 20 | V01 to V20; 5 per case |
| Cases (apparently separate) | 4 | Cases A, B, C, D |
| Investigated bank accounts | 8 | M1 to M7 (network) plus D1 (decoy) |
| Victim-side source accounts | 20 | Referenced only as masked source references; not counted among the 8 |
| Phone numbers | 6 | P1 to P5 network-related, P6 decoy |
| UPI IDs | 6 | Mapped to M1, M2, M3, M4, M7, D1 |
| Devices | 5 | DEV-1 to DEV-5 |
| Transactions | 56 | Including 6 withdrawals counted as transactions |
| Complaints | 13 | C-01 to C-13 (C-13 held out) |
| Communications | 9 | Call-log summaries and message texts |
| Planted contradictions | 4 | See 23.5 |
| Decoys | 3 | See 23.6 |
| Adversarial text samples | 1 | C-07 (prompt-injection attempt, harmless) |
| Held-out events | 7 | 6 transactions plus complaint C-13 |
| Time span | About 21 days, with a dense final burst (base date configurable) | |

### 23.3 Hidden network structure

```
Cases A, B, C, D (5 victims each, reported as separate incidents)

 Case A victims -> M1 --+
 Case B victims -> M2 --+--(shared DEV-1)--+
 Case C victims -> M3 --+                  |
 Case D victims -> M3 / M2 ...             |
                         |                 |
            Layer-1 pass-through accounts M1, M2, M3
                         |  (forwarded within minutes)
                         v
            Layer-2 accounts M4, M5
                         |
                         v
            Collector account M6
                         |
                         v
            Cash-out account M7 --> Withdrawals W1..W6 (synthetic locations)

 Phones: P1 (Case A caller), P2 (Case B caller), P3 (Case C caller), P4 (Case D caller)
         P5 = callback number in Case B and Case D narratives (different formats)
         P6 = decoy (shared family number in two unrelated complaints)
 Devices: DEV-1 -> M1, M2, M7 login   DEV-2 -> M3, M4   DEV-3 -> M5
          DEV-4 -> M6                 DEV-5 -> D1 only (decoy)
```

Case D victims pay M3 (V16 to V19 early) and M2 (V20, held out); the generator may vary which L1 account receives which victim so long as the target counts and the discoverability table below hold.

### 23.4 Transaction allocation (56)

| Block | Range | Count | Description |
|---|---|---|---|
| Victim to layer-1 | T-001 to T-020 | 20 | One payment per victim (INR 8,000 to 95,000), spread over about 14 days; T-020 held out |
| Layer-1 to layer-2 | T-021 to T-029 | 9 | Forwarded within 4 to 25 minutes, 82% to 98% of inbound |
| Layer-2 to collector M6 | T-030 to T-035 | 6 | Within 10 to 40 minutes; T-034, T-035 held out |
| Collector M6 to cash-out M7 | T-036 to T-039 | 4 | Batches; T-038, T-039 held out |
| Withdrawals from M7 | T-040 to T-045 | 6 | ATM or branch (synthetic location labels) within 60 minutes of M7 inflow; T-045 held out |
| Decoy D1 normal activity | T-046 to T-054 | 9 | Many small inflows from many counterparties over the whole period; retained funds; stable history |
| Coincidence pair | T-055 to T-056 | 2 | Two unrelated transfers with identical amount and near-identical time, not network-related |

### 23.5 Planted contradictions (4)

| ID | Contradiction | Complaint | Ledger or other source | Expected handling |
|---|---|---|---|---|
| X1 | Amount transposition | States INR 48,000 | T-0xx shows INR 84,000 | Software candidate (amount mismatch); Nemotron: likely transposition, material to total-loss figure |
| X2 | Time inconsistency | "After lunch" (about 14:10) | Transaction at 23:52 same date | Software candidate (time difference > threshold); Nemotron: narrative time unreliable or second transfer; affects chronology |
| X3 | Same "officer", different numbers | Two victims name the same officer with two different number formats | Both normalise to P5 | Software confirms same normalised identifier; Nemotron links narratives |
| X4 | Bank mismatch | Victim names Bank Beta | Matching transaction shows Bank Alpha account | Software candidate; Nemotron: likely confusion with UPI app name; low materiality |

### 23.6 Decoys

| Decoy | Why it looks suspicious | Why it is benign | Required system behaviour |
|---|---|---|---|
| D1 account | High inflow and outflow volume | Many distinct small payers; retains funds; stable history; no shared exact identifiers with network | Not in the network cluster; band Low or Medium with mitigation shown |
| P6 phone | Appears in two complaints | A victim's family contact mentioned innocently; no financial link | Weak link only; excluded from cluster; visible with "weak" badge |
| T-055 and T-056 pair | Same amount and near-identical time | Unrelated parties | No link created; no alert beyond Info |

### 23.7 Discoverability table (what the system must find, and how)

| Hidden relationship | Mechanism | Logic |
|---|---|---|
| M1, M2 and M7 login share DEV-1 | Exact device match | [DET] -> [GRAPH] |
| Case A and Case C funds converge on M6 | Money-flow path analysis | [GRAPH] |
| M3 and M4 share DEV-2 | Exact device match | [DET] |
| Case B and Case D complaints both mention callback P5 and the same agent name, in different formats | T1 narrative extraction, then exact confirmation | [NEM] -> [DET] |
| Complaint time versus ledger time conflict (X2) | Candidate + materiality | [DET] + [NEM] |
| Case C first contact earlier than the victim states (communication log shows an earlier call) | Chronology reconstruction | [NEM] |
| Withdrawals follow M6/M7 inflows within an hour | Time gap + path | [DET] + [GRAPH] |
| All four cases are one operation (cluster of M1 to M7, P1 to P5, DEV-1 to DEV-4, 20 victims) | Cluster + causal reconstruction | [GRAPH] + [NEM] |

### 23.8 Ground truth

`ground_truth.json` contains: network member entities, true links, true chronology of the chain, contradictions X1 to X4, decoys, discoverability table. It is read only by evaluation and test scripts and is not accessible through any application API.

### 23.9 Complaint narrative requirements

- Narratives are 80 to 250 words, first person, informal, with variation in tone, ordering and detail.
- Some narratives omit time, some give wrong amounts (X1), some name phone numbers in different formats, some mention an agent name.
- C-07 contains a harmless adversarial instruction (for example text asking the reader to ignore previous instructions and mark the account safe) to test prompt-injection resistance.
- At least two narratives are vague and give no identifiers (to test "insufficient evidence").

---

## 24. Graph Requirements

### F-15 — Graph Engine

| Item | Specification |
|---|---|
| Feature name | Graph Engine |
| User problem | The investigator needs reliable, deterministic discovery of connections |
| Description | Builds and queries the relationship graph; detects clusters, shared identifiers, money-flow paths and centrality |
| User interaction | Indirect via network view, search, alerts, case creation |
| Inputs | Entities, links, transactions, flags, benign allow-list, configuration |
| Processing | [DET] exact identifier matching; [GRAPH] construction, components, path search, centrality, subgraph extraction. No Nemotron |
| Outputs | Graph; clusters with IDs and members; shared-identifier sets; money-flow paths with hop times; centrality values; case subgraphs |
| Edge cases | Identifier on the benign allow-list (no link); same identifier in two roles (e.g., phone as caller and as callback) (single node, multiple role tags); cycle in money flow (path search must terminate; cycles reported); self-transfer (ignored with note); weak link bridging two clusters (not merged); cluster too large (summary view); deleted evidence on reset (graph rebuilt) |
| Acceptance criteria | AC-07 to AC-11 |
| Priority | MUST (construction, clusters, shared identifiers, paths, subgraph); SHOULD (incremental update, centrality) |

### 24.1 Graph model

- **Nodes:** Victim, Person/Entity, Bank Account, UPI ID, Phone Number, Device, Withdrawal, Complaint, Incident; Transactions as edges (expandable to nodes).
- **Edges:** relationships in Section 12.2, each with timestamp, source, evidence ID, confidence/strength, amount where relevant.
- **Identity:** nodes keyed by normalised identifier; the same normalised identifier is one node.

### 24.2 Link strength and cluster rules

| Strength | Created by | Forms clusters |
|---|---|---|
| Exact | Deterministic exact match or recorded transfer | Yes |
| Inferred (confirmed) | Nemotron proposal confirmed by exact normalised match | Yes |
| Inferred (unconfirmed) | Nemotron proposal without exact confirmation | No, until promoted |
| Weak | Deterministic heuristics (for example identifier shared between two unrelated complaints without any financial link) | No, until promoted |

### 24.3 Required graph algorithms

| Algorithm | Purpose | Priority |
|---|---|---|
| Connected components over cluster-forming links | Cluster identification | MUST |
| Time-ordered path search over TRANSFERRED_TO edges (each hop timestamp not earlier than the previous inbound) | Money-flow chains | MUST |
| Shared identifier grouping | Common phone, device, UPI across cases | MUST |
| Pass-through detection per account | Feeds risk and alerts | MUST |
| Fan-in and fan-out counts | Collector and distributor indicators | MUST |
| Betweenness centrality | Hub indication | SHOULD |
| Incremental update | Real-time | SHOULD |
| Bounded neighbourhood extraction | Case subgraph | MUST |

### 24.4 Over-merging prevention

1. Allow-list of benign identifiers produces no links.
2. Weak and unconfirmed links never merge clusters automatically.
3. Money-flow paths require time consistency.
4. A node connected to more than `HUB_BENIGN_DEGREE` (default 25) distinct unrelated clusters through the same identifier type is flagged "high-degree identifier: review before merging" and not auto-merged.

---

## 25. Nemotron Reasoning Requirements

### 25.1 What Nemotron MUST do

| Task | Description | Priority |
|---|---|---|
| T1 Complaint interpretation | Turn unstructured complaint or communication text into structured claims with uncertainty | MUST |
| T2 Cross-evidence reasoning | Propose candidate relationships across fragmented evidence in a case subgraph | MUST |
| T3 Contradiction resolution | Judge materiality of software-detected conflicts and their effect on chronology | SHOULD |
| T4 Chronology reconstruction | Produce a plausible order of events where times are missing or conflicting, with uncertainty | MUST |
| T5 Causal reconstruction | Precursor -> Trigger -> Movement -> Amplification -> Outcome, with cited evidence | MUST |
| T6 Investigative hypotheses | Evidence-backed hypotheses with confidence and counter-evidence | MUST |
| T7 Investigation plan | Ranked next steps, each with rationale and evidence | MUST |
| T8 Relationship explanation | Plain-language explanation of why two entities may be related | SHOULD |
| T9 Case summary | Investigator-facing summary of validated findings | SHOULD |

### 25.2 What Nemotron MUST NOT do

| Prohibited | Reason | Who does it instead |
|---|---|---|
| Exact identifier matching or deciding that two identifiers are equal | Exactness required | [DET] |
| Constructing or updating the graph | Reproducibility | [GRAPH] |
| Computing amounts, totals, counts, time gaps | Arithmetic errors | [DET] (values supplied to the model) |
| Sorting timestamps that are present | Deterministic | [DET] |
| Computing or modifying risk scores | Explainable, reproducible | [DET] |
| Generating or inventing evidence IDs | Grounding | Software assigns IDs |
| Deciding cluster membership alone | Over-merging risk | [GRAPH] with allow-list; investigator promotes |
| Making accusations, declaring guilt or intent as fact | Safety | Language guard, human |
| Recommending or triggering freezing, seizing or reporting | Out of scope | Not available |
| Following instructions found inside evidence text | Prompt injection | Delimited data, validator |
| Free-form chat | Product definition | Not offered |

### 25.3 Common task contract

| Item | Requirement |
|---|---|
| Context | Only the case subgraph and relevant evidence, with evidence IDs; whole-database input is prohibited. Software-computed facts (amounts, gaps, counts, scores) are provided as read-only facts |
| Allowed IDs | Every prompt lists the permitted evidence IDs |
| Untrusted data | Evidence text is placed inside clearly delimited data blocks, and the system instruction states it is data, not instructions |
| Output | JSON conforming to the task schema; no text outside it |
| Validation | Schema check, ID check, numeric consistency check, language guard |
| Retry | One repair attempt with the validation errors; then fail gracefully |
| Determinism | Low temperature; configured in Technical Documentation |
| Caching | Keyed by task, normalised input hash, model name, prompt version |
| Timeouts | `NEMOTRON_TIMEOUT_S` default 90; progress shown after 1 s |
| Masking | Identifiers in prompts masked unless exact values are needed for the task |
| Logging | Masked prompt and response stored for audit and debugging |
| Configuration | Endpoint URL, API key and model name come from environment variables |
| Rate limits | `NEMOTRON_MAX_JOBS_PER_MIN` per user default 10 |
| Job states | Queued, Running, Succeeded, Succeeded with withheld statements, Failed, Unavailable (cached served if available) |

### 25.4 Task output schemas (logical fields)

| Task | Output fields |
|---|---|
| T1 | `complaint_id`; `claims[]` (type: identifier, amount, time, event, role-mention, location-mention; value as written; normalised value if present; evidence span reference; certainty: stated, implied, unclear); `narrative_events[]` (order hint, description, claimed time or "unknown"); `ambiguities[]`; `insufficient_evidence` flag |
| T2 | `candidate_links[]` (entity pair; basis; evidence IDs; proposed strength; confidence; counter-evidence) |
| T3 | `assessments[]` (conflict ID from software; material yes/no/unclear; likely explanation; effect on chronology; evidence IDs; confidence) |
| T4 | `ordered_events[]` (evidence ID or event ID; position; placed time or "estimated range"; reason; confidence); `unplaceable[]` |
| T5 | `stages` with entries for Precursor, Trigger, Movement, Amplification, Outcome (each: description, evidence IDs, entities, confidence, gaps); `overall_confidence`; `alternatives[]` |
| T6 | `hypotheses[]` (statement; evidence IDs; reasoning; counter-evidence; confidence; next step) |
| T7 | `plan_steps[]` (rank; action phrased for a human; rationale; evidence IDs; linked hypothesis; expected information gain; priority) |
| T8 | `explanation`; `connecting_evidence[]`; `confidence`; `gaps` |
| T9 | `summary`; `key_findings[]` (reference to validated findings only); `open_questions[]` |

### 25.5 Causal reconstruction framework

| Stage | Meaning in FraudMesh | Typical demo evidence |
|---|---|---|
| Precursor | Contact or setup preceding losses | Communication log entries; early calls from reported-caller phones |
| Trigger | The event that induces the victim to transfer | Victim narrative of the call or message and the first payment |
| Movement | Rapid transfers across pass-through accounts | Transfer chain with short gaps |
| Amplification | Additional victims or accounts joining; cross-case convergence | Collector account receiving from multiple cases |
| Outcome | Cash-out or dispersal | Withdrawals |

Output must state gaps where a stage lacks evidence rather than invent a bridge.

### F-16 — Complaint Interpretation (T1)

| Item | Specification |
|---|---|
| Feature name | Complaint Interpretation |
| User problem | Narratives hold key identifiers and events that structured fields lack, but reading them all is slow |
| Description | Nemotron converts each complaint or communication into structured claims; software confirms identifiers |
| User interaction | In Evidence detail: "Interpretation" tab with extracted claims side by side with the original text and confirmation status; "Re-interpret" (rate limited) |
| Inputs | One narrative (within `MAX_NARRATIVE_CHARS`), allowed entity list for confirmation, schema |
| Processing | [NEM] T1; [DET] normalisation and exact matching of extracted identifiers; validator |
| Outputs | Claims with certainty; confirmation status (Confirmed against entity X, Unconfirmed mention, Conflicts with record Y); ambiguity list |
| Edge cases | Vague narrative (insufficient-evidence flag); injection text (ignored; audit note "instruction-like text detected" shown); non-English fragments (extract what is clear, flag the rest); identifier with typo (flagged unconfirmed, never auto-corrected); more than 8,000 characters (truncate for model with notice) |
| Acceptance criteria | AC-46, AC-47 |
| Priority | MUST |

### F-17 — Chronology and Causal Reconstruction (T2, T4, T5)

| Item | Specification |
|---|---|
| Feature name | Chronology and Causal Reconstruction |
| User problem | The investigator must understand the order of events and how a fraud chain unfolded across fragments |
| Description | Nemotron proposes cross-evidence relationships, reconstructs plausible chronology where evidence conflicts or is missing, and produces a staged causal chain |
| User interaction | "Run reasoning" in the case; progress panel; results appear in Timeline (reconstructed order), Network (chain highlight), Findings (causal chain) |
| Inputs | Case subgraph, ordered evidence, software facts (gaps, totals), conflict candidates, T1 results |
| Processing | [DET] prepares ordered evidence, gaps and facts; [NEM] T2, T4, T5; [DET] validation; [GRAPH] chain mapped to actual paths for highlighting (chain steps must correspond to real graph edges or are shown as "inferred step") |
| Outputs | Candidate links; reconstructed order; causal chain with five stages; confidence; gaps; alternatives |
| Edge cases | Evidence insufficient for a stage (stage marked "Not established"); T5 describing a transfer not in the graph (rejected as unsupported); contradiction with deterministic path (deterministic data wins; note shown); conflicting alternatives (both shown with confidence); model returns different chain on re-run (variation noted; cached result retained as authoritative until the investigator re-runs) |
| Acceptance criteria | AC-48 to AC-51 |
| Priority | MUST (T2, T4, T5 minimum); SHOULD (alternatives) |

### F-18 — Hypotheses and Investigation Plan (T6, T7)

| Item | Specification |
|---|---|
| Feature name | Hypotheses and Investigation Plan |
| User problem | After analysis, the investigator needs prioritised next steps defensible by evidence |
| Description | Nemotron generates ranked hypotheses and an investigation plan; each item links to evidence and is subject to review |
| User interaction | Plan tab: ranked steps; expand for rationale and evidence; Accept, Decline, Mark done (F-10); "Regenerate with current review state" (SHOULD) |
| Inputs | Validated findings, review state, gaps, software facts |
| Processing | [NEM] T6 and T7; [DET] validation; ranking displayed in the order returned but investigators may reorder (reorder recorded) |
| Outputs | Hypotheses with confidence; plan steps with rank, action, rationale, evidence, linked hypothesis |
| Edge cases | Step suggests external enforcement action (guard blocks and logs); all hypotheses rejected by the investigator (plan shows "No active hypotheses; consider new evidence"); step referencing a rejected finding (marked "Basis rejected"); duplicate steps (merged by exact text match) |
| Acceptance criteria | AC-52, AC-53 |
| Priority | MUST (T6, T7); SHOULD (regeneration) |

### F-19 — Contradiction Detection (T3)

| Item | Specification |
|---|---|
| Feature name | Contradiction Detection |
| User problem | Narratives often conflict with ledgers or with each other, which can mislead a reconstruction |
| Description | Software generates candidate conflicts; Nemotron judges materiality and effect on chronology |
| User interaction | Contradictions tab: list with side-by-side sources, software rule that triggered, Nemotron assessment, accept or dismiss; conflict markers appear on the timeline |
| Inputs | T1 claims vs structured records; narrative vs narrative |
| Processing | [DET] candidate rules: amount mismatch (difference above `AMOUNT_TOLERANCE_PCT` = 1), time mismatch (more than `TIME_TOLERANCE_MIN` = 120), bank mismatch, identifier normalising to same value in different narrative forms, narrative event order versus communication timestamps; [NEM] T3 |
| Outputs | Conflict records with IDs, sources and assessments |
| Edge cases | Many low-value candidates (sorted by materiality; dismissed ones hidden); candidate with only one source (not a conflict; shown as "unverified claim"); assessment disputes software values (software values win; assessment flagged) |
| Acceptance criteria | AC-54 |
| Priority | SHOULD (all four planted contradictions detected; minimum three) |

---

## 26. API Requirements

### 26.1 General rules

| Rule | Requirement |
|---|---|
| Style | REST over HTTP, JSON bodies, base path `/api/v1` |
| Authentication | Bearer token on all endpoints except `POST /auth/login` and `GET /health` |
| Authorization | Role checked server-side per endpoint (matrix in Section 27) |
| Validation | Schema validation on all inputs; unknown fields rejected; maximum body size 1 MB (ingestion files via separate limit) |
| Pagination | `limit` default 50, maximum 200; cursor-based; responses include `next_cursor` |
| Error envelope | `{ "error": { "code", "message", "request_id", "details" } }` with no stack traces or internal paths |
| Idempotency | Event and ingestion endpoints idempotent by client event ID or dataset ID |
| Time | ISO 8601 UTC in all payloads |
| Masking | Responses return masked identifiers unless an unmask action is called and permitted |
| Provenance | AI-derived objects include `source_type`, `job_id`, `model`, `prompt_version`, `cached` |
| Rate limiting | Login 5 attempts per minute per client; reasoning job creation per `NEMOTRON_MAX_JOBS_PER_MIN` |
| CORS | Restricted to configured origins |
| Versioning | Path version; breaking changes require new version |
| No dangerous endpoints | There are no endpoints to freeze, block, seize, report or delete evidence |

### 26.2 Endpoint catalogue

| Method | Path | Role | Purpose | Priority |
|---|---|---|---|---|
| POST | /auth/login | Public | Obtain session token | MUST |
| POST | /auth/logout | Any | End session | MUST |
| GET | /auth/me | Any | Current user and role | MUST |
| GET | /health | Public | Liveness, dataset loaded flag, Nemotron reachability | MUST |
| GET | /meta/limitations | Any | Limitations and safeguards text | MUST |
| POST | /datasets/load | Admin | Load a dataset package (synthetic only) | MUST |
| POST | /datasets/reset | Admin | Reset and reseed demo state | MUST |
| GET | /datasets/current | Any | Dataset name, counts, flags | MUST |
| GET | /dashboard/summary | Any | KPI tiles, priority list | MUST |
| GET | /evidence | Any | List and filter evidence | MUST |
| GET | /evidence/{id} | Any | Evidence detail with citations | MUST |
| POST | /evidence/{id}/unmask | Investigator | Reveal unmasked fields (reason required, audit logged) | MUST |
| GET | /entities | Any | List and filter entities | MUST |
| GET | /entities/{id} | Any | Entity detail, links, score | MUST |
| GET | /search | Any | Global identifier search | MUST |
| GET | /graph | Any | Graph slice by filters (cluster, case, types, time) | MUST |
| GET | /graph/clusters | Any | Cluster list with bands | MUST |
| GET | /graph/paths | Any | Money-flow paths between nodes | MUST |
| POST | /links/{id}/promote | Investigator | Promote weak or inferred link | MUST |
| POST | /links/{id}/demote | Investigator | Demote link | MUST |
| GET | /risk/{entity_id} | Any | Risk breakdown | MUST |
| GET | /cases | Any | List cases | MUST |
| POST | /cases | Investigator | Create case from seed | MUST |
| GET | /cases/{id} | Any | Case detail | MUST |
| PATCH | /cases/{id} | Investigator | Update title or status; closing note | MUST |
| POST | /cases/{id}/refresh | Investigator | Refresh subgraph | MUST |
| POST | /cases/{id}/notes | Investigator | Add note | MUST |
| GET | /cases/{id}/timeline | Any | Ordered events, gaps, conflicts | MUST |
| POST | /cases/{id}/reasoning | Investigator | Start reasoning job(s) (live or cached mode) | MUST |
| GET | /reasoning/jobs/{job_id} | Any | Job status and result | MUST |
| GET | /cases/{id}/findings | Any | Findings with review state | MUST |
| POST | /findings/{id}/review | Investigator | Accept, reject, needs evidence, annotate | MUST |
| GET | /cases/{id}/plan | Any | Plan steps | MUST |
| POST | /plan-steps/{id}/review | Investigator | Accept, decline, mark done | MUST |
| GET | /cases/{id}/contradictions | Any | Conflicts and assessments | SHOULD |
| POST | /events | Investigator | Submit a simulated event (validated) | MUST (fallback inject) |
| POST | /simulator/{action} | Investigator | play, pause, step, reset | SHOULD |
| GET | /alerts | Any | List alerts | MUST |
| GET | /alerts/{id} | Any | Alert detail | MUST |
| POST | /alerts/{id}/action | Investigator | Acknowledge, dismiss, escalate | SHOULD (MUST for escalate) |
| GET | /audit | Admin | Audit log with filters | MUST |
| GET | /users | Admin | List demo users | SHOULD |
| POST | /users | Admin | Create demo user | NICE |
| GET | /settings/mode | Any | Reasoning mode (live or cached) | MUST |
| PUT | /settings/mode | Investigator | Set reasoning mode | MUST |

### 26.3 Reasoning job lifecycle

`POST /cases/{id}/reasoning` returns `202` with `job_id`; the client polls `GET /reasoning/jobs/{job_id}` every 2 s; result contains per-task status (T1, T2, T4, T5, T6, T7, ...), validated outputs, withheld count, mode, and timing.

---

## 27. Authentication and Authorization

### F-20 — Authentication and Role-Based Access

| Item | Specification |
|---|---|
| Feature name | Authentication and Role-Based Access |
| User problem | Actions must be attributable to individuals and access limited by role |
| Description | Username and password login, expiring sessions, two roles |
| User interaction | Login form; logout; session expiry notice; role-appropriate menus |
| Inputs | Credentials |
| Processing | [DET] password hashing with a strong adaptive algorithm, token issue with expiry (`SESSION_MINUTES` default 60), lockout after 5 failed attempts for 5 minutes, server-side role checks |
| Outputs | Session token; user profile; 401 or 403 errors as appropriate |
| Edge cases | Expired token (401, UI returns to login preserving the target page); wrong password (generic message, no user enumeration); locked account (message with remaining time); role changed during session (applies on next request); token reuse after logout (rejected); demo credentials (created by setup script from environment variables, never committed) |
| Acceptance criteria | AC-55 to AC-58 |
| Priority | MUST |

### 27.1 Roles

| Role | Purpose |
|---|---|
| Investigator | Work cases, review findings, triage alerts, run reasoning, inject events |
| Admin | Everything an Investigator can read; manage users and datasets; view audit log; cannot review findings on behalf of an Investigator (no review actions) |

Supervisor and Compliance personas use the Admin role in the MVP.

### 27.2 Permission matrix

| Action | Investigator | Admin |
|---|---|---|
| Log in, view dashboard, graph, evidence, cases (read) | Yes | Yes |
| Create and update cases, notes | Yes | No |
| Run reasoning, switch reasoning mode | Yes | Read mode only |
| Review findings and plan steps; promote or demote links | Yes | No |
| Triage alerts | Yes | No |
| Inject or play events | Yes | No |
| Unmask identifiers | Yes (reason required) | Yes (reason required) |
| View audit log | Own actions only (SHOULD) | All |
| Load or reset dataset | No | Yes |
| Manage users | No | Yes |
| View withheld AI statements (debug) | No | Yes |

---

## 28. Privacy and Security Requirements

### F-22 — PII Masking and Data Protection

| Item | Specification |
|---|---|
| Feature name | PII Masking and Data Protection |
| User problem | Investigators should see only the identifiers they need, and the system should model good handling of sensitive data even with synthetic data |
| Description | Default masking of phone numbers, account numbers, UPI IDs and names; logged unmasking; data minimisation across API, logs and prompts |
| User interaction | Masked values display (for example `+91-XXXXX-XX123`, `XXXXXXXX4417`, `u***@bankalpha`); "Reveal" action asks for a short reason and shows the full value for the current view only |
| Inputs | Identifier fields; role; reason |
| Processing | [DET] masking function applied in the API serialisation layer, log formatter and prompt builder; unmask endpoint writes an audit event |
| Outputs | Masked fields by default; unmasked on permitted request |
| Edge cases | Unmask on a field inside narrative text (narratives are masked in display by pattern replacement; raw text available through the same logged reveal); search by full number still works (search normalises server-side); masked value collisions (last-4 collisions shown with disambiguating internal ID); prompt needs the exact identifier (task-specific exception documented in Technical Documentation) |
| Acceptance criteria | AC-59 to AC-61 |
| Priority | MUST |

### 28.1 Security requirements

| ID | Requirement | Priority |
|---|---|---|
| SEC-01 | Secrets (Nemotron API key, signing key, demo passwords) only from environment variables; `.env.example` contains placeholders; secrets never logged or returned | MUST |
| SEC-02 | Dataset flagged `synthetic: true` required; demo and any other data separated by directory and database | MUST |
| SEC-03 | Passwords hashed (adaptive hash with salt); no plaintext storage; no default password in the repository | MUST |
| SEC-04 | Input validation on every endpoint and ingestion record; size limits; reject unknown fields | MUST |
| SEC-05 | Parameterised database access only | MUST |
| SEC-06 | Output encoding in the UI; narratives rendered as text, never as HTML | MUST |
| SEC-07 | Prompt-injection defences: delimited evidence, explicit data-not-instructions statement, output schema, validator, language guard | MUST |
| SEC-08 | Safe error messages; stack traces only in server logs | MUST |
| SEC-09 | CORS restricted; security headers set for the web app | MUST |
| SEC-10 | Rate limiting on login and reasoning endpoints | MUST |
| SEC-11 | HTTPS for any non-local deployment (documented); local demo uses localhost | SHOULD |
| SEC-12 | Dependencies pinned; minimal set | SHOULD |
| SEC-13 | Data-at-rest encryption documented as a production requirement and not claimed unless implemented | MUST (honesty), NICE (implementation) |
| SEC-14 | Limitations and Safeguards page lists implemented and not-implemented controls | MUST |
| SEC-15 | No fake integrations; no UI element implies connection to real institutions | MUST |
| SEC-16 | Prompts and logs contain only fields required for the task (data minimisation) | MUST |

### 28.2 Limitations page (required content)

1. Uses synthetic data only; no connection to banks, UPI networks, telecom operators or law enforcement.
2. Outputs are risk indicators and hypotheses, not findings of guilt.
3. Risk score is an investigation priority.
4. AI output may be wrong; validator reduces but does not eliminate error.
5. Security controls implemented versus not implemented (explicit list).
6. Prototype built for a hackathon; not production-ready.

---

## 29. Audit Logging

### F-21 — Audit Log

| Item | Specification |
|---|---|
| Feature name | Audit Log |
| User problem | Supervisors and compliance reviewers must verify who did what, and investigators need a record of their decisions |
| Description | Append-only record of significant actions, viewable and filterable by Admin |
| User interaction | Admin: Audit view with filters (actor, action, case, date); export as CSV (SHOULD); Investigator: "History" tab in a case shows case-related entries |
| Inputs | Events from all modules |
| Processing | [DET] write on every defined event; no update or delete operation exposed; optional hash chaining (SHOULD) |
| Outputs | Records: ID, timestamp (UTC), actor ID, role, action, target type and ID, case ID, outcome (success or denied or error), request ID, details (masked) |
| Edge cases | Audit write failure (the action fails and reports an error; no silent loss); high volume of simulator events (aggregated entries with counts allowed for events, not for decisions); actor deleted (record retains actor ID); attempted denied action (recorded as denied) |
| Acceptance criteria | AC-62 to AC-64 |
| Priority | MUST |

### 29.1 Audit event list (minimum)

| Category | Events |
|---|---|
| Authentication | login success, login failure, lockout, logout, session expiry |
| Data | dataset load, dataset reset, ingestion rejection summary |
| Access | evidence unmask (with reason), audit log viewed |
| Cases | case created, updated, status changed, note added, subgraph refreshed, closed |
| Reasoning | job started, job completed, job failed, mode switched (live or cached), withheld-statement count |
| Review | finding reviewed, plan step reviewed, link promoted or demoted |
| Alerts | alert triggered, acknowledged, dismissed (with reason), escalated |
| Simulator | event injected, simulator play, pause, step, reset |
| Security | permission denied, rate limit hit |
| Configuration | scoring configuration version change |

---

## 30. Error Handling Requirements

### 30.1 Principles

1. Fail visibly and honestly; never present partial or cached output as live or complete.
2. Degrade gracefully; deterministic features keep working when AI is unavailable.
3. Never show raw errors or stack traces to users; always include a request ID.
4. Every fallback is labelled as a fallback.

### 30.2 Error and fallback matrix

| Scenario | Detection | System behaviour | User-visible message | Priority |
|---|---|---|---|---|
| Nemotron unreachable or timeout | Timeout or HTTP error | Mark job Unavailable; serve cached output if the input hash matches; otherwise show deterministic analysis only | "Reasoning unavailable. Showing deterministic analysis." or "Cached reasoning (not live)." | MUST |
| Nemotron invalid structure | Schema validation fails | One repair retry; then Failed | "AI output could not be validated." with Retry | MUST |
| Nemotron cites invalid evidence | Evidence validator | Remove statement; log; count | "N AI statements withheld for lacking valid evidence." | MUST |
| Accusatory language produced | Language guard | Rewrite by template or withhold | Safe wording or withheld count | MUST |
| Rate limit or credit exhaustion | HTTP 429 or quota error | Switch to cached mode if available; else Unavailable | "Rate limit reached. Cached mode available." | MUST |
| Graph rendering failure | Frontend error boundary | Switch to table view of entities and links | "Showing table view." | MUST |
| Database missing or corrupt | Startup check | Refuse to start with a clear message; reset-and-seed command restores | "Data store unavailable. Run reset-and-seed." | MUST |
| Dataset not flagged synthetic | Manifest check | Refuse load | "Dataset rejected: not flagged synthetic." | MUST |
| Invalid record in ingestion | Schema validation | Reject record, continue; report | Count and reasons in the ingestion report | MUST |
| Invalid event submitted | Schema validation | Reject; audit; no state change | "Event rejected: {reason}." | MUST |
| Duplicate event | Event ID check | No-op; return existing result | "Event already processed." | MUST |
| Unauthorised or forbidden action | Auth middleware | 401 or 403; audit | "You do not have access to this action." | MUST |
| Session expired | Token check | 401; redirect to login | "Session expired. Please sign in." | MUST |
| Audit write failure | Write error | Abort the action | "Action not completed (audit unavailable)." | MUST |
| Search with no results | Empty result | Empty state | "No matching records." | MUST |
| Case subgraph too large | Cap exceeded | Truncate by risk and recency; notice | "Showing top N of M entities." | MUST |
| Stale reasoning after new events | Case version compare | Mark result "Possibly out of date" | Banner with Re-run | SHOULD |
| Simulator queue empty | Empty queue | Disable step and play | "No more events." | SHOULD |

### 30.3 Error response codes

| HTTP | Meaning |
|---|---|
| 400 | Validation failure (details list the fields) |
| 401 | Not authenticated or expired |
| 403 | Authenticated but not permitted |
| 404 | Not found |
| 409 | Conflict (for example case already exists for the seed) |
| 422 | Semantic failure (for example dataset not synthetic) |
| 429 | Rate limit |
| 502 or 503 | Dependency unavailable (Nemotron, store) |
| 500 | Unexpected; safe message and request ID |

---

## 31. Performance Requirements

| ID | Operation | Target | Condition |
|---|---|---|---|
| PERF-01 | Dataset load including extraction and graph build | < 15 s | Demo dataset (about 56 transactions, 13 complaints) |
| PERF-02 | Graph build from database | < 5 s | Demo dataset |
| PERF-03 | Risk computation for all entities | < 3 s | Demo dataset |
| PERF-04 | Event pipeline, steps 1 to 6 | < 3 s | Single event |
| PERF-05 | Dashboard load | < 2 s | After login |
| PERF-06 | Case workspace tab switch | < 500 ms | Cached data |
| PERF-07 | Graph render | < 2 s initial, interactions < 200 ms | Up to 300 nodes and 600 edges |
| PERF-08 | Global search response | < 300 ms | |
| PERF-09 | Single Nemotron task | Target < 60 s; hard timeout 90 s; progress after 1 s | Live mode |
| PERF-10 | Full case reasoning (T1 per complaint, T2, T4, T5, T6, T7) | Target < 5 min total with per-task progress | Live mode; may run tasks concurrently within rate limit |
| PERF-11 | Cached reasoning display | < 1 s | Cached mode |
| PERF-12 | Reset-and-seed | < 60 s | One command |

Performance results are measured and reported in the evaluation report.

---

## 32. Testing Requirements

### 32.1 Test categories

| ID | Category | Scope | Priority |
|---|---|---|---|
| TST-01 | Generator tests | Reproducibility, counts, ground truth consistency, synthetic flag | MUST |
| TST-02 | Ingestion tests | Valid and invalid records; idempotency; evidence ID stability | MUST |
| TST-03 | Normalisation and matching tests | Phone format variants, UPI case, benign allow-list, no false exact matches | MUST |
| TST-04 | Graph tests | Components, time-ordered paths, weak-link exclusion, cycle handling, subgraph extraction | MUST |
| TST-05 | Risk tests | Determinism, factor boundaries (each threshold), decoy scoring, tie-break | MUST |
| TST-06 | API tests | Auth required, RBAC, validation errors, pagination, error envelope | MUST |
| TST-07 | Audit tests | Every event in Section 29.1 writes a record; no update or delete path | MUST |
| TST-08 | Masking tests | No unmasked identifier in API, logs or prompts without unmask | MUST |
| TST-09 | Orchestrator tests | Schema validation, repair retry, caching, timeouts, rate limit using mocked model responses | MUST |
| TST-10 | Validator tests | Fabricated IDs, missing IDs, numeric mismatch, accusatory phrasing | MUST |
| TST-11 | Prompt-injection tests | C-07 and additional adversarial strings do not change behaviour or leak | MUST |
| TST-12 | Live Nemotron tests | Real calls on seed cases return valid structure; T1, T4, T5 quality checks against ground truth | MUST |
| TST-13 | Real-time tests | Injected events produce alert, graph update, re-score, idempotency | MUST (inject), SHOULD (continuous) |
| TST-14 | Frontend tests | Manual checklist for every visual operation in Section 12; smoke automation if time | MUST |
| TST-15 | End-to-end demo test | Full Appendix A script from clean start, timed | MUST |
| TST-16 | Failure drills | Each scenario in Section 30.2 induced once | MUST |
| TST-17 | Evaluation run | Metrics versus ground truth (Section 33.3) | MUST |
| TST-18 | Text review | Language and honesty checklist across UI and documents | MUST |

### 32.2 Test rules

- Codex runs automated tests after every milestone; no milestone closes with failing tests.
- Tests use mocked Nemotron responses by default; a separate marked suite uses the live endpoint.
- Ground truth is used only by TST-01, TST-12 and TST-17.
- Each acceptance criterion in Section 33 maps to at least one test or checklist item.

---

## 33. Acceptance Criteria

### 33.1 Master acceptance criteria

| ID | Area | Criterion (Given / When / Then) | Priority |
|---|---|---|---|
| AC-01 | Ingestion | Given the demo package, when loaded, then all valid records are stored, each with a unique evidence ID, and counts match the manifest | MUST |
| AC-02 | Ingestion | Given a dataset without `synthetic: true`, when loaded, then the load is refused and nothing is stored | MUST |
| AC-03 | Generator | Given the same seed twice, when generated, then outputs are identical; counts equal the targets in Section 23.2 | MUST |
| AC-04 | Ingestion | Given a malformed record, when ingested, then it is rejected with a reason and other records load | MUST |
| AC-05 | Normalisation | Given the same phone in three formats, when normalised, then all resolve to one phone entity | MUST |
| AC-06 | Ingestion | Given the same dataset loaded twice, then evidence IDs and counts are unchanged | MUST |
| AC-07 | Graph | Given the loaded dataset, when the graph is built, then it completes in under 5 seconds | MUST |
| AC-08 | Graph | Given the demo dataset, when clusters are computed, then M1 to M7 and the 20 victims are in one cluster with at least 90% of true network members and D1 and P6 excluded | MUST |
| AC-09 | Graph | Given weak links, when clusters are computed, then no weak or unconfirmed link merges clusters | MUST |
| AC-10 | Graph | Given the transfer data, when paths are requested between a victim account and M7, then the time-ordered chain through layer-1, layer-2 and M6 is returned with hop times | MUST |
| AC-11 | Graph | Given a benign allow-list identifier, then no link is created | MUST |
| AC-12 | Risk | Given identical data and configuration, when scores are computed twice, then scores and breakdowns are identical | MUST |
| AC-13 | Risk | Given each network account, then a factor breakdown with evidence IDs is available | MUST |
| AC-14 | Risk | Given D1, then its band is Low or Medium and its mitigating factors are displayed | MUST |
| AC-15 | Risk | Given the factor thresholds in 15.2, then boundary tests pass for each factor | MUST |
| AC-16 | Risk | Given any score display, then the disclaimer "Investigation priority, not an indicator of guilt." is shown | MUST |
| AC-17 | Explainability | Given any displayed AI finding, then it lists at least one valid evidence ID, a confidence, counter-evidence or gaps, and a next step | MUST |
| AC-18 | Explainability | Given model output citing a nonexistent evidence ID, then the statement is withheld and counted; zero invented IDs appear in the UI | MUST |
| AC-19 | Explainability | Given model output containing prohibited accusatory terms, then it is rewritten or withheld | MUST |
| AC-20 | Visualization | Zoom and pan work smoothly on the case graph | MUST |
| AC-21 | Visualization | Search focuses the matching node, including for a phone typed in a different format | MUST |
| AC-22 | Visualization | Entity-type, link-strength and cluster filters change the visible graph correctly | MUST |
| AC-23 | Visualization | Clicking a node or edge shows metadata and evidence IDs; clicking an ID opens the evidence detail | MUST |
| AC-24 | Visualization | Cluster isolation shows only the selected cluster | MUST |
| AC-25 | Visualization | Fraud-chain highlighting shows the chain with numbered steps in time order | MUST |
| AC-26 | Visualization | Link strengths (exact, inferred, weak) are visually distinct and shown in the legend; table fallback appears on render failure | MUST |
| AC-27 | Evidence | Given a finding, when an evidence ID is clicked, then the evidence detail opens within 500 ms | MUST |
| AC-28 | Evidence | Given the explorer, then filters by type, date and entity work and "cited by" lists the correct findings | SHOULD |
| AC-29 | Timeline | Given a case, then events are in correct timestamp order for at least 95% of ground-truth pairs, with gaps shown for chain transfers | MUST |
| AC-30 | Dashboard | Given login, then the dashboard shows KPI tiles, alert feed, priority list and cases within 2 seconds | MUST |
| AC-31 | Dashboard | Given the demo dataset, then the dashboard lists four apparently separate cases and shows at least one cross-case cluster after processing | MUST |
| AC-32 | Cases | Given a cluster, when "Create case" is used, then a case with subgraph, evidence and timeline is created | MUST |
| AC-33 | Cases | Given a case with a seed already in an open case, then the user is offered the existing case | MUST |
| AC-34 | Timeline | Given a conflict marker, when clicked, then the contradiction detail opens | SHOULD |
| AC-35 | Timeline | Given reconstructed order, then recorded timestamps remain visible and differences are highlighted | SHOULD |
| AC-36 | Real-time | Given an injected held-out event, then the pipeline completes steps 1 to 6 in under 3 seconds | MUST |
| AC-37 | Real-time | Given the held-out transfer touching M6, then an alert fires from deterministic rules and the graph shows the new edge | MUST |
| AC-38 | Real-time | Given Nemotron unavailable, then the alert still fires and Nemotron status shows Unavailable | MUST |
| AC-39 | Real-time | Given a duplicate event, then it is ignored without state change | MUST |
| AC-40 | Alerts | Given an alert, then it shows rules fired with actual values and evidence IDs | MUST |
| AC-41 | Alerts | Given an alert, when escalated, then a case is created or attached with the alert recorded | MUST |
| AC-42 | Review | Given a finding, when rejected, then a reason is required, state and reason are stored, the audit log records it, and the case summary excludes it | MUST |
| AC-43 | Review | Given any UI or API, then there is no freeze, seize, block, report or bulk-accept control | MUST |
| AC-44 | Search | Given an identifier in any supported format, then results appear in under 300 ms | MUST |
| AC-45 | Search | Given a partial identifier of 4 or more characters, then prefix matches appear | MUST |
| AC-46 | T1 | Given the 13 complaints, then at least 90% of key identifiers and facts are extracted correctly per ground truth | MUST |
| AC-47 | T1 | Given C-07 (injection), then the instruction in the text is not followed and the complaint is still interpreted | MUST |
| AC-48 | T4 | Given the demo case, then reconstructed chronology correctly orders at least 95% of ground-truth event pairs | MUST |
| AC-49 | T5 | Given the demo case, then the causal chain correctly identifies the key stages and money chain per ground truth (at least 90% of key stages) | MUST |
| AC-50 | T5 | Given a stage lacking evidence, then it is shown as "Not established" and not invented | MUST |
| AC-51 | T2 | Given the case, then the narrative-only link via P5 (Case B and D) is proposed with evidence and confirmed by exact match | MUST |
| AC-52 | T7 | Given the case, then a ranked plan with evidence-linked rationale is produced; every step passes the validator | MUST |
| AC-53 | T6 | Given hypotheses, then each has confidence and counter-evidence or gaps | MUST |
| AC-54 | T3 | Given the four planted contradictions, then at least 3 of 4 (target 4 of 4) are surfaced with assessments | SHOULD |
| AC-55 | Auth | Given no token, then any protected endpoint returns 401 | MUST |
| AC-56 | Auth | Given an Investigator token, then Admin-only endpoints return 403 | MUST |
| AC-57 | Auth | Given 5 failed logins, then the account is locked for 5 minutes | MUST |
| AC-58 | Auth | Given the repository, then no default or hardcoded password exists | MUST |
| AC-59 | Masking | Given any API response or log line, then identifiers are masked by default | MUST |
| AC-60 | Masking | Given an unmask request, then a reason is required and an audit event is written | MUST |
| AC-61 | Masking | Given Nemotron prompts, then identifiers are masked unless a task exception is documented | MUST |
| AC-62 | Audit | Given any event in Section 29.1, then a record exists with actor, time, action and target | MUST |
| AC-63 | Audit | Given the API, then no endpoint modifies or deletes audit records | MUST |
| AC-64 | Audit | Given an audit write failure, then the originating action fails | MUST |
| AC-65 | Fallback | Given Nemotron unreachable, then all non-AI features work and cached mode is offered | MUST |
| AC-66 | Fallback | Given cached mode, then results are labelled "Cached (not live)" everywhere they appear | MUST |
| AC-67 | Honesty | Given any screen, then the synthetic-data banner is visible and the Limitations page is reachable | MUST |
| AC-68 | Honesty | Given the text review checklist, then no UI or doc text implies real data, guilt, certainty or enterprise-grade security | MUST |
| AC-69 | End-to-end | Given a clean start, then the Appendix A demo runs without manual database edits in at least 5 of 5 rehearsals | MUST |
| AC-70 | Reset | Given the reset-and-seed command, then demo state is restored in under 60 seconds | MUST |

### 33.2 Success criteria (mapping to Project Plan S1 to S12)

| Plan criterion | Proven by |
|---|---|
| S1 Ingest fragmented evidence | AC-01, AC-02, AC-04, AC-06 |
| S2 Extract entities and relationships | AC-05, AC-11, AC-46, AC-51 |
| S3 Build graph | AC-07 |
| S4 Identify fraud clusters | AC-08, AC-09 |
| S5 Calculate risk and priority | AC-12 to AC-16 |
| S6 New events update the system | AC-36, AC-37, AC-39 |
| S7 Reconstruct timeline | AC-29, AC-48 |
| S8 Nemotron reasons across evidence | AC-49, AC-51, AC-52 |
| S9 Findings linked to evidence | AC-17, AC-18 |
| S10 Next steps generated | AC-52 |
| S11 Visual inspection | AC-20 to AC-26 |
| S12 End-to-end workflow | AC-69 |

### 33.3 Evaluation metrics (measured against ground truth)

| Metric | Definition | Target |
|---|---|---|
| Entity recall | Ground-truth entities found / total | >= 95% |
| Link recall | Ground-truth links found / total | >= 90% |
| Exact-link precision | Correct exact links / exact links produced | 100% |
| Inferred-link precision | Correct inferred links / inferred links produced | >= 85% |
| Cluster coverage | True network members captured | >= 90% |
| Cluster purity | Network members / cluster members | >= 90% |
| Decoy rejection | D1, P6 and the coincidence pair excluded or weak | 100% |
| Chain accuracy | Key stages of the money chain correctly ordered | >= 90% |
| Chronology accuracy | Ground-truth event pairs correctly ordered | >= 95% |
| Contradiction recall | Planted contradictions surfaced | 4 of 4 (minimum 3) |
| Evidence-ID validity | Cited IDs that exist | 100% |
| Invented evidence shown to users | Count | 0 |
| Complaint extraction accuracy | Key facts correctly extracted | >= 90% |
| Score reproducibility | Identical across runs | 100% |
| Event-to-alert latency | Steps 1 to 6 | < 3 s |
| Demo reliability | Clean end-to-end runs | >= 5 of 5 |

### 33.4 Definition of Done for the PRD stage

The PRD stage is Done when this document is approved, every feature in Sections 10 to 25 has acceptance criteria in Section 33, the open decisions in Appendix C are assigned to the Technical Documentation, and no requirement conflicts with the Project Plan.

---

## Appendix A — End-to-End Demo Specification

### A.1 Pre-conditions

1. Clean start via the reset-and-seed command with seed `S1` (default).
2. Dataset loaded: initial 50 transactions, 12 complaints, communications, devices; held-out queue of 7 events.
3. Reasoning mode: Live (with Cached as ready fallback; cached outputs pre-validated).
4. Demo accounts: one Investigator, one Admin (credentials from environment).

### A.2 Script with expected observations

| Step | Action | Expected observation | Criteria |
|---|---|---|---|
| 1 | Log in as Investigator | Dashboard in under 2 s; banner visible | AC-30, AC-67 |
| 2 | Review dashboard | Four case labels (A to D), initial alerts, priority list headed by pass-through accounts; D1 not at top | AC-14, AC-31 |
| 3 | Inject next held-out event (transfer touching M6) | Alert appears in under 3 s: R1 and/or R3 with explanation | AC-36, AC-37, AC-40 |
| 4 | Open alert, read "Why this fired" | Rules, values, evidence IDs | AC-40 |
| 5 | Open risk breakdown for M6 | Factors listed; disclaimer | AC-13, AC-16 |
| 6 | Open network view | New edge visible; cross-case cluster visible with badge | AC-20, AC-37 |
| 7 | Isolate the cluster; search P5 typed as "0091-90000-0xxxx" | Node focused despite format difference | AC-21, AC-24 |
| 8 | Create case from the cluster | Case workspace opens with timeline and evidence | AC-32 |
| 9 | Open Timeline | Ordered events, gaps (for example transfer hops minutes apart), conflict markers X1 to X4 | AC-29, AC-34 |
| 10 | Open Evidence for a complaint | Original text and interpretation tab (pending) | AC-27 |
| 11 | Run reasoning | Progress per task; results arrive; withheld count shown if any | AC-46 to AC-52 |
| 12 | View causal chain and highlight in graph | Five stages with evidence; chain highlighted with numbered steps | AC-25, AC-49 |
| 13 | View narrative-only link via P5 (Case B and D) | Inferred link with "confirmed" badge and evidence | AC-51 |
| 14 | Open Contradictions | X1 to X4 with assessments | AC-54 |
| 15 | Review plan; accept two steps; reject one finding with a reason | States recorded; dependent step flagged | AC-42, AC-52 |
| 16 | Switch to Cached mode, re-run | Output labelled "Cached (not live)" | AC-66 |
| 17 | Log in as Admin; open Audit log | Entries for steps 1 to 16 | AC-62 |
| 18 | Open Limitations page | Required content | AC-67 |

### A.3 Failure drills during rehearsal

At least two rehearsals include an induced Nemotron failure at step 11 (expected: graceful degradation and cached mode).

---

## Appendix B — Configuration Parameters (Defaults)

| Parameter | Default | Used by |
|---|---|---|
| PASS_THROUGH_WINDOW_MIN | 30 | Risk, alerts |
| FORWARD_RATIO | 0.80 | Risk, alerts |
| TIMING_WINDOW_MIN | 60 | Risk, alerts |
| ALERT_MIN_AMOUNT (INR) | 10,000 | Alerts |
| ALERT_DEDUP_MIN | 15 | Alerts |
| BASELINE_DAYS | 14 | Risk mitigation |
| HUB_BENIGN_DEGREE | 25 | Graph |
| CASE_MAX_HOPS | 3 | Cases |
| CASE_MAX_NODES | 300 | Cases |
| AMOUNT_TOLERANCE_PCT | 1 | Contradictions |
| TIME_TOLERANCE_MIN | 120 | Contradictions |
| MAX_FILE_MB | 10 | Ingestion |
| MAX_NARRATIVE_CHARS | 8,000 | Ingestion, prompts |
| SESSION_MINUTES | 60 | Auth |
| LOGIN_MAX_ATTEMPTS / LOCKOUT_MIN | 5 / 5 | Auth |
| NEMOTRON_TIMEOUT_S | 90 | Reasoning |
| NEMOTRON_MAX_JOBS_PER_MIN | 10 | Reasoning |
| REASONING_MODE | live | Reasoning (live or cached) |
| Risk weights and thresholds | Section 15 | Risk (versioned file) |

---

## Appendix C — Open Decisions Delegated to the Technical Documentation

| # | Decision | Constraint from this PRD |
|---|---|---|
| 1 | Backend framework and database | Single-machine, simple, Codex-friendly; recommended FastAPI and SQLite (Project Plan) |
| 2 | Graph library and storage | Deterministic rebuild; in-memory acceptable |
| 3 | Frontend framework and graph rendering library | Must satisfy Section 12 and NFR-004 |
| 4 | Exact database schema and indexes | Must support Section 22.3 and F-15 |
| 5 | Prompt templates, temperature and token budgets per task | Must satisfy Section 25.3 |
| 6 | Cached-reasoning storage format and pre-validation procedure | Must satisfy FR-040 and AC-66 |
| 7 | Password hashing and token mechanism details | Must satisfy SEC-03 and F-20 |
| 8 | Masking patterns per field | Must satisfy F-22 |
| 9 | Polling versus server-sent events | Polling is the MUST baseline |
| 10 | Ground-truth file schema and evaluation scripts | Must support Section 33.3 |
| 11 | Exact transaction amounts, times and narrative templates | Must satisfy Sections 23.2 to 23.9 |
| 12 | Repository layout and test tooling | Must satisfy Section 32 |

---

## Appendix D — Language and Terminology Rules

**Required vocabulary:** risk indicator, investigation priority, potential relationship, investigative hypothesis, evidence-backed finding, pass-through pattern, reported as caller, potential mule-account indicator.

**Prohibited as assertions about a specific person or entity:** guilty, criminal, fraudster, culprit, perpetrator, mastermind, "is a mule", "committed fraud", "stole", and any equivalent definite claim of wrongdoing or intent.

**Hedged phrasing required:** "may be", "potentially", "evidence suggests", "consistent with", always followed by the evidence list.

| Term | Meaning (consistent with Project Plan) |
|---|---|
| Evidence | A stored record with a stable ID |
| Entity | A node in the graph |
| Link / relationship | An edge with metadata |
| Exact / Inferred / Weak link | Link strengths (Section 24.2) |
| Cluster | Connected group under cluster-forming links |
| Case | Investigator workspace built from a cluster, alert or selection |
| Finding | Evidence-backed statement in the Section 16.1 format |
| Hypothesis | A finding framed as a possibility with confidence and counter-evidence |
| Investigation priority / Risk score | Deterministic explainable score; not guilt |
| Causal chain | Precursor -> Trigger -> Movement -> Amplification -> Outcome |
| Cached mode | Serving pre-validated stored reasoning when live Nemotron is unavailable |

---

## Appendix E — Traceability to the Project Plan

| Project Plan section | PRD coverage |
|---|---|
| 1 Vision, 2 Problem | Sections 1, 2 |
| 3 Success criteria | Sections 33.2, 33.3 |
| 4 Scope, 5 Non-goals | Sections 0, 1.5, 1.6, 19.2, 25.2 |
| 6 MVP, 7 Advanced | Sections 8, 9, 6 |
| 9 Division of labour | Sections 22.4, 25.1, 25.2 |
| 15 to 16 Data and scenario | Section 23 |
| 17 Backend | Sections 22, 24, 26 to 31 |
| 18 Frontend | Sections 10 to 21 |
| 19 Graph | Sections 12, 24 |
| 20 Risk scoring | Sections 15, 33 |
| 21 Real-time | Sections 17, 18 |
| 22 Explainability | Section 16 |
| 23 Nemotron | Section 25 |
| 24 Security and privacy | Sections 27 to 29 |
| 25 Testing, 26 Metrics | Sections 32, 33 |
| 27 Demo | Appendix A |
| 28 Failure and fallback | Section 30 |
| 30 Definition of Done | Section 33.4, acceptance criteria |

---

## Appendix F — Change Control

Once approved, this PRD is the source of truth for the Technical Documentation. Any change requires a version increment, a change note below, and a consistency check against the Project Plan, Technical Documentation and Codex Master Prompt.

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-10-07 | Initial PRD |

**— End of FRAUDMESH_PRD —**
