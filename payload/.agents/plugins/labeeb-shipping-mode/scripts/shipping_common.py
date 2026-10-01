#!/usr/bin/env python3
import json
from pathlib import Path

def load_stdin():
    try: return json.load(__import__('sys').stdin)
    except Exception: return {}

def load_transcript(path):
    if not path: return ''
    p=Path(path).expanduser()
    try: return p.read_text(encoding='utf-8', errors='ignore')[-500000:]
    except Exception: return ''

def actor(transcript):
    markers=[
      ('release_coordinator','LABEEB_RELEASE_COORDINATOR'),
      ('discovery_coordinator','LABEEB_DISCOVERY_COORDINATOR'),
      ('discovery_researcher','LABEEB_DISCOVERY_RESEARCHER'),
      ('experiment_executor','LABEEB_EXPERIMENT_EXECUTOR'),
      ('implementation_executor','LABEEB_IMPLEMENTATION_EXECUTOR'),
      ('release_auditor','LABEEB_RELEASE_AUDITOR'),
    ]
    for a,m in markers:
        if m in transcript: return a
    return 'unknown'

def target_path(args):
    for k in ('TargetFile','targetFile','AbsolutePath','FilePath','filePath','path'):
        v=args.get(k)
        if isinstance(v,str) and v: return v.replace('\\\\','/')
    return ''
