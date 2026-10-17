"""R020: frozen small-file audit only. Never opens workbook/NPZ/NPY files."""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLES = HERE.parents[2]
LIT = ROLES / 'literature/maxwell-session004/R019-actual-field-gap-map'
START = datetime.fromisoformat('2026-10-18T03:02:41+08:00')

def read_bytes(path):
    p = Path(path)
    assert p.suffix.lower() in {'.json', '.md', '.py'}
    assert p.stat().st_size < 1_000_000
    return p.read_bytes()

def read_json(path):
    return json.loads(read_bytes(path).decode('utf-8-sig'))

def fingerprint(path):
    p = Path(path)
    data = read_bytes(p)
    return {'path': str(p), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

rules = read_json(LIT / 'input-rules-R019.json')
freeze = read_json(LIT / 'frozen-R019.json')
gap = read_json(LIT / 'field-gap-map-R019.json')
inputs = list(rules['inputs'])
extra = rules.get('additional_small_report_inputs', [])
if isinstance(extra, list):
    inputs.extend(x for x in extra if isinstance(x, dict) and 'path' in x)
expected = inputs + freeze['files']
before = []
for item in expected:
    observed = fingerprint(item['path'])
    assert observed['sha256'] == item['sha256'], item['path']
    if 'bytes' in item:
        assert observed['bytes'] == item['bytes'], item['path']
    before.append(observed)
before.append(fingerprint(LIT / 'frozen-R019.json'))

small_path = next(x['path'] for x in inputs if Path(x['path']).name == 'controlled_small_tables.json')
small = read_json(small_path)
assert all('Program Control' not in key for key in small)
assign = small['Link Assigns - Summary'][3:]
prop = small['Link Prop Def - Summary'][3:]
exp = small['Link Prop Def - Damper - Exp'][3:]
modal = small['Modal Periods And Frequencies'][3:]
assert len(assign) == 88 and {r[1][2] for r in assign} == {'Link1'}
assert len(prop) == 1 and prop[0][1][:3] == ['Link1', 'Damper - Exponential', 'U1']
assert len(exp) == 0
assert len(modal) == 300 and {r[1][0] for r in modal} == {'Modal'}
assert sorted(r[1][1] for r in modal) == list(range(1, 301))

cache_path = next(x['path'] for x in inputs if Path(x['path']).name == 'manifest.json')
cache = read_json(cache_path)
seven = ['Total Energy Components', 'Element NL Energy By Group', 'Base Reactions', 'Story Forces', 'Diaphragm CM Displacements', 'Story Accelerations', 'Story Drifts']
assert set(cache['tables']) == set(seven)
schema = gap['R022_schema_coverage']
minimum = read_bytes(ROLES / 'ideation/maxwell-session004/R022-force-target-interface/minimum-fields.json').decode('utf-8-sig')
ids = {x['id'] for x in gap['field_map']}
assert len(ids) == 25
assert gap['schema_field_count'] == sum(map(len, schema.values())) == 38
assert {k: len(v) for k, v in schema.items()} == {'reference_manifest': 9, 'mode_rows': 6, 'target_rows': 4, 'port_rows': 6, 'force_rows': 8, 'remainder_manifest': 5}
for group in schema.values():
    for field, refs in group.items():
        assert field in minimum and refs and set(refs) <= ids

after = [fingerprint(x['path']) for x in before]
assert before == after
now = datetime.now(timezone(timedelta(hours=8)))
elapsed = (now - START).total_seconds()
assert elapsed <= 480
result = {
    'task': 'R020-field-gap-crosscheck', 'started_at': START.isoformat(),
    'frozen_at': now.isoformat(), 'elapsed_seconds': elapsed,
    'must_fix_count': 0, 'scope': 'definition and delivery QA; not actual engineering certification',
    'source_fingerprints_match_and_unchanged': True,
    'role3_freeze_entries_verified': len(freeze['files']),
    'assignments': {'count': 88, 'property_summary': 'Link1 / Damper - Exponential / U1', 'summary_only': True},
    'exponential_definition_data_rows': 0,
    'current_controlled_modal_result_rows': 300,
    'modal_case': 'Modal', 'mode_range': [1, 300],
    'Eigen_Ritz_normalization_actual_C_certified': False,
    'seven_cache_table_names_verified': seven,
    'schema_fields': 38, 'schema_field_counts': {k: len(v) for k,v in schema.items()},
    'field_map_rows': 25, 'schema_references_resolve': True,
    'coverage_basis': 'Frozen R001 report only: common six-case 32; RH4X 33 complete pairs; no time-series recount',
    'initial_link_QA_preserved_with_later_delivery_addendum': True,
    'raw_workbook_accessed': False, 'NPZ_or_NPY_opened_or_hashed': False,
    'Program_Control_values_accessed': False, 'source_manifest_cache_paths_followed': False,
    'full_time_series_coverage_recounted': False,
    'technical_crosscheck': 'R019 report, R022 report/schema, R030 review, original R003 port definitions, frozen R001 coverage report'
}
save('source_manifest.json', {'files': before, 'all_hashes_recomputed_on_small_files_only': True})
save('audit_results.json', result)
save('delivery_manifest.json', {'task': result['task'], 'frozen_at': now.isoformat(), 'files': [fingerprint(HERE / name) for name in ['report.md', 'audit_small_metadata.py', 'audit_results.json', 'source_manifest.json']]})
print(json.dumps({'must_fix_count': 0, 'elapsed_seconds': elapsed, 'source_files': len(before), 'schema_fields': 38, 'output': str(HERE)}, ensure_ascii=True))
