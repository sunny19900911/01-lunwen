"""Baseline-only independent U/P/C right derivatives; no target states or ODE."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import csv, hashlib, json
import numpy as np

O = Path(__file__).resolve().parent; S = O.parents[2]; P4 = S / 'roles/role4'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def wr(name, rows):
    with (O / name).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def main():
    assert not (O / 'independent-results.json').exists()
    frozen = json.loads((P4 / 'R009/input-and-factor-contract-freeze.json').read_text())
    bindings = frozen['inputs'][:4]
    pubfreeze = json.loads((P4 / 'R004/prediction-and-envelope-freeze.json').read_text())
    bindings = bindings + [pubfreeze['local_arrays'][0]]
    for d in bindings: assert sha(Path(d['path'])) == d['sha256']
    inputs = {'observed_start': '2026-11-02T00:28:52.367001+08:00', 'input_bindings': bindings,
        'definition': 'modal p right derivative from its own exact computed peak set; p=0 uses max|vprime|; P right derivative from total peak set; U=sum p; C=P/U',
        'no_target_inputs': True, 'no_new_ODE_or_response': True,
        'numerical_status': 'saved-grid double-precision algebra, no continuous/strict FP guarantee',
        'comparison_status': 'calculate independently before opening any new role4/R011 or role1/R007 files'}
    (O / 'independent-input-rules.json').write_text(json.dumps(inputs, indent=2), encoding='utf-8')
    with np.load(Path(bindings[0]['path']), allow_pickle=False) as a:
        t, s, om, B = [a[k].copy() for k in ['t', 's_unitGamma', 'omega', 'B_direct']]
    with np.load(Path(bindings[1]['path']), allow_pickle=False) as a: z = a['z_unit'].copy()
    data = [('SHW3X', t, s, z, om, B, 1000., 'kN')]
    for case, b in [('SHW4X', bindings[2]), ('RH4X', bindings[3])]:
        with np.load(Path(b['path']), allow_pickle=False) as a:
            data.append((case, a['t'].copy(), a['s0'].copy(), a['Z'].copy(), a['omega'].copy(), a['B'].copy(), 1000., 'kN'))
    with np.load(Path(bindings[4]['path']), allow_pickle=False) as a:
        data.append(('publicExample5_H-E12140', a['t'].copy(), a['s_unit'].copy(), a['z_unit'].copy(), a['omega'].copy(), a['B'].copy(), 1., 'kip'))
    mainrows = []; modes = []; diag = []; kernelcheck = []; maxclosure = 0.; allmodal = []
    for case, t, s, z, om, B, div, unit in data:
        # Alternative unit-kernel own peaks provide a separate normalization check.
        kernelp = np.max(abs(s), axis=0); kernelprime = np.empty(len(om))
        for m in range(len(om)):
            active = np.where(abs(s[:, m]) == kernelp[m])[0]
            kernelprime[m] = max(np.sign(s[active, m]) * z[active, m]) if kernelp[m] > 0 else max(abs(z[:, m]))
        for j in range(len(B)):
            coefficient = B[j] * om ** 2 / div
            v = s * coefficient; vp = z * coefficient
            total = v.sum(axis=1); totalprime = vp.sum(axis=1)
            P = float(max(abs(total))); totalactive = np.where(abs(total) == P)[0]
            Pprime = float(max(np.sign(total[totalactive]) * totalprime[totalactive])) if P > 0 else float(max(abs(totalprime)))
            totalcontrollers = totalactive[np.sign(total[totalactive]) * totalprime[totalactive] == Pprime] if P > 0 else totalactive
            peak = np.max(abs(v), axis=0); modalprime = np.empty(len(om)); peakcounts = []; modetime = []
            for m in range(len(om)):
                active = np.where(abs(v[:, m]) == peak[m])[0]
                if peak[m] > 0:
                    slopes = np.sign(v[active, m]) * vp[active, m]; modalprime[m] = max(slopes)
                    control = active[slopes == modalprime[m]]
                else:
                    modalprime[m] = max(abs(vp[:, m])); control = np.where(abs(vp[:, m]) == modalprime[m])[0]
                peakcounts.append(len(active)); modetime.append(control)
            U, Uprime = float(sum(peak)), float(sum(modalprime))
            assert P > 0 and U > 0, 'report zero-total baseline separately instead of assigning normalized rates'
            assert P <= U * (1 + 1e-12)
            C = P / U; Cprime = (Pprime * U - P * Uprime) / U ** 2
            SS, SU, SC = -Pprime / P, -Uprime / U, -Cprime / C
            closure = SU + SC - SS; maxclosure = max(maxclosure, abs(closure))
            checkp = np.max(abs(peak - abs(coefficient) * kernelp)); checkprime = np.max(abs(modalprime - abs(coefficient) * kernelprime))
            kernelcheck.append({'Case': case, 'Story': f'Story{j + 1}', 'p_unit_kernel_scaling_max_difference': float(checkp), 'pprime_unit_kernel_scaling_max_difference': float(checkprime)})
            row = {'Case': case, 'Story': f'Story{j + 1}', 'modes': len(om), 'force_unit': unit,
                'P0': P, 'U0': U, 'C0': C, 'Pprime_right': Pprime, 'Uprime_right': Uprime, 'Cprime_right': Cprime,
                'S': SS, 'SU': SU, 'SC': SC, 'S_minus_SU_SC': SS - SU - SC,
                'total_peak_active_count': len(totalactive), 'total_right_controller_count': len(totalcontrollers),
                'total_controller_times_s': ';'.join(f'{t[n]:.12g}' for n in totalcontrollers),
                'zero_modal_peak_count': int(np.sum(peak == 0)), 'nonzero_modal_tied_peak_count': int(sum(peak[m] > 0 and peakcounts[m] > 1 for m in range(len(om)))),
                'modal_pprime_positive_count': int(np.sum(modalprime > 0)), 'modal_pprime_negative_count': int(np.sum(modalprime < 0)),
                'SU_is_negative': SU < 0, 'SC_is_negative': SC < 0,
                'scope': 'baseline own-modal-peak amplitudes and total-peak synthesis ratio; not phase-only or finite-increment causal shares'}
            mainrows.append(row)
            selected = [1, 3, 9, 12, 17, 49] if len(om) == 300 else [0, 1, 2, 3, 9, 11]
            n = int(totalcontrollers[0])
            for m in range(len(om)):
                ar = {'Case': case, 'Story': f'Story{j + 1}', 'Mode': m + 1, 'modal_peak': float(peak[m]),
                    'modal_peak_right_derivative': float(modalprime[m]), 'SU_mode_piece': float(-modalprime[m] / U),
                    'own_modal_peak_controller_times_s': ';'.join(f'{t[k]:.12g}' for k in modetime[m][:10]),
                    'own_modal_peak_controller_count': len(modetime[m]),
                    'total_peak_time_s': float(t[n]), 'total_peak_c_piece': float(-np.sign(total[n]) * vp[n, m] / P)}
                allmodal.append(ar)
                if m in selected: diag.append(ar)
            if case == 'SHW3X' and j in [4, 11]: modes.append(row)
    assert len(mainrows) == 39
    wr('independent-baseline-U-C-rates-39.csv', mainrows); wr('independent-SHW3X-priority-2.csv', modes)
    wr('selected-own-modal-peak-vs-total-peak-234.csv', diag); wr('independent-unit-kernel-checks-39.csv', kernelcheck)
    # Small all-modal peak data support later frozen-table comparison, no time histories.
    wr('independent-modal-own-peak-rates-10836.csv', allmodal)
    result = {'completed_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'floors': len(mainrows),
        'modal_own_peak_rows': len(allmodal), 'all_P_U_positive': True, 'max_S_SU_SC_closure': maxclosure,
        'SU_negative_floors': [(d['Case'], d['Story']) for d in mainrows if d['SU'] < 0],
        'SC_negative_floors': [(d['Case'], d['Story']) for d in mainrows if d['SC'] < 0],
        'zero_modal_peak_entries': sum(d['zero_modal_peak_count'] for d in mainrows),
        'max_unit_kernel_peak_scaling_difference': max(d['p_unit_kernel_scaling_max_difference'] for d in kernelcheck),
        'max_unit_kernel_peak_derivative_scaling_difference': max(d['pprime_unit_kernel_scaling_max_difference'] for d in kernelcheck),
        'priority': modes, 'new_ODE_or_target_response': False, 'new_producer_files_read_before_this_result': False}
    (O / 'independent-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
