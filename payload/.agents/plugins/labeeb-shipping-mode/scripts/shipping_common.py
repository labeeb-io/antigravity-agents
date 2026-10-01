#!/usr/bin/env python3
import json
import posixpath
import sys
from pathlib import Path
from typing import Any


ACTOR_MARKERS = {
    "release_coordinator": "LABEEB_RELEASE_COORDINATOR",
    "discovery_coordinator": "LABEEB_DISCOVERY_COORDINATOR",
    "discovery_researcher": "LABEEB_DISCOVERY_RESEARCHER",
    "experiment_executor": "LABEEB_EXPERIMENT_EXECUTOR",
    "implementation_executor": "LABEEB_IMPLEMENTATION_EXECUTOR",
    "release_auditor": "LABEEB_RELEASE_AUDITOR",
}


def load_stdin() -> dict[str, Any]:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def load_transcript(path: str, max_bytes: int = 500_000) -> str:
    if not path:
        return ""
    transcript = Path(path).expanduser()
    try:
        size = transcript.stat().st_size
        with transcript.open("rb") as handle:
            if size > max_bytes:
                handle.seek(size - max_bytes)
            return handle.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def actor(transcript: str) -> str:
    """Return a proven actor, a valid parent session, or fail-closed unknown."""
    initial_records: list[dict[str, Any]] = []
    for line in transcript.splitlines():
        try:
            record = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(record, dict):
            initial_records.append(record)
        if len(initial_records) >= 20:
            break

    if not initial_records:
        return "unknown"

    filtered = [
        r for r in initial_records
        if r.get("type") not in {"GENERIC", "USER_INPUT"} and r.get("source") != "USER_EXPLICIT"
    ]
    search_text = json.dumps(filtered if filtered else initial_records, ensure_ascii=False)
    for actor_name, marker in ACTOR_MARKERS.items():
        if f"Marker: `{marker}`" in search_text or f"Marker: {marker}" in search_text:
            return actor_name
    return "parent"


def target_path(args: dict[str, Any]) -> str:
    for key in ("TargetFile", "targetFile", "AbsolutePath", "FilePath", "filePath", "path"):
        value = args.get(key)
        if isinstance(value, str) and value:
            return posixpath.normpath(value.replace("\\", "/"))
    return ""


def command_stdin(args: dict[str, Any]) -> str:
    for key in ("Stdin", "stdin", "Input", "input"):
        value = args.get(key)
        if isinstance(value, str):
            return value
    return ""
