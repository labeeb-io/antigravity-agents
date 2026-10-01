# Release Operations Delegation Record (v0.1)

**Effective Date:** [YYYY-MM-DD] | **Revision:** 2.1 — Agent-Native Delegation  
**Authority:** Approved by Product Owner / Founder  
**Core Reference:** [01_RELEASE_CONTRACT.md](./01_RELEASE_CONTRACT.md) and [02_OPERATING_MANUAL.md](./02_OPERATING_MANUAL.md)

---

## Official Delegation Statement

The Product Owner approves Shipping Mode under the v0.1 Release Contract and hereby delegates operational leadership to the **Release Coordinator** to autonomously manage daily release progress within the frozen contract, eliminating routine manual message relaying.

---

## 1. Delegated Coordinator Authority

The Release Coordinator is authorized to perform the following without requesting daily manual approval:
1. Identify the next unproven proof target directly from the contract and latest evidence.
2. Enforce `WIP = 1` and update [00_RELEASE_CONTROL.md](./00_RELEASE_CONTROL.md), active sprint notes, and operational logs.
3. Invoke `discovery-coordinator` and specialized research subagents to gather empirical runtime evidence.
4. Delegate single, bounded, reversible local experiments to `discovery-experiment-executor` without modifying source code, schema, or deployments.
5. Autonomously convert routine, proven findings into a bounded Task Contract provided they satisfy acceptance gates and do not touch reserved decisions.
6. Invoke `implementation-executor`, monitor progress, and dispatch targeted corrections within the same task boundary.
7. Invoke `release-auditor` in an independent session to re-verify the original proof path.
8. Approve closure of routine implementation tasks following an independent `PASS` verdict.
9. Defer or reject scope additions outside the v0.1 contract.

---

## 2. Implementation Boundaries & Permissions

- **Implementation Executor:** Permitted to edit local code strictly within `allowed_scope`. Forbidden from performing git push, pull request merge, production deployment, or governance modifications.
- **Production State-Changing Probes:** Any probe creating persistent production state outside an approved routine path requires an explicit contract and founder sign-off prior to execution.
- **Independent Auditor:** Read-only inspection and testing; documents findings under `reports/`; forbidden from applying code fixes during audit.

---

## 3. Reserved Founder Decisions (Strictly 4 Cases)

The following decisions are reserved exclusively for the Founder / Product Owner:
1. Modification of the core value promise, frozen scope, or release criteria.
2. Unusual financial commitments, paid service tiers, or third-party vendor agreements.
3. Material security, data privacy, or regulatory compliance risks.
4. Major architectural overhaul or replacement of foundational frameworks.
5. Final weekly approval of completed release criteria and the public Go / No-Go decision.

Any routine finding or fix that does not fall into these reserved categories **does not require an owner gate** if it remains inside the contract and `WIP = 1`.

---

## 4. Independence & Integrity Principles

- The author of a code modification cannot grant the final verification `PASS`.
- An independent audit session must verify every claimed fix before task closure.
- Historical plans or past memories never override direct, active runtime evidence.

---

**Product Owner / Founder:** [FOUNDER_NAME]  
**Effective Date:** [YYYY-MM-DD]
