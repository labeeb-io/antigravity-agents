#!/usr/bin/env python3
import json,re,sys
from shipping_common import load_stdin, load_transcript, actor, target_path

p=load_stdin(); tr=load_transcript(str(p.get('transcriptPath',''))); who=actor(tr)
tool=p.get('toolCall',{}) or {}; name=str(tool.get('name','')); args=tool.get('args',{}) or {}
path=target_path(args)

def out(decision, reason=''):
    d={'decision':decision}
    if reason: d['reason']=reason
    print(json.dumps(d,ensure_ascii=False)); raise SystemExit(0)

write_tools={'write_to_file','replace_file_content','multi_replace_file_content'}
protected_core=(
 'tasks/release-v0.1/01_RELEASE_CONTRACT.md',
 'tasks/release-v0.1/02_OPERATING_MANUAL.md',
 'tasks/release-v0.1/03_DELEGATION_RECORD.md',
 'tasks/release-v0.1/04_ROLE_PROMPTS.md',
 '.agents/plugins/labeeb-shipping-mode/',
 'AGENTS.md',
)
ops_allowed=(
 'tasks/release-v0.1/00_RELEASE_CONTROL.md',
 'tasks/release-v0.1/sprints/',
 'tasks/release-v0.1/reports/',
)

if name in write_tools:
    if who in {'discovery_coordinator','discovery_researcher','experiment_executor'}:
        out('deny','Discovery actors are evidence-only; repository file writes are outside discovery authority.')
    if who=='release_auditor':
        if '/tasks/release-v0.1/reports/' in ('/'+path.lstrip('/')) or path.startswith('tasks/release-v0.1/reports/'):
            out('allow')
        out('deny','Independent auditor may write only its report under tasks/release-v0.1/reports/.')
    if who=='implementation_executor':
        if any(x in path for x in ('tasks/release-v0.1/','.agents/plugins/labeeb-shipping-mode/','AGENTS.md')):
            out('deny','Implementation worker cannot edit release governance or the shipping-mode control plane.')
        out('allow')
    if who=='release_coordinator':
        if any(x in path for x in protected_core):
            out('force_ask','This is founder-controlled governance. Routine Shipping Mode may not change it silently.')
        if path and not any(x in path for x in ops_allowed):
            out('deny','Release Coordinator owns operational records, not product-code edits. Delegate code changes to implementation-executor.')
        out('allow')
    # Main/unknown agent: protect canonical governance but do not over-block unrelated work.
    if any(x in path for x in protected_core):
        out('force_ask','Protected Labeeb release-governance file. Confirm this governance change explicitly.')
    out('allow')

if name!='run_command': out('allow')
cmd=str(args.get('CommandLine','')); low=cmd.lower()

# Implementation worker cannot publish/deploy or rewrite git history.
if who=='implementation_executor' and re.search(r'\bgit\s+(push|merge|rebase|reset|clean|checkout|switch|cherry-pick)\b|\b(?:wrangler|doctl|kubectl|terraform)\b[^\n]*(?:deploy|apply|destroy)|\bgh\s+pr\s+(?:merge|create)\b',cmd,re.I):
    out('deny','Implementation executor is local-only. Push/PR/merge/deploy belongs to the release coordinator after validation and policy checks.')

# Discovery/audit hard read-only command boundaries.
if who in {'discovery_coordinator','discovery_researcher','release_auditor'}:
    if re.search(r'\bcurl\b[^\n]*(?:-x\s*(?:post|put|patch|delete)|--request\s*(?:post|put|patch|delete)|(?:-d|--data|--data-raw|--data-binary)\b)',cmd,re.I|re.S):
        out('deny','Read-only discovery/audit actor cannot send state-changing HTTP requests without an explicit experiment execution path.')
    if re.search(r'\bphp\s+artisan\s+(?:migrate|db:seed|seed|queue:(?:work|restart)|schedule:(?:work|run)|crawl:)|\bdocker\s+compose\s+(?:up|down|restart|start|stop|rm|build|pull)\b',cmd,re.I):
        out('deny','Read-only discovery/audit actor cannot mutate runtime state.')

# Experiment executor: local bounded mutation only; never infra/schema/git/destructive.
if who=='experiment_executor':
    if re.search(r'\bgit\s+(?:add|commit|push|merge|rebase|reset|clean|checkout|switch|cherry-pick)\b|\bphp\s+artisan\s+(?:migrate|db:seed|seed)|\bdocker\s+compose\s+(?:up|down|restart|stop|rm|build|pull)\b|\b(?:rm|mv|cp|chmod|chown)\b',cmd,re.I):
        out('deny','Experiment executor is bounded runtime-only; git/schema/infrastructure/destructive operations are forbidden.')
    if re.search(r'\bcurl\b[^\n]*(?:-x\s*(?:post|put|patch|delete)|--request\s*(?:post|put|patch|delete)|(?:-d|--data|--data-raw|--data-binary)\b)',cmd,re.I|re.S):
        urls=re.findall(r'https?://[^\s\'"\\]+',cmd,re.I)
        for u in urls:
            if not re.match(r'https?://(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?(?:/|$)',u,re.I):
                out('deny','Automatic discovery experiment mutation is local-only. Non-local mutation requires an explicitly authorized production/staging path.')

# Force a user-visible approval for high-impact publication/destructive operations regardless of actor.
if re.search(r'\bgit\s+push\b|\bgh\s+pr\s+merge\b|\bterraform\s+(?:apply|destroy)\b|\bkubectl\s+(?:apply|delete)\b',cmd,re.I):
    out('force_ask','Remote publication or high-impact infrastructure action requires explicit tool approval even when delegated by Shipping Mode policy.')

out('allow')
