---
name: labeeb-shipping-exec
description: "Execute one already-approved bounded Labeeb release task using an isolated implementation worker. Use only when a concrete task contract/finding already exists; do not use to invent work."
---

# Labeeb Shipping Exec

## MANDATORY EXECUTION BOUNDARY
You MUST invoke `implementation-executor` via `invoke_subagent`. Do NOT implement inline.

1. Locate the active bounded `task_contract` from the current conversation/release state.
2. If no task contract exists, do not invent one; return control to `/labeeb-shipping-mode` or `/labeeb-shipping-discovery`.
3. Prefer invoking `implementation-executor` as a custom subagent.
   - use workspace `branch` for repository-only/multi-file code changes;
   - use workspace `inherit` when the task's proof requires the current local Docker/runtime state.
4. Orchestrator may be used for an explicitly selected bounded implementation, but only inside an isolated branch worktree. Pass the contract as manifest data on stdin and reject the entire result on scope drift.
5. The executor may not push, merge, deploy, edit governance, or self-audit.
6. Return its result to the release coordinator for independent audit.
