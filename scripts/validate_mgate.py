#!/usr/bin/env python3
"""
Strict validator for mgate-keeper schema enforcement.

See repo docs for required invariants.
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / 'mgate_keeper' / 'projects'
FORBIDDEN_ROOT_KEYS = {"project_name", "metadata", "notes"}

def file_has_bom(path: Path) -> bool:
    b = path.read_bytes()
    return b.startswith(b'\xef\xbb\xbf')

def load_json_strict(path: Path):
    if file_has_bom(path):
        raise ValueError(f'BOM_PRESENT:{path}')
    s = path.read_text(encoding='utf-8')
    return json.loads(s)

def is_relative_path(p: str) -> bool:
    return not ("mgate_keeper" in p or ".." in p or Path(p).is_absolute())

def main(mg8_file='photosynthesis.mg8'):
    mg8_path = BASE / mg8_file
    if not mg8_path.exists():
        print(f'FAIL: mg8 file not found: {mg8_path}')
        return 1

    issues = []

    # Load mg8 strictly
    try:
        mg8 = load_json_strict(mg8_path)
    except ValueError as e:
        issues.append(str(e))
        print("FAIL")
        for it in issues: print("- ", it)
        return 2
    except Exception as e:
        issues.append(f'ERR_LOADING_MG8: {e}')
        print("FAIL")
        for it in issues: print("- ", it)
        return 2

    # Forbidden root keys
    for fk in FORBIDDEN_ROOT_KEYS:
        if fk in mg8:
            issues.append(f'mg8 contains forbidden root key: {fk}')

    # mg8 checks
    if 'schema_version' not in mg8:
        issues.append('mg8 missing schema_version')
    if 'run_trace_id' not in mg8:
        issues.append('mg8 missing run_trace_id')
    comp = mg8.get('compatibility')
    if not isinstance(comp, dict) or not all(k in comp for k in ('gst','g8son','qson')):
        issues.append('mg8.compatibility missing or incomplete (must include gst, g8son, qson)')

    pc = mg8.get('pipeline_contract')
    expected_pc = [
        {'from':'gst','to':'g8son','fields': ['event_candidate','confidence','ambiguity']},
        {'from':'g8son','to':'qson','fields': ['decision','status','trace_id']}
    ]
    if not isinstance(pc, list):
        issues.append('mg8.pipeline_contract missing or not list')
    else:
        for exp in expected_pc:
            found = False
            for c in pc:
                if c.get('from') == exp['from'] and c.get('to') == exp['to'] and set(c.get('fields',[])) == set(exp['fields']):
                    found = True
                    break
            if not found:
                issues.append(f'mg8.pipeline_contract missing expected mapping: {exp}')

    # resolve referenced files and ensure relative paths
    refs = []
    for key in ('gst_context','qson_audit_log'):
        if key in mg8:
            refs.append(mg8[key])
    for entry in mg8.get('g8son_gates', []):
        refs.append(entry)

    for r in refs:
        if not is_relative_path(r):
            issues.append(f'Non-relative path found in mg8: {r}')
        p = BASE / r
        if not p.exists():
            issues.append(f'referenced file not found: {r}')
        else:
            try:
                data = load_json_strict(p)
            except ValueError as e:
                issues.append(str(e))
                continue
            except Exception as e:
                issues.append(f'ERR_LOADING:{r} => {e}')
                continue
            if 'schema_version' not in data:
                issues.append(f'{r} missing schema_version')

    # gst -> g8son contract
    gst_path = BASE / mg8['gst_context']
    try:
        gst = load_json_strict(gst_path)
    except Exception as e:
        issues.append(f'Cannot load gst: {e}')
        print('FAIL'); print('- ', e); return 2

    gst_emits = set(gst.get('emits', []))
    required_emits = {'event_candidate','confidence','ambiguity'}
    if not gst_emits.issuperset(required_emits):
        issues.append(f'gst.emits does not cover required fields: missing {required_emits - gst_emits}')

    # g8son checks
    g8son_produces = set()
    for gate_rel in mg8.get('g8son_gates', []):
        gate_path = BASE / gate_rel
        try:
            gate = load_json_strict(gate_path)
        except Exception as e:
            issues.append(f'ERR_LOADING_GATE {gate_rel}: {e}')
            continue
        if 'gate_id' not in gate:
            issues.append(f'{gate_rel} missing gate_id')
        if 'atomic_requirements' not in gate:
            issues.append(f'{gate_rel} missing atomic_requirements')
        expects_set = set(gate.get('expects', []))
        if not expects_set.issubset(required_emits):
            issues.append(f'{gate_rel} expects mismatch: {expects_set}')
        produces = set(gate.get('produces', []))
        if 'trace_id' not in produces:
            issues.append(f'{gate_rel} produces does not include trace_id')
        g8son_produces.update(produces)
        if 'failure_policy' not in gate or not isinstance(gate.get('failure_policy'), dict):
            issues.append(f'{gate_rel} missing failure_policy')

    # pipeline_contract: ensure g8son.produces satisfies required qson fields
    pc_required = set()
    for c in mg8.get('pipeline_contract', []):
        if c.get('from') == 'g8son' and c.get('to') == 'qson':
            pc_required.update(c.get('fields', []))
    if not pc_required.issubset(g8son_produces):
        issues.append(f'g8son.produces does not satisfy mg8.pipeline_contract required qson fields: missing {pc_required - g8son_produces}')

    # qson checks
    qson_path = BASE / mg8['qson_audit_log']
    if not qson_path.exists():
        issues.append('qson file missing')
    else:
        try:
            qson = load_json_strict(qson_path)
        except Exception as e:
            issues.append(f'ERR_LOADING_QSON: {e}')
            qson = {}
        if 'schema_version' not in qson:
            issues.append('qson missing schema_version')
        if 'run_trace_id' not in qson:
            issues.append('qson missing run_trace_id')
        else:
            if 'run_trace_id' in mg8 and qson.get('run_trace_id') != mg8.get('run_trace_id'):
                issues.append('run_trace_id mismatch between mg8 and qson')
        if qson.get('context_ref') != gst.get('context_id'):
            issues.append('qson.context_ref does not match gst.context_id')
        if 'responses' not in qson:
            issues.append('qson missing responses')
        events = qson.get('events', [])
        if not isinstance(events, list) or len(events) == 0:
            issues.append('qson.events must be a non-empty array')
        else:
            seen_trace_ids = set()
            existing_gate_ids = set()
            for g in mg8.get('g8son_gates', []):
                gp = BASE / g
                if gp.exists():
                    try:
                        existing_gate_ids.add(load_json_strict(gp).get('gate_id'))
                    except Exception:
                        pass
            for i, ev in enumerate(events):
                for key in ('trace_id','parent_trace_id','run_trace_id','decision','status','confidence_at_decision','ambiguity','rule_triggered','timestamp'):
                    if key not in ev:
                        issues.append(f'qson.events[{i}] missing field: {key}')
                if 'rule_triggered' in ev and not isinstance(ev['rule_triggered'], list):
                    issues.append(f'qson.events[{i}].rule_triggered must be an array')
                tid = ev.get('trace_id')
                if tid in seen_trace_ids:
                    issues.append(f'qson.events[{i}] trace_id reused: {tid}')
                else:
                    seen_trace_ids.add(tid)
                if 'run_trace_id' in ev and ev.get('trace_id') == ev.get('run_trace_id'):
                    issues.append(f'qson.events[{i}] trace_id equals run_trace_id (invalid): {tid}')
                if i == 0 and ev.get('parent_trace_id') != mg8.get('run_trace_id'):
                    issues.append(f'qson.events[0].parent_trace_id must equal mg8.run_trace_id')
                sp = ev.get('source_paths', {})
                for key in ('mg8','gst','g8son'):
                    val = sp.get(key)
                    if not val:
                        issues.append(f'qson.events[{i}].source_paths.{key} missing')
                    else:
                        if not is_relative_path(val):
                            issues.append(f'qson.events[{i}].source_paths.{key} is not relative: {val}')
                gid = ev.get('source_objects', {}).get('gate_id')
                if gid and gid not in existing_gate_ids:
                    issues.append(f'qson.events[{i}].source_objects.gate_id "{gid}" not found in g8son definitions')

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
