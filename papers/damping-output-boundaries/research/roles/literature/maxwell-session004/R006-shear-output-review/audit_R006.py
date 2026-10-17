"""Independent arithmetic review of existing CSI caches; never opens Excel."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import csv
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / 'protocol-R006.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_csv(name, rows):
    with (HERE / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    protocol_sha = sha(PROTOCOL)
    p = json.loads(PROTOCOL.read_text(encoding='utf-8'))
    inputs = {Path(x['path']).name: Path(x['path']) for x in p['inputs']}
    for x in p['inputs']:
        assert sha(Path(x['path'])) == x['sha256'], x['path']
    m = json.loads(inputs['manifest.json'].read_text(encoding='utf-8'))
    prior = json.loads(inputs['validation.json'].read_text(encoding='utf-8'))
    assert m['sha256'] == prior['source_sha256_inherited_from_manifest']
    for name, h in prior['inputs'].items():
        assert sha(Path(name)) == h
    assert sha(inputs['audit_shear_outputs.py']) == prior['script_sha256']
    tables = m['tables']
    data = {}
    for name in ['Base Reactions', 'Story Forces', 'Story Accelerations']:
        t = tables[name]
        cols = t['columns']
        groups = {}
        with np.load(inputs[t['cache']], allow_pickle=False) as z:
            assert set(z.files) == set(t['groups'])
            for gid, meta in t['groups'].items():
                key = tuple(sorted(meta['keys'].items()))
                assert key not in groups
                if name == 'Story Accelerations' and meta['keys']['Story'] != 'Base':
                    continue
                a = z[gid]
                assert a.ndim == 2 and a.shape == (meta['n'], len(cols))
                assert np.isfinite(a).all()
                assert np.all(np.diff(a[:, cols.index('Time')]) > 0)
                assert np.all(a[:, cols.index('SourceRow')] == np.floor(a[:, cols.index('SourceRow')]))
                groups[key] = a
        data[name] = groups
    def get(name, **keys):
        return data[name][tuple(sorted(keys.items()))]
    def col(name, a, field):
        return a[:, tables[name]['columns'].index(field)]
    def unit(name, field):
        t = tables[name]
        return t['units'][t['headers'].index(field)]
    def peaks(y):
        peak = float(np.max(np.abs(y)))
        ii = np.flatnonzero(np.abs(y) == peak)
        return peak, ii
    cases = sorted(dict(k)['Output Case'] for k in data['Base Reactions'])
    assert len(cases) == len(set(cases)) == 6
    base_rows, pairs, ties, direction_rows = [], [], [], []
    for case in cases:
        common = {'Output Case': case, 'Case Type': 'NonModHist'}
        b = get('Base Reactions', **common)
        first = get('Story Forces', **common, Story='Story1', Location='Bottom')
        t = col('Base Reactions', b, 'Time')
        assert np.array_equal(t, col('Story Forces', first, 'Time'))
        for direction in ['X', 'Y']:
            bv = col('Base Reactions', b, 'F' + direction)
            sv = col('Story Forces', first, 'V' + direction)
            assert unit('Base Reactions', 'F' + direction) == unit('Story Forces', 'V' + direction) == 'kN'
            peak, ii = peaks(bv)
            i = int(ii[0])
            base_rows.append({'Case': case, 'CaseType': 'NonModHist', 'Direction': direction,
                'n': len(t), 'exact_same_signed_history': bool(np.array_equal(bv, sv)),
                'max_absolute_difference_kN': float(np.max(np.abs(bv - sv))),
                'base_peak_abs_kN': peak, 'peak_time_s': float(t[i]),
                'Base_SourceRow_at_peak': int(col('Base Reactions', b, 'SourceRow')[i]),
                'Story1_SourceRow_at_peak': int(col('Story Forces', first, 'SourceRow')[i])})
        direction = case[-1]
        assert direction in ['X', 'Y']
        acc = get('Story Accelerations', **common, Story='Base')
        assert np.array_equal(t, col('Story Accelerations', acc, 'Time'))
        maxima = {d: float(np.max(np.abs(col('Story Accelerations', acc, 'U' + d)))) for d in ['X', 'Y']}
        assert maxima[direction] > 0 and maxima['Y' if direction == 'X' else 'X'] == 0
        direction_rows.append({'Case': case, 'selected_component': direction, 'Base_horizontal_component_abs_peaks': maxima})
        for lower in range(1, 12):
            a = get('Story Forces', **common, Story=f'Story{lower}', Location='Bottom')
            b2 = get('Story Forces', **common, Story=f'Story{lower+1}', Location='Bottom')
            assert np.array_equal(t, col('Story Forces', a, 'Time'))
            assert np.array_equal(t, col('Story Forces', b2, 'Time'))
            av, bv = col('Story Forces', a, 'V' + direction), col('Story Forces', b2, 'V' + direction)
            pa, ia = peaks(av)
            pb, ib = peaks(bv)
            i, j = int(ib[0]), int(ia[0])
            n = float(av[i] - bv[i])
            sn = float(np.sign(bv[i]) * n)
            row = {'Case': case, 'CaseType': 'NonModHist', 'Direction': direction,
                'lower_Bottom': f'Story{lower}', 'upper_Bottom': f'Story{lower+1}',
                'lower_abs_record_peak_kN': pa, 'upper_abs_record_peak_kN': pb,
                'upper_peak_exceeds_lower': pb > pa, 'peak_gap_kN': pb - pa,
                'peak_gap_over_lower': (pb - pa) / pa, 'upper_peak_time_s': float(t[i]),
                'upper_peak_tie_count': len(ib), 'lower_signed_at_upper_peak_kN': float(av[i]),
                'upper_signed_at_upper_peak_kN': float(bv[i]),
                'net_lower_minus_upper_at_upper_peak_kN': n, 'upper_sign_times_net_kN': sn,
                'lower_SourceRow_at_upper_peak': int(col('Story Forces', a, 'SourceRow')[i]),
                'upper_SourceRow_at_upper_peak': int(col('Story Forces', b2, 'SourceRow')[i]),
                'lower_peak_time_s': float(t[j]), 'lower_peak_tie_count': len(ia),
                'lower_SourceRow_at_own_peak': int(col('Story Forces', a, 'SourceRow')[j])}
            pairs.append(row)
            for index in ib:
                nn = float(av[index] - bv[index])
                signed_n = float(np.sign(bv[index]) * nn)
                if pb > pa:
                    assert signed_n <= pa - pb + p['inequality_roundoff_absolute_tolerance_kN']
                    assert pa - pb < 0 and signed_n < 0
                ties.append({'Case': case, 'lower_Bottom': row['lower_Bottom'], 'upper_Bottom': row['upper_Bottom'],
                    'upper_peak_time_s': float(t[index]), 'net_kN': nn, 'signed_net_kN': signed_n})
    def compare(filename, rows, keys):
        with inputs[filename].open(encoding='utf-8-sig', newline='') as f:
            expected = list(csv.DictReader(f))
        left = {tuple(r[k] for k in keys): r for r in rows}
        right = {tuple(r[k] for k in keys): r for r in expected}
        assert len(left) == len(rows) and len(right) == len(expected)
        assert set(left) == set(right)
        errors = []
        for key, row in right.items():
            for field, value in row.items():
                actual = left[key][field]
                ok = (value == str(actual)) if isinstance(actual, (str, bool)) else float(value) == actual
                if not ok:
                    errors.append({'key': key, 'field': field, 'source': value, 'computed': actual})
        return errors
    reversals = [r for r in pairs if r['upper_peak_exceeds_lower']]
    differences = {'base': compare('base_vs_story1.csv', base_rows, ['Case', 'Direction']),
        'pairs': compare('all_66_adjacent_peak_order_pairs.csv', pairs, ['Case', 'lower_Bottom', 'upper_Bottom']),
        'reversals': compare('observed_peak_order_reversals.csv', reversals, ['Case', 'lower_Bottom', 'upper_Bottom'])}
    assert len(base_rows) == 12 and sum(r['n'] for r in base_rows) == 32592
    assert all(r['exact_same_signed_history'] for r in base_rows)
    assert len(pairs) == 66 and len(reversals) == 4
    for x in p['inputs']:
        assert sha(Path(x['path'])) == x['sha256']
    assert sha(PROTOCOL) == protocol_sha
    write_csv('base-vs-story1-reviewed.csv', base_rows)
    write_csv('all66-pairs-reviewed.csv', pairs)
    write_csv('four-reversals-reviewed.csv', reversals)
    result = {'session': p['session'], 'role': 3, 'started_at': p['started_at'],
        'computed_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'protocol_sha256': protocol_sha, 'script_sha256': sha(Path(__file__)),
        'inputs': p['inputs'], 'inputs_unchanged': True, 'source_sha_inherited_not_recomputed': m['sha256'],
        'checks': {'groups_unique': True, 'finite_selected_arrays': True, 'strict_time_grids_exactly_equal': True,
            'units_kN': True, 'base_component_histories': 12, 'component_samples': 32592,
            'maximum_base_story1_difference_kN': max(r['max_absolute_difference_kN'] for r in base_rows),
            'all_adjacent_pairs': 66, 'reversals': 4, 'all_upper_peak_ties_retained': True,
            'same_time_inequality_checked': True},
        'direction_checks': direction_rows, 'differences_vs_source_csvs': differences,
        'all_source_csv_fields_exactly_match': not any(differences.values()), 'reversals': reversals,
        'scope': 'Independent arithmetic on same-source caches; not a new raw workbook reader, causal damping comparison, mode identification or device-force attribution.',
        'operations': {'Excel_reads': 0, 'NPZ_caches': 3, 'fits': 0, 'solver_runs': 0, 'network': 0, 'Git': 0}}
    (HERE / 'validation-R006.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'checks': result['checks'], 'source_csv_match': result['all_source_csv_fields_exactly_match'],
        'differences': differences, 'reversals': reversals}, ensure_ascii=False))


if __name__ == '__main__':
    main()
