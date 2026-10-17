"""Frozen input-only backward Euler synthetic D. Reference opens only after both predictions freeze."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json, math, sys, time, traceback
import numpy as np

H = Path(__file__).resolve().parent
CONTEXT = {}
EVENTS = []

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def save(name, value):
    path = H / name
    assert not path.exists(), 'Refuse to overwrite frozen output: ' + name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def csvsave(name, rows):
    assert not (H / name).exists()
    with (H / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def event(name, **kwargs):
    EVENTS.append({'event': name, 'utc': timestamp(), 'monotonic_ns': time.monotonic_ns(), **kwargs})

def main():
    started = time.perf_counter()
    p = json.loads((H / 'protocol.json').read_text(encoding='utf-8'))
    frozen = json.loads((H / 'pre_run_freeze.json').read_text(encoding='utf-8'))
    for entry in frozen['files']:
        assert sha(entry['path']) == entry['sha256']
    assert p['N'] == [8192, 16384] and p['max_bisections'] == 60 and p['root_relative_gate'] == 1e-11
    assert p['fine_displacement_maxerror_gate'] == .1
    deadline = datetime.fromisoformat(p['deadline'])
    event('code_and_protocol_verified_before_predictions', code_sha256=sha(__file__), protocol_sha256=sha(H / 'protocol.json'))
    sq2, sq3 = math.sqrt(2), math.sqrt(3)
    T = 20 * math.pi / sq2
    cd, co = (1 + sq3) / 20, (1 - sq3) / 20
    kappa, c, q = 8., 10., 10. / 3.
    def g(F):
        return math.copysign((abs(F) / c) ** q, F)
    def energy(u1, u2, v1, v2, F):
        return u1*u1 + u2*u2 - u1*u2 + .5*(v1*v1 + v2*v2) + F*F/(2*kappa)
    def rootsolve(a, b, h):
        endpoint = b/a
        lo, hi = (0., endpoint) if b >= 0 else (endpoint, 0.)
        tol = 1e-11 * max(1., abs(b))
        def residual(x): return a*x + h*g(x) - b
        for iteration in range(1, 61):
            mid = (lo + hi)/2
            if mid == lo or mid == hi:
                fl, fh = residual(lo), residual(hi)
                F, r = (lo, fl) if abs(fl) <= abs(fh) else (hi, fh)
                return F, r, tol, iteration, True, min(0., endpoint) <= F <= max(0., endpoint)
            r = residual(mid)
            if abs(r) <= tol:
                return mid, r, tol, iteration, False, min(0., endpoint) <= mid <= max(0., endpoint)
            if r > 0: hi = mid
            else: lo = mid
        return mid, r, tol, 60, False, min(0., endpoint) <= mid <= max(0., endpoint)

    runs, summaries, snapshots = {}, [], []
    for N in [8192, 16384]:
        run_start = time.perf_counter(); h = T/N
        ad, ao = 1 + h*cd + 2*h*h, h*co - h*h
        determinant = ad*ad - ao*ao
        d, o = ad/determinant, -ao/determinant
        S = d; a = 1/kappa + h*h*S
        assert S > 0 and a > 0
        trajectory = np.zeros((6*N+1, 6), dtype='<f8')
        trajectory[:, 0] = np.arange(6*N+1)*h
        u1 = u2 = v1 = v2 = F = 0.
        Eold = 0.; totals = [0.]*6
        max_root = max_root_scaled = max_step = max_cumulative = max_body = max_const = max_identity = 0.
        min_device = min_background = min_numerical = math.inf
        iter_max = iter_total = stagnations = 0
        indices = [0, N, 6*N] if N == 8192 else [0, N, 16529, 6*N]
        def snapshot(n, root_residual):
            snapshots.append({'N': N, 'node': n, 'time_synthetic': n*h, 'u1': u1, 'u2': u2, 'v1': v1, 'v2': v2, 'F': F,
                              'E': energy(u1,u2,v1,v2,F), 'W_input': totals[0], 'D_background': totals[1], 'D_device': totals[2],
                              'D_numerical_u': totals[3], 'D_numerical_v': totals[4], 'D_numerical_F': totals[5],
                              'actual_cumulative_balance': energy(u1,u2,v1,v2,F)+sum(totals[1:])-totals[0], 'root_residual': root_residual})
        snapshot(0, 0.)
        for n in range(1, 6*N+1):
            if n % 8192 == 0:
                CONTEXT.update(N=N, step=n, elapsed_seconds=time.perf_counter()-started)
                if datetime.now(timezone.utc) > deadline: raise TimeoutError('Task 10-minute deadline reached')
            f = math.sin(sq2*(n*h)) if n < N else 0.
            r1 = v1 + h*(f - 2*u1 + u2)
            r2 = v2 + h*(f + u1 - 2*u2)
            z1, z2 = d*r1 + o*r2, o*r1 + d*r2
            b = F/kappa + h*z2
            Fnew, root_r, tolerance, iterations, stagnant, in_bracket = rootsolve(a, b, h)
            CONTEXT.update(N=N, step=n, root_residual=root_r, root_tolerance=tolerance)
            if not in_bracket or abs(root_r) > tolerance:
                save('root_failure.json', {**CONTEXT, 'F': Fnew, 'a': a, 'b': b, 'iterations': iterations, 'stagnant': stagnant})
                raise ArithmeticError('Fixed root gate failed; no threshold adjustment')
            v1n, v2n = z1 - h*o*Fnew, z2 - h*d*Fnew
            u1n, u2n = u1 + h*v1n, u2 + h*v2n
            du1, du2, dv1, dv2, dF = u1n-u1, u2n-u2, v1n-v1, v2n-v2, Fnew-F
            gn = g(Fnew)
            increments = [h*f*(v1n+v2n), h*(cd*(v1n*v1n+v2n*v2n)+2*co*v1n*v2n), h*Fnew*gn,
                          du1*du1+du2*du2-du1*du2, .5*(dv1*dv1+dv2*dv2), .5*dF*dF/kappa]
            Enew = energy(u1n,u2n,v1n,v2n,Fnew)
            step_balance = Enew-Eold + sum(increments[1:]) - increments[0]
            body1 = dv1 + h*(cd*v1n+co*v2n+2*u1n-u2n-f)
            body2 = dv2 + h*(co*v1n+cd*v2n-u1n+2*u2n+Fnew-f)
            constitutive = dF/kappa + h*gn - du2
            identity_defect = step_balance - (v1n*body1 + v2n*body2 + Fnew*constitutive)
            for j, value in enumerate(increments): totals[j] += value
            cumulative = Enew + sum(totals[1:]) - totals[0]
            max_root = max(max_root, abs(root_r)); max_root_scaled = max(max_root_scaled, abs(root_r)/max(1.,abs(b)))
            max_step = max(max_step, abs(step_balance)); max_cumulative = max(max_cumulative, abs(cumulative))
            max_body = max(max_body, abs(body1), abs(body2)); max_const = max(max_const, abs(constitutive))
            max_identity = max(max_identity, abs(identity_defect))
            min_device = min(min_device,increments[2]); min_background = min(min_background,increments[1]); min_numerical = min(min_numerical,sum(increments[3:]))
            iter_max = max(iter_max, iterations); iter_total += iterations; stagnations += stagnant
            u1,u2,v1,v2,F,Eold = u1n,u2n,v1n,v2n,Fnew,Enew
            trajectory[n,1:] = u1,u2,v1,v2,F
            if n in indices: snapshot(n, root_r)
        assert np.isfinite(trajectory).all()
        peaks = {}
        for name, col in [('u1',1),('u2',2),('F',5)]:
            peaks[name] = {}
            for window, begin in [('whole_window',0),('strictly_after_T',N+1)]:
                index = begin + int(np.argmax(abs(trajectory[begin:,col])))
                peaks[name][window] = {'sampled_abs_peak': abs(float(trajectory[index,col])), 'signed_value': float(trajectory[index,col]), 'node': index, 'time': index*h}
        trajectory_sha = hashlib.sha256(trajectory.tobytes(order='C')).hexdigest()
        summary = {'N':N,'h':h,'steps':6*N,'nodes':6*N+1,'elapsed_seconds':time.perf_counter()-run_start,
                   'trajectory_columns':['t','u1','u2','v1','v2','F'],'trajectory_dtype':'little-endian float64 C order',
                   'memory_trajectory_sha256':trajectory_sha,'trajectory_saved_to_disk':False,
                   'A_inverse':[[d,o],[o,d]],'S_h':S,'a':a,
                   'root_max_abs_residual':max_root,'root_max_scaled_residual':max_root_scaled,'root_gate':1e-11,'root_gate_pass':max_root_scaled<=1e-11,
                   'root_max_iterations':iter_max,'root_mean_iterations':iter_total/(6*N),'root_stagnations':stagnations,'all_roots_in_theoretical_bracket':True,
                   'energy_terminal':Eold,'work_input':totals[0],'physical_background_dissipation':totals[1],'physical_device_dissipation':totals[2],
                   'numerical_dissipation_u':totals[3],'numerical_dissipation_v':totals[4],'numerical_dissipation_F':totals[5],
                   'actual_terminal_balance':Eold+sum(totals[1:])-totals[0], 'max_abs_actual_step_balance':max_step,'max_abs_actual_cumulative_balance':max_cumulative,
                   'max_abs_body_increment_residual':max_body,'max_abs_constitutive_increment_residual':max_const,'max_abs_energy_identity_vs_equation_defects':max_identity,
                   'minimum_step_background_dissipation':min_background,'minimum_step_device_dissipation':min_device,'minimum_step_numerical_dissipation':min_numerical,
                   'sampled_peaks':peaks,'fixed_indices':indices,'coarse_J_not_on_grid_no_interpolation':N==8192}
        summaries.append(summary); runs[N] = trajectory
        event('prediction_complete',N=N,trajectory_sha256=trajectory_sha)
    save('prediction_summary.json', {'status':'candidate_before_reference_access','predictions':summaries,'reference_accessed':False})
    csvsave('prediction_fixed_snapshots.csv',snapshots)
    save('prediction_freeze.json', {'utc':timestamp(),'code_sha256':sha(__file__),'protocol_sha256':sha(H/'protocol.json'),
                                   'prediction_summary_sha256':sha(H/'prediction_summary.json'),'fixed_snapshots_sha256':sha(H/'prediction_fixed_snapshots.csv'),
                                   'memory_trajectory_sha256':{str(s['N']):s['memory_trajectory_sha256'] for s in summaries},'both_predictions_complete':True,'reference_not_yet_accessed':True})
    pred_freeze = json.loads((H/'prediction_freeze.json').read_text(encoding='utf-8'))
    assert pred_freeze['both_predictions_complete'] and len(runs)==2
    assert pred_freeze['prediction_summary_sha256']==sha(H/'prediction_summary.json')
    assert pred_freeze['fixed_snapshots_sha256']==sha(H/'prediction_fixed_snapshots.csv')
    event('both_predictions_and_hashes_on_disk_before_reference',prediction_freeze_sha256=sha(H/'prediction_freeze.json'))
    event('reference_hash_access_start')
    reference = Path(p['reference_path'])
    actual_reference_sha = sha(reference)
    assert actual_reference_sha == p['reference_sha256']
    event('reference_hash_verified_np_load_next',sha256=actual_reference_sha)
    # This is the only np.load call; no reference state/force exists before the disk gate above.
    with np.load(reference, allow_pickle=False) as z:
        ref = z['D_N16384']
    event('D_N16384_reference_read_complete')
    assert ref.shape==(98305,9) and ref.dtype==np.float64 and np.isfinite(ref).all()
    assert np.array_equal(ref[:,0],runs[16384][:,0])
    assert np.array_equal(ref[::2,0],runs[8192][:,0])
    def errors(pred, truth):
        output={}
        for name, pc, rc in [('u1',1,1),('u2',2,2),('F',5,5)]:
            err=pred[:,pc]-truth[:,rc]; index=int(np.argmax(abs(err)))
            output[name]={'max_abs_error':float(max(abs(err))),'RMS_error':float(np.sqrt(np.mean(err*err))),
                          'max_error_witness_node_in_comparison':index,'time':float(pred[index,0]),'signed_error':float(err[index])}
        return output
    comparison={'coarse_vs_reference_on_49153_common_nodes':errors(runs[8192],ref[::2]),
                'fine_vs_reference_on_49153_common_nodes':errors(runs[16384][::2],ref[::2]),
                'fine_vs_reference_on_98305_all_nodes':errors(runs[16384],ref),
                'coarse_vs_fine_prediction_on_49153_common_nodes':errors(runs[8192],runs[16384][::2])}
    improvement={name:{metric:comparison['fine_vs_reference_on_49153_common_nodes'][name][metric]<comparison['coarse_vs_reference_on_49153_common_nodes'][name][metric] for metric in ['max_abs_error','RMS_error']} for name in ['u1','u2','F']}
    gates={name:comparison['fine_vs_reference_on_98305_all_nodes'][name]['max_abs_error']<.1 for name in ['u1','u2']}
    fixed_comparison=[]
    for snap in snapshots:
        n=snap['node'];ri=n*2 if snap['N']==8192 else n
        fixed_comparison.append({**snap,'reference_index':ri,'reference_u1':float(ref[ri,1]),'reference_u2':float(ref[ri,2]),'reference_F':float(ref[ri,5]),
                                 'u1_error':snap['u1']-float(ref[ri,1]),'u2_error':snap['u2']-float(ref[ri,2]),'F_error':snap['F']-float(ref[ri,5])})
    csvsave('comparison_fixed_snapshots.csv',fixed_comparison)
    assert sha(reference)==actual_reference_sha
    for entry in frozen['files']: assert sha(entry['path'])==entry['sha256']
    event('comparison_complete')
    save('reference_read_order.json',{'events':EVENTS,'gate':'Both model/input-only predictions and hashes persisted before any reference hash or np.load','not_a_blind_test':True})
    summary={'task':'R022-forward-BE-synthetic','status':'candidate_math_author_and_independent_review_pending',
             'finished_utc':timestamp(),'elapsed_seconds':time.perf_counter()-started,'predictions':summaries,'comparison':comparison,
             'coarse_to_fine_improvement_on_common_grid':improvement,'fine_u1_u2_maxerror_below_point1':gates,
             'reference_sha256':actual_reference_sha,'reference_member_read':'D_N16384 only',
             'J_fine_index':16529,'J_coarse_index':None,'J_coarse_grid_coordinate':8264.5,
             'reference_used_in_prediction':False,'source_code_protocol_unchanged':True,'large_trajectory_outputs_saved':False,
             'limits':'Same synthetic model numerical comparison; not blind, new method, physical external validation, rigorous convergence/order bound, continuous-peak or engineering certification'}
    save('summary.json',summary)
    lines=['# R022：仅模型与输入的 Backward Euler 合成前向检验','',
           '状态为 **candidate**，数学R026作者与独审尚待。两档从模型、规定外力和零初态闭环求F；预测摘要、7个固定快照及内存轨迹SHA先落盘，随后才读取原D_N16384比较。不是盲测或独立物理验证。','',
           '经典BE使用右端点外力，n=N起置理论零；单端口消元以理论括区间二分，最多60次，固定根残差门1e−11·max(1,|b|)。未将观测力、位移或速度用于递推或初始化。', '',
           '| N | 根最大归一残差 | 背景/器件物理耗散 | u/v/F数值耗散 | 实际终端余额 | 最大逐步余额 |','|---:|---:|---:|---:|---:|---:|']
    for s in summaries:
        lines.append(f"| {s['N']} | {s['root_max_scaled_residual']:.9g} | {s['physical_background_dissipation']:.9g} / {s['physical_device_dissipation']:.9g} | {s['numerical_dissipation_u']:.9g} / {s['numerical_dissipation_v']:.9g} / {s['numerical_dissipation_F']:.9g} | {s['actual_terminal_balance']:+.9g} | {s['max_abs_actual_step_balance']:.9g} |")
    lines += ['', '余额按 E−E0+物理耗散+数值耗散−输入功直接计算，未裁剪为零；逐步余额亦与动量/本构浮点残差所致缺陷独立核对。余额小不表示连续解误差小。', '', '| 比较网格 | 输出 | maxabs | RMS |','|---|---|---:|---:|']
    for label, group in comparison.items():
        for name, m in group.items(): lines.append(f"| {label} | {name} | {m['max_abs_error']:.10g} | {m['RMS_error']:.10g} |")
    lines += ['', f'细档全网格固定诊断门 maxerror<0.1：u1={gates["u1"]}，u2={gates["u2"]}。门槛保持原值；全部成败结果保留。共同粗网格的粗到细改善逐项见summary，不据两档推断严格收敛阶。', '',
              '每档全窗采样峰及严格t>T后的采样峰、峰时和符号保留于prediction_summary。细档J=16529真实在网格；其粗网格坐标为8264.5，粗档仅保存0/N/6N，未伪造同刻J或插值快照。', '',
              '运行前协议/代码指纹见pre_run_freeze，预测先后读取门见prediction_freeze与reference_read_order。仅保存小代码、JSON、7行预测与比较快照和执行记录；内存轨迹只存SHA，没有另存NPZ、大CSV或图。未扫描参数、添加第三步长、操作ETABS或读取真实工程数据。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return summary

if __name__=='__main__':
    began=timestamp(); code=0
    try:
        result=main()
        print(json.dumps({'status':result['status'],'fine_gate':result['fine_u1_u2_maxerror_below_point1'],'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=True))
    except Exception as exc:
        code=1
        save('failure.json',{'utc':timestamp(),'exception':str(exc),'context':CONTEXT,'traceback':traceback.format_exc(),'events':EVENTS,'status':'candidate_failed_preserved_no_retuning'})
        print(traceback.format_exc())
    save('run_record.json',{'started_utc':began,'finished_utc':timestamp(),'exit_code':code,'python':sys.version,'numpy':np.__version__,'command':[sys.executable,str(Path(__file__).resolve())],'code_sha256':sha(__file__)})
    files=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(H.iterdir()) if p.is_file() and p.name!='delivery_manifest.json']
    save('delivery_manifest.json',{'frozen_utc':timestamp(),'status':'candidate','files':files})
    sys.exit(code)
