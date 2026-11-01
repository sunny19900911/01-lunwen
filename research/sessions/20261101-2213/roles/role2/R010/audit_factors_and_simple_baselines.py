"""Baseline factor reconstruction and CSV-only fair simple-comparator audit."""
from pathlib import Path
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent; S = O.parents[2]; P4 = S / 'roles/role4'; F = P4 / 'R009'; P6 = S / 'roles/role6/R005'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rd(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def wr(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    assert not (O / 'results.json').exists()
    mf = json.loads((F / 'delivery-manifest.json').read_text()); mb = json.loads((P6 / 'freeze.json').read_text())
    for d in mf['files']:
        p = Path(d['path']); assert sha(p) == d['sha256'] and p.stat().st_size == d['bytes']
    for name, d in mb['files'].items():
        p = P6 / name; assert sha(p) == d['sha256'] and p.stat().st_size == d['bytes']
    for rel, digest in mb['source_sha256'].items(): assert sha(P4 / rel) == digest
    factorinputs = json.loads((F / 'input-and-factor-contract-freeze.json').read_text())['inputs']
    for d in factorinputs: assert sha(Path(d['path'])) == d['sha256']
    count = {'factor': 0, 'baseline': 0}; diffs = {'factor': 0., 'baseline': 0.}
    def check(kind, row, values):
        for k, v in values.items():
            count[kind] += 1
            if isinstance(v, (bool, np.bool_)): assert row[k] == str(bool(v)), (k, v, row[k])
            elif isinstance(v, str): assert row[k] == v, (k, v, row[k])
            else:
                e = abs(float(v) - float(row[k])); diffs[kind] = max(diffs[kind], e)
                assert e < 1e-7, (k, v, row[k])
    with np.load(Path(factorinputs[0]['path']), allow_pickle=False) as a:
        t3, s3, om, B = [a[k].copy() for k in ['t', 's_unitGamma', 'omega', 'B_direct']]
    with np.load(Path(factorinputs[1]['path']), allow_pickle=False) as a: z3 = a['z_unit'].copy()
    datasets = [('SHW3X', t3, s3, z3)]
    for case, binding in [('SHW4X', factorinputs[2]), ('RH4X', factorinputs[3])]:
        with np.load(Path(binding['path']), allow_pickle=False) as a:
            assert np.array_equal(om, a['omega']) and np.array_equal(B, a['B'])
            datasets.append((case, a['t'].copy(), a['s0'].copy(), a['Z'].copy()))
    sourcefactor = {(d['Case'], d['Story'], int(d['controller_number']), int(d['Mode'])): d for d in rd(F / 'all300-fixed-and-response-factors-2400.csv')}
    sourcectrl = {(d['Case'], d['Story'], int(d['controller_number'])): d for d in rd(F / 'controller-and-contribution-closure-8.csv')}
    coeff = B * om ** 2 / 1000; selected = [1, 3, 9, 12, 17, 49]; controllers = []; focus = []; maxclose = 0.; modecount = 0
    for case, t, states, z in datasets:
        V = np.einsum('tr,jr->tj', states, coeff, optimize=False); VZ = np.einsum('tr,jr->tj', z, coeff, optimize=False)
        p0 = np.max(abs(V), 0); Sr = []
        for j in range(12):
            active = np.flatnonzero(abs(V[:, j]) == p0[j]); gg = np.sign(V[:, j]) * VZ[:, j]
            prime = max(gg[active]); ctrl = active[gg[active] == prime]
            Sr.append((-float(prime) / p0[j], j, ctrl))
        slowj = min(Sr, key=lambda d: d[0])[1]
        for j in sorted(set([4, 11, slowj])):
            sval, _, control = Sr[j]; story = f'Story{j + 1}'
            for cnum, n in enumerate(control, 1):
                v = coeff[j] * states[n]; dv = coeff[j] * z[n]; cc = -np.sign(V[n, j]) * dv / p0[j]
                order = sorted(range(300), key=lambda k: (-abs(cc[k]), k)); rest = [k for k in range(300) if k not in selected]
                maxclose = max(maxclose, float(abs(np.sum(cc) - sval)))
                check('factor', sourcectrl[case, story, cnum], {'time_s': t[n], 'baseline_signed_V0_kN': V[n, j], 'P0_kN': p0[j],
                    'S_percent_per_damping_pp': sval, 'selected6_c_sum': np.sum(cc[selected]), 'other294_c_sum': np.sum(cc[rest]),
                    'abs_c_top5_sum': np.sum(cc[order[:5]]), 'other295_c_sum': np.sum(cc[order[5:]]),
                    'modal_force_sum_kN': np.sum(v), 'promoting_c_sum': np.sum(cc[cc > 0]), 'opposing_c_sum': np.sum(cc[cc < 0])})
                controllers.append({'Case': case, 'Story': story, 'time_s': float(t[n]), 'S': float(sval),
                    'c_closure_error': float(np.sum(cc) - sval), 'v_closure_error_kN': float(np.sum(v) - V[n, j]),
                    'dv_closure_error_kN_per_zeta': float(np.sum(dv) - VZ[n, j]),
                    'selected6_plus_other294_error': float(np.sum(cc[selected]) + np.sum(cc[rest]) - sval),
                    'top5_plus_other295_error': float(np.sum(cc[order[:5]]) + np.sum(cc[order[5:]]) - sval)})
                for m in range(300):
                    vals = {'time_s': t[n], 'period_s': 2 * np.pi / om[m], 'omega_rad_s': om[m], 'omega_squared_s2': om[m] ** 2,
                        'B_kg': B[j, m], 'sign_B': np.sign(B[j, m]), 's0_unit_m': states[n, m], 'z_unit_m_per_fractional_zeta': z[n, m],
                        'sign_z': np.sign(z[n, m]), 'baseline_signed_V0_kN': V[n, j], 'sign_V0': np.sign(V[n, j]), 'P0_kN': p0[j],
                        'modal_baseline_shear_v_r_kN': v[m], 'modal_shear_derivative_kN_per_zeta': dv[m],
                        'c_improvement_percent_per_damping_pp': cc[m], 'effect': 'promotes' if cc[m] > 0 else ('opposes' if cc[m] < 0 else 'zero')}
                    check('factor', sourcefactor[case, story, cnum, m + 1], vals); modecount += 1
                    if m == 12 and ((case == 'SHW3X' and j in [4, 11]) or (case == 'SHW4X' and j == 4)):
                        focus.append({'Case': case, 'Story': story, 'time_s': float(t[n]), 'period_s': float(2 * np.pi / om[m]),
                            'B_kg': float(B[j, m]), 's_m': float(states[n, m]), 'z_m_per_zeta': float(z[n, m]),
                            'sign_V0': float(np.sign(V[n, j])), 'P0_kN': float(p0[j]), 'v13_kN': float(v[m]), 'dv13_kN_per_zeta': float(dv[m]), 'c13': float(cc[m])})
    assert len(controllers) == 8 and modecount == 2400
    for d in rd(F / 'selected-mode-periods-and-fixed-B-by-floor-24.csv'):
        j, m = int(d['Story'][5:]) - 1, int(d['Mode']) - 1
        check('factor', d, {'period_s': 2 * np.pi / om[m], 'omega_squared_s2': om[m] ** 2, 'B_kg': B[j, m]})
    a = next(d for d in focus if d['Case'] == 'SHW3X' and d['Story'] == 'Story5')
    b = next(d for d in focus if d['Case'] == 'SHW4X')
    roof = next(d for d in focus if d['Case'] == 'SHW3X' and d['Story'] == 'Story12')
    assert a['B_kg'] == b['B_kg'] and a['sign_V0'] == b['sign_V0'] == 1
    assert a['z_m_per_zeta'] < 0 < b['z_m_per_zeta'] and a['c13'] < 0 < b['c13']
    assert a['B_kg'] < 0 and roof['B_kg'] < 0 and a['z_m_per_zeta'] < 0 and roof['z_m_per_zeta'] < 0
    assert a['dv13_kN_per_zeta'] > 0 and roof['dv13_kN_per_zeta'] > 0 and roof['sign_V0'] == -1
    ratio = abs(roof['c13'] / a['c13']); product = abs(roof['B_kg'] / a['B_kg']) * abs(roof['z_m_per_zeta'] / a['z_m_per_zeta']) * a['P0_kN'] / roof['P0_kN']
    assert abs(ratio - product) < 1e-12
    wr('independent-controllers-8.csv', controllers); wr('independent-mode13-factors-3.csv', focus)
    # The rest of this audit reads only the seven already-frozen small CSV sources.
    private = 'SHW3X_fixed300'; public = 'publicExample5_H-E12140'; cases = [private, public]; targets = [.06, .07, .08, .10]
    floors = rd(P4 / 'R006/baseline-sensitivity-ranked-floors-15.csv')
    rates = {(d['Case'], d['Story']): float(d['S_percent_per_damping_pp']) for d in floors}
    medians = {case: float(np.median([v for (c, st), v in rates.items() if c == case])) for case in cases}
    truths = {}
    for case, name, field in [(private, 'R002/exact-reference-truth-peaks-48.csv', 'exact_reference_decrease_percent'),
                             (public, 'R005/exact-reference-floor-peaks-12.csv', 'reference_decrease_percent')]:
        for d in rd(P4 / name): truths[case, d['Story'], float(d['target_zeta'])] = float(d[field])
    predicted = {}
    for (case, story), rate in rates.items():
        for target in targets:
            predicted[case, story, target, 'local_S'] = rate * (100 * (target - .05))
            predicted[case, story, target, 'uniform_median_S'] = medians[case] * (100 * (target - .05))
    for case, name in [(private, 'R002/frozen-prediction-vs-exact-reference-96.csv'), (public, 'R005/frozen-prediction-vs-reference-24.csv')]:
        for d in rd(P4 / name):
            predicted[case, d['Story'], float(d['target_zeta']), 'whole_window_order' + d['Taylor_order']] = float(d['predicted_decrease_percent']) if case == private else 100 * float(d['predicted_D'])
    points = {}
    for (case, story, target, method), pred in predicted.items():
        true = truths[case, story, target]
        points[case, story, target, method] = {'Case': case, 'Story': story, 'target_zeta': target, 'method': method,
            'S_floor': rates[case, story], 'fixed_input_median_S': medians[case], 'b_damping_pp': 100 * (target - .05),
            'predicted_D_percent': pred, 'reference_D_percent': true, 'signed_error_pp': pred - true, 'absolute_error_pp': abs(pred - true),
            'point_decision': 'provisional_meets' if pred >= 10 else 'provisional_insufficient', 'true_insufficient': true < 10, 'true_adverse': true < 0,
            'false_pass': pred >= 10 > true, 'false_reject': pred < 10 <= true, 'false_adverse': pred < 0 <= true, 'missed_adverse': pred >= 0 > true}
    for filename in ['simple-point-baselines-120.csv', 'frozen-whole-window-point-comparators-120.csv']:
        for d in rd(P6 / filename): check('baseline', d, points[d['Case'], d['Story'], float(d['target_zeta']), d['method']])
    summaries = []; candidates = []; candidate_errors = []
    source_summary = rd(P6 / 'method-summary-by-input-8.csv'); source_candidates = rd(P6 / 'whole-candidate-point-decisions-32.csv'); source_detail = rd(P6 / 'method-candidate-errors-32.csv')
    for case in cases:
        for method in ['local_S', 'uniform_median_S', 'whole_window_order1', 'whole_window_order2']:
            rr = [v for k, v in points.items() if k[0] == case and k[3] == method]
            summary = {'n': len(rr), 'bias_pp': float(np.mean([d['signed_error_pp'] for d in rr])), 'MAE_pp': float(np.mean([d['absolute_error_pp'] for d in rr])),
                'max_absolute_error_pp': max(d['absolute_error_pp'] for d in rr),
                **{k: sum(d[k] for d in rr) for k in ['false_pass', 'false_reject', 'false_adverse', 'missed_adverse', 'true_insufficient', 'true_adverse']},
                'predicted_meets': sum(d['predicted_D_percent'] >= 10 for d in rr), 'predicted_adverse': sum(d['predicted_D_percent'] < 0 for d in rr)}
            check('baseline', next(d for d in source_summary if d['Case'] == case and d['method'] == method), summary)
            summaries.append({'Case': case, 'method': method, **summary})
            for target in targets:
                group = [d for d in rr if d['target_zeta'] == target]
                de = {'n': len(group), 'MAE_pp': float(np.mean([d['absolute_error_pp'] for d in group])), 'max_absolute_error_pp': max(d['absolute_error_pp'] for d in group),
                    **{k: sum(d[k] for d in group) for k in ['false_pass', 'false_reject', 'false_adverse', 'missed_adverse']}}
                check('baseline', next(d for d in source_detail if d['Case'] == case and d['method'] == method and float(d['target_zeta']) == target), de)
                predpass = all(d['predicted_D_percent'] >= 10 for d in group); truepass = all(d['reference_D_percent'] >= 10 for d in group)
                ca = {'target_floor_count': len(group), 'point_all_floor_meets': predpass, 'reference_all_floor_meets': truepass,
                    'candidate_false_pass': predpass and not truepass, 'candidate_false_reject': not predpass and truepass}
                check('baseline', next(d for d in source_candidates if d['Case'] == case and d['method'] == method and float(d['target_zeta']) == target), ca)
                candidates.append({'Case': case, 'method': method, 'target_zeta': target, **ca}); candidate_errors.append({'Case': case, 'method': method, 'target_zeta': target, **de})
    mismatch_keys = {(c, st, z, m) for (c, st, z, m), d in points.items() if any(d[k] for k in ['false_pass', 'false_reject', 'false_adverse', 'missed_adverse'])}
    source_mis = rd(P6 / 'all-point-misclassification-cases.csv')
    assert mismatch_keys == {(d['Case'], d['Story'], float(d['target_zeta']), d['method']) for d in source_mis}
    for d in source_mis: check('baseline', d, points[d['Case'], d['Story'], float(d['target_zeta']), d['method']])
    intervals = rd(P6 / 'frozen-whole-window-interval-states-16.csv')
    for case, rel, label in [(private, 'R002/coth-interval-coverage-width-decisions-96.csv', 'private sampled-coth'),
                             (public, 'R005/interval-coverage-width-decisions-24.csv', 'public guarded-discrete')]:
        old = rd(P4 / rel)
        for target in targets:
            for order in [1, 2]:
                rr = [d for d in old if float(d['target_zeta']) == target and int(d['Taylor_order']) == order]
                states = [d['interval_decision'] if case == private else d['decision_status'] for d in rr]
                vals = {'n': len(rr), 'meets': sum(v == 'meets' for v in states), 'insufficient': sum(v == 'insufficient' for v in states),
                    'uncertain': sum(v == 'uncertain' for v in states), 'v001_operational_flagged_floors': sum(d['operational_full_recompute' if case == private else 'v001_operational_recompute'] == 'True' for d in rr), 'interval_method': label}
                check('baseline', next(d for d in intervals if d['Case'] == case and float(d['target_zeta']) == target and int(d['Taylor_order']) == order), vals)
    wr('independent-method-summary-8.csv', summaries); wr('independent-candidate-point-decisions-32.csv', candidates)
    wr('independent-method-candidate-errors-32.csv', candidate_errors)
    result = {'factor_source_files_SHA_verified': len(mf['files']), 'baseline_source_files_SHA_verified': len(mb['files']),
        'factor_baseline_inputs_SHA_verified': len(factorinputs), 'simple_comparison_CSV_inputs_SHA_verified': len(mb['source_sha256']),
        'controllers': len(controllers), 'all_mode_factors_checked': modecount, 'selected_period_B_rows_checked': 24,
        'factor_fields_checked': count['factor'], 'factor_max_numeric_difference': diffs['factor'], 'max_c_closure': maxclose,
        'fixed_omega_B_identical_three_inputs': True, 'Story5_input_change_z_sign_flips_c': True,
        'SHW3_floor5_roof_total_peak_sign_alone_flips_c_sign_with_B_z_signs_same': True,
        'mode13_roof_to_floor5_abs_c_ratio': ratio, 'mode13_B_z_inverseP0_product': product,
        'simple_and_whole_point_rows_checked': len(points), 'baseline_fields_checked': count['baseline'], 'baseline_max_numeric_difference': diffs['baseline'],
        'fixed_input_median_S': medians, 'method_groups': len(summaries), 'candidate_point_groups': len(candidates), 'interval_groups_separate': len(intervals),
        'misclassification_identity_rows_checked': len(mismatch_keys), 'new_ODE_or_target_calculation': False,
        'scope': 'factor audit reads baseline states only; simple-comparator audit reads small CSV only; retrospective known cases, no domination or speedup claim'}
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
