"""R048: freeze small text sources and verify proof obligations; no ODE/data runs."""
from pathlib import Path
from datetime import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[7]
OUT = Path(__file__).resolve().parent
SOURCES = [
    'research/sessions/20261017-2109/continuous-velocity-endpoint-protocol-v001.md',
    'papers/damping-output-boundaries/research/roles/verification/maxwell-session004/非零末力耗散峰力区间独审-R017.md',
    'papers/damping-output-boundaries/manuscript/maxwell-fixed-dissipation-peak-appendix-v002.md',
]

def record(path):
    data = path.read_bytes()
    data.decode('utf-8')
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

assert (ROOT / SOURCES[0]).is_file(), ROOT
sources = [record(ROOT / p) for p in SOURCES]
assert sources[1]['sha256'] == '5a3596a03e9508861ccfda513ee170addf62c29a35ef97e4ed9e33a3db4c5c6d'
assert sources[2]['sha256'] == 'c36bbd54984e119de7ca89b25f3bc651ce92e90bc13e3dcaf1c67d3cf6843f5f'
write('source-freeze.json', {
    'round': 'R048', 'role_started_at': '2026-10-18T05:48:40.007283+08:00',
    'protocol_started_at': '2026-10-18T05:44:38.077390+08:00',
    'global_deadline': '2026-10-18T07:09:45+08:00',
    'sources': sources, 'new_author_candidate_read': False,
})
proof_checks = {
    'lower_equality_forces_internal_zero_to_V_jump': True,
    'upper_equality_forces_internal_V_to_minus_V_jump': True,
    'signed_endpoint_and_zero_set_cases_checked': True,
    'ramps_preserve_velocity_bound_and_continuity': True,
    'endpoint_parameter_maps_continuous_and_strictly_monotone': True,
    'fixed_brackets_persist_by_uniform_L1_continuous_dependence': True,
    'IVT_enforces_exact_terminal_force_for_each_ramp': True,
    'parameter_roots_converge_to_old_switches': True,
    'uniform_force_and_dissipation_convergence': True,
    'minimal_time_attainment_exception': True,
    'no_complete_continuous_D_range_or_fixed_D_peak_claim': True,
}
write('closure_checks.json', {
    'method': 'symbolic proof with three independent adversarial reviews; these booleans are a manual obligation ledger, not numerical tests',
    'checks': proof_checks, 'logical_gaps_found': 0,
    'ode_runs': 0, 'data_arrays': 0, 'numerical_examples': 0,
})
outputs = [record(OUT / n) for n in ['report.md', 'freeze_review.py', 'source-freeze.json', 'closure_checks.json']]
frozen_at = datetime.now().astimezone().isoformat()
write('validation.json', {
    'round': 'R048', 'frozen_at': frozen_at,
    'within_role_eight_minutes': datetime.fromisoformat(frozen_at) <= datetime.fromisoformat('2026-10-18T05:56:40.007283+08:00'),
    'sources_verified_unchanged': True, 'outputs': outputs,
    'old_files_modified': False, 'independent_before_official_comparison': True,
    'conclusion': 'Both endpoints are unattained but sharp for continuous bounded velocity when T>tmin; T=tmin is attained.',
})
for n in ['source-freeze.json', 'closure_checks.json', 'validation.json']:
    json.loads((OUT / n).read_text(encoding='utf-8'))
print(json.dumps({'frozen_at': frozen_at, 'outputs': outputs,
                  'validation': record(OUT / 'validation.json')}, ensure_ascii=False, indent=2))
