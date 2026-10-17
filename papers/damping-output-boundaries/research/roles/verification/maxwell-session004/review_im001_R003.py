"""Role2 independent scalar review of frozen I-M001, no Y or I-M002."""
import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np

CASES = ('RH4X', 'SHW4X', 'SHW7X')
WINDOWS = ((10, 20), (20, 30), (30, 40), (40, 50))
PROTOCOL = 'cfe32266bf3bdaef16709594fda40acef8024af26c179ec189bc5512303d1833'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def csvrows(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def run(cache, author, out):
    out.mkdir(parents=True, exist_ok=False)
    manifest_path = cache / 'manifest.json'
    m = json.loads(manifest_path.read_text(encoding='utf-8'))
    protocol = author / 'R001-energy-force-candidates.md'
    assert sha(protocol) == PROTOCOL
    arun_path = author / 'R002-im001-firstcalc/run_record.json'
    arun = json.loads(arun_path.read_text(encoding='utf-8'))
    for x in arun['input_files']:
        assert sha(Path(x['path'])) == x['sha256']
    assert sha(author / 'R002_im001_firstcalc.py') == arun['script_sha256']
    assert m['complete'] and m['source_unchanged']
    fm, em = m['tables']['Story Forces'], m['tables']['Total Energy Components']
    for meta, name, expected in [(fm, 'VX', 'kN'), (em, 'Global Damping Energy', 'kN-m'), (em, 'Link Damper Energy', 'kN-m')]:
        assert meta['units'][meta['headers'].index(name)] == expected
        assert set(meta['step_types']) == {'Step By Step'}
    af = author / 'R002-im001-firstcalc'
    author_windows = {(r['case'], r['window']): r for r in csvrows(af / 'windows.csv')}
    author_pairs = {(r['case'], r['window_u'], r['window_v']): r for r in csvrows(af / 'pairs.csv')}
    assert len(author_windows) == 12 and len(author_pairs) == 18

    def excel_column(i):
        s = ''
        while i:
            i, d = divmod(i - 1, 26); s = chr(65 + d) + s
        return s

    vx_letter = excel_column(fm['headers'].index('VX') + 1)
    eg_letter = excel_column(em['headers'].index('Global Damping Energy') + 1)
    el_letter = excel_column(em['headers'].index('Link Damper Energy') + 1)

    def select(meta, archive, keys):
        candidates = [(key, g) for key, g in meta['groups'].items() if g['keys'] == keys]
        assert len(candidates) == 1
        key, g = candidates[0]; a = archive[key]
        assert a.shape == (g['n'], len(meta['columns'])) and np.isfinite(a).all()
        ix = {name: i for i, name in enumerate(meta['columns'])}
        times = [float(x) for x in a[:, ix['Time']]]
        assert all(v > u for u, v in zip(times, times[1:]))
        ticks = [round(t / .02) for t in times]
        assert all(abs(t - k * .02) <= 1e-12 for t, k in zip(times, ticks))
        assert len(set(ticks)) == len(ticks) and ticks[0] == 0 and ticks[-1] >= 2500
        records = {tick: {name: float(v) for name, v in zip(meta['columns'], row)}
                   for tick, row in zip(ticks, a) if tick <= 2500}
        assert set(records) == set(range(2501))
        for r in records.values(): assert r['SourceRow'] == int(r['SourceRow']) and r['SourceRow'] >= 4
        return key, records

    def check_row(actual, reference):
        assert set(actual) == set(reference)
        for k, value in actual.items():
            if value is None: assert reference[k] == '', k
            elif isinstance(value, bool): assert reference[k] == str(value), k
            elif isinstance(value, (int, float)):
                assert math.isclose(value, float(reference[k]), abs_tol=1e-11, rel_tol=1e-12), (k, value, reference[k])
            else: assert value == reference[k], (k, value, reference[k])

    window_rows, pair_rows, diagnostics = [], [], []
    with np.load(cache / fm['cache'], allow_pickle=False) as force, np.load(cache / em['cache'], allow_pickle=False) as energy:
        for case in CASES:
            keys = {'Output Case': case, 'Case Type': 'NonModHist'}
            ek, e = select(em, energy, keys)
            s1k, a = select(fm, force, {'Story': 'Story1', 'Location': 'Bottom', **keys})
            s2k, b = select(fm, force, {'Story': 'Story2', 'Location': 'Bottom', **keys})
            assert all(e[k]['Time'] == a[k]['Time'] == b[k]['Time'] for k in e)
            S1 = [a[k]['VX'] for k in range(2501)]; S2 = [b[k]['VX'] for k in range(2501)]
            net = [math.fsum((u, -v)) for u, v in zip(S1, S2)]
            activity = [math.fsum((abs(u), abs(v))) for u, v in zip(S1, S2)]
            eg = [e[k]['Global Damping Energy'] for k in range(2501)]
            el = [e[k]['Link Damper Energy'] for k in range(2501)]
            total_g, total_l = eg[-1] - eg[0], el[-1] - el[0]
            assert total_g > 0 and total_l > 0
            full_activity = max(activity); local = []
            for start, stop in WINDOWS:
                i, j = start * 50, stop * 50
                # Python max preserves the earliest index for exact ties.
                peak = max(range(i, j + 1), key=lambda k: abs(net[k]))
                dg, dl = math.fsum((eg[j], -eg[i])), math.fsum((el[j], -el[i]))
                d = activity[peak]
                gates = (dg > 0 and dg >= total_g / 100,
                         dl > 0 and dl >= total_l / 100,
                         d > 0 and d >= full_activity / 20)
                labels = ('EG_increment_nonpositive_or_below_1pct', 'EL_increment_nonpositive_or_below_1pct',
                          'force_activity_nonpositive_or_below_5pct')
                reason = ';'.join(label for label, passed in zip(labels, gates) if not passed)
                eta = abs(net[peak]) / d if d > 0 else None
                assert eta is None or 0 <= eta <= 1
                er, r1, r2 = int(e[peak]['SourceRow']), int(a[peak]['SourceRow']), int(b[peak]['SourceRow'])
                ei, ej = int(e[i]['SourceRow']), int(e[j]['SourceRow'])
                row = {'case': case, 'window': f'{start}-{stop}', 'start_s': start, 'end_s': stop,
                       'delta_EG_kNm': dg, 'delta_EL_kNm': dl, 'R': dl / dg if dg > 0 else None,
                       'EG_fraction_of_0_50': dg / total_g, 'EL_fraction_of_0_50': dl / total_l,
                       'tN_s': e[peak]['Time'], 'S1_VX_kN': S1[peak], 'S2_VX_kN': S2[peak],
                       'N_kN': net[peak], 'D_kN': d, 'max_D_0_50_kN': full_activity,
                       'D_fraction': d / full_activity if full_activity > 0 else None, 'eta': eta,
                       'EL_at_tN_kNm': el[peak], 'EG_at_tN_kNm': eg[peak],
                       'S1_VX_cell': f'Story Forces!{vx_letter}{r1}', 'S2_VX_cell': f'Story Forces!{vx_letter}{r2}',
                       'energy_at_tN_cells': f'Total Energy Components!{eg_letter}{er}:{el_letter}{er}',
                       'EG_endpoint_cells': f'{eg_letter}{ei},{eg_letter}{ej}', 'EL_endpoint_cells': f'{el_letter}{ei},{el_letter}{ej}',
                       'energy_gate': all(gates[:2]), 'force_gate': gates[2], 'eligible': all(gates),
                       'exclusion_reasons': reason}
                check_row(row, author_windows[(case, row['window'])]); local.append(row); window_rows.append(row)
            for u, v in itertools.combinations(local, 2):
                valid = u['eligible'] and v['eligible']
                dr = 2 * abs(u['R'] - v['R']) / math.fsum((u['R'], v['R'])) if valid else None
                de = abs(u['eta'] - v['eta']) if valid else None
                matched = valid and dr <= .05; witness = matched and de >= .20
                reason = '' if witness else ('ineligible_window: ' + ';'.join(x for x in [u['exclusion_reasons'], v['exclusion_reasons']] if x)
                         if not valid else 'R_not_matched_5pct' if not matched else 'eta_gap_below_0.20')
                row = {'case': case, 'window_u': u['window'], 'window_v': v['window'], 'eligible': valid,
                       'R_u': u['R'], 'R_v': v['R'], 'eta_u': u['eta'], 'eta_v': v['eta'],
                       'delta_R_relative': dr, 'delta_eta': de, 'energy_matched': matched, 'witness': witness, 'failure_reason': reason}
                check_row(row, author_pairs[(case, u['window'], v['window'])]); pair_rows.append(row)
            diagnostics.append({'case': case, 'groups': {'energy': ek, 'Story1': s1k, 'Story2': s2k},
                                'common_points': len(e), 'total_delta_EG_0_50': total_g, 'total_delta_EL_0_50': total_l,
                                'negative_EL_increments_preserved': sum(y < x for x, y in zip(el, el[1:])),
                                'negative_EG_increments': sum(y < x for x, y in zip(eg, eg[1:])),
                                'peak_tie_counts': {r['window']: sum(abs(net[k]) == abs(r['N_kN']) for k in range(r['start_s'] * 50, r['end_s'] * 50 + 1)) for r in local}})
    counts = {'window_count': len(window_rows), 'pair_count': len(pair_rows),
              'eligible_window_count': sum(w['eligible'] for w in window_rows),
              'eligible_pair_count': sum(p['eligible'] for p in pair_rows),
              'energy_matched_pair_count': sum(p['energy_matched'] for p in pair_rows),
              'witness_count': sum(p['witness'] for p in pair_rows)}
    assert all(arun[k] == v for k, v in counts.items())
    verdict = ('supported_candidate' if counts['witness_count'] else 'not_supported_under_frozen_protocol'
               if counts['energy_matched_pair_count'] else 'not_testable_no_eligible_match')
    assert verdict == arun['verdict']
    files = [protocol, manifest_path, cache / em['cache'], cache / fm['cache'], author / 'R002_im001_firstcalc.py',
             author / 'R002-im001-results.md', af / 'windows.csv', af / 'pairs.csv', arun_path, author / 'R002-validation.json']
    for name, rows in [('review_windows.csv', window_rows), ('review_pairs.csv', pair_rows)]:
        with (out / name).open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    record = {'recorded_at': datetime.now(timezone(timedelta(hours=8))).isoformat(), 'checks_passed': True,
              'script_sha256': sha(Path(__file__)), 'python': platform.python_version(), 'numpy': np.__version__,
              'verdict': verdict, **counts, 'all_window_and_pair_fields_checked': True,
              'cases': diagnostics, 'nearest_eligible_pair': min((p for p in pair_rows if p['eligible']), key=lambda p: p['delta_R_relative']),
              'source_workbook_sha256_inherited': m['sha256'], 'no_raw_XLSX_Y_or_IM002': True,
              'inputs': [{'path': str(p.resolve()), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files],
              'limits': ['Frozen operational diagnostic, not novel theory or fair-equivalent-model falsification.',
                         'No official section sign/composition or P/U1/25kg inertial interface certification.']}
    (out / 'review_record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'verdict': verdict, **counts, 'nearest_eligible_pair': record['nearest_eligible_pair'], 'cases': diagnostics}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--cache', required=True, type=Path)
    p.add_argument('--author', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    a = p.parse_args(); run(a.cache, a.author, a.out)
