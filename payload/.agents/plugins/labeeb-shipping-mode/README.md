# Labeeb Shipping Mode — Agent System Architecture

Status: Active as of 2026-10-01 (Refined V2 Architecture).

## Goal

Keep the founder out of routine message passing while preserving release-contract authority, bounded execution, independent proof, and WIP=1.

## Canonical Layout & Source of Truth

The agent architecture uses a clean separation of concerns without duplicate active definitions:

```text
.agents/
├── agents/                          # Canonical Runtime Subagents
│   ├── release-coordinator/agent.md
│   ├── discovery-coordinator/agent.md
│   ├── discovery-researcher/agent.md
│   ├── discovery-experiment-executor/agent.md
│   ├── implementation-executor/agent.md
│   └── release-auditor/agent.md
├── skills/                          # Canonical Workspace Skills (Slash Commands)
│   ├── labeeb-shipping-mode/SKILL.md
│   ├── labeeb-shipping-lead/SKILL.md
│   ├── labeeb-shipping-discovery/SKILL.md
│   ├── labeeb-shipping-exec/SKILL.md
│   ├── labeeb-shipping-audit/SKILL.md
│   └── labeeb-shipping-experiment-broker/SKILL.md
└── plugins/
    └── labeeb-shipping-mode/         # Packaging: Rules, Hooks, Scripts
        ├── plugin.json
        ├── rules/
        ├── hooks.json
        ├── hooks.template.json
        └── scripts/
```

- **Canonical Agent Source:** `.agents/agents/<name>/agent.md` is the sole source of truth for runtime subagents. Each agent is configured with `subagent: true` and `mainAgent: false` to ensure isolated execution via `invoke_subagent`.
- **Canonical Workspace Skills:** `.agents/skills/` provides the project-native slash commands (`/labeeb-shipping-mode`, `/labeeb-shipping-lead`, `/labeeb-shipping-discovery`, `/labeeb-shipping-exec`, `/labeeb-shipping-audit`) and reusable coordinator skills (`labeeb-shipping-experiment-broker`).
- **Plugin Packaging:** `.agents/plugins/labeeb-shipping-mode/` packages rules, fail-fast lifecycle hooks, and safety scripts. It contains no duplicate active agents or skills.
- **Historical Archive:** Initial plugin agent definitions are preserved under `tasks/release-v0.1/archive/agent-definitions-v2-initial/`.

## Control plane

`/labeeb-shipping-mode` is the primary front door. It invokes `release-coordinator`, which reads the frozen release contract and current evidence and then delegates to isolated workers.

```text
Founder
  -> /shipping
     -> release-coordinator
        -> discovery-coordinator
           -> discovery-researcher / built-in research
           -> discovery-experiment-executor (via experiment-broker)
        -> implementation-executor
        -> release-auditor
```

## Separation of authority

- Release Coordinator: sequencing/reconciliation/operational records; no product-code edits.
- Discovery: evidence acquisition; no implementation.
- Experiment Executor: one bounded local runtime mutation; no code changes.
- Implementation Executor: one task contract; local code only; no publish/deploy.
- Auditor: independent proof; no fixes.

## Delegation transport

1. Native Antigravity `invoke_subagent` for custom subagent isolation.
2. Event-driven completion: Parent agents await automatic notification upon subagent completion without polling.
3. Orchestrator fallback for surfaces without native custom-subagent execution or when an external model is materially useful.
4. Manual founder handoff is not a normal transport mechanism.

## Evidence loop

```text
contract -> runtime proof -> finding -> delegation gate -> bounded task
-> implementation -> independent audit -> reconciliation -> state update
```

## Legacy compatibility

Skills preserve `/lead`, `/release-cycle`, `/exec`, `/executor`, `/audit`, and `/auditor` as slash commands. `/release-cycle` aliases `/shipping`. The old workflows `manager-handoff`, `prestart-approval`, `soft-gate`, and `plan-approval` are intentionally not recreated as separate steps; their responsibilities are absorbed into coordinator logic, task/experiment contracts, rules, and hooks.

## Scope & Non-Technical Impact

The six Arabic release documents remain canonical for product/release governance. This architecture file describes only the agent execution implementation. These architectural updates are strictly control-plane refinements and do not serve as technical proof for any Release Criterion or alter any Product/Release status.
