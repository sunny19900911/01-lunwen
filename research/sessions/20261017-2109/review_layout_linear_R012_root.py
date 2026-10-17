"""Independent floating analytic LTI check of frozen synthetic RK4 results.

Matrix eigendecomposition and analytic quadratic integrals, not RK4 or an ODE
error certificate. Writes one small new review; no full arrays or source edits.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
from datetime import datetime
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R012-layout-symmetry-synthetic'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def modes(A, x):
    ev, V = np.linalg.eig(A.astype(complex))
    coeff = np.linalg.solve(V, x.astype(complex))
    cond = float(np.linalg.cond(V))
    residual = float(np.max(abs(A @ V - V * ev)))
    assert cond < 1e9 and residual < 1e-10
    return ev, V, coeff, cond, residual


def values(mode, t):
    ev, V, coeff, _, _ = mode
    out = (V * coeff) @ np.exp(ev[:, None] * t[None, :])
    imag = float(np.max(abs(out.imag)))
    assert imag < 1e-8
    return out.real, imag


def quadratic_integral(mode, Q, duration):
    ev, V, coeff, _, _ = mode
    sums = ev[:, None] + ev[None, :]
    integ = np.full(sums.shape, duration, dtype=complex)
    nz = abs(sums) > 1e-12
    integ[nz] = np.expm1(sums[nz] * duration) / sums[nz]
    # Bilinear transpose, not conjugate: x is real through conjugate pairs.
    ans = np.sum((coeff[:, None] * coeff[None, :]) * (V.T @ Q @ V) * integ)
    assert abs(ans.imag) < 1e-7
    return float(ans.real)


def main():
    target = HERE / 'R009-layout-numerical-root-review.json'
    assert not target.exists()
    protocol = HERE / 'layout-symmetry-protocol-v001.json'
    assert digest(protocol) == '5fbd02e556ec24a7b4431cef5a09e749596b47466b8a32a2990f47a76c2ce41e'
    p = json.loads(protocol.read_text(encoding='utf-8'))
    manifest = json.loads((SOURCE / 'delivery_manifest_r012.json').read_text(encoding='utf-8'))
    checked = {}
    for f in manifest['files']:
        q = SOURCE / f['name']
        assert q.stat().st_size == f['bytes'] and digest(q) == f['sha256']
        checked[f['name']] = f['sha256']
    rows = list(csv.DictReader((SOURCE / 'four_actual_runs_r012.csv').open(encoding='utf-8', newline='')))
    eps = p['epsilon']
    K = np.array([[1 + eps, -eps], [-eps, 1 + eps]])
    w = math.sqrt(1 + 2 * eps)
    C = .1 * w / (1 + w) * np.eye(2) + .1 / (1 + w) * K
    roots = np.roots([1., 0., -3., .1])
    r = float(next(x.real for x in roots if abs(x.imag) < 1e-12 and 1.7 < x.real < 1.73))
    rate = r ** 3
    k = 3 * r * r - 1 - .1 * rate
    c = k / rate
    T = 20 * math.pi
    results = []
    for row in rows:
        port = 0 if row['layout'] == 'A' else 1
        B = np.eye(2)[port]
        A = np.zeros((5, 5))
        A[:2, 2:4] = np.eye(2)
        A[2:4, :2] = -K
        A[2:4, 2:4] = -C
        A[2:4, 4] = -B
        A[4, 2:4] = k * B
        A[4, 4] = -rate
        driven = np.zeros((7, 7))
        driven[:5, :5] = A
        driven[2:4, 5] = 1.
        driven[5, 6] = 1.
        driven[6, 5] = -1.
        init = np.zeros(7)
        init[6] = 1.
        before = modes(driven, init)
        xT, _ = values(before, np.array([T]))
        after = modes(A, xT[:5, 0])
        assert max(after[0].real) < 0.
        N = int(row['N_steps_per_T'])
        prefix, im1 = values(before, np.arange(N + 1) * T / N)
        suffix, im2 = values(after, np.arange(1, 5 * N + 1) * T / N)
        path = np.concatenate([prefix[:5], suffix], axis=1)
        peak_u = float(np.max(abs(path[0])))
        peak_f = float(np.max(abs(path[4])))
        E = lambda x: float((x[2:4] @ x[2:4] + x[:2] @ K @ x[:2] + x[4] ** 2 / k) / 2)
        terminal, _ = values(after, np.array([5 * T]))
        Qbg = np.zeros((7, 7)); Qbg[2:4, 2:4] = C
        Qdd = np.zeros((7, 7)); Qdd[4, 4] = 1 / c
        Qw = np.zeros((7, 7)); Qw[2:4, 5] = .5; Qw[5, 2:4] = .5
        db = quadratic_integral(before, Qbg, T) + quadratic_integral(after, Qbg[:5, :5], 5 * T)
        dd = quadratic_integral(before, Qdd, T) + quadratic_integral(after, Qdd[:5, :5], 5 * T)
        work = quadratic_integral(before, Qw, T)
        analytic = {'sampled_u1_abs_peak': peak_u, 'sampled_device_force_abs_peak': peak_f,
                    'E_at_T': E(xT[:5, 0]), 'E_terminal_6T': E(terminal[:, 0]),
                    'W_terminal': work, 'Db_terminal': db, 'Dd_terminal': dd}
        diff = {n: analytic[n] - float(row[n]) for n in analytic}
        assert max(abs(d) for d in diff.values()) < 2e-7
        results.append({'layout': row['layout'], 'N': N, 'analytic_floating_values': analytic,
                        'analytic_minus_frozen_RK4': diff,
                        'energy_balance_terminal': analytic['E_terminal_6T'] - work + db + dd,
                        'eigenvector_condition': [before[3], after[3]],
                        'eigendecomposition_residual': [before[4], after[4]],
                        'max_trajectory_imaginary_residual': max(im1, im2)})
    out = {'finished_at': datetime.now().astimezone().isoformat(), 'root_protocol_sha256': digest(protocol),
           'source_manifest_sha256': digest(SOURCE / 'delivery_manifest_r012.json'), 'checked_source_files': checked,
           'code_sha256': digest(Path(__file__)), 'independent_algorithm': 'LTI eigendecomposition plus exact-form floating quadratic integrals, no RK4',
           'numpy': np.__version__, 'four_run_checks': results,
           'scope': 'synthetic alpha1 finite-grid arithmetic independently checked; floating tolerances are diagnostic, not rigorous error bounds or fulltail proof; no real ETABS validation',
           'passed': True, 'full_arrays_written': False}
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'runs': len(results), 'max_abs_analytic_minus_RK4': max(abs(v) for x in results for v in x['analytic_minus_frozen_RK4'].values()), 'output': str(target)}))


if __name__ == '__main__':
    main()
