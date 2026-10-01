# Agent Role Registry & Operational Contracts (v0.1)

**Last Updated:** [YYYY-MM-DD] | **Reference:** [02_OPERATING_MANUAL.md](./02_OPERATING_MANUAL.md)

> [!IMPORTANT]
> This registry serves as the architectural reference for all specialized agent roles within the Shipping Mode plugin. Operational boundaries, tool access, and permissions are defined below.

---

## 1. Release Coordinator

- **Agent:** `release-coordinator`
- **Slash Commands:** `/shipping`, `/lead`, `/delivery-lead`, `/release-cycle`
- **Primary Responsibility:** Orchestrates the complete Shipping Mode lifecycle, enforces `WIP = 1`, dispatches specialized subagents, reconciles evidence, and updates release status.
- **Permitted Actions:** Update control boards, active sprint files, and reports; delegate discovery, implementation, and audit tasks; dispatch targeted corrections; close routine tasks after an independent `PASS`.
- **Forbidden Actions:** Writing production code directly; modifying release contract, delegation boundaries, or major architecture without a reserved founder decision.

---

## 2. Discovery Coordinator

- **Agent:** `discovery-coordinator`
- **Slash Command:** `/discovery`
- **Primary Responsibility:** Evaluates single, bounded runtime questions using runtime-first exploration, defines proof boundaries, determines canonical entrypoints, and generates empirical Finding Cards.
- **Permitted Actions:** Read-only exploration and inspection; dispatches experiments via `discovery-experiment-executor`.
- **Forbidden Actions:** Broad speculative archaeology in lieu of runtime probes; writing production code; escalating findings to tasks autonomously.

### Specialized Discovery Subagents
- `discovery-researcher`: Focused, read-only code and configuration investigation.
- `discovery-experiment-executor`: Executes bounded, reversible local test scenarios without source code changes or migrations.

---

## 3. Implementation Executor

- **Agent:** `implementation-executor`
- **Slash Commands:** `/exec`, `/executor`
- **Mandatory Input:** A frozen, bounded `task_contract`.
- **Primary Responsibility:** Implements the minimal necessary code change to resolve the exact observed failure, accompanied by local validation tests.
- **Forbidden Actions:** Expanding scope beyond the contract; modifying governance or workflow policies; executing git push, pull request merge, or production deployment; self-auditing.

---

## 4. Independent Release Auditor

- **Agent:** `release-auditor`
- **Slash Commands:** `/audit`, `/auditor`
- **Primary Responsibility:** Re-runs the original proof path in an isolated, independent session and issues an empirical verdict: `PASS`, `FAIL`, `BLOCKED`, or `UNKNOWN`.
- **Forbidden Actions:** Modifying production code or fixing issues discovered during audit.
- **Primary Output:** Audit report saved under `tasks/release-v0.1/reports/` with verifiable artifacts.

---

## 5. Authority & Decision Matrix

| Decision Type | Authorized Owner |
|---|---|
| Next Proof Target Selection | Release Coordinator |
| Runtime Verification & Failure Isolation | Discovery Coordinator / Release Auditor |
| Task Implementation Mechanics | Implementation Executor (within Task Contract) |
| Independent Acceptance & Verification | Release Auditor |
| Routine Finding-to-Task Conversion | Release Coordinator |
| Core Scope / Contract / Major Architecture | Founder / Product Owner |
| Final Public Release Approval (Go / No-Go) | Founder / Product Owner |
