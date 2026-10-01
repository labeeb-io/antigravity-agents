#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable

DISCOVERY_MARKERS = (
    "/discovery",
    "discovery_request",
    "runtime-first discovery",
    "labeeb runtime-first discovery",
)

ACTOR_MARKERS = {
    "coordinator": "LABEEB_DISCOVERY_COORDINATOR",
    "researcher": "LABEEB_DISCOVERY_RESEARCHER",
    "executor": "LABEEB_EXPERIMENT_EXECUTOR",
}

TERMINAL_MARKERS = (
    "WORKING_LOCALLY",
    "PROVEN_LOCAL_ISSUE",
    "AWAITING_EXPERIMENT_APPROVAL",
    "BLOCKED",
    "UNKNOWN",
    "OUT_OF_SCOPE",
)


def load_stdin() -> Dict[str, Any]:
    try:
        return json.load(__import__("sys").stdin)
    except Exception:
        return {}


def load_transcript(path: str, max_bytes: int = 3_000_000) -> str:
    if not path:
        return ""
    try:
        p = Path(os.path.expanduser(path))
        if not p.exists():
            return ""
        size = p.stat().st_size
        with p.open("rb") as f:
            if size > max_bytes:
                f.seek(size - max_bytes)
            data = f.read()
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def iter_jsonl(transcript: str) -> Iterable[Dict[str, Any]]:
    for line in transcript.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                yield obj
        except Exception:
            continue


def latest_user_text(transcript: str) -> str:
    latest = ""
    for obj in iter_jsonl(transcript):
        typ = str(obj.get("type", "")).upper()
        source = str(obj.get("source", "")).upper()
        if typ == "USER_INPUT" or source == "USER_EXPLICIT":
            latest = str(obj.get("content", ""))
    return latest


def actor_from_transcript(transcript: str) -> str:
    # Check only if first step / step 0 is subagent declaration
    first_chunk = transcript[:3000] if transcript else ""
    # If it is main conversation, step 0 has USER_INPUT / USER_REQUEST
    if '"step_index":0' in first_chunk and "USER_INPUT" in first_chunk:
        return "parent"
    for actor, marker in ACTOR_MARKERS.items():
        if marker in first_chunk and (f"Marker: {marker}" in first_chunk or f"Marker: `{marker}`" in first_chunk):
            return actor
    return "parent"


def state_path(payload: Dict[str, Any]) -> Path:
    artifact = payload.get("artifactDirectoryPath") or "/tmp"
    return Path(os.path.expanduser(str(artifact))) / ".labeeb_discovery_v2_state.json"


def read_state(payload: Dict[str, Any]) -> Dict[str, Any]:
    p = state_path(payload)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_state(payload: Dict[str, Any], state: Dict[str, Any]) -> None:
    p = state_path(payload)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def discovery_requested(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in DISCOVERY_MARKERS)


def is_discovery_active(payload: Dict[str, Any], transcript: str) -> bool:
    actor = actor_from_transcript(transcript)
    if actor in {"coordinator", "researcher", "executor"}:
        return True

    state = read_state(payload)
    if state.get("active") is True:
        return True

    if discovery_requested(latest_user_text(transcript)):
        state["active"] = True
        write_state(payload, state)
        return True

    return False


def close_discovery(payload: Dict[str, Any]) -> None:
    state = read_state(payload)
    state["active"] = False
    write_state(payload, state)


def research_since_runtime(transcript: str) -> int:
    research_types = {
        "VIEW_FILE", "GREP_SEARCH", "FIND_BY_NAME", "LIST_DIR",
        "READ_URL_CONTENT", "SEARCH_WEB"
    }
    runtime_types = {
        "RUN_COMMAND", "BROWSER", "BROWSER_TOOL", "MANAGE_TASK",
        "INVOKE_SUBAGENT", "MCP_TOOL"
    }
    count = 0
    for obj in iter_jsonl(transcript):
        typ = str(obj.get("type", "")).upper()
        if typ in runtime_types:
            count = 0
        elif typ in research_types:
            count += 1
    return count


def orchestrator_requested(transcript: str) -> bool:
    low = transcript.lower()
    patterns = (
        "/orchestrator",
        "استعمل orchestrator",
        "استخدم orchestrator",
        "use orchestrator",
        "using orchestrator",
    )
    return any(p in low for p in patterns)


def orchestrator_executed(transcript: str) -> bool:
    patterns = (
        r'commandline[^\n]{0,200}\borchestrator\s+(?:help|doctor|run|start|launch|exec|limits|models|sessions)',
        r'"CommandLine"\s*:\s*"[^"\n]*\borchestrator\s+(?:help|doctor|run|start|launch|exec|limits|models|sessions)',
    )
    return any(re.search(p, transcript, re.IGNORECASE) for p in patterns)


def recent_text(transcript: str, limit: int = 100_000) -> str:
    return transcript[-limit:]
