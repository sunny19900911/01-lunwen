from pathlib import Path
from datetime import datetime, timedelta
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import numpy as np

OUT = Path(__file__).resolve().parent
SRC = OUT.parent / 'role1'
START = datetime.fromisoformat('2026-10-20T20:02:11.633268+08:00')
DEADLINE = START + timedelta(minutes=8)


def ident(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def same(a, b):
    assert np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), rtol=2e-12, atol=2e-13), (a, b)


def rc(name):
    with (SRC / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def js(name, value):
    p = OUT / name
    assert not p.exists(), p
    p.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    json.loads(p.read_text(encoding='utf-8'))


assert datetime.now(START.tzinfo) < DEADLINE
assert not (OUT / 'R006-validation.json').exists()
sources = []
for manifest in [OUT / 'R004-manifest.json', SRC / 'R004-manifest.json']:
    sources.append(ident(manifest))
    for r in json.loads(manifest.read_text(encoding='utf-8'))['files']:
        p = Path(r['path']) if 'path' in r else manifest.parent / r['file']
        got = ident(p)
        assert got['bytes'] == r['bytes'] and got['sha256'] == r['sha256']
        sources.append(got)
own = json.loads((OUT / 'R004-checks.json').read_text(encoding='utf-8'))
known = {x['path']: x for x in own['source_bindings']}
freeze = json.loads((SRC / 'R004-input-freeze.json').read_text(encoding='utf-8'))
cache = {}
errors = []
for pos, source in zip(freeze['positions'], freeze['source_summaries']):
    p = SRC / source['file']
    got = ident(p)
    assert got['sha256'] == source['sha256'] and got == known[str(p)]
    sources.append(got)
    summary = json.loads(p.read_text(encoding='utf-8'))
    state = Path(summary['source_state']['path'])
    got = ident(state)
    assert got == known[str(state)] and got['sha256'] == summary['source_state']['sha256']
    sources.append(got)
    modelpath = Path(summary['source_model_freeze']['path'])
    got = ident(modelpath)
    assert got == known[str(modelpath)]
    sources.append(got)
    model = json.loads(modelpath.read_text(encoding='utf-8'))
    M = np.array(summary['mass'])
    phi = np.array(summary['phi_columns_mass_normalized'])
    same(phi.T @ M @ phi, np.eye(3))
    with np.load(state, allow_pickle=False) as z:
        arr = z['trajectory']
    cols = model['state_columns']
    t = arr[:, cols.index('t')]
    u = arr[:, [cols.index(k) for k in ['u1', 'u2', 'u3']]]
    assert len(t) == 40001 and t[0] == 0 and t[-1] == 200 and np.all(np.diff(t) > 0)
    q = np.linalg.solve(phi, u.T).T
    same(q, u @ M @ phi)
    coef = phi[1] - phi[0]
    same(coef, own['output_coefficients']['QS2'])
    assert np.all(coef != 0)
    terms, direct = q * coef, u[:, 1] - u[:, 0]
    err = float(np.max(np.abs(terms.sum(axis=1) - direct)))
    assert err < 1e-12
    errors.append(err)
    cache[pos] = {'t': t, 'q': q, 'terms': terms, 'direct': direct, 'coef': coef}
assert np.array_equal(cache[0]['t'], cache[1]['t'])
t = cache[0]['t']
rows = rc('R004-common-time-terms.csv')
diff = rc('R004-common-time-differences.csv')
peaks = rc('R004-whole-window-mode-peaks.csv')
local = rc('R004-local-curves.csv')
assert len(rows) == 20 and len(diff) == 10 and len(peaks) == 3 and len(local) == 161
ri = {(int(r['index0']), int(r['position'])): r for r in rows}
expected_indices = sorted({int(round(v / .005)) + d for v in [20.09, 20.215] for d in [-20, -10, 0, 10, 20]})
assert set(ri) == {(i, p) for i in expected_indices for p in [0, 1]}
for (i, p), r in ri.items():
    c = cache[p]
    v, y = c['terms'][i], c['direct'][i]
    same(r['time_nondimensional'], t[i])
    same([r['mode1_signed'], r['mode2_signed'], r['mode3_signed']], v)
    for field, value in [('sum_modes', sum(v)), ('QS2_direct', y), ('sum_abs_terms', sum(abs(v))), ('abs_sum_over_sum_abs', abs(y) / sum(abs(v)))]:
        same(r[field], value)
for r in diff:
    i = int(r['index0'])
    dv = cache[1]['terms'][i] - cache[0]['terms'][i]
    dy = cache[1]['direct'][i] - cache[0]['direct'][i]
    same(r['time_nondimensional'], t[i])
    same([r['device_minus_none_mode1'], r['device_minus_none_mode2'], r['device_minus_none_mode3']], dv)
    same(r['device_minus_none_total'], dy)
    same(sum(dv), dy)
    same(r['none_total'], cache[0]['direct'][i])
    same(r['device_total'], cache[1]['direct'][i])
    same(r['device_abs_minus_none_abs'], abs(cache[1]['direct'][i]) - abs(cache[0]['direct'][i]))
peak_results = []
for r in peaks:
    k = int(r['mode']) - 1
    computed = {}
    same(r['QS2_output_coefficient'], cache[0]['coef'][k])
    for p, name in [(0, 'none'), (1, 'story1')]:
        c = cache[p]
        y = c['terms'][:, k]
        i = int(np.argmax(abs(y)))
        qp = float(np.max(abs(c['q'][:, k])))
        for field, value in [('absolute_peak', abs(y[i])), ('signed_at_peak', y[i]), ('peak_time', t[i]), ('q_absolute_peak', qp)]:
            same(r[name + '_' + field], value)
        same(abs(y[i]), abs(c['coef'][k]) * qp)
        computed[name + '_P'] = float(abs(y[i]))
        computed[name + '_qP'] = qp
        computed[name + '_t'] = float(t[i])
    ratio = computed['story1_P'] / computed['none_P']
    same(r['story1_over_none_amplitude_ratio'], ratio)
    same(r['signed_peak_change_percent'], 100 * (ratio - 1))
    same(ratio, computed['story1_qP'] / computed['none_qP'])
    computed.update(mode=k+1, ratio=ratio, reduction_percent=100*(1-ratio))
    peak_results.append(computed)
window = np.flatnonzero((t >= 19.7) & (t <= 20.5))
assert len(window) == len(local)
for i, r in zip(window, local):
    same(r['time_nondimensional'], t[i])
    for p, name in [(0, 'none'), (1, 'story1')]:
        same([r[name + '_mode' + str(k)] for k in [1, 2, 3]], cache[p]['terms'][i])
        same(r[name + '_total'], cache[p]['direct'][i])
# Verify the SVG's plotted coordinates against the frozen CSV and source-derived values.
svg = ET.parse(SRC / 'R004-local-modal-terms.svg').getroot()
polylines = svg.findall('{http://www.w3.org/2000/svg}polyline')
assert len(polylines) == 8
pixel_error = 0.
for panel, (p, top) in enumerate([(0, 115), (1, 455)]):
    for k in range(4):
        y = cache[p]['terms'][window, k] if k < 3 else cache[p]['direct'][window]
        expected = np.column_stack((100 + (t[window]-19.7)/.8*940, top+200*(.010-y)/.085))
        actual = np.array([[float(v) for v in point.split(',')] for point in polylines[panel*4+k].attrib['points'].split()])
        assert actual.shape == expected.shape
        e = float(np.max(abs(actual - expected)))
        assert e <= .005001
        pixel_error = max(pixel_error, e)
controls = []
for v in [20.09, 20.215]:
    i = int(round(v/.005))
    a, b = cache[0]['terms'][i], cache[1]['terms'][i]
    d = b-a
    assert np.all(a < 0) and np.all(b < 0)
    assert d[0] < 0 and d[1] < 0 and d[2] > 0 and sum(d) > 0
    controls.append({'t': float(t[i]), 'none_terms': a.tolist(), 'device_terms': b.tolist(), 'device_minus_none': d.tolist(), 'total_change': float(sum(d)), 'instantaneous_abs_term_ratios': (abs(b)/abs(a)).tolist()})
assert abs(cache[1]['terms'][window[0], 2]) > abs(cache[0]['terms'][window[0], 2])
for x in sources:
    assert ident(Path(x['path'])) == x
report = '''# R006｜共同控制时刻与全程模态峰比独审

**采用：角色1冻结R004数表和局部图数据通过独立复核，无数值必改项。** 仅审R004，不读取或等待其新R005。沿用本角色R004已核主体、质量和输出接口，从旧H2两条完整保存状态恢复坐标，不求解ODE。

10个共同时间×2方案的20行三阶项、总和、直接QS2、绝对项和及叠加比，10行差分，三阶各自全程绝对峰/峰时/q峰/峰比，以及局部161节点×2方案的全部图数据均一致。SVG八条折线也与源状态及CSV吻合，坐标最大舍入误差不超过0.0051像素；本项核数据与坐标，不另做视觉排版审查。

## 采用的实数结论

|阶次|无装置单阶QS2峰|层1装置单阶QS2峰|装置/无装置峰比|降幅|
|---|---:|---:|---:|---:|
|1|0.03686062919|0.03569833073|0.96846775|3.1532%|
|2|0.00545162933|0.00383898775|0.70419090|29.5809%|
|3|0.04835673918|0.03937378834|0.81423580|18.5764%|

同一基下QS2输出系数分别约+0.315637347、−0.022185735、−1.316515929，三者均非零；因此每阶QS2绝对峰比等于其q绝对峰比。该等式不意味着装置轨迹是无装置轨迹按此常数逐时缩放，也不意味着三阶独立求解。

|共同时间|Δ第1阶|Δ第2阶|Δ第3阶|Δ总QS2|
|---:|---:|---:|---:|---:|
|20.090|−0.000701539|−0.000133053|+0.003444061|+0.002609469|
|20.215|−0.000690976|−0.000054827|+0.005281957|+0.004536154|

差分为装置减无装置。两个时刻两方案的三项均为负，前两项负幅略增，第三项负幅减小，总值向零移动。完整峰时的同向叠加不支持“反向抵消损失”；“前两项变化部分抵消第三项变化的收益”仅是跨方案同刻差分的分账，不能混同成原响应模态项之间的反向抵消。

## 写稿必须保留的口径

“前两项略增强、第三项减弱”只对所列两个控制时刻及经列示时间成立，不能推广到局部窗口或全程每一点。局部窗口起点t=19.700的第三阶项，装置负幅反而比无装置大；这也说明不能用全程峰比作固定逐时缩放。

第二阶各自全程峰时73.210与23.430对应不同控制时段，二者差不能称为模态相位角，也不能单独证明相位因果。所有时间和响应均无量纲、在h=.005的旧保存网格上取峰；无装置保留C=.02K。本项是同状态坐标展开及跨两完整轨迹比较，不是两阶重新耦合求解，也不是实际建筑X/Y/扭转的逐阶贡献。

## 可直接写稿的段落

在旧三层H2输入下，采用同一参考振型基比较完整保存响应，第一至第三阶对第二层主体弹性剪力的全程绝对峰分别下降3.1532%、29.5809%和18.5764%，但各阶全程峰比不能代表控制时刻的同比缩放。在共同时间20.090和20.215，两方案的三阶剪力项均同向为负；装置方案第一、二阶项的负幅略增，第三阶项的负幅减小，后者带来的总剪力绝对值减小被前两项变化部分抵消。该有限模型结果说明，局部剪力需按同一时刻的有符号分量叠加判断，不能仅凭单阶全程峰减幅或峰时迁移认定抵消损失及相位因果。
'''
p = OUT / 'R006-common-time-review.md'
assert not p.exists()
p.write_bytes(report.encode('utf-8'))
end = datetime.now(START.tzinfo)
assert end <= DEADLINE
js('R006-checks.json', {'source_bindings': sources, 'common_time_count': 10, 'common_rows_checked': 20, 'difference_rows_checked': 10, 'whole_window_mode_peaks': peak_results, 'required_controls': controls, 'local_nodes_per_scheme': 161, 'svg_polylines': 8, 'max_pixel_rounding_error': pixel_error, 'full_output_reconstruction_errors': errors, 'new_ODE_runs': 0, 'source_states_read': 2, 'new_full_history_files': 0})
js('R006-validation.json', {'status': 'adopt frozen R004 data; no numerical changes', 'actual_start': START.isoformat(), 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'within_8_minutes': end <= DEADLINE, 'only_role2_written': True, 'no_new_ODE_ETABS_Git_automation_agents': True, 'qa': {'UTF8_LF': '\r' not in report, 'no_trailing_whitespace': all(x.rstrip() == x for x in report.splitlines()), 'JSON_parse': True}})
js('R006-manifest.json', {'frozen_at': end.isoformat(), 'files': [ident(OUT / name) for name in ['R006-audit-common-times.py', 'R006-common-time-review.md', 'R006-checks.json', 'R006-validation.json']]})
print(json.dumps({'status': 'adopt', 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'controls': controls, 'pixel_error': pixel_error}, ensure_ascii=False))
