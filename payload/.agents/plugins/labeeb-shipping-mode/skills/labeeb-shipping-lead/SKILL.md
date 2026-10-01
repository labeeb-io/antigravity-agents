---
name: labeeb-shipping-lead
description: "Use Labeeb's Release Coordinator to report current v0.1 state, select the next proof target, and optionally continue routine Shipping Mode work without manual handoffs."
---

# Labeeb Shipping Lead

## MANDATORY EXECUTION BOUNDARY
You MUST invoke the custom subagent `release-coordinator` using the native `invoke_subagent` tool.
Required invocation:
- TypeName: release-coordinator
- Workspace: inherit
- Model: inherit
- Mode: lead

Do NOT execute the Release Coordinator role inline.
Do NOT read the release bootstrap files on behalf of the coordinator.
Do NOT impersonate or reproduce the coordinator's reasoning in the parent session.

The parent session may only:
1. invoke `release-coordinator`;
2. wait for its completion/error result;
3. present the returned result to the user.

If `invoke_subagent` is unavailable or the custom agent cannot be constructed, return:
```text
RELEASE_COORDINATOR_DELEGATION=BLOCKED
```
Do not silently fall back to inline execution.

Default behavior: read the frozen contract/current evidence, return the current target, why it is next, what is running/ready, and whether founder action is required. If the user said to continue, the coordinator may proceed with routine delegated work instead of stopping at a status report.

Use Orchestrator internally when it is the explicitly selected bounded offload or an external model materially improves confidence; native subagents remain the routine coordination default.
