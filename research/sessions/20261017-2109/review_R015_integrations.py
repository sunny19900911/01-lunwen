"""R015 completed package identity review. Numerical run is separately frozen."""
from pathlib import Path
from datetime import datetime
import hashlib
import importlib.util
import json
import re

S = Path(__file__).resolve().parent
R = S.parents[2]
B = R / 'papers/damping-output-boundaries/research/roles'
FOLDERS = [
    'experiments/maxwell-session004/R019-force-output-replay-prototype',
    'verification/maxwell-session004/R031-force-replay-review',
    'ideation/maxwell-session004/R023-target-peak-decision',
    'verification/maxwell-session004/R032-target-peak-decision-review',
    'literature/maxwell-session004/R019-actual-field-gap-map',
    'experiments/maxwell-session004/R020-field-gap-crosscheck',
    'novelty/maxwell-session004/R016-mechanism-contribution-boundary',
    'writing/maxwell-session004/force-response-interface-v001',
    'novelty/maxwell-session004/R017-force-interface-integration',
    'literature/maxwell-session004/R020-force-replay-FFT-review',
]


def main():
    spec = importlib.util.spec_from_file_location('review014', S / 'review_R014_integrations.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    checked = {}
    for folder in FOLDERS:
        directory = B / folder
        for p in directory.iterdir():
            if p.is_file() and p.suffix == '.json':
                common.verify_records(json.loads(p.read_text(encoding='utf-8')), directory, checked)
    d = S / 'R014-force-replay-FFT'
    common.verify_records(common.read(d / 'freeze.json'), d, checked)
    force_result = common.read(d / 'summary.json')
    assert force_result['nodes_compared'] == 98305 and force_result['agreement_gate_passed']
    assert len(force_result['agreement_differences']) == 12
    assert max(force_result['agreement_differences'].values()) < 1e-8
    assert all(x['max_error_below_point01'] for x in force_result['metrics_against_original_D_cache'].values())
    manuscript = R / 'papers/damping-output-boundaries/manuscript/maxwell-force-response-interface-v001.md'
    text = manuscript.read_text(encoding='utf-8')
    assert len(re.findall(r'\$\$.*?\$\$', text, re.S)) == 3
    assert common.sha(manuscript) == '32edbfb408e264c28b49e2cf07f31d622239972b085b9eb1c63fdfb3b22c2c68'
    for p in [B / 'writing/maxwell-session004/frozen-draft-v010.json',
              B / 'writing/maxwell-session004/layout-input-templates-v001/freeze.json']:
        common.verify_records(common.read(p), p.parent, checked)
    preserved = R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md'
    assert common.sha(preserved) == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    result = {
        'at': datetime.now().astimezone().isoformat(), 'checks_passed': True,
        'root_content_review': [
            'Full R019 replay code plus R031 implementation report; FFT protocol/code actually executed by root',
            'R023 report/checks and R032 full independent proof report; peak-map Lipschitz argument reviewed',
            'R019 actual-field report/full25row table and source-gap semantics plus R020 crosscheck report',
            'Companion entire manuscript, three equations, direct-source freeze plus R017 integration audit',
            'R016 mechanism/contribution boundaries and R020 FFT source/low-dimensional audit',
        ],
        'checked_small_file_identities': checked,
        'numerical_scope': {
            'root_FFT_nodes_against_original_D_cache': 98305,
            'between_algorithms_comparison': '4 whole-window max/RMS statistics and 8 values at four fixed points; not pointwise comparison of both complete prediction trajectories',
            'maximum_statistic_or_point_difference': max(force_result['agreement_differences'].values()),
            'source_cache': 'Frozen synthetic NPZ actually read and SHA checked by root replay; no engineering Excel read',
            'independent_role_audit': 'Role3 complete code/small-output and 18 tiny scalar challenges only; no claim it recomputed full arrays',
        },
        'engineering_scope': 'Field existence/meaning and minimal export requirements reviewed; actual C/reference/modal basis/conjugate ports and complete force history remain uncertified',
        'source_QA_addenda': 'R019 field-map self-link file-creation timing and R020 math-text mistaken-link false flags retained; final delivery addenda and freezes resolve them without rewriting originals',
        'classical_peak_rule': 'Supported conditional finite-window sufficient intervals, including common reference error; no unknown remainder assigned zero',
        'companion_integration_accepted': True, 'companion_formulas': 3,
        'excluded': ['R024 feedback closure pending R033', 'R025 asymmetric-neighborhood pending author and independent audit', 'RH4X export filter R021 in progress'],
        'arrays_and_manual_pages_for_publication': False,
    }
    (S / 'R015-root-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed': True, 'small_identities': len(checked), 'between_algorithm_max_stat_or_point_difference': max(force_result['agreement_differences'].values())}))


if __name__ == '__main__':
    main()
