#!/usr/bin/env bash
set -euo pipefail
TARGET=${1:-}
[ -n "$TARGET" ] || { echo "usage: $0 /path/to/labeeb"; exit 2; }
TARGET=$(cd "$TARGET" && pwd)
P="$TARGET/.agents/plugins/labeeb-shipping-mode"
test -f "$P/plugin.json"
test -f "$P/hooks.json"
python3 -m json.tool "$P/plugin.json" >/dev/null
python3 -m json.tool "$P/hooks.json" >/dev/null
python3 - "$P/scripts" <<'PYCODE'
import ast, pathlib, sys
for p in pathlib.Path(sys.argv[1]).glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
PYCODE
PYTHONDONTWRITEBYTECODE=1 python3 "$P/tests/test_guards.py"
for f in tasks/release-v0.1/00_RELEASE_CONTROL.md tasks/release-v0.1/01_RELEASE_CONTRACT.md tasks/release-v0.1/02_OPERATING_MANUAL.md tasks/release-v0.1/03_DELEGATION_RECORD.md tasks/release-v0.1/04_ROLE_PROMPTS.md tasks/release-v0.1/sprints/sprint_S01.md tasks/release-v0.1/CHANGELOG.md; do test -f "$TARGET/$f" || { echo "missing $f"; exit 1; }; done
if find "$TARGET/.agent/workflows" -maxdepth 1 -type f -name '*.md' 2>/dev/null | grep -q .; then echo 'WARNING: active legacy workflows remain'; fi
if [ -f "$TARGET/.agent/rules/release_governance.md" ]; then echo 'WARNING: legacy release_governance.md remains active'; fi
for old in AGENTIC_SYSTEM_DEVELOPER_GUIDE.md delivery_lead_integration_guide.md implementation_plan.md labeeb_shipping_mode_operational_manual.md workflow_improvments_plan.md; do
  if [ -f "$TARGET/tasks/release-v0.1/$old" ]; then echo "WARNING: superseded release design doc remains active: $old"; fi
done
echo 'INSTALL_VERIFY=PASS'
