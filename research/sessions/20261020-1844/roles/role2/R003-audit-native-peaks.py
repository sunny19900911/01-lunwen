from pathlib import Path
from datetime import datetime, timedelta
import csv
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
DATA = OUT.parent / 'role4'
START = datetime.fromisoformat('2026-10-20T19:42:22.707579+08:00')
DEADLINE = START + timedelta(minutes=8)


def now():
    return datetime.now(START.tzinfo)


def identity(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def readcsv(name):
    with (DATA / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def close(a, b):
    assert np.isclose(float(a), float(b), rtol=1e-12, atol=1e-8), (a, b)


def writejson(name, value):
    p = OUT / name
    assert not p.exists(), p
    p.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    json.loads(p.read_text(encoding='utf-8'))


assert now() < DEADLINE
assert not (OUT / 'R003-validation.json').exists()
sources = []
for name in ['R002-delivery-manifest.json', 'R003-delivery-manifest.json']:
    p = DATA / name
    sources.append(identity(p))
    for item in json.loads(p.read_text(encoding='utf-8'))['files']:
        got = identity(Path(item['path']))
        assert got['sha256'] == item['sha256'] and got['bytes'] == item['bytes']
        sources.append(got)

main = readcsv('R002-all14-main-axis-168.csv')
common = readcsv('R002-common-six-main-axis-72.csv')
three = readcsv('R003-three-model-peaks-72.csv')
physical = readcsv('R001-story-forces-72.csv')
key = lambda r: (r['Case'], r['Story'], r['Location'], r.get('Axis', r['Case'][-1]))
mi = {key(r): r for r in main}
ci = {key(r): r for r in common}
ti = {key(r): r for r in three}
pi = {key(r): r for r in physical}
assert len(main) == len(mi) == 168
assert len(common) == len(ci) == len(three) == len(ti) == len(physical) == len(pi) == 72
assert set(ci) == set(ti) == set(pi)
assert len({r['Case'] for r in main}) == 14
assert len({r['Case'] for r in common}) == 6
for r in main:
    assert r['Axis'] == r['Case'][-1] and r['Location'] == 'Bottom'
    assert float(r['P0_kN']) > 1e-10
    p0, p3 = float(r['P0_kN']), float(r['P3_kN'])
    close(r['peak_reduction_percent'], 100 * (1 - p3 / p0))
    close(r['peak_change_percent'], 100 * (p3 / p0 - 1))
    close(r['peak_change_kN'], p3 - p0)
    close(r['peak_time_shift_s'], float(r['t_peak3_s']) - float(r['t_peak0_s']))
    close(r['peak_change_kN'], float(r['same_time_signed_change_kN']) + float(r['repeak_recovery_kN']))
    assert float(r['repeak_recovery_kN']) >= -1e-8
for k, r in ci.items():
    assert r == mi[k]
    t, p = ti[k], pi[k]
    assert p['units'] == t['units'] == 'kN'
    assert t['physical_input_and_complete_model_pair_verified'] == 'False'
    assert t['label0_label3_input_pair_verified'] == 'True'
    for field in ['P0_kN', 'P3_kN', 't_peak0_s', 't_peak3_s', 'source_row0', 'source_row3']:
        close(t[field], r[field])
    field = 'V' + t['Axis']
    for a, b in [('Pphysical_kN', field + '_peak_abs'), ('t_peakphysical_s', field + '_peak_t_s'), ('source_rowphysical', field + '_peak_SourceRow')]:
        close(t[a], p[b])
    close(t['physical_over_label3_peak'], float(t['Pphysical_kN']) / float(t['P3_kN']))

binding = {}
for name in ['R001-input-freeze.json', 'R002-input-freeze.json']:
    for item in json.loads((DATA / name).read_text(encoding='utf-8'))['inputs']:
        p = Path(item['path'])
        if p.name in ['manifest.json', 'response_cache_manifest.json', 'Story_Forces.npz', 'native_paired_validation.json']:
            got = identity(p)
            assert got['sha256'] == item['sha256'] and got['bytes'] == item['bytes']
            binding[str(p)] = got
sources.extend(binding.values())
w = ROOT.parent / 'W5-重燃双塔连体'
d = w / '02-数据/增阻尼多目标研究-20261016'
model_manifests = [
    ('label0', d / '原生0数据缓存/manifest.json'),
    ('label3', d / 'response_cache_manifest.json'),
    ('physical', w / 'research/maxwell-20261017/experiments/R001/core-cache/manifest.json'),
]
paired = json.loads((d / 'native_paired_validation.json').read_text(encoding='utf-8'))
assert len(paired['matched_grids_and_inputs']) == 14
assert all(r['same_input_all_samples'] for r in paired['matched_grids_and_inputs'])
samples = []
arrays_read = 0
for model, path in model_manifests:
    meta = json.loads(path.read_text(encoding='utf-8'))
    table = meta['tables']['Story Forces']
    cols = table.get('columns', table.get('value_columns'))
    for field in ['VX', 'VY']:
        assert table['units'][table['headers'].index(field)] == 'kN'
    with np.load(path.parent / table['cache'], allow_pickle=False) as z:
        for case, story in [('SHW4Y', 'Story7'), ('RH4X', 'Story1')]:
            matches = [(k, g) for k, g in table['groups'].items() if g['keys']['Output Case'] == case and g['keys']['Story'] == story and g['keys']['Location'] == 'Bottom']
            assert len(matches) == 1
            group, g = matches[0]
            a = z[group]
            arrays_read += 1
            tt, y = a[:, cols.index('Time')], a[:, cols.index('V' + case[-1])]
            assert np.isfinite(a).all() and np.all(np.diff(tt) > 0)
            # Independent peak rule: enumerate all absolute maxima and take earliest saved time.
            peak = float(np.max(np.abs(y)))
            tied = np.flatnonzero(np.abs(y) == peak)
            i = int(tied[np.argmin(tt[tied])])
            row = ti[(case, story, 'Bottom', case[-1])]
            prefix = {'label0': '0', 'label3': '3', 'physical': 'physical'}[model]
            close(peak, row['P' + prefix + '_kN'])
            close(tt[i], row['t_peak' + prefix + '_s'])
            close(a[i, cols.index('SourceRow')], row['source_row' + prefix])
            sample = {'model': model, 'Case': case, 'Story': story, 'Axis': case[-1], 'Location': 'Bottom', 'units': 'kN', 'cache_group': group, 'n': len(tt), 't0_s': float(tt[0]), 't1_s': float(tt[-1]), 'peak_abs_kN': peak, 'signed_at_peak_kN': float(y[i]), 'peak_t_s': float(tt[i]), 'SourceRow': int(a[i, cols.index('SourceRow')]), 'ties': len(tied), 'time_grid_sha256': hashlib.sha256(tt.tobytes()).hexdigest()}
            if model in ['label0', 'label3']:
                r = mi[(case, story, 'Bottom', case[-1])]
                close(y[i], r['signed' + prefix + '_at_own_peak_kN'])
            if model == 'label3':
                ref = float(mi[(case, story, 'Bottom', case[-1])]['t_peak0_s'])
                jj = np.flatnonzero(tt == ref)
                assert len(jj) == 1
                close(y[jj[0]], mi[(case, story, 'Bottom', case[-1])]['label3_at_label0_peak_kN'])
            samples.append(sample)
for case in ['SHW4Y', 'RH4X']:
    rr = [s for s in samples if s['Case'] == case]
    assert len({s['time_grid_sha256'] for s in rr}) == 1
assert arrays_read == 6
assert sum(float(r['peak_change_kN']) > 0 for r in main) == 0
hi = sum(float(r['Pphysical_kN']) > float(r['P3_kN']) for r in three)
lo = sum(float(r['Pphysical_kN']) < float(r['P3_kN']) for r in three)
assert (hi, lo) == (34, 38)
least = min(main, key=lambda r: float(r['peak_reduction_percent']))
most = max(main, key=lambda r: float(r['peak_reduction_percent']))
shift = max(main, key=lambda r: abs(float(r['peak_time_shift_s'])))
for item in binding.values():
    assert identity(Path(item['path'])) == item
report = '''# R003｜原生楼层剪力小表独立审核

**通过本项限定范围审核：168行主轴减幅、72行三态峰比及两组缓存抽核一致。没有发现把独立峰时当同一时刻的计算错误。** 本项未等待或审核角色1的新H2结果。

## 作者可用的实数结论

标签0与标签3的14工况×12层共168个主方向Bottom剪力记录，绝对峰减幅为6.851271%—30.545762%，反增为0/168；共同六工况为0/72。最大绝对峰时迁移12.76 s。这里的峰分别在各自保存时程上重新寻找，峰时差不是模态相位角。

|工况、楼层|标签0/标签3/实体峰值（kN）|三态各自峰时（s）|标签3相对0减幅|实体/标签3|
|---|---|---|---|---|
|SHW4Y，Story7|7343.5700 / 6788.3221 / 6715.1270|29.84 / 29.86 / 29.92|7.561008%|0.98921749|
|RH4X，Story1|10566.7533 / 8528.6654 / 8916.7141|21.68 / 12.20 / 12.08|19.287740%|1.04549934|

72个同名工况—楼层主方向记录中，实体装置模型的原生绝对峰高于标签3为34项，低于为38项，无相等项。这是模型输出的描述性对照，不能据此裁决两类阻尼策略优劣。

**正文必须保留的范围限定：** 以上为所列工况、楼层及保存时刻的原生Bottom剪力QT对照；实体模型与0/3的输入和完整主体身份尚未完全配对，不能把差异归因于阻尼方式，也不能直接解释为剔除Link后的主体弹性剪力QS或某阶模态贡献。标签0不是零阻尼认证，标签3也不是实际装置等效性认证。

## 独审依据与峰时规则

逐行独立重算168项减幅、峰变化、峰时差和同刻变化加重新寻峰恢复量的闭合；72项检查唯一工况—楼层—Bottom—主轴键、三态峰比、峰时、源行与原小表一致。抽核仅从三份旧NPZ各读取SHW4Y/Story7及RH4X/Story1两个组，共六组，不重提Excel、不新增ODE或频带分析。

从缓存重新枚举绝对最大值，并列峰取最早保存时刻；本次六组均为唯一峰。三份Story Forces元数据的VX/VY单位均为kN。两组的三态时间轴逐点相同；这只验证输出网格，不能补齐实体模型身份。

|工况、层|标签0/标签3/实体源行（Story Forces）|标签0/标签3/实体峰值符号|
|---|---|---|
|SHW4Y，Story7|212513 / 212514 / 90933|负 / 负 / 负|
|RH4X，Story1|424984 / 424510 / 179864|正 / 负 / 负|

源行来自旧缓存SourceRow列，已与两份冻结小表核对；本项没有重新打开原工作簿核单元格。RH4X的峰值符号改变说明独立绝对峰不能当同刻有符号量相减；当前小表保留的同刻变化与重新寻峰恢复量恰好闭合峰差，并非模态机制分解。

输入配对范围沿用旧native_paired_validation.json的14工况逐样本一致记录，本项校验其冻结SHA，并未重新提取输入函数。小表全量算术复核与六组缓存抽核分开记录，不宣称已独立重算全部168组时程峰。

下一项可审角色1冻结的同状态模态分解；本项没有用真实峰时差反推模态相位或因果。
'''
for case in ['SHW4Y', 'RH4X']:
    print(case, [(s['model'], s['signed_at_peak_kN'], s['SourceRow'], s['ties']) for s in samples if s['Case'] == case])
assert all(s['ties'] == 1 for s in samples)
assert all(s['signed_at_peak_kN'] < 0 for s in samples if s['Case'] == 'SHW4Y')
assert all(s['signed_at_peak_kN'] < 0 for s in samples if s['Case'] == 'RH4X' and s['model'] != 'label0')
p = OUT / 'R003-native-peak-review.md'
assert not p.exists()
p.write_bytes(report.encode('utf-8'))
end = now()
assert end <= DEADLINE
writejson('R003-checks.json', {'main_rows_arithmetic_checked': 168, 'common_three_model_rows_checked': 72, 'cache_groups_independently_read': arrays_read, 'samples': samples, 'higher_lower_equal': [hi, lo, 72-hi-lo], 'least': least, 'most': most, 'largest_abs_time_shift': shift, 'source_bindings': sources, 'whole_workbook_reads': 0, 'whole_time_history_reextractions': 0, 'new_ODE_frequency_or_modal_runs': 0})
writejson('R003-validation.json', {'status': 'frozen independent native-output audit; scoped pass', 'actual_start': START.isoformat(), 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'within_8_minutes': end <= DEADLINE, 'within_session_deadline': end <= datetime.fromisoformat('2026-10-20T21:44:25+08:00'), 'physical_complete_pairing_certified': False, 'new_agents_Git_ETABS_API': False, 'only_role2_written': True, 'qa': {'UTF8_LF': '\r' not in report, 'no_trailing_whitespace': all(x.rstrip() == x for x in report.splitlines()), 'JSON_parse': True}})
writejson('R003-manifest.json', {'frozen_at': end.isoformat(), 'files': [identity(OUT / n) for n in ['R003-audit-native-peaks.py', 'R003-native-peak-review.md', 'R003-checks.json', 'R003-validation.json']]})
print(json.dumps({'status': 'scoped pass', 'end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'higher_lower': [hi, lo], 'peak_reduction_range': [least['peak_reduction_percent'], most['peak_reduction_percent']], 'largest_time_shift_s': shift['peak_time_shift_s']}, ensure_ascii=False))
