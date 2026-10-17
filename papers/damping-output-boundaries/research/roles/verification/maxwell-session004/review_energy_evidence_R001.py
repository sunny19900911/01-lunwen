"""Independent scalar recomputation of frozen energy evidence, without rereading XLSX.

Uses math.fsum over named columns; does not import either reviewed audit script.
Outputs only six-row summaries/diagnostics, never full response arrays.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def near(a, b, atol=1e-12, rtol=1e-12):
    return math.isclose(float(a), float(b), abs_tol=atol, rel_tol=rtol)


def run(cache, native, master, out):
    out.mkdir(parents=True, exist_ok=False)
    manifest_path = cache / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    source_result = json.loads((native / 'independent_energy_source.json').read_text(encoding='utf-8'))
    main_run = json.loads((master / 'run_record.json').read_text(encoding='utf-8'))
    with (master / 'energy_summary.csv').open(encoding='utf-8-sig', newline='') as f:
        main_rows = {r['case']: r for r in csv.DictReader(f)}
    originals = {r['case']: r for r in source_result['rows']}
    assert manifest['complete'] and manifest['source_unchanged']
    assert all(source_result['checks'].values())
    assert manifest['sha256'] == source_result['sha256'] == main_run['source_sha256']
    assert manifest['bytes'] == main_run['source_bytes'] == 635525054
    assert source_result['units'] == manifest['tables']['Total Energy Components']['units']
    assert all(x == 'kN-m' for x in source_result['units'][4:])
    for item in main_run['input_files']:
        assert sha(Path(item['path'])) == item['sha256'], item['path']
    main_script = master.parent / 'audit_core_energy.py'
    assert sha(main_script) == main_run['script_sha256']
    te = manifest['tables']['Total Energy Components']
    ge = manifest['tables']['Element NL Energy By Group']
    assert not te['reaches_excel_row_limit'] and not ge['reaches_excel_row_limit']
    ti = {name: i for i, name in enumerate(te['columns'])}
    gi = {name: i for i, name in enumerate(ge['columns'])}
    all_by_case = {}
    for key, meta in ge['groups'].items():
        assert meta['keys']['Group'] == 'All'
        case = meta['keys']['Output Case']
        assert case not in all_by_case
        all_by_case[case] = (key, meta)
    cases = {m['keys']['Output Case'] for m in te['groups'].values()}
    expected = {'RH4X', 'RH4Y', 'SHW4X', 'SHW4Y', 'SHW7X', 'SHW7Y'}
    assert cases == set(all_by_case) == set(originals) == set(main_rows) == expected
    energy_names = ['Input Energy', 'Kinetic Energy', 'Potential Energy',
                    'Global Damping Energy', 'Link Damper Energy',
                    'Link Hysteresis Energy', 'Energy Error']
    rows, detail = [], []
    p_total, p_all = cache / te['cache'], cache / ge['cache']
    with np.load(p_total, allow_pickle=False) as total, np.load(p_all, allow_pickle=False) as grouped:
        for key, meta in te['groups'].items():
            case = meta['keys']['Output Case']
            gkey, gmeta = all_by_case[case]
            assert meta['keys']['Case Type'] == gmeta['keys']['Case Type'] == 'NonModHist'
            a, b = total[key], grouped[gkey]
            assert np.isfinite(a).all() and np.isfinite(b).all()
            t = [float(v) for v in a[:, ti['Time']]]
            assert t == [float(v) for v in b[:, gi['Time']]]
            assert len(t) == meta['n'] == gmeta['n'] == originals[case]['n']
            steps = [y - x for x, y in zip(t, t[1:])]
            assert t[0] == 0 and all(near(v, .02, atol=1e-11) for v in steps)
            sr = [int(v) for v in a[:, ti['SourceRow']]]
            assert all(y == x + 1 for x, y in zip(sr, sr[1:]))
            assert sr[-1] == originals[case]['source_end_row'] == int(main_rows[case]['source_row_final'])
            v = {name: [float(x) for x in a[:, ti[name]]] for name in energy_names}
            assert all(v[name][0] == 0 for name in energy_names)
            eg = math.fsum((v['Global Damping Energy'][-1], -v['Global Damping Energy'][0]))
            ed = math.fsum((v['Link Damper Energy'][-1], -v['Link Damper Energy'][0]))
            assert eg > 0 and ed > 0
            ratio = ed / eg
            residual = [math.fsum((v['Input Energy'][i],
                         *(-v[name][i] for name in energy_names[1:6]))) for i in range(len(t))]
            error = v['Energy Error']
            minus = max(abs(math.fsum((r, -e))) for r, e in zip(residual, error))
            plus = max(abs(math.fsum((r, e))) for r, e in zip(residual, error))
            scale = max(abs(x) for x in v['Input Energy'])
            assert scale > 0
            cross = [abs(math.fsum((float(b[i, gi['Internal Viscous Damping']]),
                     float(b[i, gi['Support Viscous Damping']]), -v['Link Damper Energy'][i])))
                     for i in range(len(t))]
            hcross = [abs(math.fsum((float(b[i, gi['Internal Hysteretic Damping']]),
                      float(b[i, gi['Support Hysteretic Damping']]), -v['Link Hysteresis Energy'][i])))
                      for i in range(len(t))]
            assert max(cross) < 1e-9 and max(hcross) < 1e-9
            assert minus < 1e-6 and plus > 1000 * max(minus, 1e-15)
            dg = [y - x for x, y in zip(v['Global Damping Energy'], v['Global Damping Energy'][1:])]
            dd = [y - x for x, y in zip(v['Link Damper Energy'], v['Link Damper Energy'][1:])]
            original, main = originals[case], main_rows[case]
            assert near(eg, original['global_energy_end_kNm']) and near(ed, original['device_energy_end_kNm'])
            assert near(.05 * ratio, original['energy_additional_damping_if_xi0_0p05'])
            assert near(eg, main['Eglobal_increment_kNm']) and near(ed, main['Elink_increment_kNm'])
            assert near(ratio, main['ratio_Elink_over_Eglobal'])
            assert near(.05 * ratio, main['conditional_added_damping_at_5pct'])
            assert near(max(map(abs, residual)) / scale, main['max_balance_residual_over_max_input'])
            assert near(minus / scale, main['residual_minus_reported_error_over_input'])
            assert near(max(cross), main['max_All_vs_total_link_diff_kNm'])
            assert near(min(dd), original['dEdevice_min_kNm'])
            end_stored = math.fsum((v['Kinetic Energy'][-1], v['Potential Energy'][-1]))
            assert near(end_stored / scale, main['end_kinetic_plus_potential_over_input_scale'])
            row = {'case': case, 'n': len(t), 't0_s': t[0], 'T_s': t[-1],
                   'source_start_row': sr[0], 'source_end_row': sr[-1],
                   'Eglobal_delta_kNm': eg, 'Elink_delta_kNm': ed, 'Elink_over_Eglobal': ratio,
                   'conditional_added_damping_if_background_5pct': .05 * ratio,
                   'conditional_added_damping_percent': 5 * ratio,
                   'max_abs_balance_kNm': max(map(abs, residual)), 'balance_end_kNm': residual[-1],
                   'max_abs_balance_over_peak_input': max(map(abs, residual)) / scale,
                   'max_balance_minus_EnergyError_kNm': minus, 'max_balance_plus_EnergyError_kNm': plus,
                   'max_All_viscous_minus_LinkDamper_kNm': max(cross),
                   'max_All_hysteretic_minus_LinkHysteresis_kNm': max(hcross),
                   'min_Global_increment_kNm': min(dg), 'negative_Global_increment_count': sum(x < 0 for x in dg),
                   'min_Link_increment_kNm': min(dd), 'negative_Link_increment_count': sum(x < 0 for x in dd),
                   'end_kinetic_plus_potential_kNm': end_stored,
                   'end_storage_over_peak_input': end_stored / scale,
                   'end_storage_over_end_input': end_stored / abs(v['Input Energy'][-1]),
                   'actual_background_damping_verified': False}
            rows.append(row)
            quarter = []
            for fraction in [.25, .5, .75, 1]:
                i = next(i for i, x in enumerate(t) if x >= fraction * t[-1])
                delta_g = v['Global Damping Energy'][i] - v['Global Damping Energy'][0]
                quarter.append({'fraction': fraction, 'actual_t_s': t[i],
                                'ratio': (v['Link Damper Energy'][i] - v['Link Damper Energy'][0]) / delta_g if delta_g > 0 else None})
            main_case = next(x for x in main_run['cases'] if x['case'] == case)
            assert all(near(x['ratio'], y['ratio']) and x['actual_t_s'] == y['actual_T_s']
                       for x, y in zip(quarter, main_case['quarter_windows']))
            detail.append({'case': case, 'end_values_kNm': {name: v[name][-1] for name in energy_names},
                           'quarter_windows': quarter, 'dt_min_s': min(steps), 'dt_max_s': max(steps),
                           'All_group_native_reader_independently_repeated_here': False})
    assert sum(r['n'] for r in rows) == 16296
    files = [manifest_path, p_total, p_all, main_script, master / 'run_record.json', master / 'energy_summary.csv',
             native / 'audit_energy_source.py', native / '独立原生能量复核.md',
             native / 'independent_energy_source.json', native / 'independent_energy_summary.csv']
    report = {'recorded_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'source_sha256_inherited_not_rehashed': manifest['sha256'],
              'source_bytes': manifest['bytes'], 'source_table_units': 'kN-m',
              'script_sha256': sha(Path(__file__)),
              'inputs': [{'path': str(p.resolve()), 'sha256': sha(p)} for p in files],
              'checks_passed': True, 'rows': rows, 'details': detail,
              'scope': 'Review existing openpyxl source evidence and independent scalar cache recomputation; no XLSX row re-extraction.',
              'limits': ['No actual 5% background setting verified.', 'Export end is not certified complete free tail.',
                         'All-group crosscheck uses existing lxml cache, not a second independent raw All-group extraction.',
                         'Negative Link increments preserved; no monotonic repair or missing-value filling.',
                         'Accepting numeric export consistency does not certify solver convergence or physical device model.']}
    with (out / 'energy_review_summary.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (out / 'energy_review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checks_passed': True, 'n': 16296, 'rows': rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache', required=True, type=Path)
    parser.add_argument('--native-evidence', required=True, type=Path)
    parser.add_argument('--master-audit', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    run(args.cache, args.native_evidence, args.master_audit, args.out)
