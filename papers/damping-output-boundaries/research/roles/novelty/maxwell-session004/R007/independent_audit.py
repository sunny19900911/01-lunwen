"""R007: independent exact-decimal screening audit, standard library only."""
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLES = HERE.parents[2]
AUTHOR = ROLES / 'ideation/maxwell-session004/R006-force-screening'
SOURCE = ROLES / 'experiments/maxwell-session004/R006-device-distribution/device_record_summary_r006.csv'


def read_csv(p):
    with p.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def select_second(values):
    threshold = sorted(values.values(), reverse=True)[1]
    return {i for i, value in values.items() if value >= threshold}, threshold


def diagnose(peaks, scores):
    chosen, threshold = select_second(scores)
    peak2, _ = select_second(peaks)
    largest = max(peaks.values())
    picked = max(peaks[i] for i in chosen)
    controllers = {i for i, value in peaks.items() if value == largest}
    covered = chosen & peak2
    return dict(A=chosen, threshold=threshold, B=peak2, Pmax=largest, Psel=picked,
                G=controllers, covered=covered, LF=None if largest == 0 else 1-picked/largest,
                recall=Q(len(covered), len(peak2)), omitted=peak2-chosen,
                all_omitted=not bool(chosen & controllers),
                any_omitted=bool(controllers-chosen))


def synthetic_checks():
    p = dict(a=Q(10), b=Q(9), c=Q(8), d=Q(7))
    a = diagnose(p, dict(a=Q(1), b=Q(4), c=Q(3), d=Q(2)))
    assert a['LF'] == Q(1, 10) and a['recall'] == Q(1, 2) and a['all_omitted']
    b = diagnose(p, dict(a=Q(4), b=Q(1), c=Q(3), d=Q(2)))
    assert b['LF'] == 0 and b['recall'] == Q(1, 2)
    c = diagnose(dict(a=Q(10), b=Q(10), c=Q(8), d=Q(7)),
                 dict(a=Q(4), b=Q(1), c=Q(3), d=Q(2)))
    assert c['LF'] == 0 and c['any_omitted'] and not c['all_omitted']
    d = diagnose(dict(a=Q(10), b=Q(9), c=Q(9), d=Q(7)),
                 dict(a=Q(4), b=Q(1), c=Q(3), d=Q(2)))
    assert len(d['B']) == 3 and d['recall'] == Q(2, 3)
    e = diagnose(p, dict(a=Q(4), b=Q(3), c=Q(3), d=Q(2)))
    assert e['A'] == {'a', 'b', 'c'}
    f = diagnose(dict.fromkeys(p, Q(0)), dict(a=Q(4), b=Q(1), c=Q(3), d=Q(2)))
    assert f['LF'] is None and f['recall'] == Q(1, 2)
    g = diagnose(p, dict.fromkeys(p, Q(0)))
    assert g['A'] == set(p) and g['LF'] == 0 and g['recall'] == 1
    h = diagnose(p, dict(a=Q(-1), b=Q(-2), c=Q(-3), d=Q(-4)))
    assert h['A'] == {'a', 'b'}
    return 8


def names(value):
    return set(value.split(';')) if value else set()


def check(condition, message):
    if not condition:
        errors.append(message)


freeze = json.loads((HERE/'input-freeze.json').read_text(encoding='utf-8'))
for item in freeze['inputs']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest() == item['sha256']
synthetic_count = synthetic_checks()
rows = read_csv(SOURCE)
groups = defaultdict(dict)
for row in rows:
    key = (row['Case'], row['Story'])
    assert row['Link'] not in groups[key]
    assert Q(row['max_abs_native_P_kN']) >= 0
    groups[key][row['Link']] = row
assert len(rows) == 192 and len(groups) == 24 and all(len(g) == 8 for g in groups.values())
assert {k[0] for k in groups} == {'RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y'}
assert {k[1] for k in groups} == {'Story8','Story9','Story10','Story11'}
errors = []
results = []
expected_omitted = {}
counts = {}
max_display_error = Q(0)
for method, field, filename in [
    ('conditional_Dport','Dport_conditional_kNm','conditional_Dport_groups.csv'),
    ('native_Wtrap','Wtrap_native_kNm','native_Wtrap_groups.csv')]:
    published = read_csv(AUTHOR/'results'/filename)
    indexed = {(r['Case'],r['Story']):r for r in published}
    check(len(published) == len(indexed) == 24 and set(indexed) == set(groups), method+' group identity')
    count = dict(groups=24, positive_LF=0, LF_zero_incomplete_recall=0, full_recall=0,
                 undefined_LF=0, energy_ties=0, peak2_ties=0, maximum_ties=0,
                 all_global_max_omitted=0, any_global_max_omitted=0)
    for key, g in sorted(groups.items()):
        peaks = {i:Q(r['max_abs_native_P_kN']) for i,r in g.items()}
        scores = {i:Q(r[field]) for i,r in g.items()}
        d = diagnose(peaks, scores)
        r = indexed[key]
        prefix = '/'.join((method,)+key)
        state = 'none_covered' if d['all_omitted'] else 'partially_covered' if d['any_omitted'] else 'all_covered'
        set_fields = dict(selected_ids=d['A'],global_max_ids=d['G'],
                          omitted_global_max_ids=d['G']-d['A'],peak_top2_ids=d['B'],
                          covered_peak_top2_ids=d['covered'],omitted_peak_top2_ids=d['omitted'])
        for fieldname, expected in set_fields.items():
            check(names(r[fieldname]) == expected, prefix+' '+fieldname)
        for fieldname, expected in dict(n_devices=8, selected_count=len(d['A']),
                peak_top2_count=len(d['B']),covered_peak_top2_count=len(d['covered'])).items():
            check(int(r[fieldname]) == expected, prefix+' '+fieldname)
        check(r['method'] == method, prefix+' method')
        check(r['global_max_coverage_state'] == state, prefix+' coverage state')
        for fieldname, expected in [('all_global_max_omitted',d['all_omitted']),('any_global_max_omitted',d['any_omitted'])]:
            check(r[fieldname] == str(expected), prefix+' '+fieldname)
        check(Q(r['peak_top2_recall_exact']) == d['recall'], prefix+' recall exact')
        check((not r['L_F_exact'] and d['LF'] is None) or Q(r['L_F_exact']) == d['LF'], prefix+' LF exact')
        check(r['LF_reason'] == ('zero_group_peak' if d['LF'] is None else ''), prefix+' LF reason')
        for fieldname, expected in [('score_second_threshold',d['threshold']),('Pmax_kN',d['Pmax']),
                                     ('Psel_kN',d['Psel']),('L_F',d['LF']),('peak_top2_recall',d['recall'])]:
            if expected is None:
                check(r[fieldname] == '', prefix+' undefined '+fieldname)
            else:
                err = abs(Q(r[fieldname])-expected)
                max_display_error = max(max_display_error,err)
                check(err <= Q(1,10**14)*max(1,abs(expected)), prefix+' displayed '+fieldname)
        selected_values = json.loads(r['selected_peak_values_json'])
        check(set(selected_values) == d['A'], prefix+' selected JSON ids')
        for i,v in selected_values.items():
            check(Q(v) == peaks[i], prefix+' selected JSON peak '+i)
        count['positive_LF'] += d['LF'] is not None and d['LF'] > 0
        count['LF_zero_incomplete_recall'] += d['LF'] == 0 and d['recall'] < 1
        count['full_recall'] += d['recall'] == 1
        count['undefined_LF'] += d['LF'] is None
        count['energy_ties'] += len(d['A']) > 2
        count['peak2_ties'] += len(d['B']) > 2
        count['maximum_ties'] += len(d['G']) > 1
        count['all_global_max_omitted'] += d['all_omitted']
        count['any_global_max_omitted'] += d['any_omitted']
        for i in d['omitted']:
            expected_omitted[(method,)+key+(i,)] = (d, g[i])
        record = dict(method=method,Case=key[0],Story=key[1])
        record.update({k:(sorted(v) if isinstance(v,set) else str(v) if isinstance(v,Q) else v) for k,v in d.items()})
        results.append(record)
    counts[method] = count

for filename, global_only in [('omitted_peak_top2.csv',False),('omitted_global_max.csv',True)]:
    table = read_csv(AUTHOR/'results'/filename)
    expected = {k:v for k,v in expected_omitted.items() if not global_only or k[-1] in v[0]['G']}
    keys = [(r['method'],r['Case'],r['Story'],r['Link']) for r in table]
    check(len(keys) == len(set(keys)) and set(keys) == set(expected), filename+' identities')
    for r in table:
        key=(r['method'],r['Case'],r['Story'],r['Link']); d,source=expected[key]
        check(Q(r['native_Ppeak_kN']) == Q(source['max_abs_native_P_kN']), filename+' native peak '+str(key))
        check(Q(r['L_F_exact']) == d['LF'], filename+' exact LF '+str(key))
        check(r['is_global_max_controller'] == str(key[-1] in d['G']), filename+' maximum flag '+str(key))
        check(json.loads(r['native_force_peak_controllers_json']) == json.loads(source['force_peak_controllers_json']),filename+' source locator '+str(key))
        for fieldname,expected_value in [('group_Pmax_kN',d['Pmax']),('selected_Pmax_kN',d['Psel']),('L_F',d['LF']),('peak_top2_recall',d['recall'])]:
            check(abs(Q(r[fieldname])-expected_value) <= Q(1,10**14)*max(1,abs(expected_value)), filename+' display '+fieldname)
        state='none_covered' if d['all_omitted'] else 'partially_covered' if d['any_omitted'] else 'all_covered'
        check(r['global_max_coverage_state'] == state, filename+' coverage state')

same = sum(a['A'] == b['A'] for a,b in zip(results[:24],results[24:]))
changed = [i['path'] for i in freeze['inputs'] if hashlib.sha256(Path(i['path']).read_bytes()).hexdigest()!=i['sha256']]
check(not changed, 'frozen source mutation')
output = dict(computed_at=datetime.now().astimezone().isoformat(timespec='seconds'),
              standard_library_only=True,author_code_read_or_executed=False,NPZ_or_Excel_read=False,
              synthetic_checks=synthetic_count,source_rows=len(rows),group_counts=counts,
              W_D_same_selected_groups=same,omitted_peak_top2_rows=len(expected_omitted),
              omitted_global_max_rows=sum(k[-1] in v[0]['G'] for k,v in expected_omitted.items()),
              max_scalar_display_absolute_error=str(max_display_error),
              exact_LF_and_recall_comparison=True,input_changed=changed,errors=errors,results=results)
with (HERE/'recomputed.json').open('x',encoding='utf-8') as stream:
    json.dump(output,stream,ensure_ascii=False,indent=2); stream.write('\n')
print(json.dumps({k:v for k,v in output.items() if k!='results'},ensure_ascii=False,indent=2))
assert not errors, errors
