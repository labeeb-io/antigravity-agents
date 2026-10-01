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

# backup canonical docs and legacy control plane
for p in \
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
  if [ -e "$TARGET/$p" ]; then mkdir -p "$BACKUP/$(dirname "$p")"; cp -a "$TARGET/$p" "$BACKUP/$p"; fi
done

# Preflight drift check: abort before installing anything if uploaded baselines no longer match.
# This prevents a partial cutover or overwriting newer governance/release state.
if [ "$FORCE" != "--force-legacy-cutover" ]; then
  preflight_conflicts=0
  check_same(){
    local live="$1" base="$2" rel="$3"
    [ -e "$live" ] || return 0
    if ! cmp -s "$live" "$base"; then
      echo "MIGRATION_CONFLICT: $rel differs from the uploaded baseline. No migration changes were applied."
      preflight_conflicts=$((preflight_conflicts+1))
    fi
  }
  for f in "$ROOT"/legacy-baseline/workflows/*.md; do n=$(basename "$f"); check_same "$TARGET/.agent/workflows/$n" "$f" "workflows/$n"; done
  check_same "$TARGET/.agent/rules/release_governance.md" "$ROOT/legacy-baseline/rules/release_governance.md" "rules/release_governance.md"
  check_same "$TARGET/.agent/hooks.json" "$ROOT/legacy-baseline/hooks.json" "hooks.json"
  for f in "$ROOT"/legacy-baseline/scripts/*; do n=$(basename "$f"); check_same "$TARGET/.agent/scripts/$n" "$f" "scripts/$n"; done
  for f in "$ROOT"/legacy-baseline/release-docs/*.md; do n=$(basename "$f"); check_same "$TARGET/tasks/release-v0.1/$n" "$f" "tasks/release-v0.1/$n"; done
  for f in "$ROOT"/legacy-baseline/release-canonical/*.md; do n=$(basename "$f"); check_same "$TARGET/tasks/release-v0.1/$n" "$f" "tasks/release-v0.1/$n"; done
  if [ -f "$ROOT/legacy-baseline/release-canonical/sprints/sprint_S01.md" ]; then
    check_same "$TARGET/tasks/release-v0.1/sprints/sprint_S01.md" "$ROOT/legacy-baseline/release-canonical/sprints/sprint_S01.md" "tasks/release-v0.1/sprints/sprint_S01.md"
  fi
  if [ "$preflight_conflicts" -gt 0 ]; then
    echo "MIGRATION_STATE=ABORTED_PRECHECK count=$preflight_conflicts"
    echo "Review the changed files and rebuild the migration package, or use --force-legacy-cutover only after intentional review."
    exit 3
  fi
fi

# Install plugin and docs
mkdir -p "$TARGET/.agents/plugins"
rm -rf "$TARGET/.agents/plugins/labeeb-shipping-mode"
cp -a "$ROOT/payload/.agents/plugins/labeeb-shipping-mode" "$TARGET/.agents/plugins/"
PLUGIN="$TARGET/.agents/plugins/labeeb-shipping-mode"
mkdir -p "$TARGET/tasks/release-v0.1"
cp -a "$ROOT/payload/tasks/release-v0.1/." "$TARGET/tasks/release-v0.1/"

# Cut over known legacy files. Exact-baseline files are archived automatically; modified files require force.
LEGACY_ARCH="$TARGET/.agent/archive/shipping-mode-legacy-$STAMP"
mkdir -p "$LEGACY_ARCH"
conflicts=0
cut_one(){
  local live="$1" base="$2" rel="$3"
  [ -e "$live" ] || return 0
  if [ "$FORCE" = "--force-legacy-cutover" ] || cmp -s "$live" "$base"; then
    mkdir -p "$LEGACY_ARCH/$(dirname "$rel")"
    mv "$live" "$LEGACY_ARCH/$rel"
  else
    echo "LEGACY_CONFLICT_AFTER_PREFLIGHT: $rel changed during migration; left active. Review before retrying."
    conflicts=$((conflicts+1))
  fi
}
for f in "$ROOT"/legacy-baseline/workflows/*.md; do n=$(basename "$f"); cut_one "$TARGET/.agent/workflows/$n" "$f" "workflows/$n"; done
cut_one "$TARGET/.agent/rules/release_governance.md" "$ROOT/legacy-baseline/rules/release_governance.md" "rules/release_governance.md"
cut_one "$TARGET/.agent/hooks.json" "$ROOT/legacy-baseline/hooks.json" "hooks.json"
for f in "$ROOT"/legacy-baseline/scripts/*; do n=$(basename "$f"); cut_one "$TARGET/.agent/scripts/$n" "$f" "scripts/$n"; done

# Archive superseded Shipping Mode design documents from the active release root.
# Canonical historical copies are installed under tasks/release-v0.1/archive/legacy-agent-system/.
for f in "$ROOT"/legacy-baseline/release-docs/*.md; do
  n=$(basename "$f")
  cut_one "$TARGET/tasks/release-v0.1/$n" "$f" "release-docs/$n"
done

# Sanity checks
python3 -m json.tool "$PLUGIN/plugin.json" >/dev/null
python3 -m json.tool "$PLUGIN/hooks.json" >/dev/null
python3 - "$PLUGIN/scripts" <<'PYCODE'
import ast, pathlib, sys
for p in pathlib.Path(sys.argv[1]).glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
PYCODE
PYTHONDONTWRITEBYTECODE=1 python3 "$PLUGIN/tests/test_guards.py" >/dev/null

echo "BACKUP=$BACKUP"
echo "PLUGIN=$PLUGIN"
echo "LEGACY_ARCHIVE=$LEGACY_ARCH"
if [ "$conflicts" -gt 0 ]; then
  echo "MIGRATION_STATE=INSTALLED_WITH_LEGACY_CONFLICTS count=$conflicts"
  exit 3
fi
echo 'MIGRATION_STATE=PASS'
