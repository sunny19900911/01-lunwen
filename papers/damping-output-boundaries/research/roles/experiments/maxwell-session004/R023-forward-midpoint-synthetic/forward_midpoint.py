"""Fixed C027 D input-only implicit midpoint; small outputs and delayed reference gate."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json, math, sys, time, traceback
import numpy as np

H = Path(__file__).resolve().parent
EVENTS, CONTEXT = [], {}

def stamp(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name, value):
    assert not (H/name).exists(), 'Refuse frozen output overwrite: '+name
    (H/name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
def csvsave(name, rows):
    assert not (H/name).exists()
    with (H/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def event(name, **kwargs): EVENTS.append({'event':name,'utc':stamp(),'monotonic_ns':time.monotonic_ns(),**kwargs})

def main():
    start=time.perf_counter()
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'))
    freeze=json.loads((H/'pre_run_freeze.json').read_text(encoding='utf-8'))
    for f in freeze['files']: assert sha(f['path'])==f['sha256']
    assert p['N']==[8192,16384] and p['root_gate']==1e-11 and p['max_bisections']==60 and p['fine_displacement_gate']==.1
    deadline=datetime.fromisoformat(p['deadline'])
    event('code_protocol_sources_verified_before_predictions',code_sha256=sha(__file__),protocol_sha256=sha(H/'protocol.json'))
    sqrt2,sqrt3=math.sqrt(2),math.sqrt(3); T=20*math.pi/sqrt2
    cd,co=(1+sqrt3)/20,(1-sqrt3)/20; kappa,c,q=8.,10.,10./3.
    def g(F): return math.copysign((abs(F)/c)**q,F)
    def E(u1,u2,v1,v2,F): return u1*u1+u2*u2-u1*u2+.5*(v1*v1+v2*v2)+F*F/(2*kappa)
    def solve(ar,b,half):
        end=b/ar; lo,hi=sorted((0.,end)); tol=1e-11*max(1.,abs(b))
        def residual(x):return ar*x+half*g(x)-b
        for it in range(1,61):
            mid=(lo+hi)/2
            if mid==lo or mid==hi:
                rl,rh=residual(lo),residual(hi)
                x,r=(lo,rl) if abs(rl)<=abs(rh) else (hi,rh)
                return x,r,tol,it,True,min(0.,end)<=x<=max(0.,end)
            r=residual(mid)
            if abs(r)<=tol:return mid,r,tol,it,False,min(0.,end)<=mid<=max(0.,end)
            if r>0:hi=mid
            else:lo=mid
        return mid,r,tol,60,False,min(0.,end)<=mid<=max(0.,end)

    names=['r_u1_increment','r_u2_increment','r_p1_increment','r_p2_increment','r_F_compliance_increment']
    runs,summaries,snapshots,blocks=[],[],[],[]
    memory_runs={}
    for N in [8192,16384]:
        began=time.perf_counter(); h=T/N; half=h/2
        ad,ao=1+half*cd+2*half*half,half*co-half*half
        det=ad*ad-ao*ao; d,o=ad/det,-ao/det; S=d; ar=1/kappa+half*half*S
        assert S>0 and ar>0
        z=np.zeros((6*N+1,6),dtype='<f8');z[:,0]=np.arange(6*N+1)*h
        u1=u2=v1=v2=F=Eold=0.;totals=[0.]*3;work_sums=[0.]*3;abs_work_sums=[0.]*3
        residuals={name:{'max_abs':0.,'signed_at_max':0.,'right_node_at_max':0,'nonzero_count':0} for name in names}
        max_root=max_scaled=max_step=max_balance=max_identity=max_root_to_const=max_mid_consistency=0.
        max_work=[0.]*3;iterations_total=iterations_max=stagnations=0
        min_bg=min_dev=math.inf; block_max=[0.]*5; block_root=block_balance=0.;block_works=[0.]*3
        indices=[0,N,6*N] if N==8192 else [0,N,16529,6*N]
        def snapshot(n,root_res):
            snapshots.append({'N':N,'node':n,'time':n*h,'u1':u1,'u2':u2,'v1':v1,'v2':v2,'F':F,'E':E(u1,u2,v1,v2,F),
                              'input_work':totals[0],'physical_background_dissipation':totals[1],'physical_device_dissipation':totals[2],
                              'actual_cumulative_balance':E(u1,u2,v1,v2,F)+totals[1]+totals[2]-totals[0],
                              'kinematic_residual_work_sum':work_sums[0],'momentum_residual_work_sum':work_sums[1],'constitutive_residual_work_sum':work_sums[2],
                              'scalar_root_residual':root_res})
        snapshot(0,0.)
        for n in range(1,6*N+1):
            if n%8192==0:
                CONTEXT.update(N=N,right_node=n,elapsed_seconds=time.perf_counter()-start)
                if datetime.now(timezone.utc)>deadline:raise TimeoutError('Fixed 10-minute deadline reached')
            forcing=math.sin(sqrt2*((n-.5)*h)) if n<=N else 0.
            r1=v1+half*(forcing-2*u1+u2);r2=v2+half*(forcing+u1-2*u2)
            z1,z2=d*r1+o*r2,o*r1+d*r2; b=F/kappa+half*z2
            Fmid,root_r,tol,it,stagnant,in_bracket=solve(ar,b,half)
            if not in_bracket or abs(root_r)>tol:
                save('root_failure.json',{'N':N,'right_node':n,'a_F':ar,'b':b,'F_mid':Fmid,'residual':root_r,'tolerance':tol,'iterations':it,'stagnation':stagnant})
                raise ArithmeticError('Fixed scalar root gate failed; preserve and stop')
            vm1,vm2=z1-half*o*Fmid,z2-half*d*Fmid
            un1,un2=u1+h*vm1,u2+h*vm2;vn1,vn2=2*vm1-v1,2*vm2-v2;Fn=2*Fmid-F
            du1,du2,dv1,dv2,dF=un1-u1,un2-u2,vn1-v1,vn2-v2,Fn-F
            um1,um2=(u1+un1)/2,(u2+un2)/2; vb1,vb2=(v1+vn1)/2,(v2+vn2)/2;Fb=(F+Fn)/2
            Kmu1,Kmu2=2*um1-um2,-um1+2*um2
            ru1,ru2=du1-h*vb1,du2-h*vb2
            rp1=dv1+h*(cd*vb1+co*vb2+Kmu1-forcing)
            rp2=dv2+h*(co*vb1+cd*vb2+Kmu2+Fb-forcing)
            rF=dF/kappa-h*(vb2-g(Fb))
            rs=[ru1,ru2,rp1,rp2,rF]
            works=[Kmu1*ru1+Kmu2*ru2,vb1*rp1+vb2*rp2,Fb*rF]
            W=h*(vb1+vb2)*forcing;Db=h*(cd*(vb1*vb1+vb2*vb2)+2*co*vb1*vb2);Dd=h*Fb*g(Fb)
            Enew=E(un1,un2,vn1,vn2,Fn); step_balance=Enew-Eold+Db+Dd-W
            for j,value in enumerate([W,Db,Dd]):totals[j]+=value
            for j,value in enumerate(works):
                work_sums[j]+=value;abs_work_sums[j]+=abs(value);max_work[j]=max(max_work[j],abs(value));block_works[j]+=value
            balance=Enew+totals[1]+totals[2]-totals[0]
            for j,(name,value) in enumerate(zip(names,rs)):
                s=residuals[name];s['nonzero_count']+=value!=0
                if abs(value)>s['max_abs']:s.update(max_abs=abs(value),signed_at_max=value,right_node_at_max=n)
                block_max[j]=max(block_max[j],abs(value))
            max_root=max(max_root,abs(root_r));max_scaled=max(max_scaled,abs(root_r)/max(1.,abs(b)))
            max_step=max(max_step,abs(step_balance));max_balance=max(max_balance,abs(balance));max_identity=max(max_identity,abs(step_balance-sum(works)))
            max_root_to_const=max(max_root_to_const,abs(rF/2-root_r))
            max_mid_consistency=max(max_mid_consistency,abs(vb1-vm1),abs(vb2-vm2),abs(Fb-Fmid))
            block_root=max(block_root,abs(root_r));block_balance=max(block_balance,abs(balance))
            iterations_max=max(iterations_max,it);iterations_total+=it;stagnations+=stagnant;min_bg=min(min_bg,Db);min_dev=min(min_dev,Dd)
            u1,u2,v1,v2,F,Eold=un1,un2,vn1,vn2,Fn,Enew;z[n,1:]=u1,u2,v1,v2,F
            if n in indices:snapshot(n,root_r)
            if n%N==0:
                blocks.append({'N':N,'block_T':n//N,**dict(zip(names,block_max)),'max_abs_scalar_root_residual':block_root,'max_abs_actual_cumulative_balance':block_balance,
                               'kinematic_residual_work_sum':block_works[0],'momentum_residual_work_sum':block_works[1],'constitutive_residual_work_sum':block_works[2]})
                block_max=[0.]*5;block_root=block_balance=0.;block_works=[0.]*3
        assert np.isfinite(z).all()
        peaks={}
        for name,col in [('u1',1),('u2',2),('F',5)]:
            peaks[name]={}
            for label,begin in [('whole_window',0),('strictly_after_T',N+1)]:
                j=begin+int(np.argmax(abs(z[begin:,col])));peaks[name][label]={'sampled_abs_peak':abs(float(z[j,col])),'signed_value':float(z[j,col]),'node':j,'time':j*h}
        trajectory_sha=hashlib.sha256(z.tobytes(order='C')).hexdigest()
        s={'N':N,'h':h,'steps':6*N,'nodes':6*N+1,'elapsed_seconds':time.perf_counter()-began,'a_half':half,'A_inverse':[[d,o],[o,d]],'S_h':S,'a_F':ar,
           'memory_trajectory_sha256':trajectory_sha,'trajectory_columns':['t','u1','u2','v1','v2','F'],'trajectory_dtype':'little-endian float64 C-order','trajectory_saved':False,
           'root_max_abs_residual':max_root,'root_max_scaled_residual':max_scaled,'root_gate_pass':max_scaled<=1e-11,'root_max_iterations':iterations_max,'root_mean_iterations':iterations_total/(6*N),'root_stagnations':stagnations,'all_roots_in_theoretical_bracket':True,
           'energy_terminal':Eold,'input_work':totals[0],'physical_background_dissipation':totals[1],'physical_device_dissipation':totals[2],
           'actual_terminal_balance':Eold+totals[1]+totals[2]-totals[0],'max_abs_actual_step_balance':max_step,'max_abs_actual_cumulative_balance':max_balance,
           'complete_endpoint_increment_residuals':residuals,'residual_work_order':['kinematic_Ku_mid_dot_ru','momentum_v_mid_dot_rp','constitutive_F_mid_times_rF'],
           'signed_residual_work_sums':work_sums,'absolute_residual_work_sums':abs_work_sums,'max_abs_step_residual_works':max_work,
           'terminal_balance_minus_summed_residual_work':Eold+totals[1]+totals[2]-totals[0]-sum(work_sums),
           'max_abs_step_energy_balance_minus_residual_works':max_identity,'max_abs_half_constitutive_residual_minus_scalar_root_residual':max_root_to_const,
           'max_abs_endpoint_midpoint_minus_solved_midpoint':max_mid_consistency,'minimum_step_background_dissipation':min_bg,'minimum_step_device_dissipation':min_dev,
           'BE_numerical_dissipation_formula_used':False,'dissipation_midpoints':'actual endpoint averages','sampled_peaks':peaks,'fixed_indices':indices}
        summaries.append(s);memory_runs[N]=z;event('prediction_complete',N=N,trajectory_sha256=trajectory_sha)
    save('prediction_summary.json',{'status':'candidate_before_reference_access','reference_accessed':False,'predictions':summaries})
    csvsave('prediction_fixed_snapshots.csv',snapshots);csvsave('six_block_increment_residuals.csv',blocks)
    save('prediction_freeze.json',{'utc':stamp(),'both_predictions_complete':True,'reference_not_accessed':True,
                                  'code_sha256':sha(__file__),'protocol_sha256':sha(H/'protocol.json'),
                                  'prediction_summary_sha256':sha(H/'prediction_summary.json'),'snapshots_sha256':sha(H/'prediction_fixed_snapshots.csv'),
                                  'residual_blocks_sha256':sha(H/'six_block_increment_residuals.csv'),
                                  'memory_trajectory_sha256':{str(s['N']):s['memory_trajectory_sha256'] for s in summaries}})
    pf=json.loads((H/'prediction_freeze.json').read_text(encoding='utf-8'))
    assert pf['both_predictions_complete'] and len(memory_runs)==2 and sha(H/'prediction_summary.json')==pf['prediction_summary_sha256']
    assert sha(H/'prediction_fixed_snapshots.csv')==pf['snapshots_sha256'] and sha(H/'six_block_increment_residuals.csv')==pf['residual_blocks_sha256']
    event('both_prediction_summaries_snapshots_and_hashes_persisted',prediction_freeze_sha256=sha(H/'prediction_freeze.json'))
    event('reference_hash_access_start');reference=Path(p['reference_path']);ref_sha=sha(reference);assert ref_sha==p['reference_sha256']
    event('reference_hash_verified_np_load_next',sha256=ref_sha)
    # The only np.load is behind the persisted two-prediction gate; no other member is accessed.
    with np.load(reference,allow_pickle=False) as archive:ref=archive['D_N16384']
    event('D_N16384_reference_read_complete')
    assert ref.shape==(98305,9) and ref.dtype==np.float64 and np.isfinite(ref).all()
    assert np.array_equal(ref[:,0],memory_runs[16384][:,0]) and np.array_equal(ref[::2,0],memory_runs[8192][:,0])
    def errors(pred,truth):
        out={}
        for name,col in [('u1',1),('u2',2),('F',5)]:
            er=pred[:,col]-truth[:,col];j=int(np.argmax(abs(er)))
            out[name]={'max_abs_error':float(max(abs(er))),'RMS_error':float(np.sqrt(np.mean(er*er))),'max_error_node_in_comparison':j,'time':float(pred[j,0]),'signed_error':float(er[j])}
        return out
    comparisons={'coarse_vs_reference_on_49153_common_nodes':errors(memory_runs[8192],ref[::2]),
                 'fine_vs_reference_on_49153_common_nodes':errors(memory_runs[16384][::2],ref[::2]),
                 'fine_vs_reference_on_98305_all_nodes':errors(memory_runs[16384],ref),
                 'coarse_vs_fine_prediction_on_49153_common_nodes':errors(memory_runs[8192],memory_runs[16384][::2])}
    gates={name:comparisons['fine_vs_reference_on_98305_all_nodes'][name]['max_abs_error']<.1 for name in ['u1','u2']}
    improvement={name:{metric:comparisons['fine_vs_reference_on_49153_common_nodes'][name][metric]<comparisons['coarse_vs_reference_on_49153_common_nodes'][name][metric] for metric in ['max_abs_error','RMS_error']} for name in ['u1','u2','F']}
    fixed=[]
    for row in snapshots:
        i=row['node']*(2 if row['N']==8192 else 1)
        fixed.append({**row,'reference_node':i,'reference_u1':float(ref[i,1]),'reference_u2':float(ref[i,2]),'reference_F':float(ref[i,5]),
                      'u1_error':row['u1']-float(ref[i,1]),'u2_error':row['u2']-float(ref[i,2]),'F_error':row['F']-float(ref[i,5])})
    csvsave('comparison_fixed_snapshots.csv',fixed)
    # Compare only already-frozen BE error summaries, never BE trajectories.
    be_path=Path(p['BE_summary_path']);assert sha(be_path)==p['BE_summary_sha256']
    be=json.loads(be_path.read_text(encoding='utf-8'));be_comparison={}
    for label,group in comparisons.items():
        be_comparison[label]={}
        for name,metrics in group.items():
            be_comparison[label][name]={metric:{'midpoint':metrics[metric],'BE':be['comparison'][label][name][metric],
                                                       'midpoint_less_than_BE':metrics[metric]<be['comparison'][label][name][metric]} for metric in ['max_abs_error','RMS_error']}
    assert sha(reference)==ref_sha
    for f in freeze['files']:assert sha(f['path'])==f['sha256']
    event('comparisons_complete')
    save('reference_read_order.json',{'events':EVENTS,'not_a_blind_test':True,'all_reference_access_after_two_prediction_freeze':True})
    summary={'task':'R023-forward-midpoint-synthetic','status':'candidate_math_and_independent_review_pending','finished_utc':stamp(),'elapsed_seconds':time.perf_counter()-start,
             'predictions':summaries,'comparison':comparisons,'fine_u1_u2_maxerror_below_point1':gates,'coarse_to_fine_improvement_on_common_grid':improvement,
             'BE_small_summary_comparison_only':be_comparison,'BE_source_sha256':sha(be_path),'BE_trajectory_pointwise_comparison_performed':False,
             'reference_sha256':ref_sha,'reference_member':'D_N16384 only','J_fine_index':16529,'J_coarse_index':None,'J_coarse_grid_coordinate':8264.5,
             'model_input_only_predictions':True,'sources_code_protocol_unchanged':True,'no_large_arrays_saved':True,
             'limits':'Finite same-model sampled numerical comparison; not blind/physical/engineering/FNA certification; no strict convergence order or continuous error bound'}
    save('summary.json',summary)
    lines=['# R023：同一C027基准的隐式中点前向复核','','**candidate**，待每步数学与实现/小输出独审。两档均仅用固定模型、规定中点输入与零初态闭环求F；先冻结预测摘要、7行快照和内存轨迹SHA，随后才读取原D_N16384。未改变旧BE失败或任何旧冻件。','',
           '单端口按冻结消元式，理论括区间为0与b/a_F；最多60次二分，根门1e−11·max(1,|b|)。物理耗散使用实际端点均值。运动学、动量、本构均以完整端点增量重算，并保留非零浮点残差及其残差功；没有套用BE三项数值耗散。','',
           '| N | 最大归一根残差 | 背景/器件物理耗散 | 实际末余额 | 最大逐步余额 |','|---:|---:|---:|---:|---:|']
    for s in summaries:lines.append(f"| {s['N']} | {s['root_max_scaled_residual']:.9g} | {s['physical_background_dissipation']:.9g} / {s['physical_device_dissipation']:.9g} | {s['actual_terminal_balance']:+.9g} | {s['max_abs_actual_step_balance']:.9g} |")
    lines+=['','能量余额按E−E0+物理耗散−输入功直接计算，未裁为零；逐步核对恒等式为 ΔE+Db+Dd−W=(K u_mid)·r_u+v_mid·r_p+F_mid r_F。三项有符号/绝对残差功、逐分量残差最大值/有符号见证/非零计数及12个T块统计均保留。余额小不表示连续误差小。','',
            '| 对照网格 | 输出 | maxabs | RMS |','|---|---|---:|---:|']
    for label,group in comparisons.items():
        for name,m in group.items():lines.append(f"| {label} | {name} | {m['max_abs_error']:.10g} | {m['RMS_error']:.10g} |")
    lines+=['',f'细全网格固定门 maxerror<0.1：u1={gates["u1"]}，u2={gates["u2"]}；全部成败结果原样保留。粗到细的逐项max/RMS改善布尔值见summary，不据两档宣称严格阶数或连续界。','',
            '全窗及严格t>T后的u1/u2/F采样峰和峰时在prediction_summary。粗快照仅0/N/6N；细为0/N/16529/6N，J在粗网格坐标8264.5不是节点，未插值伪造。','',
            'summary另附与已冻结BE小summary的同网格误差统计比较，没有读取或重建BE轨迹，不声称新旧轨迹逐点互比。BE已测数值耗散可作机制线索，改善不能证明误差唯一来源。两种方法与同一RK4参考的有限比较都不构成盲测、物理外验、真实楼层预测或FNA算法认证。','',
            'pre_run_freeze记录根协议/代码及小来源指纹，prediction_freeze与reference_read_order记录先后读取门。仅新目录小代码/JSON/7行预测和比较快照/12行块统计/执行记录，没有NPZ、大时程、图、参数扫描、第三档或ETABS。冻结后停止。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return summary

if __name__=='__main__':
    began=stamp();exit_code=0
    try:
        result=main();print(json.dumps({'status':result['status'],'fine_gate':result['fine_u1_u2_maxerror_below_point1'],'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=True))
    except Exception as exc:
        exit_code=1;save('failure.json',{'status':'candidate_failed_preserved_no_retuning','utc':stamp(),'error':str(exc),'context':CONTEXT,'events':EVENTS,'traceback':traceback.format_exc()});print(traceback.format_exc())
    save('run_record.json',{'started_utc':began,'finished_utc':stamp(),'exit_code':exit_code,'command':[sys.executable,str(Path(__file__).resolve())],'python':sys.version,'numpy':np.__version__,'code_sha256':sha(__file__)})
    save('delivery_manifest.json',{'frozen_utc':stamp(),'status':'candidate','files':[{'path':str(x),'bytes':x.stat().st_size,'sha256':sha(x)} for x in sorted(H.iterdir()) if x.is_file() and x.name!='delivery_manifest.json']})
    sys.exit(exit_code)
