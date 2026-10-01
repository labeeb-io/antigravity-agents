---
name: delivery-lead
description: Compatibility alias for Labeeb Shipping Mode Delivery Lead. Routes legacy delivery-lead usage into the modern /shipping release-coordinator flow.
---

# Labeeb `/delivery-lead` compatibility alias

This legacy-facing command must execute the same control plane as `/shipping`.

1. Load and follow the bundled `shipping` skill.
2. Prefer the native `release-coordinator` custom subagent.
3. Preserve the same native-subagent -> Orchestrator fallback -> BLOCKED isolation policy.
4. Do not recreate the old copy/paste Delivery Lead session model.
