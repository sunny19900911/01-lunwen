"""Independent augmented RK4 plus scalar prediction audit; no producer imports."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np

O = Path(__file__).resolve().parent
R = O.parents[5]
P = R / 'research/sessions/20261101-2213/roles/role4/R001'
BASE = R / 'research/sessions/20261031-1130/roles/role4/R004/local-cache/actual300-SHW3X-z0.05-factorized-reference.npz'
MASS = R / 'research/sessions/20261031-1130/roles/role2/R003/independent-identification-before-comparison-36.csv'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def readcsv(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def writecsv(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def integrate(ag, omega, dt, subdivisions):
    """ODE differentiations, not propagator differentiation or cached-state forcing."""
    om2 = omega ** 2
    x = np.zeros((3, 6))
    states = np.zeros((len(ag), 3, 6))
    h = dt / subdivisions

    def rhs(v, a):
        q = np.empty_like(v)
        q[:, 0::2] = v[:, 1::2]
        q[:, 1] = -om2 * v[:, 0] - .1 * omega * v[:, 1] - a
        q[:, 3] = -om2 * v[:, 2] - .1 * omega * v[:, 3] - 2 * omega * v[:, 1]
        q[:, 5] = -om2 * v[:, 4] - .1 * omega * v[:, 5] - 4 * omega * v[:, 3]
        return q

    for i in range(len(ag) - 1):
        step = ag[i + 1] - ag[i]
        for j in range(subdivisions):
            a0 = ag[i] + step * j / subdivisions
            am = ag[i] + step * (j + .5) / subdivisions
            a1 = ag[i] + step * (j + 1) / subdivisions
            k1 = rhs(x, a0); k2 = rhs(x + h * k1 / 2, am)
            k3 = rhs(x + h * k2 / 2, am); k4 = rhs(x + h * k3, a1)
            x += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        states[i + 1] = x
    return states


def main():
    if (O / 'results.json').exists():
        raise FileExistsError('Frozen audit already exists.')
    manifest = json.loads((P / 'prediction-freeze-manifest.json').read_text(encoding='utf-8'))
    for d in manifest['outputs']:
        p = P / d['name']; assert p.stat().st_size == d['bytes'] and sha(p) == d['sha256']
    assert sha(BASE) == manifest['inputs'][0]['sha256']
    cache = Path(manifest['local_only_prediction_array']['path'])
    assert sha(cache) == manifest['local_only_prediction_array']['sha256']
    with np.load(BASE, allow_pickle=False) as a:
        t, ag, om, s, v, B0, G, px = [a[k].copy() for k in ['t', 'ag', 'omega', 's_unitGamma', 'sdot_unitGamma', 'B_direct', 'Gamma_X', 'phi_X']]
    with np.load(cache, allow_pickle=False) as a:
        Z, ZD, W, WD = [a[k].copy() for k in ['z_unit', 'zdot_unit', 'w_unit', 'wdot_unit']]
        saved = {k: a[k].copy() for k in a.files if k.endswith('_shear_inertia_kN')}
    assert len(t) == 2691 and len(om) == 300 and np.max(abs(np.diff(t) - .02)) < 1e-9
    assert np.all(s[0] == 0) and np.all(v[0] == 0)
    assert all(np.all(a[0] == 0) for a in [Z, ZD, W, WD])
    masses = [d for d in readcsv(MASS) if d['direction'] == 'X']
    masses.sort(key=lambda d: (int(d['Story'][5:]), d['Diaphragm']))
    mx = np.array([float(d['identified_mass_kg']) for d in masses])
    levels = np.array([int(d['Story'][5:]) for d in masses])
    B = np.stack([(mx[levels >= j, None] * px[levels >= j]).sum(axis=0) * G for j in range(1, 13)])
    selected = np.array([1, 9, 12])
    coarse = integrate(ag, om[selected], .02, 8)
    fine = integrate(ag, om[selected], .02, 16)
    truth = np.stack([s[:, selected], v[:, selected], Z[:, selected], ZD[:, selected], W[:, selected], WD[:, selected]], axis=2)
    checks = []
    for i, mode in enumerate(selected + 1):
        for j, label in enumerate(['s', 'sdot', 'z', 'zdot', 'w', 'wdot']):
            nc = float(np.linalg.norm(coarse[:, i, j] - truth[:, i, j]))
            nf = float(np.linalg.norm(fine[:, i, j] - truth[:, i, j]))
            scale = float(np.linalg.norm(truth[:, i, j]))
            checks.append({'Mode': int(mode), 'state': label,
                           'RK8_relative_L2_error': nc / scale, 'RK16_relative_L2_error': nf / scale,
                           'RK8_to_RK16_error_ratio': nc / nf,
                           'RK16_max_absolute_error': float(np.max(abs(fine[:, i, j] - truth[:, i, j])))})
    writecsv('independent-RK4-derivatives-18.csv', checks)
    baseV = (s * om ** 2) @ B.T / 1000
    baseP = np.max(abs(baseV), axis=0); oldidx = np.argmax(abs(baseV), axis=0)
    v3base = (fine[:, :, 0] * om[selected] ** 2) @ B[:, selected].T / 1000
    p3base = np.max(abs(v3base), axis=0)
    peakrows = readcsv(P / 'all300-layer-peak-predictions-96.csv')
    three_rows = {(float(d['target_zeta']), int(d['Taylor_order']), d['Story']): d
                  for d in readcsv(P / 'early-three-mode-target-predictions-96.csv')}
    results = []; selected_results = []; max_curve = 0.
    for target in [.06, .07, .08, .10]:
        delta = target - .05
        for order in [1, 2]:
            pred = s + delta * Z + (delta ** 2 * W / 2 if order == 2 else 0)
            predV = (pred * om ** 2) @ B.T / 1000
            max_curve = max(max_curve, float(np.max(abs(predV - saved[f'z{target:g}_order{order}_shear_inertia_kN']))))
            pp = fine[:, :, 0] + delta * fine[:, :, 2] + (delta ** 2 * fine[:, :, 4] / 2 if order == 2 else 0)
            vp3 = (pp * om[selected] ** 2) @ B[:, selected].T / 1000
            for j in range(12):
                story = f'Story{j + 1}'; ip = int(np.argmax(abs(predV[:, j])))
                d = next(a for a in peakrows if float(a['target_zeta']) == target and int(a['Taylor_order']) == order and a['Story'] == story)
                p = float(abs(predV[ip, j])); decrease = 100 * (1 - p / baseP[j])
                numeric = {'baseline5_peak_kN': baseP[j], 'predicted_peak_kN': p,
                           'predicted_decrease_percent': decrease,
                           'baseline5_peak_time_s': t[oldidx[j]], 'predicted_peak_time_s': t[ip],
                           'prediction_abs_at_baseline_peak_kN': abs(predV[oldidx[j], j])}
                errors = {key: float(abs(value - float(d[key]))) for key, value in numeric.items()}
                assert (p / baseP[j] > .9) == (d['predicted_below10pct_demo'] == 'True')
                assert (p > baseP[j]) == (d['predicted_adverse_peak'] == 'True')
                results.append({'target_zeta': target, 'order': order, 'Story': story, **numeric,
                                'max_saved_scalar_difference': max(errors.values())})
                p3 = float(np.max(abs(vp3[:, j]))); ip3 = int(np.argmax(abs(vp3[:, j])))
                d3 = three_rows[(target, order, story)]
                selected_results.append({'target_zeta': target, 'order': order, 'Story': story,
                    'independent_3mode_peak_kN': p3,
                    'saved_3mode_peak_difference_kN': abs(p3 - float(d3['predicted3mode_peak_kN'])),
                    'saved_3mode_decrease_difference_pp': abs(100 * (1 - p3 / p3base[j]) - float(d3['predicted3mode_decrease_percent'])),
                    'saved_3mode_peak_time_difference_s': abs(float(t[ip3]) - float(d3['predicted_peak_time_s']))})
    writecsv('independent-all300-peak-checks-96.csv', results)
    writecsv('independent-three-mode-predictions-96.csv', selected_results)
    summary = {'manifest_files_verified': len(manifest['outputs']), 'source_baseline_sha256': sha(BASE),
               'prediction_cache_sha256': sha(cache), 'independent_mass_source_sha256': sha(MASS),
               'B_independent_X_mass_projection_max_abs_kg': float(np.max(abs(B - B0))),
               'RK_subdivisions': [8, 16], 'new_candidate_target_solutions': 0,
               'selected_modes': [2, 10, 13],
               'selected_z_w_derivative_max_RK16_relative_L2_error': max(d['RK16_relative_L2_error'] for d in checks if d['state'] in ['z', 'zdot', 'w', 'wdot']),
               'minimum_derivative_refinement_ratio': min(d['RK8_to_RK16_error_ratio'] for d in checks if d['state'] in ['z', 'zdot', 'w', 'wdot']),
               'reconstructed_all300_curve_max_error_kN': max_curve,
               'all300_scalar_rows': len(results), 'all300_numeric_fields': 6 * len(results), 'boolean_fields': 2 * len(results),
               'all300_max_scalar_difference': max(d['max_saved_scalar_difference'] for d in results),
               'independent_three_mode_peak_max_difference_kN': max(d['saved_3mode_peak_difference_kN'] for d in selected_results),
               'independent_three_mode_decrease_max_difference_pp': max(d['saved_3mode_decrease_difference_pp'] for d in selected_results),
               'independent_three_mode_peak_time_max_difference_s': max(d['saved_3mode_peak_time_difference_s'] for d in selected_results),
               'source_static_isolation_review': 'producer reads baseline5 and helper only; no finite candidate truth source in audited code; historical execution I/O was not instrumented',
               'all300_derivative_independence_limit': 'only modes2/10/13 independently integrated; other derivatives used as frozen inputs for all300 scalar reconstruction'}
    assert summary['selected_z_w_derivative_max_RK16_relative_L2_error'] < 1e-6
    assert summary['B_independent_X_mass_projection_max_abs_kg'] < 1e-6
    assert summary['all300_max_scalar_difference'] < 1e-7
    assert summary['independent_three_mode_peak_max_difference_kN'] < 1e-4
    assert summary['independent_three_mode_peak_time_max_difference_s'] == 0
    (O / 'results.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
