# Labeeb Shipping Mode v2 — Agent-Native Migration

This package converts the uploaded Shipping Mode control plane from legacy `.agent/workflows/*.md` into an Antigravity plugin built around Skills + Custom Subagents + Rules + Hooks.

## What you get

Primary command:

```text
/shipping
```

Modern commands:
- `/shipping`
- `/lead` / `/delivery-lead`
- `/discovery`
- `/exec` / `/executor`
- `/audit` / `/auditor`
- `/release-cycle` compatibility alias

Custom agents:
- `release-coordinator`
- `discovery-coordinator`
- `discovery-researcher`
- `discovery-experiment-executor`
- `implementation-executor`
- `release-auditor`

## Safe first install

```bash
unzip labeeb-shipping-mode-v2.zip
cd labeeb-shipping-mode-v2
./verify.sh
./apply-migration.sh /home/hany/webserver/server/www/labeeb2025
```

The installer first performs a baseline drift check. If any uploaded workflow/governance/release file changed since this package was built, it aborts before installing anything. When the precheck passes, it creates a timestamped backup, installs the plugin and canonical release docs. Existing evidence under `tasks/release-v0.1/reports/` is not overwritten. It and archives the known legacy Shipping Mode workflow/rule/hook/script files when they match the supplied baseline. It also removes the superseded Shipping Mode design documents from the active `tasks/release-v0.1/` root after installing historical copies under `archive/legacy-agent-system/`. If any legacy file differs from the uploaded baseline, it is left active and reported as a conflict unless `--force-legacy-cutover` is used.

## Runtime acceptance test

After reloading Antigravity:

1. Check custom agents using `/agents` if your surface supports it.
2. Run:

```text
/shipping
اعطيني الحالة الحالية فقط ولا تنفذ أي mutation.
```

Expected: `release-coordinator` is invoked natively, or the skill explicitly uses Orchestrator fallback. It should read the release contract/control state and return one current target without broad repository archaeology.

3. Run the current discovery:

```text
/discovery
استأنف TASK-BE-DISCOVERY Runtime-First. Read-only أولاً.
```

Expected: proof-boundary behavior from Discovery V2; no mandatory Memory→Wiki→GitNexus chain.

## Cutover note

The migration changes the agent control plane. It does **not** prove or change any product/release criterion by itself.

See `CHANGELOG.md` for an exact workflow-by-workflow mapping.

## Isolation fallback

Delegation order is intentionally: native Antigravity custom subagents -> project Orchestrator CLI -> read-only inline/BLOCKED. The migration never asks the founder to manually copy task packets between agents.
