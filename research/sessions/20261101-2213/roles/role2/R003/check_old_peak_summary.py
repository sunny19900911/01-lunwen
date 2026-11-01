"""Reproduce the small-table comparison without rewriting its frozen output."""
from pathlib import Path
import csv, json

O = Path(__file__).resolve().parent
P = O.parents[5] / 'research/sessions/20261101-2213/roles/role4/R002'


def read(name):
    with (P / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


old = read('old-peak-first-order-baseline-comparison-48.csv')
whole = [d for d in read('frozen-prediction-vs-exact-reference-96.csv') if d['Taylor_order'] == '1']
counts = {'whole_window_error_smaller': 0, 'equal_within_1e-12': 0, 'whole_window_error_larger': 0}
by_target = []
for z in [.06, .07, .08, .10]:
    a = [d for d in old if float(d['target_zeta']) == z]
    b = [d for d in whole if float(d['target_zeta']) == z]
    for d in a:
        e = next(v for v in b if v['Story'] == d['Story'])
        difference = abs(float(e['peak_relative_error'])) - abs(float(d['peak_relative_error']))
        counts['whole_window_error_smaller' if difference < -1e-12 else
               ('whole_window_error_larger' if difference > 1e-12 else 'equal_within_1e-12')] += 1
    by_target.append({'target_zeta': z,
        'old_peak_max_abs_relative_error': max(abs(float(d['peak_relative_error'])) for d in a),
        'whole_window_max_abs_relative_error': max(abs(float(d['peak_relative_error'])) for d in b),
        'old_peak_insufficient_misses': sum(d['miss_insufficient'] == 'True' for d in a),
        'whole_window_insufficient_misses': sum(d['point_miss_insufficient'] == 'True' for d in b)})
assert {'counts': counts, 'by_target': by_target} == json.loads((O / 'old-peak-baseline-comparison-summary.json').read_text())
print('Old-peak comparison summary: pass; no outputs rewritten')
