#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
TARGET=${1:-}
FORCE=${2:-}
if [ -z "$TARGET" ]; then echo "usage: $0 /path/to/labeeb [--force-legacy-cutover]"; exit 2; fi
TARGET=$(cd "$TARGET" && pwd)
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP="$TARGET/.migration-backups/labeeb-shipping-mode-v2-$STAMP"
mkdir -p "$BACKUP"

# Backup existing agents, plugin, canonical docs and legacy control plane
for p in \
  .agents/agents .agents/plugins/labeeb-shipping-mode \
  .agent/hooks.json .agent/rules/release_governance.md \
  .agent/workflows/audit.md .agent/workflows/auditor.md .agent/workflows/discovery.md \
  .agent/workflows/exec.md .agent/workflows/executor.md .agent/workflows/lead.md \
  .agent/workflows/manager-handoff.md .agent/workflows/plan-approval.md \
  .agent/workflows/prestart-approval.md .agent/workflows/release-cycle.md .agent/workflows/soft-gate.md \
  .agent/scripts/auto-lint-check.sh .agent/scripts/guard-governance-files.sh .agent/scripts/inject-release-state.sh \
  .agent/scripts/pre-flight-check.sh .agent/scripts/smart-delegate.sh \
  tasks/release-v0.1/00_RELEASE_CONTROL.md tasks/release-v0.1/01_RELEASE_CONTRACT.md \
  tasks/release-v0.1/02_OPERATING_MANUAL.md tasks/release-v0.1/03_DELEGATION_RECORD.md \
  tasks/release-v0.1/04_ROLE_PROMPTS.md tasks/release-v0.1/README.md tasks/release-v0.1/sprints/sprint_S01.md \
  tasks/release-v0.1/AGENTIC_SYSTEM_DEVELOPER_GUIDE.md \
  tasks/release-v0.1/delivery_lead_integration_guide.md \
  tasks/release-v0.1/implementation_plan.md \
  tasks/release-v0.1/labeeb_shipping_mode_operational_manual.md \
  tasks/release-v0.1/workflow_improvments_plan.md; do
  if [ -e "$TARGET/$p" ]; then
    mkdir -p "$BACKUP/$(dirname "$p")"
    cp -a "$TARGET/$p" "$BACKUP/$p"
  fi
done

# Install plugin, standalone agents, and docs
mkdir -p "$TARGET/.agents/plugins" "$TARGET/.agents/agents"
rm -rf "$TARGET/.agents/plugins/labeeb-shipping-mode"
cp -a "$ROOT/payload/.agents/plugins/labeeb-shipping-mode" "$TARGET/.agents/plugins/"
PLUGIN="$TARGET/.agents/plugins/labeeb-shipping-mode"

if [ -d "$ROOT/payload/.agents/agents" ]; then
  cp -a "$ROOT/payload/.agents/agents/." "$TARGET/.agents/agents/"
fi

mkdir -p "$TARGET/tasks/release-v0.1"
cp -a "$ROOT/payload/tasks/release-v0.1/." "$TARGET/tasks/release-v0.1/"

# Sanity checks
python3 -m json.tool "$PLUGIN/plugin.json" >/dev/null
python3 -m json.tool "$PLUGIN/hooks.json" >/dev/null
python3 - "$PLUGIN/scripts" <<'PYCODE'
import ast, pathlib, sys
for p in pathlib.Path(sys.argv[1]).glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
PYCODE

if [ -f "$PLUGIN/tests/guard_policy_test.py" ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$PLUGIN/tests/guard_policy_test.py" >/dev/null
elif [ -f "$PLUGIN/tests/test_guards.py" ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$PLUGIN/tests/test_guards.py" >/dev/null
fi

echo "BACKUP=$BACKUP"
echo "PLUGIN=$PLUGIN"
echo "AGENTS=$TARGET/.agents/agents"
echo 'MIGRATION_STATE=PASS'
