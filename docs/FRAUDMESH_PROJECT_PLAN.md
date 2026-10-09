# FRAUDMESH — PROJECT PLAN

**Cross-Bank Financial Crime Reconstruction & Recovery Agent**

| Field | Value |
|---|---|
| Document | FRAUDMESH_PROJECT_PLAN.md |
| Version | 1.0 (Draft for approval) |
| Date | 2026-10-07 |
| Position in chain | Document 1 of 4 (Project Plan -> PRD -> Technical Documentation -> Codex Master Prompt) |
| Author role | Claude (Planning / Architecture / Documentation lead) |
| Implementation agent | OpenAI Codex |
| Primary AI model | NVIDIA Nemotron |
| Data policy | Synthetic or authorized data only |
| Status | Source of truth for the PRD once approved |

> **Positioning:** Normal systems see suspicious transactions. FraudMesh sees the fraud network.

---

## 0. How to Read This Document

This is the master execution plan. It explains WHAT must be built, WHY it matters, and WHEN each component is built. It is not a coding instruction and contains no application code. Later documents inherit its terminology, entities, architecture and assumptions:

- The **PRD** turns this plan into user stories, functional requirements and acceptance criteria.
- The **Technical Documentation** turns the PRD into schemas, APIs, module designs and prompts.
- The **Codex Master Prompt** turns the Technical Documentation into step-by-step implementation instructions.

Priority labels used throughout: **MUST HAVE**, **SHOULD HAVE**, **NICE TO HAVE**.

Logic-type labels used throughout, so that responsibilities never blur:

| Label | Meaning |
|---|---|
| **[DET]** | Deterministic software logic: exact matching, queries, sorting, aggregation, validation, scoring arithmetic |
| **[GRAPH]** | Graph algorithms: construction, traversal, connected components, path finding, centrality |
| **[LLM]** | Generic language-model capability that any capable model could provide (e.g., summarisation wording) |
| **[NEM]** | Nemotron-specific reasoning that is the core justification for the model: long-context, multi-source, uncertain, narrative reasoning |

---

## 1. Project Vision

FraudMesh is an investigation-support platform that reconstructs fragmented financial-fraud evidence into an explainable network, a chronology and an investigation plan, so that a human investigator can see the whole operation instead of isolated incidents.

**Vision statement.** Give an investigator the ability to open one suspicious event and, within minutes, understand who and what is connected, in what order things happened, how money moved, which separate cases may belong to one operation, what evidence supports each conclusion, and what to examine next.

**What FraudMesh is:**

- A cross-case network reconstruction tool.
- An evidence-grounded reasoning assistant for investigators.
- A transparent risk-indicator and investigation-priority engine.
- A visual exploration environment for fraud networks.

**What FraudMesh is not:**

- Not a fraud classifier or transaction scorer on its own.
- Not a chatbot or generic RAG application.
- Not a dashboard with AI decoration.
- Not a system that decides guilt, freezes accounts or seizes funds.

**Architectural principle.**

```
Deterministic Systems
   + Graph Analysis
   + Nemotron Reasoning
   + Human Investigation
```

The LLM never does everything. Software does what software does reliably; Nemotron does what only a long-context reasoning model can do; the human decides.

---

## 2. Problem Definition

### 2.1 The problem

Modern fraud is a network problem. One scam operation may involve multiple victims, bank accounts, UPI IDs, phone numbers, devices, mule accounts, transfers, cash withdrawals, timestamps, communications and earlier complaints. Each victim files a separate complaint, each bank sees a fragment, and each case is worked in isolation.

### 2.2 The systemic gap

Existing systems can flag suspicious transactions or identifiers. Investigators must still:

1. Collect scattered evidence from multiple incidents.
2. Decide which identifiers genuinely link cases and which are coincidences.
3. Reconstruct the order of events and the money trail.
4. Reconcile conflicting accounts (victim narrative versus ledger versus device record).
5. Decide whether apparently unrelated cases belong to one network.
6. Decide what to examine next.

Steps 2 to 6 are reasoning tasks over messy, partially inconsistent evidence. That is the gap FraudMesh targets.

### 2.3 Example chain to reconstruct

```
Victim A
  -> Scammer Phone X
  -> Mule Account B
  -> Mule Account C
  -> Cash Withdrawal
  -> Victim D (a second, apparently unrelated case)
```

The important capability is not detecting each transaction. It is reconstructing the larger network and relationships between apparently separate incidents.

### 2.4 Core pipeline

```
Evidence Ingest
   -> Entity & Link Extraction
   -> Chronology Build
   -> Causal Reconstruction
   -> Risk / Investigation Priority
   -> Investigation Plan
   -> Human Investigator Review
```

| Stage | Primary logic type | Notes |
|---|---|---|
| Evidence Ingest | [DET] | Validation, normalisation, evidence IDs |
| Entity & Link Extraction | [DET] for structured fields, [NEM] for free-text complaints | Exact identifiers by software; narrative interpretation by Nemotron |
| Chronology Build | [DET] sorting + [NEM] reconciliation | Software sorts timestamps; Nemotron resolves conflicting or missing times |
| Causal Reconstruction | [NEM] over [GRAPH] output | Precursor -> Trigger -> Movement -> Amplification -> Outcome |
| Risk / Investigation Priority | [DET] + [GRAPH] | Explainable weighted factors; never a guilt probability |
| Investigation Plan | [NEM] | Evidence-backed, ranked next steps |
| Investigator Review | Human | Accept, reject, annotate; all recorded in audit log |

---

## 3. Success Criteria

FraudMesh is successful when the following twelve statements are demonstrably true on the synthetic dataset, with no hardcoded answer.

| # | Criterion | Measurable target |
|---|---|---|
| S1 | Fragmented synthetic evidence can be ingested | 100% of valid seed records ingested; invalid records rejected with reasons |
| S2 | Entities and relationships can be extracted | >= 95% of ground-truth entities and >= 90% of ground-truth links recovered |
| S3 | A graph can be constructed | Graph built from raw records in under 5 seconds |
| S4 | Fraud-related clusters can be identified | The hidden network is isolated as one cluster covering >= 90% of its true members, with the decoy entities excluded |
| S5 | Risk/priority scores can be calculated | Every scored entity shows its factor breakdown; scores reproducible across runs |
| S6 | New events update the system | A simulated event updates graph, risk and alert in under 3 seconds (excluding Nemotron) |
| S7 | A timeline can be reconstructed | Chronology ordered correctly for >= 95% of ground-truth event pairs |
| S8 | Nemotron reasons across the evidence | Reasoning output cites evidence from at least 3 distinct source types per finding |
| S9 | AI findings are linked to evidence | 100% of cited evidence IDs exist; 0 invented IDs reach the UI |
| S10 | Investigative next steps are generated | Plan contains ranked steps, each linked to evidence and a stated rationale |
| S11 | Investigator can visually inspect the network | Zoom, pan, search, filter, node/edge inspection, cluster isolation, chain highlight all working |
| S12 | The complete workflow works end to end | Login -> alert -> case -> timeline -> reasoning -> plan -> review -> audit log, demonstrated without manual database edits |

**Non-negotiable honesty criteria** (failure of any of these is project failure regardless of the above):

- No output claims guilt, certainty or criminality.
- No fake integration is presented as real.
- No real bank, government or private data is used.
- Prototype limitations are visible in the UI and the presentation.

---

## 4. Scope

### 4.1 In scope

- Synthetic data generator with a seeded, reproducible hidden fraud network, decoys and planted contradictions.
- Evidence ingestion, validation and normalisation with stable evidence IDs.
- Deterministic entity and link extraction from structured records.
- Nemotron-based interpretation of unstructured complaints and communication snippets.
- Graph construction, cluster detection, path analysis and graph features.
- Deterministic, explainable risk score / investigation priority.
- Chronology reconstruction and causal chain reconstruction.
- Case workspace, evidence explorer, timeline view and interactive network visualisation.
- Evidence-grounded findings with confidence levels and recommended next steps.
- Lightweight real-time event simulation.
- Basic authentication, role separation, audit logging, PII masking.
- Fallback and cached-reasoning mode for demo reliability.

### 4.2 Out of scope

See Section 5 (Non-goals).

### 4.3 Assumptions

1. The hackathon team has roughly one week of build time; Section 29 shows how to compress to 48 hours.
2. Codex performs all implementation under instructions derived from these documents.
3. Nemotron is accessed through an OpenAI-compatible HTTP endpoint (hosted by NVIDIA or self-hosted); the exact model name and endpoint are configuration, not code.
4. The demo runs on a single machine (laptop or one small server).
5. The audience includes mentors and judges who are not fraud-domain experts, so explanations must be self-evident.

---

## 5. Non-Goals

FraudMesh will NOT:

- Access, simulate access to, or claim integration with any real bank, UPI network, telecom operator, law-enforcement database or government system.
- Use any real personal or financial data.
- Autonomously accuse any person or declare guilt.
- Freeze accounts, reverse transactions, seize funds or trigger any enforcement action.
- Claim enterprise-grade security, compliance certification or production readiness.
- Provide a risk score presented as a probability of guilt.
- Build enterprise-scale streaming infrastructure (Kafka clusters, distributed graph databases).
- Train or fine-tune a model.
- Replace the investigator's judgment.

---

## 6. MVP Definition

The MVP is the smallest system that satisfies all twelve success criteria with a reliable end-to-end demo. Everything in the MUST HAVE list below constitutes the MVP.

### 6.1 Feature classification

| Feature | Priority | Logic type | Why it matters to the core problem |
|---|---|---|---|
| Synthetic dataset with hidden network, decoys, contradictions | MUST HAVE | [DET] | Without it nothing can be demonstrated or evaluated |
| Evidence ingestion with stable evidence IDs | MUST HAVE | [DET] | Grounding foundation; every finding needs an ID to cite |
| Entity & link extraction (structured) | MUST HAVE | [DET] | Exact matching must not be delegated to the model |
| Complaint interpretation (unstructured) | MUST HAVE | [NEM] | Where narrative reasoning starts; core Nemotron role |
| Fraud graph construction | MUST HAVE | [GRAPH] | The central data structure |
| Cluster detection and money-flow path finding | MUST HAVE | [GRAPH] | Discovers the hidden network deterministically |
| Transaction analysis (velocity, pass-through, fan-in/out) | MUST HAVE | [DET] | Feeds risk factors |
| Explainable risk score / investigation priority | MUST HAVE | [DET]+[GRAPH] | Prioritises review; must show why |
| Investigation case workspace | MUST HAVE | [DET] | Unit of investigator work |
| Visual network (zoom, pan, search, filter, inspect) | MUST HAVE | UI | Network understanding at a glance |
| Chronology / timeline | MUST HAVE | [DET]+[NEM] | Sequence is the heart of reconstruction |
| Causal chain reconstruction | MUST HAVE | [NEM] | The hardest reasoning task; Nemotron's showcase |
| Evidence-grounded findings with confidence | MUST HAVE | [NEM]+[DET] validator | Explainability and trust |
| Investigation plan | MUST HAVE | [NEM] | Converts analysis into action for a human |
| Basic authentication and roles | MUST HAVE | [DET] | Credibility; investigator identity for audit |
| Audit logging | MUST HAVE | [DET] | Human-in-the-loop accountability |
| Working end-to-end demo | MUST HAVE | All | Judged outcome |
| Real-time event simulation | SHOULD HAVE | [DET]+[GRAPH] | Shows live detection; lightweight replay is enough |
| Contradiction detection | SHOULD HAVE | [DET] candidates + [NEM] resolution | Differentiates from classifiers |
| Automated investigation plan refinement | SHOULD HAVE | [NEM] | Improves plan quality |
| Graph filtering by type, time, amount, confidence | SHOULD HAVE | UI + [DET] | Usability |
| Evidence explorer | SHOULD HAVE | UI | Lets judges verify grounding |
| Advanced graph analytics (betweenness, community detection) | SHOULD HAVE | [GRAPH] | Richer risk factors |
| Richer risk factors | SHOULD HAVE | [DET] | Better explanations |
| Investigator feedback loop on findings | SHOULD HAVE | [DET] | Demonstrates human control |
| Advanced streaming infrastructure | NICE TO HAVE | [DET] | Not needed for the claim |
| Sophisticated graph algorithms (embeddings, GNNs) | NICE TO HAVE | [GRAPH] | Distracts from explainability |
| Advanced role management | NICE TO HAVE | [DET] | Two roles suffice |
| Advanced analytics dashboards | NICE TO HAVE | UI | Superficial relative to core |
| Production-scale infrastructure | NICE TO HAVE | — | Out of hackathon reach |
| Case export as PDF report | NICE TO HAVE | [DET] | Useful but not core |

**Rule:** Hackathon reliability is more important than feature quantity. No SHOULD HAVE item starts until every MUST HAVE item meets its Definition of Done.

### 6.2 MVP boundary test

A feature belongs in the MVP only if removing it would break at least one success criterion S1 to S12. Otherwise it is SHOULD HAVE or lower.

---

## 7. Advanced Features (Beyond MVP)

Ordered by value to the core problem:

1. **Real-time event simulation (SHOULD):** replay a held-out slice of events through the same pipeline; the investigator sees the alert appear and the graph grow.
2. **Contradiction detection (SHOULD):** deterministic code proposes candidate conflicts (timestamp, amount, identifier mismatches between narrative and ledger); Nemotron judges which are material and what they imply.
3. **Investigation plan refinement (SHOULD):** Nemotron re-ranks leads after the investigator rejects or accepts a finding.
4. **Graph analytics (SHOULD):** betweenness and community detection to show mule hubs and collector accounts.
5. **Evidence explorer (SHOULD):** searchable list of every evidence record with the findings that cite it.
6. **Counterfactual check (NICE):** ask Nemotron "which single link, if wrong, collapses this finding?"
7. **Case report export (NICE).**

---

## 8. System Overview and Component Map

```
+-----------------------------------------------------------------+
|                      Investigator (human)                       |
+----------------------------+------------------------------------+
                             |
+----------------------------v------------------------------------+
| Frontend: Login | Dashboard | Case | Network | Timeline | Evidence|
+----------------------------+------------------------------------+
                             | REST (validated, authenticated)
+----------------------------v------------------------------------+
| Backend API                                                     |
|  Auth/RBAC | Audit log | Ingest | Extract | Graph | Risk | Events|
|  Reasoning Orchestrator (prompt build, schema check, evidence   |
|  validator, cache)                                              |
+-----+------------------------+-------------------------+--------+
      |                        |                         |
+-----v------+        +--------v--------+        +-------v--------+
| Database   |        | In-memory graph |        | Nemotron       |
| (records,  |        | (built from DB, |        | endpoint       |
| evidence,  |        | rebuilt/updated)|        | (configurable) |
| audit)     |        +-----------------+        +----------------+
+------------+
      ^
+-----+---------------------------------+
| Synthetic data generator + ground     |
| truth (used only by tests/evaluation) |
+---------------------------------------+
```

### 8.1 Core entities

Victim, Person/Entity, Bank Account, UPI ID, Phone Number, Device, Transaction, Withdrawal, Complaint, Incident, Communication, Event.

### 8.2 Core relationships

OWNS, USES, LINKED_TO, TRANSFERRED_TO, REPORTED_IN, WITHDREW_FROM, USED_DEVICE, USED_PHONE, CONNECTED_TO, PRECEDES, PART_OF_CASE.

Every relationship carries metadata where applicable: timestamp, source, evidence ID, confidence, transaction amount, relationship type. Relationships created by deterministic matching carry confidence "exact"; relationships proposed by Nemotron carry a confidence level and are marked "inferred".

### 8.3 Evidence ID convention

Every ingested record receives a stable ID such as `E-0001`. Categories are prefixed in metadata (transaction, complaint, device log, communication, account record). Findings may only cite IDs that exist. IDs are generated by software, never by the model.

---

## 9. Division of Labour: Software, Graph, LLM, Nemotron

This section is the authority on who does what. It is the most important design decision in the project.

| Task | Owner | Reason |
|---|---|---|
| Parse and validate records | [DET] | Exact, testable |
| Normalise phone/UPI/account formats | [DET] | Exact |
| Exact identifier matching (same phone, same device, same account) | [DET] | Models must not guess equality |
| Timestamp sorting and time-gap computation | [DET] | Arithmetic |
| Transaction aggregation, velocity, pass-through ratio | [DET] | Arithmetic |
| Graph construction and updates | [GRAPH] | Standard algorithms |
| Connected components, shortest/money-flow paths, centrality | [GRAPH] | Standard algorithms |
| Candidate contradiction generation (field mismatches) | [DET] | Cheap and exhaustive |
| Risk factor computation and weighted total | [DET] | Must be reproducible and explainable |
| Evidence-ID validation of AI output | [DET] | Guardrail against hallucination |
| Interpreting free-text complaints (who, what, how, when, which identifiers, implied events) | [NEM] | Messy language, ambiguity, missing data |
| Resolving which candidate contradictions are material and why | [NEM] | Requires weighing conflicting sources |
| Estimating plausible chronology where timestamps are missing or conflicting | [NEM] | Requires inference with stated uncertainty |
| Causal reconstruction: Precursor -> Trigger -> Movement -> Amplification -> Outcome | [NEM] | Multi-source, long-context reasoning |
| Generating investigative hypotheses with confidence and counter-evidence | [NEM] | Reasoning under uncertainty |
| Explaining why two entities may be related | [NEM] | Natural-language explanation grounded in cited evidence |
| Ranked investigation plan | [NEM] | Prioritisation across leads |
| Case summary for the investigator | [LLM]/[NEM] | Wording; generic capability, but fed by Nemotron findings |
| Decision to accept or reject a finding | Human | Accountability |

**Test for any new feature:** "Could normal software do this exactly?" If yes, it is not sent to Nemotron.

---

## 10. Development Phases Overview

| Phase | Name | Outcome |
|---|---|---|
| 0 | Foundations and approvals | Documents approved; repo, environment, secrets handling, Nemotron connectivity verified |
| 1 | Data and deterministic core | Synthetic dataset, ingestion, extraction, evidence IDs, database |
| 2 | Graph and risk | Graph, clusters, paths, risk engine, case objects |
| 3 | Interface and security | Auth, audit, dashboard, case view, network visualisation, timeline |
| 4 | Nemotron reasoning | Complaint interpretation, chronology, causal reconstruction, findings, plan, evidence validator |
| 5 | Real-time and polish | Event simulator, alerts, contradictions, filtering, evidence explorer |
| 6 | Hardening and demo | Fallbacks, caches, tests, evaluation, rehearsal, presentation |

---

## 11. What Should Be Built First

Build order is driven by dependencies: nothing can be reasoned about without data, and nothing can be grounded without evidence IDs.

1. **Repository, configuration and secrets handling** (environment variables, `.env.example`, no hardcoded secrets).
2. **Synthetic data generator and ground-truth file** (seeded, reproducible).
3. **Data model and database** (entities, relationships, evidence records).
4. **Ingestion with validation and evidence IDs.**
5. **Deterministic extraction and exact matching.**
6. **Nemotron connectivity smoke test** (one trivial call proving the endpoint, key and latency; done early to retire the biggest external risk).

## 12. What Should Be Built Second

1. Graph construction, cluster detection, money-flow path finding.
2. Deterministic risk engine with factor breakdown.
3. Case object model (case = cluster + evidence + chronology + findings + review state).
4. Authentication, roles and audit logging (needed before the UI so every action is attributable from day one).
5. Backend API surface for graph, case, evidence, risk.
6. Frontend skeleton: login, dashboard, case page, network view.
7. Timeline view (software-sorted first, reasoning-enriched later).
8. Nemotron integration: complaint interpretation, then chronology and causal reconstruction, then findings and plan, with the evidence validator built alongside, not after.

## 13. What Should Be Built Last

1. Real-time event simulator and alerting.
2. Contradiction detection UI and reasoning.
3. Filtering, evidence explorer, analytics refinements.
4. Cached-reasoning fallback mode and offline demo assets.
5. Presentation polish, demo script, recorded backup video.
6. NICE TO HAVE items only if all above meet Definition of Done.

---

## 14. Dependencies Between Components

```
Synthetic Data ---> Ingestion ---> Extraction ---> Database
                                        |             |
                                        v             v
                                     Graph ------> Risk Engine
                                        |             |
                                        v             v
                                   Case Builder <-----+
                                        |
          Auth/Audit --> API <----------+
                          |
          +---------------+----------------+
          v                                v
      Frontend                    Reasoning Orchestrator --> Nemotron
  (Network, Timeline,                    |
   Case, Evidence)                Evidence Validator
                                         |
                                  Findings + Plan --> Investigator Review --> Audit log
```

| Component | Depends on | Blocks |
|---|---|---|
| Synthetic data | Scenario design | Everything |
| Ingestion | Data model | Extraction, graph |
| Graph | Extraction | Risk, case, visualisation |
| Risk engine | Graph, transactions | Dashboard priority, alerts |
| Case builder | Graph, risk | Case UI, reasoning inputs |
| Auth/audit | Database | All write endpoints, review workflow |
| Reasoning orchestrator | Case builder, evidence IDs | Findings, plan |
| Evidence validator | Evidence records | Any display of AI output |
| Frontend network view | Graph API | Demo |
| Real-time simulator | Ingestion, graph, risk | Live-alert demo moment |

**Critical path:** Data -> Ingestion -> Extraction -> Graph -> Case builder -> Reasoning orchestrator + Validator -> Findings UI.

---

## 15. Data-Generation Plan

### 15.1 Principles

- 100% synthetic. All names, phone numbers, account numbers, UPI IDs and device identifiers are fabricated and use clearly synthetic patterns (for example, reserved or obviously fake number ranges and a fake bank-name set such as "Bank Alpha", "Bank Beta").
- Seeded and reproducible: the same seed produces the same dataset.
- Generated by a script (the generator is software, not an LLM call), so the ground truth is exactly known.
- Optionally, Nemotron or another LLM may be used offline to draft realistic complaint text from structured templates; the resulting text is saved as static fixture files so demos do not depend on live generation.
- Demo data and any other data live in separate directories and databases; the application refuses to load a dataset not flagged `synthetic: true`.

### 15.2 Dataset targets

| Element | Target |
|---|---|
| Victims | 20 |
| Transactions | 50+ (plan: about 56) |
| Bank accounts | 8 (plus clearly labelled victim-side accounts as needed) |
| Phone numbers | 6 |
| UPI IDs | about 6, mapped to accounts |
| Devices | 4 to 5 |
| Complaints | about 12 to 14 (not every victim complains; some complaints are late or vague) |
| Communications | about 8 to 10 snippets (message/call-log summaries) |
| Apparently separate cases | 4 |
| Hidden connected networks | 1 |
| Decoys | 2 to 3 (legitimate lookalikes) |
| Planted contradictions | 4 |
| Time span | about 3 weeks, with a dense final burst |

### 15.3 Ground-truth file

A separate `ground_truth` file records: network membership, true links, true chronology, planted contradictions, decoys. It is read only by tests and evaluation scripts, never by the application at runtime.

---

## 16. Synthetic Fraud Scenario Design

### 16.1 Narrative

Four victim groups file complaints that look unrelated: different scam stories, different cities, different dates, different banks. All four feed one mule infrastructure.

| Case | Surface story (as victims describe it) | Victims |
|---|---|---|
| Case 1 | "Digital arrest" / authority-impersonation call demanding a transfer to a "safe account" | 5 |
| Case 2 | Fake part-time job / task scam with small initial payouts then a large deposit | 5 |
| Case 3 | UPI refund / wrong-payment scam | 5 |
| Case 4 | Fake investment / trading app | 5 |

### 16.2 Hidden network structure

```
Scam phones P1..P4 (one per case)         Linking phone P5
        |                                    |  (appears as callback number
        v                                    |   in two different cases)
 Victims (20) --> Layer-1 mules M1, M2, M3 --+
                       |  (rapid pass-through, minutes apart)
                       v
              Layer-2 mules M4, M5
                       |
                       v
              Collector account M6
                       |
                       v
              Cash-out account M7 ---> Withdrawals (ATM/branch, synthetic locations)
```

Account count: M1 to M7 are the network (7 accounts) plus D1, a legitimate high-volume decoy account, for a total of 8 bank accounts.
Phone count: P1 to P5 network-related, P6 a decoy (a shared family or business number that appears in two complaints innocently).
Devices: one device shared between two layer-1 mule accounts and one cash-out login (a deterministic link); one device shared only with the decoy.

### 16.3 What must be discoverable and by which mechanism

| Hidden relationship | Discovery mechanism |
|---|---|
| Layer-1 mules M1 and M2 share a device | [DET] exact match -> [GRAPH] edge |
| Funds from Cases 1 and 3 converge on M6 | [GRAPH] path analysis |
| Case 2 and Case 4 link only through narrative (complaint text mentions the same callback number written in a different format, and the same "agent name") | [NEM] interpretation, then [DET] normalised matching to confirm |
| Complaint says transfer occurred "after lunch" while ledger shows a late-night transfer | [DET] candidate + [NEM] material-contradiction judgement |
| Order of events in Case 3 (victim says call came before the transfer; communication log suggests a first contact days earlier) | [NEM] chronology reconstruction |
| Withdrawals follow collector inflows within a short window | [DET] time-gap + [GRAPH] path |
| Why the whole thing is one operation | [NEM] causal reconstruction with cited evidence |

### 16.4 Planted contradictions (4)

1. Amount in complaint differs from ledger amount (digit transposition).
2. Complaint time of transfer is inconsistent with the transaction timestamp.
3. Two victims describe the same "officer" with different phone numbers that normalise to the same number.
4. A victim's stated bank differs from the bank on the matching transaction record.

### 16.5 Decoys (false-positive tests)

- D1: a legitimate account with high inflow and outflow (small shop). Must not be pulled into the cluster or must be ranked low with a clear reason.
- P6: a shared number between two unrelated complaints (a victims' family contact). Must be flagged as a weak, explainable link, not a network member.
- A coincidental same-amount transfer pair unrelated to the network.

### 16.6 Held-out real-time slice

The last 6 to 8 events (including one new complaint and one new transfer touching M6) are withheld from the initial load and replayed during the live-detection demo.

---

## 17. Backend Development Plan

Technology choices are recommendations here and are finalised in the Technical Documentation. Selection criteria: simplicity, reliability, Codex familiarity.

| Concern | Recommendation | Rationale |
|---|---|---|
| Language/framework | Python with FastAPI | Fast to build, typed validation, Codex-friendly |
| Database | SQLite (single file) | Zero setup, adequate for the dataset |
| Graph | In-memory graph library built from the database, with deterministic rebuild | No separate graph server to fail |
| Auth | Token-based session with hashed passwords, two demo roles | Credible and simple |
| Config | Environment variables | No hardcoded secrets |
| Reasoning calls | HTTP client to an OpenAI-compatible Nemotron endpoint | Endpoint and model name configurable |

### 17.1 Backend modules

| Module | Responsibility | Priority | Logic |
|---|---|---|---|
| Config | Load environment, refuse to start with missing secrets in non-demo mode | MUST | [DET] |
| Data model | Schemas for entities, relationships, evidence | MUST | [DET] |
| Ingestion | Validate, normalise, assign evidence IDs, reject bad input | MUST | [DET] |
| Extraction | Exact identifier extraction and link creation | MUST | [DET] |
| Graph service | Build, update, query graph; clusters, paths | MUST | [GRAPH] |
| Risk engine | Compute factors and priority with explanations | MUST | [DET]+[GRAPH] |
| Case service | Create and manage cases from clusters or alerts | MUST | [DET] |
| Chronology service | Sort events, compute gaps, expose timeline | MUST | [DET] |
| Reasoning orchestrator | Build bounded prompts, call Nemotron, parse and validate | MUST | [NEM] |
| Evidence validator | Reject or flag any cited ID that does not exist | MUST | [DET] |
| Auth and RBAC | Login, roles, endpoint protection | MUST | [DET] |
| Audit log | Append-only record of significant actions | MUST | [DET] |
| Event simulator | Replay held-out events through the pipeline | SHOULD | [DET] |
| Contradiction candidate finder | Compare narrative-derived fields with structured records | SHOULD | [DET] |
| Masking service | Mask PII in API responses by role | MUST | [DET] |

### 17.2 API principles

- Every endpoint authenticated except login and a health check.
- Every input validated against a schema; unknown fields rejected.
- Pagination on list endpoints.
- Errors return a safe message and an error code; no stack traces to clients.
- AI-derived outputs are always labelled with their source (deterministic, inferred, Nemotron) and an evidence list.

---

## 18. Frontend Development Plan

Design intent: a serious investigation workspace, calm and dense with meaning, not a flashy AI dashboard. Dark-neutral or light-neutral professional palette, restrained accent colours reserved for risk and evidence state, minimal clutter.

### 18.1 Screens

| Screen | Purpose | Priority |
|---|---|---|
| Login | Authenticate; shows synthetic-data banner | MUST |
| Dashboard | Fraud activity overview, alerts feed, top priority cases | MUST |
| Case page | Summary, risk factors, findings, plan, review controls | MUST |
| Network view | Interactive graph | MUST |
| Timeline view | Chronology with evidence | MUST |
| Evidence explorer | Browse and search records and their citations | SHOULD |
| Audit log view | Investigator and admin view of recorded actions | SHOULD |

### 18.2 Network view capabilities

| Capability | Priority |
|---|---|
| Zoom and pan | MUST |
| Node and edge inspection (metadata, evidence IDs) | MUST |
| Search by identifier | MUST |
| Cluster isolation | MUST |
| Fraud-chain highlighting | MUST |
| Transaction inspection | MUST |
| Filtering by entity type, time window, amount, confidence | SHOULD |
| Distinguish exact, inferred and weak links visually | MUST |
| Risk-based node sizing or colouring with legend | SHOULD |

### 18.3 Frontend rules

- Never display an AI statement without its evidence list and confidence.
- Never use the words guilty, criminal or fraudster for a specific entity; use risk indicator, potential relationship, hypothesis.
- Show a persistent banner: "Synthetic data. Investigation-support prototype. Not for enforcement decisions."
- Graceful degradation: if the graph fails to render, a tabular fallback of entities and links is available.
- Performance target: network view responsive with up to a few hundred nodes.

---

## 19. Graph System Plan

### 19.1 Graph model

Nodes: Victim, Person/Entity, Bank Account, UPI ID, Phone Number, Device, Transaction (optionally as an edge attribute or node), Withdrawal, Complaint, Incident.
Edges: relationships listed in Section 8.2, each with timestamp, source, evidence ID, confidence, amount (where relevant), relationship type.

### 19.2 Graph operations

| Operation | Purpose | Priority | Logic |
|---|---|---|---|
| Build from database | Deterministic, repeatable | MUST | [GRAPH] |
| Incremental update on new event | Real-time behaviour | SHOULD | [GRAPH] |
| Connected components / clustering | Isolate candidate networks | MUST | [GRAPH] |
| Money-flow path finding with time ordering | Reconstruct chain | MUST | [GRAPH] |
| Shared-identifier detection | Common phone, device, account | MUST | [DET]+[GRAPH] |
| Fan-in / fan-out and pass-through detection | Mule behaviour | MUST | [GRAPH]+[DET] |
| Centrality (degree, betweenness) | Hub identification | SHOULD | [GRAPH] |
| Community detection | Sub-structure within large clusters | NICE | [GRAPH] |
| Subgraph extraction for a case | Bounded reasoning input | MUST | [GRAPH] |

### 19.3 Link strength model

| Strength | Definition | Example | Created by |
|---|---|---|---|
| Exact | Identical normalised identifier or direct recorded transfer | Same device ID on two accounts | [DET] |
| Inferred | Proposed by Nemotron with cited evidence and confidence | Two complaints describe the same callback number in different formats, later confirmed by normalisation | [NEM] then [DET] check |
| Weak | Possible coincidence, flagged for review | P6 shared family number | [DET] heuristics |

Weak links must not be allowed to merge clusters on their own; they are displayed but excluded from cluster membership unless the investigator promotes them.

### 19.4 Graph design guardrails

- Prevent over-merging: a single shared common identifier (for example a public helpline number) must not collapse unrelated cases. Maintain an allow-list of known benign identifiers within the synthetic data.
- Time-aware paths: a money-flow path is valid only if transfer times are consistent with order.
- Bounded subgraphs: reasoning inputs are limited to a case subgraph, never the whole graph.

---

## 20. Risk Scoring Plan

### 20.1 Principles

The output is a **Risk Score / Investigation Priority**, never a guilt probability. It is deterministic, reproducible, and fully explained. Nemotron may describe the score in words but never computes or alters it.

### 20.2 Proposed factors (weights are initial values to be tuned on the synthetic data)

| Factor | Description | Indicative max points | Priority |
|---|---|---|---|
| Rapid fund movement | Inflow forwarded within a short window | 20 | MUST |
| Account hopping | Multi-hop pass-through chain depth | 15 | MUST |
| Shared identifiers | Common phone, device or UPI across otherwise separate cases | 20 | MUST |
| Multiple victims | Distinct victims paying the same account | 15 | MUST |
| Multiple linked complaints | Complaints referencing the entity or its identifiers | 10 | MUST |
| Unusual transaction pattern | Deviation from the account's baseline in the dataset | 10 | SHOULD |
| Suspicious timing | Clustered bursts, night-time cluster, immediate cash-out | 5 | SHOULD |
| Connection to previously flagged synthetic entity | Proximity to an entity already flagged by an investigator | 10 | SHOULD |
| Graph centrality | Unusually high betweenness in the cluster | 5 | SHOULD |
| Mitigating factors | Evidence consistent with ordinary behaviour (stable history, single-source inflows) | negative adjustment | SHOULD |

Total is normalised to 0 to 100 and banded: **Low, Medium, High, Critical priority**.

### 20.3 Required explanation format

Each score shows: total, band, per-factor points, the data each factor used, the evidence IDs behind each factor, and any mitigating factors. A fixed disclaimer is attached: "Investigation priority, not an indicator of guilt."

### 20.4 Risk scoring tests

- Same input produces the same score every run.
- Decoy D1 scores below the network accounts with mitigating factors displayed.
- Changing a single input changes only the expected factors.

---

## 21. Real-Time Detection Plan

### 21.1 Scope

A lightweight simulation, not a streaming platform. The held-out slice from Section 16.6 is replayed through the same code path real events would use.

### 21.2 Pipeline

```
New event
   -> validation
   -> feature extraction
   -> graph update
   -> risk evaluation
   -> alert (if threshold crossed)
   -> optional Nemotron reasoning (investigator-triggered or rate-limited auto-queue)
   -> investigator review
```

| Step | Logic | Priority |
|---|---|---|
| Event endpoint and simulator controls (play, pause, step) | [DET] | SHOULD |
| Validation and evidence ID assignment | [DET] | MUST (shared with ingestion) |
| Incremental graph update | [GRAPH] | SHOULD |
| Re-score affected entities only | [DET] | SHOULD |
| Alert generation with reason summary | [DET] | SHOULD |
| Nemotron reasoning on alert | [NEM] | SHOULD, never blocks the alert |
| Live push to UI (polling or server-sent events) | [DET] | SHOULD |

**Rule:** the alert must fire from deterministic logic alone. Nemotron enrichment arrives afterwards and is clearly marked as pending, complete or unavailable.

---

## 22. Explainability Plan

### 22.1 Standard finding format

Every finding shown to an investigator contains:

| Field | Content |
|---|---|
| Finding | One plain-language statement, phrased as a potential relationship or hypothesis |
| Evidence | List of existing evidence IDs, each with a one-line description |
| Reasoning | Short explanation of how the evidence supports the finding |
| Counter-evidence / gaps | What weakens or is missing |
| Confidence | Low, Medium or High, with rationale |
| Source type | Deterministic, graph, or Nemotron-inferred |
| Recommended next step | One concrete action for the investigator |
| Review state | Pending, accepted, rejected, needs more evidence |

Example:

> **Finding:** Account B may be connected to the same fraud network as Account C.
> **Evidence:** E12 (shared phone identifier), E19 (transfer within 7 minutes), E24 (common device), E27 (linked complaint).
> **Confidence:** Medium.
> **Recommended next step:** Review Account C's outgoing transactions.

### 22.2 Grounding guardrails

1. The prompt supplies the exact list of permitted evidence IDs.
2. The model must answer in a defined structured format.
3. A deterministic validator rejects any ID not in the permitted list and any finding with no evidence.
4. Rejected findings are logged and not shown as findings; the UI may show "N AI statements were withheld for lacking valid evidence."
5. The model is instructed to state uncertainty and to say "insufficient evidence" instead of guessing.
6. Language guard: outputs containing accusatory terms are flagged and rewritten or withheld.

---

## 23. Nemotron Integration Plan

### 23.1 Why Nemotron is essential here

The hardest part of the problem is not matching identifiers; it is reasoning across long, messy, partially conflicting evidence from many sources and turning it into a defensible chronology, causal chain and plan. Nemotron is used only for these reasoning-heavy tasks. If Nemotron were removed, FraudMesh would still show a graph and a score, but it could not interpret complaints, reconcile contradictions, reconstruct causality or produce an evidence-backed plan. That dependency is intentional and should be demonstrated in the presentation.

### 23.2 Nemotron tasks

| Task | Input | Output | Priority |
|---|---|---|---|
| T1 Complaint interpretation | One complaint text plus allowed entity list | Structured extraction: claimed identifiers, amounts, times, narrative events, uncertainty | MUST |
| T2 Cross-evidence reasoning | Case subgraph plus evidence digest | Candidate relationships between entities with evidence | MUST |
| T3 Contradiction resolution | Candidate conflicts from software plus source records | Which are material, likely explanation, effect on chronology | SHOULD |
| T4 Chronology reconstruction | Case events with conflicting or missing times | Plausible ordered sequence with stated uncertainty | MUST |
| T5 Causal reconstruction | Chronology plus graph paths | Precursor -> Trigger -> Movement -> Amplification -> Outcome with cited evidence | MUST |
| T6 Investigative hypotheses | Findings so far | Ranked hypotheses with confidence and counter-evidence | MUST |
| T7 Investigation plan | Hypotheses plus gaps | Ranked next steps, each tied to evidence and rationale | MUST |
| T8 Relationship explanation | Two entities plus connecting evidence | Plain-language explanation | SHOULD |
| T9 Case summary | Findings | Investigator-facing summary | SHOULD |

### 23.3 Integration rules

- **Bounded context:** send only the case subgraph and relevant evidence, with evidence IDs, never raw whole databases.
- **Structured output:** every task has a defined output schema; invalid output triggers one repair retry, then graceful degradation.
- **Allowed-ID list in every prompt.**
- **Temperature kept low** for reproducibility; the exact settings are defined in the Technical Documentation.
- **Cache:** responses are cached by task and input hash; a cached-reasoning mode serves pre-validated outputs if the endpoint is unavailable (see Section 28).
- **No model-computed numbers:** amounts, counts, scores and time gaps are always supplied by software and verified; the model may reference but not recompute them.
- **No secrets or PII beyond what the task needs:** masked identifiers are used in prompts where exact values are not required for reasoning.
- **Prompt and response logging** (with masking) for audit and debugging.
- **Configurable endpoint and model name** through environment variables; no vendor-specific claims hardcoded.
- **Timeouts and rate limits** with clear UI status when reasoning is pending or unavailable.

### 23.4 Nemotron success measures

- Complaint interpretation extracts the key identifiers and narrative events at a rate defined in Section 25.
- Causal chain matches the ground-truth chain on the key stages.
- Zero invented evidence IDs reach the investigator.
- Hypotheses distinguish evidence from speculation.

---

## 24. Security and Privacy Plan

Honest framing: this is a prototype that demonstrates sound practices. It must not claim enterprise-grade security.

| Area | Plan | Priority |
|---|---|---|
| Synthetic data by default | Dataset flagged `synthetic: true`; loader refuses unflagged data; visible UI banner | MUST |
| Data separation | Separate directories and database files for demo and any authorised data; no mixing | MUST |
| Authentication | Password hashing, session or token expiry, no default passwords in the repository (demo credentials supplied via environment or setup script) | MUST |
| Authorization | Role-based access: Investigator (review and annotate) and Admin (view audit, manage users); read/write separation | MUST |
| Audit logging | Append-only log: login, case open, finding review, plan decision, event replay, configuration changes | MUST |
| Secrets | Environment variables; `.env.example` only; secrets never committed or logged | MUST |
| Input validation | Schema validation on every endpoint and ingestion record; size limits; reject unknown fields | MUST |
| Secure API handling | CORS restricted, rate limiting on login and reasoning endpoints, safe error messages | MUST |
| PII masking | Mask phone, account and UPI identifiers by default in UI and prompts (for example, last four visible); unmask permitted for Investigator on explicit action, logged | MUST |
| Data minimisation | Prompts and API responses include only fields needed for the task | MUST |
| Prompt-injection resistance | Complaint and communication text is treated as untrusted data: delimited in prompts, instructions inside evidence ignored, outputs validated | MUST |
| Encryption considerations | HTTPS in any non-local deployment; password hashing; note that data-at-rest encryption is documented as a production requirement and not claimed as implemented unless it is | SHOULD |
| Dependency hygiene | Pinned versions, minimal dependencies | SHOULD |
| Limitation disclosure | A "Limitations and Safeguards" page listing what is not implemented | MUST |

### 24.1 Prompt-injection note

Synthetic complaints should include at least one adversarial instruction (for example, text telling the model to ignore previous instructions) to prove the delimiting and validation controls work.

---

## 25. Testing Plan

| Layer | What is tested | Method | Priority |
|---|---|---|---|
| Data generator | Reproducibility, counts match targets, ground truth consistent | Unit tests | MUST |
| Ingestion | Valid records accepted, invalid rejected with reason, evidence IDs unique and stable | Unit tests | MUST |
| Normalisation and matching | Phone/account/UPI format variants resolve identically; no false exact matches | Unit tests with edge cases | MUST |
| Graph | Components, paths, time-ordering rule, weak-link exclusion | Unit tests against known subgraphs | MUST |
| Risk engine | Determinism, factor breakdown, decoy scoring, monotonic behaviour | Unit tests | MUST |
| API | Auth required, RBAC enforced, validation errors, pagination | Integration tests | MUST |
| Audit | Every defined action produces a record; log cannot be edited via API | Integration tests | MUST |
| Reasoning orchestrator | Schema validation, retry, degradation, caching | Tests with mocked model responses | MUST |
| Evidence validator | Fabricated IDs rejected; empty-evidence findings rejected | Unit tests with adversarial outputs | MUST |
| Nemotron live | Real calls on seed cases produce valid structure | Manual and scripted checks | MUST |
| Prompt injection | Injected instructions in complaints do not change behaviour | Scripted adversarial cases | MUST |
| Real-time | Replay produces alert, graph growth, re-score | Integration test | SHOULD |
| Frontend | Core flows (login, case open, graph interaction, review) | Manual checklist; smoke automation if time | MUST (manual) |
| End to end | Full demo script from clean start | Rehearsal run, timed | MUST |
| Failure injection | Nemotron timeout, invalid JSON, DB missing, graph render failure | Manual failure drills | MUST |

Testing rule: Codex runs the automated tests after each milestone; no milestone is closed with failing tests.

---

## 26. Evaluation Metrics

Evaluation compares system output with the ground-truth file.

| Metric | Definition | Target |
|---|---|---|
| Entity recall | Ground-truth entities found / total | >= 95% |
| Link recall | Ground-truth links found / total | >= 90% |
| Link precision | Correct links / links produced (exact links) | 100% for exact; >= 85% for inferred |
| Cluster purity | Network members in the hidden cluster / cluster size | >= 90% |
| Cluster coverage | True network members captured | >= 90% |
| Decoy rejection | Decoys excluded from cluster or flagged weak | 100% |
| Chain accuracy | Key stages of the money chain correctly ordered | >= 90% |
| Chronology accuracy | Ground-truth event pairs correctly ordered | >= 95% |
| Contradiction recall | Planted contradictions detected | 4 of 4 (minimum 3 of 4) |
| Evidence-ID validity | Cited IDs that exist | 100% |
| Hallucinated-claim rate | Statements with unsupported facts after validation | 0 shown to investigators |
| Complaint extraction accuracy | Identifiers and key facts correctly extracted from complaints | >= 90% |
| Latency (deterministic pipeline) | Event to alert | < 3 seconds |
| Latency (Nemotron task) | Single reasoning task | Reported; target < 60 seconds with visible progress |
| Score reproducibility | Same score on repeated runs | 100% |
| Demo reliability | Successful clean end-to-end runs in rehearsal | >= 5 of 5 |

Results are recorded in an evaluation report that is shown in the presentation, with honest notes about where the system fails.

---

## 27. Demo Preparation

### 27.1 Demo script (aligned with the target demo)

| Step | Action | What judges should see |
|---|---|---|
| 1 | Investigator logs in | Authentication; synthetic-data banner |
| 2 | Dashboard shows fraud activity | Four separate cases, alert feed, priority list |
| 3 | A suspicious event appears | Replay of held-out event; alert fires from deterministic logic |
| 4 | Risk engine evaluates it | Score with factor breakdown |
| 5 | Graph updates | New nodes and edges animate in |
| 6 | Related accounts become visible | Cluster expands; four "separate" cases merge into one network |
| 7 | Investigator opens the case | Case page with summary |
| 8 | Timeline reconstructs sequence | Ordered events with evidence IDs |
| 9 | Evidence displayed | Evidence explorer with citations |
| 10 | Nemotron reasons across evidence | Progress indicator, then structured result |
| 11 | Fraud chain is explained | Causal chain, highlighted path in the graph |
| 12 | Risk factors shown | Per-factor explanation |
| 13 | Recommended next steps | Ranked plan with rationale |
| 14 | Investigator reviews | Accept / reject / annotate |
| 15 | Action recorded | Audit log entry visible |

### 27.2 Demo hardening

- Start-from-clean script that resets the database, loads the seed dataset and loads the cached reasoning set.
- A "live mode" and a "cached mode" toggle, clearly labelled in the UI.
- Pre-validated cached Nemotron outputs for every demo task.
- Recorded backup video of the full flow.
- Offline-capable run (no dependency on venue network except Nemotron live mode).
- A one-page runbook listing commands, credentials source, and recovery steps.
- Rehearsal at least five times, including two with induced failures.

---

## 28. Failure and Fallback Strategy

| Failure | Detection | Fallback | User-visible behaviour |
|---|---|---|---|
| Nemotron endpoint unreachable or slow | Timeout, HTTP error | Serve cached validated reasoning (if input hash matches), else degrade to deterministic-only view | Banner: "Reasoning unavailable — showing deterministic analysis" or "Cached reasoning (not live)" |
| Nemotron returns invalid structure | Schema check fails | One repair retry, then discard | "AI output could not be validated" with option to retry |
| Nemotron cites invalid evidence | Evidence validator | Remove finding; log | Count of withheld statements shown |
| Nemotron makes an accusatory statement | Language guard | Rewrite template or withhold | Safe wording shown |
| Rate limit or credit exhaustion | Error codes | Switch to cached mode | Cached-mode label |
| Graph rendering failure | Frontend error boundary | Table view of entities and links | "Showing table view" |
| Database corrupted or missing | Startup check | Re-run reset-and-seed script (reproducible) | Setup message |
| Event simulator misfire | Step controls | Manual step or preloaded state | Reset button |
| Authentication problem on stage | Pre-checked credentials | Documented recovery account via environment | None |
| Scope slip | Weekly milestone review | Cut SHOULD and NICE items, never MUST | Not applicable |
| Total laptop failure | — | Backup machine with same repository and recorded video | None |

**Design rule:** every demo moment must have a fallback that is honest about being a fallback.

---

## 29. Timeline with Realistic Phases

Assumption: seven build days, one buffer day, and one demo-preparation day. Hours are indicative for a small team using Codex for implementation. If only 48 hours exist, use the compressed column.

| Phase | Standard schedule | 48-hour compression | Key outputs | Gate to proceed |
|---|---|---|---|---|
| 0 Foundations | Day 0 | Hours 0 to 3 | Approved plan and PRD summary, repo skeleton, config, Nemotron smoke test | Nemotron returns a valid response |
| 1 Data and deterministic core | Day 1 | Hours 3 to 10 | Generator, ground truth, database, ingestion, extraction, evidence IDs | Tests pass; counts match targets |
| 2 Graph and risk | Day 2 | Hours 10 to 18 | Graph, clusters, paths, risk engine, case objects | Hidden cluster isolated; decoys excluded |
| 3 Interface and security | Days 3 to 4 | Hours 18 to 28 | Auth, audit, dashboard, case, network view, timeline | Login -> case -> graph works |
| 4 Nemotron reasoning | Days 4 to 5 | Hours 24 to 36 (overlaps phase 3) | T1, T4, T5, T6, T7, validator, findings UI | Zero invalid IDs shown; chain matches ground truth |
| 5 Real-time and polish | Day 6 | Hours 36 to 42 | Simulator, alerts, contradictions, filters, evidence explorer | Live-alert moment works |
| 6 Hardening and demo | Days 7 to 8 | Hours 42 to 48 | Cache mode, tests, evaluation report, rehearsals, slides | 5 clean rehearsals (3 in compressed plan) |

**Cut order when behind (cut from the bottom first):**

1. NICE TO HAVE items.
2. Advanced graph analytics and community detection.
3. Audit log view and evidence explorer (keep the recording of audit events).
4. Contradiction detection UI (keep the backend candidate list).
5. Real-time simulator (fall back to a scripted "new event" button that runs the same pipeline once).

Never cut: synthetic data, evidence IDs, graph, risk explanation, timeline, Nemotron causal reconstruction with validation, authentication, audit logging, end-to-end demo.

---

## 30. Hackathon Presentation Preparation

### 30.1 Narrative arc (about 5 to 7 minutes)

1. **The gap (45 sec):** four victims, four "unrelated" complaints, one operation nobody can see.
2. **The idea (30 sec):** "Normal systems see suspicious transactions. FraudMesh sees the fraud network."
3. **Architecture in one slide (45 sec):** deterministic systems + graph + Nemotron + human. Emphasise what Nemotron does and what it does not.
4. **Live demo (3 to 4 min):** the 15-step script, narrated around three "aha" moments: the four cases merging, the reconstructed chain, the evidence-cited explanation.
5. **Trust and safety (45 sec):** evidence validator, no accusations, human review, audit log, honest limitations.
6. **Results (30 sec):** evaluation metrics against ground truth.
7. **Roadmap and close (30 sec):** what it would take to move from synthetic to authorised data.

### 30.2 Slides

| Slide | Content |
|---|---|
| 1 | Title and positioning line |
| 2 | Problem: fragmented evidence, network fraud |
| 3 | Solution pipeline diagram |
| 4 | Division of labour: software vs graph vs Nemotron |
| 5 | Demo (live) |
| 6 | Explainability and safety guardrails |
| 7 | Evaluation results and honest limitations |
| 8 | Roadmap |

### 30.3 Likely judge questions to prepare

- Why is Nemotron necessary rather than rules or graph algorithms alone? (Answer with the T1, T4, T5 examples that rules cannot do.)
- How do you prevent hallucinated evidence? (Validator and allowed-ID list.)
- Is this real bank data? (No; synthetic; no fake integrations.)
- What happens if the model is wrong? (Confidence, counter-evidence, human review, audit log.)
- How would this work with real data? (Authorised data pipelines, legal review, stronger security; clearly future work.)
- Does the risk score mean someone is guilty? (No; investigation priority only.)

### 30.4 Presentation assets

Demo runbook, recorded backup video, screenshot set, one-page architecture diagram, evaluation table, limitations page.

---

## 31. Definition of Done for Every Major Component

A component is Done only when every listed condition is met and verified by Codex running the tests and by a human smoke check.

| Component | Definition of Done |
|---|---|
| Repository and configuration | Runs from a clean clone with documented steps; `.env.example` present; no secrets committed; startup refuses unsafe config |
| Synthetic data generator | Seeded and reproducible; produces target counts; outputs hidden network, decoys, 4 contradictions, injected adversarial text; ground-truth file written; dataset flagged `synthetic: true` |
| Database and data model | All core entities and relationships represented; evidence records have unique stable IDs; reset-and-seed script works in one command |
| Ingestion | Validates every record; rejects invalid with reasons; normalises identifiers; assigns evidence IDs; has tests for malformed input |
| Extraction and matching | Exact matches correct on all format variants; no false exact matches on decoys; every link has source, evidence ID, confidence |
| Graph service | Built from the database in under 5 seconds; clusters, money-flow paths and subgraph extraction work; weak links do not merge clusters; tests pass against ground truth |
| Risk engine | Deterministic; factor breakdown with evidence IDs; bands defined; decoy outranked by network accounts; disclaimer attached; tests pass |
| Case service | Case created from cluster or alert; contains subgraph, evidence, chronology, findings, review state |
| Chronology service | Events ordered by software; gaps computed; conflicts flagged for reasoning; timeline API available |
| Reasoning orchestrator | All MUST tasks (T1, T2, T4, T5, T6, T7) implemented with schemas, bounded context, allowed-ID list, retry, caching, timeout handling |
| Evidence validator | Rejects fabricated IDs and evidence-less findings; adversarial tests pass; rejection counts exposed |
| Authentication and RBAC | Login works; protected endpoints enforced; roles tested; no default passwords in the repository |
| Audit log | All defined actions recorded with actor, time, action, target; append-only through the API; viewable by Admin |
| PII masking | Identifiers masked by default in UI, API and prompts; unmask is explicit and logged |
| Frontend: dashboard and case | Shows alerts, priorities, case summary, risk explanation, findings with evidence and confidence, review controls |
| Frontend: network view | Zoom, pan, search, node/edge inspection, cluster isolation, chain highlight, link-strength styling, table fallback |
| Frontend: timeline | Ordered events with evidence IDs; click-through to evidence and graph |
| Real-time simulator | Replay of held-out events with play/step; alert from deterministic logic; incremental graph and score update; Nemotron enrichment labelled and non-blocking |
| Contradiction handling | Candidates generated deterministically; Nemotron judgement attached; the 4 planted contradictions surfaced |
| Fallback and cache mode | Live/cached toggle; cached outputs pre-validated; every failure in Section 28 drilled once |
| Testing | Automated suites for all MUST layers pass; manual checklist signed off |
| Evaluation | Metrics computed against ground truth; report generated; failures documented honestly |
| Documentation | README and runbook accurate; limitations page present; document chain consistent |
| Demo and presentation | Five clean rehearsals; backup video; slides and speaker notes complete |

---

## 32. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Nemotron access, latency or credits | Medium | High | Early smoke test; caching; cached mode; low call volume via bounded tasks |
| Model hallucination of evidence | Medium | High | Allowed-ID list, validator, schema output |
| Over-scoping | High | High | MUST/SHOULD/NICE discipline; cut order in Section 29 |
| Graph over-merging | Medium | Medium | Weak-link rule, allow-list, time-aware paths |
| Synthetic data too easy or too contrived | Medium | Medium | Decoys, planted contradictions, narrative-only link, noise transactions |
| Frontend graph usability at scale | Low | Medium | Bounded subgraphs, filtering, table fallback |
| Demo failure on stage | Medium | High | Cached mode, backup video, rehearsals |
| Perception as accusatory or unsafe | Low | High | Language guard, banner, human-in-the-loop, limitations page |
| Document drift across chain | Medium | Medium | This plan is source of truth; any change requires updating downstream documents |

---

## 33. Glossary and Terminology (Consistent Across All FraudMesh Documents)

| Term | Meaning |
|---|---|
| Evidence | A stored record with a stable ID (transaction, complaint, communication, device log, account record) |
| Entity | A node: victim, person/entity, account, UPI ID, phone, device, withdrawal, complaint, incident |
| Link / Relationship | An edge between entities with metadata |
| Exact / Inferred / Weak link | Link strength levels defined in Section 19.3 |
| Cluster | A connected group of entities under exact and inferred links |
| Case | An investigator workspace built from a cluster or alert |
| Finding | An evidence-backed statement in the Section 22 format |
| Hypothesis | A finding framed as a possibility with confidence and counter-evidence |
| Investigation Priority / Risk Score | Deterministic explainable score; not guilt |
| Causal chain | Precursor -> Trigger -> Movement -> Amplification -> Outcome |
| Cached mode | Serving pre-validated stored reasoning outputs when live Nemotron is unavailable |

---

## 34. Approval and Change Control

Once approved, this document is the source of truth for the PRD. Changes after approval require: (1) a short change note at the end of this document, (2) a version increment, and (3) review of the PRD, Technical Documentation and Codex Master Prompt for consistency.

**Constraints restated (apply to every downstream document):**

- Do not pretend the prototype has access to real cross-bank data.
- Do not claim it can definitively identify criminals.
- Do not claim the risk score represents guilt.
- Do not build fake integrations and present them as real.
- Use synthetic or authorized data and clearly label limitations.

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-10-07 | Initial project plan |

**— End of FRAUDMESH_PROJECT_PLAN —**
