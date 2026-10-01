#!/usr/bin/env python3
import json, os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GUARD=ROOT/'scripts/shipping_guard.py'

def run_guard(marker, tool, args):
    with tempfile.TemporaryDirectory() as td:
        tr=Path(td)/'t.jsonl'; tr.write_text(marker,encoding='utf-8')
        payload={'transcriptPath':str(tr),'toolCall':{'name':tool,'args':args}}
        p=subprocess.run(['python3',str(GUARD)],input=json.dumps(payload),text=True,capture_output=True,cwd=str(ROOT/'scripts'))
        if p.returncode!=0: raise AssertionError(p.stderr)
        return json.loads(p.stdout)

class GuardTests(unittest.TestCase):
    def test_discovery_write_denied(self):
        self.assertEqual(run_guard('LABEEB_DISCOVERY_COORDINATOR','write_to_file',{'TargetFile':'src/x.php'})['decision'],'deny')
    def test_implementation_product_write_allowed(self):
        self.assertEqual(run_guard('LABEEB_IMPLEMENTATION_EXECUTOR','write_to_file',{'TargetFile':'api/app/X.php'})['decision'],'allow')
    def test_implementation_governance_write_denied(self):
        self.assertEqual(run_guard('LABEEB_IMPLEMENTATION_EXECUTOR','write_to_file',{'TargetFile':'tasks/release-v0.1/00_RELEASE_CONTROL.md'})['decision'],'deny')
    def test_coordinator_operational_write_allowed(self):
        self.assertEqual(run_guard('LABEEB_RELEASE_COORDINATOR','write_to_file',{'TargetFile':'tasks/release-v0.1/reports/a.md'})['decision'],'allow')
    def test_coordinator_product_write_denied(self):
        self.assertEqual(run_guard('LABEEB_RELEASE_COORDINATOR','write_to_file',{'TargetFile':'api/app/X.php'})['decision'],'deny')
    def test_contract_change_requires_ask(self):
        self.assertEqual(run_guard('LABEEB_RELEASE_COORDINATOR','replace_file_content',{'TargetFile':'tasks/release-v0.1/01_RELEASE_CONTRACT.md'})['decision'],'force_ask')
    def test_auditor_report_allowed(self):
        self.assertEqual(run_guard('LABEEB_RELEASE_AUDITOR','write_to_file',{'TargetFile':'tasks/release-v0.1/reports/a.md'})['decision'],'allow')
    def test_auditor_code_write_denied(self):
        self.assertEqual(run_guard('LABEEB_RELEASE_AUDITOR','write_to_file',{'TargetFile':'api/app/X.php'})['decision'],'deny')
    def test_experiment_local_post_allowed(self):
        d=run_guard('LABEEB_EXPERIMENT_EXECUTOR','run_command',{'CommandLine':'curl -X POST http://localhost:8080/x -d "{}"'})
        self.assertEqual(d['decision'],'allow')
    def test_experiment_prod_post_denied(self):
        d=run_guard('LABEEB_EXPERIMENT_EXECUTOR','run_command',{'CommandLine':'curl -X POST https://labeeb.io/api/x -d "{}"'})
        self.assertEqual(d['decision'],'deny')
    def test_worker_push_denied(self):
        self.assertEqual(run_guard('LABEEB_IMPLEMENTATION_EXECUTOR','run_command',{'CommandLine':'git push origin x'})['decision'],'deny')

if __name__=='__main__': unittest.main()
