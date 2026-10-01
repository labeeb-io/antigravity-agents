# CHANGELOG — Release Control System Migration

## 2026-10-02 — v2.1.0 Agent-Native Standalone Subagents

### Objective
Provide standalone custom subagents under `.agents/agents/` alongside `.agents/plugins/labeeb-shipping-mode`, enabling seamless invocation via Antigravity IDE native subagents (`invoke_subagent`) while maintaining full isolation, reproducible runtime evidence, and strict frozen contract boundaries.

---

## 2026-10-01 — v2.0 Agent-Native Migration

### Objective
Transform the Shipping Mode operational layer from legacy Antigravity workflows and manual copy-paste sessions into Agent Skills + Custom Subagents + Rules + Hooks, keeping release contracts and field evidence decoupled from the execution mechanism.

### Migration of Legacy Workflows

| Legacy Workflow | Post-Migration Status | Current Replacement | Architectural Improvements |
|---|---|---|---|
| `.agent/workflows/lead.md` | **MIGRATED** | `/lead` + `/delivery-lead` Skills + `release-coordinator` | No longer a manual session prompt; operates as an autonomous coordinator reading contract/status and driving progress. |
| `.agent/workflows/release-cycle.md` | **REPLACED** | `/shipping` + `release-coordinator`, and `/release-cycle` alias | Multi-agent coordination replaced sequential in-context stages with isolated subagent dispatch and centralized reconciliation. |
| `.agent/workflows/discovery.md` | **REPLACED/REDESIGNED** | `/discovery` + `discovery-coordinator` + researcher/experiment executor | Converted to Runtime-First adaptive discovery. Removed mandatory serial doc chains in favor of direct proof boundary verification. |
| `.agent/workflows/exec.md` | **MIGRATED** | `/exec` + `implementation-executor` | Isolated worker operating strictly within a frozen Task Contract without git push/merge or deployment permissions. |
| `.agent/workflows/executor.md` | **DEDUPLICATED** | `/executor` alias for `/exec` | Deduplicated redundant legacy files into single canonical skill with aliases. |
| `.agent/workflows/audit.md` | **MIGRATED** | `/audit` + `release-auditor` | Independent verification executes in a clean-context custom subagent re-running the original proof path. |
| `.agent/workflows/auditor.md` | **DEDUPLICATED** | `/auditor` alias for `/audit` | Deduplicated redundant legacy wrappers. |
| `.agent/workflows/manager-handoff.md` | **REMOVED AS STAGE** | Native `invoke_subagent` first; Orchestrator fallback | Manual packet relaying eliminated; coordination occurs programmatically. |
| `.agent/workflows/prestart-approval.md` | **DISSOLVED** | Coordinator authority classification + Rules + PreToolUse hook | Mandatory archaeology removed; safety enforced JIT at tool execution boundaries. |
| `.agent/workflows/soft-gate.md` | **DISSOLVED** | Task Contract + bounded validation + reconciliation | Redundant review cycles removed; validation scoped directly to Task Contracts. |
| `.agent/workflows/plan-approval.md` | **DISSOLVED** | Founder reserved-decision gate + Task Contract | Routine implementation plans proceed autonomously; escalation reserved for core contract/security decisions. |

### Legacy Rules Migration

| Legacy Rule | Modern Replacement |
|---|---|
| `.agent/rules/release_governance.md` | `rules/shipping-invariants.md` + `rules/evidence-invariants.md` |

**Key Difference:** Legacy rules mixed routing, roles, and static tool chains in permanent prompt context. Modern rules preserve core invariants using standard `trigger: model_decision` frontmatter evaluated JIT by Antigravity.

### Hooks & Scripts Migration

| Legacy Script / Hook | Status | Modern Replacement |
|---|---|---|
| `guard-governance-files.sh` | Replaced | `shipping_guard.py` (actor-aware permission enforcement) |
| `inject-release-state.sh` | Removed | State read dynamically on-demand by coordinator |
| `auto-lint-check.sh` | Removed | Validation enforced directly within Task Contract acceptance criteria |
| `smart-delegate.sh` | Removed | Native Antigravity subagents with project Orchestrator fallback |
| `pre-flight-check.sh` | Migrated | Plugin `scripts/preflight.sh` informational environment probe |
| Root `.agent/hooks.json` | Replaced | Plugin `hooks.json` (PreToolUse security guards + discovery drift + stop gates) |

### Governance & Operational Principles

- **No Manual Relay:** Routine findings inside the frozen contract convert to bounded Task Contracts autonomously.
- **Reserved Founder Escalations:** Scope alterations, material risks, major architectural shifts, and final Go/No-Go decisions remain strictly with the founder.
- **Single Work-in-Progress (`WIP = 1`):** Focus is maintained on one proof boundary at a time.
- **`Merged != DONE`:** Release criteria require independent field verification (`PASS`) on the live environment.
