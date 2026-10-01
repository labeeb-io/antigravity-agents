#!/usr/bin/env bash
set -u
status=0
printf '%s\n' '== Labeeb bounded implementation preflight =='
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)
echo "branch=$branch"
if git status --porcelain >/tmp/labeeb-preflight-git 2>/dev/null; then
  if [ -s /tmp/labeeb-preflight-git ]; then echo 'working_tree=dirty'; head -n 20 /tmp/labeeb-preflight-git; else echo 'working_tree=clean'; fi
else echo 'working_tree=unknown'; fi
if command -v docker >/dev/null 2>&1 && docker compose ps --services >/tmp/labeeb-preflight-services 2>/dev/null; then
  echo 'docker_compose=available'
  for svc in api scraper db redis search queue; do
    if grep -qx "$svc" /tmp/labeeb-preflight-services; then echo "service_declared:$svc=yes"; else echo "service_declared:$svc=no"; fi
  done
else
  echo 'docker_compose=unavailable_or_not_configured'
fi
echo 'preflight=informational_complete'
exit $status
