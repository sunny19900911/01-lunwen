"""Finite two-story check, zero initial state; no engineering cache access."""
from pathlib import Path
import csv
import hashlib
import json
import math
import numpy as np

OUT = Path(__file__).resolve().parent
K = np.array([[2., -1.], [-1., 1.]])
lam, phi = np.linalg.eigh(K)
omega = np.sqrt(lam)
gamma = phi.T @ np.ones(2)
B = phi[0] * gamma  # first-story elastic spring force, k1=1
ZETA0, DELTA, T = .05, .03, 120.


def excitation(t, packet):
    start, duration, frequency = (0., 60., omega[0]) if packet == 0 else (80., 30., omega[1])
    tau = t - start
    if tau < 0 or tau > duration:
        return 0.
    return math.sin(math.pi * tau / duration) ** 2 * math.sin(frequency * tau)


def solve(dt, zeta, packet, derivatives=False):
    n = round(T / dt)
    # Each row is one mode; columns s, sdot, z, zdot, w, wdot.
    state = np.zeros((2, 6))
    history = np.zeros((n + 1, 2, 6))

    def rhs(t, x):
        out = np.zeros_like(x)
        out[:, 0::2] = x[:, 1::2]
        out[:, 1] = -2 * zeta * omega * x[:, 1] - lam * x[:, 0] - excitation(t, packet)
        if derivatives:
            out[:, 3] = -2 * zeta * omega * x[:, 3] - lam * x[:, 2] - 2 * omega * x[:, 1]
            out[:, 5] = -2 * zeta * omega * x[:, 5] - lam * x[:, 4] - 4 * omega * x[:, 3]
        return out

    for j in range(n):
        t = j * dt
        k1 = rhs(t, state)
        k2 = rhs(t + dt / 2, state + dt * k1 / 2)
        k3 = rhs(t + dt / 2, state + dt * k2 / 2)
        k4 = rhs(t + dt, state + dt * k3)
        state = state + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        history[j + 1] = state
    return np.arange(n + 1) * dt, history


def output(h, column=0):
    return h[:, :, column] @ B


def run():
    if (OUT / 'prediction-freeze.json').exists():
        raise FileExistsError('Frozen run exists; use a fresh isolated directory.')
    t, h0 = solve(.01, ZETA0, 0, True)
    _, h1 = solve(.01, ZETA0, 1, True)
    early = t < 80
    y0, y1 = output(h0), output(h1)
    early_peak = float(np.max(np.abs(y0[early])))
    desired_late = early_peak / 1.002
    lo, hi = 0., 100.
    for _ in range(55):
        middle = (lo + hi) / 2
        if np.max(np.abs((y0 + middle * y1)[~early])) > desired_late:
            hi = middle
        else:
            lo = middle
    amplitude = (lo + hi) / 2
    h = h0 + amplitude * h1
    y = output(h)
    z, w = output(h, 2), output(h, 4)
    pred1 = y + DELTA * z
    pred2 = pred1 + .5 * DELTA ** 2 * w
    config = {'M': [[1, 0], [0, 1]], 'K': K.tolist(), 'output': 'u1 N; first-story spring k1=1 N/m',
              'initial_states': 'all zero for every damping; derivative states zero',
              'zeta0': ZETA0, 'delta': DELTA, 'duration_s': T, 'dt_s': .01,
              'input': 'sum of two disjoint sine-squared sine packets: [0,60], [80,110]',
              'second_packet_amplitude': amplitude, 'omega_rad_s': omega.tolist(),
              'B': B.tolist(), 'selection': 'amplitude tuned using baseline .05 only; late peak=early/1.002',
              'target_response_read_before_prediction_freeze': False}
    (OUT / 'prediction-freeze.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    # Only now generate candidate references for the frozen excitation.
    _, hc0 = solve(.01, ZETA0 + DELTA, 0)
    _, hc1 = solve(.01, ZETA0 + DELTA, 1)
    actual = output(hc0 + amplitude * hc1)
    i0 = int(np.argmax(np.abs(y)))
    rows = []
    for name, curve in [('baseline', y), ('linear', pred1), ('quadratic', pred2), ('candidate', actual)]:
        ip = int(np.argmax(np.abs(curve)))
        rows.append({'method': name, 'peak_N': float(abs(curve[ip])), 'peak_time_s': float(t[ip]),
                     'early_peak_N': float(np.max(np.abs(curve[early]))),
                     'late_peak_N': float(np.max(np.abs(curve[~early]))),
                     'old_peak_time_value_abs_N': float(abs(curve[i0]))})
    with (OUT / 'peak-comparison.csv').open('x', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    # Infinite-horizon impulse-response L1 bound for 0<zeta<1.
    zc = ZETA0 + DELTA
    l1 = 1 / lam / np.tanh(math.pi * zc / (2 * math.sqrt(1 - zc ** 2)))
    r1 = 2 * omega * DELTA ** 2 * h[:, :, 3]
    r2 = omega * DELTA ** 3 * h[:, :, 5]
    e1 = float(np.sum(np.abs(B) * l1 * np.max(np.abs(r1), axis=0)))
    e2 = float(np.sum(np.abs(B) * l1 * np.max(np.abs(r2), axis=0)))
    # Numeric implementation checks: independent parameter differences and step halving.
    eps = 1.e-4
    _, hp0 = solve(.01, ZETA0 + eps, 0)
    _, hp1 = solve(.01, ZETA0 + eps, 1)
    _, hm0 = solve(.01, ZETA0 - eps, 0)
    _, hm1 = solve(.01, ZETA0 - eps, 1)
    yp = output(hp0 + amplitude * hp1); ym = output(hm0 + amplitude * hm1)
    fd_z = (yp - ym) / (2 * eps); fd_w = (yp - 2 * y + ym) / eps ** 2
    tf, hf0 = solve(.005, ZETA0 + DELTA, 0)
    _, hf1 = solve(.005, ZETA0 + DELTA, 1)
    actual_fine = output(hf0 + amplitude * hf1)
    result = {'comparison': rows, 'parameter_derivative_relative_inf_errors': {
        'z_central_difference': float(np.max(np.abs(z - fd_z)) / np.max(np.abs(z))),
        'w_central_difference': float(np.max(np.abs(w - fd_w)) / np.max(np.abs(w)))},
        'candidate_dt_halving_max_N': float(np.max(np.abs(actual - actual_fine[::2]))),
        'candidate_dt_halving_peak_difference_N': float(abs(np.max(abs(actual)) - np.max(abs(actual_fine)))),
        'linear_curve_max_error_N': float(np.max(np.abs(actual - pred1))),
        'quadratic_curve_max_error_N': float(np.max(np.abs(actual - pred2))),
        'linear_residual_bound_N': e1, 'quadratic_residual_bound_N': e2,
        'bound_evaluation_caveat': 'sampled residual maxima; numerical check, not directed-rounded continuous certificate',
        'baseline_old_peak_linear_reduction': float(1 - abs(pred1[i0]) / abs(y[i0])),
        'whole_curve_linear_reduction': float(1 - np.max(abs(pred1)) / np.max(abs(y))),
        'actual_reduction': float(1 - np.max(abs(actual)) / np.max(abs(y))),
        'prediction_freeze_sha256': hashlib.sha256((OUT / 'prediction-freeze.json').read_bytes()).hexdigest()}
    assert rows[0]['peak_time_s'] < 80 and rows[3]['peak_time_s'] >= 80
    assert rows[1]['peak_time_s'] >= 80
    assert result['candidate_dt_halving_max_N'] < 1e-6
    assert result['parameter_derivative_relative_inf_errors']['z_central_difference'] < 1e-4
    assert result['parameter_derivative_relative_inf_errors']['w_central_difference'] < 1e-4
    assert result['linear_curve_max_error_N'] <= e1 and result['quadratic_curve_max_error_N'] <= e2
    (OUT / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    run()
