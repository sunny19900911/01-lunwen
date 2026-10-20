from pathlib import Path
from datetime import datetime, timedelta
import csv
import hashlib
import json
import numpy as np

OUT = Path(__file__).resolve().parent
SRC = OUT.parent / 'role1'
START = datetime.fromisoformat('2026-10-20T20:07:02.374210+08:00')
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
assert not (OUT / 'R007-validation.json').exists()
sources = []
for manifest in [OUT / 'R004-manifest.json', SRC / 'R005-manifest.json']:
    sources.append(ident(manifest))
    for r in json.loads(manifest.read_text(encoding='utf-8'))['files']:
        p = Path(r['path']) if 'path' in r else manifest.parent / r['file']
        got = ident(p)
        assert got['bytes'] == r['bytes'] and got['sha256'] == r['sha256']
        sources.append(got)
known = {r['path']: r for r in json.loads((OUT / 'R004-checks.json').read_text(encoding='utf-8'))['source_bindings']}
freeze = json.loads((SRC / 'R005-input-freeze.json').read_text(encoding='utf-8'))
for r in freeze['inputs']:
    p = SRC / r['file']
    got = ident(p)
    assert got['sha256'] == r['sha256']
    sources.append(got)
cache = []
for name in ['R003-none-summary.json', 'R003-story1-summary.json']:
    p = SRC / name
    assert ident(p) == known[str(p)]
    s = json.loads(p.read_text(encoding='utf-8'))
    state, model = Path(s['source_state']['path']), Path(s['source_model_freeze']['path'])
    for p in [state, model]:
        got = ident(p)
        assert got == known[str(p)]
        sources.append(got)
    columns = json.loads(model.read_text(encoding='utf-8'))['state_columns']
    with np.load(state, allow_pickle=False) as z:
        a = z['trajectory']
    t = a[:, columns.index('t')]
    u = a[:, [columns.index(k) for k in ['u1', 'u2', 'u3']]]
    phi = np.array(s['phi_columns_mass_normalized'])
    q = np.linalg.solve(phi, u.T).T
    same(q, u @ np.array(s['mass']) @ phi)
    terms = q * (phi[1] - phi[0])
    direct = u[:, 1] - u[:, 0]
    same(terms.sum(axis=1), direct)
    assert len(t) == 40001 and t[0] == 0 and t[-1] == 200
    assert np.all(np.diff(t) > 0) and np.isfinite(a).all()
    cache.append({'t': t, 'terms': terms, 'direct': direct})
assert np.array_equal(cache[0]['t'], cache[1]['t'])
t = cache[0]['t']
v0, vd = cache[0]['terms'], cache[1]['terms']
p0, pd = np.max(abs(v0), axis=0), np.max(abs(vd), axis=0)
assert np.all(p0 > 0)
scale = pd / p0
assert np.all(scale > 0)
vr = v0 * scale
reference = v0 @ scale
same(reference, vr.sum(axis=1))
same(np.max(abs(vr), axis=0), pd)
mode_rows = rc('R005-mode-scale-and-waveform-check.csv')
assert len(mode_rows) == 3
mode_checks = []
for r in mode_rows:
    k = int(r['mode']) - 1
    err = float(np.max(abs(vr[:, k] - vd[:, k])))
    for field, value in [('none_mode_absolute_peak', p0[k]), ('actual_device_mode_absolute_peak', pd[k]), ('a_k', scale[k]), ('reference_mode_absolute_peak', np.max(abs(vr[:, k]))), ('reference_actual_waveform_max_abs_difference', err)]:
        same(r[field], value)
    i0, ir = int(np.argmax(abs(v0[:, k]))), int(np.argmax(abs(vr[:, k])))
    assert i0 == ir
    waveerr = float(np.max(abs(vr[:, k] / scale[k] - v0[:, k])))
    assert waveerr < 1e-12 and err > 1e-6
    mode_checks.append({'mode': k+1, 'a': float(scale[k]), 'reference_peak': float(np.max(abs(vr[:, k]))), 'actual_peak': float(pd[k]), 'unchanged_reference_single_mode_peak_index': i0, 'unchanged_reference_single_mode_peak_time': float(t[i0]), 'rescaled_waveform_recovery_error': waveerr, 'reference_actual_waveform_max_abs_difference': err})
outputs = {'none_full': cache[0]['direct'], 'posterior_amplitude_only_reference': reference, 'actual_device_story1': cache[1]['direct']}
rows = rc('R005-three-output-peaks.csv')
assert len(rows) == 3
peaks = []
full0 = float(np.max(abs(cache[0]['direct'])))
for r in rows:
    y = outputs[r['output']]
    p = float(np.max(abs(y)))
    ii = np.flatnonzero(abs(y) == p)
    assert len(ii) == 1
    i = int(ii[0])
    for field, value in [('QS2_absolute_peak', p), ('QS2_signed_at_peak', y[i]), ('peak_time_nondimensional', t[i]), ('peak_over_none', p/full0), ('peak_change_from_none_percent', 100*(p/full0-1))]:
        same(r[field], value)
    peaks.append({'output': r['output'], 'peak': p, 'signed_at_peak': float(y[i]), 'index': i, 't': float(t[i]), 'reduction_percent': 100*(1-p/full0)})
common_rows = rc('R005-common-time-values.csv')
assert len(common_rows) == 2
common = []
for r in common_rows:
    when = float(r['time_nondimensional'])
    i = int(round(when/.005))
    same(when, t[i])
    for label, y in outputs.items():
        same(r[label], y[i])
    same(r['reference_minus_actual_signed'], reference[i]-cache[1]['direct'][i])
    same(r['reference_abs_minus_actual_abs'], abs(reference[i])-abs(cache[1]['direct'][i]))
    common.append({'t': float(t[i]), **{label: float(y[i]) for label, y in outputs.items()}})
summary = json.loads((SRC / 'R005-numeric-summary.json').read_text(encoding='utf-8'))
same(summary['reference_actual_output_max_abs_difference'], np.max(abs(reference-cache[1]['direct'])))
assert peaks[0]['t'] == 20.215 and peaks[1]['t'] == 20.185 and peaks[2]['t'] == 20.09
assert all(abs(peaks[i]['peak']-peaks[j]['peak']) > 1e-4 for i in range(3) for j in range(i))
for x in sources:
    assert ident(Path(x['path'])) == x
report = '''# R007｜各阶峰比缩放参照独审

**采用：角色1冻结R005的三行输出峰、两行共同时间值及三行各阶匹配检查均通过独立复算，无数值必改项。** 只读旧两条H2完整状态，沿用本角色R004已核质量归一基及QS2=u2−u1；独立解Φq=u恢复坐标，未运行角色1脚本、未新增ODE或扫描参数。

## 可采用的数值

a_r=max|V_dr|/max|V_0r|独立算得(0.968467752944，0.704190897124，0.814235802706)。在相同保存时间轴上构造Q_ref=Σa_rV_0r，各阶参照绝对峰与实际装置项的绝对峰逐一匹配；正数缩放保持各单阶原波形时序及其绝对峰节点，独立核对通过。

|输出|绝对峰|有符号峰值|保存网格峰时|相对无装置减幅|
|---|---:|---:|---:|---:|
|无装置完整状态|0.06635368725|−0.06635368725|20.215|0%|
|后验幅值缩放参照|0.05751805433|−0.05751805433|20.185|13.315964%|
|实际层1装置状态|0.06273951643|−0.06273951643|20.090|5.446827%|

|共同时间|无装置|缩放参照|实际装置|
|---:|---:|---:|---:|
|20.090|−0.06534898547|−0.05704854020|−0.06273951643|
|20.215|−0.06635368725|−0.05746431342|−0.06181753334|

三阶参照与实际波形的全程最大绝对差分别约0.003662234、0.001578197、0.016788791；合成输出最大点值差约0.018098897。这是逐点差的最大值，不能与两个合成绝对峰之差混用。

## 采用边界与必须保留的表述

参照与无装置的每一单阶项只差一个正数倍率，没有移动时间位置，合成绝对峰却由20.215移至20.185。因此，本有限算例直接说明：合成峰时迁移本身不足以证明单阶相位改变。三阶峰比是三个全程标量，不能确定同刻叠加的完整波形，也不能由单阶峰匹配推出总峰匹配。

该参照使用已经算出的实际装置峰值校定倍率，属于结果已知后的人工信号构造；没有证明它满足原结构与装置反馈方程。不能写成可实现减剪方案、预测算法或纯相位分解，也不能把参照与实际之间的差额直接称为相位损失、反向抵消损失或某阶独立因果作用。幅值包络、相对时序和波形形状未被唯一分离。

时间及响应均无量纲；40001节点、h=.005、窗口0—200，均为旧近似保存状态上的后验检验。无装置主体C=.02K非零；本项没有两阶重新耦合求解或真实建筑模态归因。原报告已包含这些限制，无需修改冻结数表。

## 可直接写稿的段落

以实际装置方案和无装置方案的各阶剪力绝对峰之比，对无装置单阶时程作常数缩放，所得人工参照虽逐阶匹配实际装置峰值，其合成剪力峰仍为0.05751805，低于实际装置的0.06273952。参照没有改变各单阶波形的时间位置，合成峰时却从无装置的20.215移至20.185，说明合成峰时迁移本身不足以证明模态相位改变。该旧三层模型的后验检验表明，单阶全程峰值削弱不足以恢复局部剪力峰；它未提供可实现预测，也未将幅值与相位的独立作用分离。
'''
p = OUT / 'R007-amplitude-reference-review.md'
assert not p.exists()
p.write_bytes(report.encode('utf-8'))
end = datetime.now(START.tzinfo)
assert end <= DEADLINE
js('R007-checks.json', {'source_bindings': sources, 'mode_checks': mode_checks, 'three_output_peaks': peaks, 'two_common_times': common, 'reference_actual_output_max_abs_pointwise_difference': float(np.max(abs(reference-cache[1]['direct']))), 'source_full_states_read': 2, 'new_ODE_parameter_scans_Excel_reads': 0, 'new_full_history_files': 0})
js('R007-validation.json', {'status': 'adopt posterior-reference results; no numerical changes', 'actual_start': START.isoformat(), 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'within_8_minutes': end <= DEADLINE, 'only_role2_written': True, 'no_new_ODE_ETABS_Git_automation_agents': True, 'qa': {'UTF8_LF': '\r' not in report, 'no_trailing_whitespace': all(x.rstrip() == x for x in report.splitlines()), 'JSON_parse': True}})
js('R007-manifest.json', {'frozen_at': end.isoformat(), 'files': [ident(OUT / name) for name in ['R007-audit-amplitude-reference.py', 'R007-amplitude-reference-review.md', 'R007-checks.json', 'R007-validation.json']]})
print(json.dumps({'status': 'adopt', 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'scales': scale.tolist(), 'three_output_peaks': peaks}, ensure_ascii=False))
