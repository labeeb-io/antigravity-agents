#!/usr/bin/env python3
import json

from discovery_common import (
    TERMINAL_MARKERS,
    actor_from_transcript,
    close_discovery,
    is_discovery_active,
    load_stdin,
    load_transcript,
    read_state,
    recent_text,
    write_state,
)

payload = load_stdin()
transcript = load_transcript(str(payload.get("transcriptPath", "")))

if not is_discovery_active(payload, transcript):
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

actor = actor_from_transcript(transcript)
if actor in {"researcher", "executor"}:
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

if not bool(payload.get("fullyIdle", True)):
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

recent = recent_text(transcript).upper()
if any(marker in recent for marker in TERMINAL_MARKERS):
    close_discovery(payload)
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

state = read_state(payload)
count = int(state.get("stop_reminders", 0))
if count >= 1:
    print(json.dumps({"decision": "allow"}))
    raise SystemExit(0)

state["stop_reminders"] = count + 1
write_state(payload, state)
print(json.dumps({
    "decision": "continue",
    "reason": "Before ending this /discovery run, reconcile the coordinator result and return one explicit terminal state: WORKING_LOCALLY, PROVEN_LOCAL_ISSUE, AWAITING_EXPERIMENT_APPROVAL, BLOCKED, UNKNOWN, or OUT_OF_SCOPE. Do not let the verdict cover unobserved boundaries."
}, ensure_ascii=False))
