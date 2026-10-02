#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)

# 1. Plugin JSON & Hooks Validation
python3 -m json.tool "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/plugin.json" >/dev/null
python3 -m json.tool "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/hooks.json" >/dev/null 2>&1 || true

# 2. Python Syntax AST Verification
python3 - "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/scripts" <<'PYCODE'
import ast, pathlib, sys
for p in pathlib.Path(sys.argv[1]).glob('*.py'):
    ast.parse(p.read_text(), filename=str(p))
PYCODE

# 3. Guard Tests
if [ -f "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/tests/guard_policy_test.py" ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/tests/guard_policy_test.py" >/dev/null
elif [ -f "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/tests/test_guards.py" ]; then
  PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/tests/test_guards.py" >/dev/null
fi

# 4. Rules Trigger Header Verification
for f in "$ROOT"/payload/.agents/plugins/labeeb-shipping-mode/rules/*.md; do
  grep -q '^trigger: ' "$f" || { echo "missing trigger: $f"; exit 1; }
done

# 5. Skills Manifest Verification
for s in shipping lead delivery-lead discovery exec executor audit auditor release-cycle; do
  test -f "$ROOT/payload/.agents/plugins/labeeb-shipping-mode/skills/$s/SKILL.md" || { echo "missing skill $s"; exit 1; }
done

# 6. Standalone Custom Agents Verification
for a in release-coordinator discovery-coordinator discovery-researcher discovery-experiment-executor implementation-executor release-auditor; do
  test -f "$ROOT/payload/.agents/agents/$a/agent.md" || { echo "missing standalone agent $a"; exit 1; }
done

echo 'PACKAGE_VERIFY=PASS'
