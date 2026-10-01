#!/usr/bin/env python3
"""Regression checks for shipping-mode guard and Orchestrator boundaries."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
GUARD = "./scripts/shipping_guard.py"
DISCOVERY_GUARD = "./scripts/discovery_guard.py"
DRIFT = "./scripts/discovery_drift.py"
STOP = "./scripts/discovery_stop.py"
SCOPE_GUARD = "./scripts/scope_guard.py"


def run_hook(script: str, payload: dict, raw_input: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", script],
        input=raw_input if raw_input is not None else json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        check=False,
    )


def run_guard(
    marker: str | None,
    tool: str,
    args: dict,
    *,
    malformed_transcript: bool = False,
    script: str = GUARD,
) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        transcript = Path(directory) / "transcript.jsonl"
        if malformed_transcript:
            transcript.write_text("not-json\n", encoding="utf-8")
        elif marker:
            transcript.write_text(
                '{"type":"metadata"}\n'
                + json.dumps({"step_index": 0, "content": f"Marker: {marker}"})
                + "\n",
                encoding="utf-8",
            )
        else:
            transcript.write_text('{"step_index":0,"type":"USER_INPUT","content":"normal parent"}\n', encoding="utf-8")
        payload = {"transcriptPath": str(transcript), "toolCall": {"name": tool, "args": args}}
        process = run_hook(script, payload)
        if process.returncode != 0:
            raise AssertionError(f"Hook failed ({process.returncode}): {process.stderr}")
        return json.loads(process.stdout)


class GuardTests(unittest.TestCase):
    def test_hook_cwd_execution_guard(self):
        process = run_hook(GUARD, {"toolCall": {"name": "view_file", "args": {}}})
        self.assertEqual(process.returncode, 0)
        self.assertEqual(json.loads(process.stdout)["decision"], "allow")

    def test_hook_cwd_execution_drift(self):
        self.assertEqual(run_hook(DRIFT, {"transcriptPath": ""}).returncode, 0)

    def test_hook_cwd_execution_stop(self):
        self.assertEqual(run_hook(STOP, {"transcriptPath": ""}).returncode, 0)

    def test_fail_fast_on_missing_script(self):
        process = run_hook("./scripts/non_existent_guard.py", {})
        self.assertNotEqual(process.returncode, 0)

    def test_only_shipping_guard_is_active_pre_tool_policy(self):
        hooks = json.loads((ROOT / "hooks.json").read_text(encoding="utf-8"))
        commands = [
            hook["command"]
            for group in hooks.values()
            for entries in group.values()
            for entry in entries
            for hook in entry.get("hooks", [entry])
            if hook.get("type") == "command"
        ]
        self.assertIn("python3 ./scripts/shipping_guard.py", commands)
        self.assertNotIn("python3 ./scripts/discovery_guard.py", commands)

    def test_fast_researcher_is_pinned_read_only(self):
        config = json.loads((REPO / ".orchestrator/config.json").read_text(encoding="utf-8"))
        args = config["agents"]["codex-researcher-fast"]["args"]
        self.assertEqual(args[args.index("--model") + 1], "gpt-5.6-luna")
        self.assertEqual(args[args.index("--sandbox") + 1], "read-only")

    def test_agents_do_not_depend_on_absolute_skill_symlink(self):
        for agent_file in (REPO / ".agents/agents").glob("*/agent.md"):
            content = agent_file.read_text(encoding="utf-8")
            self.assertNotRegex(content, r"(?m)^\s*-\s+labeeb-orchestrator\s*$")

    def test_labeeb_orchestrator_metadata_uses_supported_products(self):
        metadata = (REPO / "skills/labeeb-orchestrator/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertNotRegex(metadata, r"(?m)^\s*-\s+api\s*$")

    def test_discovery_compatibility_entrypoint_matches_shipping_guard(self):
        args = {"CommandLine": "git add api/app/X.php"}
        active = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", args, script=GUARD)
        compatibility = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", args, script=DISCOVERY_GUARD)
        self.assertEqual(compatibility, active)

    def test_discovery_write_denied(self):
        decision = run_guard("LABEEB_DISCOVERY_COORDINATOR", "write_to_file", {"TargetFile": "src/x.php"})
        self.assertEqual(decision["decision"], "deny")

    def test_auditor_write_denied(self):
        decision = run_guard("LABEEB_RELEASE_AUDITOR", "write_to_file", {"TargetFile": "tasks/release-v0.1/reports/a.md"})
        self.assertEqual(decision["decision"], "deny")

    def test_unknown_actor_write_denied(self):
        process = run_hook(GUARD, {"toolCall": {"name": "write_to_file", "args": {"TargetFile": "api/app/X.php"}}})
        self.assertEqual(json.loads(process.stdout)["decision"], "deny")

    def test_malformed_transcript_command_denied(self):
        decision = run_guard(None, "run_command", {"CommandLine": "git status"}, malformed_transcript=True)
        self.assertEqual(decision["decision"], "deny")

    def test_valid_parent_product_write_allowed(self):
        decision = run_guard(None, "write_to_file", {"TargetFile": "api/app/X.php"})
        self.assertEqual(decision["decision"], "allow")

    def test_implementation_product_write_allowed(self):
        decision = run_guard("LABEEB_IMPLEMENTATION_EXECUTOR", "write_to_file", {"TargetFile": "api/app/X.php"})
        self.assertEqual(decision["decision"], "allow")

    def test_implementation_governance_write_denied(self):
        decision = run_guard(
            "LABEEB_IMPLEMENTATION_EXECUTOR",
            "write_to_file",
            {"TargetFile": "tasks/release-v0.1/00_RELEASE_CONTROL.md"},
        )
        self.assertEqual(decision["decision"], "deny")

    def test_implementation_orchestrator_control_plane_write_denied(self):
        for target in (".orchestrator/config.json", "skills/labeeb-orchestrator/SKILL.md"):
            with self.subTest(target=target):
                decision = run_guard(
                    "LABEEB_IMPLEMENTATION_EXECUTOR",
                    "write_to_file",
                    {"TargetFile": target},
                )
                self.assertEqual(decision["decision"], "deny")

    def test_coordinator_operational_write_allowed(self):
        decision = run_guard(
            "LABEEB_RELEASE_COORDINATOR",
            "write_to_file",
            {"TargetFile": "tasks/release-v0.1/reports/a.md"},
        )
        self.assertEqual(decision["decision"], "allow")

    def test_coordinator_product_write_denied(self):
        decision = run_guard("LABEEB_RELEASE_COORDINATOR", "write_to_file", {"TargetFile": "api/app/X.php"})
        self.assertEqual(decision["decision"], "deny")

    def test_contract_change_requires_ask(self):
        decision = run_guard(
            "LABEEB_RELEASE_COORDINATOR",
            "replace_file_content",
            {"TargetFile": "tasks/release-v0.1/01_RELEASE_CONTRACT.md"},
        )
        self.assertEqual(decision["decision"], "force_ask")

    def test_read_only_shell_writes_denied(self):
        commands = (
            "echo changed > api/app/X.php",
            "tee api/app/X.php",
            "rm api/app/X.php",
            "python3 -c 'open(\"api/app/X.php\", \"w\").write(\"x\")'",
            "sed -i s/a/b/ api/app/X.php",
            "find api -name '*.php' -delete",
        )
        for command in commands:
            with self.subTest(command=command):
                decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", {"CommandLine": command})
                self.assertEqual(decision["decision"], "deny")

    def test_read_only_http_mutations_and_downloads_denied(self):
        commands = (
            "curl -XPOST https://example.test/x",
            "curl --request=DELETE https://example.test/x",
            "curl --json '{}' https://example.test/x",
            "curl -o result.json https://example.test/x",
            "curl -O https://example.test/x",
        )
        for command in commands:
            with self.subTest(command=command):
                decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", {"CommandLine": command})
                self.assertEqual(decision["decision"], "deny")

    def test_read_only_commands_cannot_use_write_or_exec_options(self):
        commands = (
            "git diff --output=/tmp/diff",
            "git diff --ext-diff",
            "docker compose config --output /tmp/config",
            "rg --pre ./script pattern .",
        )
        for command in commands:
            with self.subTest(command=command):
                decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", {"CommandLine": command})
                self.assertEqual(decision["decision"], "deny")

    def test_read_only_git_mutations_denied(self):
        for command in ("git add .", "git commit -m x", "git worktree add /tmp/x HEAD", "git restore api/app/X.php"):
            with self.subTest(command=command):
                decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", {"CommandLine": command})
                self.assertEqual(decision["decision"], "deny")

    def test_read_only_installs_denied(self):
        for command in ("npm install x", "composer require x/y", "pip install x"):
            with self.subTest(command=command):
                decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", {"CommandLine": command})
                self.assertEqual(decision["decision"], "deny")

    def test_read_only_inspection_allowed(self):
        for command in ("git status --short", "rg -n shipping_guard.py .agents", "sed -n 1,20p AGENTS.md"):
            with self.subTest(command=command):
                decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", {"CommandLine": command})
                self.assertEqual(decision["decision"], "allow")

    def test_prompt_is_data_in_stdin_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            sentinel = Path(directory) / "executed"
            hostile = f"quotes ' \" backticks `touch {sentinel}` $(touch {sentinel})"
            manifest = {
                "schemaVersion": 1,
                "tasks": [{
                    "runtime": "codex-researcher-fast",
                    "name": "injection-test",
                    "task": "[READ-ONLY RESEARCH CONTRACT]\nQuestion: " + hostile,
                }],
            }
            args = {
                "CommandLine": "./.orchestrator/orchestrator launch -f - --json --compact --brief",
                "Stdin": json.dumps(manifest),
            }
            decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", args)
            self.assertEqual(decision["decision"], "allow")
            self.assertFalse(sentinel.exists())

    def test_prompt_is_data_in_file_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_file = Path(directory) / "task.json"
            manifest = {
                "schemaVersion": 1,
                "tasks": [{
                    "runtime": "codex-researcher-fast",
                    "name": "file-manifest-test",
                    "task": "[READ-ONLY RESEARCH CONTRACT]\nQuestion: inspect one route",
                }],
            }
            manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
            args = {
                "CommandLine": f"./.orchestrator/orchestrator launch -f {manifest_file} --json --compact --brief",
            }
            decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", args)
            self.assertEqual(decision["decision"], "allow")

    def test_discovery_scratch_write_allowed_and_product_write_denied(self):
        scratch_decision = run_guard(
            "LABEEB_DISCOVERY_RESEARCHER",
            "write_to_file",
            {"TargetFile": "/tmp/scratch/task.json"},
        )
        self.assertEqual(scratch_decision["decision"], "allow")

        brain_scratch_decision = run_guard(
            "LABEEB_DISCOVERY_RESEARCHER",
            "write_to_file",
            {"TargetFile": "/home/hany/.gemini/antigravity-ide/brain/123/scratch/task.json"},
        )
        self.assertEqual(brain_scratch_decision["decision"], "allow")

        product_decision = run_guard(
            "LABEEB_DISCOVERY_RESEARCHER",
            "write_to_file",
            {"TargetFile": "api/app/Services/TestService.php"},
        )
        self.assertEqual(product_decision["decision"], "deny")

    def test_orchestrator_prompt_on_command_line_denied(self):
        args = {
            "CommandLine": './.orchestrator/orchestrator launch codex-researcher-fast --brief "$(touch /tmp/nope)"'
        }
        decision = run_guard("LABEEB_DISCOVERY_RESEARCHER", "run_command", args)
        self.assertEqual(decision["decision"], "deny")

    def test_non_repository_orchestrator_entrypoint_denied(self):
        manifest = {
            "schemaVersion": 1,
            "tasks": [{
                "runtime": "codex-researcher-fast",
                "name": "probe",
                "task": "[READ-ONLY RESEARCH CONTRACT]\nQuestion: inspect one file",
            }],
        }
        decision = run_guard(
            "LABEEB_DISCOVERY_RESEARCHER",
            "run_command",
            {
                "CommandLine": "/tmp/orchestrator launch -f - --json --compact --brief",
                "Stdin": json.dumps(manifest),
            },
        )
        self.assertEqual(decision["decision"], "deny")

    def test_experiment_local_post_allowed(self):
        decision = run_guard(
            "LABEEB_EXPERIMENT_EXECUTOR",
            "run_command",
            {"CommandLine": 'curl -X POST http://localhost:8080/x -d "{}"'},
        )
        self.assertEqual(decision["decision"], "allow")

    def test_experiment_prod_post_denied(self):
        decision = run_guard(
            "LABEEB_EXPERIMENT_EXECUTOR",
            "run_command",
            {"CommandLine": 'curl -X POST https://labeeb.io/api/x -d "{}"'},
        )
        self.assertEqual(decision["decision"], "deny")

    def test_worker_push_denied(self):
        decision = run_guard(
            "LABEEB_IMPLEMENTATION_EXECUTOR",
            "run_command",
            {"CommandLine": "git push origin x"},
        )
        self.assertEqual(decision["decision"], "deny")

    def test_scope_guard_allows_complete_in_scope_set(self):
        payload = {
            "allowed_scope": ["api/app/**", "api/tests/**"],
            "changed_files": ["api/app/X.php", "api/tests/XTest.php"],
        }
        process = run_hook(SCOPE_GUARD, payload)
        self.assertEqual(json.loads(process.stdout)["decision"], "allow")

    def test_scope_guard_rejects_entire_drifted_set(self):
        payload = {
            "allowed_scope": ["api/app/**"],
            "changed_files": ["api/app/X.php", "frontend/package.json"],
        }
        process = run_hook(SCOPE_GUARD, payload)
        result = json.loads(process.stdout)
        self.assertEqual(result["decision"], "deny")
        self.assertEqual(result["out_of_scope"], ["frontend/package.json"])

    def test_scope_guard_rejects_traversal_and_absolute_paths(self):
        for changed, allowed in (("../AGENTS.md", ["AGENTS.md"]), ("/tmp/X.php", ["tmp/**"])):
            with self.subTest(changed=changed):
                process = run_hook(
                    SCOPE_GUARD,
                    {"allowed_scope": allowed, "changed_files": [changed]},
                )
                self.assertEqual(json.loads(process.stdout)["decision"], "deny")


if __name__ == "__main__":
    unittest.main()
