"""Four actual RK4 integrations of root-frozen synthetic alpha1 Maxwell model."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='13b73b8306d09215b26fe96a4368e4d068900bd79669803b6a287e4b1e93119b'
NAMES=['u1','u2','v1','v2','F','W_input','D_background','D_device']
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    started=time.perf_counter();assert not (H/'summary_r012.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));source=Path(p['root_protocol']['path'])
    assert source.is_absolute() and sha(source)==p['root_protocol']['sha256']
    root=json.loads(source.read_text(encoding='utf-8'));assert root['M']==[[1,0],[0,1]] and root['ports']=={'layout_A':[1,0],'layout_B':[0,1]}
    eps=root['epsilon'];T=20*math.pi;w=math.sqrt(1+2*eps);aR=.1*w/(1+w);bR=.1/(1+w)
    Kd=1+eps;Ko=-eps;Cd=aR+bR*Kd;Co=bR*Ko
    lo,hi=1.7,1.73
    for _ in range(64):
        mid=(lo+hi)/2
        if mid==lo or mid==hi:break
        if mid**3-3*mid+.1>0:hi=mid
        else:lo=mid
    r=(lo+hi)/2;rate=r**3;kappa=3*r*r-1-.1*rate;c=kappa/rate
    assert aR>=0 and bR>=0 and kappa>0 and c>0 and 1.7<r<1.73 and abs(r**3-3*r+.1)<1e-14
    model={'synthetic_alpha':1,'epsilon':eps,'M':root['M'],'K':[[Kd,Ko],[Ko,Kd]],'Rayleigh_aR':aR,'Rayleigh_bR':bR,'C':[[Cd,Co],[Co,Cd]],
        'bare_modal_omega':[1,w],'bare_modal_zeta':[(Cd+Co)/2,(Cd-Co)/(2*w)],'r':r,'cubic_residual':r**3-3*r+.1,
        'a_device':rate,'kappa':kappa,'c_device':c,'T':T,'end_time_6T':6*T}
    assert all(abs(z-.05)<1e-14 for z in model['bare_modal_zeta'])
    def rhs(y,ff,port):
        u1,u2,v1,v2,F,_,_,_=y
        return (v1,v2,ff-Cd*v1-Co*v2-Kd*u1-Ko*u2-(F if port==0 else 0.),
            ff-Cd*v2-Co*v1-Kd*u2-Ko*u1-(F if port==1 else 0.),kappa*(v1 if port==0 else v2)-rate*F,
            (v1+v2)*ff,Cd*(v1*v1+v2*v2)+2*Co*v1*v2,F*F/c)
    def integrate(N,port):
        tstart=time.perf_counter();h=T/N;h2=h/2;h6=h/6;y=(0.,)*8;data=np.empty((6*N+1,8));data[0]=y
        def force(j):return math.sin(j*h) if 0<j<N else 0.
        for i in range(6*N):
            if i%8192==0 and time.perf_counter()-started>360:raise TimeoutError('Frozen runtime exhausted')
            f0,fhalf,f1=force(i),force(i+.5),force(i+1)
            k1=rhs(y,f0,port);k2=rhs(tuple(y[j]+h2*k1[j] for j in range(8)),fhalf,port)
            k3=rhs(tuple(y[j]+h2*k2[j] for j in range(8)),fhalf,port);k4=rhs(tuple(y[j]+h*k3[j] for j in range(8)),f1,port)
            y=tuple(y[j]+h6*(k1[j]+2*k2[j]+2*k3[j]+k4[j]) for j in range(8));data[i+1]=y
        assert np.isfinite(data).all()
        return data,time.perf_counter()-tstart
    def energies(z):
        u1,u2,v1,v2,F=z[:,:5].T
        kin=(v1*v1+v2*v2)/2;elastic=(Kd*(u1*u1+u2*u2)+2*Ko*u1*u2)/2;device=F*F/(2*kappa)
        return np.c_[kin,elastic,device,kin+elastic+device]
    def peaks(z,j,h):
        value=float(max(abs(z[:,j])));ii=np.flatnonzero(abs(z[:,j])==value)
        return value,[{'t':float(i*h),'signed_value':float(z[i,j])} for i in ii]
    runs={};small=[];symmetry=[]
    for N in [8192,16384]:
        for port,label in [(0,'A'),(1,'B')]:
            z,elapsed=integrate(N,port);e=energies(z);h=T/N;balance=e[:,3]-z[:,5]+z[:,6]+z[:,7]
            upeak,ut=peaks(z,0,h);u2peak,u2t=peaks(z,1,h);Fpeak,Ft=peaks(z,4,h)
            row={'layout':label,'N_steps_per_T':N,'dt':h,'actual_steps':6*N,'sampled_u1_abs_peak':upeak,'u1_peak_controllers_json':json.dumps(ut),
                'sampled_u2_abs_peak':u2peak,'u2_peak_controllers_json':json.dumps(u2t),'sampled_device_force_abs_peak':Fpeak,'force_peak_controllers_json':json.dumps(Ft),
                'E_at_T':float(e[N,3]),'W_at_T':float(z[N,5]),'Db_at_T':float(z[N,6]),'Dd_at_T':float(z[N,7]),
                'E_terminal_6T':float(e[-1,3]),'Ekin_terminal':float(e[-1,0]),'Ephysical_elastic_terminal':float(e[-1,1]),'Edevice_spring_terminal':float(e[-1,2]),
                'W_terminal':float(z[-1,5]),'Db_terminal':float(z[-1,6]),'Dd_terminal':float(z[-1,7]),
                'max_abs_energy_balance_0_6T':float(max(abs(balance))),'terminal_energy_balance':float(balance[-1]),
                'max_abs_normalized_energy_balance':float(max(abs(balance)))/max(1.,float(max(abs(z[:,5]))),float(max(e[:,3]))),
                'min_stored_energy_unclipped':float(min(e[:,3])),'run_elapsed_seconds':elapsed}
            small.append(row);runs[(N,label)]=(z,e,row)
            print(json.dumps({'actual_run_finished':label,'N':N,'elapsed_s':elapsed,'u1_sampled_peak':upeak}),flush=True)
        A,EA,_=runs[(N,'A')];B,EB,_=runs[(N,'B')];permuted=A[:,[1,0,3,2,4,5,6,7]]
        state_diff=np.max(abs(B-permuted),axis=0);energy_diff=np.max(abs(EB-EA),axis=0)
        symmetry.append({'N':N,'max_permuted_state_residual_by_component':dict(zip(NAMES,map(float,state_diff))),
            'max_energy_trajectory_difference':dict(zip(['kinetic','physical_elastic','device_spring','total'],map(float,energy_diff))),
            'max_inputwork_difference':float(max(abs(B[:,5]-A[:,5]))),'max_background_dissipation_difference':float(max(abs(B[:,6]-A[:,6]))),
            'max_device_dissipation_difference':float(max(abs(B[:,7]-A[:,7]))),
            'arithmetic_tolerance':1e-10*max(1.,float(np.max(abs(A))),float(np.max(abs(B))))})
    convergence=[]
    for label in ['A','B']:
        co,Ec,rc=runs[(8192,label)];fi,Ef,rf=runs[(16384,label)]
        differences=np.max(abs(fi[::2]-co),axis=0)
        convergence.append({'layout':label,**{'max_common_grid_difference_'+name:float(differences[i]) for i,name in enumerate(NAMES)},
            'max_common_grid_total_energy_difference':float(max(abs(Ef[::2,3]-Ec[:,3]))),
            'fine_minus_coarse_u1_sampled_peak':rf['sampled_u1_abs_peak']-rc['sampled_u1_abs_peak'],
            'fine_minus_coarse_device_sampled_peak':rf['sampled_device_force_abs_peak']-rc['sampled_device_force_abs_peak'],
            'fine_minus_coarse_terminal_E':rf['E_terminal_6T']-rc['E_terminal_6T'],
            'fine_minus_coarse_terminal_W':rf['W_terminal']-rc['W_terminal'],
            'fine_minus_coarse_terminal_Db':rf['Db_terminal']-rc['Db_terminal'],'fine_minus_coarse_terminal_Dd':rf['Dd_terminal']-rc['Dd_terminal']})
    write('four_actual_runs_r012.csv',small);write('step_convergence_r012.csv',convergence)
    symmetry_ok=all(max(list(x['max_permuted_state_residual_by_component'].values())+list(x['max_energy_trajectory_difference'].values()))<=x['arithmetic_tolerance'] for x in symmetry)
    checks={'four_independent_actual_RK4_runs':len(small)==4,'root_parameters_unchanged_positive':True,'bare_system_exact5percent_by_construction':True,
        'all_states_finite_no_clipping':True,'permutation_and_energy_trajectory_residuals_in_arithmetic_tolerance':symmetry_ok,
        'root_and_own_protocol_SHA_unchanged':sha(source)==p['root_protocol']['sha256'] and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below360seconds':time.perf_counter()-started<360}
    out={'evidence_id':'M-EXP-R012','status':'synthetic finite_sampled_support_only','finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-started,
        'root_protocol':p['root_protocol'],'own_protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'parameters':model,'four_runs':small,
        'symmetry_checks':symmetry,'step_convergence':convergence,'checks':checks,'not_fulltail_or_fullpeak_proof':True,
        'no_full_time_state_array_files_written':True,'synthetic_alpha1_not_real_ETABS_or_alpha_point3':True}
    lines=['# M-EXP-R012：两DOF布局置换的独立合成RK4验证','',
        '本项是根冻结协议的合成alpha=1 Maxwell测试，不是用户alpha=0.3或真实ETABS工程验证，不是新指标。两个布局各自实际积分两次，未用交换A轨迹代替B计算。参数、输入、窗口与步长未按结果修改。', '',
        f"根协议SHA `{p['root_protocol']['sha256']}`。由三次方程在(1.7,1.73)内二分得到r={r:.16g}，残差{model['cubic_residual']:.6g}；kappa={kappa:.16g}，c={c:.16g}，a_device={rate:.16g}。C按非负Rayleigh定义生成，裸主体两阶背景ζ为{model['bare_modal_zeta']}。主体K不含器件串联弹簧。", '',
        '输入为两坐标相同sin(t)，T=20pi处取数学端点0，此后为0。标准RK4对u1/u2/v1/v2/F及输入功、背景耗能、器件耗能8状态同步积分至6T，时间由步编号生成，截止恰在N。未裁剪负值、积分结果或末储能。', '',
        '| 布局 | 每T步数 | dt | u1采样绝对峰 | u1峰时刻及符号 | 装置力采样绝对峰 | 力峰时刻及符号 |', '|---|---:|---:|---:|---|---:|---|']
    for row in small:
        show=lambda k:'; '.join(f"{x['t']:.10g} / {x['signed_value']:+.10g}" for x in json.loads(row[k]))
        lines.append(f"| {row['layout']} | {row['N_steps_per_T']} | {row['dt']:.9g} | {row['sampled_u1_abs_peak']:.12g} | {show('u1_peak_controllers_json')} | {row['sampled_device_force_abs_peak']:.12g} | {show('force_peak_controllers_json')} |")
    lines+=['', '## 总能量与全过程收支', '',
        '储能E=动能+主体弹性势能+F²/(2kappa)。全程核R=E−W_input+D_background+D_device，初态全部0。输入功和两种耗能分别是RK4增广状态，未用末储能代替耗散。', '',
        '| 布局/步数 | E(T) | E(6T) | W(6T) | Db(6T) | Dd(6T) | 全程max abs R |', '|---|---:|---:|---:|---:|---:|---:|']
    for row in small:lines.append(f"| {row['layout']}/{row['N_steps_per_T']} | {row['E_at_T']:.12g} | {row['E_terminal_6T']:.12g} | {row['W_terminal']:.12g} | {row['Db_terminal']:.12g} | {row['Dd_terminal']:.12g} | {row['max_abs_energy_balance_0_6T']:.6g} |")
    for sym in symmetry:lines+=['',f"每T步数{sym['N']}：置换后8状态最大残差{max(sym['max_permuted_state_residual_by_component'].values()):.6g}，总储能轨迹差{sym['max_energy_trajectory_difference']['total']:.6g}，输入功/背景耗能/器件耗能轨迹差分别{sym['max_inputwork_difference']:.6g}/{sym['max_background_dissipation_difference']:.6g}/{sym['max_device_dissipation_difference']:.6g}。动能、主体势能、器件储能的单项差保留于JSON。"]
    lines+=['', '## 步长变化与解释限制', '']
    for row in convergence:lines.append(f"布局{row['layout']}：细步对粗步在共同网格的u1最大差{row['max_common_grid_difference_u1']:.6g}、F最大差{row['max_common_grid_difference_F']:.6g}、总储能最大差{row['max_common_grid_total_energy_difference']:.6g}；u1采样峰差{row['fine_minus_coarse_u1_sampled_peak']:+.6g}、装置采样峰差{row['fine_minus_coarse_device_sampled_peak']:+.6g}。完整8状态和末收支变化另列小CSV。")
    lines+=['', '这些是有限步长、有限0至6T网格上的数值支持，不是连续峰值或无限自由尾证明；末储能即使很小也不被置0。全尾解析界由角色1R013审查。置换及能量差使用预定浮点尺度检查，dt变化未按工程合格阈值判定，也未补算新参数追阳性。', '',
        '所有错误/未通过标志原样保留于summary。没有写出完整时间/状态数组、生成图片或调用Excel/ETABS/新依赖/付费求解。根协议和共享/Git保持不变，冻结后停止。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={name:sha(H/name) for name in ['four_actual_runs_r012.csv','step_convergence_r012.csv','report.md']}
    (H/'summary_r012.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    run={'actual_command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,'python':sys.version,'numpy':np.__version__,
        'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r012.json'),'checks':checks}
    (H/'run_record_r012.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','parameters','symmetry_checks','step_convergence','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
