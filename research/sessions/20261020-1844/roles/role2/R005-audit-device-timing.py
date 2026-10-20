from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import csv
import hashlib
import json
import numpy as np

OUT = Path(__file__).resolve().parent
SRC = OUT.parent / 'role4'
ROOT = OUT.parents[4]
START = datetime.fromisoformat('2026-10-20T19:56:19.406027+08:00')
DEADLINE = START + timedelta(minutes=10)


def ident(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def rc(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def same(a, b):
    assert np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), rtol=1e-12, atol=1e-8), (a, b)


def js(name, obj):
    p = OUT / name
    assert not p.exists(), p
    p.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    json.loads(p.read_text(encoding='utf-8'))


assert datetime.now(START.tzinfo) < DEADLINE
assert not (OUT / 'R005-validation.json').exists()
manifest = SRC / 'R005-delivery-manifest.json'
sources = [ident(manifest)]
for x in json.loads(manifest.read_text(encoding='utf-8'))['files']:
    got = ident(Path(x['path']))
    assert got['bytes'] == x['bytes'] and got['sha256'] == x['sha256']
    sources.append(got)
freeze = json.loads((SRC / 'R005-input-freeze.json').read_text(encoding='utf-8'))
for x in freeze['inputs']:
    got = ident(Path(x['path']))
    assert got['bytes'] == x['bytes'] and got['sha256'] == x['sha256']
    sources.append(got)
paths = [Path(x['path']) for x in freeze['inputs']]
hp = next(p for p in paths if p.name == 'local_history_manifest_r006.json')
zp = next(p for p in paths if p.name == 'local_paired_histories_r006.npz')
gp = next(p for p in paths if p.name == 'R001-link-geometry-88.csv')
cp = next(p for p in paths if p.name == 'manifest.json')
hm = json.loads(hp.read_text(encoding='utf-8'))
cm = json.loads(cp.read_text(encoding='utf-8'))
geom = {(r['Story'], r['Link']): r for r in rc(gp)}
assert len(geom) == 88
groups = defaultdict(list)
for r in hm['arrays']:
    groups[r['Story'], r['Case']].append(r)
assert len(hm['arrays']) == 192 and len(groups) == 24
assert len({(r['Story'], r['Link']) for r in hm['arrays']}) == 32
assert {s for s, c in groups} == {'Story8', 'Story9', 'Story10', 'Story11'}
for (story, case), rr in groups.items():
    assert len(rr) == 8 and len({r['Link'] for r in rr}) == 8
    assert {r['Link'] for r in rr} == {link for s, link in geom if s == story}
    for r in rr:
        assert r['key'].endswith('__' + case)

summary = rc(SRC / 'R005-Story8-six-layer-summary.csv')
devices = rc(SRC / 'R005-Story8-device-at-QT-peak-48.csv')
coverage = rc(SRC / 'R005-coverage-24.csv')
assert len(summary) == 6 and len(devices) == 48 and len(coverage) == 24
si = {r['Case']: r for r in summary}
di = {(r['Case'], r['Link']): r for r in devices}
assert len(si) == 6 and len(di) == 48
assert rc(SRC / 'R005-first-two-layer-summary.csv') == summary[:2]
assert rc(SRC / 'R005-first-two-device-at-QT-peak-16.csv') == devices[:16]
for r in coverage:
    assert int(r['complete_devices']) == 8
    assert all(r[k] == 'True' for k in ['P_I_equals_P_J_once', 'time_matches_Base_and_Story_exactly', 'P_U1_finite', 'geometry_matches'])
for case, r in si.items():
    assert r['Story'] == 'Story8' and r['Axis'] == case[-1]
    rr = [x for x in devices if x['Case'] == case]
    assert len(rr) == 8 and sum(x['axis_projection_nonzero'] == 'True' for x in rr) == 4
    same(sum(float(x['qJ_resisting_at_QT_peak_kN']) for x in rr), r['QD_J_resisting_at_QT_peak_kN'])
    same(sum(float(x['qJ_resisting_at_layer_QD_peak_kN']) for x in rr), r['QD_J_resisting_signed_at_own_peak_kN'])
    same(float(r['t_QD_abs_peak_s']) - float(r['t_QT_peak_s']), r['t_QD_minus_t_QT_s'])
    same(float(r['QD_J_resisting_at_QT_peak_kN']), -float(r['QD_J_external_at_QT_peak_kN']))
    pd, pt = float(r['QD_J_resisting_peak_abs_kN']), float(r['QT_peak_abs_kN'])
    same(abs(float(r['QD_J_resisting_signed_at_own_peak_kN'])), pd)
    same(abs(float(r['QT_signed_at_peak_kN'])), pt)
    same(100 * float(r['QD_J_resisting_at_QT_peak_kN']) / pd, r['QD_at_QT_signed_percent_own_abs_peak'])
    same(100 * abs(float(r['QD_J_resisting_at_QT_peak_kN'])) / pd, r['QD_at_QT_abs_percent_own_abs_peak'])
    same(100 * abs(float(r['QT_signed_at_QD_abs_peak_kN'])) / pt, r['QT_at_QD_abs_percent_own_abs_peak'])
    for x in rr:
        g = geom[x['Story'], x['Link']]
        assert x['I_Point'] == g['I_Point'] and x['J_Point'] == g['J_Point']
        assert g['I_Story'] == 'Story7' and g['J_Story'] == 'Story8'
        delta = np.array([float(g['J_' + a + '_m']) - float(g['I_' + a + '_m']) for a in 'XYZ'])
        n = delta / np.linalg.norm(delta)
        assert delta[2] > 0
        same(n, [g['nx'], g['ny'], g['nz']])
        na = n['XY'.index(case[-1])]
        same(na, x['n_axis'])
        same(x['geometry_SourceRow'], g['link_source_row'])
        same(float(x['qJ_resisting_at_QT_peak_kN']), na * float(x['P_at_QT_peak_kN']))
        same(float(x['qJ_external_at_QT_peak_kN']), -float(x['qJ_resisting_at_QT_peak_kN']))
        qp = abs(na) * float(x['P_abs_peak_kN'])
        same(qp, x['qJ_resisting_abs_peak_kN'])
        same(100 * float(x['qJ_resisting_at_QT_peak_kN']) / pd, x['q_at_QT_signed_percent_layer_QD_abs_peak'])
        if qp > 1e-10:
            same(x['t_qJ_abs_peak_s'], x['t_P_peak_s'])
            same(100 * float(x['qJ_resisting_at_QT_peak_kN']) / qp, x['q_at_QT_signed_percent_device_own_abs_peak'])
            same(100 * abs(float(x['qJ_resisting_at_QT_peak_kN'])) / qp, x['q_at_QT_abs_percent_device_own_abs_peak'])
        else:
            assert x['t_qJ_abs_peak_s'] == x['q_at_QT_signed_percent_device_own_abs_peak'] == x['q_at_QT_abs_percent_device_own_abs_peak'] == ''

sf, br = cm['tables']['Story Forces'], cm['tables']['Base Reactions']
assert sf['units'][sf['headers'].index('VX')] == sf['units'][sf['headers'].index('VY')] == 'kN'
recomputed = []
with np.load(zp, allow_pickle=False) as z, np.load(cp.parent / sf['cache'], allow_pickle=False) as sz, np.load(cp.parent / br['cache'], allow_pickle=False) as bz:
    for case in ['RH4X', 'RH4Y']:
        r = si[case]
        keys = [k for k, g in sf['groups'].items() if g['keys']['Story'] == 'Story8' and g['keys']['Output Case'] == case and g['keys']['Location'] == 'Bottom']
        assert len(keys) == 1
        arr = sz[keys[0]]
        col = sf['columns']
        t, qt = arr[:, col.index('Time')], arr[:, col.index('V' + case[-1])]
        bk = next(k for k, g in br['groups'].items() if g['keys']['Output Case'] == case)
        assert np.array_equal(t, bz[bk][:, br['columns'].index('Time')])
        assert np.all(np.diff(t) > 0) and np.isfinite(arr).all()
        parts, records = [], []
        for a in sorted(groups['Story8', case], key=lambda x: x['Link']):
            ar, ac = z[a['key']], a['columns']
            assert list(ar.shape) == a['shape'] and np.isfinite(ar).all()
            assert np.array_equal(t, ar[:, ac.index('t_s')])
            assert np.array_equal(ar[:, ac.index('P_I_kN')], ar[:, ac.index('P_J_kN')])
            same(ar[:, ac.index('U1_m')], .001 * ar[:, ac.index('U1_mm')])
            g = geom['Story8', a['Link']]
            n = float(g['n' + case[-1].lower()])
            p = ar[:, ac.index('P_J_kN')]  # One scalar per device, never I+J.
            parts.append(n * p)
            records.append((a, ar, ac, p))
        qd = np.add.reduce(parts)
        it, idd = int(np.argmax(np.abs(qt))), int(np.argmax(np.abs(qd)))
        for field, value in [('QT_peak_abs_kN', abs(qt[it])), ('QT_signed_at_peak_kN', qt[it]), ('t_QT_peak_s', t[it]), ('QT_peak_SourceRow', arr[it, col.index('SourceRow')]), ('QD_J_resisting_peak_abs_kN', abs(qd[idd])), ('QD_J_resisting_signed_at_own_peak_kN', qd[idd]), ('t_QD_abs_peak_s', t[idd]), ('QD_J_resisting_at_QT_peak_kN', qd[it]), ('QT_signed_at_QD_abs_peak_kN', qt[idd])]:
            same(r[field], value)
        for part, (a, ar, ac, p) in zip(parts, records):
            x = di[case, a['Link']]
            u = ar[:, ac.index('U1_mm')]
            ip, iu = int(np.argmax(abs(p))), int(np.argmax(abs(u)))
            for field, value in [('P_abs_peak_kN', abs(p[ip])), ('t_P_peak_s', t[ip]), ('U1_abs_peak_total_mm', abs(u[iu])), ('t_U1_peak_s', t[iu]), ('P_at_QT_peak_kN', p[it]), ('U1_total_at_QT_peak_mm', u[it]), ('qJ_resisting_at_QT_peak_kN', part[it]), ('qJ_resisting_at_layer_QD_peak_kN', part[idd]), ('P_SourceRow_at_QT_peak', ar[it, ac.index('force_I_row')]), ('U1_SourceRow_at_QT_peak', ar[it, ac.index('deformation_row')])]:
                same(x[field], value)
        recomputed.append({'Case': case, 'QT_peak_abs_kN': float(abs(qt[it])), 't_QT_s': float(t[it]), 'QD_peak_abs_kN': float(abs(qd[idd])), 't_QD_s': float(t[idd]), 'QD_at_QT_kN': float(qd[it]), 'QT_at_QD_kN': float(qt[idd]), 'QD_at_QT_percent_own_peak': float(100 * abs(qd[it]) / abs(qd[idd])), 'time_difference_QD_minus_QT_s': float(t[idd] - t[it]), 'n': len(t), 'devices_read': 8, 'I_J_scalar_counted_once': True})
for x in sources:
    assert ident(Path(x['path'])) == x
report = '''# R005｜Story8装置出力与原生QT峰时独审

**采纳：角色4 R005的Story8六例、48个同刻分力及合力口径通过本项审核，无数值必改项。** RH4X/Y从旧缓存独立重算，其他四例仅小表算术核对；未把这一抽核范围扩大成六例全时程独立复算。未等待角色1新结果。

## 工程结果

|工况|QT绝对峰/kN（时刻/s）|QD绝对峰/kN（时刻/s）|QT峰时QD/kN|占QD自身峰绝对值|QD峰时QT/kN|tQD−tQT/s|
|---|---|---|---:|---:|---:|---:|
|RH4X|5776.6513（21.60）|405.8268（11.50）|−238.1133|58.6736%|−1868.8754|−10.10|
|RH4Y|5205.2112（21.58）|447.2019（11.46）|−279.6257|62.5278%|−1367.4040|−10.12|

六例QT峰时的|QD|/max|QD|为48.5899%—65.9515%；这是装置水平合力相对自身保存峰的比例，不是装置对QT的贡献率，也不是耗能效率。两个峰的时间差仅描述不同输出的控制时刻，不是相位角。

## 几何、去重与符号

Story8的8只实际几何均为I端在Story7、J端在Story8且ZJ>ZI；从端点坐标重算n=(rJ−rI)/L与几何表一致。每个主输入方向4只非零投影、4只零投影。逐只采用相同Story、Link、Case的P，没有借其他楼层或同角度装置的历史。

沿用原生P按正拉轴力解释的既有约定，J端结构内力抵抗项为nP，装置对J节点的外力为−nP；两者不可混写。两例16条记录的P_I与P_J逐点相同，独立计算仅取P_J一份，不能相加两端。此处几何核查不另行认证软件Bottom截面方向或节点局部轴。

48行逐只表的nP、外力反号、各器件自身峰比例、层QD峰比例，以及六行合力的同刻分力和、合力自身峰时分力和、峰时差与比值均闭合。零投影方向的分力峰为零，其自身峰比及峰时保留空白，不能补成0%利用率。总U1继续称装置总轴向变形，不称黏壶变形或速度。

## 审核覆盖与必须保留的限定

正式清单、脚本、小表和七项输入SHA均一致；从旧P/U1 NPZ读取Story8/RH4X/Y各8只，另读对应QT与Base两例，时间轴逐点相同、有限且递增，无插值补零。两例逐只峰、同刻P/U1和源行均与小表一致；源行追溯至旧缓存，本项没有重开Excel核源单元格。其他四例的P/U1峰值和全时程完整性沿用冻结数据角色结果，本项只验证小表算术。

192份历史的元数据只覆盖Story8—11每层8只，共32只；88只是几何数量，不代表全楼力时程齐全。24行覆盖表与元数据一致，但本次没有重读全部192份历史。原生Bottom的侧别、正方向与Link包含性仍未闭合，不能用QT±QD认定主体QS，也不能由峰值不同步认定模态或减震因果。

## 可直接用于正文的工程句

“Story8两例原生记录表明，装置水平合力与楼层Bottom剪力的绝对峰出现在不同保存时刻：RH4X、RH4Y的装置合力分别在11.50 s和11.46 s取峰，而层剪峰分别出现在21.60 s和21.58 s；在层剪峰时，装置合力绝对值分别为其自身峰的58.6736%和62.5278%。”

“因此，比较该层装置出力与剪力需求时应保留同刻有符号值；上述结果只描述现有Story8的时序，未认证主体剪力扣分关系，也不构成相位角或单阶模态归因。”

不要求角色4改冻表。作者使用时必须同时保留QD的J端抵抗项定义、上述覆盖范围及QT包含性未定的限制；旧审核中改布置建议不属于本轮主线。
'''
assert min(float(r['QD_at_QT_abs_percent_own_abs_peak']) for r in summary) > 48.5898
assert max(float(r['QD_at_QT_abs_percent_own_abs_peak']) for r in summary) < 65.9516
p = OUT / 'R005-device-timing-review.md'
assert not p.exists()
p.write_bytes(report.encode('utf-8'))
end = datetime.now(START.tzinfo)
assert end <= DEADLINE
js('R005-checks.json', {'source_bindings': sources, 'two_cases_independent_recomputation': recomputed, 'six_summary_rows_arithmetic_checked': 6, 'device_rows_arithmetic_checked': 48, 'native_P_U1_records_read': 16, 'other_four_cases_full_histories_reread': False, 'metadata_unique_devices': 32, 'geometry_devices': 88, 'new_full_history_files': 0, 'raw_Excel_ODE_ETABS_runs': 0})
js('R005-validation.json', {'status': 'adopt scoped Story8 timing results; no numerical corrections', 'actual_start': START.isoformat(), 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'within_10_minutes': end <= DEADLINE, 'only_role2_written': True, 'no_QS_subtraction_or_phase_angle_inference': True, 'no_Git_automation_agents': True, 'qa': {'UTF8_LF': '\r' not in report, 'no_trailing_whitespace': all(x.rstrip() == x for x in report.splitlines()), 'JSON_parse': True}})
js('R005-manifest.json', {'frozen_at': end.isoformat(), 'files': [ident(OUT / name) for name in ['R005-audit-device-timing.py', 'R005-device-timing-review.md', 'R005-checks.json', 'R005-validation.json']]})
print(json.dumps({'status': 'adopt scoped timing results', 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'two_cases': recomputed}, ensure_ascii=False))
