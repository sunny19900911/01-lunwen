"""Independent max-envelope/S/controller audit; one selected new10 RK4 check."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent; S = O.parents[2]; P4 = S / 'roles/role4'; P = P4 / 'R010'
CASES = ['SHW3X', 'SHW4X', 'RH4X']; ZS = [.06, .07, .08, .10]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rd(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def wr(n, rows):
    with (O / n).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    assert not (O / 'results.json').exists()
    m = json.loads((P / 'delivery-manifest.json').read_text()); rules = json.loads((P / 'input-method-envelope-rules-freeze-v002.json').read_text())
    for d in m['files'] + m['local_only_new_arrays'] + m['readonly_reused8_arrays']:
        p = Path(d['path']); assert sha(p) == d['sha256'] and p.stat().st_size == d['bytes']
    for d in rules['inputs']: assert sha(Path(d['path'])) == d['sha256']
    policyfile = S / 'engineering-input-envelope-policy-freeze-v001.json'; policy = json.loads(policyfile.read_text())
    assert policy['cases'] == CASES and policy['Dreq_fraction'] == .10 and policy['width_max_fraction'] == .05
    freeze = json.loads((P / 'prediction-and-envelope-freeze.json').read_text())
    assert sha(policyfile) == freeze['additional_input_envelope_policy_sha256']
    assert policyfile.stat().st_mtime < datetime.fromisoformat(freeze['frozen_utc']).timestamp()
    count = 0; maxdiff = 0.
    def check(d, vals):
        nonlocal count, maxdiff
        for k, v in vals.items():
            count += 1
            if isinstance(v, (bool, np.bool_)): assert d[k] == str(bool(v)), (k, v, d[k])
            elif isinstance(v, str): assert d[k] == v, (k, v, d[k])
            else:
                e = abs(float(v) - float(d[k])); maxdiff = max(maxdiff, e); assert e < 1e-7, (k, v, d[k])
    # Independently normalize the original individual-input snapshots, retaining them all.
    individual = {}
    def add(case, bounds, preds):
        for b in bounds:
            z, order, story = float(b['target_zeta']), int(b['Taylor_order']), b['Story']
            p = next(d for d in preds if float(d['target_zeta']) == z and int(d['Taylor_order']) == order and d['Story'] == story)
            p0 = float(b['P0_kN']); ph = float(p.get('Phat_kN', p.get('predicted_peak_kN')))
            lo, up = float(b['P_lower_kN']), float(b['P_upper_kN']); dl, du = 1 - up / p0, 1 - lo / p0
            status = 'meets' if dl >= .1 else ('insufficient' if du < .1 else 'uncertain')
            individual[case, z, order, story] = {'Case': case, 'target_zeta': z, 'Taylor_order': order, 'Story': story,
                'P0_kN': p0, 'Phat_kN': ph, 'L_kN': lo, 'U_kN': up, 'D_lower': dl, 'D_upper': du, 'D_width': du - dl,
                'decision_status': status, 'width_status': 'too_wide' if du - dl > .05 else 'acceptable', 'v001_recompute': status == 'uncertain' or du - dl > .05}
    add('SHW3X', rd(P4 / 'R003/baseline-only-discrete-envelope-intervals-96.csv'), rd(P4 / 'R001/all300-layer-peak-predictions-96.csv'))
    for case, path in [('SHW4X', 'R007'), ('RH4X', 'R008')]:
        add(case, rd(P4 / path / 'frozen-discrete-intervals-48.csv'), rd(P4 / path / 'frozen-candidate-peak-predictions-48.csv'))
        add(case, [d for d in rd(P / 'new-individual-discrete-intervals-96.csv') if d['Case'] == case], [d for d in rd(P / 'new-individual-peak-predictions-96.csv') if d['Case'] == case])
    assert len(individual) == 288
    for d in rd(P / 'all-individual-frozen-intervals-288.csv'): check(d, individual[d['Case'], float(d['target_zeta']), int(d['Taylor_order']), d['Story']])
    # New predictions are checked against stored baseline derivatives, no new derivative solve.
    base = {}; pred = {}; env = {}; projection = 0.; curvechecks = []
    for case, ruleidx, ar in [('SHW4X', 4, freeze['new_local_arrays'][0]), ('RH4X', 5, freeze['new_local_arrays'][1])]:
        with np.load(Path(rules['inputs'][ruleidx]['path']), allow_pickle=False) as a:
            base[case] = {k: a[k].copy() for k in ['t', 'ag', 'omega', 'B', 's0', 'Z', 'W']}
        d = base[case]
        with np.load(Path(ar['path']), allow_pickle=False) as a:
            assert np.array_equal(d['t'], a['t'])
            for z in [.08, .10]:
                for order in [1, 2]:
                    pred[case, z, order] = a[f'z{z:g}_order{order}_V'].copy(); env[case, z, order] = a[f'z{z:g}_order{order}_E'].copy()
                    sh = d['s0'] + (z - .05) * d['Z'] + ((z - .05) ** 2 * d['W'] / 2 if order == 2 else 0)
                    projection = max(projection, float(np.max(abs((sh * d['omega'] ** 2) @ d['B'].T / 1000 - pred[case, z, order]))))
                    for j in range(12):
                        r = individual[case, z, order, f'Story{j + 1}']; vh = abs(pred[case, z, order][:, j]); ee = env[case, z, order][:, j]
                        assert abs(max(0., np.max(vh - ee)) - r['L_kN']) < 1e-7 and abs(np.max(vh + ee) - r['U_kN']) < 1e-7
    truths = {}
    for d in rd(P4 / 'R002/exact-reference-truth-peaks-48.csv'):
        truths['SHW3X', float(d['target_zeta']), d['Story']] = {'P0_kN': float(d['baseline_peak_kN']), 'reference_peak_kN': float(d['exact_reference_peak_kN']), 'reference_D': float(d['exact_reference_decrease_percent']) / 100, 'reference_peak_time_s': float(d['exact_reference_peak_time_s'])}
    for case, path in [('SHW4X', 'R007'), ('RH4X', 'R008')]:
        for d in rd(P4 / path / 'exact-reference-floor-peaks-24.csv'):
            truths[case, float(d['target_zeta']), d['Story']] = {k: float(d[k]) for k in ['P0_kN', 'reference_peak_kN', 'reference_D', 'reference_peak_time_s']}
    referenceindex = json.loads((P / 'reference-array-index-4.json').read_text()); strict_uncovered = 0; new10positions = None
    for item in referenceindex:
        case, z = item['Case'], item['target_zeta']; b = base[case]
        assert item['new_state_solve'] == int(z == .10)
        with np.load(Path(item['path']), allow_pickle=False) as a:
            assert np.array_equal(b['t'], a['t']) and np.array_equal(b['ag'], a['ag']) and np.array_equal(b['omega'], a['omega'])
            assert np.array_equal(b['B'], a['B_direct' if z == .08 else 'B'])
            qs = a['s_unitGamma' if z == .08 else 's'].copy(); vt = a['shear_elastic_inertia_predicted_kN' if z == .08 else 'V'].copy()
        assert np.max(abs((qs * b['omega'] ** 2) @ b['B'].T / 1000 - vt)) < 1e-7
        if case == 'SHW4X' and z == .10: new10positions = qs
        pk = np.max(abs(vt), 0); it = np.argmax(abs(vt), 0)
        for j in range(12):
            p0 = individual[case, z, 1, f'Story{j + 1}']['P0_kN']
            truths[case, z, f'Story{j + 1}'] = {'P0_kN': p0, 'reference_peak_kN': float(pk[j]), 'reference_D': float(1 - pk[j] / p0), 'reference_peak_time_s': float(b['t'][it[j]])}
        for order in [1, 2]:
            for j in range(12):
                gap = abs(pred[case, z, order][:, j] - vt[:, j]) - env[case, z, order][:, j]
                strict_uncovered += int(np.count_nonzero(gap > 0))
                curvechecks.append({'Case': case, 'zeta': z, 'order': order, 'Story': f'Story{j + 1}', 'uncovered_samples': int(np.count_nonzero(gap > 0)), 'max_error_minus_E_kN': float(np.max(gap))})
    assert len(truths) == 144 and strict_uncovered == 0
    for d in rd(P / 'all-individual-reference-peaks-144.csv'): check(d, truths[d['Case'], float(d['target_zeta']), d['Story']])
    for d in rd(P / 'all-individual-scalar-validation-288.csv'):
        case, z, order, story = d['Case'], float(d['target_zeta']), int(d['Taylor_order']), d['Story']; r = individual[case, z, order, story]; tr = truths[case, z, story]
        dh = 1 - r['Phat_kN'] / r['P0_kN']; dt = tr['reference_D']; pt = tr['reference_peak_kN']
        check(d, {**r, 'reference_peak_kN': pt, 'reference_D': dt, 'peak_relative_error': r['Phat_kN'] / pt - 1,
            'peak_covered': r['L_kN'] <= pt <= r['U_kN'], 'point_insufficient_miss': dt < .1 <= dh, 'point_false_insufficient': dh < .1 <= dt,
            'point_false_adverse': dh < 0 <= dt, 'true_adverse': dt < 0, 'interval_insufficient_miss': dt < .1 and r['decision_status'] == 'meets', 'interval_false_insufficient': dt >= .1 and r['decision_status'] == 'insufficient'})
    # Envelope baseline uses the active peak-input set, never min over all S values.
    rates = {}
    for case, path in [('SHW3X', 'R006/baseline-sensitivity-ranked-floors-15.csv'), ('SHW4X', 'R007/baseline-S-ranked-floors-12.csv'), ('RH4X', 'R008/baseline-S-ranked-floors-12.csv')]:
        for d in rd(P4 / path):
            if case == 'SHW3X' and d['Case'] != 'SHW3X_fixed300': continue
            rates[case, d['Story']] = float(d['S_percent_per_damping_pp'])
    baseline = []; p0env = {}
    for j in range(12):
        st = f'Story{j + 1}'; pp = {c: individual[c, .06, 1, st]['P0_kN'] for c in CASES}; peak = max(pp.values()); active = [c for c in CASES if pp[c] == peak]
        sval = -max(-rates[c, st] * pp[c] for c in active) / peak; p0env[st] = peak
        baseline.append({'Story': st, 'P0env_kN': peak, 'baseline_controlling_inputs': ';'.join(active), 'exact_input_tie_count': len(active),
            'S_env_percent_per_damping_pp': sval, 'min_individual_S_percent_per_damping_pp': min(rates[c, st] for c in CASES), 'env_slow_rank': 0})
    for d in baseline: d['env_slow_rank'] = 1 + sum(v['S_env_percent_per_damping_pp'] < d['S_env_percent_per_damping_pp'] for v in baseline)
    for d in rd(P / 'baseline-input-envelope-S-12.csv'): check(d, next(v for v in baseline if v['Story'] == d['Story']))
    envsource = rd(P / 'input-envelope-interval-and-objective-validation-96.csv'); envtruthsource = rd(P / 'input-envelope-reference-peaks-and-strong-objective-48.csv')
    calculated = []; envelope_truth = []
    for z in ZS:
        for j in range(12):
            st = f'Story{j + 1}'; rr = [truths[c, z, st] for c in CASES]; truepeak = max(d['reference_peak_kN'] for d in rr)
            truecases = [c for c in CASES if truths[c, z, st]['reference_peak_kN'] == truepeak]; trueD = 1 - truepeak / p0env[st]; strongD = min(d['reference_D'] for d in rr)
            et = {'target_zeta': z, 'Story': st, 'P0env_kN': p0env[st], 'reference_envelope_peak_kN': truepeak, 'reference_envelope_D': trueD,
                'reference_controlling_inputs': ';'.join(truecases), 'min_individual_reference_D': strongD,
                'min_individual_controlling_inputs': ';'.join(c for c in CASES if truths[c, z, st]['reference_D'] == strongD), 'envelope_minus_min_individual_D': trueD - strongD}
            check(next(d for d in envtruthsource if float(d['target_zeta']) == z and d['Story'] == st), et); envelope_truth.append(et)
            for order in [1, 2]:
                ir = [individual[c, z, order, st] for c in CASES]; lo = max(d['L_kN'] for d in ir); up = max(d['U_kN'] for d in ir); ph = max(d['Phat_kN'] for d in ir)
                dl, du = 1 - up / p0env[st], 1 - lo / p0env[st]; width = du - dl; dec = 'meets' if dl >= .1 else ('insufficient' if du < .1 else 'uncertain')
                potential = [c for c in CASES if individual[c, z, order, st]['U_kN'] >= lo]; allcovered = all(c in potential for c in truecases)
                ev = {'target_zeta': z, 'Taylor_order': order, 'Story': st, 'P0env_kN': p0env[st], 'Phat_env_kN': ph, 'L_env_kN': lo, 'U_env_kN': up,
                    'D_env_point': 1 - ph / p0env[st], 'D_env_lower': dl, 'D_env_upper': du, 'D_env_width': width, 'decision_status': dec,
                    'width_status': 'too_wide' if width > .05 else 'acceptable', 'v001_recompute': dec == 'uncertain' or width > .05,
                    'predicted_peak_controlling_inputs': ';'.join(c for c in CASES if individual[c, z, order, st]['Phat_kN'] == ph),
                    'potential_controlling_inputs': ';'.join(potential), 'min_individual_D_lower': min(d['D_lower'] for d in ir), 'min_individual_D_upper': min(d['D_upper'] for d in ir),
                    'reference_envelope_peak_kN': truepeak, 'reference_envelope_D': trueD, 'reference_controlling_inputs': ';'.join(truecases),
                    'min_individual_reference_D': strongD, 'envelope_minus_min_individual_D': trueD - strongD, 'peak_covered': lo <= truepeak <= up,
                    'point_insufficient_miss': trueD < .1 <= 1 - ph / p0env[st], 'interval_insufficient_miss': trueD < .1 and dec == 'meets',
                    'interval_false_insufficient': trueD >= .1 and dec == 'insufficient', 'true_envelope_adverse': trueD < 0, 'actual_input_among_potential': allcovered}
                check(next(d for d in envsource if float(d['target_zeta']) == z and int(d['Taylor_order']) == order and d['Story'] == st), ev); calculated.append(ev)
    def action(rr, lower, upper, width):
        return 'reject' if any(d[upper] < .1 for d in rr) else ('pass' if all(d[lower] >= .1 and d[width] <= .05 for d in rr) else 'recompute')
    candidates = []; sourcec = rd(P / 'input-envelope-candidate-validation-8.csv')
    for z in ZS:
        true = [d for d in envelope_truth if d['target_zeta'] == z]
        for order in [1, 2]:
            rr = [d for d in calculated if d['target_zeta'] == z and d['Taylor_order'] == order]; ir = [individual[c, z, order, f'Story{j + 1}'] for c in CASES for j in range(12)]
            a = action(rr, 'D_env_lower', 'D_env_upper', 'D_env_width'); stronga = action(ir, 'D_lower', 'D_upper', 'D_width')
            truepass = all(d['reference_envelope_D'] >= .1 for d in true); strongpass = all(d['min_individual_reference_D'] >= .1 for d in true)
            vals = {'envelope_candidate_action': a, 'strong_each_input_candidate_action': stronga,
                'envelope_meets_floors': sum(d['decision_status'] == 'meets' for d in rr), 'envelope_insufficient_floors': sum(d['decision_status'] == 'insufficient' for d in rr),
                'envelope_uncertain_floors': sum(d['decision_status'] == 'uncertain' for d in rr), 'envelope_too_wide_floors': sum(d['width_status'] == 'too_wide' for d in rr),
                'envelope_v001_flagged_floors': sum(d['v001_recompute'] for d in rr), 'true_envelope_all12_meet': truepass, 'true_strong_each_input_all12_meet': strongpass,
                'envelope_false_pass': not truepass and a == 'pass', 'envelope_false_reject': truepass and a == 'reject',
                'min_envelope_reference_D': min(d['reference_envelope_D'] for d in true), 'min_strong_reference_D': min(d['min_individual_reference_D'] for d in true)}
            check(next(d for d in sourcec if float(d['target_zeta']) == z and int(d['Taylor_order']) == order), vals)
            limit = min(true, key=lambda d: d['reference_envelope_D'])
            candidates.append({'target_zeta': z, 'Taylor_order': order, 'limiting_floor': limit['Story'], **vals})
    # One independent new10 reference subset, without producing a full target history.
    b = base['SHW4X']; sel = np.array([1, 9, 12]); om = b['omega'][sel]; ag = b['ag']
    def rk(sub):
        x = np.zeros((3, 2)); hist = np.zeros((len(ag), 3)); h = .02 / sub
        def f(v, a): return np.column_stack([v[:, 1], -om ** 2 * v[:, 0] - .2 * om * v[:, 1] - a])
        for n in range(len(ag) - 1):
            da = ag[n + 1] - ag[n]
            for j in range(sub):
                a = ag[n] + da * j / sub; am = ag[n] + da * (j + .5) / sub; ae = ag[n] + da * (j + 1) / sub
                k1 = f(x, a); k2 = f(x + h * k1 / 2, am); k3 = f(x + h * k2 / 2, am); k4 = f(x + h * k3, ae)
                x += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            hist[n + 1] = x[:, 0]
        return hist
    coarse, fine = rk(8), rk(16); rkrows = []
    for j, mode in enumerate(sel + 1):
        target = new10positions[:, mode - 1]; ec = np.linalg.norm(coarse[:, j] - target); ef = np.linalg.norm(fine[:, j] - target)
        rkrows.append({'Case': 'SHW4X', 'zeta': .10, 'Mode': int(mode), 'RK16_relative_L2_error': float(ef / np.linalg.norm(target)), 'RK8_to_RK16_error_ratio': float(ec / ef)})
    assert max(d['RK16_relative_L2_error'] for d in rkrows) < 1e-6
    assert all(d['actual_input_among_potential'] for d in calculated)
    wr('independent-envelope-baseline-S-12.csv', baseline); wr('independent-envelope-reference-48.csv', envelope_truth)
    wr('independent-envelope-candidate-decisions-8.csv', candidates); wr('independent-new-reference-RK4-3.csv', rkrows)
    wr('independent-new-individual-curve-checks-96.csv', curvechecks)
    s5 = next(d for d in baseline if d['Story'] == 'Story5'); s7 = next(d for d in baseline if d['Story'] == 'Story7')
    result = {'source_files_SHA_verified': len(m['files']), 'new_arrays_SHA_verified': len(m['local_only_new_arrays']),
        'reused8_arrays_SHA_and_t_ag_omega_B_verified': len(m['readonly_reused8_arrays']), 'input_files_SHA_verified': len(rules['inputs']),
        'individual_intervals': len(individual), 'individual_references': len(truths), 'envelope_intervals': len(calculated), 'envelope_truths': len(envelope_truth),
        'fields_checked': count, 'max_numeric_difference': maxdiff, 'new_prediction_projection_max_error_kN': projection,
        'new96_curve_strict_uncovered_samples': strict_uncovered, 'new_full300_target_solves': 0, 'independent_selected_target': 'SHW4X10% modes2/10/13',
        'selected_RK16_max_relative_L2_error': max(d['RK16_relative_L2_error'] for d in rkrows),
        'selected_RK_refinement_min_ratio': min(d['RK8_to_RK16_error_ratio'] for d in rkrows),
        'Senv_Story5': s5['S_env_percent_per_damping_pp'], 'minS_Story5': s5['min_individual_S_percent_per_damping_pp'],
        'Senv_slowest': min(baseline, key=lambda d: d['S_env_percent_per_damping_pp'])['Story'],
        'Story7_baseline_controller': s7['baseline_controlling_inputs'],
        'Story7_true_controllers': {str(z): next(d['reference_controlling_inputs'] for d in envelope_truth if d['target_zeta'] == z and d['Story'] == 'Story7') for z in ZS},
        'actual_controllers_all_in_potential_set': True, 'interval_miss_count': sum(d['interval_insufficient_miss'] for d in calculated),
        'envelope_point_miss_count': sum(d['point_insufficient_miss'] for d in calculated),
        'true_individual_adverse_count': sum(d['reference_D'] < 0 for d in truths.values()),
        'scope': 'additional max-of-input-peak objective; previous per-input objective preserved; not simultaneous wave summation, strict FP/continuous certificate or speedup'}
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
