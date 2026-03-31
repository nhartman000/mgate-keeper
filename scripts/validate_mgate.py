#!/usr/bin/env python3
"""
Validator for mgate-keeper project files (lightweight, read-only).
Checks schema_version presence, relative path resolution, and basic contract alignment.
"""
import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / 'mgate_keeper' / 'projects'

def load_json(path: Path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def main(mg8_file='photosynthesis.mg8'):
    mg8_path = BASE / mg8_file
    if not mg8_path.exists():
        print(f'FAIL: mg8 file not found: {mg8_path}')
        return 1

    mg8 = load_json(mg8_path)
    issues = []

    # schema_version in mg8
    if 'schema_version' not in mg8:
        issues.append('mg8 missing schema_version')

    run_trace = mg8.get('run_trace_id')

    # Resolve referenced files
    refs = []
    for k in ['gst_context', 'qson_audit_log']:
        if k in mg8:
            refs.append(mg8[k])

    for entry in mg8.get('g8son_gates', []):
        refs.append(entry)

    for r in refs:
        p = BASE / r
        if not p.exists():
            issues.append(f'referenced file not found: {r}')
        else:
            data = load_json(p)
            if 'schema_version' not in data:
                issues.append(f'{r} missing schema_version')

    # gst emits vs g8son expects
    gst_path = BASE / mg8['gst_context']
    gst = load_json(gst_path)
    gst_emits = set(gst.get('emits', []))

    for gate_rel in mg8.get('g8son_gates', []):
        gate_path = BASE / gate_rel
        gate = load_json(gate_path)
        gate_expects = set(gate.get('expects', []))
        if not gst_emits.issuperset(gate_expects):
            issues.append(f'gst.emits does not cover gate.expects for {gate_rel}: missing {gate_expects - gst_emits}')

    # pipeline_contract alignment
    pipeline_contract = mg8.get('pipeline_contract', [])
    g8son_produces = set()
    for gate_rel in mg8.get('g8son_gates', []):
        gate = load_json(BASE / gate_rel)
        g8son_produces.update(gate.get('produces', []))

    for contract in pipeline_contract:
        if contract['to'] == 'qson':
            required = set(contract.get('fields', []))
            if not required.issubset(g8son_produces):
                issues.append(f'pipeline_contract requires fields {required} but g8son.produces has {g8son_produces}')

    # qson events trace ids and run_trace_id consistency
    qson = load_json(BASE / mg8['qson_audit_log'])
    if 'run_trace_id' not in qson:
        issues.append('qson missing run_trace_id')
    else:
        if run_trace and qson['run_trace_id'] != run_trace:
            issues.append('run_trace_id mismatch between mg8 and qson')

    events = qson.get('events', [])
    if not isinstance(events, list) or len(events) == 0:
        issues.append('qson.events must be a non-empty array')
    else:
        for ev in events:
            if 'trace_id' not in ev:
                issues.append('qson.events[].trace_id missing')

    if issues:
        print('FAIL')
        for it in issues:
            print('- ', it)
        return 2
    else:
        print('PASS')
        return 0

if __name__ == '__main__':
    raise SystemExit(main())
