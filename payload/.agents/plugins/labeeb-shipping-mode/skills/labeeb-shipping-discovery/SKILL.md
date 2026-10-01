---
name: labeeb-shipping-discovery
description: "Starts one Labeeb runtime-first product/capability discovery. Use for release-relevant unknowns, end-to-end runtime/data tracing, readiness checks, or finding the first material failure without turning discovery into code review."
---

# Labeeb `/labeeb-shipping-discovery`

This skill is the **front door**, not the investigator.

## MANDATORY EXECUTION BOUNDARY
You MUST invoke `discovery-coordinator` via `invoke_subagent`. Do NOT perform Runtime-First Discovery inline in the parent session.

## Preferred mode: native coordinator subagent

When the `invoke_subagent` tool and the bundled custom agent `discovery-coordinator` are available:

1. Invoke exactly one `discovery-coordinator` subagent.
2. Use `Workspace: inherit` so it sees the same Labeeb workspace/runtime.
3. Pass the owner’s actual discovery request and relevant explicit constraints. Do not forward unrelated conversation history.
4. Use the custom agent type/name `discovery-coordinator` (`TypeName` when the tool schema exposes that field).
5. Let the coordinator own the entire evidence loop. Do not duplicate repository research in the parent conversation.
6. Collect the coordinator’s terminal result before replying to the owner.

The coordinator may itself invoke the bundled researcher or experiment executor. Nested subagents are intentional.

## Experiment authority

Default to:

```yaml
experiment_authority: read_only
```

If the owner explicitly says that reversible bounded local experiments are pre-authorized, pass:

```yaml
experiment_authority: bounded_local
```

This only authorizes the isolated experiment executor for one exact local contract. It never authorizes production mutation, code edits, migrations, destructive cleanup, deployment changes, dependency installation, or git changes.

## Compatibility and execution order

If native custom-subagent invocation is unavailable on the active Antigravity surface/version, do **not** pretend isolation exists and do not turn the owner into a message bus.

Use this execution order:

1. **Native custom subagent** — preferred.
2. **Installed project Orchestrator CLI** — use it for an explicit owner request or intentionally selected bounded offload. Launch exactly one configured read-only worker with a stdin manifest and retrieve that same task ID. Verify the CLI/runtime first; reading instructions alone is not execution.
3. **Inline read-only compatibility** — only if neither native subagents nor Orchestrator are available. Clearly label:

```text
execution_mode: inline_compatibility
```

In inline mode follow the same runtime-first proof ledger, but the parent remains read-only. If decisive proof requires mutation, return the exact experiment contract as `AWAITING_EXPERIMENT_APPROVAL`/`BLOCKED` rather than executing it inline.

## Named external orchestration

Native custom subagents are the default for routine bounded delegation. If the owner explicitly requests `/orchestrator`, or an external Claude/Codex independent challenge materially improves the decision, use the installed Orchestrator skill/CLI for that bounded question even when native subagents are available.
