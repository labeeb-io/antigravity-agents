# CHANGELOG — Labeeb Shipping Mode Package

## 2026-10-02 — v2.1.0 Agent-Native Standalone Release

### Highlights
- **Dedicated Subagent Manifests**: Added standalone custom agents under `.agents/agents/` (`discovery-coordinator`, `discovery-experiment-executor`, `discovery-researcher`, `implementation-executor`, `release-auditor`, `release-coordinator`) to work seamlessly with Antigravity IDE native subagents.
- **Enhanced Verification & Installation**: Refactored `apply.sh`, `rollback.sh`, `verify.sh`, and `verify-install.sh` to validate and synchronize both `.agents/plugins/labeeb-shipping-mode` and `.agents/agents/`.
- **Clean Standardized English Release Templates**: Upgraded release governance documents (`00_RELEASE_CONTROL.md`, `01_RELEASE_CONTRACT.md`, `02_OPERATING_MANUAL.md`, `03_DELEGATION_RECORD.md`, `04_ROLE_PROMPTS.md`, `sprint_S01.md`) with clean, generic dummy templates adhering to strict release standards.
- **Robust Integrity & Hashes**: Generated fresh SHA256 checksums and file manifests.

### Migration Summary

| Component | v2.0 | v2.1.0 |
|---|---|---|
| `.agents/plugins/labeeb-shipping-mode` | Initial plugin migration | Refined hooks, rules, and scripts |
| `.agents/agents/` | Embedded in plugin only | Dedicated top-level subagent profiles for direct Antigravity IDE invocation |
| `apply.sh` | Installs plugin + tasks | Installs plugin + agents + tasks with complete backup & rollback support |
| `rollback.sh` | Restores legacy backups | Restores legacy backups and handles agent directories |
| `verify.sh` | Validates plugin & syntax | Validates plugin, agents, python syntax, and guard test suites |

---

## 2026-10-01 — v2.0 Agent-Native Migration

### Goal
Convert Shipping Mode from legacy workflows into Agent Skills + Custom Subagents + Rules + Hooks while keeping release contracts and empirical evidence decoupled from the execution mechanism.
