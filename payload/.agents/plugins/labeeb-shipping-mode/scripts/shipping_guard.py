#!/usr/bin/env python3
import json
import re
import shlex
from pathlib import Path, PurePosixPath
from typing import Any

from shipping_common import actor, command_stdin, load_stdin, load_transcript, target_path


READ_ONLY_ACTORS = {"discovery_coordinator", "discovery_researcher", "release_auditor"}
WRITE_TOOLS = {
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "apply_patch",
    "delete_file",
    "move_file",
}
PROTECTED_CORE = (
    "tasks/release-v0.1/01_RELEASE_CONTRACT.md",
    "tasks/release-v0.1/02_OPERATING_MANUAL.md",
    "tasks/release-v0.1/03_DELEGATION_RECORD.md",
    "tasks/release-v0.1/04_ROLE_PROMPTS.md",
    ".agents/plugins/labeeb-shipping-mode",
    ".orchestrator",
    "skills/labeeb-orchestrator",
    "AGENTS.md",
)
OPS_ALLOWED = (
    "tasks/release-v0.1/00_RELEASE_CONTROL.md",
    "tasks/release-v0.1/sprints",
    "tasks/release-v0.1/reports",
)
RESEARCH_RUNTIMES = {
    "codex-researcher-fast",
    "codex-researcher-standard",
    "codex-researcher-deep",
    "claude-researcher",
    "claude-reviewer",
}
READ_ONLY_EXECUTABLES = {
    "cat", "command", "curl", "cut", "docker", "find", "git", "grep", "head",
    "jq", "ls", "pwd", "readlink", "realpath", "rg", "sed",
    "sort", "stat", "tail", "test", "tr", "uniq", "wc", "which",
}


def result(decision: str, reason: str = "") -> dict[str, str]:
    response = {"decision": decision}
    if reason:
        response["reason"] = reason
    return response


def is_scratch_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if any(
        normalized.startswith(prefix)
        for prefix in (
            "/tmp/",
            "tmp/",
            "/home/hany/.gemini/",
            "/home/hany/.orchestrator/",
            ".orchestrator/scratch/",
        )
    ) or "/scratch/" in normalized or "/brain/" in normalized:
        if not path_matches(path, PROTECTED_CORE) and not normalized.startswith("api/") and not normalized.startswith("frontend/"):
            return True
    return False


def path_matches(path: str, candidates: tuple[str, ...]) -> bool:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return any(
        normalized == candidate
        or normalized.startswith(candidate.rstrip("/") + "/")
        or normalized.endswith("/" + candidate)
        for candidate in candidates
    )


def parse_manifest(raw: str) -> list[dict[str, Any]] | None:
    try:
        manifest = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    tasks = manifest.get("tasks") if isinstance(manifest, dict) else None
    if not isinstance(tasks, list) or not tasks:
        return None
    return tasks if all(isinstance(task, dict) for task in tasks) else None


def safe_orchestrator_command(command: str, stdin: str, who: str) -> bool:
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    if len(argv) < 2 or argv[0] not in {"./.orchestrator/orchestrator", ".orchestrator/orchestrator"}:
        return False

    operation = argv[1]
    if operation in {"help", "doctor", "models", "limits", "ps", "read", "logs", "events", "watch", "interrupt"}:
        return True
    if operation != "launch" or "-f" not in argv:
        return False
    try:
        manifest_source = argv[argv.index("-f") + 1]
    except (ValueError, IndexError):
        return False

    raw_manifest = None
    if manifest_source == "-":
        raw_manifest = stdin
    else:
        path = Path(manifest_source)
        if path.is_file():
            try:
                raw_manifest = path.read_text(encoding="utf-8")
            except Exception:
                return False
        else:
            return False

    if not raw_manifest:
        return False

    tasks = parse_manifest(raw_manifest)
    if tasks is None or len(tasks) != 1:
        return False
    task = tasks[0]
    runtime = task.get("runtime")
    prompt = task.get("task")
    if runtime not in RESEARCH_RUNTIMES or not isinstance(prompt, str):
        return False
    if not prompt.startswith("[READ-ONLY RESEARCH CONTRACT]"):
        return False
    if who != "release_auditor" and runtime == "claude-reviewer":
        return False
    return True


def curl_is_read_only(argv: list[str]) -> bool:
    state_changing = {
        "-d", "--data", "--data-ascii", "--data-binary", "--data-raw", "--data-urlencode",
        "-F", "--form", "--form-string", "--json", "-T", "--upload-file",
        "-o", "--output", "-O", "--remote-name", "--remote-name-all", "--output-dir",
    }
    safe_methods = {"GET", "HEAD", "OPTIONS"}
    index = 1
    while index < len(argv):
        argument = argv[index]
        if argument in state_changing or any(argument.startswith(flag + "=") for flag in state_changing if flag.startswith("--")):
            return False
        if argument in {"-X", "--request"}:
            index += 1
            if index >= len(argv) or argv[index].upper() not in safe_methods:
                return False
        elif argument.startswith("-X") and argument[2:].upper() not in safe_methods:
            return False
        elif argument.startswith("--request=") and argument.split("=", 1)[1].upper() not in safe_methods:
            return False
        elif argument.startswith("-") and not argument.startswith("--") and any(
            flag in argument[1:] for flag in ("d", "F", "T", "o", "O")
        ):
            return False
        index += 1
    return True


def safe_read_only_command(command: str, stdin: str, who: str) -> bool:
    if not command.strip():
        return False
    if re.search(r"[\r\n;\x60<>]|\$\(|&&|\|\||\|", command):
        return False
    if safe_orchestrator_command(command, stdin, who):
        return True

    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    if not argv:
        return False
    executable = PurePosixPath(argv[0]).name
    if executable not in READ_ONLY_EXECUTABLES:
        return False

    low = " ".join(argv).lower()
    if executable == "command":
        return len(argv) == 3 and argv[1] == "-v"
    if executable == "git":
        return (
            len(argv) >= 2
            and argv[1] in {"status", "diff", "show", "log", "rev-parse", "ls-files", "grep"}
            and not any(
                arg in {"--ext-diff", "--textconv", "--open-files-in-pager", "--output"}
                or arg.startswith("--output=")
                for arg in argv[2:]
            )
        )
    if executable == "docker":
        if any(arg in {"-o", "--output"} or arg.startswith("--output=") for arg in argv[1:]):
            return False
        if len(argv) >= 3 and argv[1] == "compose":
            return argv[2] in {"ps", "logs", "config", "top", "images", "version"}
        return len(argv) >= 2 and argv[1] in {"inspect", "images", "info", "logs", "ps", "stats", "top", "version"}
    if executable == "curl":
        return curl_is_read_only(argv)
    if executable == "rg" and any(arg == "--pre" or arg.startswith("--pre=") for arg in argv[1:]):
        return False
    if executable == "sort" and any(arg == "-o" or arg.startswith("--output") for arg in argv[1:]):
        return False
    if executable == "sed" and (
        any(arg == "-i" or arg.startswith("-i") for arg in argv[1:])
        or any(re.search(r"(?:^|[;\s])w\s", arg) for arg in argv[1:])
    ):
        return False
    forbidden = (r"\bfind\b.*(?:-delete|-exec|-execdir|-ok|-okdir)\b",)
    return not any(re.search(pattern, low, re.I | re.S) for pattern in forbidden)


def evaluate(payload: dict[str, Any]) -> dict[str, str]:
    transcript = load_transcript(str(payload.get("transcriptPath", "")))
    who = actor(transcript)
    tool = payload.get("toolCall", {}) or {}
    name = str(tool.get("name", ""))
    args = tool.get("args", {}) or {}
    path = target_path(args)

    if name in WRITE_TOOLS:
        if who == "unknown":
            return result("deny", "Shipping guard could not prove the acting session identity from a valid transcript.")
        if who in READ_ONLY_ACTORS or who == "experiment_executor":
            if path and is_scratch_path(path):
                return result("allow")
            return result("deny", "Discovery, experiment, and audit actors are evidence-only; repository writes are forbidden.")
        if who == "implementation_executor":
            if path_matches(
                path,
                (
                    "tasks/release-v0.1",
                    ".agents/plugins/labeeb-shipping-mode",
                    ".orchestrator",
                    "skills/labeeb-orchestrator",
                    "AGENTS.md",
                ),
            ):
                return result("deny", "Implementation worker cannot edit release governance or the shipping-mode control plane.")
            return result("allow")
        if who == "release_coordinator":
            if path_matches(path, PROTECTED_CORE):
                return result("force_ask", "This is founder-controlled governance. Routine Shipping Mode may not change it silently.")
            if not path or not path_matches(path, OPS_ALLOWED):
                return result("deny", "Release Coordinator owns operational records, not product-code edits.")
            return result("allow")
        if path_matches(path, PROTECTED_CORE):
            return result("force_ask", "Protected Labeeb release-governance file. Confirm this governance change explicitly.")
        return result("allow")

    if name != "run_command":
        return result("allow")

    command = str(args.get("CommandLine", ""))
    stdin = command_stdin(args)
    if who == "unknown":
        return result("deny", "Shipping guard could not prove the acting session identity from a valid transcript.")
    if who in READ_ONLY_ACTORS and not safe_read_only_command(command, stdin, who):
        return result("deny", "Discovery and audit commands are fail-closed: use one read-only command or a validated Orchestrator stdin manifest.")

    if who == "implementation_executor" and re.search(
        r"\bgit\s+(?:push|merge|rebase|reset|clean|checkout|switch|cherry-pick)\b|"
        r"\b(?:wrangler|doctl|kubectl|terraform)\b[^\n]*(?:deploy|apply|destroy)|"
        r"\bgh\s+pr\s+(?:merge|create)\b",
        command,
        re.I,
    ):
        return result("deny", "Implementation executor is local-only; remote publication and deployment are forbidden.")

    if who == "experiment_executor" and re.search(
        r"\bgit\s+(?:add|commit|push|merge|rebase|reset|clean|checkout|switch|cherry-pick)\b|"
        r"\bphp\s+artisan\s+(?:migrate|db:seed|seed)|"
        r"\bdocker\s+compose\s+(?:up|down|restart|stop|rm|build|pull)\b|"
        r"\b(?:rm|mv|cp|chmod|chown)\b",
        command,
        re.I,
    ):
        return result("deny", "Experiment executor is bounded runtime-only; git/schema/infrastructure/destructive operations are forbidden.")

    if who == "experiment_executor" and re.search(
        r"\bcurl\b[^\n]*(?:-x\s*(?:post|put|patch|delete)|--request\s*(?:post|put|patch|delete)|(?:-d|--data|--data-raw|--data-binary)\b)",
        command,
        re.I | re.S,
    ):
        urls = re.findall(r"https?://[^\s'\"\\]+", command, re.I)
        if any(
            not re.match(r"https?://(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?(?:/|$)", url, re.I)
            for url in urls
        ):
            return result("deny", "Automatic discovery experiment mutation is local-only.")

    if re.search(r"\bgit\s+push\b|\bgh\s+pr\s+merge\b|\bterraform\s+(?:apply|destroy)\b|\bkubectl\s+(?:apply|delete)\b", command, re.I):
        return result("force_ask", "Remote publication or high-impact infrastructure action requires explicit tool approval.")
    return result("allow")


def main() -> None:
    print(json.dumps(evaluate(load_stdin()), ensure_ascii=False))


if __name__ == "__main__":
    main()
