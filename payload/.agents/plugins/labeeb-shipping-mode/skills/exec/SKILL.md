---
name: exec
description: Execute one already-approved bounded Labeeb release task using an isolated implementation worker. Use only when a concrete task contract/finding already exists; do not use to invent work.
---

# Labeeb Exec

1. Locate the active bounded `task_contract` from the current conversation/release state.
2. If no task contract exists, do not invent one; return control to `/shipping` or `/discovery`.
3. Prefer invoking `implementation-executor` as a custom subagent.
   - use workspace `branch` for repository-only/multi-file code changes;
   - use workspace `inherit` when the task's proof requires the current local Docker/runtime state.
4. If native subagents are unavailable, use the installed Orchestrator internally; prefer `codex` for implementation when available.
5. The executor may not push, merge, deploy, edit governance, or self-audit.
6. Return its result to the release coordinator for independent audit.
