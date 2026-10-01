---
name: labeeb-shipping-audit
description: "Independently verify one Labeeb release task or criterion on its original proof path and return PASS/FAIL/BLOCKED/UNKNOWN without fixing code."
---

# Labeeb Shipping Audit

## MANDATORY EXECUTION BOUNDARY
You MUST invoke `release-auditor` via `invoke_subagent`. Do NOT perform the independent audit inline.

1. Identify the original proof path, expected observable behavior, environment, and required identity from the task/experiment contract.
2. Prefer invoking `release-auditor` as a clean custom subagent.
3. Do not pass implementation reasoning beyond what is necessary to know what behavior to retest.
4. Orchestrator may be intentionally selected for independent review; use the configured `claude-reviewer` through a read-only stdin manifest.
5. If the proof requires an unavailable browser interaction, return `BLOCKED` rather than substituting repository inspection.
6. Send the verdict/evidence back to the release coordinator; the auditor does not close the release criterion itself.
