"""Exact scalar inequalities and frozen small-file identities only."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

out = Path(__file__).resolve().parent
root = next(p for p in out.parents if (p / 'research/sessions/20261017-2109').is_dir())
freeze = json.loads((out / 'source-freeze.json').read_text('utf-8'))
for item in freeze['sources']:
    b = (root / item['path']).read_bytes()
    assert len(b) == item['bytes']
    assert hashlib.sha256(b).hexdigest() == item['sha256']
adoption = json.loads((root / 'research/sessions/20261017-2109/R011-nonlinear-certificate-adoption.json').read_text('utf-8'))
for rel, sha in adoption['checked_sources'].items():
    # Never open the NPZ, helper, or other unfrozen files.
    matched = [i for i in freeze['sources'] if i['path'] == rel]
    if matched:
        assert matched[0]['sha256'] == sha
summary_path = next(i['path'] for i in freeze['sources'] if i['path'].endswith('/summary_r015.json'))
summary = json.loads((root / summary_path).read_text('utf-8'))
bounds = summary['candidate_bounds']
F = Q.from_float
Eupper = F(bounds['terminal_E_interval_candidate'][1])
sqrt_upper = F(bounds['tail_sqrt_interval_candidate'][1])
I_H = F(bounds['I_total_6T_upper_candidate'])
assert sqrt_upper * sqrt_upper >= 2 * Eupper
assert sqrt_upper + I_H < Q('1.098')
assert Q(adoption['safe_decimal_statements']['A_fulltime_peak_upper']) == Q('1.325')
assert Q(adoption['safe_decimal_statements']['B_at_T_lower']) == Q('8.809')
for name, hex_value in adoption['bound_binary64_hex'].items():
    assert F(float.fromhex(hex_value)) == F(bounds[name])
assert F(bounds['early_upper_candidate']) < Q('1.325')
assert F(bounds['tail_upper_candidate']) < Q('1.325')
assert F(bounds['fixed_T_lower_candidate']) > Q('8.809')

mu = Q(1, 10**6)
pi_upper, sqrt2_upper = Q(22, 7), Q(99, 70)
assert sqrt2_upper**2 > 2
# pi<22/7 is the standard exact analytic bound used in the proof.
q = Q('1.000001')
assert q*q*(1-mu) > 1
assert q*q > 1+mu
r_H = 40 * sqrt2_upper * mu * 120 * pi_upper
r_T = 40 * sqrt2_upper * mu * 20 * pi_upper
assert r_H < Q('.02134') and r_T < Q('.003556')
early = Q('1.325') + q * Q('.02134')
tail = q * (q * Q('1.098') + Q('.02134'))
lower = Q('8.809') - q * Q('.003556')
gap = lower - max(early, tail)
assert tail < early < Q('1.35')
assert lower > Q('8.80') and gap > Q('7.45')

def exact(x):
    return str(x)

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'source_sha_unchanged': True, 'adoption_matching_frozen_source_identities': True,
          'sqrt_upper_squared_covers_twice_complete_Eupper': True,
          'nominal_complete_state_radius_upper_exact': exact(sqrt_upper+I_H),
          'nominal_state_radius_below_1_098': True,
          'rho_H_rational_upper': exact(r_H), 'rho_T_rational_upper': exact(r_T),
          'uniform_early_upper': exact(early), 'uniform_tail_upper': exact(tail),
          'uniform_fixed_T_lower': exact(lower), 'uniform_gap_lower': exact(gap),
          'strict_thresholds': {'A_fullpeak_lt_1_35': True,
                                'B_fixed_T_gt_8_80': True, 'gap_gt_7_45': True},
          'not_executed': ['ODE', 'parameter sweep', 'solver', 'helper import',
                           'NPZ/array read', 'external search'],
          'inherited_scope': 'Root C025 adoption and its original mathematical, parameter, machine, helper, decoding and runtime assumptions remain conditional.'}
(out / 'checks.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result, ensure_ascii=False))
