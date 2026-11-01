"""Independent baseline-only peak derivatives, modal sources and local-peak audit."""
from pathlib import Path
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent; S = O.parents[2]; P = S / 'roles/role4/R006'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def rd(path):
    with path.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def wr(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    assert not (O / 'results.json').exists()
    manifest = json.loads((P / 'delivery-manifest.json').read_text())
    addendum = json.loads((P / 'delivery-manifest-v002.json').read_text())
    assert sha(P / 'delivery-manifest.json') == addendum['original_manifest']['sha256']
    for d in manifest['files'] + addendum['additive_files']:
        p = Path(d['path']); assert sha(p) == d['sha256'] and p.stat().st_size == d['bytes']
    inputs = json.loads((P / 'input-method-freeze.json').read_text())['inputs']
    for d in inputs: assert sha(Path(d['path'])) == d['sha256']
    with np.load(Path(inputs[0]['path']), allow_pickle=False) as a:
        tp, sp, op, bp = [a[k].copy() for k in ['t', 's_unitGamma', 'omega', 'B_direct']]
    with np.load(Path(inputs[1]['path']), allow_pickle=False) as a: zp = a['z_unit'].copy()
    with np.load(Path(inputs[2]['path']), allow_pickle=False) as a:
        tu, su, ou, bu, zu = [a[k].copy() for k in ['t', 's_unit', 'omega', 'B', 'z_unit']]
    tables = {name: rd(P / name) for name in ['baseline-sensitivity-ranked-floors-15.csv', 'right-controller-modal-source-summary-15.csv',
        'all-mode-signed-sensitivity-sources-3636.csv', 'top5-signed-sensitivity-sources-75.csv',
        'near1pct-saved-grid-branches.csv', 'top5-distinct-local-peaks-per-floor-75.csv']}
    mainidx = {(d['Case'], d['Story']): d for d in tables['baseline-sensitivity-ranked-floors-15.csv']}
    ctrlidx = {(d['Case'], d['Story'], int(d['controller_number'])): d for d in tables['right-controller-modal-source-summary-15.csv']}
    modalidx = {(d['Case'], d['Story'], int(d['controller_number']), int(d['Mode'])): d for d in tables['all-mode-signed-sensitivity-sources-3636.csv']}
    topidx = {(d['Case'], d['Story'], int(d['controller_number']), int(d['Mode'])): d for d in tables['top5-signed-sensitivity-sources-75.csv']}
    localidx = {(d['Case'], d['Story'], int(d['local_peak_amplitude_rank'])): d for d in tables['top5-distinct-local-peaks-per-floor-75.csv']}
    nearidx = {(d['Case'], d['Story'], int(d['saved_index'])): d for d in tables['near1pct-saved-grid-branches.csv']}
    fields = 0; maxdiff = 0.; maxclosure = 0.; author = []; mainmodes = []; modalrows = []; localrows = []; nearcount = 0
    def compare(row, values):
        nonlocal fields, maxdiff
        for name, value in values.items():
            fields += 1
            if isinstance(value, (bool, np.bool_)): assert row[name] == str(bool(value)), (name, value, row[name])
            elif isinstance(value, str): assert row[name] == value, (name, value, row[name])
            else:
                err = abs(float(value) - float(row[name])); maxdiff = max(maxdiff, err)
                assert err < 1e-8, (name, value, row[name])
    datasets = [('SHW3X_fixed300', tp, sp, zp, op, bp, 1000., 'kN'), ('publicExample5_H-E12140', tu, su, zu, ou, bu, 1., 'kip')]
    for case, time, states, z, omega, B, div, unit in datasets:
        coefficient = B * omega ** 2 / div
        # Scalar mode sums, rather than producer BLAS matrix multiplication.
        v = np.einsum('tr,jr->tj', states, coefficient, optimize=False)
        vz = np.einsum('tr,jr->tj', z, coefficient, optimize=False)
        for j in range(B.shape[0]):
            story = f'Story{j + 1}'; amp = abs(v[:, j]); p0 = float(max(amp)); active = np.where(amp == p0)[0]
            slopes = np.sign(v[:, j]) * vz[:, j]; prime = float(max(slopes[active])); controllers = active[slopes[active] == prime]
            sval = -prime / p0
            # Sign changes of adjacent amplitude differences, including one-sided endpoints.
            delta = np.diff(amp)
            local = [i for i in range(1, len(amp) - 1) if delta[i - 1] >= 0 and delta[i] <= 0]
            if amp[0] >= amp[1]: local.insert(0, 0)
            if amp[-1] >= amp[-2]: local.append(len(amp) - 1)
            assert not any(local[k + 1] == local[k] + 1 and amp[local[k + 1]] == amp[local[k]] for k in range(len(local) - 1)), 'plateau needs separate grouping'
            local.sort(key=lambda i: (-amp[i], i))
            near = np.where(amp >= .99 * p0)[0]; near_local = [n for n in local if amp[n] >= .99 * p0 and n not in active]
            runner = next(n for n in local if n not in active)
            base = {'P0': p0, 'exact_active_count': len(active), 'exact_active_indices': ';'.join(str(int(n)) for n in active),
                'right_controller_count': len(controllers), 'right_controller_indices': ';'.join(str(int(n)) for n in controllers),
                'Pprime_right_force_per_zeta': prime, 'S_percent_per_damping_pp': sval, 'force_change_per_damping_pp': .01 * prime,
                'near1pct_saved_points': len(near), 'near1pct_inactive_local_peak_count': len(near_local),
                'runnerup_local_peak_relative_gap': 1 - amp[runner] / p0, 'runnerup_local_peak_time_s': time[runner]}
            compare(mainidx[case, story], base)
            for cnum, n in enumerate(controllers, 1):
                contributions = -np.sign(v[n, j]) * coefficient[j] * z[n] / p0
                order = sorted(range(len(omega)), key=lambda r: (-abs(contributions[r]), r))
                top, rest = order[:5], order[5:]
                positive = float(sum(c for c in contributions if c > 0)); negative = float(sum(c for c in contributions if c < 0))
                closure = float(np.sum(contributions) - sval); maxclosure = max(maxclosure, abs(closure))
                compare(ctrlidx[case, story, cnum], {'saved_index': n, 'time_s': time[n], 'signed_V0': v[n, j], 'P0': p0,
                    'S_percent_per_damping_pp': sval, 'promoting_positive_c_sum': positive, 'opposing_negative_c_sum': negative,
                    'top5_c_sum': np.sum(contributions[top]), 'remaining_mode_count': len(rest),
                    'remaining_signed_c_sum': np.sum(contributions[rest]), 'all_mode_c_sum': np.sum(contributions)})
                for rank, r in enumerate(order, 1):
                    vals = {'abs_c_rank': rank, 'omega_rad_s': omega[r], 'c_improvement_percent_per_damping_pp': contributions[r],
                        'a_opposing_derivative': -contributions[r], 'baseline_modal_signed_force_at_controller': coefficient[j, r] * states[n, r]}
                    compare(modalidx[case, story, cnum, r + 1], vals)
                    if rank <= 5: compare(topidx[case, story, cnum, r + 1], vals)
                    modalrows.append({'Case': case, 'Story': story, 'controller': cnum, 'Mode': r + 1, 'c': float(contributions[r])})
                text = '; '.join(f'{r + 1}:{contributions[r]:+.9f}' for r in top)
                author.append({'Case': case, 'Story': story, 'force_unit': unit, 'P0': p0, 'controller_time_s': float(time[n]),
                    'S_percent_per_damping_pp': sval, 'slow_rank': 0, 'force_change_per_damping_pp': .01 * prime,
                    'promoting_sum': positive, 'opposing_sum': negative, 'top5_signed_c': text,
                    'remaining_mode_count': len(rest), 'remaining_signed_c': float(np.sum(contributions[rest])),
                    'exact_active_count': len(active), 'near1pct_inactive_local_peaks': len(near_local),
                    'runnerup_peak_time_s': float(time[runner]), 'runnerup_relative_gap_percent': float(100 * (1 - amp[runner] / p0))})
                if case == 'SHW3X_fixed300' and story in ['Story5', 'Story12']:
                    for r in top: mainmodes.append({'Story': story, 'Mode': str(r + 1), 'c': float(contributions[r]), 'scope': 'baseline controller derivative contribution'})
                    mainmodes.append({'Story': story, 'Mode': 'remaining295', 'c': float(np.sum(contributions[rest])), 'scope': 'baseline controller derivative contribution'})
            for rank, n in enumerate(local[:5], 1):
                values = {'saved_index': n, 'time_s': time[n], 'signed_V0': v[n, j], 'relative_amplitude_gap': 1 - amp[n] / p0,
                    'branch_g_force_per_zeta': slopes[n], 'branch_S_using_P0': -slopes[n] / p0,
                    'is_exact_active': n in active, 'inside_diagnostic1pct': amp[n] >= .99 * p0}
                compare(localidx[case, story, rank], values)
                localrows.append({'Case': case, 'Story': story, 'local_peak_rank': rank, 'time_s': float(time[n]),
                    'gap_percent': float(100 * (1 - amp[n] / p0)), 'branch_S_using_global_P0': float(-slopes[n] / p0), 'inside1pct': bool(amp[n] >= .99 * p0)})
            for n in near:
                nearcount += 1
                compare(nearidx[case, story, int(n)], {'time_s': time[n], 'relative_amplitude_gap': 1 - amp[n] / p0,
                    'branch_g_force_per_zeta': slopes[n], 'branch_S_using_P0': -slopes[n] / p0,
                    'is_exact_active': n in active, 'is_exact_right_controller': n in controllers, 'is_local_abs_peak': n in local})
    assert len(modalrows) == 3636 and len(author) == 15 and nearcount == len(nearidx)
    for d in author:
        d['slow_rank'] = 1 + sum(v['Case'] == d['Case'] and v['S_percent_per_damping_pp'] < d['S_percent_per_damping_pp'] for v in author)
        compare(mainidx[d['Case'], d['Story']], {'slow_improvement_rank': d['slow_rank']})
    # No target arrays or recomputation: only already-audited small reference tables.
    rankchecks = []; candidatecontext = []
    for case, truthpath, field in [('SHW3X_fixed300', S / 'roles/role4/R002/exact-reference-truth-peaks-48.csv', 'exact_reference_decrease_percent'),
            ('publicExample5_H-E12140', S / 'roles/role4/R005/exact-reference-floor-peaks-12.csv', 'reference_decrease_percent')]:
        truth = rd(truthpath); main = [d for d in author if d['Case'] == case]
        for target in [.06, .07, .08, .10]:
            values = {d['Story']: float(d[field]) for d in truth if float(d['target_zeta']) == target}
            inversions = sum((a['S_percent_per_damping_pp'] - b['S_percent_per_damping_pp']) * (values[a['Story']] - values[b['Story']]) < 0
                for i, a in enumerate(main) for b in main[i + 1:])
            sranks = np.array([d['slow_rank'] for d in main]); tranks = np.array([1 + sum(v < values[d['Story']] for v in values.values()) for d in main])
            rho = float(np.corrcoef(sranks, tranks)[0, 1])
            row = next(d for d in rd(P / 'posterior-rank-inversions-8.csv') if d['Case'] == case and float(d['target_zeta']) == target)
            compare(row, {'strict_order_inversions': inversions, 'Spearman_no_ties_rho': rho, 'pairs': len(main) * (len(main) - 1) // 2})
            rankchecks.append({'Case': case, 'target': target, 'inversions': int(inversions), 'Spearman': rho})
            for d in main: candidatecontext.append({'Case': case, 'Story': d['Story'], 'target': target, 'baseline_S': d['S_percent_per_damping_pp'], 'known_reference_decrease_percent': values[d['Story']]})
    public_truth = rd(S / 'roles/role4/R005/exact-reference-floor-peaks-12.csv')
    pubroof6 = next(d for d in public_truth if float(d['target_zeta']) == .06 and d['Story'] == 'Story3')
    localroof = [d for d in localrows if d['Case'] == 'publicExample5_H-E12140' and d['Story'] == 'Story3']
    assert localroof[1]['gap_percent'] > 1 and not localroof[1]['inside1pct']
    assert float(pubroof6['reference_peak_time_s']) == localroof[1]['time_s']
    wr('author-floor-summary-15.csv', author); wr('author-main5-and-rest-12.csv', mainmodes)
    wr('independent-local-peaks-75.csv', localrows); wr('independent-rank-checks-8.csv', rankchecks)
    wr('known-candidate-S-context-60.csv', candidatecontext)
    private5 = next(d for d in author if d['Case'] == 'SHW3X_fixed300' and d['Story'] == 'Story5')
    private12 = next(d for d in author if d['Case'] == 'SHW3X_fixed300' and d['Story'] == 'Story12')
    result = {'source_numeric_files_verified': len(manifest['files']), 'additive_v002_files_verified': len(addendum['additive_files']),
        'source_baseline_inputs_verified': len(inputs), 'floors': len(author), 'modal_contributions_checked': len(modalrows),
        'top5_terms_checked': 75, 'near_saved_grid_points_checked': nearcount, 'local_peaks_checked': len(localrows),
        'field_checks': fields, 'max_numeric_difference': maxdiff, 'max_closure_error': maxclosure,
        'all15_computed_active_sets_singleton': all(d['exact_active_count'] == 1 for d in author),
        'private_Story5_S': private5['S_percent_per_damping_pp'], 'private_roof_S': private12['S_percent_per_damping_pp'],
        'roof_to_Story5_S_ratio': private12['S_percent_per_damping_pp'] / private5['S_percent_per_damping_pp'],
        'public_roof_runnerup_gap_percent': localroof[1]['gap_percent'], 'public_roof_runnerup_branch_S': localroof[1]['branch_S_using_global_P0'],
        'public6pct_roof_peak_time_matches_runnerup': True, 'one_percent_independent_near_peak_diagnostic_misses_runnerup': True,
        'rank_validation_posthoc_only': True, 'all_rank_inversions_zero': all(d['inversions'] == 0 for d in rankchecks),
        'new_ODE_or_target_state_solves': 0, 'target_response_arrays_opened': False,
        'scope': 'baseline controller derivatives, not candidate modal force shares; saved-grid computed equality, not strict FP/continuous peak proof'}
    (O / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8'); print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
