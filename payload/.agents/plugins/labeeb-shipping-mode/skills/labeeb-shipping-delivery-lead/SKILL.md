---
name: labeeb-shipping-delivery-lead
description: "Compatibility alias for Labeeb Shipping Mode Delivery Lead. Routes legacy delivery-lead usage into the modern /labeeb-shipping-mode release-coordinator flow."
---

# Labeeb `/labeeb-shipping-delivery-lead` compatibility alias

This legacy-facing command executes the same control plane as `/labeeb-shipping-mode`.

1. Load and follow the bundled `labeeb-shipping-mode` skill.
2. Prefer the native `release-coordinator` custom subagent.
3. Preserve the same native-subagent default, intentional Orchestrator offload, and fail-closed isolation policy.
4. Do not recreate the old copy/paste Delivery Lead session model.
