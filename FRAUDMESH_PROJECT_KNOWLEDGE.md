# FRAUDMESH_PROJECT_KNOWLEDGE.md

## 1. Project Identity

**Project Name:** FraudMesh  
**Product Type:** AI-powered financial fraud investigation web platform

**One-line description:**  
> FraudMesh reconstructs fragmented financial-fraud evidence into an explainable network and investigation plan.

**Short positioning:**  
> Normal systems see suspicious transactions. FraudMesh sees the fraud network.

**Primary objective:**  
Build a real, working web application that helps authorized investigators or fraud analysts connect fragmented fraud evidence, visualize relationships between entities, identify suspicious networks, understand why activity is risky, and organize an investigation.

FraudMesh is a **site/web application only** for this project. It is NOT being presented as a payment processor, banking app, UPI replacement, or direct payment-blocking system.

---

## 2. Core Problem

Modern financial fraud is often a **network problem rather than a single-transaction problem**.

A single fraud case may contain evidence spread across:

- Victim complaints
- Bank accounts
- UPI IDs
- Phone numbers
- Devices
- IP/session information where authorized
- Transactions
- Withdrawals
- Merchant/payment identifiers
- Timestamps
- Communication metadata where legally and appropriately available
- Previous complaints
- Known mule accounts
- Investigation notes
- Other related cases

The difficult part is connecting these fragments.

Two complaints may appear unrelated because they involve different victims, amounts, dates, or accounts. However, they may share:

- The same phone number
- The same UPI ID
- The same device
- The same receiving account
- A chain of intermediate accounts
- Similar transaction timing
- A common withdrawal location
- A recurring entity across previous cases

FraudMesh is designed to expose these hidden relationships.

---

## 3. The Solution

FraudMesh takes fragmented authorized/synthetic fraud evidence and transforms it into:

1. A connected fraud network
2. Entity and relationship analysis
3. Risk scores
4. A chronological view of activity
5. Explainable findings
6. Investigation priorities
7. An evidence-backed investigation plan

### Core pipeline

```text
Evidence Ingestion
        ↓
Entity & Link Extraction
        ↓
Transaction / Relationship Analysis
        ↓
Fraud Graph Construction
        ↓
Chronology & Pattern Reconstruction
        ↓
Risk Scoring
        ↓
Nemotron Reasoning
        ↓
Explainable Findings
        ↓
Investigation Case
        ↓
Investigation Plan
```

---

## 4. Product Boundary

### FraudMesh IS

- A fraud investigation web application
- A fraud-network analysis platform
- A graph-based investigation interface
- An evidence exploration system
- A risk-analysis system
- An explainable AI investigation assistant
- A case-management interface

### FraudMesh IS NOT

- A bank
- A payment gateway
- A UPI application
- Google Pay / PhonePe / Paytm
- A payment authorization system
- A system that can directly block third-party payments
- An autonomous law-enforcement system
- An autonomous account-freezing system
- A replacement for human investigators

Do not claim that FraudMesh can directly stop or block real-world payments unless an authorized financial institution integration is explicitly implemented in a future version.

---

## 5. Target Users

Primary users:

- Financial fraud investigators
- Bank fraud analysts
- Fraud-risk teams
- Compliance/investigation teams
- Authorized financial-crime analysts

For the hackathon, the product should be demonstrated using **synthetic or explicitly authorized data**.

---

## 6. Core User Journey

A typical investigator should be able to:

1. Log into FraudMesh.
2. Open the investigation dashboard.
3. View suspicious cases or alerts.
4. Select a fraud case.
5. Explore related transactions.
6. View the connected fraud network.
7. Click entities such as accounts, phones, devices, UPI IDs, and transactions.
8. Inspect the timeline.
9. See the calculated risk score.
10. Ask/view Nemotron's reasoning about the network.
11. Read evidence-backed explanations.
12. Identify important connections and suspicious patterns.
13. Generate or view an investigation plan.
14. Record investigation actions/findings.
15. Review the audit trail.

---

## 7. Major Features

### 7.1 Fraud Investigation Dashboard

The dashboard should provide a high-level overview:

- Active investigations
- High-risk cases
- Recent alerts
- Connected entities
- Suspicious transaction volume
- Risk distribution
- Investigation status
- Recent activity

The dashboard should be useful rather than decorative.

### 7.2 Fraud Case Management

Each investigation should have a dedicated case page.

A case can contain:

- Case ID
- Case title
- Status
- Risk level
- Victims
- Accounts
- Transactions
- Related entities
- Evidence
- Timeline
- Findings
- Investigation notes
- AI analysis
- Investigation plan
- Audit history

Suggested statuses:

- New
- Under Review
- Investigating
- Escalated
- Resolved
- Closed

### 7.3 Entity Management

FraudMesh should recognize entities such as:

- Person/victim
- Bank account
- UPI ID
- Phone number
- Device
- Transaction
- Merchant
- IP/session identifier where authorized
- Complaint
- Location where appropriately available
- Case

Each entity should have an identifiable node in the fraud graph.

### 7.4 Relationship Detection

Important relationships include:

- Account → transfers → Account
- Person → owns/uses → Account
- Person → uses → Phone
- Person → uses → Device
- Account → linked_to → UPI ID
- Transaction → involves → Account
- Complaint → references → Account
- Complaint → references → Phone
- Device → associated_with → Account
- Case → contains → Transaction
- Case → contains → Evidence

Relationships should include relevant metadata where available, such as:

- Timestamp
- Amount
- Source evidence
- Confidence
- Relationship type

---

## 8. Fraud Graph

The fraud graph is one of FraudMesh's core visual features.

### Example

```text
Victim A
   │
   └── Transaction ──→ Account A
                         │
                         ├──→ UPI ID X
                         │
                         └──→ Account B
                                │
                                ├──→ Phone X
                                │
                                └──→ Device X
                                       │
                                       └──→ Account C
```

A visually connected cluster may reveal that apparently separate complaints are related.

### Graph requirements

The graph should support:

- Zoom
- Pan
- Node selection
- Edge selection
- Filtering
- Search
- Entity-type filtering
- Risk-based highlighting
- Relationship inspection
- Case filtering
- Timeline-aware exploration

The graph should prioritize clarity over visual complexity.

---

## 9. Real-Time Detection — Scope

FraudMesh should support a **real-time-style analysis architecture within the web application**, but the project must not falsely claim direct access to live banking networks.

When a new authorized transaction/evidence event enters the application:

```text
New Evidence
     ↓
Entity Extraction
     ↓
Relationship Update
     ↓
Graph Update
     ↓
Risk Recalculation
     ↓
Alert Generation
     ↓
Nemotron Analysis
     ↓
Investigator Review
```

The implementation can use an application event/API layer and authorized or synthetic event streams.

The important product concept is that the fraud network and risk assessment can change as new evidence arrives.

---

## 10. Risk Scoring

FraudMesh should calculate a risk score using multiple evidence-backed factors.

Example factors:

- Shared phone across cases
- Shared device
- Shared UPI identifier
- Rapid movement of funds
- Multiple incoming victims
- Multiple outgoing transfers
- Unusual transaction frequency
- Transaction timing anomalies
- Known suspicious relationships
- Repeated entity appearance across cases
- Network centrality
- Transaction-chain complexity
- Contradictory evidence

The exact scoring formula should be deterministic and explainable wherever possible.

### Example output

```text
Risk Score: 91/100
Risk Level: HIGH

Reasons:
- Account connected to 4 unrelated victim cases
- Same device associated with 3 accounts
- Rapid fund movement through 2 intermediary accounts
- Shared phone number appears in 5 suspicious records
- High-value transfers occurred shortly after victim payments
```

Risk scores are **investigation indicators**, not proof of criminal activity.

---

## 11. Explainable AI

Every important AI-generated conclusion should be traceable to evidence.

Avoid statements such as:

> "This account is definitely fraudulent."

Prefer:

> "This account is high priority for investigation because it is connected to four unrelated victim cases, shares a device identifier with two other accounts, and received funds that were transferred onward shortly after receipt."

The system should show:

- Finding
- Supporting evidence
- Related entities
- Relevant transactions
- Timeline
- Reasoning
- Confidence/uncertainty where appropriate

---

## 12. Nemotron's Role

Nemotron must have a **meaningful reasoning role**.

FraudMesh should NOT simply use Nemotron as a generic chatbot.

### Deterministic software should handle

- Database operations
- Exact entity matching
- Transaction aggregation
- Numeric calculations
- Timestamps
- Graph construction
- Filtering
- Sorting
- Authentication
- Audit logging
- Basic rule evaluation

### Nemotron should handle tasks such as

- Understanding unstructured complaint text
- Extracting useful entities and relationships from narrative evidence
- Reconciling fragmented evidence
- Detecting contradictions
- Reconstructing chronology from messy evidence
- Connecting contextual clues
- Explaining why multiple cases may be related
- Generating evidence-grounded investigation hypotheses
- Summarizing complex fraud networks
- Suggesting investigation priorities
- Generating an investigator-facing investigation plan

### Core principle

> Use code for precision. Use Nemotron for reasoning over fragmented evidence.

---

## 13. Example Nemotron Analysis

Input evidence:

```text
Complaint 1:
Victim reports payment to UPI X at 10:14.

Complaint 2:
Different victim reports payment to Account B at 10:22.

Transaction records:
Account A → Account B at 10:16
Account B → Account C at 10:25

Device records:
Device D7 associated with Account B and Account C.

Phone records:
Phone P3 associated with UPI X and Account B.
```

Nemotron should be able to reason:

- The complaints may be connected.
- The same phone identifier links the victim-facing UPI identity to Account B.
- Funds moved rapidly from Account A to B and then C.
- The same device links B and C.
- The sequence forms a potentially coordinated transaction chain.
- These relationships justify prioritizing the cluster for investigation.

The AI must distinguish **evidence-backed findings** from hypotheses.

---

## 14. Investigation Plan Generation

FraudMesh should be capable of generating a structured investigation plan.

Example:

```text
Priority 1
Review Account B because it connects multiple cases.

Priority 2
Verify the relationship between Phone P3 and the identified accounts.

Priority 3
Review the 10:14–10:25 transaction chain.

Priority 4
Inspect Device D7's authorized historical associations.

Priority 5
Compare the linked cases for additional common entities.
```

The plan is advisory and must remain subject to human review.

---

## 15. Evidence Explorer

Investigators should be able to inspect evidence behind an AI finding.

Possible evidence types:

- Transaction records
- Complaint text
- Account records
- Phone records
- Device associations
- UPI identifiers
- Timestamps
- Case records
- Investigator notes

Each evidence item should have:

- Evidence ID
- Type
- Source
- Timestamp
- Related entities
- Content/summary
- Reliability or confidence metadata where appropriate

---

## 16. Timeline

Every investigation should have a chronological view.

Example:

```text
10:14 — Victim A sends ₹20,000
10:16 — Account A → Account B
10:22 — Victim B sends ₹15,000
10:25 — Account B → Account C
10:27 — Account C → Account D
10:31 — Complaint created
```

The timeline should help investigators understand the sequence of events.

---

## 17. Privacy & Security

FraudMesh deals with highly sensitive financial information.

The project must follow privacy-by-design principles.

### Requirements

- Use synthetic or authorized data.
- Never expose real personal financial information in the demo.
- Store passwords securely.
- Use secure authentication.
- Apply authorization checks.
- Validate all input.
- Avoid unnecessary collection of personal information.
- Maintain audit logs for important investigator actions.
- Protect sensitive fields.
- Do not expose internal secrets or API keys to the frontend.
- Avoid hardcoded credentials.
- Keep AI prompts and responses appropriately controlled.
- Clearly distinguish demonstration data from real financial data.

---

## 18. Human-in-the-Loop

FraudMesh must not make autonomous accusations.

AI output should be framed as:

- Risk indicator
- Investigation priority
- Potential relationship
- Investigative hypothesis
- Evidence-backed finding
- Suggested next step

A human investigator remains responsible for final decisions.

FraudMesh should never autonomously:

- Arrest someone
- Freeze an account
- Seize funds
- Contact law enforcement
- Declare someone guilty
- Take irreversible financial action

---

## 19. Demo Dataset

For the hackathon demonstration, create a realistic synthetic dataset.

Suggested scale:

- ~20 victims
- 50+ transactions
- 8+ bank accounts
- 6+ phone numbers
- Multiple UPI IDs
- Multiple devices
- Multiple complaints
- Multiple apparent cases
- At least one hidden connected fraud network
- Several unrelated legitimate transactions
- Some ambiguous/contradictory evidence

The dataset should be complex enough that simple manual inspection does not immediately reveal the complete network.

---

## 20. Recommended Demo Story

### Stage 1 — Dashboard
Show several investigations and risk levels.

### Stage 2 — Open a suspicious case
Show victim complaint and transaction evidence.

### Stage 3 — Open Network Graph
Reveal connections to other accounts/cases.

### Stage 4 — Expand the network
Show shared phone/device/UPI identifiers.

### Stage 5 — Timeline
Show the movement of funds chronologically.

### Stage 6 — Risk Score
Show the score and individual contributing factors.

### Stage 7 — Nemotron Analysis
Show an evidence-grounded explanation of how the cases connect.

### Stage 8 — Investigation Plan
Generate prioritized next steps.

### Final message

> "What looked like several separate fraud complaints is actually one connected network."

---

## 21. Recommended Site Structure

```text
/
├── Login
├── Dashboard
├── Investigations
│   ├── Case List
│   └── Case Details
├── Fraud Network
├── Transactions
├── Alerts
├── Evidence
├── AI Analysis
├── Investigation Plans
├── Audit Log
└── Settings
```

Exact routing may change during implementation, but the product should preserve this conceptual structure.

---

## 22. UI/UX Direction

The site should feel like a professional investigation platform, not a generic AI dashboard.

Preferred design:

- Dark professional interface
- Strong information hierarchy
- Clean cards
- Graph visualization as a central visual element
- High-risk alerts clearly visible
- Minimal unnecessary decoration
- Clear typography
- Responsive layout
- Fast navigation
- Investigator-focused workflows

Avoid:

- Excessive gradients
- Generic chatbot layouts
- Fake futuristic decoration
- Excessive animations
- Unnecessary landing-page sections
- AI-generated-looking clutter

The product should look credible enough to be shown to a bank fraud-analysis team.

---

## 23. Architecture Principle

Conceptual architecture:

```text
                 ┌───────────────────────┐
                 │      FraudMesh UI     │
                 │       Web App         │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │      Backend/API      │
                 └───────────┬───────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Transaction │    │ Fraud Graph │    │   Evidence  │
   │ / Rules     │    │ / Entities  │    │   Store     │
   └─────────────┘    └─────────────┘    └─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                 ┌───────────────────────┐
                 │   Nemotron Reasoning  │
                 │        Layer          │
                 └───────────┬───────────┘
                             ▼
                 ┌───────────────────────┐
                 │ Findings / Risk /    │
                 │ Investigation Plan   │
                 └───────────────────────┘
```

The exact technology stack is determined during technical planning and implementation.

---

## 24. Development Principle

The project must be developed as a **real working application**.

Do not build:

- Static screenshots
- Fake buttons
- Hardcoded graph screenshots
- Fake AI responses presented as live reasoning
- Fake payment-blocking claims
- Pure frontend-only mockups

Every major UI feature should connect to functioning application logic.

For hackathon demonstration, synthetic data is acceptable and expected, but the application itself should genuinely process that data.

---

## 25. Implementation Priorities

### MUST HAVE

1. Working web application
2. Authentication
3. Dashboard
4. Fraud case management
5. Evidence ingestion/display
6. Entity extraction/management
7. Fraud graph
8. Transaction analysis
9. Risk scoring
10. Timeline
11. Explainable findings
12. Nemotron integration
13. Investigation plan
14. Audit logging
15. End-to-end working demo
16. Synthetic/authorized dataset

### SHOULD HAVE

1. Real-time event processing architecture
2. Contradiction detection
3. Advanced graph filtering
4. Evidence explorer
5. Network analytics
6. Advanced risk factors
7. Better investigation workflows
8. Search across cases/entities

### NICE TO HAVE

1. Advanced streaming infrastructure
2. Advanced graph algorithms
3. Multiple investigator roles
4. Advanced analytics
5. Production-scale infrastructure
6. External authorized integrations

Do not sacrifice MUST HAVE functionality to add NICE TO HAVE features.

---

## 26. Success Criteria

FraudMesh is successful if a reviewer can understand within a few minutes that:

1. Fraud evidence is fragmented.
2. FraudMesh connects the fragments.
3. The system creates a meaningful fraud network.
4. The graph exposes hidden relationships.
5. Risk scoring prioritizes important cases.
6. The timeline reconstructs events.
7. Nemotron provides meaningful reasoning over complex evidence.
8. Every important AI conclusion can be traced back to evidence.
9. The investigator receives a useful investigation plan.
10. The entire workflow works end-to-end.

---

## 27. Core Differentiator

FraudMesh should not be positioned as:

> "An AI chatbot for fraud."

It should be positioned as:

> "An AI-powered fraud-network reconstruction and investigation platform."

The central innovation is the combination of:

**Fragmented Evidence + Graph Relationships + Temporal Reconstruction + Risk Scoring + Nemotron Reasoning + Explainable Investigation**

---

## 28. Important Product Language

Use:

- "risk score"
- "investigation priority"
- "potential relationship"
- "evidence-backed finding"
- "investigative hypothesis"
- "suspicious network"
- "requires human review"

Avoid:

- "criminal"
- "guilty"
- "definitely fraudulent"
- "automatically arrests"
- "automatically freezes accounts"
- "guaranteed fraud"

unless explicitly quoting source evidence or describing a hypothetical future system.

---

## 29. Project Documentation Chain

The project documentation should follow this order:

```text
FRAUDMESH_PROJECT_KNOWLEDGE.md
             ↓
FRAUDMESH_PROJECT_PLAN.md
             ↓
FRAUDMESH_PRD.md
             ↓
FRAUDMESH_TECHNICAL_DOCUMENTATION.md
             ↓
FRAUDMESH_CODEX_MASTER_PROMPT.md
             ↓
Implementation
             ↓
Testing
             ↓
Final Demo
```

This file is the **stable project knowledge/source-of-truth document**.

Other project documents should remain consistent with it.

---

## 30. Codex Responsibility

Codex is the primary coding/building agent.

Codex should use this knowledge as the product context when implementing FraudMesh.

Claude/other planning tools may be used for:

- Product planning
- Architecture discussion
- Documentation
- Research
- Requirement refinement

Codex should handle:

- Project setup
- Frontend implementation
- Backend implementation
- Database implementation
- Graph implementation
- Nemotron integration
- Authentication
- Testing
- Debugging
- Integration
- Final build

Do not let documentation drift away from the actual implementation.

---

## 31. Non-Negotiable Constraints

1. FraudMesh remains a **web application/site** for this project.
2. It must be a working application, not a static mockup.
3. Use synthetic or authorized financial data.
4. Do not claim unauthorized access to banks or payment apps.
5. Do not claim the website can directly block third-party UPI/payment transactions.
6. Nemotron must have a meaningful reasoning role.
7. AI findings must be explainable and evidence-grounded.
8. Risk scores are indicators, not proof of guilt.
9. Human investigators remain in control.
10. Security and privacy must be considered throughout development.
11. Deterministic calculations should not be delegated unnecessarily to an LLM.
12. Do not expose secrets/API keys in frontend code.
13. Do not use fake AI output while presenting it as live model reasoning.
14. Prioritize a complete end-to-end workflow over excessive feature count.

---

## 32. Final Product Definition

**FraudMesh is a working AI-powered web platform for financial-fraud investigation that transforms fragmented fraud evidence into connected networks, chronological event views, explainable risk scores, and evidence-grounded investigation plans using graph analysis and Nemotron reasoning.**

The website is the product interface.

The goal is not to stop payments directly.

The goal is to help investigators answer:

> **"Are these separate fraud incidents actually connected, how are they connected, what evidence supports that connection, and what should we investigate next?"**
