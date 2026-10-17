"""Independent finite FOH displacement replay via analytic lag kernels and FFT."""
from pathlib import Path
from datetime import datetime
import csv
import hashlib
import json
import math
import sys
import time
import numpy as np

S = Path(__file__).resolve().parent
R = S.parents[2]
O = S / 'R014-force-replay-FFT'
B = R / 'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004'


def record(p):
    raw = p.read_bytes()
    return {'path': str(p), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    start = time.perf_counter()
    O.mkdir(exist_ok=True)
    assert not (O / 'summary.json').exists(), 'Frozen result already exists'
    protocol = S / 'force-replay-independent-FFT-protocol-v001.md'
    source = B / 'R016-addition-local-peak-synthetic/local-cache/four_actual_RK4_histories.npz'
    old = B / 'R019-force-output-replay-prototype'
    refs = [record(protocol), record(source), record(old / 'summary_r019.json'), record(old / 'four_fixed_point_replay.csv'), record(Path(__file__))]
    assert refs[1]['sha256'] == '6adf4f158d320c84f7cfa2cbab2c8cfce34d86839573cbf82a027a88681a6a62'
    assert refs[2]['sha256'] == 'd84bc3f9fe6225e4c1ec9a9dd82b4ca6fe0349455ae53b5bfe1e707d9047d29f'
    prior = json.loads((old / 'summary_r019.json').read_text(encoding='utf-8'))
    with np.load(source, allow_pickle=False) as archive:
        data = archive['D_N16384']
        assert data.shape == (98305, 9) and data.dtype == np.float64
        t = data[:, 0].copy()
        targets = data[:, 1:3].copy()
        force = data[:, 5].copy()
    del data
    N = 16384
    steps = 6 * N
    omega_input = math.sqrt(2)
    T = 20 * math.pi / omega_input
    h = T / N
    assert np.array_equal(t, np.arange(steps + 1) * h)
    assert np.isfinite(np.c_[t, targets, force]).all()
    length = 1 << ((2 * steps - 2).bit_length())
    assert length >= 2 * steps - 1
    force_left = np.fft.rfft(force[:-1], length)
    force_right = np.fft.rfft(force[1:], length)
    modal = []
    lag = np.arange(steps) * h
    scale = 1 / math.sqrt(2)
    kernel_checks = []
    for stiffness, beta in [(1.0, scale), (3.0, -scale)]:
        omega = math.sqrt(stiffness)
        decay = .05 * omega
        damped = math.sqrt(stiffness - decay * decay)
        z = complex(-decay, damped)
        em1 = np.expm1(z * h)
        e = 1 + em1
        left_c = e / z - em1 / (h * z * z)
        right_c = em1 / (h * z * z) - 1 / z
        propagation = np.exp(z * lag)
        left = np.imag(propagation * left_c) / damped
        right = np.imag(propagation * right_c) / damped
        convolution = np.fft.irfft(np.fft.rfft(left, length) * force_left + np.fft.rfft(right, length) * force_right, length)[:steps]
        values = np.r_[0., -beta * convolution]
        assert len(values) == steps + 1 and np.isfinite(values).all()
        modal.append(values)
        kernel_checks.append({'stiffness_exact_float': stiffness, 'beta': beta, 'left_at_zero_lag': float(left[0]),
                              'right_at_zero_lag': float(right[0]), 'FFT_linear_padding_length': length})
    # Independent harmonic transfer form of the zero-initial bare reference.
    H = 1 / complex(1 - omega_input ** 2, .1 * omega_input)
    a = .05
    nu = math.sqrt(1 - a * a)
    C0 = -H.imag
    D0 = (-omega_input * H.real + a * C0) / nu

    def loaded(x):
        return np.imag(H * np.exp(1j * omega_input * x)) + np.exp(-a * x) * (C0 * np.cos(nu * x) + D0 * np.sin(nu * x))

    base = loaded(t)
    base[N:] -= loaded(t[N:] - T)
    initial_velocity = omega_input * H.real - a * C0 + nu * D0
    assert abs(float(loaded(np.array([0.]))[0])) < 1e-12 and abs(initial_velocity) < 1e-12
    predictions = np.column_stack((base + scale * (modal[0] + modal[1]), base + scale * (modal[0] - modal[1])))
    errors = predictions - targets
    metrics = {}
    agreements = {}
    for j in range(2):
        name = f'u{j+1}'
        index = int(np.argmax(np.abs(errors[:, j])))
        maximum = float(abs(errors[index, j]))
        rms = float(np.sqrt(np.mean(errors[:, j] ** 2)))
        metrics[name] = {'maximum_abs_error': maximum, 'RMS_error': rms, 'maximum_error_index': index,
                         'signed_error_at_maximum': float(errors[index, j]), 'max_error_below_point01': maximum < .01}
        previous = prior['whole_window_error_metrics'][name]
        agreements[name + '_max'] = abs(maximum - previous['maximum_abs_error'])
        agreements[name + '_RMS'] = abs(rms - previous['RMS_error'])
    previous_points = list(csv.DictReader((old / 'four_fixed_point_replay.csv').open(encoding='utf-8', newline='')))
    snapshots = []
    for index, row in zip([0, N, 16529, steps], previous_points):
        assert int(row['node_index']) == index
        entry = {'node_index': index, 'time_float': float(t[index]), 'analytic_U': float(base[index]),
                 'u1_FFT_replay': float(predictions[index, 0]), 'u2_FFT_replay': float(predictions[index, 1]),
                 'u1_D_cache': float(targets[index, 0]), 'u2_D_cache': float(targets[index, 1])}
        for j in range(2):
            name = f'u{j+1}'
            agreement = float(predictions[index, j]) - float(row[name + '_D_replay'])
            entry[name + '_FFT_minus_R019'] = agreement
            agreements[f'{name}_point_{index}'] = abs(agreement)
        snapshots.append(entry)
    assert all(value < 1e-8 for value in agreements.values()), 'Preregistered independent agreement gate failed'
    assert time.perf_counter() - start < 300
    assert all(record(Path(item['path'])) == item for item in refs)
    result = {'at': datetime.now().astimezone().isoformat(), 'elapsed_seconds': time.perf_counter() - start,
              'status': 'finite_same_source_force_replay_independent_algorithm_candidate',
              'source_refs_checked': refs, 'method': 'Analytic complex-pole FOH displacement lag kernels and zero-padded FFT linear convolution; no R019 state recursion or author-code import.',
              'N': N, 'nodes_compared': steps + 1, 'window_end_float': float(t[-1]), 'kernel_checks': kernel_checks,
              'metrics_against_original_D_cache': metrics, 'agreement_differences': agreements,
              'fixed_agreement_gate': 1e-8, 'agreement_gate_passed': True, 'four_fixed_points': snapshots,
              'last_known_force': float(force[-1]), 'unknown_force_after_window_not_extended': True,
              'limits': 'Known same-source PL force only. Ordinary float/FFT errors and exact-model-vs-rounded parameters, true force interpolation, original D error and continuous extrema unbounded. No new-layout/input prediction, physical external validation or tail certificate.',
              'command': [sys.executable, '-X', 'utf8', str(Path(__file__).resolve())], 'exit_code': 0,
              'python': sys.version, 'numpy': np.__version__}
    (O / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    with (O / 'four_points.csv').open('w', encoding='utf-8', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(snapshots[0]))
        writer.writeheader()
        writer.writerows(snapshots)
    report = f'''# 给定力FOH重放的独立FFT有限复算

本轮用解析复根时延权重与零填充FFT线性卷积，复算同一冻结D力史的98305个节点，没有导入/运行R019递推、重解非线性ODE或改输入/布局。源NPZ实际SHA核过。

与R019报告的全窗max/RMS和四固定点预测比较，12项差最大为{max(agreements.values()):.12g}，全部小于预设1e−8。u1/u2对原D缓存的maxerror分别为{metrics['u1']['maximum_abs_error']:.12g}、{metrics['u2']['maximum_abs_error']:.12g}；两个旧0.01诊断门均通过。详细结果见summary.json。

此为不同算法的有限实现一致性，不是独立物理实验。输入仍是同一D的既有器件力，不能用来证明新输入/新布局预测优势。未认证真力插值、原D精度、连续峰、精确参数全窗误差或未知6T外力尾。未保存大数组/图件，没有操作ETABS或原工程Excel。本小包待独审，原冻结结果不改。
'''
    (O / 'report.md').write_text(report, encoding='utf-8', newline='\n')
    print(json.dumps({'elapsed_seconds': result['elapsed_seconds'], 'metrics': metrics, 'maximum_agreement_difference': max(agreements.values()), 'passed': True}))


if __name__ == '__main__':
    main()
