---
name: shipping
description: Continue or run Labeeb v0.1 Shipping Mode end-to-end: choose the next proof target from the frozen release contract, delegate discovery/implementation/audit, reconcile evidence, update release state, and escalate only reserved founder decisions. Use for "continue shipping", "what is next", "finish v0.1", or a full release cycle.
---

# Labeeb Shipping Mode

This is the primary front door for daily release work.

1. Prefer invoking custom subagent `release-coordinator` with workspace `inherit` and a compact prompt containing the user's current instruction.
2. The coordinator owns the full loop and should not return merely because it needs another specialist; it should invoke the appropriate subagent and reconcile the result.
3. Do not make the user copy messages between agents.
4. If native `invoke_subagent` is unavailable, execute the Release Coordinator logic in the current session and use the project's installed Orchestrator CLI internally for isolated discovery/implementation/audit workers. Verify Orchestrator availability first; do not merely read its instructions.
5. If neither native subagents nor Orchestrator can provide the required isolation, return `BLOCKED` with the missing capability.
6. Preserve the frozen release contract, WIP=1, and founder-reserved decision boundaries.

Expected user-facing result is a concise release state plus the next automatic action or one reserved founder decision.
