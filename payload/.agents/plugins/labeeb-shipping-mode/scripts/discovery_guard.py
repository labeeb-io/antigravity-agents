#!/usr/bin/env python3
import json
import re
import sys

from discovery_common import actor_from_transcript, is_discovery_active, load_stdin, load_transcript

payload = load_stdin()
transcript = load_transcript(str(payload.get("transcriptPath", "")))

if not is_discovery_active(payload, transcript):
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

actor = actor_from_transcript(transcript)
tool = payload.get("toolCall", {}) or {}
name = str(tool.get("name", ""))
args = tool.get("args", {}) or {}

# No discovery actor is allowed to edit repository files directly.
if name in {"write_to_file", "replace_file_content", "multi_replace_file_content"}:
    print(json.dumps({
        "decision": "deny",
        "reason": "Labeeb discovery is evidence-only. Repository file edits belong after Finding -> Owner Decision -> Approved Ticket, not inside discovery."
    }))
    raise SystemExit(0)

if name != "run_command":
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

cmd = str(args.get("CommandLine", ""))
low = cmd.lower()

# Commands forbidden even for the experiment executor.
always_forbidden = [
    r"\bgit\s+(?:add|commit|checkout|switch|reset|clean|merge|rebase|push|pull|cherry-pick|restore)\b",
    r"\b(?:npm|pnpm|yarn)\s+(?:install|add|remove|update)\b",
    r"\bcomposer\s+(?:install|update|require|remove)\b",
    r"\bphp\s+artisan\s+(?:migrate|db:seed|seed)(?::|\s|$)",
    r"\bdocker\s+compose\s+(?:up|down|restart|start|stop|rm|build|pull)\b",
    r"\b(?:rm|mv|cp|touch|chmod|chown)\b",
    r"\b(?:insert\s+into|update\s+\w+\s+set|delete\s+from|truncate\s+|create\s+(?:table|index)|alter\s+|drop\s+)\b",
]

if any(re.search(p, cmd, re.I | re.S) for p in always_forbidden):
    print(json.dumps({
        "decision": "deny",
        "reason": "This command crosses the bounded discovery safety boundary (repository/git/dependency/schema/infrastructure/destructive mutation)."
    }))
    raise SystemExit(0)

# Executor may perform the exact bounded local runtime mutation supplied by its contract.
if actor == "executor":
    # Still block state-changing HTTP calls to non-local hosts. Production/staging mutation
    # belongs behind an explicit project governance path rather than automatic discovery.
    state_changing_http = bool(re.search(
        r"\bcurl\b[^\n]*(?:-x\s*(?:post|put|patch|delete)|--request\s*(?:post|put|patch|delete)|(?:-d|--data|--data-raw|--data-binary)\b)",
        cmd, re.I | re.S
    ))
    if state_changing_http:
        urls = re.findall(r"https?://[^\s'\"\\]+", cmd, re.I)
        if any(not re.match(r"https?://(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?(?:/|$)", u, re.I) for u in urls):
            print(json.dumps({
                "decision": "deny",
                "reason": "Automatic discovery executor may mutate only the local runtime. Non-local state-changing HTTP calls require the separate production/staging approval path."
            }))
            raise SystemExit(0)
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

# Coordinator, researcher, and inline compatibility parent stay read-only.
mutation_patterns = [
    r"\bcurl\b[^\n]*(?:-x\s*(?:post|put|patch|delete)|--request\s*(?:post|put|patch|delete)|(?:-d|--data|--data-raw|--data-binary)\b)",
    r"\bphp\s+artisan\s+(?:queue:(?:work|restart)|horizon|schedule:(?:work|run)|crawl:[^\s]*|[^\s]*reindex[^\s]*|[^\s]*index[^\s]*)\b",
]

if "artisan tinker" in low and re.search(r"(?:::create\b|->save\s*\(|->delete\s*\(|->update\s*\(|\binsert\s*\(|\btruncate\s*\()", cmd, re.I):
    mutation_patterns.append(r"artisan\s+tinker")

if any(re.search(p, cmd, re.I | re.S) for p in mutation_patterns):
    print(json.dumps({
        "decision": "deny",
        "reason": "The discovery coordinator/researcher is read-only. Build an exact experiment_contract and delegate it to discovery-experiment-executor when authority permits."
    }))
    raise SystemExit(0)

print(json.dumps({"decision": "allow"}))
