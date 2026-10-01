# Release Control Board (v0.1 Release Management)

**Last Updated:** [YYYY-MM-DD] | **Project Mode:** Shipping Mode
**Overall Goal:** Deliver and field-verify the first validated public release (`v0.1 Public Beta`).

> [!NOTE]
> This control board is the live source of truth for release progress. It is continuously updated by `release-coordinator` as new empirical evidence is gathered from runtime discovery, execution, or independent audits.

---

## 🗺️ Release Documentation Map

| Document | Primary Function | Direct Link |
|---|---|:---:|
| **Release Contract** | Frozen scope boundaries and the 6 release criteria | [01_RELEASE_CONTRACT.md](./01_RELEASE_CONTRACT.md) |
| **Operating Manual** | Shipping Mode cycle, proof rules, and escalation matrix | [02_OPERATING_MANUAL.md](./02_OPERATING_MANUAL.md) |
| **Delegation Record** | Coordinator permissions vs. reserved founder decisions | [03_DELEGATION_RECORD.md](./03_DELEGATION_RECORD.md) |
| **Agent Roles & Prompts** | Agent roles, skills, and subagent boundaries | [04_ROLE_PROMPTS.md](./04_ROLE_PROMPTS.md) |
| **Current Sprint (S01)** | Active sprint targets and focus paths | [sprints/sprint_S01.md](./sprints/sprint_S01.md) |
| **Reports Directory** | Field test logs, probe results, and audit reports | [reports/](./reports/) |

---

## 📊 Release Criteria Field Status

| Criterion | Target Requirement | Technical State | Latest Evidence & Deploy Identity | Environment & Date | Weekly Founder Status |
|:---:|---|:---:|---|:---:|:---:|
| **Criterion 1** | **User Journey Initiation** | 🟡 **IN_PROGRESS** | Testing user entrypoint and stable session ID generation. | Staging / Prod<br>[YYYY-MM-DD] | ⏸️ Under Review |
| **Criterion 2** | **Processing & Tracking** | ❓ **UNKNOWN** | Blocked on Criterion 1 verification and stable ID generation. | — | ⏸️ Blocked on Criterion 1 |
| **Criterion 3** | **Result Accuracy & Evidence** | ❓ **UNKNOWN** | Awaiting backend service pipeline completion and verification. | — | ⏸️ Blocked on Criterion 1 |
| **Criterion 4** | **UI Integrity & UX** | 🟡 **PARTIAL_PASS** | Core input interface verified; full end-to-end output presentation pending. | Staging<br>[YYYY-MM-DD] | ⏸️ Under Review |
| **Criterion 5** | **Data Freshness & Storage** | ❓ **UNKNOWN** | Requires two consecutive automatic ingestion cycles and verifiable retrieval. | Staging<br>[YYYY-MM-DD] | ⏸️ Under Review |
| **Criterion 6** | **Deployed Version Alignment** | ❓ **UNKNOWN** | Live commit SHAs and release artifacts pending verification against repository. | Production<br>[YYYY-MM-DD] | ⏸️ Under Review |

---

## 🎯 Current Operational Focus (`WIP = 1`)

> [!IMPORTANT]
> Strict Single Work-In-Progress Rule: Exactly one active proof target is processed at any given time (`WIP = 1`).

- **Task Identifier:** `TASK-CORE-DISCOVERY-001`
- **Name:** **Core Ingestion & Processing Pipeline Runtime Discovery**
- **Coordinator:** `release-coordinator` via `/shipping` command.
- **Observed State:** Exploring the first unproven failure boundary using bounded runtime testing.
- **Completion Evidence:** Runtime proof report verifying valid execution (`WORKING_LOCALLY`) or identifying an exact failure boundary (`PROVEN_LOCAL_ISSUE`).

---

## 🚧 Active Blockers & Hypotheses

| Blocker ID | Description | Release Impact | Proof Action |
|:---:|---|---|---|
| **BLK-01** | Core backend processing pipeline verification | Critical path for product value | Run `/discovery` (Runtime-First) to identify the first unproven failure boundary. |
| **BLK-02** | Test fixture & isolated data readiness | Blocks clean repeatable verification | Verify configuration and initialize isolated test fixtures. |

---

## 📝 Strategic Decision Log
- **[[YYYY-MM-DD]]:** Approved v0.1 Release Contract and froze scope boundaries.
- **[[YYYY-MM-DD]]:** Approved Operating Manual, Delegation Record, and Agent topology.

---

## 🚀 Immediate Next Step
Execute `/shipping` to allow `release-coordinator` to delegate `TASK-CORE-DISCOVERY-001` to `discovery-coordinator` autonomously without requiring routine manual handoffs.
