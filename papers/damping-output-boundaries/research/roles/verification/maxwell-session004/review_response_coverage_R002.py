"""Independent integer-grid review of four frozen response caches; no XLSX read."""
import argparse
import csv
import hashlib
import json
import math
import platform
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_csv(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def run(cache, evidence, out):
    out.mkdir(parents=True, exist_ok=False)
    mp = cache / 'manifest.json'
    m = json.loads(mp.read_text(encoding='utf-8'))
    assert m['complete'] and m['source_unchanged']
    source_audit = json.loads((evidence / 'response_coverage_audit.json').read_text(encoding='utf-8'))
    assert source_audit['source_sha256_from_existing_manifest'] == m['sha256']
    dimensions = ['Story', 'Location', 'Diaphragm', 'Direction', 'Output Case', 'Case Type']
    cov = load_csv(evidence / 'response_coverage.csv')
    source_rows = {(r['table'], *(r[k] for k in dimensions)): r for r in cov}
    assert len(source_rows) == len(cov)
    raw_rows = load_csv(evidence / 'drift_raw_summary.csv')
    raw = {(r['Story'], r['Direction'], r['Output Case'], r['Case Type']): r for r in raw_rows}
    assert len(raw) == len(raw_rows) == 144
    tables = m['tables']
    dt = .02

    def grid(values):
        times = [float(x) for x in values]
        assert all(math.isfinite(x) for x in times)
        assert all(b > a for a, b in zip(times, times[1:]))
        ticks = [round(x / dt) for x in times]
        assert len(set(ticks)) == len(ticks)
        assert all(abs(x - k * dt) < 1e-10 for x, k in zip(times, ticks))
        return ticks

    paths = [mp]
    base = tables['Base Reactions']; bp = cache / base['cache']; paths.append(bp)
    references = {}
    with np.load(bp, allow_pickle=False) as z:
        ci = base['columns'].index('Time')
        for key, meta in base['groups'].items():
            case = meta['keys']['Output Case']; assert case not in references
            assert meta['keys']['Case Type'] == 'NonModHist'
            ticks = grid(z[key][:, ci])
            assert ticks == list(range(ticks[-1] + 1))
            references[case] = set(ticks)
    cases = {'RH4X', 'RH4Y', 'SHW4X', 'SHW4Y', 'SHW7X', 'SHW7Y'}
    assert set(references) == cases
    names = ['Story Forces', 'Diaphragm CM Displacements', 'Story Accelerations', 'Story Drifts']
    result_rows, statistics, locations, diaphragms = [], {}, set(), defaultdict(set)
    acceleration_stories, drift_partition = set(), defaultdict(list)
    max_alignment_error = 0
    for name in names:
        meta = tables[name]; p = cache / meta['cache']; paths.append(p)
        assert not meta['reaches_excel_row_limit']
        index = {n: i for i, n in enumerate(meta['columns'])}
        local = []
        with np.load(p, allow_pickle=False) as arrays:
            for key, group in meta['groups'].items():
                a = arrays[key]; k = group['keys']; assert k['Case Type'] == 'NonModHist'
                assert np.isfinite(a).all() and len(a) == group['n']
                ticks = grid(a[:, index['Time']]); observed = set(ticks)
                reference = references[k['Output Case']]
                ident = (name, *(k.get(x, '') for x in dimensions))
                original = source_rows[ident]
                sr = a[:, index['SourceRow']]
                assert all(x == int(x) for x in sr) and all(y > x for x, y in zip(sr, sr[1:]))
                row = {'table': name, **{x: k.get(x, '') for x in dimensions},
                       'rows': len(a), 'reference_rows': len(reference),
                       'missing_times': len(reference - observed), 'outside_reference': len(observed - reference),
                       't0': float(a[0, index['Time']]), 't1': float(a[-1, index['Time']]),
                       'first_source_row': int(sr[0]), 'last_source_row': int(sr[-1])}
                for field in ['rows', 'reference_rows', 'missing_times', 'outside_reference', 'first_source_row', 'last_source_row']:
                    assert row[field] == int(original[field]), (ident, field)
                for field in ['t0', 't1']:
                    assert math.isclose(row[field], float(original[field]), abs_tol=1e-12)
                max_alignment_error = max(max_alignment_error, *(abs(float(t) - j * dt) for t, j in zip(a[:, index['Time']], ticks)))
                if name == 'Story Forces': locations.add(k['Location'])
                elif name == 'Diaphragm CM Displacements': diaphragms[k['Story']].add(k['Diaphragm'])
                elif name == 'Story Accelerations': acceleration_stories.add(k['Story'])
                else:
                    rr = raw[(k['Story'], k['Direction'], k['Output Case'], k['Case Type'])]
                    drift = [float(x) for x in a[:, index['Drift']]]
                    ip = max(range(len(drift)), key=lambda i: abs(drift[i]))
                    assert len(a) == int(rr['n'])
                    assert sum(x < 0 for x in drift) == int(rr['negative_rows'])
                    assert sum(x == 0 for x in drift) == int(rr['zero_rows'])
                    assert math.isclose(drift[ip], float(rr['peak_value']), abs_tol=1e-15, rel_tol=1e-12)
                    assert math.isclose(float(a[ip, index['Time']]), float(rr['peak_time']), abs_tol=1e-12)
                    assert int(sr[ip]) == int(rr['peak_source_row'])
                    row.update({'record_peak': drift[ip], 'peak_time': float(a[ip, index['Time']]),
                                'peak_source_row': int(sr[ip]), 'raw_summary_unique_labels': int(rr['unique_labels'])})
                    direction_class = 'same_suffix_direction' if k['Output Case'][-1] == k['Direction'] else 'cross_suffix_direction'
                    drift_partition[direction_class].append(row)
                local.append(row); result_rows.append(row)
        assert sum(r['rows'] for r in local) == meta['data_rows']
        stats = {'groups': len(local), 'groups_with_missing_times': sum(r['missing_times'] > 0 for r in local),
                 'missing_times_total': sum(r['missing_times'] for r in local),
                 'outside_times_total': sum(r['outside_reference'] for r in local),
                 'data_rows': sum(r['rows'] for r in local)}
        assert all(stats[k] == v for k, v in source_audit['table_coverage'][name].items())
        statistics[name] = stats
    assert len(result_rows) == len(cov) == 402
    assert locations == {'Bottom'}
    expected_diaphragms = {f'Story{i}': {'D1', 'D2'} if 3 <= i <= 8 else {'D1'} for i in range(1, 13)}
    assert dict(diaphragms) == expected_diaphragms
    assert acceleration_stories == {'Base', *(f'Story{i}' for i in range(1, 13))}
    assert not {'Diaphragm', 'Label', 'Unique Name'} & set(tables['Story Accelerations']['headers'])
    partition = {k: {'groups': len(v), 'missing_min': min(r['missing_times'] for r in v),
                    'missing_max': max(r['missing_times'] for r in v),
                    'missing_sum': sum(r['missing_times'] for r in v)} for k, v in drift_partition.items()}
    sparse = max((r for r in result_rows if r['table'] == 'Story Drifts'), key=lambda r: r['missing_times'])
    label_counts = [int(r['unique_labels']) for r in raw_rows]
    paths += [evidence / n for n in ['audit_response_coverage.py', '楼层响应定义与覆盖补充核查.md',
                                    'response_coverage_audit.json', 'response_coverage.csv', 'drift_raw_summary.csv']]
    record = {'recorded_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'script_sha256': digest(Path(__file__)), 'python': platform.python_version(), 'numpy': np.__version__,
              'source_sha256_inherited_not_rehashed': m['sha256'], 'checks_passed': True,
              'grid_method': 'Integer ticks with dt=0.02s, alignment error <1e-10s; no resampling or interpolation.',
              'max_alignment_error_s': max_alignment_error, 'table_coverage': statistics,
              'story_force_locations': sorted(locations),
              'diaphragms_by_story': {k: sorted(v) for k, v in diaphragms.items()},
              'acceleration_stories': sorted(acceleration_stories), 'drift_partition': partition,
              'sparsest_drift': sparse, 'raw_summary_label_range': [min(label_counts), max(label_counts)],
              'inputs': [{'path': str(p.resolve()), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in paths],
              'limits': ['No raw XLSX extraction repeated.', 'Label and coordinates are absent from caches; use audited auxiliary raw summary, not second native validation.',
                         'No omission-generation rule inferred.', 'No absolute/relative classification of Story Accelerations made.',
                         'Complete export grid does not certify continuous peak or complete free tail.']}
    (out / 'response_review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    fields = list(result_rows[0]) + ['record_peak', 'peak_time', 'peak_source_row', 'raw_summary_unique_labels']
    with (out / 'response_review_groups.csv').open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(result_rows)
    print(json.dumps({k: record[k] for k in ['checks_passed', 'table_coverage', 'drift_partition', 'sparsest_drift', 'raw_summary_label_range', 'max_alignment_error_s']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--cache', required=True, type=Path)
    p.add_argument('--evidence', required=True, type=Path); p.add_argument('--out', required=True, type=Path)
    a = p.parse_args(); run(a.cache, a.evidence, a.out)
