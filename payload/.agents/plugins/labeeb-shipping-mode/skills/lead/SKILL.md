---
name: lead
description: Use Labeeb's Release Coordinator to report current v0.1 state, select the next proof target, and optionally continue routine Shipping Mode work without manual handoffs.
---

# Labeeb Lead

Invoke `release-coordinator` in workspace `inherit` with mode `lead`.

Default behavior: read the frozen contract/current evidence, return the current target, why it is next, what is running/ready, and whether founder action is required. If the user said to continue, the coordinator may proceed with routine delegated work instead of stopping at a status report.

Use Orchestrator internally only as fallback when native subagent isolation is unavailable or an external model is explicitly useful.
