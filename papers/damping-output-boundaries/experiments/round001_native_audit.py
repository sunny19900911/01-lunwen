"""Independent cached-array audit, followed by targeted raw CSI-cell verification.

Read-only inputs. Run with bundled Python; outputs stay beside this script.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT.parent / 'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016'
OUT = Path(__file__).resolve().parent / 'round001'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(Path.home() / '.codex/skills/etabs-response-analysis/scripts'))
from stream_csi import Workbook


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def table(folder, manifest, sheet, keys):
    tab = manifest['tables'][sheet]
    columns = tab.get('columns', tab.get('value_columns'))
    with np.load(folder / tab['cache'], allow_pickle=False) as z:
        data = {tuple(g['keys'][key] for key in keys): z[k].copy()
                for k, g in tab['groups'].items()}
    return data, columns


def peak(y):
    i = int(np.argmax(np.abs(y)))
    return i, float(y[i]), float(abs(y[i]))


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    start = time.perf_counter()
    folders = [SOURCE / '原生0数据缓存', SOURCE]
    manifests = [load_json(folders[0] / 'manifest.json'), load_json(folders[1] / 'response_cache_manifest.json')]
    source_paths = [Path(m.get('source', m.get('path'))) for m in manifests]
    stats0 = [(p.stat().st_size, p.stat().st_mtime_ns) for p in source_paths]
    hashes = [sha(p) for p in source_paths]
    assert all(h == m['sha256'] for h, m in zip(hashes, manifests)), 'Raw source changed since extraction'
    inputs = []
    for folder, m, path, h in zip(folders, manifests, source_paths, hashes):
        selected = [folder / m['tables'][sheet]['cache'] for sheet in ['Story Forces', 'Story Accelerations', 'Base Reactions']]
        inputs.append({'source': str(path), 'sha256': h, 'bytes': path.stat().st_size,
                       'cache_files': [{'path': str(p), 'sha256': sha(p)} for p in selected]})

    force, accel, base = [], [], []
    for folder, manifest in zip(folders, manifests):
        f, fcols = table(folder, manifest, 'Story Forces', ['Output Case', 'Story', 'Location'])
        a, acols = table(folder, manifest, 'Story Accelerations', ['Output Case', 'Story'])
        b, bcols = table(folder, manifest, 'Base Reactions', ['Output Case'])
        force.append(f)
        accel.append(a)
        base.append(b)

    cases = sorted(k[0] for k in base[0])
    assert set(base[0]) == set(base[1])
    grids, nets, stories, traces, targets = [], [], [], {}, [[], []]
    max_telescope = 0.0
    for case in cases:
        fi, ai, bi = fcols.index('V' + case[-1]), acols.index('U' + case[-1]), bcols.index('F' + case[-1])
        t = base[0][(case,)][:, 0]
        assert len(t) == len(np.unique(t)) and np.all(np.diff(t) > 0)
        assert np.allclose(np.diff(t), .02, atol=1e-12, rtol=0)
        assert np.array_equal(t, base[1][(case,)][:, 0])
        assert np.array_equal(accel[0][(case, 'Base')][:, ai], accel[1][(case, 'Base')][:, ai])
        x = []
        for state in range(2):
            for story in range(1, 13):
                assert np.array_equal(t, force[state][(case, f'Story{story}', 'Bottom')][:, 0])
                assert np.array_equal(t, accel[state][(case, f'Story{story}')][:, 0])
            x.append(np.column_stack([force[state][(case, f'Story{s}', 'Bottom')][:, fi] for s in range(1, 13)]))
        n = [np.diff(np.column_stack([xx, np.zeros(len(t))]), axis=1) * -1 for xx in x]
        max_telescope = max(max_telescope, *(float(np.max(abs(nn.sum(axis=1) - xx[:, 0]))) for nn, xx in zip(n, x)))
        grids.append({'case': case, 'n': len(t), 'start_s': float(t[0]), 'end_s': float(t[-1]),
                      'output_dt_s': .02, 'all_24_force_grids_equal': True,
                      'all_24_acceleration_grids_equal': True, 'base_input_samples_equal': True})
        for s in range(12):
            p = [peak(nn[:, s]) for nn in n]
            old_i, old_signed, old_peak = p[0]
            new_i, _, new_peak = p[1]
            sign = float(np.sign(old_signed))
            fixed_change = sign * (n[1][old_i, s] - n[0][old_i, s])
            recovery = new_peak - sign * n[1][old_i, s]
            nets.append({'case': case, 'lower_cut': f'Story{s+1}/Bottom',
                         'upper_cut': f'Story{s+2}/Bottom' if s < 11 else 'declared_zero_top',
                         'peak0_kN': old_peak, 'peak3_kN': new_peak, 'increase_ratio': new_peak / old_peak - 1,
                         't0_s': float(t[old_i]), 't3_s': float(t[new_i]),
                         'fixed_old_peak_change_kN': float(fixed_change), 'repeak_recovery_kN': float(recovery),
                         'budget_residual_kN': float(new_peak - old_peak - fixed_change - recovery)})
            ap = [peak(aa[(case, f'Story{s+1}')][:, ai]) for aa in accel]
            vp = [peak(xx[:, s]) for xx in x]
            stories.append({'case': case, 'story': f'Story{s+1}',
                            'cut_peak0_kN': vp[0][2], 'cut_peak3_kN': vp[1][2],
                            'cut_reduction': 1 - vp[1][2] / vp[0][2],
                            'spatial_accel_peak0_mm_s2': ap[0][2], 'spatial_accel_peak3_mm_s2': ap[1][2],
                            'spatial_accel_increase_ratio': ap[1][2] / ap[0][2] - 1})
            if ap[1][2] > ap[0][2]:
                for state in range(2):
                    arr = accel[state][(case, f'Story{s+1}')]
                    row = int(arr[ap[state][0], -1])
                    targets[state].append({'sheet': 'Story Accelerations', 'row': row,
                                           'value_col': 5 if case.endswith('X') else 6, 'case': case,
                                           'story': f'Story{s+1}', 'time_s': float(t[ap[state][0]]),
                                           'value': ap[state][1], 'unit': 'mm/sec²'})
            if new_peak > old_peak:
                for state in range(2):
                    for ss in [s+1, s+2]:
                        arr = force[state][(case, f'Story{ss}', 'Bottom')]
                        idx = p[state][0]
                        targets[state].append({'sheet': 'Story Forces', 'row': int(arr[idx, -1]),
                                               'value_col': 7 if case.endswith('X') else 8, 'case': case,
                                               'story': f'Story{ss}', 'time_s': float(t[idx]),
                                               'value': float(arr[idx, fi]), 'unit': 'kN'})
        if case == 'SHW6X':
            traces = {'t': t, 'V0_Story1': x[0][:, 0], 'V0_Story2': x[0][:, 1],
                      'V3_Story1': x[1][:, 0], 'V3_Story2': x[1][:, 1],
                      'N0': n[0][:, 0], 'N3': n[1][:, 0]}

    write_csv('adjacent_cut_net.csv', nets)
    write_csv('story_cut_and_spatial_acceleration.csv', stories)
    write_csv('time_grid_audit.csv', grids)
    # Only a compact +/- 0.10 s window enters the reviewable repository.
    window = abs(traces['t'] - 20.6) <= .10000001
    write_csv('SHW6X_control_window.csv', [{key: float(value[i]) for key, value in traces.items()}
                                          for i in np.flatnonzero(window)])
    raw_checks, raw_meta = [], []
    for state, path in enumerate(source_paths):
        with Workbook(path) as wb:
            meta = {sheet: list(wb.rows(sheet)) for sheet in ['Centers Of Mass And Rigidity', 'Load Cases - TH - Nonlin Modal', 'Modal Periods And Frequencies']}
            raw_meta.append(meta)
            for sheet in ['Story Forces', 'Story Accelerations']:
                wanted = {item['row']: item for item in targets[state] if item['sheet'] == sheet}
                headers, units = None, None
                for rn, row in wb.rows(sheet):
                    if rn == 2:
                        headers = row
                    if rn == 3:
                        units = row
                    if rn in wanted:
                        item = wanted[rn]
                        c = item['value_col']
                        actual = row[c]
                        ok = (row[0] == item['story'] and row[1] == item['case'] and row[4] == item['time_s']
                              and actual == item['value'] and units[c] == item['unit'])
                        if sheet == 'Story Forces':
                            ok = ok and row[5] == 'Bottom'
                        raw_checks.append(dict(item, source=str(path), state=state, column=headers[c],
                                               source_cell=f'{chr(65+c)}{rn}', actual=actual,
                                               raw_unit=units[c], exact_match=bool(ok)))
                    if wanted and rn >= max(wanted):
                        break
        print(f'raw selected engineering cells checked: state {state}', flush=True)

    mass_equal = raw_meta[0]['Centers Of Mass And Rigidity'] == raw_meta[1]['Centers Of Mass And Rigidity']
    cases_equal = {r[1][0]: r[1][:23] for r in raw_meta[0]['Load Cases - TH - Nonlin Modal'][3:]} == {
        r[1][0]: r[1][:23] for r in raw_meta[1]['Load Cases - TH - Nonlin Modal'][3:]}
    frequencies = [np.array([r[1][4] for r in meta['Modal Periods And Frequencies'][3:]], dtype=float) for meta in raw_meta]
    frequency_diff = float(np.max(abs(frequencies[1] / frequencies[0] - 1)))
    stats1 = [(p.stat().st_size, p.stat().st_mtime_ns) for p in source_paths]
    hashes1 = [sha(p) for p in source_paths]
    checks = {'sources_stable': stats0 == stats1 and hashes == hashes1,
              'raw_engineering_cells_exact': len(raw_checks) == 10 and all(c['exact_match'] for c in raw_checks),
              'mass_and_rigidity_centers_equal_raw': mass_equal, 'solver_and_input_case_fields_equal_raw': cases_equal,
              'omega_relative_difference_below_1e-7': frequency_diff < 1e-7,
              'one_adjacent_cut_net_increase': sum(r['increase_ratio'] > 0 for r in nets) == 1,
              'all_168_cut_peaks_decrease': all(r['cut_reduction'] > 0 for r in stories),
              'three_spatial_acceleration_increases': sum(r['spatial_accel_increase_ratio'] > 0 for r in stories) == 3,
              'telescope_residual_below_1e-9_kN': max_telescope < 1e-9}
    result = {'evidence_id': 'E-EXP-001', 'utc_finished': datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds': time.perf_counter() - start, 'inputs': inputs,
              'code_sha256': sha(__file__), 'python': platform.python_version(), 'numpy': np.__version__,
              'checks': checks, 'n_records': 7, 'n_direction_cases': len(cases), 'n_story_pairs': len(stories),
              'omega_max_relative_difference': frequency_diff, 'max_telescope_residual_kN': max_telescope,
              'net_increases': [r for r in nets if r['increase_ratio'] > 0],
              'spatial_acceleration_increases': [r for r in stories if r['spatial_accel_increase_ratio'] > 0],
              'selected_raw_cells': raw_checks,
              'boundary': 'Cached full exported windows audited; raw selected cells and small metadata re-read. No continuous-time extrema or floor inertia identity established.'}
    (OUT / 'audit_result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checks': checks, 'elapsed_seconds': result['elapsed_seconds'], 'net_increases': result['net_increases']}, ensure_ascii=False, indent=2))
    assert all(checks.values()), 'Audit failed; retain output and investigate'


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
