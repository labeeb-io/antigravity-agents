# Release Sprint S01 (Active Sprint Plan)

**Sprint Window:** [YYYY-MM-DD] — [YYYY-MM-DD]
**Status:** ACTIVE
**Primary Field Goal:**
> "Verify core user journey initiation and end-to-end data processing in the local runtime environment to achieve field acceptance for Criterion 1 and Criterion 2."

---

## Active Work & Queue (`WIP = 1`)

| Priority | Task Identifier | Target Work Unit | Release Alignment | Status |
|:---:|---|---|---|:---:|
| **1** | **TASK-CORE-DISCOVERY-001** | Runtime-First exploration of the core ingestion and processing pipeline; prove execution path or isolate the earliest failure boundary. | Foundation for Criteria 1, 2, and 5 | 🎯 **ACTIVE — WIP=1** |
| **2** | **TASK-ENTRYPOINT-002** | Verify user entrypoint session initialization and stable ID assignment. | Criterion 1 | ⏸️ Queued |
| **3** | **TASK-PROCESSING-003** | Verify end-to-end request processing, payload persistence, and result tracking. | Criterion 2 | ⏸️ Queued |
| **4** | **TASK-EVIDENCE-004** | Verify citation formatting, data freshness, and reference integrity. | Criteria 3 & 4 | ⏸️ Queued |
| **5** | **AUD-SPRINT-001** | Independent audit of completed acceptance paths. | Criteria 1–4 | ⏸️ Queued |

---

## Operational Workflow

1. `/shipping` coordinates the sprint from the frozen contract and empirical evidence.
2. `/discovery` serves as the runtime-first path for unverified boundaries.
3. Proven findings convert to implementation tasks via bounded Task Contracts.
4. Independent verification by `release-auditor` is required prior to task closure.

**Core Reference:** [00_RELEASE_CONTROL.md](../00_RELEASE_CONTROL.md)
