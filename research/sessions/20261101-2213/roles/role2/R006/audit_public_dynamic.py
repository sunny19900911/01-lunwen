"""Independent selected-mode RK4 and public-case small-table/decision/cost audit."""
from pathlib import Path
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent; S = O.parents[2]; P = S / 'roles/role4/R004'; Q = S / 'roles/role4/R005'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rd(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def wr(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def integrate(ag, omega, substeps):
    # Three selected baseline modes and the same three modes at candidate .10.
    om = np.r_[omega, omega]; zeta = np.r_[np.full(3, .05), np.full(3, .10)]
    deriv = np.r_[np.ones(3), np.zeros(3)]; x = np.zeros((6, 6)); hist = np.zeros((len(ag), 6, 6)); h = .005 / substeps
    def f(v, a):
        out = np.empty_like(v); out[:, 0::2] = v[:, 1::2]
        out[:, 1] = -om ** 2 * v[:, 0] - 2 * zeta * om * v[:, 1] - a
        out[:, 3] = -om ** 2 * v[:, 2] - 2 * zeta * om * v[:, 3] - 2 * om * v[:, 1] * deriv
        out[:, 5] = -om ** 2 * v[:, 4] - 2 * zeta * om * v[:, 5] - 4 * om * v[:, 3] * deriv
        return out
    for n in range(len(ag) - 1):
        da = ag[n + 1] - ag[n]
        for j in range(substeps):
            a0 = ag[n] + da * j / substeps; am = ag[n] + da * (j + .5) / substeps; a1 = ag[n] + da * (j + 1) / substeps
            k1 = f(x, a0); k2 = f(x + h * k1 / 2, am); k3 = f(x + h * k2 / 2, am); k4 = f(x + h * k3, a1)
            x += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        hist[n + 1] = x
    return hist


def main():
    assert not (O / 'results.json').exists()
    manifests = [json.loads((d / 'delivery-manifest.json').read_text()) for d in [P, Q]]
    for m in manifests:
        for d in m['files'] + m['local_only_arrays']:
            path = Path(d['path']); assert sha(path) == d['sha256'] and path.stat().st_size == d['bytes']
    rules = json.loads((P / 'input-method-rules-freeze.json').read_text())
    for d in rules['inputs']: assert sha(Path(d['path'])) == d['sha256']
    interface = json.loads((S / 'roles/role6/R002/assembled-v001/static-interface.json').read_text())
    phi, C, G, B = [np.array(interface[k]) for k in ['Phi12', 'C3x12', 'Gamma12', 'B3x12']]
    with np.load(Path(manifests[0]['local_only_arrays'][0]['path']), allow_pickle=False) as a:
        t, ag, om, s0, v0, Z, ZD, W, WD = [a[k].copy() for k in ['t', 'ag_in_s2', 'omega', 's_unit', 'sdot_unit', 'z_unit', 'zdot_unit', 'w_unit', 'wdot_unit']]
        pred = {(z, o): a[f'z{z:g}_order{o}_shear_kip'].copy() for z in [.06, .07, .08, .10] for o in [1, 2]}
        Vbase_saved = a['baseline_shear_kip'].copy()
    with np.load(Path(manifests[0]['local_only_arrays'][1]['path']), allow_pickle=False) as a:
        E = {(z, o): a[f'z{z:g}_order{o}_E_kip'].copy() for z in [.06, .07, .08, .10] for o in [1, 2]}
    record = Path(next(d['path'] for d in rules['inputs'] if d['path'].endswith('.AT2')))
    rawlines = record.read_text(encoding='ascii').splitlines()
    raw = np.array([float(v) for line in rawlines[4:] for v in line.split()])
    assert len(raw) == 7802 and np.array_equal(raw * 386.4, ag) and np.array_equal(t, np.arange(7802) * .005)
    assert abs(t[-1] - 39.005) < 1e-12 and abs(np.max(abs(raw)) - .1433283) < 1e-12
    vbase = ((s0 * G) @ phi.T) @ C.T; p0 = np.max(abs(vbase), 0); i0 = np.argmax(abs(vbase), 0)
    maxphysical = float(np.max(abs(vbase - Vbase_saved)))
    for z in [.06, .07, .08, .10]:
        for o in [1, 2]:
            sh = s0 + (z - .05) * Z + ((z - .05) ** 2 * W / 2 if o == 2 else 0)
            vv = ((sh * G) @ phi.T) @ C.T
            maxphysical = max(maxphysical, float(np.max(abs(vv - pred[z, o]))))
    target = {}
    for d in manifests[1]['local_only_arrays']:
        with np.load(Path(d['path']), allow_pickle=False) as a:
            assert np.array_equal(a['ag_in_s2'], ag) and np.array_equal(a['t'], t) and np.array_equal(a['omega'], om)
            ss, vs, saved = a['s_unit'].copy(), a['sdot_unit'].copy(), a['shear_kip'].copy()
        vc = ((ss * G) @ phi.T) @ C.T
        maxphysical = max(maxphysical, float(np.max(abs(vc - saved))))
        target[d['target_zeta']] = (ss, vs, saved)
    # Fixed low/mid/high mode selection, independent of observed prediction errors.
    selected = np.array([0, 5, 11]); coarse = integrate(ag, om[selected], 16); fine = integrate(ag, om[selected], 32)
    baseline_states = np.stack([s0[:, selected], v0[:, selected], Z[:, selected], ZD[:, selected], W[:, selected], WD[:, selected]], axis=2)
    rkrows = []
    for i, mode in enumerate(selected + 1):
        for col, label in enumerate(['s', 'sdot', 'z', 'zdot', 'w', 'wdot']):
            exact = baseline_states[:, i, col]; ec = np.linalg.norm(coarse[:, i, col] - exact); ef = np.linalg.norm(fine[:, i, col] - exact)
            rkrows.append({'zeta': .05, 'Mode': int(mode), 'state': label, 'RK32_relative_L2_error': float(ef / np.linalg.norm(exact)), 'RK16_to_RK32_error_ratio': float(ec / ef)})
        for col, label in [(0, 's'), (1, 'sdot')]:
            exact = target[.10][col][:, mode - 1]; ec = np.linalg.norm(coarse[:, i + 3, col] - exact); ef = np.linalg.norm(fine[:, i + 3, col] - exact)
            rkrows.append({'zeta': .10, 'Mode': int(mode), 'state': label, 'RK32_relative_L2_error': float(ef / np.linalg.norm(exact)), 'RK16_to_RK32_error_ratio': float(ec / ef)})
    tables = {name: rd(Q / name) for name in ['exact-reference-floor-peaks-12.csv', 'frozen-prediction-vs-reference-24.csv', 'interval-coverage-width-decisions-24.csv', 'candidate-v001-v002-decision-validation-8.csv']}
    old = rd(Q / 'old-time-first-order-comparison-12.csv')
    maxdiff = 0.; fieldchecks = 0
    def compare(row, vals):
        nonlocal maxdiff, fieldchecks
        for k, val in vals.items():
            fieldchecks += 1
            if isinstance(val, (bool, np.bool_)): assert row[k] == str(bool(val)), (k, val, row[k])
            elif isinstance(val, str): assert row[k] == val, (k, val, row[k])
            else:
                error = abs(float(val) - float(row[k])); maxdiff = max(maxdiff, error)
                assert error < 1e-7, (k, val, row[k])
    rows = []; references = []; strict_uncovered = 0
    for z, (ss, vs, truth) in target.items():
        pt = np.max(abs(truth), 0); it = np.argmax(abs(truth), 0); dt = 1 - pt / p0
        for j in range(3):
            st = f'Story{j + 1}'; ref = {'baseline_peak_kip': p0[j], 'reference_abs_peak_kip': pt[j],
                'reference_signed_value_at_abs_peak_kip': truth[it[j], j], 'reference_min_signed_kip': np.min(truth[:, j]),
                'reference_max_signed_kip': np.max(truth[:, j]), 'reference_peak_time_s': t[it[j]],
                'reference_D': dt[j], 'reference_decrease_percent': 100 * dt[j], 'true_insufficient': dt[j] < .10, 'true_adverse': dt[j] < 0}
            compare(next(d for d in tables['exact-reference-floor-peaks-12.csv'] if float(d['target_zeta']) == z and d['Story'] == st), ref)
            references.append({'zeta': z, 'Story': st, 'Dtrue': float(dt[j]), 'signed_peak': float(truth[it[j], j])})
            oldp = abs(pred[z, 1][i0[j], j]); oldD = 1 - oldp / p0[j]
            compare(next(d for d in old if float(d['target_zeta']) == z and d['Story'] == st), {
                'old_peak_time_s': t[i0[j]], 'old_time_abs_first_order_value_kip': oldp, 'reference_peak_kip': pt[j],
                'reference_D': dt[j], 'old_time_D': oldD, 'peak_relative_error': oldp / pt[j] - 1,
                'miss_insufficient': dt[j] < .1 <= oldD, 'false_insufficient': oldD < .1 <= dt[j],
                'true_adverse': dt[j] < 0, 'miss_adverse': dt[j] < 0 <= oldD, 'false_adverse': oldD < 0 <= dt[j]})
            for o in [1, 2]:
                phcurve = pred[z, o][:, j]; ih = np.argmax(abs(phcurve)); ph = abs(phcurve[ih]); dh = 1 - ph / p0[j]
                err = ph / pt[j] - 1; curveerr = abs(phcurve - truth[:, j]); ee = E[z, o][:, j]
                lo = max(0., float(np.max(abs(phcurve) - ee))); up = float(np.max(abs(phcurve) + ee))
                dl, du = 1 - up / p0[j], 1 - lo / p0[j]; width = du - dl
                decision = 'meets' if dl >= .1 else ('insufficient' if du < .1 else 'uncertain')
                vals = {'baseline_peak_kip': p0[j], 'predicted_peak_kip': ph, 'predicted_signed_value_at_abs_peak_kip': phcurve[ih],
                    'reference_peak_kip': pt[j], 'reference_signed_value_at_abs_peak_kip': truth[it[j], j],
                    'peak_relative_error': err, 'absolute_peak_relative_error': abs(err), 'predicted_D': dh, 'reference_D': dt[j],
                    'D_error_percentage_points': 100 * (dh - dt[j]), 'predicted_peak_time_s': t[ih], 'reference_peak_time_s': t[it[j]],
                    'peak_time_error_s': t[ih] - t[it[j]], 'signed_curve_NRMSE': np.linalg.norm(phcurve - truth[:, j]) / np.linalg.norm(truth[:, j]),
                    'curve_sup_error_kip': np.max(curveerr), 'true_insufficient': dt[j] < .1,
                    'point_miss_insufficient': dt[j] < .1 <= dh, 'point_false_insufficient': dh < .1 <= dt[j],
                    'true_adverse': dt[j] < 0, 'point_miss_adverse': dt[j] < 0 <= dh, 'point_false_adverse': dh < 0 <= dt[j]}
                compare(next(d for d in tables['frozen-prediction-vs-reference-24.csv'] if float(d['target_zeta']) == z and int(d['Taylor_order']) == o and d['Story'] == st), vals)
                mask = abs(phcurve) + ee >= lo; gap = curveerr - ee; strict_uncovered += int(np.count_nonzero(gap > 0))
                iv = {'P0_kip': p0[j], 'Phat_kip': ph, 'P_lower_kip': lo, 'P_upper_kip': up, 'D_lower': dl, 'D_upper': du,
                    'D_width': width, 'decision_status': decision, 'width_status': 'too_wide' if width > .05 else 'acceptable',
                    'v001_operational_recompute': decision == 'uncertain' or width > .05, 'max_discrete_E_kip': np.max(ee),
                    'reference_peak_kip': pt[j], 'reference_D': dt[j], 'peak_covered': lo <= pt[j] <= up,
                    'curve_covered_all_samples_strict': np.all(gap <= 0), 'curve_covered_all_samples_tolerance1e8': np.all(gap <= 1e-8),
                    'strict_uncovered_samples': np.count_nonzero(gap > 0), 'max_error_minus_envelope_kip': np.max(gap),
                    'true_peak_time_in_potential_regions': mask[it[j]], 'true_insufficient': dt[j] < .1, 'true_adverse': dt[j] < 0,
                    'insufficient_action_miss': dt[j] < .1 and decision == 'meets', 'false_insufficient': dt[j] >= .1 and decision == 'insufficient',
                    'adverse_action_miss': dt[j] < 0 and decision == 'meets', 'adverse_risk_miss': dt[j] < 0 and dl >= 0}
                compare(next(d for d in tables['interval-coverage-width-decisions-24.csv'] if float(d['target_zeta']) == z and int(d['Taylor_order']) == o and d['Story'] == st), iv)
                rows.append({'zeta': z, 'order': o, 'Story': st, **vals, **iv})
    decisions = []
    for z in [.06, .07, .08, .10]:
        for o in [1, 2]:
            rr = [d for d in rows if d['zeta'] == z and d['order'] == o]
            action = 'reject' if any(d['decision_status'] == 'insufficient' for d in rr) else ('pass' if all(d['decision_status'] == 'meets' and d['width_status'] == 'acceptable' for d in rr) else 'recompute')
            truthpass = all(d['reference_D'] >= .1 for d in rr); anyadverse = any(d['true_adverse'] for d in rr)
            vals = {'v002_candidate_action': action, 'v001_flagged_floors': sum(d['v001_operational_recompute'] for d in rr),
                'v001_building_recompute': int(any(d['v001_operational_recompute'] for d in rr)), 'v002_building_recompute': int(action == 'recompute'),
                'meets_floors': sum(d['decision_status'] == 'meets' for d in rr), 'insufficient_floors': sum(d['decision_status'] == 'insufficient' for d in rr),
                'uncertain_floors': sum(d['decision_status'] == 'uncertain' for d in rr), 'true_all3_meet': truthpass,
                'true_any_floor_adverse': anyadverse, 'v002_false_pass': not truthpass and action == 'pass', 'v002_false_reject': truthpass and action == 'reject',
                'v002_adverse_missed_pass': anyadverse and action == 'pass', 'reference_min_floor_D': min(d['reference_D'] for d in rr),
                'reference_max_floor_D': max(d['reference_D'] for d in rr)}
            compare(next(d for d in tables['candidate-v001-v002-decision-validation-8.csv'] if float(d['target_zeta']) == z and int(d['Taylor_order']) == o), vals)
            decisions.append({'zeta': z, 'order': o, **vals})
    # Fair cost reconstruction: actual measured components, not a new timing experiment.
    directrows = rd(Q / 'complete-candidate-measured-cost-4.csv'); replay = rd(Q / 'per-candidate-frozen-pipeline-replay-cost-8.csv')
    fair = rd(Q / 'fair-pipeline-cost-including-baseline-output-4.csv'); costchecks = []
    byz = {float(d['target_zeta']): float(d['complete_candidate_core_seconds']) for d in directrows}
    for d in directrows:
        assert abs(sum(float(d[k]) for k in ['state_solve_seconds', 'elastic_output_projection_seconds', 'peak_and_decision_metrics_seconds']) - float(d['complete_candidate_core_seconds'])) < 1e-12
    for d in fair:
        o = int(d['Taylor_order']); policy = d['policy']
        rr = [v for v in decisions if v['order'] == o]; needed = [v['zeta'] for v in rr if v[policy + '_building_recompute']]
        core = sum(float(v['candidate_prediction_core_seconds']) for v in replay if int(v['Taylor_order']) == o)
        conditional = sum(byz[z] for z in needed)
        prep = sum(float(d[k]) for k in ['common_input_preparation_seconds', 'baseline_state_seconds', 'derivative_coefficient_setup_seconds', 'first_derivative_seconds', 'second_derivative_seconds', 'baseline_output_and_peak_seconds'])
        total = prep + core + conditional; direct = float(d['common_input_preparation_seconds']) + sum(byz.values())
        compare(d, {'triggered_building_solves': len(needed), 'all4_candidate_prediction_and_bound_seconds': core,
            'triggered_complete_analysis_measured_seconds': conditional, 'total_measured_component_seconds': total,
            'direct4_complete_core_plus_commonprep_seconds': direct, 'method_to_direct_cost_ratio': total / direct})
        costchecks.append({'order': o, 'policy': policy, 'cost_total_s': total, 'direct_total_s': direct, 'ratio': total / direct})
    misses = [d for d in rows if d['point_miss_insufficient']]; falsead = [d for d in rows if d['point_false_adverse']]
    worse = []
    for ref in references:
        pair = [next(d for d in rows if d['zeta'] == ref['zeta'] and d['Story'] == ref['Story'] and d['order'] == o) for o in [1, 2]]
        if pair[1]['absolute_peak_relative_error'] > pair[0]['absolute_peak_relative_error']: worse.append((ref['zeta'], ref['Story']))
    assert len(misses) == 1 and (misses[0]['zeta'], misses[0]['order'], misses[0]['Story']) == (.08, 2, 'Story3')
    assert len(falsead) == 4 and len(worse) == 2 and strict_uncovered == 0
    wr('independent-selected-RK4-checks-24.csv', rkrows); wr('independent-candidate-decisions-8.csv', decisions)
    wr('independent-cost-checks-4.csv', costchecks)
    wr('independent-point-failure-checks-5.csv', [{k: d[k] for k in ['zeta', 'order', 'Story', 'predicted_D', 'reference_D', 'point_miss_insufficient', 'point_false_adverse', 'decision_status']} for d in misses + falsead])
    result = {'upstream_file_counts_verified': [len(m['files']) for m in manifests], 'all6_cached_arrays_hash_verified': True,
        'record_sha256': sha(record), 'record_samples': len(raw), 'dt_s': .005, 'last_time_s': float(t[-1]),
        'raw_PGA_g': float(np.max(abs(raw))), 'ag_equals_raw_times_386_4': True,
        'selected_modes_fixed_low_mid_high': [1, 6, 12], 'RK_substeps': [16, 32],
        'RK32_max_relative_L2_error': max(d['RK32_relative_L2_error'] for d in rkrows),
        'RK_refinement_min_ratio': min(d['RK16_to_RK32_error_ratio'] for d in rkrows),
        'physical_C_Phi_Gamma_max_abs_difference_kip': maxphysical, 'field_checks': fieldchecks, 'max_small_table_difference': maxdiff,
        'strict_curve_uncovered_samples': strict_uncovered, 'point_insufficient_miss_count': len(misses),
        'point_false_adverse_count': len(falsead), 'second_order_worse_pairs': worse,
        'true_adverse_cases': sum(d['Dtrue'] < 0 for d in references), 'adverse_miss_rate': None,
        'v002_reject_count_order1': sum(d['order'] == 1 and d['v002_candidate_action'] == 'reject' for d in decisions),
        'v002_reject_count_order2': sum(d['order'] == 2 and d['v002_candidate_action'] == 'reject' for d in decisions),
        'all_fair_component_ratios_exceed_one': all(d['ratio'] > 1 for d in costchecks),
        'new_all12_target_solves': 0, 'new_selected_target_zeta': .10,
        'audit_scope': 'selected low/mid/high augmented states and one candidate independently integrated; physical output/all24 coverage/decisions/cost recomputed; no complete new ODE production'}
    assert result['RK32_max_relative_L2_error'] < 1e-5 and result['RK_refinement_min_ratio'] > 14
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
