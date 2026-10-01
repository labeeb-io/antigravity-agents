# Official Antigravity sources used for this migration

- Workflows to skills migration: https://antigravity.google/docs/migration/workflows-to-skills
- Plugins: https://antigravity.google/docs/plugins
- Custom subagents: https://antigravity.google/docs/subagents/
- Rules: https://antigravity.google/docs/rules/
- Hooks: https://antigravity.google/docs/hooks
- Antigravity changelog (custom-agent dependency declarations): https://antigravity.google/docs/changelog

Key verified design facts:
- Legacy workflows are deprecated and scheduled for retirement on 2026-11-01.
- Skills remain slash-command invocable and can bundle references/scripts.
- Plugins can package skills, custom agents, rules and hooks.
- Custom subagents have isolated conversation context, support `inherit|branch|share` workspaces, and can nest up to 10 levels.
- Rules under `.agents/rules/*.md` require valid YAML `trigger` frontmatter.
- Hooks can enforce PreToolUse decisions and Stop continuation gates.
