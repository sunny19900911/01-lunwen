"""Root conditional-math, export-list and frozen-byte checks; no source execution."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime
import csv
import hashlib
import json

S = Path(__file__).resolve().parent
R = S.parents[2]
B = R / 'papers/damping-output-boundaries/research/roles'
FOLDERS = [
    'ideation/maxwell-session004/R024-force-feedback-closure',
    'verification/maxwell-session004/R033-force-feedback-closure-review',
    'ideation/maxwell-session004/R025-asymmetric-neighborhood',
    'verification/maxwell-session004/R034-asymmetric-neighborhood-review',
    'novelty/maxwell-session004/R018-asymmetry-contribution',
    'experiments/maxwell-session004/R021-RH4X-export-filter-list',
    'literature/maxwell-session004/R021-RH4X-export-list-review',
]


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(obj, parent, checked):
    if isinstance(obj, list):
        for value in obj:
            verify(value, parent, checked)
    elif isinstance(obj, dict):
        if 'sha256' in obj and any(key in obj for key in ['path', 'file', 'name']):
            name = obj.get('path', obj.get('file', obj.get('name')))
            p = Path(name)
            if not p.is_absolute():
                p = (R if name.startswith(('papers/', 'research/')) else parent) / p
            if p.is_relative_to(R) and p.suffix.lower() not in {'.npz', '.npy', '.xlsx', '.pdf', '.png'}:
                assert sha(p) == obj['sha256'], p
                if 'bytes' in obj:
                    assert p.stat().st_size == obj['bytes']
                checked[p.relative_to(R).as_posix()] = sha(p)
        for value in obj.values():
            verify(value, parent, checked)


def main():
    checked = {}
    for name in FOLDERS:
        directory = B / name
        for p in directory.iterdir():
            if p.is_file() and p.suffix == '.json':
                verify(read(p), directory, checked)
    adopted = read(S / 'R011-nonlinear-certificate-adoption.json')
    bounds = adopted['bound_values_as_binary64']
    r = F(bounds['tail_sqrt_interval_candidate'][1])
    e = F(bounds['terminal_E_interval_candidate'][1])
    radius = r + F(bounds['I_total_6T_upper_candidate'])
    assert r * r > 2 * e and radius < F('1.098')
    q = F('1.000001')
    mu = F(1, 10**6)
    assert q*q*(1-mu) > 1 and q*q > 1+mu
    early = F('1.325') + q*F('.02134')
    tail = q*(q*F('1.098') + F('.02134'))
    lower = F('8.809') - q*F('.003556')
    assert tail < early < F('1.35') and lower > F('8.80')
    assert lower-early == F('7.459103975104') > F('7.45')
    directory = B / 'experiments/maxwell-session004/R021-RH4X-export-filter-list'
    with (directory / 'RH4X-88-device-coverage.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 88 and len({(row['assignment_Name'],row['Story']) for row in rows}) == 88
    counts = {key: sum(row[key] == 'yes' for row in rows) for key in ['complete_P_I','complete_P_J','complete_U1']}
    assert list(counts.values()) == [33,33,65]
    for route, column, number in [('P','complete_internal_P_I_and_J',55),('U1','complete_U1',23)]:
        wanted = {row['assignment_Name'] for row in rows if row[column] != 'yes'}
        with (directory / f'RH4X-supplement-{route}-filter.csv').open(encoding='utf-8-sig', newline='') as f:
            actual = list(csv.DictReader(f))
        txt = (directory / f'RH4X-supplement-{route}-IDs.txt').read_text(encoding='utf-8').splitlines()
        assert len(actual) == len(txt) == len(wanted) == number
        assert {row['assignment_Name'] for row in actual} == set(txt) == wanted
    assert all(row['raw_Unique_Name_per_device'] == row['raw_Link_Element_per_device'] == 'unknown_not_retained' for row in rows)
    assert sha(R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md') == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    result = {
        'at': datetime.now().astimezone().isoformat(), 'checks_passed': True,
        'root_content_review': ['R024/R033 full conditional feedback-equivalence reports and regularity/IC scope',
                                'R025/R034 full fixed-asymmetry proof/review and Fraction code; original state bound provenance',
                                'R018 contribution boundary; not an extension of equal-energy histories',
                                'Export-builder entire code, two full reports and root small-CSV subset/count checks'],
        'checked_small_file_identities': checked,
        'root_exact_checks': {'complete_H_radius_below_1_098':str(radius),'sqrt_square_covers_terminal_E':True,
                              'A_early_upper':str(early),'A_tail_upper':str(tail),'B_T_lower':str(lower),
                              'uniform_gap_lower':str(lower-early)},
        'RH4X_single_stream_counts':counts, 'supplement_P':55, 'supplement_U1_if_Keff':23,
        'raw_result_key_mapping_remains_unknown':True,
        'scope': 'Conditional classical feedback equivalence; conditional fixed one-direction asymmetry family; frozen export-grid lists only. No true engineering prediction, parameter tolerance or new theory.',
        'excluded':['compact manuscript awaiting independent reviews','R026 BE step proof candidate','input-only BE prototype candidate','new BE primary-source search'],
        'source_scripts_executed':False, 'raw_engineering_or_synthetic_arrays_read':False,
    }
    (S / 'R016-root-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'passed':True,'identities':len(checked),'uniform_gap':str(lower-early),'export_P':55,'export_U1':23}))


if __name__ == '__main__':
    main()
