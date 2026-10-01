#!/usr/bin/env python3
import json

from discovery_common import (
    actor_from_transcript,
    is_discovery_active,
    load_stdin,
    load_transcript,
    orchestrator_executed,
    orchestrator_requested,
    read_state,
    research_since_runtime,
    write_state,
)

payload = load_stdin()
transcript = load_transcript(str(payload.get("transcriptPath", "")))

if not is_discovery_active(payload, transcript):
    print("{}")
    raise SystemExit(0)

actor = actor_from_transcript(transcript)
if actor in {"researcher", "executor"}:
    print("{}")
    raise SystemExit(0)

invocation = int(payload.get("invocationNum", 0) or 0)
state = read_state(payload)
inject = []

if orchestrator_requested(transcript) and not orchestrator_executed(transcript):
    last = int(state.get("orchestrator_reminder", -100))
    if invocation >= 2 and invocation - last >= 3:
        inject.append({
            "ephemeralMessage": "The owner explicitly requested Orchestrator. Reading its SKILL.md is preparation only. Either execute the installed Orchestrator CLI contract for the bounded question now, or explicitly state why it cannot/should not be used."
        })
        state["orchestrator_reminder"] = invocation

research_count = research_since_runtime(transcript)
last_drift = int(state.get("drift_reminder", -100))
if research_count >= 6 and invocation - last_drift >= 2:
    inject.append({
        "ephemeralMessage": "Runtime-first drift guard: repository research is expanding without new runtime evidence. Re-state the first unproven boundary. Probe it now if safely observable; delegate one narrow question if entrypoint knowledge is missing; or use experiment-broker if mutation is required."
    })
    state["drift_reminder"] = invocation

write_state(payload, state)
print(json.dumps({"injectSteps": inject}, ensure_ascii=False))
