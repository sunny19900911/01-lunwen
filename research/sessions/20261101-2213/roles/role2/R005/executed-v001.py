"""Independent positive convolution and stored-envelope classification audit."""
from pathlib import Path
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent
S = O.parents[2]
P = S / 'roles/role4'
Q = P / 'R003'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rd(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def wr(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def transition(omega, zeta, h):
    """Generic spectral matrix exponential and exact ramp-input moments."""
    F = np.zeros((300, 2, 2)); F[:, 0, 1] = 1.
    F[:, 1, 0] = -omega ** 2; F[:, 1, 1] = -2 * zeta * omega
    val, vec = np.linalg.eig(F)
    A = ((vec * np.exp(val * h)[:, None, :]) @ np.linalg.inv(vec)).real
    unitforce = np.tile([0., -1.], (300, 1))
    identity = np.eye(2)[None]
    m0 = np.linalg.solve(F, np.einsum('mij,mj->mi', A - identity, unitforce)[..., None])[..., 0]
    m1 = np.linalg.solve(F, np.linalg.solve(F,
        np.einsum('mij,mj->mi', A - identity - F * h, unitforce)[..., None]))[..., 0]
    return A, m0, m1


def main():
    assert not (O / 'results.json').exists()
    manifest = json.loads((Q / 'delivery-manifest.json').read_text())
    method = json.loads((Q / 'method-and-inputs-freeze.json').read_text())
    for d in manifest['files'] + manifest['local_only_arrays']:
        p = Path(d['path']); assert p.stat().st_size == d['bytes'] and sha(p) == d['sha256']
    for d in method['inputs']: assert sha(Path(d['path'])) == d['sha256']
    with np.load(Path(method['inputs'][0]['path']), allow_pickle=False) as a:
        t, ag, om, B, s0, v0 = [a[k].copy() for k in ['t', 'ag', 'omega', 'B_direct', 's_unitGamma', 'sdot_unitGamma']]
    with np.load(Path(method['inputs'][1]['path']), allow_pickle=False) as a:
        Z, ZD, W, WD = [a[k].copy() for k in ['z_unit', 'zdot_unit', 'w_unit', 'wdot_unit']]
        pred = {(z, order): a[f'z{z:g}_order{order}_shear_inertia_kN'].copy() for z in [.06, .07, .08, .10] for order in [1, 2]}
    with np.load(Path(manifest['local_only_arrays'][0]['path']), allow_pickle=False) as a:
        savedE = {(z, order): a[f'z{z:g}_order{order}_story_E_kN'].copy() for z in [.06, .07, .08, .10] for order in [1, 2]}
        savedq = {(z, order): a[f'z{z:g}_order{order}_selected_modes_2_10_13_Q_m'].copy() for z in [.06, .07, .08, .10] for order in [1, 2]}
    N = len(t); h = float(np.median(np.diff(t))); eps = np.finfo(float).eps
    selected = [1, 9, 12]  # fixed in code before any target response is read
    times = [0, 1, 100, N // 2, N - 1]
    coeff = abs(B) * om ** 2 / 1000
    slope = np.diff(ag) / h; V0 = (s0 * om ** 2) @ B.T / 1000; p0 = np.max(abs(V0), 0)
    selectedrows = []; timerows = []; lagrows = []; guardrows = []
    maxnominal = 0.
    for z in [.06, .07, .08, .10]:
        A, m0, m1 = transition(om, z, h)
        Anom, _, _ = transition(om, z, .02)
        maxnominal = max(maxnominal, float(np.max(abs(A[:, 0, 0] - Anom[:, 0, 0]))),
                         float(np.max(abs((A[:, 0, 1] - Anom[:, 0, 1]) * om))))
        b = ag[:-1, None, None] * m0[None] + slope[:, None, None] * m1[None]
        # Full matrix powers before row extraction/absolute value; no scalar A11 powers.
        powers = np.tile(np.eye(2), (300, 1, 1)); kq = np.empty((N - 1, 300)); kv = np.empty_like(kq)
        for lag in range(N - 1):
            kq[lag] = abs(powers[:, 0, 0]); kv[lag] = abs(powers[:, 0, 1])
            powers = A @ powers
        alpha = z * om; beta = om * np.sqrt(1 - z ** 2); tau = np.arange(N - 1)[:, None] * h
        decay = np.exp(-tau * alpha); co = np.cos(tau * beta); si = np.sin(tau * beta) / beta
        # Add the producer's frozen engineering guard definitions, not an interval proof.
        kq += 128 * eps * decay * (abs(co) + abs(alpha * si) + 1)
        kv += 128 * eps * decay * (abs(si) + 1 / om)
        for order in [1, 2]:
            delta = z - .05
            s = s0 + delta * Z + (delta ** 2 * W / 2 if order == 2 else 0)
            v = v0 + delta * ZD + (delta ** 2 * WD / 2 if order == 2 else 0)
            x = np.stack([s, v], axis=2)
            defect = np.einsum('mij,nmj->nmi', A, x[:-1]) + b - x[1:]
            # The guard covers the actual particular-solution arithmetic used upstream.
            qp0 = -ag[:-1, None] / om ** 2 + 2 * alpha * slope[:, None] / om ** 4
            qp1 = -ag[1:, None] / om ** 2 + 2 * alpha * slope[:, None] / om ** 4
            vp = -slope[:, None] / om ** 2
            sq, sv = s[:-1] - qp0, v[:-1] - vp
            gq = 64 * eps * (abs(A[:, 0, 0] * sq) + abs(A[:, 0, 1] * sv) + abs(qp1) + abs(s[1:]))
            gv = 64 * eps * (abs(A[:, 1, 0] * sq) + abs(A[:, 1, 1] * sv) + abs(vp) + abs(v[1:]))
            aq = abs(defect[:, :, 0]) + gq; av = abs(defect[:, :, 1]) + gv
            fftg = 1e-12 * (kq.sum(0) * aq.sum(0) + kv.sum(0) * av.sum(0))
            for pos, m in enumerate(selected):
                direct = np.zeros(N)
                direct[1:] = (np.convolve(kq[:, m], aq[:, m]) + np.convolve(kv[:, m], av[:, m]))[:N - 1] + fftg[m]
                selectedrows.append({'zeta': z, 'order': order, 'Mode': m + 1,
                    'positive_direct_vs_saved_modal_Q_max_error_m': float(np.max(abs(direct - savedq[z, order][:, pos]))),
                    'max_modal_Q_m': float(np.max(direct)), 'FFT_guard_m': float(fftg[m])})
                # Unguarded first step: velocity defect has zero immediate displacement kernel.
                lagrows.append({'zeta': z, 'order': order, 'Mode': m + 1,
                    'raw_first_step_displacement': float(abs(defect[0, m, 0])),
                    'raw_first_step_velocity_multiplier': 0.,
                    'raw_second_step': float(abs(A[m, 0, 0]) * abs(defect[0, m, 0]) + abs(A[m, 0, 1]) * abs(defect[0, m, 1]) + abs(defect[1, m, 0]))})
            for n in times:
                if n == 0: modeenv = np.zeros(300)
                else:
                    modeenv = (kq[:n][::-1] * aq[:n] + kv[:n][::-1] * av[:n]).sum(0) + fftg
                storyenv = coeff @ modeenv
                timerows.append({'zeta': z, 'order': order, 'index': n, 'time_s': float(t[n]),
                    'all12_story_envelope_max_difference_kN': float(np.max(abs(storyenv - savedE[z, order][n]))),
                    'max_recomputed_story_E_kN': float(np.max(storyenv))})
            guardrows.append({'zeta': z, 'order': order, 'max_recomputed_FFT_guard_story_kN': float(np.max(coeff @ fftg))})
    # Only now read already-known target arrays for full stored-envelope coverage audit.
    raw = rd(Q / 'baseline-only-discrete-envelope-intervals-96.csv')
    evaluated = rd(Q / 'discrete-envelope-coverage-width-decisions-96.csv')
    summary = rd(Q / 'discrete-vs-coth-summary-8.csv')
    policy = json.loads((S / 'engineering-policy-freeze-v001.json').read_text())
    req, wl = policy['demonstration_Dreq'], policy['width_limit_D_fraction']
    rows = []; maxdiff = 0.; checks = 0; strict_uncovered = 0; max_uncovered = -np.inf
    def compare(d, values):
        nonlocal maxdiff, checks
        for k, v in values.items():
            checks += 1
            if isinstance(v, (bool, np.bool_)): assert d[k] == str(bool(v)), (k, v, d[k])
            elif isinstance(v, str): assert d[k] == v, (k, v, d[k])
            else:
                err = abs(float(v) - float(d[k])); maxdiff = max(maxdiff, err)
                assert err < 1e-7, (k, v, d[k])
    for item in json.loads((P / 'R002/reference-truth-array-index.json').read_text()):
        z = item['zeta']; path = Path(item['path']); assert sha(path) == item['sha256']
        with np.load(path, allow_pickle=False) as a: truth = a['shear_elastic_inertia_predicted_kN' if z == .08 else 'shear_elastic_inertia_kN'].copy()
        for order in [1, 2]:
            for j in range(12):
                st = f'Story{j + 1}'; d = next(d for d in raw if float(d['target_zeta']) == z and int(d['Taylor_order']) == order and d['Story'] == st)
                de = next(d for d in evaluated if float(d['target_zeta']) == z and int(d['Taylor_order']) == order and d['Story'] == st)
                E = savedE[z, order][:, j]; vh = abs(pred[z, order][:, j]); lo = max(0., float(np.max(vh - E))); up = float(np.max(vh + E))
                dl, du = 1 - up / p0[j], 1 - lo / p0[j]; width = du - dl
                dec = 'meets' if dl >= req else ('insufficient' if du < req else 'uncertain')
                mask = vh + E >= lo; components = np.count_nonzero(mask & np.r_[True, ~mask[:-1]])
                vals = {'P0_kN': p0[j], 'predicted_peak_kN': np.max(vh), 'P_lower_kN': lo, 'P_upper_kN': up,
                    'D_lower': dl, 'D_upper': du, 'D_interval_width': width, 'interval_decision': dec,
                    'width_status': 'too_wide' if width > wl else 'acceptable', 'operational_full_recompute': dec == 'uncertain' or width > wl,
                    'max_time_dependent_E_kN': np.max(E), 'potential_peak_region_components': components,
                    'potential_peak_time_samples': mask.sum(), 'potential_peak_first_s': t[np.flatnonzero(mask)[0]],
                    'potential_peak_last_s': t[np.flatnonzero(mask)[-1]]}
                compare(d, vals); compare(de, vals)
                pt = np.max(abs(truth[:, j])); dt = 1 - pt / p0[j]; gap = abs(pred[z, order][:, j] - truth[:, j]) - E
                strict_uncovered += int(np.count_nonzero(gap > 0)); max_uncovered = max(max_uncovered, float(np.max(gap)))
                coverage = {'true_reference_peak_kN': pt, 'true_reference_D': dt, 'true_insufficient': dt < req,
                    'true_adverse': dt < 0, 'peak_covered': lo - 1e-8 <= pt <= up + 1e-8,
                    'curve_covered_all_samples': np.max(gap) <= 1e-8, 'max_error_minus_envelope_kN': np.max(gap),
                    'uncovered_samples_tolerance1e8': np.count_nonzero(gap > 1e-8),
                    'insufficient_action_miss': dt < req and dec == 'meets', 'false_insufficient': dt >= req and dec == 'insufficient',
                    'adverse_action_miss': dt < 0 and dec == 'meets', 'adverse_risk_miss': dt < 0 and dl >= 0}
                compare(de, coverage)
                rows.append({'zeta': z, 'order': order, 'Story': st, **vals, **coverage})
    summaryrows = []
    for z in [.06, .07, .08, .10]:
        for order in [1, 2]:
            rr = [d for d in rows if d['zeta'] == z and d['order'] == order]
            sm = {'layers': 12, 'peak_coverage': sum(d['peak_covered'] for d in rr) / 12,
                'curve_coverage': sum(d['curve_covered_all_samples'] for d in rr) / 12,
                'median_D_width_pp': 100 * float(np.median([d['D_interval_width'] for d in rr])),
                'max_D_width_pp': 100 * max(d['D_interval_width'] for d in rr),
                'meets': sum(d['interval_decision'] == 'meets' for d in rr), 'insufficient': sum(d['interval_decision'] == 'insufficient' for d in rr),
                'uncertain': sum(d['interval_decision'] == 'uncertain' for d in rr), 'too_wide': sum(d['width_status'] == 'too_wide' for d in rr),
                'operational_recompute_count': sum(d['operational_full_recompute'] for d in rr),
                **{k: sum(d[k] for d in rr) for k in ['insufficient_action_miss', 'false_insufficient', 'adverse_action_miss', 'adverse_risk_miss']},
                'true_adverse_count': sum(d['true_adverse'] for d in rr)}
            compare(next(d for d in summary if float(d['target_zeta']) == z and int(d['Taylor_order']) == order), sm)
            summaryrows.append({'zeta': z, 'order': order, **sm})
    wr('independent-selected-positive-convolutions-24.csv', selectedrows)
    wr('independent-all300-fixed-time-story-envelopes-40.csv', timerows)
    wr('independent-first-two-step-lags-24.csv', lagrows)
    wr('independent-summary-8.csv', summaryrows)
    cost = rd(Q / 'measured-envelope-cost-8.csv')
    result = {'source_files_SHA_verified': len(manifest['files']), 'envelope_cache_SHA_verified': True,
        'input_files_SHA_verified': len(method['inputs']), 'selected_modes_fixed': [2, 10, 13], 'fixed_time_indices': times,
        'direct_positive_convolution_max_modal_Q_difference_m': max(d['positive_direct_vs_saved_modal_Q_max_error_m'] for d in selectedrows),
        'direct_all300_at_fixed_times_max_story_E_difference_kN': max(d['all12_story_envelope_max_difference_kN'] for d in timerows),
        'interval_classification_and_coverage_fields_checked': checks, 'max_metric_difference': maxdiff,
        'strict_uncovered_curve_samples': strict_uncovered, 'max_error_minus_E_kN': max_uncovered,
        'median_dt_s': h, 'nominal_dt_s': .02, 'dt_difference_s': h - .02,
        'max_A11_or_omegaA12_nominal_vs_median_difference': maxnominal,
        'fft_length': 8192, 'linear_convolution_required_length': 2 * (N - 1) - 1,
        'core_seconds_reaggregated': sum(float(d['candidate_core_seconds']) for d in cost),
        'new_ODE_or_target_truth_solves': 0, 'proof_status': 'numeric audit; median step differs nominal; guards not rigorous FP/continuous certificate',
        'isolated_source_review': 'envelope computation only baseline/predictor and candidate parameter; frozen then reads historical targets; all target outcomes already known'}
    assert result['direct_positive_convolution_max_modal_Q_difference_m'] < 1e-8
    assert result['direct_all300_at_fixed_times_max_story_E_difference_kN'] < 1e-5
    assert strict_uncovered == 0
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
