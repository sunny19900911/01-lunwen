from pathlib import Path
from datetime import datetime, timedelta
import csv
import hashlib
import json
import numpy as np

OUT = Path(__file__).resolve().parent
SRC = OUT.parent / 'role1'
START = datetime.fromisoformat('2026-10-20T20:19:39.744320+08:00')
DEADLINE = START + timedelta(minutes=8)


def ident(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def same(a, b):
    assert np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), rtol=2e-12, atol=2e-13), (a, b)


def rc(name):
    with (SRC / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def js(name, obj):
    p = OUT / name
    assert not p.exists(), p
    p.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    json.loads(p.read_text(encoding='utf-8'))


assert datetime.now(START.tzinfo) < DEADLINE
assert not (OUT / 'R008-validation.json').exists()
sources = []
for manifest in [SRC / 'R006-manifest.json', OUT / 'R006-manifest.json']:
    sources.append(ident(manifest))
    for item in json.loads(manifest.read_text(encoding='utf-8'))['files']:
        p = Path(item['path']) if 'path' in item else manifest.parent / item['file']
        got = ident(p)
        assert got['bytes'] == item['bytes'] and got['sha256'] == item['sha256']
        sources.append(got)
known = {r['path']: r for r in json.loads((OUT / 'R006-checks.json').read_text(encoding='utf-8'))['source_bindings']}
freeze = json.loads((SRC / 'R006-input-freeze.json').read_text(encoding='utf-8'))
for item in freeze['source_files']:
    p = SRC / item['file']
    got = ident(p)
    assert got['sha256'] == item['sha256'] and got == known[str(p)]
    sources.append(got)
summary = json.loads((SRC / 'R003-none-summary.json').read_text(encoding='utf-8'))
M, K = np.array(summary['mass']), np.array(summary['stiffness'])
same(M, np.diag([1., 1.2, .8]))
same(K, [[2.4, -1, 0], [-1, 1.7, -.7], [0, -.7, .7]])
lam, phi = np.linalg.eig(np.linalg.solve(M, K))
assert np.isreal(lam).all() and np.isreal(phi).all()
order = np.argsort(lam)
lam, phi = lam[order], phi[:, order]
for k in range(3):
    phi[:, k] /= np.sqrt(phi[:, k] @ M @ phi[:, k])
    if phi[0, k] < 0:
        phi[:, k] *= -1
orth = float(np.max(abs(phi.T @ M @ phi - np.eye(3))))
eigerr = float(np.max(abs(K @ phi - (M @ phi) * lam)))
assert max(orth, eigerr) < 1e-12
same(phi, summary['phi_columns_mass_normalized'])
direction = np.ones(3)
weighted = M @ phi
gamma = phi.T @ M @ direction
mass = gamma**2 / (direction @ M @ direction)
same(sum(mass), 1.)
coefficient = phi[1] - phi[0]
roof_coefficient = phi[2]
table = rc('R006-shape-mass-local-shear.csv')
oldpeaks = {int(r['mode']): r for r in rc('R004-whole-window-mode-peaks.csv')}
assert len(table) == 3
peak_checks = []
max_product_error = 0.
for r in table:
    k = int(r['mode']) - 1
    old = oldpeaks[k+1]
    for field, value in [('Gamma_uniform_horizontal', gamma[k]), ('directional_effective_mass_ratio', mass[k]), ('directional_effective_mass_percent', 100*mass[k]), ('phi_base_massnorm', 0.), ('phi_floor1_massnorm', phi[0, k]), ('phi_floor2_massnorm', phi[1, k]), ('phi_floor3_roof_coefficient_massnorm', roof_coefficient[k]), ('QS2_coefficient_k2_times_phi2_minus_phi1', coefficient[k]), ('k2', 1.)]:
        same(r[field], value)
    for name in ['none', 'story1']:
        pq, pv = float(r[name+'_q_peak']), float(r[name+'_QS2_modal_peak'])
        same(pq, old[name+'_q_absolute_peak'])
        same(pv, old[name+'_absolute_peak'])
        product = abs(coefficient[k]) * pq
        same(product, pv)
        max_product_error = max(max_product_error, abs(product-pv))
        peak_checks.append({'mode': k+1, 'scheme': name, 'q_peak': pq, 'QS2_peak': pv, 'abs_L_times_q_peak': float(product), 'roof_single_mode_peak': float(abs(roof_coefficient[k])*pq), 'QS2_own_peak_time': float(old[name+'_peak_time'])})
third_weighted = weighted[:, 2]
same(sum(third_weighted), gamma[2])
assert third_weighted[0] > 0 and third_weighted[1] < 0 and third_weighted[2] > 0
assert abs(sum(third_weighted)) < sum(abs(third_weighted))
assert abs(coefficient[2]) > max(abs(coefficient[:2]))
for scheme in ['none', 'story1']:
    rr = [r for r in peak_checks if r['scheme'] == scheme]
    assert rr[2]['QS2_peak'] > max(r['QS2_peak'] for r in rr[:2])
    assert rr[2]['roof_single_mode_peak'] < min(r['roof_single_mode_peak'] for r in rr[:2])
    assert len({r['QS2_own_peak_time'] for r in rr}) == 3
for item in sources:
    assert ident(Path(item['path'])) == item
report = '''# R008｜方向有效质量与局部剪力系数独审

**采用：角色1冻结R006正文及三行配套表通过独立3×3代数复核，无数值必改项。** 全部峰值仅对照本角色R006已独审的R004冻结峰表；本项不读全时程、不新增ODE。

## 已核数值与解释

从M=diag(1,1.2,.8)和已知K另行求解广义特征向量，按频率升序、每列首分量为正并质量归一，所得Φ与表格一致。方向有效质量比依次为87.0288832618%、8.1819083912%、4.7892083469%，和为100%；前两阶累计95.2107916531%。

第二层弹性剪力系数k2(φ2r−φ1r)依次为+0.3156373469、−0.0221857350、−1.3165159292；k2=1。第三阶屋顶系数φ33为+0.2048249085。三阶×两方案共六项|L_r|P_qr=P_Vr均通过，振型、广义坐标峰和输出系数未混用不同归一方式。

第三阶的全楼质量加权振型分量约为+0.815911677、−0.600725102、+0.163859927，合为Γ3=+0.379046502，体现正负分量在整体加权和中部分抵消。相邻第一、二层分量却为+0.815911677和−0.500604252，取“第二层减第一层”得到−1.316515929。因此，小的方向有效质量和较大的局部剪力投影系数可以并存；这不是两种相互矛盾的贡献率。

旧H2中第三阶q峰虽较小，乘局部剪力系数后，无装置/层1装置的单阶QS2峰分别为0.0483567392/0.0393737883，均大于该方案前两阶各自峰。第三阶屋顶单阶峰则小于前两阶各自峰。该响应排序同时依赖已知q和输出系数，不能单凭质量参与率或系数大小推出任意输入下的响应排序。

## 必须保留的归一与峰值口径

Γ=φᵀM1及Γ²/(1ᵀM1)的写法要求φᵀMφ=1。若改用任意示意振型ψ=cφ，必须同时用qψ=q/c，输出系数改为cL，才能保持Lq不变；此时有效质量的一般式为(ψᵀM1)²/[(ψᵀMψ)(1ᵀM1)]。原稿已明确使用同一质量归一基，未发现示意归一混入。

L是带符号输出系数，不是剪力贡献百分数。各阶全程峰发生在不同时刻，不能相加成总峰；小质量参与率也不代表控制时刻剪力项必小。所有量为旧单向无量纲三层模型结果，不能将第三阶直接命名为实际建筑扭转模态或推广成普遍高阶规律。

## 可直接写稿的简短正文

第三阶振型在相邻楼层反向，质量加权求和时部分抵消，而第二层层间振型差却较大，因而其方向有效质量仅占4.7892%，第二层剪力系数绝对值仍达1.3165。在旧H2响应中，该系数与配套广义位移相乘，使第三阶单阶剪力峰高于前两阶各自峰；这说明方向有效质量不能替代局部剪力分析。各阶系数和响应必须采用同一归一基，并按同一时刻叠加，不能将独立峰值相加或解释为贡献率。
'''
p = OUT / 'R008-shape-mass-review.md'
assert not p.exists()
p.write_bytes(report.encode('utf-8'))
end = datetime.now(START.tzinfo)
assert end <= DEADLINE
js('R008-checks.json', {'source_bindings': sources, 'M': M.tolist(), 'K': K.tolist(), 'independent_mass_normalized_phi': phi.tolist(), 'mass_orthogonality_error': orth, 'eigen_equation_error': eigerr, 'Gamma': gamma.tolist(), 'directional_effective_mass_ratios': mass.tolist(), 'QS2_coefficients': coefficient.tolist(), 'roof_coefficients': roof_coefficient.tolist(), 'third_mode_mass_weighted_components': third_weighted.tolist(), 'six_peak_product_checks': peak_checks, 'max_abs_peak_product_error': max_product_error, 'full_state_reads': 0, 'new_ODE': 0})
js('R008-validation.json', {'status': 'adopt shape/mass/local-output explanation; no numerical changes', 'actual_start': START.isoformat(), 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'within_8_minutes': end <= DEADLINE, 'only_role2_written': True, 'no_new_ODE_ETABS_Git_automation_agents': True, 'qa': {'UTF8_LF': '\r' not in report, 'no_trailing_whitespace': all(x.rstrip() == x for x in report.splitlines()), 'JSON_parse': True}})
js('R008-manifest.json', {'frozen_at': end.isoformat(), 'files': [ident(OUT / n) for n in ['R008-audit-shape-mass.py', 'R008-shape-mass-review.md', 'R008-checks.json', 'R008-validation.json']]})
print(json.dumps({'status': 'adopt', 'end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'mass_percent': (100*mass).tolist(), 'QS2_coefficients': coefficient.tolist(), 'roof3': float(roof_coefficient[2]), 'peak_product_max_error': max_product_error}, ensure_ascii=False))
