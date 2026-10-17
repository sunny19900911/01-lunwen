"""Floating midpoint/residual-budget feasibility only, never a rigorous certificate."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time,traceback
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='68dd9a7f9d49a4a1d9285ca0918f1d75193bdc72a0b6b22db13489c6a8a5e927'
CONTEXT={}
DIAG=['r_u1','r_u2','r_v1','r_v2','r_F','Lg_float_nominal','scalar_root_residual','budget_midpoint','budget_variation','budget_total','root_iterations']
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    start=time.perf_counter();assert not (H/'summary_r014.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs']
    assert all(sha(x['path'])==x['sha256'] for x in refs.values())
    root=json.loads(Path(refs['nonlinear_root']['path']).read_text(encoding='utf-8'));assert root['id']=='M-SYN-LAYOUT-N03-001'
    N=16384;steps=6*N;T=20*math.pi;h=T/N;q=10/3;eps=.001;w=math.sqrt(1+2*eps)
    aR=.1*w/(1+w);bR=.1/(1+w);Kd=1+eps;Ko=-eps;Cd=aR+bR*Kd;Co=bR*Ko
    lo,hi=1.7,1.73
    for _ in range(64):
        mid=(lo+hi)/2
        if mid==lo or mid==hi:break
        if mid**3-3*mid+.1>0:hi=mid
        else:lo=mid
    r=(lo+hi)/2;r3=r**3;kappa=3*r*r-1-.1*r3;c=kappa/r3
    assert 0<kappa<8 and c>0
    Dd=2/h+Cd+(h/2)*Kd;Do=Co+(h/2)*Ko;det=Dd*Dd-Do*Do
    d1=Dd/det;d2=-Do/det;aroot=2/(kappa*h)+d1
    def g(F):return math.copysign((abs(F)/c)**q,F)
    def gp(F):return q/c*(abs(F)/c)**(q-1)
    def solve_scalar(R,guess):
        if R==0:return 0.,0.,0
        lo,hi=sorted((0.,R/aroot));x=min(hi,max(lo,guess));tol=1e-13*max(1.,abs(R))
        for it in range(1,51):
            value=aroot*x+g(x)-R
            if abs(value)<=tol:return x,value,it
            if value>0:hi=x
            else:lo=x
            trial=x-value/(aroot+gp(x))
            if not lo<trial<hi:trial=(lo+hi)/2
            if trial==x:raise ArithmeticError(f'Monotone root stagnated; residual={value!r}, tol={tol!r}')
            x=trial
        raise ArithmeticError(f'Monotone root not converged in50iterations; residual={value!r}')
    def energy(u1,u2,v1,v2,F):
        kin=(v1*v1+v2*v2)/2;elastic=(Kd*(u1*u1+u2*u2)+2*Ko*u1*u2)/2;spring=F*F/(2*kappa)
        return kin,elastic,spring,kin+elastic+spring
    endpoints=np.empty((steps+1,6));endpoints[0]=0.;diagnostics=np.empty((steps,len(DIAG)))
    u1=u2=v1=v2=F=0.;W=Db=Ddev=0.;balance_max=0.;energy_T=None;totals_T=None
    for i in range(steps):
        if i%8192==0 and time.perf_counter()-start>600:raise TimeoutError('Frozen runtime600s exceeded')
        CONTEXT.update({'segment':i,'time':i*h,'state5':[u1,u2,v1,v2,F]})
        forcing=math.sin((i+.5)*h) if i<N else 0.
        rhs1=(2/h)*v1-Kd*u1-Ko*u2+forcing;rhs2=(2/h)*v2-Kd*u2-Ko*u1+forcing
        w1=(Dd*rhs1-Do*rhs2)/det;w2=(Dd*rhs2-Do*rhs1)/det
        Froot,root_res,it=solve_scalar(w1+2*F/(kappa*h),F)
        vm1=w1-d1*Froot;vm2=w2-d2*Froot
        un1=u1+h*vm1;un2=u2+h*vm2;vn1=2*vm1-v1;vn2=2*vm2-v2;Fn=2*Froot-F
        if not all(math.isfinite(x) for x in [un1,un2,vn1,vn2,Fn]):raise ArithmeticError('Nonfinite midpoint state')
        Du1,Du2=un1-u1,un2-u2;Dv1,Dv2=vn1-v1,vn2-v2;DF=Fn-F
        um1,um2=(u1+un1)/2,(u2+un2)/2;emv1,emv2=(v1+vn1)/2,(v2+vn2)/2;emF=(F+Fn)/2
        ru1,ru2=Du1/h-emv1,Du2/h-emv2
        rv1=Dv1/h+Cd*emv1+Co*emv2+Kd*um1+Ko*um2+emF-forcing
        rv2=Dv2/h+Cd*emv2+Co*emv1+Kd*um2+Ko*um1-forcing
        rF=DF/(kappa*h)-emv1+g(emF)
        Lg=q*c**(-q)*max(abs(F),abs(Fn))**(q-1)
        bound_mid=h*(1.001*(abs(ru1)+abs(ru2))+abs(rv1)+abs(rv2)+3*abs(rF))
        linear1=Cd*Dv1+Co*Dv2+Kd*Du1+Ko*Du2+DF;linear2=Cd*Dv2+Co*Dv1+Kd*Du2+Ko*Du1
        bound_var=h/4*(1.001*(abs(Dv1)+abs(Dv2))+abs(linear1)+abs(linear2)+2*h*(1 if i<N else 0)+3*(abs(Dv1)+Lg*abs(DF)))
        budget=bound_mid+bound_var
        diagnostics[i]=[ru1,ru2,rv1,rv2,rF,Lg,root_res,bound_mid,bound_var,budget,it]
        W+=h*(emv1+emv2)*forcing;Db+=h*(Cd*(emv1*emv1+emv2*emv2)+2*Co*emv1*emv2);Ddev+=h*emF*g(emF)
        u1,u2,v1,v2,F=un1,un2,vn1,vn2,Fn;endpoints[i+1]=[(i+1)*h,u1,u2,v1,v2,F]
        es=energy(u1,u2,v1,v2,F);balance_max=max(balance_max,abs(es[3]-W+Db+Ddev))
        if i+1==N:energy_T=es;totals_T=[W,Db,Ddev]
    assert np.isfinite(endpoints).all() and np.isfinite(diagnostics).all()
    Iprefix=math.fsum(map(float,diagnostics[:N,9]));Itotal=math.fsum(map(float,diagnostics[:,9]))
    Eend=energy(*endpoints[-1,1:]);u1max=float(max(abs(endpoints[:,1])));u2atT=float(endpoints[N,2])
    early=u1max+Itotal;tail=math.sqrt(2*Eend[3])+Itotal;lower=abs(u2atT)-Iprefix;margin=lower-max(early,tail)
    candidates={'all_floating_not_certified':True,'I_prefix_T_float_not_upper':Iprefix,'I_total_6T_float_not_upper':Itotal,
        'fixed_T_abs_uh2':abs(u2atT),'fixed_T_signed_uh2':u2atT,'all_node_max_abs_uh1':u1max,'terminal_energy_float_not_upper':Eend[3],
        'candidate_early_upper_float':early,'candidate_tail_upper_float':tail,'candidate_T_lower_float':lower,'candidate_nominal_margin':margin,'candidate_nominal_separation':bool(margin>0)}
    blocks=[]
    for k in range(6):
        a=diagnostics[k*N:(k+1)*N];row={'block_T_index':k+1,'start_t':k*T,'end_t':(k+1)*T,'budget_mid_sum_float':math.fsum(map(float,a[:,7])),
            'budget_variation_sum_float':math.fsum(map(float,a[:,8])),'budget_total_sum_float':math.fsum(map(float,a[:,9])),
            'Lg_min_float':float(min(a[:,5])),'Lg_max_float':float(max(a[:,5])),'root_iterations_max':int(max(a[:,10]))}
        for j,name in enumerate(DIAG[:5]+['Lg_float_nominal','scalar_root_residual']):
            row['max_abs_'+name]=float(max(abs(a[:,j])));row['nonzero_count_'+name]=int(sum(a[:,j]!=0))
        blocks.append(row)
    chosen=set(map(int,np.argsort(diagnostics[:,9])[-8:]))
    for j in range(7):chosen.add(int(np.argmax(abs(diagnostics[:,j]))))
    examples=[{'segment_index':i,'t_left':i*h,'t_mid':(i+.5)*h,'t_right':(i+1)*h,**dict(zip(DIAG,map(float,diagnostics[i])))} for i in sorted(chosen)]
    write('six_block_budget_diagnostics.csv',blocks);write('representative_nonzero_residuals.csv',examples)
    cache=H/'local-cache';cache.mkdir(exist_ok=False);local=cache/'float_midpoint_endpoints_and_diagnostics.npz'
    np.savez_compressed(local,endpoints=endpoints,segment_float_diagnostics=diagnostics)
    root_summary=json.loads(Path(refs['RK4_scalars']['path']).read_text(encoding='utf-8'))
    rk=next(x for x in root_summary['four_runs'] if x['layout']=='A' and x['N_steps_per_T']==N)
    Fmax=float(max(abs(endpoints[:,5])));peak_i=int(np.argmax(abs(endpoints[:,1])));Fp_i=int(np.argmax(abs(endpoints[:,5])))
    comparison={'RK4_not_rerun':True,'same_fixed_N_and_window':True,'midpoint_sampled_u1_abs_peak':u1max,'midpoint_u1_peak_time':float(endpoints[peak_i,0]),
        'midpoint_u1_peak_signed':float(endpoints[peak_i,1]),'midpoint_sampled_force_abs_peak':Fmax,'midpoint_force_peak_time':float(endpoints[Fp_i,0]),
        'midpoint_force_peak_signed':float(endpoints[Fp_i,5]),'midpoint_minus_RK4_u1_peak':u1max-rk['sampled_u1_abs_peak'],
        'midpoint_minus_RK4_F_peak':Fmax-rk['sampled_device_force_abs_peak'],'midpoint_minus_RK4_E_T':energy_T[3]-rk['E_at_T'],
        'midpoint_minus_RK4_terminal_E':Eend[3]-rk['E_terminal_6T']}
    residual_summary={name:{'maximum_abs_float':float(max(abs(diagnostics[:,j]))),'nonzero_count':int(sum(diagnostics[:,j]!=0)),
        'smallest_abs_nonzero_float':float(min(abs(diagnostics[diagnostics[:,j]!=0,j]))) if np.any(diagnostics[:,j]!=0) else None} for j,name in enumerate(DIAG[:7])}
    checks={'one_A_midpoint_98304_steps_only':len(endpoints)==98305,'all_float_values_finite':True,'all_monotone_roots_accepted_actual_residuals_kept':True,
        'all_midpoint_residuals_recomputed_from_endpoints':True,'all_budget_terms_retained_nonnegative':bool(np.min(diagnostics[:,7:10])>=0),
        'all_source_and_protocol_SHA_unchanged':all(sha(x['path'])==x['sha256'] for x in refs.values()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below600seconds':time.perf_counter()-start<600};assert all(checks.values())
    out={'evidence_id':'M-EXP-R014','status':'floating_prototype_not_certificate','finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
        'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'root_parameters_float':{'r':r,'kappa':kappa,'c':c,'alpha':3/10,'q':q,'h':h,'N':N,'steps':steps,
            'D_diag':Dd,'D_offdiag':Do,'root_linear_coefficient':aroot},'candidate_float_diagnostics':candidates,'residual_float_summary':residual_summary,
        'root_iteration_histogram':{str(int(it)):int(sum(diagnostics[:,10]==it)) for it in np.unique(diagnostics[:,10])},
        'terminal_energy_float_components':dict(zip(['kinetic','physical_elastic','device_spring','total'],Eend)),
        'energy_T_float_components':dict(zip(['kinetic','physical_elastic','device_spring','total'],energy_T)),
        'additional_midpoint_work_balance_not_state_error':{'W_T':totals_T[0],'Db_T':totals_T[1],'Dd_T':totals_T[2],'W_terminal':W,'Db_terminal':Db,'Dd_terminal':Ddev,'max_abs_balance_float':balance_max},
        'comparison_to_frozen_RK4_scalars':comparison,'checks':checks,'source_refs':refs,
        'local_only_cache_not_stage_or_upload':{'path':str(local),'bytes':local.stat().st_size,'sha256':sha(local),'endpoint_columns':['t','u1','u2','v1','v2','F'],
            'endpoints_shape':list(endpoints.shape),'segment_diagnostic_columns':DIAG,'segment_diagnostics_shape':list(diagnostics.shape)}}
    lines=['# M-EXP-R014：隐式中点残差预算浮点原型','',
        '状态：floating prototype，非严格证书。只运行A布局、每T步数16384至6T，未重跑原四次RK4，未改参数或增加第三档。所有I、Lg、候选上/下量和末能均为普通浮点计算，不是向外包络，不能认证连续全尾/全峰。', '',
        '按根proposal分解线性结构中点解和严格单调标量Fm方程；根用预冻括区与Newton/二分保护求解，保留实际根残差。三类中点残差均由实际端点均值和端点差重新计算，未声明为零。每段Lg由端点最大绝对力的导数公式浮点评价；I按proposal固定中点项与h/4变化项累计。', '',
        f"浮点I_prefix(T)={Iprefix:.12g}，I_total(6T)={Itotal:.12g}；固定T的|uh2|={abs(u2atT):.12g}，全节点max|uh1|={u1max:.12g}。",
        '',f"候选early量={early:.12g}，tail量={tail:.12g}，Tlower量={lower:.12g}；名义余量={margin:+.12g}，浮点名义分离={margin>0}。这个布尔值不颁发数学或数值认证。", '',
        f"末完整浮点储能={Eend[3]:.16g}，其中动能={Eend[0]:.16g}、主体弹性={Eend[1]:.16g}、器件串联弹簧={Eend[2]:.16g}。未置零，也不称严格Ehat_upper。", '',
        '## 非零残差与标量根诊断', '', '| 项 | 最大绝对浮点值 | 非零段数 | 最小绝对非零值 |', '|---|---:|---:|---:|']
    for name,z in residual_summary.items():lines.append(f"| {name} | {z['maximum_abs_float']:.9g} | {z['nonzero_count']} | {z['smallest_abs_nonzero_float']} |")
    lines+=['', '六个T长度块的中点/变化预算、Lg范围及非零残差计数另列小CSV；代表段保留实际有符号残差。全部逐段r_u/r_v/r_F、Lg和预算保存在同一个本地NPZ的诊断数组，供后续从端点轨迹独立重算，禁止stage/上传。', '',
        '## 与原固定RK4标量的区别', '',
        f"中点u1采样峰={u1max:.12g}，时刻={endpoints[peak_i,0]:.12g}；器件力采样峰={Fmax:.12g}，时刻={endpoints[Fp_i,0]:.12g}。相对已冻同网格RK4峰差分别{comparison['midpoint_minus_RK4_u1_peak']:+.9g}、{comparison['midpoint_minus_RK4_F_peak']:+.9g}，E(T)差{comparison['midpoint_minus_RK4_E_T']:+.9g}、末E差{comparison['midpoint_minus_RK4_terminal_E']:+.9g}。没有RK4完整轨迹文件，因此只比较已冻标量，不假称共同网格全点误差。", '',
        f"中点增广功/耗能余额最大浮点残差{balance_max:.9g}，仅作实现一致性诊断，未用它替换状态误差预算。", '',
        '本项所有量为无量纲alpha=0.3合成模型，非用户工程参数或新指标。初值、输入和模型浮点偏差仍需严格覆盖；pi/sin、分数幂、线性解、根误差、逐段及总和、末能均未向外取整。数学R015/R024及后续严格数值实现分别独审，本原型只说明固定预算是否值得进入严格实现。', '',
        '本地缓存精确路径、形状、列名和SHA见summary，完整轨迹和诊断不输出日志/共享文件。无Excel、ETABS、新依赖、图或Git操作。完成冻结停止。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={n:sha(H/n) for n in ['six_block_budget_diagnostics.csv','representative_nonzero_residuals.csv','report.md']}
    (H/'summary_r014.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    record={'actual_command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,'python':sys.version,'numpy':np.__version__,
        'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r014.json'),'checks':checks}
    (H/'run_record_r014.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'elapsed_seconds':out['elapsed_seconds'],'candidate_float_diagnostics':candidates,'residual_float_summary':residual_summary,
        'terminal_energy_float_components':out['terminal_energy_float_components'],'comparison_to_RK4':comparison,'checks':checks,'local_cache_bytes':local.stat().st_size},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        failure={'evidence_id':'M-EXP-R014','status':'failed_float_prototype_no_retry','failed_utc':datetime.now(timezone.utc).isoformat(),'error':repr(exc),'context':CONTEXT,'traceback':traceback.format_exc()}
        with (H/'failure_r014.json').open('x',encoding='utf-8') as f:json.dump(failure,f,ensure_ascii=False,indent=2)
        raise
