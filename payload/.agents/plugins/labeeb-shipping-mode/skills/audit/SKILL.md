---
name: audit
description: Independently verify one Labeeb release task or criterion on its original proof path and return PASS/FAIL/BLOCKED/UNKNOWN without fixing code.
---

# Labeeb Audit

1. Identify the original proof path, expected observable behavior, environment, and required identity from the task/experiment contract.
2. Prefer invoking `release-auditor` as a clean custom subagent.
3. Do not pass implementation reasoning beyond what is necessary to know what behavior to retest.
4. If native subagents are unavailable, use Orchestrator internally; prefer `claude-code` for independent read-only audit when available.
5. If the proof requires an unavailable browser interaction, return `BLOCKED` rather than substituting repository inspection.
6. Send the verdict/evidence back to the release coordinator; the auditor does not close the release criterion itself.
