#!/usr/bin/env python3
import fnmatch
import json
import posixpath
import sys
from typing import Any


def normalize(path: str) -> str | None:
    value = path.replace("\\", "/")
    if value.startswith("/"):
        return None
    normalized = posixpath.normpath(value)
    if normalized in {"", ".", ".."} or normalized.startswith("../"):
        return None
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def in_scope(path: str, allowed_scope: list[str]) -> bool:
    normalized = normalize(path)
    if normalized is None:
        return False
    for raw_scope in allowed_scope:
        scope = normalize(raw_scope.rstrip("/"))
        if scope is None:
            continue
        if raw_scope.endswith("/**"):
            prefix = scope.removesuffix("/**").rstrip("/")
            if normalized == prefix or normalized.startswith(prefix + "/"):
                return True
        elif any(character in scope for character in "*?["):
            if fnmatch.fnmatchcase(normalized, scope):
                return True
        elif normalized == scope or normalized.startswith(scope + "/"):
            return True
    return False


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = payload.get("allowed_scope")
    changed = payload.get("changed_files")
    if not isinstance(allowed, list) or not allowed or not all(isinstance(item, str) for item in allowed):
        return {"decision": "deny", "reason": "allowed_scope must be a non-empty string list."}
    if not isinstance(changed, list) or not all(isinstance(item, str) for item in changed):
        return {"decision": "deny", "reason": "changed_files must be a string list."}
    outside = sorted(path for path in changed if not in_scope(path, allowed))
    if outside:
        return {"decision": "deny", "reason": "scope_drift", "out_of_scope": outside}
    return {"decision": "allow", "changed_files": sorted(changed)}


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError, TypeError):
        payload = {}
    print(json.dumps(evaluate(payload if isinstance(payload, dict) else {}), ensure_ascii=False))


if __name__ == "__main__":
    main()
