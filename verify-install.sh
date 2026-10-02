#!/usr/bin/env bash
set -euo pipefail
TARGET=${1:-}
if [ -z "$TARGET" ]; then echo "usage: $0 /path/to/labeeb"; exit 2; fi
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

if [ -f "$P/tests/guard_policy_test.py" ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$P/tests/guard_policy_test.py" >/dev/null
elif [ -f "$P/tests/test_guards.py" ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$P/tests/test_guards.py" >/dev/null
fi

# Verify standalone agents
for a in release-coordinator discovery-coordinator discovery-researcher discovery-experiment-executor implementation-executor release-auditor; do
  test -f "$TARGET/.agents/agents/$a/agent.md" || { echo "missing installed agent $a"; exit 1; }
done

# Verify release documentation
for f in tasks/release-v0.1/00_RELEASE_CONTROL.md tasks/release-v0.1/01_RELEASE_CONTRACT.md tasks/release-v0.1/02_OPERATING_MANUAL.md tasks/release-v0.1/03_DELEGATION_RECORD.md tasks/release-v0.1/04_ROLE_PROMPTS.md tasks/release-v0.1/sprints/sprint_S01.md tasks/release-v0.1/CHANGELOG.md; do
  test -f "$TARGET/$f" || { echo "missing $f"; exit 1; }
done

echo 'INSTALL_VERIFY=PASS'
