"""One frozen candidate, independent full-matrix powers and direct positive sums."""
from pathlib import Path
import json
import numpy as np

O = Path(__file__).resolve().parent; P = O.parents[2] / 'roles/role4/R004'
with np.load(P / 'local-cache/baseline-sensitivities-and-frozen-predictions.npz', allow_pickle=False) as a:
    ag, om, B, s0, v0, Z, ZD, W, WD = [a[k].copy() for k in ['ag_in_s2', 'omega', 'B', 's_unit', 'sdot_unit', 'z_unit', 'zdot_unit', 'w_unit', 'wdot_unit']]
with np.load(P / 'local-cache/frozen-discrete-envelopes.npz', allow_pickle=False) as a:
    saved = {o: a[f'z0.08_order{o}_E_kip'].copy() for o in [1, 2]}
h = .005; z = .08; N = len(ag); eps = np.finfo(float).eps
F = np.zeros((12, 2, 2)); F[:, 0, 1] = 1; F[:, 1, 0] = -om ** 2; F[:, 1, 1] = -2 * z * om
ev, vv = np.linalg.eig(F); A = ((vv * np.exp(ev * h)[:, None, :]) @ np.linalg.inv(vv)).real
gf = np.tile([0., -1.], (12, 1)); identity = np.eye(2)[None]
m0 = np.linalg.solve(F, np.einsum('mij,mj->mi', A - identity, gf)[..., None])[..., 0]
m1 = np.linalg.solve(F, np.linalg.solve(F, np.einsum('mij,mj->mi', A - identity - F * h, gf)[..., None]))[..., 0]
sl = np.diff(ag) / h; b = ag[:-1, None, None] * m0[None] + sl[:, None, None] * m1[None]
power = np.tile(np.eye(2), (12, 1, 1)); kq = np.empty((N - 1, 12)); kv = np.empty_like(kq)
for k in range(N - 1):
    kq[k] = abs(power[:, 0, 0]); kv[k] = abs(power[:, 0, 1]); power = A @ power
alpha = z * om; beta = om * np.sqrt(1 - z * z); tau = np.arange(N - 1)[:, None] * h
de = np.exp(-tau * alpha); co = np.cos(tau * beta); si = np.sin(tau * beta) / beta
kq += 128 * eps * de * (abs(co) + abs(alpha * si) + 1)
kv += 128 * eps * de * (abs(si) + 1 / om)
rows = []
for order in [1, 2]:
    delta = z - .05; s = s0 + delta * Z + (delta ** 2 * W / 2 if order == 2 else 0)
    v = v0 + delta * ZD + (delta ** 2 * WD / 2 if order == 2 else 0)
    x = np.stack([s, v], axis=2); defect = np.einsum('mij,nmj->nmi', A, x[:-1]) + b - x[1:]
    qp0 = -ag[:-1, None] / om ** 2 + 2 * alpha * sl[:, None] / om ** 4
    qp1 = -ag[1:, None] / om ** 2 + 2 * alpha * sl[:, None] / om ** 4
    vp = -sl[:, None] / om ** 2; sq = s[:-1] - qp0; sv = v[:-1] - vp
    aq = abs(defect[:, :, 0]) + 64 * eps * (abs(A[:, 0, 0] * sq) + abs(A[:, 0, 1] * sv) + abs(qp1) + abs(s[1:]))
    av = abs(defect[:, :, 1]) + 64 * eps * (abs(A[:, 1, 0] * sq) + abs(A[:, 1, 1] * sv) + abs(vp) + abs(v[1:]))
    fftg = 1e-12 * (kq.sum(0) * aq.sum(0) + kv.sum(0) * av.sum(0))
    for n in [0, 1, N // 2, N - 1]:
        modal = np.zeros(12) if n == 0 else (kq[:n][::-1] * aq[:n] + kv[:n][::-1] * av[:n]).sum(0) + fftg
        E = (abs(B) * om ** 2) @ modal
        rows.append({'zeta': z, 'order': order, 'index': n, 'max_all3_E_difference_kip': float(np.max(abs(E - saved[order][n])))})
assert max(d['max_all3_E_difference_kip'] for d in rows) < 1e-6
with (O / 'independent-public-envelope-points-8.json').open('x', encoding='utf-8') as f: json.dump(rows, f, indent=2)
print(json.dumps({'fixed_zeta': z, 'all12_modes_points': len(rows), 'maximum_E_difference_kip': max(d['max_all3_E_difference_kip'] for d in rows)}))
