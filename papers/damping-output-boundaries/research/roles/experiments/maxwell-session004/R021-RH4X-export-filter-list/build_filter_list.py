"""Build RH4X export filters from frozen coverage metadata; never reads arrays/workbooks."""
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent
ROOT = HERE.parents[6]
W5 = ROOT.parent / 'W5-重燃双塔连体'
START = datetime.fromisoformat('2026-10-18T03:11:48+08:00')
SOURCES = {
    'coverage': OLD / 'link_case_coverage_r001.csv',
    'audit': OLD / 'pairing_audit_r001.json',
    'original_audit_code': OLD / 'audit_link_pairing_r001.py',
    'original_report': OLD / 'R001-P-U1覆盖与配对输入.md',
    'small_tables': W5 / 'research/maxwell-20261017/roles/experiments/metadata/controlled_small_tables.json',
    'headers': W5 / '02-数据/maxwell_headers_20261017.json',
    'seven_table_manifest': W5 / 'research/maxwell-20261017/experiments/R001/core-cache/manifest.json',
}
EXPECTED_SHA = {
    'coverage': 'b2e41e8c4ee8f6654efe98b582a1e7c39f3f89f0a4a66a4c7277621008ba6fe8',
    'audit': 'a35bb7003983c1fd412fa804fe42a5cf08637e92300ba87766ad814d9d5f95fd',
    'original_audit_code': '5e9b4e3bec6a62a6244dd4153e3075a8256ba032bad4a029b1bbfc9db185feb9',
    'small_tables': 'd8175ddc436ec7edfea1c0c168679f8d3327d9096a0afc7fc7128f3e5045a5fc',
    'headers': 'd42ec83cfabbbe8cdf299476d169c634f72a94532bd4acea72b700d0d1b6c886',
    'seven_table_manifest': '03cae034bd5409c6dc6bed06727a58fd85391a6f583a2b38776cf03bf45f26f4',
}

def load_bytes(path):
    path = Path(path)
    assert path.suffix.lower() in {'.json', '.csv', '.md', '.py', '.txt'}
    assert path.stat().st_size < 1_000_000
    return path.read_bytes()

def sha(path):
    data = load_bytes(path)
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def js(path):
    return json.loads(load_bytes(path).decode('utf-8-sig'))

def save_json(name, value):
    path = HERE / name
    assert not path.exists(), 'Frozen output exists'
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def save_csv(name, rows):
    path = HERE / name
    assert not path.exists(), 'Frozen output exists'
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

before = {key: sha(path) for key, path in SOURCES.items()}
for key, expected in EXPECTED_SHA.items():
    assert before[key]['sha256'] == expected, key
audit = js(SOURCES['audit'])
small = js(SOURCES['small_tables'])
assert all('Program Control' not in key for key in small)
assign = small['Link Assigns - Summary']
assert assign[1][1] == ['Name', 'Story', 'Link Property']
devices = {str(values[0]): {'Story': str(values[1]), 'Property': str(values[2]), 'source_row': n} for n, values in assign if n >= 4}
assert len(devices) == 88 and {v['Property'] for v in devices.values()} == {'Link1'}
headers = js(SOURCES['headers'])
force_headers = headers['Element Forces - Links'][1][1]
u_headers = headers['Element Deformations - Links'][1][1]
assert force_headers[:9] == ['Story', 'Unique Name', 'Link Element', 'Output Case', 'Case Type', 'Step Type', 'Step Number', 'Location', 'P']
assert u_headers[:8] == ['Story', 'Unique Name', 'Link Element', 'Output Case', 'Case Type', 'Step Type', 'Step Number', 'U1']
manifest = js(SOURCES['seven_table_manifest'])
rh4x = [g for g in manifest['tables']['Base Reactions']['groups'].values() if g['keys']['Output Case'] == 'RH4X']
assert len(rh4x) == 1
assert (rh4x[0]['n'], rh4x[0]['n_unique'], rh4x[0]['t0'], rh4x[0]['t1']) == (2501, 2501, 0.0, 50.0)
assert audit['unknown_keys_or_locations'] == []
assert audit['metadata_sha256'] == before['small_tables']['sha256']
assert audit['core_manifest_sha256'] == before['seven_table_manifest']['sha256']
assert audit['source_sha256'] == manifest['sha256']
with SOURCES['coverage'].open(encoding='utf-8-sig', newline='') as f:
    all_rows = list(csv.DictReader(f))
rows = [(number, row) for number, row in enumerate(all_rows, 2) if row['Case'] == 'RH4X']
assert len(rows) == 88 and {r['Link'] for _, r in rows} == set(devices)
assert len({r['Link'] for _, r in rows}) == 88

def complete(row, stream):
    ncol = {'I': 'P_I_n', 'J': 'P_J_n', 'U': 'U1_n'}[stream]
    missing = {'I': 'missing_I', 'J': 'missing_J', 'U': 'missing_U'}[stream]
    extra = {'I': 'extra_I', 'J': 'extra_J', 'U': 'extra_U'}[stream]
    dup = {'I': 'dup_I', 'J': 'dup_J', 'U': 'dup_U'}[stream]
    required = [ncol, missing, extra, dup, 'invalid_rows']
    if any(row.get(k, '') == '' for k in required):
        return 'unknown'
    return 'yes' if int(row[ncol]) == 2501 and all(int(row[k]) == 0 for k in [missing, extra, dup, 'invalid_rows']) else 'no'

def reason(row, streams):
    status = [complete(row, s) for s in streams]
    if 'unknown' in status:
        return 'unknown: per-stream evidence missing; do not infer from paired completeness'
    if all(s == 'yes' for s in status):
        return 'complete on existing export grid only; physical tail and port identity not certified'
    ncols = {'I': 'P_I_n', 'J': 'P_J_n', 'U': 'U1_n'}
    if all(int(row[ncols[s]]) == 0 for s in streams):
        return 'no rows in frozen export for this device/case/stream; source tables hit Excel row limit; exact exclusion mechanism unproven'
    return 'partial/duplicate/extra/invalid stream; inspect source coverage counts; never fill gaps with zero'

result = []
for csv_row, row in rows:
    device = devices[row['Link']]
    assert row['Story'] == device['Story']
    assert (row['CaseType'], row['StepType'], int(row['expected_n']), float(row['expected_t0_s']), float(row['expected_t1_s'])) == ('NonModHist', 'Step By Step', 2501, 0.0, 50.0)
    p_i, p_j, u = [complete(row, s) for s in ['I', 'J', 'U']]
    p = 'unknown' if 'unknown' in [p_i, p_j] else ('yes' if p_i == p_j == 'yes' else 'no')
    item = {
        'assignment_Name': row['Link'], 'Story': row['Story'], 'Link_Property': device['Property'],
        'coverage_canonical_Link': row['Link'], 'Case': 'RH4X', 'CaseType': row['CaseType'], 'StepType': row['StepType'],
        'window_t0_s': 0, 'window_t1_s': 50, 'expected_points': 2501,
        'complete_internal_P_I_and_J': p, 'complete_P_I': p_i, 'complete_P_J': p_j, 'complete_U1': u,
        'P_I_points': row['P_I_n'], 'P_J_points': row['P_J_n'], 'U1_points': row['U1_n'],
        'missing_I': row['missing_I'], 'missing_J': row['missing_J'], 'missing_U1': row['missing_U'],
        'extra_I': row['extra_I'], 'extra_J': row['extra_J'], 'extra_U1': row['extra_U'],
        'duplicate_I': row['dup_I'], 'duplicate_J': row['dup_J'], 'duplicate_U1': row['dup_U'], 'invalid_rows_all_streams': row['invalid_rows'],
        'P_I_source_row_range': row['P_I_source_rows'], 'P_J_source_row_range': row['P_J_source_rows'], 'U1_source_row_range': row['U_source_rows'],
        'P_gap_reason': reason(row, ['I', 'J']), 'U1_gap_reason': reason(row, ['U']),
        'coverage_source': str(SOURCES['coverage']), 'coverage_csv_row': csv_row,
        'assignment_source': str(SOURCES['small_tables']), 'assignment_table': 'Link Assigns - Summary', 'assignment_original_row': device['source_row'],
        'raw_Unique_Name_per_device': 'unknown_not_retained', 'raw_Link_Element_per_device': 'unknown_not_retained',
        'key_mapping_evidence': 'R001: canonical Link=Unique Name if in assigned Name set, else Link Element; per-record raw key pair not retained in coverage CSV; no claim all raw key columns equal',
    }
    result.append(item)

save_csv('RH4X-88-device-coverage.csv', result)
p_need = [r for r in result if r['complete_internal_P_I_and_J'] != 'yes']
u_need = [r for r in result if r['complete_U1'] != 'yes']
batches = []
for stream, needed, table, locations, mult in [
    ('P', p_need, 'Element Forces - Links', 'I-End and J-End kept separately', 2),
    ('U1', u_need, 'Element Deformations - Links', 'not applicable', 1),
]:
    filters = []
    for row in needed:
        filters.append({
            'assignment_Name': row['assignment_Name'], 'Story': row['Story'], 'batch_id': stream + '-' + row['Story'],
            'table': table, 'Case': 'RH4X', 'CaseType': 'NonModHist', 'StepType': 'Step By Step',
            't0_s': 0, 't1_s': 50, 'expected_points_per_stream': 2501, 'locations': locations,
            'reason': row['P_gap_reason' if stream == 'P' else 'U1_gap_reason'],
            'identity_scope': 'assigned Name and Story; raw Unique Name/Link Element must be checked in filtered preview',
            'coverage_source_csv_row': row['coverage_csv_row'],
        })
    save_csv('RH4X-supplement-' + stream + '-filter.csv', filters)
    txt = HERE / ('RH4X-supplement-' + stream + '-IDs.txt')
    assert not txt.exists()
    txt.write_text('\n'.join(r['assignment_Name'] for r in needed) + '\n', encoding='utf-8')
    for story, count in sorted(Counter(r['Story'] for r in needed).items(), key=lambda x: int(x[0][5:]), reverse=True):
        ids = [r['assignment_Name'] for r in needed if r['Story'] == story]
        batches.append({'batch_id': stream + '-' + story, 'table': table, 'Story': story, 'Case': 'RH4X', 'device_count': count,
                        'expected_data_rows_if_one_element_per_device': count * 2501 * mult,
                        'assignment_Name_filter': '|'.join(ids), 'note': 'row estimate conditional on preview key multiplicity; compare actual filtered count before export'})
save_csv('RH4X-batch-plan.csv', batches)
assert (sum(r['complete_P_I'] == 'yes' for r in result), sum(r['complete_P_J'] == 'yes' for r in result), sum(r['complete_U1'] == 'yes' for r in result)) == (33, 33, 65)
assert (len(p_need), len(u_need)) == (55, 23)
assert all(r['complete_internal_P_I_and_J'] != 'unknown' and r['complete_U1'] != 'unknown' for r in result)
assert all(int(r['invalid_rows_all_streams']) == 0 for r in result)
assert max(r['expected_data_rows_if_one_element_per_device'] for r in batches) <= 40016
after = {key: sha(path) for key, path in SOURCES.items()}
assert before == after
now = datetime.now(timezone(timedelta(hours=8)))
elapsed = (now - START).total_seconds()
assert elapsed <= 480
save_json('source_manifest.json', {'files': before, 'original_workbook_sha_inherited_only': audit['source_sha256'], 'original_workbook_not_accessed': True, 'unchanged_after': True})
save_json('validation.json', {
    'task': 'R021-RH4X-export-filter-list', 'started_at': START.isoformat(), 'frozen_at': now.isoformat(), 'elapsed_seconds': elapsed,
    'assigned_devices': 88, 'RH4X_coverage_rows': 88, 'name_set_equal': True, 'Story_equal': True,
    'P_I_complete': 33, 'P_J_complete': 33, 'internal_P_both_ends_complete': 33, 'U1_complete': 65,
    'supplement_P_devices': 55, 'supplement_U1_devices_if_Keff_residual': 23, 'per_stream_unknown_status': 0,
    'P_missing_rows_per_end': 137555, 'U1_missing_rows': 57523,
    'batches': len(batches), 'largest_conditional_batch_rows': 40016,
    'single_flow_fields_present_and_used': True, 'paired_33_not_used_as_single_flow_inference': True,
    'canonical_key_rule': 'Unique Name if assigned, else Link Element; inherited from frozen R001 audit code',
    'raw_key_equality_per_device_certified': False, 'raw_key_unknown_is_not_coverage_unknown': True,
    'P_units': 'kN', 'U1_units': 'mm', 'U1_to_m_scale': 0.001,
    'source_files_unchanged': True, 'NPZ_NPY_workbook_or_arrays_accessed': False, 'solver_used': False,
    'Program_Control_values_accessed': False, 'engineering_certified': False,
})
outputs = [p for p in HERE.iterdir() if p.is_file() and p.name != 'delivery_manifest.json']
save_json('delivery_manifest.json', {'task': 'R021-RH4X-export-filter-list', 'frozen_at': now.isoformat(), 'files': [sha(p) for p in sorted(outputs)]})
print(json.dumps({'P_supplement': len(p_need), 'U1_supplement': len(u_need), 'elapsed_seconds': elapsed, 'batches': len(batches), 'max_batch_rows': 40016}, ensure_ascii=True))
