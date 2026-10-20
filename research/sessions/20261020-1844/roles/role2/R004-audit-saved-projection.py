from pathlib import Path
from datetime import datetime, timedelta
import csv
import hashlib
import json
import numpy as np

OUT = Path(__file__).resolve().parent
SRC = OUT.parent / 'role1'
START = datetime.fromisoformat('2026-10-20T19:46:55.274376+08:00')
DEADLINE = START + timedelta(minutes=8)


def identity(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def check(p, entry):
    got = identity(p)
    assert got['bytes'] == entry['bytes'] and got['sha256'] == entry['sha256'], p
    return got


def same(a, b, atol=2e-13):
    assert np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), rtol=2e-12, atol=atol), (a, b)


def writejson(name, obj):
    p = OUT / name
    assert not p.exists()
    p.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    json.loads(p.read_text(encoding='utf-8'))


assert datetime.now(START.tzinfo) < DEADLINE
assert not (OUT / 'R004-validation.json').exists()
final = SRC / 'R003-final-manifest.json'
fm = json.loads(final.read_text(encoding='utf-8'))
sources = [identity(final)]
for item in fm['files']:
    sources.append(check(SRC / item['file'], item))
assert fm['preferred_report'] == 'R003-report-v002.md'
freeze = json.loads((SRC / 'R003-input-freeze.json').read_text(encoding='utf-8'))
base = Path(freeze['source_root'])
mp = base / 'H021-delivery-manifest.json'
assert identity(mp)['sha256'] == freeze['H021_manifest_sha256']
sources.append(identity(mp))
manifest = json.loads(mp.read_text(encoding='utf-8'))
entries = manifest['files'] + manifest['local_only_states']


def checked(p):
    entry = next(x for x in entries if Path(x['path']).resolve() == p.resolve())
    sources.append(check(p, entry))


prepath = base / 'H021-three-floor-prospective/pre-run-freeze.json'
checked(prepath)
pre = json.loads(prepath.read_text(encoding='utf-8'))
M, K, D = (np.array(pre[k]) for k in ['M', 'K', 'D'])
stiff = np.array(pre['story_stiffness'])
same(K, D.T @ np.diag(stiff) @ D)
same(pre['C'], .02 * K)
# Independent generalized eigenvector construction; no original script imports.
lam, phi = np.linalg.eig(np.linalg.solve(M, K))
assert np.isreal(lam).all() and np.isreal(phi).all()
order = np.argsort(lam)
lam, phi = lam[order], phi[:, order]
for j in range(3):
    phi[:, j] /= np.sqrt(phi[:, j] @ M @ phi[:, j])
    if phi[0, j] < 0:
        phi[:, j] *= -1
orth = float(np.max(np.abs(phi.T @ M @ phi - np.eye(3))))
eigerr = float(np.max(np.abs(K @ phi - (M @ phi) * lam)))
assert max(orth, eigerr) < 1e-12
coeffs = {'QS2': phi[1] - phi[0], 'roof': phi[2]}
same(stiff[1] * D[1], [-1, 1, 0])
mass_ratios = (phi.T @ M @ np.ones(3)) ** 2 / np.sum(M)
with (SRC / 'R003-mechanism-table.csv').open(encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 8
index = {(int(r['position']), r['quantity'], r['anchor']): r for r in rows}
assert len(index) == 8
summaries, anchors, global_errors = [], [], []
for pos, tag in [(0, 'none'), (1, 'story1')]:
    old = json.loads((SRC / ('R003-' + tag + '-summary.json')).read_text(encoding='utf-8'))
    same(old['phi_columns_mass_normalized'], phi)
    same(old['omega'], np.sqrt(lam))
    path = base / 'H021-three-floor-prospective/local-only' / f'H2_envelope__position{pos}__h0.005.npz'
    checked(path)
    with np.load(path, allow_pickle=False) as z:
        a = z['trajectory']
    cols = pre['state_columns']
    t = a[:, cols.index('t')]
    u = a[:, [cols.index('u1'), cols.index('u2'), cols.index('u3')]]
    assert len(t) == 40001 and t[0] == 0 and t[-1] == 200
    assert np.isfinite(a).all() and np.all(np.diff(t) > 0)
    same(np.diff(t), .005)
    # Recover coordinates by full linear-system solve, then compare the mass projection.
    q = np.linalg.solve(phi, u.T).T
    coordinate_error = float(np.max(np.abs(q - u @ M @ phi)))
    recovery_error = float(np.max(np.abs(q @ phi.T - u)))
    assert max(coordinate_error, recovery_error) < 1e-12
    for label in ['QS2', 'roof']:
        direct = u[:, 1] - u[:, 0] if label == 'QS2' else u[:, 2]
        terms = q * coeffs[label]
        two = terms[:, 0] + terms[:, 1]
        three = np.sum(terms, axis=1)
        err = float(np.max(np.abs(direct - three)))
        tailerr = float(np.max(np.abs(direct - two - terms[:, 2])))
        assert max(err, tailerr) < 1e-12
        global_errors.append(err)
        i = int(np.argmax(np.abs(direct)))
        j = int(np.argmax(np.abs(two)))
        p, pr = float(abs(direct[i])), float(abs(two[j]))
        expected = next(x for x in old['summaries'] if x['quantity'] == label)
        for field, value in [('full_peak', p), ('full_peak_t', t[i]), ('two_mode_posthoc_peak', pr), ('two_mode_peak_t', t[j]), ('signed_peak_change_relative', pr / p - 1)]:
            same(expected[field], value)
        summaries.append({'position': pos, 'quantity': label, 'full_peak': p, 'full_peak_t': float(t[i]), 'two_mode_posthoc_peak': pr, 'two_mode_peak_t': float(t[j]), 'signed_peak_change_percent': 100 * (pr / p - 1), 'coordinate_projection_max_error': coordinate_error, 'u_recovery_max_error': recovery_error, 'output_recovery_max_error': err, 'tail_identity_max_error': tailerr})
        for name, n in [('full_output_own_peak', i), ('two_mode_posthoc_own_peak', j)]:
            r = index[(pos, label, name)]
            same(int(r['index']), n)
            same(r['time_nondimensional'], t[n])
            same([float(r['mode' + str(k) + '_signed']) for k in [1, 2, 3]], terms[n])
            den = float(np.sum(np.abs(terms[n])))
            for field, value in [('two_mode_signed_sum', two[n]), ('three_mode_signed_sum', three[n]), ('direct_full_signed', direct[n]), ('sum_abs_modal_terms', den), ('absolute_sum_over_sum_absolute', abs(three[n]) / den), ('full_peak', p), ('two_mode_posthoc_peak', pr), ('signed_peak_change_relative', pr / p - 1)]:
                same(float(r[field]), value)
            anchors.append({'position': pos, 'quantity': label, 'anchor': name, 'index': n, 'time': float(t[n]), 'terms': terms[n].tolist(), 'direct': float(direct[n])})
    assert old['new_ODE_runs'] == 0 and old['not_a_reduced_feedback_solve']
script = (SRC / 'R003-project-saved.py').read_text(encoding='utf-8')
assert "source) as f:a=f['trajectory']" in script
assert 'terms[:,:2].sum(axis=1)' in script
assert 'solve_ivp' not in script and 'from ' not in script.replace('from pathlib import Path', '')
# Review results are newly computed from only two frozen full trajectories.
report = f'''# R004｜旧H2完整状态投影独审

**采用：角色1 R003-report-v002.md及8行机制表通过独立复核，无需修改其四组数值或方法公式。** 采用版本以R003-final-manifest.json为准，不回退到旧report.md。本项未读取角色1新R004。

## 独立核查结果

两组旧H2完整状态均由H021正式清单验证字节与SHA256，每组40001节点、h=.005、t∈[0,200]。按冻结state_columns定位u1/u2/u3，使用M⁻¹K的特征向量另行构建质量归一基，并用ΦQᵀ=Uᵀ的线性方程恢复Q，与质量投影UMΦ对照；未运行角色1脚本、未导入源runner，也未求解ODE。

质量正交误差为{orth:.3e}，特征方程误差为{eigerr:.3e}，完整输出重构最大误差为{max(global_errors):.3e}，均通过1e−12检查。QS2直接按u2−u1计算，其系数为φ2k−φ1k；roof按u3计算，系数为φ3k。与冻结模型的diag(k)D一致。两条状态使用同一参考主体基；背景C=.02K非零。

四组完整峰及两阶后验峰、其各自峰时和全部8个锚点的三阶有符号项、两阶和、三阶和、直接值、绝对项和及抵消比均通过核对。第一、第二阶累计方向有效质量独立算得{100 * sum(mass_ratios[:2]):.8f}%，仍不能将它改称剪力贡献率。

|方案|输出|完整峰|两阶后验峰|有符号相对峰差/%|
|---|---|---:|---:|---:|
'''
for r in summaries:
    report += f"|{'无装置' if r['position'] == 0 else '层1装置'}|{r['quantity']}|{r['full_peak']:.11f}|{r['two_mode_posthoc_peak']:.11f}|{r['signed_peak_change_percent']:+.6f}|\n"
report += '''
## 采用与必须保留的口径

数值与机制表采用，无科学内容必改项。写稿时必须保留“同一完整保存状态、后验截断、无量纲保存网格”这三个条件：43.3215%/41.6360%不能写成两阶重新耦合求解误差或FNA误差；1.8839%/3.1416%是roof峰高估，不能写成低估。四个输出—方案组合各有完整峰和两阶峰，共8次寻峰与8个锚点，不是只在一个统一控制时刻比较。

完整QS2峰时三项同号、roof完整峰时第三阶与前两阶和反号的描述通过。不同方案各自峰时的分量不能直接相减认定装置相位因果；完整峰差也不等于某个任选锚点的第三阶项。当前结果没有混用两阶重解：所有分量来自两条完整三层轨迹，第二阶后验和仅为相同Q的前两列相加。

## 可直接写稿的三句话

在旧三层H2输入下，对无装置与第一层装置两组完整保存状态采用同一质量归一参考振型基展开，三阶重构均与直接输出在数值精度内一致。

仅保留前两阶作后验重构时，第二层主体弹性剪力的保存网格峰值分别低估43.3215%和41.6360%，而屋顶位移峰值分别高估1.8839%和3.1416%。

这一有限模型结果表明，前两阶累计方向有效质量达到95.2108%仍不足以保证局部剪力峰重构准确；所列差异属于同状态后验截断，不代表两阶重新耦合求解误差或真实建筑的逐阶归因。
'''
p = OUT / 'R004-H2-projection-review.md'
assert not p.exists()
p.write_bytes(report.encode('utf-8'))
end = datetime.now(START.tzinfo)
assert end <= DEADLINE
writejson('R004-checks.json', {'source_bindings': sources, 'mass_orthogonality_error': orth, 'eigen_equation_error': eigerr, 'output_coefficients': {k: v.tolist() for k, v in coeffs.items()}, 'directional_mass_ratios': mass_ratios.tolist(), 'four_output_peak_groups': summaries, 'eight_anchors': anchors, 'saved_states_read': 2, 'new_ODE': 0, 'reduced_feedback_results_read': 0})
writejson('R004-validation.json', {'status': 'adopt scoped saved-state results; no numerical corrections required', 'actual_start': START.isoformat(), 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'within_8_minutes': end <= DEADLINE, 'only_role2_written': True, 'no_ODE_ETABS_Git_automation_agents': True, 'execution_repair': 'First audit execution stopped at CSV string/float comparison; numeric coercion repaired before any result file was written. No source data or scientific formula changed.', 'qa': {'UTF8_LF': '\r' not in report, 'no_trailing_whitespace': all(x.rstrip() == x for x in report.splitlines()), 'JSON_parse': True}})
writejson('R004-manifest.json', {'frozen_at': end.isoformat(), 'files': [identity(OUT / name) for name in ['R004-audit-saved-projection.py', 'R004-H2-projection-review.md', 'R004-checks.json', 'R004-validation.json']]})
print(json.dumps({'end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'status': 'adopt', 'orth_error': orth, 'full_output_error': max(global_errors), 'peak_relative_changes_percent': [r['signed_peak_change_percent'] for r in summaries], 'anchors': len(anchors)}, ensure_ascii=False))
