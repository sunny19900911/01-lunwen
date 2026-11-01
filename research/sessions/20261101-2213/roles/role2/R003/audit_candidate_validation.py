"""Read frozen predictions/references, independently check every comparison table."""
from pathlib import Path
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent
R = O.parents[5]
P = R / 'research/sessions/20261101-2213/roles/role4'
Q = P / 'R002'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def key(d, order=True):
    return ((float(d['target_zeta']), int(d['Taylor_order']), d['Story']) if order
            else (float(d['target_zeta']), d['Story']))


def rk(ag, omega, zeta, subdivisions):
    x = np.zeros((3, 2)); result = np.zeros((len(ag), 3, 2)); h = .02 / subdivisions

    def f(v, a):
        return np.column_stack((v[:, 1], -omega ** 2 * v[:, 0] - 2 * zeta * omega * v[:, 1] - a))

    for i in range(len(ag) - 1):
        da = ag[i + 1] - ag[i]
        for j in range(subdivisions):
            a = ag[i] + da * j / subdivisions; am = ag[i] + da * (j + .5) / subdivisions
            ae = ag[i] + da * (j + 1) / subdivisions
            k1 = f(x, a); k2 = f(x + h * k1 / 2, am)
            k3 = f(x + h * k2 / 2, am); k4 = f(x + h * k3, ae)
            x += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        result[i + 1] = x
    return result


def main():
    assert not (O / 'results.json').exists()
    man = json.loads((Q / 'delivery-manifest.json').read_text(encoding='utf-8'))
    for d in man['outputs']:
        p = Q / d['name']; assert p.stat().st_size == d['bytes'] and sha(p) == d['sha256']
    for d in man['inputs']: assert sha(Path(d['path'])) == d['sha256']
    for d in man['target_reference_arrays']: assert sha(Path(d['path'])) == d['sha256']
    policy = json.loads((R / 'research/sessions/20261101-2213/engineering-policy-freeze-v001.json').read_text())
    req, widthlim = policy['demonstration_Dreq'], policy['width_limit_D_fraction']
    with np.load(Path(man['inputs'][0]['path']), allow_pickle=False) as a:
        t, ag, om, s0, b0, px, gamma = [a[k].copy() for k in ['t', 'ag', 'omega', 's_unitGamma', 'B_direct', 'phi_X', 'Gamma_X']]
    masspath = R / 'research/sessions/20261031-1130/roles/role2/R003/independent-identification-before-comparison-36.csv'
    masses = sorted([d for d in read(masspath) if d['direction'] == 'X'], key=lambda d: (int(d['Story'][5:]), d['Diaphragm']))
    mx = np.array([float(d['identified_mass_kg']) for d in masses]); levels = np.array([int(d['Story'][5:]) for d in masses])
    B = np.stack([(mx[levels >= j, None] * px[levels >= j]).sum(0) * gamma for j in range(1, 13)])
    with np.load(Path(man['inputs'][2]['path']), allow_pickle=False) as a:
        zd, wd = a['zdot_unit'].copy(), a['wdot_unit'].copy()
        pred = {(z, o): a[f'z{z:g}_order{o}_shear_inertia_kN'].copy() for z in [.06, .07, .08, .10] for o in [1, 2]}
    v0 = (s0 * om ** 2) @ B.T / 1000; p0 = np.max(abs(v0), 0); idx0 = np.argmax(abs(v0), 0)
    j1 = 2 * abs(B) @ (om * np.max(abs(zd), 0)) / 1000
    j2 = abs(B) @ (om * np.max(abs(wd), 0)) / 1000
    tables = {name: read(Q / name) for name in [
        'exact-reference-truth-peaks-48.csv', 'frozen-prediction-vs-exact-reference-96.csv',
        'baseline-only-coth-bound-prediction-intervals-96.csv', 'coth-interval-coverage-width-decisions-96.csv',
        'all12-target-reference-comparison-wide-48.csv', 'old-peak-first-order-baseline-comparison-48.csv',
        'prediction-and-coth-bound-summary-8.csv', 'candidate-level-recompute-accounting-8.csv',
        'Story5-Story12-priority-truth-and-predictions-8.csv', 'order2-worse-than-order1-peak-cases.csv',
        'point-prediction-insufficient-miss-cases-2.csv']}
    maxdiff = {}; counts = {}; indexes = {}
    for name, rows in tables.items():
        if name in ['prediction-and-coth-bound-summary-8.csv', 'candidate-level-recompute-accounting-8.csv']:
            indexes[name] = {(float(d['target_zeta']), int(d['Taylor_order'])): d for d in rows}
        else:
            indexes[name] = {key(d, 'Taylor_order' in d): d for d in rows}

    def check(name, k, values):
        d = indexes[name][k]
        for field, value in values.items():
            counts[name] = counts.get(name, 0) + 1
            if isinstance(value, (bool, np.bool_)):
                assert d[field] == str(bool(value)), (name, k, field, value, d[field])
            elif isinstance(value, str):
                assert d[field] == value, (name, k, field, value, d[field])
            else:
                diff = abs(float(value) - float(d[field])); maxdiff[name] = max(maxdiff.get(name, 0.), diff)
                assert diff < 1e-7, (name, k, field, value, d[field])

    computed = []; reference = []; oldrows = []; projection_error = 0.; rkrows = []
    for origin in man['target_reference_arrays']:
        z = origin['zeta']
        with np.load(Path(origin['path']), allow_pickle=False) as a:
            assert np.array_equal(t, a['t']) and np.array_equal(om, a['omega']) and np.array_equal(b0, a['B_direct'])
            ss, vv = a['s_unitGamma'].copy(), a['sdot_unitGamma'].copy()
            savedv = a['shear_elastic_inertia_predicted_kN'] if z == .08 else a['shear_elastic_inertia_kN']
            vt = (ss * om ** 2) @ B.T / 1000
            projection_error = max(projection_error, float(np.max(abs(vt - savedv))))
        if z == .10:
            sel = np.array([1, 9, 12]); c = rk(ag, om[sel], z, 8); f = rk(ag, om[sel], z, 16)
            for i, mode in enumerate(sel + 1):
                for col, label in [(0, 's'), (1, 'sdot')]:
                    arr = ss[:, mode - 1] if col == 0 else vv[:, mode - 1]
                    ec = np.linalg.norm(c[:, i, col] - arr); ef = np.linalg.norm(f[:, i, col] - arr)
                    rkrows.append({'target_zeta': z, 'Mode': int(mode), 'state': label,
                        'RK16_relative_L2_error': float(ef / np.linalg.norm(arr)),
                        'RK8_to_RK16_error_ratio': float(ec / ef),
                        'RK16_max_absolute_error': float(np.max(abs(f[:, i, col] - arr)))})
        pt = np.max(abs(vt), 0); it = np.argmax(abs(vt), 0); dt = 1 - pt / p0
        kappa = 1 / np.tanh(np.pi * z / (2 * np.sqrt(1 - z ** 2)))
        for j in range(12):
            story = f'Story{j + 1}'; kr = (z, story)
            ref = {'baseline_peak_kN': p0[j], 'exact_reference_peak_kN': pt[j],
                   'exact_reference_decrease_percent': 100 * dt[j], 'exact_reference_peak_time_s': t[it[j]],
                   'truth_insufficient_below10pct': dt[j] < req, 'truth_adverse_Dlt0': dt[j] < 0}
            check('exact-reference-truth-peaks-48.csv', kr, ref)
            check('all12-target-reference-comparison-wide-48.csv', kr, ref)
            if j in [4, 11]: check('Story5-Story12-priority-truth-and-predictions-8.csv', kr, ref)
            reference.append({'target_zeta': z, 'Story': story, 'Dtrue': float(dt[j]), 'Ptrue': float(pt[j])})
            oldp = abs(pred[z, 1][idx0[j], j]); oldlin = p0[j] + np.sign(v0[idx0[j], j]) * (pred[z, 1][idx0[j], j] - v0[idx0[j], j])
            do = 1 - oldp / p0[j]
            old = {'baseline5_peak_time_s': t[idx0[j]], 'old_time_first_order_abs_value_kN': oldp,
                   'old_time_linearized_peak_value_kN': oldlin, 'linearized_value_negative': oldlin < 0,
                   'old_time_prediction_decrease_percent': 100 * do, 'exact_reference_peak_kN': pt[j],
                   'peak_relative_error': oldp / pt[j] - 1, 'decrease_error_pp': 100 * (do - dt[j]),
                   'miss_insufficient': dt[j] < req <= do, 'false_insufficient': do < req <= dt[j],
                   'miss_adverse': dt[j] < 0 <= do, 'false_adverse': do < 0 <= dt[j]}
            check('old-peak-first-order-baseline-comparison-48.csv', kr, old)
            oldrows.append({'target_zeta': z, 'Story': story, **old})
            for order in [1, 2]:
                k = (z, order, story); phcurve = pred[z, order][:, j]; ih = np.argmax(abs(phcurve)); ph = abs(phcurve[ih])
                dh = 1 - ph / p0[j]; err = ph / pt[j] - 1; sup = np.max(abs(phcurve - vt[:, j]))
                vals = {'P0_kN': p0[j], 'predicted_peak_kN': ph, 'exact_reference_peak_kN': pt[j],
                    'peak_relative_error': err, 'absolute_peak_relative_error': abs(err),
                    'predicted_decrease_percent': 100 * dh, 'exact_reference_decrease_percent': 100 * dt[j],
                    'decrease_error_percentage_points': 100 * (dh - dt[j]),
                    'predicted_peak_time_s': t[ih], 'exact_reference_peak_time_s': t[it[j]],
                    'peak_time_error_s': t[ih] - t[it[j]], 'curve_signed_NRMSE': np.linalg.norm(phcurve - vt[:, j]) / np.linalg.norm(vt[:, j]),
                    'curve_sup_error_kN': sup, 'truth_insufficient': dt[j] < req,
                    'point_miss_insufficient': dt[j] < req <= dh, 'point_false_insufficient': dh < req <= dt[j],
                    'truth_adverse': dt[j] < 0, 'point_miss_adverse': dt[j] < 0 <= dh, 'point_false_adverse': dh < 0 <= dt[j]}
                check('frozen-prediction-vs-exact-reference-96.csv', k, vals)
                wide = {f'order{order}_{name}': value for name, value in [
                    ('peak_kN', ph), ('peak_relative_error', err), ('decrease_percent', 100 * dh),
                    ('decrease_error_pp', 100 * (dh - dt[j])), ('peak_time_s', t[ih])]}
                check('all12-target-reference-comparison-wide-48.csv', kr, wide)
                if j in [4, 11]: check('Story5-Story12-priority-truth-and-predictions-8.csv', kr, wide)
                E = (j1[j] * (z - .05) ** 2 if order == 1 else j2[j] * abs(z - .05) ** 3) * kappa
                pl = max(0., ph - E); pu = ph + E; dl = 1 - pu / p0[j]; du = 1 - pl / p0[j]; width = du - dl
                decision = 'meets' if dl >= req else ('insufficient' if du < req else 'uncertain')
                op = decision == 'uncertain' or width > widthlim
                b = {'P0_kN': p0[j], 'predicted_peak_kN': ph, 'sampled_residual_coth_E_kN': E,
                     'E_over_P0': E / p0[j], 'P_lower_kN': pl, 'P_upper_kN': pu, 'D_lower': dl, 'D_upper': du,
                     'D_interval_width': width, 'Dreq_demo': req, 'Wmax_demo': widthlim,
                     'interval_decision': decision, 'width_status': 'too_wide' if width > widthlim else 'acceptable',
                     'operational_full_recompute': op,
                     'adverse_interval_flag': 'certain_adverse' if du < 0 else ('adverse_not_excluded' if dl < 0 else 'adverse_excluded_within_interval')}
                check('baseline-only-coth-bound-prediction-intervals-96.csv', k, b)
                b.update({'exact_reference_peak_kN': pt[j], 'exact_reference_decrease_percent': 100 * dt[j],
                    'observed_curve_sup_error_kN': sup, 'sampled_bound_peak_coverage': pl - 1e-8 <= pt[j] <= pu + 1e-8,
                    'sampled_bound_curve_coverage': sup <= E + 1e-8,
                    'interval_miss_insufficient': dt[j] < req and decision == 'meets',
                    'interval_false_insufficient': dt[j] >= req and decision == 'insufficient',
                    'interval_miss_adverse': dt[j] < 0 and dl >= 0,
                    'adverse_action_miss': dt[j] < 0 and decision == 'meets', 'adverse_risk_miss': dt[j] < 0 and dl >= 0})
                check('coth-interval-coverage-width-decisions-96.csv', k, b)
                computed.append({'target_zeta': z, 'Taylor_order': order, 'Story': story, **vals, **b})
    summaries = []; candidates = []
    for z in [.06, .07, .08, .10]:
        for order in [1, 2]:
            rr = [d for d in computed if d['target_zeta'] == z and d['Taylor_order'] == order]
            summ = {'layers': 12, 'max_absolute_peak_relative_error': max(d['absolute_peak_relative_error'] for d in rr),
                'max_absolute_decrease_error_pp': max(abs(d['decrease_error_percentage_points']) for d in rr),
                'max_absolute_peak_time_error_s': max(abs(d['peak_time_error_s']) for d in rr),
                **{name: sum(bool(d[name]) for d in rr) for name in ['point_miss_insufficient', 'point_false_insufficient', 'truth_insufficient', 'truth_adverse', 'point_miss_adverse', 'point_false_adverse', 'interval_miss_insufficient', 'interval_miss_adverse']},
                'peak_interval_coverage': sum(d['sampled_bound_peak_coverage'] for d in rr) / 12,
                'curve_interval_coverage': sum(d['sampled_bound_curve_coverage'] for d in rr) / 12,
                'median_D_interval_width': float(np.median([d['D_interval_width'] for d in rr])),
                'max_D_interval_width': max(d['D_interval_width'] for d in rr),
                'mathematical_uncertain_fraction': sum(d['interval_decision'] == 'uncertain' for d in rr) / 12,
                'too_wide_fraction': sum(d['width_status'] == 'too_wide' for d in rr) / 12,
                'full_recompute_fraction': sum(d['operational_full_recompute'] for d in rr) / 12}
            check('prediction-and-coth-bound-summary-8.csv', (z, order), summ)
            dec = 'insufficient' if any(d['interval_decision'] == 'insufficient' for d in rr) else ('meets' if all(d['interval_decision'] == 'meets' for d in rr) else 'uncertain')
            flags = sum(d['operational_full_recompute'] for d in rr)
            cand = {'mathematical_whole_building_decision': dec, 'operational_flagged_layers': int(flags), 'unique_full_building_recompute_count_if_all_flagged_layers_checked': int(flags > 0)}
            check('candidate-level-recompute-accounting-8.csv', (z, order), cand)
            summaries.append({'target_zeta': z, 'Taylor_order': order, **summ}); candidates.append({'target_zeta': z, 'Taylor_order': order, **cand})
    misses = [d for d in computed if d['point_miss_insufficient']]
    assert set(key(d) for d in misses) == set(indexes['point-prediction-insufficient-miss-cases-2.csv'])
    for d in misses: check('point-prediction-insufficient-miss-cases-2.csv', key(d), {name: d[name] for name in ['predicted_decrease_percent', 'exact_reference_decrease_percent', 'peak_relative_error', 'point_miss_insufficient']})
    pairkeys = [(d['target_zeta'], d['Story']) for d in reference]
    worse = []
    for z, st in pairkeys:
        a, b = [next(d for d in computed if key(d) == (z, order, st)) for order in [1, 2]]
        if b['absolute_peak_relative_error'] > a['absolute_peak_relative_error']:
            worse.append({'target_zeta': z, 'Story': st, 'order1_error': float(a['peak_relative_error']), 'order2_error': float(b['peak_relative_error'])})
    assert set((d['target_zeta'], d['Story']) for d in worse) == set(indexes['order2-worse-than-order1-peak-cases.csv'])
    write('independent-target-RK4-6.csv', rkrows); write('independent-summary-8.csv', summaries)
    write('independent-point-misses-2.csv', [{k: d[k] for k in ['target_zeta', 'Taylor_order', 'Story', 'predicted_decrease_percent', 'exact_reference_decrease_percent', 'interval_decision', 'operational_full_recompute']} for d in misses])
    write('independent-order2-worse-14.csv', worse)
    write('independent-table-checks.csv', [{'table': name, 'field_checks': counts[name], 'max_numeric_difference': maxdiff.get(name, 0.)} for name in counts])
    result = {'producer_files_SHA_verified': len(man['outputs']), 'source_files_SHA_verified': len(man['inputs']),
        'target_array_SHA_verified': 4, 'independent_X_B_max_difference_kg': float(np.max(abs(B - b0))),
        'physical_target_projection_max_difference_kN': projection_error,
        'table_field_checks': int(sum(counts.values())), 'table_count': len(counts), 'max_table_numeric_difference': max(maxdiff.values()),
        'selected_new_target_zeta': .10, 'selected_modes': [2, 10, 13],
        'selected_target_RK16_max_relative_L2_error': max(d['RK16_relative_L2_error'] for d in rkrows),
        'selected_target_RK_refinement_min_ratio': min(d['RK8_to_RK16_error_ratio'] for d in rkrows),
        'new_full300_reference_solves_by_auditor': 0, 'point_miss_count': len(misses), 'order2_worse_pairs': len(worse),
        'truth_adverse_count': sum(d['Dtrue'] < 0 for d in reference), 'adverse_miss_rate': None,
        'all96_peak_and_curve_coverage': all(d['sampled_bound_peak_coverage'] and d['sampled_bound_curve_coverage'] for d in computed),
        'all8_candidates_still_trigger_one_building_solve_under_frozen_policy': all(d['unique_full_building_recompute_count_if_all_flagged_layers_checked'] == 1 for d in candidates),
        'bound_scope': 'sampled residual maxima; empirical grid check, no continuous numerical certificate',
        'recovery_source_review': 'no states solver or producer import in recovery; only existing tables/arrays read',
        'adverse_miss_denominator': 'NA because no adverse truth samples'}
    assert result['selected_target_RK16_max_relative_L2_error'] < 1e-6
    assert result['selected_target_RK_refinement_min_ratio'] > 15
    assert result['point_miss_count'] == 2 and result['order2_worse_pairs'] == 14
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
