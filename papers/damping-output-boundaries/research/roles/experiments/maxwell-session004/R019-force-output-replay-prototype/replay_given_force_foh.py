"""Known same-source force conditioned FOH replay; no nonlinear ODE or forecast."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time,traceback
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='22278c170d95b36af6c5d63b6bd9c4921e6cc43cbd6ddd747d964405e6b91b9c'
CONTEXT={}
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    start=time.perf_counter();assert not (H/'summary_r019.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs']
    assert all(sha(x['path'])==x['sha256'] for x in refs.values())
    N=p['N'];indices=p['fixed_indices'];assert N==16384 and indices==[0,N,16529,6*N]
    s2=math.sqrt(2);s3=math.sqrt(3);scale=1/s2;T=20*math.pi/s2;h=T/N
    coefficient_rows=[{'source_type':'synthetic_exact_bare_reference_operator','mode':'+','omega':1.,'zeta':.05,'modal_mass':1.,'beta':scale,'gamma_u1':scale,'gamma_u2':scale},
        {'source_type':'synthetic_exact_bare_reference_operator','mode':'-','omega':s3,'zeta':.05,'modal_mass':1.,'beta':-scale,'gamma_u1':scale,'gamma_u2':-scale}]
    write('synthetic_modal_port_target_coefficients.csv',coefficient_rows)
    weights=[];algebra=[];b=np.array([0.,1.]);I2=np.eye(2)
    for mode in coefficient_rows:
        w=mode['omega'];k=w*w;cm=2*mode['zeta']*w;decay=cm/2;wd=math.sqrt(k-decay*decay)
        A=np.array([[0.,1.],[-k,-cm]]);Ai=np.array([[-cm/k,-1/k],[1.,0.]])
        cs=math.cos(wd*h);sn=math.sin(wd*h)/wd;ex=math.exp(-decay*h)
        E=ex*np.array([[cs+decay*sn,sn],[-k*sn,cs-decay*sn]])
        J0=Ai@(E-I2)@b;J1=Ai@Ai@(E-I2-A*h)@b/h;W0=J0-J1;W1=J1
        # Independently derive constant/ramp convolution weights by matrix powers.
        Ak=I2.copy();Eref=np.zeros((2,2));J0ref=np.zeros(2);J1ref=np.zeros(2)
        for degree in range(13):
            Eref+=Ak*h**degree/math.factorial(degree)
            J0ref+=(Ak@b)*h**(degree+1)/math.factorial(degree+1)
            J1ref+=(Ak@b)*h**(degree+1)/math.factorial(degree+2)
            Ak=Ak@A
        residuals={'A_Ainv_minus_I':float(np.max(abs(A@Ai-I2))),
            'E_closed_minus_series13':float(np.max(abs(E-Eref))),'J0_closed_minus_series13':float(max(abs(J0-J0ref))),
            'J1_closed_minus_series13':float(max(abs(J1-J1ref))),'A_J0_minus_EminusI_b':float(max(abs(A@J0-(E-I2)@b))),
            'A_J1_minus_J0overh_minus_b':float(max(abs(A@J1-(J0/h-b))))}
        tol=1e-11*max(1.,float(np.max(abs(E))),float(max(abs(J0))),float(max(abs(J1))))
        check={'mode':mode['mode'],'A':A.tolist(),'Ainv':Ai.tolist(),'E':E.tolist(),'J0':J0.tolist(),'J1':J1.tolist(),
            'W_left':W0.tolist(),'W_right':W1.tolist(),'matrix_power_series_reference_terms':13,'residuals':residuals,'arithmetic_tolerance':tol,'passed':all(x<=tol for x in residuals.values())}
        algebra.append(check);weights.append((E,W0,W1))
    (H/'foh_weight_algebra_checks.json').write_text(json.dumps({'scope':'Finite floating algebra/series check, not a rigorous matrix exponential certificate','checks':algebra},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert all(x['passed'] for x in algebra),'FOH algebra gate failed; preserve and stop'
    with np.load(refs['local_cache']['path'],allow_pickle=False) as z:
        a=z['D_N16384'];assert a.shape==(98305,9) and a.dtype==np.float64
        t=a[:,0].copy();target=a[:,1:3].copy();F=a[:,5].copy()
    assert np.isfinite(np.c_[t,target,F]).all() and np.array_equal(t,np.arange(len(t))*h)
    # R020 analytic zero-initial response; never read the U cache or solve U.
    nu=math.sqrt(399/400);aa=1/20;Ap=-50/51;Bp=-5*s2/51;C0=5*s2/51;D0=67*s2/(68*nu)
    def xh(x):return math.exp(-aa*x)*(C0*math.cos(nu*x)+D0*math.sin(nu*x))
    def xp(x):return Ap*math.sin(s2*x)+Bp*math.cos(s2*x)
    def baseline(x,index):return xp(x)+xh(x) if index<=N else xh(x)-xh(x-T)
    raw_initial_u=xp(0)+xh(0);raw_initial_v=Ap*s2-aa*C0+nu*D0
    cutoff_continuity=(xp(T)+xh(T))-(xh(T)-xh(0))
    analytic_qa={'R020_coefficients':{'A':Ap,'B':Bp,'C0':C0,'D0':D0,'decay':aa,'nu':nu},'initial_u_float':raw_initial_u,
        'initial_v_float':raw_initial_v,'cutoff_formula_continuity_difference_float':cutoff_continuity,'no_U_ODE_or_cache_used':True}
    assert max(abs(raw_initial_u),abs(raw_initial_v),abs(cutoff_continuity))<1e-11
    states=[np.zeros(2),np.zeros(2)];sums=[0.,0.];comp=[0.,0.];max_error=[-1.,-1.];max_witness=[None,None];snapshots=[]
    for n in range(len(t)):
        if n%16384==0:
            CONTEXT.update({'node':n,'elapsed_seconds':time.perf_counter()-start})
            if time.perf_counter()-start>480:raise TimeoutError('Frozen runtime480s exceeded')
        base=baseline(float(t[n]),n);qplus=float(states[0][0]);qminus=float(states[1][0])
        du1p=scale*qplus;du1m=scale*qminus;du2p=scale*qplus;du2m=-scale*qminus
        pred=[base+du1p+du1m,base+du2p+du2m];err=[pred[0]-float(target[n,0]),pred[1]-float(target[n,1])]
        if not all(math.isfinite(x) for x in pred+err):raise ArithmeticError('Nonfinite replay output')
        for j in range(2):
            magnitude=abs(err[j])
            if magnitude>max_error[j]:
                max_error[j]=magnitude;max_witness[j]={'node':n,'time_original_label':float(t[n]),'signed_error':err[j],
                    'prediction':pred[j],'cached_D':float(target[n,j])}
            squared=err[j]*err[j]-comp[j];new=sums[j]+squared;comp[j]=(new-sums[j])-squared;sums[j]=new
        if n in indices:
            snapshots.append({'node_index':n,'time_original_label':float(t[n]),'F_given_signed':float(F[n]),'analytic_U_scalar':base,
                'qdiff_plus':qplus,'qdiff_minus':qminus,'u1_device_delta_plus':du1p,'u1_device_delta_minus':du1m,
                'u2_device_delta_plus':du2p,'u2_device_delta_minus':du2m,'u1_D_replay':pred[0],'u2_D_replay':pred[1],
                'u1_D_cache':float(target[n,0]),'u2_D_cache':float(target[n,1]),'u1_error_pred_minus_cache':err[0],'u2_error_pred_minus_cache':err[1]})
        if n==len(t)-1:break
        for j,mode in enumerate(coefficient_rows):
            E,W0,W1=weights[j];p0=-mode['beta']*float(F[n])/mode['modal_mass'];p1=-mode['beta']*float(F[n+1])/mode['modal_mass']
            states[j]=E@states[j]+W0*p0+W1*p1
    error_metrics={f'u{j+1}':{'maximum_abs_error':max_error[j],'RMS_error':math.sqrt(sums[j]/len(t)),
        'maximum_error_witness':max_witness[j],'fixed_diagnostic_threshold':.01,'max_error_below_point01':max_error[j]<.01} for j in range(2)}
    write('four_fixed_point_replay.csv',snapshots)
    checks={'two_bare_modes_FOH_algebra_gate_passed':all(x['passed'] for x in algebra),'only_given_D_force_targets_used':True,
        'analytic_U_R020_no_new_U_solution':True,'98305_nodes_original_full_window_compared':len(t)==98305,'four_fixed_snapshots_only':len(snapshots)==4,
        'stored_force_retained_after_input_stop_no_unknown_tail_fill':True,'all_source_and_protocol_SHA_unchanged':all(sha(x['path'])==x['sha256'] for x in refs.values()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below480seconds':time.perf_counter()-start<480};assert all(checks.values())
    out={'evidence_id':'M-EXP-R019','status':'same_source_given_force_FOH_float_replay_candidate','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-start,'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'source_refs':refs,
        'N':N,'T':T,'dt':h,'window_end':float(t[-1]),'modal_coefficients':coefficient_rows,'FOH_algebra_checks':algebra,'analytic_U_float_QA':analytic_qa,
        'whole_window_error_metrics':error_metrics,'both_fixed_diagnostic_gates_passed':all(x['max_error_below_point01'] for x in error_metrics.values()),
        'force_window_scope':{'last_recorded_F':float(F[-1]),'max_abs_F_after_external_input_stop':float(max(abs(F[N:]))),
            'recorded_force_after_T_not_zeroed':True,'no_output_beyond6T_or_unknown_F_extension':True},
        'checks':checks,'no_nonlinear_ODE_or_fullarray_output':True}
    lines=['# M-EXP-R019：给定同源器件力的FOH条件重放原型','',
        '状态：candidate。输入是同源D记录已有力史，结果只是经典裸主体线性卷积接口的有限双精度实现检查，不是新输入/新布局预测、独立物理外验、新方法或有向数值证书。R022接口的独审边界继续保留。', '',
        '参考算子取本精确合成M/K/C的两个完整裸模态，系数小CSV标synthetic；没有从实际FNA频率、参与质量猜端口/目标投影。差模态的输入为p=−beta F/m，目标分别用gamma投影。两模态均先核闭式2×2 E/J0/J1与固定13项矩阵幂积分级数及A*J0、A*J1身份，实际余差见JSON。这一有限浮点核查不等于严格矩阵指数证明。', '',
        '无装置基线只用R020的解析xp+xh；停载后用xh(t)−xh(t−T)，没有读取U缓存或新求解U。F按每段线性插值，用E*x+(J0−J1)*p0+J1*p1递推差状态；完整0..6T原F保留，外部正弦停止后没有把器件力清零，也不延伸未知6T后力史。', '',
        '## 全窗误差与固定诊断门', '', '| 输出 | 最大绝对误差 | RMS误差 | 最大误差节点/时间 | 有符号误差 | maxerror<0.01 |', '|---|---:|---:|---|---:|---|']
    for name,m in error_metrics.items():
        w=m['maximum_error_witness'];lines.append(f"| {name} | {m['maximum_abs_error']:.12g} | {m['RMS_error']:.12g} | {w['node']} / {w['time_original_label']:.12g} | {w['signed_error']:+.12g} | {m['max_error_below_point01']} |")
    lines+=['', '误差为重放减原D缓存，遍历全部98305节点；两个0.01门在读取结果前固定，无论成败均保留。误差混合了F采样插值、浮点递推和原D轨迹误差，不能解释为独立物理预测优势或严格误差上界。', '',
        '## 固定四点同刻结果', '', '| 节点 | 解析U | u1器件差贡献(+/−) | u1重放/缓存 | u2器件差贡献(+/−) | u2重放/缓存 |', '|---|---:|---|---|---|---|']
    for x in snapshots:lines.append(f"| {x['node_index']} | {x['analytic_U_scalar']:.10g} | {x['u1_device_delta_plus']:+.10g} / {x['u1_device_delta_minus']:+.10g} | {x['u1_D_replay']:.10g} / {x['u1_D_cache']:.10g} | {x['u2_device_delta_plus']:+.10g} / {x['u2_device_delta_minus']:+.10g} | {x['u2_D_replay']:.10g} / {x['u2_D_cache']:.10g} |")
    lines+=['', f"窗口最后一个已知F={float(F[-1]):.12g}，仍按记录使用；不把它假设成零或承诺未知尾。没有保存新的大时程、作图、非线性ODE、参数/频率/阈值搜索、原始工程表或Git修改。源数组只读，完成冻结交主控独审。"]
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={n:sha(H/n) for n in ['synthetic_modal_port_target_coefficients.csv','foh_weight_algebra_checks.json','four_fixed_point_replay.csv','report.md']}
    (H/'summary_r019.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'run_record_r019.json').write_text(json.dumps({'actual_command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,
        'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],'python':sys.version,'numpy':np.__version__,
        'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r019.json'),'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','whole_window_error_metrics','both_fixed_diagnostic_gates_passed','force_window_scope','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        failure={'evidence_id':'M-EXP-R019','status':'failed_fixed_FOH_prototype_no_tuning','failed_utc':datetime.now(timezone.utc).isoformat(),'error':repr(exc),'context':CONTEXT,'traceback':traceback.format_exc()}
        with (H/'failure_r019.json').open('x',encoding='utf-8') as f:json.dump(failure,f,ensure_ascii=False,indent=2)
        raise
