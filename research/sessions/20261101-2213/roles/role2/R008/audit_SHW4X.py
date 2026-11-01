"""Independent new-input derivative/target subset, all metrics and rank audit."""
from pathlib import Path
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent; S = O.parents[2]; P = S / 'roles/role4/R007'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rd(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def wr(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def integrate(ag, omega, subdivisions):
    om = np.r_[omega, omega]; zz = np.r_[np.full(3, .05), np.full(3, .07)]; deriv = np.r_[np.ones(3), np.zeros(3)]
    x = np.zeros((6, 6)); history = np.zeros((len(ag), 6, 6)); h = .02 / subdivisions
    def f(v, a):
        out = np.empty_like(v); out[:, 0::2] = v[:, 1::2]
        out[:, 1] = -om ** 2 * v[:, 0] - 2 * zz * om * v[:, 1] - a
        out[:, 3] = -om ** 2 * v[:, 2] - 2 * zz * om * v[:, 3] - 2 * om * v[:, 1] * deriv
        out[:, 5] = -om ** 2 * v[:, 4] - 2 * zz * om * v[:, 5] - 4 * om * v[:, 3] * deriv
        return out
    for n in range(len(ag) - 1):
        da = ag[n + 1] - ag[n]
        for j in range(subdivisions):
            a0 = ag[n] + da * j / subdivisions; am = ag[n] + da * (j + .5) / subdivisions; a1 = ag[n] + da * (j + 1) / subdivisions
            k1 = f(x, a0); k2 = f(x + h * k1 / 2, am); k3 = f(x + h * k2 / 2, am); k4 = f(x + h * k3, a1)
            x += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        history[n + 1] = x
    return history


def main():
    assert not (O / 'results.json').exists()
    man = json.loads((P / 'delivery-manifest.json').read_text()); rules = json.loads((P / 'input-method-freeze.json').read_text())
    for d in man['files'] + man['local_only_arrays']:
        p = Path(d['path']); assert sha(p) == d['sha256'] and p.stat().st_size == d['bytes']
    for d in rules['inputs']: assert sha(Path(d['path'])) == d['sha256']
    with np.load(Path(rules['inputs'][0]['path']), allow_pickle=False) as a:
        t, ag, om, B, s0, v0 = [a[k].copy() for k in ['t', 'ag', 'omega', 'B_direct', 's_unitGamma', 'sdot_unitGamma']]
    with np.load(Path(man['local_only_arrays'][0]['path']), allow_pickle=False) as a:
        assert all(np.array_equal(v, a[k]) for v, k in [(t, 't'), (ag, 'ag'), (om, 'omega'), (B, 'B'), (s0, 's0'), (v0, 'v0')])
        Z, ZD, W, WD = [a[k].copy() for k in ['Z', 'ZD', 'W', 'WD']]
        pred = {(z, o): a[f'z{z:g}_order{o}_V'].copy() for z in [.06, .07] for o in [1, 2]}
        E = {(z, o): a[f'z{z:g}_order{o}_E'].copy() for z in [.06, .07] for o in [1, 2]}
    assert len(t) == 2951 and t[0] == 0 and t[-1] == 59 and np.max(abs(np.diff(t) - .02)) < 1e-9
    assert abs(np.max(abs(ag)) - .35) < 1e-12 and np.all(s0[0] == 0) and np.all(v0[0] == 0)
    shw3rule = json.loads((S / 'roles/role4/R001/input-prediction-rules-freeze.json').read_text())
    with np.load(Path(shw3rule['inputs'][0]['path']), allow_pickle=False) as a:
        assert np.array_equal(om, a['omega']) and np.array_equal(B, a['B_direct'])
    target = {}
    for d in man['local_only_arrays'][1:]:
        with np.load(Path(d['path']), allow_pickle=False) as a:
            assert all(np.array_equal(v, a[k]) for v, k in [(t, 't'), (ag, 'ag'), (om, 'omega'), (B, 'B')])
            target[d['target_zeta']] = tuple(a[k].copy() for k in ['s', 'v', 'V'])
    sel = np.array([1, 9, 12]); coarse = integrate(ag, om[sel], 8); fine = integrate(ag, om[sel], 16)
    saved = np.stack([s0[:, sel], v0[:, sel], Z[:, sel], ZD[:, sel], W[:, sel], WD[:, sel]], axis=2)
    rkrows = []
    for i, mode in enumerate(sel + 1):
        for col, label in enumerate(['s', 'sdot', 'z', 'zdot', 'w', 'wdot']):
            a = saved[:, i, col]; ec = np.linalg.norm(coarse[:, i, col] - a); ef = np.linalg.norm(fine[:, i, col] - a)
            rkrows.append({'zeta': .05, 'Mode': int(mode), 'state': label, 'RK16_relative_L2_error': float(ef / np.linalg.norm(a)), 'RK8_to_RK16_ratio': float(ec / ef)})
        for col, label in [(0, 's'), (1, 'sdot')]:
            a = target[.07][col][:, mode - 1]; ec = np.linalg.norm(coarse[:, i + 3, col] - a); ef = np.linalg.norm(fine[:, i + 3, col] - a)
            rkrows.append({'zeta': .07, 'Mode': int(mode), 'state': label, 'RK16_relative_L2_error': float(ef / np.linalg.norm(a)), 'RK8_to_RK16_ratio': float(ec / ef)})
    fields = 0; maxdiff = 0.
    def check(d, vals):
        nonlocal fields, maxdiff
        for k, v in vals.items():
            fields += 1
            if isinstance(v, (bool, np.bool_)): assert d[k] == str(bool(v)), (k, v, d[k])
            elif isinstance(v, str): assert d[k] == v, (k, v, d[k])
            else:
                e = abs(float(v) - float(d[k])); maxdiff = max(maxdiff, e); assert e < 1e-7, (k, v, d[k])
    V0 = np.einsum('tr,jr->tj', s0, B * om ** 2 / 1000, optimize=False)
    VZ = np.einsum('tr,jr->tj', Z, B * om ** 2 / 1000, optimize=False)
    p0 = np.max(abs(V0), 0); sourceS = {d['Story']: d for d in rd(P / 'baseline-S-ranked-floors-12.csv')}
    sourceC = {(d['Story'], int(d['controller_number']), int(d['Mode'])): d for d in rd(P / 'all-mode-signed-S-sources-3600.csv')}
    floors = []; maxclose = 0.
    for j in range(12):
        st = f'Story{j + 1}'; active = np.flatnonzero(abs(V0[:, j]) == p0[j]); g = np.sign(V0[:, j]) * VZ[:, j]
        prime = max(g[active]); control = active[g[active] == prime]; assert len(control) == 1
        n = int(control[0]); c = -np.sign(V0[n, j]) * B[j] * om ** 2 * Z[n] / (1000 * p0[j]); sval = -prime / p0[j]
        order = sorted(range(300), key=lambda i: (-abs(c[i]), i)); maxclose = max(maxclose, float(abs(np.sum(c) - sval)))
        check(sourceS[st], {'P0_kN': p0[j], 'exact_active_count': len(active), 'right_controller_count': len(control),
            'controller_indices': str(n), 'Pprime_right_kN_per_zeta': prime, 'S_percent_per_damping_pp': sval, 'force_rate_kN_per_damping_pp': .01 * prime})
        for rank, m in enumerate(order, 1): check(sourceC[st, 1, m + 1], {'time_s': t[n], 'abs_c_rank': rank, 'c_improvement_percent_per_damping_pp': c[m]})
        floors.append({'Story': st, 'S': float(sval), 'baseline_rank': 0, 'control_time_s': float(t[n]), 'mode13_c': float(c[12]),
            'promoting_sum': float(np.sum(c[c > 0])), 'opposing_sum': float(np.sum(c[c < 0])), 'top5_rest_sum': float(np.sum(c[order[5:]]))})
    for d in floors:
        d['baseline_rank'] = 1 + sum(v['S'] < d['S'] for v in floors); check(sourceS[d['Story']], {'slow_improvement_rank': d['baseline_rank']})
    comparisons = rd(P / 'prediction-vs-reference-48.csv'); intervals = rd(P / 'interval-coverage-and-decision-validation-48.csv')
    truthrows = rd(P / 'exact-reference-floor-peaks-24.csv'); candsource = rd(P / 'candidate-decision-validation-4.csv')
    computed = []; refs = []; candidates = []; inversepairs = []; ranks = []; strict_uncovered = 0; maxproject = 0.; maxpred = 0.
    for z, (ss, vs, vt) in target.items():
        maxproject = max(maxproject, float(np.max(abs((ss * om ** 2) @ B.T / 1000 - vt))))
        pt = np.max(abs(vt), 0); it = np.argmax(abs(vt), 0); dt = 1 - pt / p0
        for o in [1, 2]:
            sh = s0 + (z - .05) * Z + ((z - .05) ** 2 * W / 2 if o == 2 else 0)
            maxpred = max(maxpred, float(np.max(abs((sh * om ** 2) @ B.T / 1000 - pred[z, o]))))
        for j in range(12):
            st = f'Story{j + 1}'; refs.append({'zeta': z, 'Story': st, 'Dtrue': float(dt[j])})
            check(next(d for d in truthrows if float(d['target_zeta']) == z and d['Story'] == st), {'P0_kN': p0[j], 'reference_peak_kN': pt[j],
                'reference_D': dt[j], 'reference_signed_peak_kN': vt[it[j], j], 'reference_peak_time_s': t[it[j]],
                'reference_signed_min_kN': np.min(vt[:, j]), 'reference_signed_max_kN': np.max(vt[:, j])})
            for o in [1, 2]:
                vh = pred[z, o][:, j]
                ih = np.argmax(abs(vh)); ph = abs(vh[ih]); dh = 1 - ph / p0[j]; er = ph / pt[j] - 1; gap = abs(vh - vt[:, j]) - E[z, o][:, j]
                strict_uncovered += int(np.count_nonzero(gap > 0))
                pv = {'P0_kN': p0[j], 'Phat_kN': ph, 'predicted_D': dh, 'predicted_signed_peak_kN': vh[ih], 'predicted_peak_time_s': t[ih],
                    'reference_peak_kN': pt[j], 'reference_D': dt[j], 'reference_signed_peak_kN': vt[it[j], j], 'reference_peak_time_s': t[it[j]],
                    'peak_relative_error': er, 'absolute_peak_relative_error': abs(er), 'D_error_pp': 100 * (dh - dt[j]),
                    'curve_signed_NRMSE': np.linalg.norm(vh - vt[:, j]) / np.linalg.norm(vt[:, j]),
                    'point_miss_insufficient': dt[j] < .1 <= dh, 'point_false_insufficient': dh < .1 <= dt[j],
                    'true_adverse': dt[j] < 0, 'point_miss_adverse': dt[j] < 0 <= dh, 'point_false_adverse': dh < 0 <= dt[j]}
                check(next(d for d in comparisons if float(d['target_zeta']) == z and int(d['Taylor_order']) == o and d['Story'] == st), pv)
                lo = max(0., float(np.max(abs(vh) - E[z, o][:, j]))); up = float(np.max(abs(vh) + E[z, o][:, j]))
                dl, du = 1 - up / p0[j], 1 - lo / p0[j]; width = du - dl
                dec = 'meets' if dl >= .1 else ('insufficient' if du < .1 else 'uncertain')
                iv = {'P0_kN': p0[j], 'P_lower_kN': lo, 'P_upper_kN': up, 'D_lower': dl, 'D_upper': du, 'D_width': width,
                    'decision_status': dec, 'width_status': 'too_wide' if width > .05 else 'acceptable', 'v001_recompute': dec == 'uncertain' or width > .05,
                    'max_E_kN': np.max(E[z, o][:, j]), 'reference_D': dt[j], 'reference_peak_kN': pt[j], 'peak_covered': lo <= pt[j] <= up,
                    'curve_covered_strict': np.max(gap) <= 0, 'strict_uncovered_samples': np.count_nonzero(gap > 0), 'max_error_minus_envelope_kN': np.max(gap),
                    'insufficient_action_miss': dt[j] < .1 and dec == 'meets', 'false_insufficient': dt[j] >= .1 and dec == 'insufficient',
                    'adverse_action_miss': dt[j] < 0 and dec == 'meets', 'adverse_risk_miss': dt[j] < 0 and dl >= 0}
                check(next(d for d in intervals if float(d['target_zeta']) == z and int(d['Taylor_order']) == o and d['Story'] == st), iv)
                computed.append({'zeta': z, 'order': o, 'Story': st, **pv, **iv})
        for o in [1, 2]:
            rr = [d for d in computed if d['zeta'] == z and d['order'] == o]
            action = 'reject' if any(d['decision_status'] == 'insufficient' for d in rr) else ('pass' if all(d['decision_status'] == 'meets' and d['width_status'] == 'acceptable' for d in rr) else 'recompute')
            truthpass = bool(np.all(dt >= .1)); adverse = bool(np.any(dt < 0)); flagged = sum(d['v001_recompute'] for d in rr)
            vals = {'v002_action': action, 'v001_flagged_floors': int(flagged), 'v001_building_recompute': int(flagged > 0), 'v002_building_recompute': int(action == 'recompute'),
                'true_all12_meet': truthpass, 'true_any_adverse': adverse, 'false_pass': not truthpass and action == 'pass', 'false_reject': truthpass and action == 'reject', 'adverse_missed_pass': adverse and action == 'pass'}
            check(next(d for d in candsource if float(d['target_zeta']) == z and int(d['Taylor_order']) == o), vals)
            candidates.append({'zeta': z, 'order': o, **vals})
        dv = {f'Story{j + 1}': dt[j] for j in range(12)}
        for i, a in enumerate(floors):
            for b in floors[i + 1:]:
                if (a['S'] - b['S']) * (dv[a['Story']] - dv[b['Story']]) < 0:
                    slow, fast = (a, b) if a['S'] < b['S'] else (b, a)
                    inversepairs.append({'target_zeta': z, 'baseline_slower_floor': slow['Story'], 'baseline_faster_floor': fast['Story'],
                        'S_slower': slow['S'], 'S_faster': fast['S'], 'reference_D_of_baseline_slower': float(dv[slow['Story']]), 'reference_D_of_baseline_faster': float(dv[fast['Story']])})
        base_rank = np.array([d['baseline_rank'] for d in floors]); ref_rank = np.array([1 + sum(v < dv[d['Story']] for v in dv.values()) for d in floors])
        rho = float(np.corrcoef(base_rank, ref_rank)[0, 1]); count = sum(d['target_zeta'] == z for d in inversepairs)
        check(next(d for d in rd(P / 'posterior-rank-validation-2.csv') if float(d['target_zeta']) == z), {
            'strict_inversions': count, 'Spearman_no_ties_rho': rho, 'baseline_slowest': min(floors, key=lambda d: d['S'])['Story'],
            'reference_slowest': min(dv, key=dv.get), 'Story5_reference_rank': int(ref_rank[4])})
        ranks.append({'target_zeta': z, 'inversions': count, 'rho': rho, 'baseline_first': min(floors, key=lambda d: d['S'])['Story'], 'true_first': min(dv, key=dv.get)})
    pairsource = rd(P / 'posterior-rank-inversion-pairs-3.csv')
    for row in inversepairs:
        check(next(d for d in pairsource if float(d['target_zeta']) == row['target_zeta'] and d['baseline_slower_floor'] == row['baseline_slower_floor'] and d['baseline_faster_floor'] == row['baseline_faster_floor']), row)
    misses = [d for d in computed if d['point_miss_insufficient']]
    assert len(misses) == 2 and all(d['zeta'] == .07 and d['order'] == 1 and d['decision_status'] != 'meets' for d in misses)
    assert strict_uncovered == 0 and len(inversepairs) == 3
    wr('independent-RK4-checks-24.csv', rkrows); wr('independent-S-floors-12.csv', floors); wr('independent-rank-inversions-3.csv', inversepairs)
    wr('independent-rank-summary-2.csv', ranks); wr('independent-candidate-actions-4.csv', candidates)
    wr('independent-point-misses-2.csv', [{k: d[k] for k in ['zeta', 'order', 'Story', 'predicted_D', 'reference_D', 'decision_status', 'v001_recompute']} for d in misses])
    result = {'upstream_files_SHA_verified': len(man['files']), 'local_arrays_SHA_verified': len(man['local_only_arrays']), 'input_SHA_verified': len(rules['inputs']),
        'source_baseline_SHA': sha(Path(rules['inputs'][0]['path'])), 'record_points': len(t), 'nominal_dt_s': .02, 'record_end_s': float(t[-1]), 'cached_ag_PGA_m_s2': float(np.max(abs(ag))),
        'omega_B_identical_SHW3X': True, 'selected_modes': [2, 10, 13], 'RK_substeps': [8, 16],
        'RK16_max_relative_L2_error': max(d['RK16_relative_L2_error'] for d in rkrows), 'RK_refinement_min_ratio': min(d['RK8_to_RK16_ratio'] for d in rkrows),
        'new_independent_selected_target_zeta': .07, 'new_all300_target_production': 0,
        'S_floors': len(floors), 'modal_contributions_checked': len(sourceC), 'max_c_closure_error': maxclose,
        'field_checks': fields, 'max_numeric_difference': maxdiff, 'prediction_projection_max_difference_kN': maxpred, 'target_projection_max_difference_kN': maxproject,
        'strict_curve_uncovered_samples': strict_uncovered, 'point_miss_count': len(misses), 'rank_inversion_count': len(inversepairs),
        'baseline_first_wrong_at_6pct': ranks[0]['baseline_first'] != ranks[0]['true_first'],
        'true_adverse_count': sum(d['Dtrue'] < 0 for d in refs), 'adverse_miss_rate': None,
        'scope': 'new input known historically; baseline5 reused, 6/7 predictions frozen before reference; ranking not guaranteed; grid calculation envelope not strict FP/continuous certificate'}
    assert result['RK16_max_relative_L2_error'] < 1e-6 and result['RK_refinement_min_ratio'] > 15
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
