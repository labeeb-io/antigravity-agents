# Compatibility

## Native mode

The package is designed for Antigravity surfaces that expose custom subagents and `invoke_subagent`. Official current custom-subagent docs list Antigravity 2.0 and Antigravity CLI. Plugins, skills, rules and hooks are documented across Antigravity 2.0, CLI and IDE.

## Fallback mode

If native custom-subagent execution is unavailable, `/shipping`, `/discovery`, `/exec` and `/audit` instruct the current agent to use the project's installed Orchestrator CLI internally. This preserves isolated workers without manual founder handoffs.

If neither native subagents nor Orchestrator is available for a step that requires independence, the correct result is `BLOCKED`, not simulated isolation.

## Browser audits

The official built-in Browser subagent is invoked via `/browser`. This package does not invent an undocumented browser tool name for custom agents. If a required visual journey cannot be executed by the active surface, the auditor must return a browser-capability blocker rather than substituting code review.

## Runtime isolation fallback

Official Custom Subagents documentation currently lists Antigravity 2.0 and Antigravity CLI for native `invoke_subagent`. Plugin packaging itself is supported across Antigravity 2.0, CLI, and IDE. Therefore the skills use native subagents when exposed by the active surface, then the project Orchestrator internally, and only then a read-only inline/BLOCKED fallback.
