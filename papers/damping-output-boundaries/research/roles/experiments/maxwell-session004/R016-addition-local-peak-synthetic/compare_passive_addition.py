"""Root-frozen finite RK4 U/D diagnostic; all dimensionless, no fulltail proof."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time,traceback
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='fecfc5804181d97fbe10a3c9014f1590c74c3986f82ded05007fb16a170afc66'
NAMES=['u1','u2','v1','v2','F','W_input','D_background','D_device']
CONTEXT={};COMPLETED=[]
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    started=time.perf_counter();assert not (H/'summary_r016.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));source=Path(p['root_protocol']['path'])
    assert sha(source)==p['root_protocol']['sha256']
    root=json.loads(source.read_text(encoding='utf-8'))
    assert root['M']==[[1,0],[0,1]] and root['K']==[[2,-1],[-1,2]] and root['Maxwell']['B']==[0,1] and root['forcing']['b']==[1,1]
    kappa=float(root['Maxwell']['kappa']);c=float(root['Maxwell']['c']);alpha=Fraction(root['Maxwell']['alpha']);q=float(1/alpha)
    assert kappa==8 and c==10 and alpha==Fraction(3,10)
    omega=math.sqrt(2);T=20*math.pi/omega;sqrt3=math.sqrt(3);Cd=(1+sqrt3)/20;Co=(1-sqrt3)/20
    parameters={'M':root['M'],'K':root['K'],'C':[[Cd,Co],[Co,Cd]],'bare_modal_frequencies':[1,sqrt3],
        'bare_modal_zeta':[(Cd+Co)/2,(Cd-Co)/(2*sqrt3)],'kappa':kappa,'c':c,'alpha_rational':str(alpha),'q_rational':str(1/alpha),
        'device_B':[0,1],'forcing_b':[1,1],'forcing_omega':omega,'T':T,'end_time_6T':6*T}
    def rhs(y,ff,device):
        u1,u2,v1,v2,F,_,_,_=y
        speed=(abs(F)/c)**q if device else 0.;sg=math.copysign(speed,F)
        return (v1,v2,ff-Cd*v1-Co*v2-2*u1+u2,
            ff-Cd*v2-Co*v1-2*u2+u1-(F if device else 0.),
            kappa*(v2-sg) if device else 0.,(v1+v2)*ff,
            Cd*(v1*v1+v2*v2)+2*Co*v1*v2,abs(F)*speed if device else 0.)
    def integrate(N,device,label):
        start=time.perf_counter();h=T/N;h2=h/2;h6=h/6;y=(0.,)*8;z=np.empty((6*N+1,8));z[0]=y
        def forcing(j):return math.sin(omega*(j*h)) if 0<j<N else 0.
        for i in range(6*N):
            CONTEXT.update({'branch':label,'N':N,'step':i,'time':i*h,'state8':list(y)})
            if i%8192==0 and time.perf_counter()-started>480:raise TimeoutError('Frozen runtime480s exceeded')
            f0,fhalf,f1=forcing(i),forcing(i+.5),forcing(i+1)
            k1=rhs(y,f0,device);k2=rhs(tuple(y[j]+h2*k1[j] for j in range(8)),fhalf,device)
            k3=rhs(tuple(y[j]+h2*k2[j] for j in range(8)),fhalf,device);k4=rhs(tuple(y[j]+h*k3[j] for j in range(8)),f1,device)
            y=tuple(y[j]+h6*(k1[j]+2*k2[j]+2*k3[j]+k4[j]) for j in range(8));z[i+1]=y
        assert np.isfinite(z).all()
        return z,time.perf_counter()-start
    def energy(z,device):
        u1,u2,v1,v2,F=z[:,:5].T;kin=(v1*v1+v2*v2)/2;elastic=u1*u1+u2*u2-u1*u2
        spring=F*F/(2*kappa) if device else np.zeros(len(z))
        return np.c_[kin,elastic,spring,kin+elastic+spring]
    def peak(z,j,h):
        value=float(max(abs(z[:,j])));ii=np.flatnonzero(abs(z[:,j])==value);first,last=int(ii[0]),int(ii[-1])
        return value,{'first_time':first*h,'first_signed_value':float(z[first,j]),'last_time':last*h,'last_signed_value':float(z[last,j]),'exact_tie_count':len(ii)}
    results=[];runs={}
    for N in [8192,16384]:
        for label,device in [('U',False),('D',True)]:
            z,elapsed=integrate(N,device,label);h=T/N;e=energy(z,device);balance=e[:,3]-z[:,5]+z[:,6]+z[:,7]
            u1p,u1w=peak(z,0,h);u2p,u2w=peak(z,1,h);fp,fw=peak(z,4,h)
            if not device:assert np.all(z[:,4]==0) and np.all(z[:,7]==0)
            row={'branch':label,'N_steps_per_T':N,'dt':h,'actual_steps':6*N,'u1_sampled_abs_peak':u1p,'u1_peak_witness_json':json.dumps(u1w),
                'u2_sampled_abs_peak':u2p,'u2_peak_witness_json':json.dumps(u2w),'F_sampled_abs_peak':fp,'F_peak_witness_json':json.dumps(fw),
                'F_scope':'specified_device' if device else 'no_device_F_identically_zero_not_applicable_physical_force',
                'E_at_T':float(e[N,3]),'E_terminal_6T':float(e[-1,3]),'Ekin_terminal':float(e[-1,0]),
                'Ephysical_elastic_terminal':float(e[-1,1]),'Edevice_spring_terminal':float(e[-1,2]),
                'W_at_T':float(z[N,5]),'Db_at_T':float(z[N,6]),'Dd_at_T':float(z[N,7]),
                'W_terminal':float(z[-1,5]),'Db_terminal':float(z[-1,6]),'Dd_terminal':float(z[-1,7]),
                'max_abs_balance_0_6T':float(max(abs(balance))),'terminal_balance':float(balance[-1]),
                'normalized_max_abs_balance':float(max(abs(balance)))/max(1.,float(max(abs(z[:,5]))),float(max(e[:,3]))),
                'min_stored_energy_unclipped':float(min(e[:,3])),'run_elapsed_seconds':elapsed}
            results.append(row);COMPLETED.append(row);runs[(N,label)]=(z,e,row)
            print(json.dumps({'actual_run_finished':label,'N':N,'elapsed_s':elapsed,'u1_sampled_peak':u1p}),flush=True)
    margins=[]
    for N in [8192,16384]:
        U=runs[(N,'U')][2];D=runs[(N,'D')][2];delta=D['u1_sampled_abs_peak']-U['u1_sampled_abs_peak']
        margins.append({'N_steps_per_T':N,'U_u1_sampled_abs_peak':U['u1_sampled_abs_peak'],'D_u1_sampled_abs_peak':D['u1_sampled_abs_peak'],
            'D_minus_U_fixed_u1_sampled_peak':delta,'D_exceeds_U_on_this_grid':bool(delta>0)})
    convergence=[]
    for label in ['U','D']:
        co,Ec,rc=runs[(8192,label)];fi,Ef,rf=runs[(16384,label)];error=np.max(abs(fi[::2]-co),axis=0)
        convergence.append({'branch':label,**{'max_common_grid_difference_'+name:float(error[j]) for j,name in enumerate(NAMES)},
            'max_common_grid_total_energy_difference':float(max(abs(Ef[::2,3]-Ec[:,3]))),
            'fine_minus_coarse_u1_sampled_peak':rf['u1_sampled_abs_peak']-rc['u1_sampled_abs_peak'],
            'fine_minus_coarse_u2_sampled_peak':rf['u2_sampled_abs_peak']-rc['u2_sampled_abs_peak'],
            'fine_minus_coarse_force_sampled_peak':rf['F_sampled_abs_peak']-rc['F_sampled_abs_peak'],
            'fine_minus_coarse_terminal_E':rf['E_terminal_6T']-rc['E_terminal_6T']})
    write('four_actual_runs_r016.csv',results);write('fixed_u1_addition_margins.csv',margins);write('step_convergence_r016.csv',convergence)
    cache=H/'local-cache';cache.mkdir(exist_ok=False);history=cache/'four_actual_RK4_histories.npz'
    np.savez_compressed(history,**{f'{label}_N{N}':np.c_[np.arange(len(z))*(T/N),z] for (N,label),(z,_,_) in runs.items()})
    checks={'four_actual_independent_RK4_runs':len(results)==4,'same_M_K_C_input_initial_state_prespecified':True,'all_states_finite_no_clipping':True,
        'U_no_device_force_dissipation_exact_zero':True,'positive_Maxwell_parameters_and_bare5percent':kappa>0 and c>0 and alpha>0 and all(abs(x-.05)<1e-14 for x in parameters['bare_modal_zeta']),
        'root_and_own_protocol_SHA_unchanged':sha(source)==p['root_protocol']['sha256'] and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below480seconds':time.perf_counter()-started<480}
    assert all(checks.values())
    outcome={'diagnostic_success_on_both_frozen_grids':all(m['D_exceeds_U_on_this_grid'] for m in margins),'no_parameter_frequency_or_window_search':True,
        'finite_sampled_support_only_not_continuous_fulltail_proof':True}
    out={'evidence_id':'M-EXP-R016','status':'nondimensional_finite_sampled_candidate','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-started,'root_protocol':p['root_protocol'],'own_protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),
        'parameters':parameters,'four_actual_runs':results,'fixed_u1_addition_margins':margins,'step_convergence':convergence,'outcome':outcome,'checks':checks,
        'local_only_history_not_stage_upload':{'path':str(history),'bytes':history.stat().st_size,'sha256':sha(history),
            'columns':['t']+NAMES,'arrays':{f'{label}_N{N}':[len(z),9] for (N,label),(z,_,_) in runs.items()}}}
    lines=['# M-EXP-R016：加一只被动Maxwell的固定输出有限采样诊断','',
        '本项是预注册的无量纲两接地质量加耦合弹簧模型，不是普通二层剪切结构、真实ETABS或安全阈值。比较同一M/K/C、同一外力和零初态：U无装置；D只在第二个质量与固定参考点间加入根协议给定的被动Maxwell。没有按结果调参数、输入频率、目标或窗口。', '',
        f"根协议SHA `{p['root_protocol']['sha256']}`。M=I，K=[[2,−1],[−1,2]]，C=0.1sqrt(K)的正定对称分支，裸主体两阶背景ζ均为0.05；kappa=8、c=10、alpha=3/10、B=(0,1)。外力(1,1)sin(sqrt2*t)持续T=20pi/sqrt2，T之后为0。主体K不重复计Maxwell串联弹簧。", '',
        'U/D各自实际运行两档标准RK4：N=8192/16384每T步，各至6T。输入截断在N节点恰好发生，端点数学sin20pi取0。输入功、背景耗能和器件耗能作为增广状态积分；器件耗散率|F|(|F|/10)^(10/3)，储能F²/16。U的F/Dd恒零是无装置分支定义，不是缺失填0。', '',
        '| 分支/每T步数 | 固定u1采样绝对峰 | 首见时刻/有符号值 | u2采样绝对峰 | 器件力采样绝对峰 |', '|---|---:|---|---:|---:|']
    for row in results:
        pw=json.loads(row['u1_peak_witness_json']);lines.append(f"| {row['branch']}/{row['N_steps_per_T']} | {row['u1_sampled_abs_peak']:.12g} | {pw['first_time']:.12g} / {pw['first_signed_value']:+.12g} | {row['u2_sampled_abs_peak']:.12g} | {row['F_sampled_abs_peak']:.12g} |")
    lines+=['', '峰值来自原节点网格，未作峰时插值。两位移及装置力峰的首/末见时刻、符号和精确并列点数均在四行小CSV；U的全程零力以并列计数及首/末时刻压缩记录。', '',
        '| 每T步数 | D减U的固定u1采样峰差 | 本网格D峰大于U峰 |', '|---|---:|---|']
    for row in margins:lines.append(f"| {row['N_steps_per_T']} | {row['D_minus_U_fixed_u1_sampled_peak']:+.12g} | {row['D_exceeds_U_on_this_grid']} |")
    lines+=['', f"两档预定有限网格均满足D峰大于U峰：{outcome['diagnostic_success_on_both_frozen_grids']}。这是本模型、本输入、固定u1的有限采样诊断；失败标志同样原样保留。不能凭两步长一致把它改写为连续无限尾全峰证明、工程普遍反升规律或创新性结论。", '',
        '## 完整末储能及收支', '', '| 分支/步数 | E(T) | E(6T) | W(6T) | Db(6T) | Dd(6T) | 全程max abs余额 |', '|---|---:|---:|---:|---:|---:|---:|']
    for row in results:lines.append(f"| {row['branch']}/{row['N_steps_per_T']} | {row['E_at_T']:.12g} | {row['E_terminal_6T']:.12g} | {row['W_terminal']:.12g} | {row['Db_terminal']:.12g} | {row['Dd_terminal']:.12g} | {row['max_abs_balance_0_6T']:.6g} |")
    lines+=['', 'E为动能、主体弹性和D分支串联弹簧能之和，完整末端三项分量均保留小表/JSON，不将末能置0。相同外力不要求输入功相同，W取决于各自速度；未把收支余额当严格状态误差或全尾证书。', '',
        '## 两步长比较', '']
    for row in convergence:lines.append(f"{row['branch']}：共同网格u1最大差{row['max_common_grid_difference_u1']:.6g}，F最大差{row['max_common_grid_difference_F']:.6g}，总E最大差{row['max_common_grid_total_energy_difference']:.6g}；各自u1采样峰差{row['fine_minus_coarse_u1_sampled_peak']:+.6g}。新增中间采样点会影响采样峰，峰差不等于共同网格轨迹误差或严格误差包络。")
    lines+=['', '完整四次实际轨迹仅留local-cache，精确路径/列/形状/SHA见summary，不stage或上传，不输出数组日志。源SHA前后相同，无原始工程表、ETABS、ODE以外求解器、图、新依赖或Git操作。完成冻结停止，是否进行连续认证由主控另定。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={n:sha(H/n) for n in ['four_actual_runs_r016.csv','fixed_u1_addition_margins.csv','step_convergence_r016.csv','report.md']}
    (H/'summary_r016.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'run_record_r016.json').write_text(json.dumps({'actual_command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,
        'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],'python':sys.version,'numpy':np.__version__,
        'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r016.json'),'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','fixed_u1_addition_margins','step_convergence','outcome','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        failure={'evidence_id':'M-EXP-R016','status':'failed_prespecified_diagnostic_no_tuning','failed_utc':datetime.now(timezone.utc).isoformat(),'error':repr(exc),
            'context':CONTEXT,'completed_runs':COMPLETED,'traceback':traceback.format_exc()}
        with (H/'failure_r016.json').open('x',encoding='utf-8') as f:json.dump(failure,f,ensure_ascii=False,indent=2)
        raise
