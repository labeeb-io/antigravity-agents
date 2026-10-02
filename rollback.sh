#!/usr/bin/env bash
set -euo pipefail
TARGET=${1:-}; BACKUP=${2:-}
[ -n "$TARGET" ] && [ -n "$BACKUP" ] || { echo "usage: $0 /path/to/labeeb /path/to/backup"; exit 2; }
TARGET=$(cd "$TARGET" && pwd); BACKUP=$(cd "$BACKUP" && pwd)

rm -rf "$TARGET/.agents/plugins/labeeb-shipping-mode"
rm -rf "$TARGET/.agents/agents"
rm -f "$TARGET/tasks/release-v0.1/AGENT_SYSTEM_ARCHITECTURE.md"
rm -f "$TARGET/tasks/release-v0.1/CHANGELOG.md"
rm -rf "$TARGET/tasks/release-v0.1/archive/legacy-agent-system"

cp -a "$BACKUP/." "$TARGET/"
echo 'ROLLBACK_RESTORED_BACKUP=PASS'
