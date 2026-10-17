"""Classical signed bare-body modal diagnostics from frozen fine U/D records."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time,traceback
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='9780d45d2ea9103d2ce701430bce97074a70b6d38cfb2b221d2bd82ec660a7ab'
CONTEXT={}
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    start=time.perf_counter();assert not (H/'summary_r018.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs']
    assert all(sha(x['path'])==x['sha256'] for x in refs.values())
    root=json.loads(Path(refs['addition_model']['path']).read_text(encoding='utf-8'))
    assert root['K']==[[2,-1],[-1,2]] and root['Maxwell']['B']==[0,1]
    N=p['N'];J=p['J'];indices=p['fixed_indices'];assert indices==[0,N,J,6*N] and N==16384 and J==16529
    s2=math.sqrt(2);s3=math.sqrt(3);scale=1/s2;Cd=(1+s3)/20;Co=(1-s3)/20;omega=s2
    snapshots=[];ledger=[];identity_checks={};branch_diagnostics={};fixedJ={};original_t=None
    def identity(label,lhs,rhs):
        err=float(max(abs(lhs-rhs)));tolerance=1e-12*max(1.,float(max(abs(lhs))),float(max(abs(rhs))))
        identity_checks[label]={'max_abs_residual':err,'arithmetic_tolerance':tolerance,'passed':err<=tolerance}
    with np.load(refs['local_cache']['path'],allow_pickle=False) as z:
        for branch in ['U','D']:
            CONTEXT['branch']=branch;a=z[branch+'_N16384'];assert a.shape==(98305,9) and np.isfinite(a).all()
            t,u1,u2,v1,v2,F,originalW,originalDb,originalDd=a.T
            assert np.all(np.diff(t)>0)
            if original_t is None:original_t=t.copy()
            else:assert np.array_equal(t,original_t)
            forcing=np.array([math.sin(omega*float(tt)) if 0<i<N else 0. for i,tt in enumerate(t)])
            qp=(u1+u2)*scale;qm=(u1-u2)*scale;vp=(v1+v2)*scale;vm=(v1-v2)*scale
            u1p,u1m=qp*scale,qm*scale;u2p,u2m=qp*scale,-qm*scale
            Ep=(vp*vp+qp*qp)/2;Em=(vm*vm+3*qm*qm)/2;Es=F*F/16 if branch=='D' else np.zeros(len(t))
            raw_body=(v1*v1+v2*v2)/2+u1*u1+u2*u2-u1*u2
            Pinp=s2*forcing*vp;Pinm=np.zeros(len(t));Pdevp=-F*vp*scale;Pdevm=F*vm*scale
            Pbgp=.1*vp*vp;Pbgm=.1*s3*vm*vm
            physical_input=forcing*(v1+v2);physical_device=-F*v2;physical_background=Cd*(v1*v1+v2*v2)+2*Co*v1*v2
            Dd_power=abs(F)*(abs(F)/10)**(10/3)
            identity(branch+'_u1_reconstruction',u1p+u1m,u1);identity(branch+'_u2_reconstruction',u2p+u2m,u2)
            identity(branch+'_v1_reconstruction',(vp+vm)*scale,v1);identity(branch+'_v2_reconstruction',(vp-vm)*scale,v2)
            identity(branch+'_body_energy_reconstruction',Ep+Em,raw_body)
            identity(branch+'_input_power_sum',Pinp+Pinm,physical_input)
            identity(branch+'_device_power_sum',Pdevp+Pdevm,physical_device)
            identity(branch+'_background_power_sum',Pbgp+Pbgm,physical_background)
            for j in indices:
                snapshots.append({'branch':branch,'node_index':j,'t_original_label':float(t[j]),'u1_signed':float(u1[j]),'u2_signed':float(u2[j]),
                    'v1_signed':float(v1[j]),'v2_signed':float(v2[j]),'F_signed':float(F[j]),'q_plus':float(qp[j]),'q_minus':float(qm[j]),
                    'qdot_plus':float(vp[j]),'qdot_minus':float(vm[j]),'u1_from_plus_signed':float(u1p[j]),'u1_from_minus_signed':float(u1m[j]),
                    'u2_from_plus_signed':float(u2p[j]),'u2_from_minus_signed':float(u2m[j]),'E_plus_bare':float(Ep[j]),'E_minus_bare':float(Em[j]),
                    'E_body_physical':float(raw_body[j]),'E_Maxwell_spring':float(Es[j]),'E_total_modal_plus_spring':float(Ep[j]+Em[j]+Es[j]),
                    'input_scalar_a':float(forcing[j]),'Pin_plus':float(Pinp[j]),'Pin_minus':float(Pinm[j]),'Pdevice_plus_signed':float(Pdevp[j]),
                    'Pdevice_minus_signed':float(Pdevm[j]),'Pbackground_plus':float(Pbgp[j]),'Pbackground_minus':float(Pbgm[j])})
            def trap(values,j):
                return math.fsum(float(x) for x in (t[1:j+1]-t[:j])*(values[1:j+1]+values[:j])/2)
            for j in [N,J,6*N]:
                Win=trap(Pinp+Pinm,j);Wdev=trap(Pdevp+Pdevm,j);Dbg=trap(Pbgp+Pbgm,j);Wdevphysical=trap(physical_device,j)
                delta_spring=float(Es[j]-Es[0]);Dd_old=float(originalDd[j]-originalDd[0]);Dd_trap=trap(Dd_power,j)
                body_delta=float(raw_body[j]-raw_body[0]);port_RK4_diag=Wdev+delta_spring+Dd_old
                body_diag=body_delta-(Win+Wdev-Dbg)
                for mode,E,Pin,Pdev,Pbg in [('plus',Ep,Pinp,Pdevp,Pbgp),('minus',Em,Pinm,Pdevm,Pbgm)]:
                    win=trap(Pin,j);wdev=trap(Pdev,j);dbg=trap(Pbg,j);delta=float(E[j]-E[0])
                    ledger.append({'branch':branch,'bare_mode':mode,'end_node_index':j,'t_end_original_label':float(t[j]),
                        'delta_E_mode':delta,'external_input_work_trap':win,'device_work_to_mode_trap_signed':wdev,'background_dissipation_trap':dbg,
                        'modal_energy_minus_trap_work_residual':delta-(win+wdev-dbg),
                        'aggregate_external_input_work_trap':Win,'aggregate_device_work_two_modes_trap_signed':Wdev,
                        'aggregate_background_dissipation_trap':Dbg,'aggregate_delta_body_energy':body_delta,'aggregate_body_energy_trap_residual':body_diag,
                        'device_two_modes_minus_physical_port_trap':Wdev-Wdevphysical,
                        'delta_Maxwell_spring_energy':delta_spring,'device_dissipation_original_RK4':Dd_old,'device_dissipation_power_trap':Dd_trap,
                        'device_mode_work_plus_storage_plus_original_RK4diss_residual':port_RK4_diag,
                        'device_mode_work_plus_storage_plus_trap_diss_residual':Wdev+delta_spring+Dd_trap,
                        'modal_input_trap_minus_original_RK4_input':Win-float(originalW[j]-originalW[0]),
                        'modal_background_trap_minus_original_RK4_background':Dbg-float(originalDb[j]-originalDb[0]),
                        'device_power_trap_minus_original_RK4_dissipation':Dd_trap-Dd_old})
            def combination(x,y):
                if x*y>0:return 'same_sign_addition'
                if x*y<0:return 'opposite_sign_cancellation'
                return 'one_or_both_components_zero'
            fixedJ[branch]={'node_index':J,'time_original_label':float(t[J]),'q_plus':float(qp[J]),'q_minus':float(qm[J]),
                'u1_plus_contribution':float(u1p[J]),'u1_minus_contribution':float(u1m[J]),'u1_sum':float(u1[J]),'u1_combination':combination(u1p[J],u1m[J]),
                'u2_plus_contribution':float(u2p[J]),'u2_minus_contribution':float(u2m[J]),'u2_sum':float(u2[J]),'u2_combination':combination(u2p[J],u2m[J]),
                'E_minus_bare_at_J':float(Em[J]),'minus_direct_input_work_0_J':trap(Pinm,J),'minus_device_work_0_J':trap(Pdevm,J),
                'minus_background_dissipation_0_J':trap(Pbgm,J),'minus_energy_work_residual_0_J':float(Em[J]-Em[0])-trap(Pdevm,J)+trap(Pbgm,J)}
            branch_diagnostics[branch]={'max_abs_q_minus':float(max(abs(qm))),'max_abs_qdot_minus':float(max(abs(vm))),
                'max_E_minus_bare':float(max(Em)),'max_abs_minus_direct_input_power':float(max(abs(Pinm))),
                'nonzero_minus_at_fixed_J':bool(qm[J]!=0 or vm[J]!=0),'F_is_zero_all_points':bool(np.all(F==0))}
    checks={'8_fixed_same_time_rows':len(snapshots)==8,'12_mode_window_work_rows':len(ledger)==12,
        'all_point_kinematic_energy_power_identities_in_arithmetic_tolerance':all(x['passed'] for x in identity_checks.values()),
        'U_antisymmetric_projection_exact_zero_in_frozen_data':branch_diagnostics['U']['max_abs_q_minus']==0 and branch_diagnostics['U']['max_abs_qdot_minus']==0,
        'signed_trapezoid_work_and_residuals_retained':True,'all_source_and_protocol_SHA_unchanged':all(sha(x['path'])==x['sha256'] for x in refs.values()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below480seconds':time.perf_counter()-start<480};assert all(checks.values())
    write('same_time_modal_snapshots.csv',snapshots);write('modal_signed_work_ledger.csv',ledger)
    out={'evidence_id':'M-EXP-R018','status':'classical_bare_modal_finite_grid_diagnostic_candidate','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-start,'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'source_refs':refs,
        'basis':{'phi_plus':[scale,scale],'phi_minus':[scale,-scale],'bare_omega_squared':[1,3],'bare_modal_C_diagonal':[.1,.1*s3],
            'D_device_modal_generalized_loads':['-F/sqrt2','+F/sqrt2'],'not_independent_added_device_linear_modes':True},
        'fixed_J_signed_contributions':fixedJ,'branch_projection_diagnostics':branch_diagnostics,'all_point_identity_checks':identity_checks,
        'max_abs_modal_energy_trap_work_residual':max(abs(x['modal_energy_minus_trap_work_residual']) for x in ledger),
        'max_abs_device_work_storage_original_RK4diss_residual':max(abs(x['device_mode_work_plus_storage_plus_original_RK4diss_residual']) for x in ledger),
        'checks':checks,'two_CSV_rows':{'same_time_modal_snapshots.csv':8,'modal_signed_work_ledger.csv':12},'no_new_ODE_arrays_or_files':True}
    lines=['# M-EXP-R018：裸主体模态与同刻有符号功账本','',
        '这是冻结R016两分支的经典坐标投影和有限细网格诊断，不是加入非线性器件后的两个独立线性模态、新指标、证明、误差证书或实际布置结论。没有新ODE、调参、作图或改选节点。', '',
        '裸主体phi+=(1,1)/sqrt2、phi−=(1,−1)/sqrt2，质量归一；omega²为1/3，背景阻尼投影为diag(0.1,0.1sqrt3)。D在这同一基底中的器件广义力为−F/sqrt2、+F/sqrt2，F内态仍耦合两个坐标。反对称分量没有直接输入项，不能由此把它删掉。', '',
        '## 固定J=16529的同刻贡献', '', '| 分支 | q+ | q− | u1的+贡献 | u1的−贡献 | 原u1 | u2的+贡献 | u2的−贡献 | 原u2 |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for branch in ['U','D']:
        x=fixedJ[branch];lines.append(f"| {branch} | {x['q_plus']:.10g} | {x['q_minus']:.10g} | {x['u1_plus_contribution']:.10g} | {x['u1_minus_contribution']:.10g} | {x['u1_sum']:.10g} | {x['u2_plus_contribution']:.10g} | {x['u2_minus_contribution']:.10g} | {x['u2_sum']:.10g} |")
    d=fixedJ['D'];u=fixedJ['U']
    lines+=['',f"U的反对称q/qdot在全部冻结点均为0。D在固定J的反对称分量非零={branch_diagnostics['D']['nonzero_minus_at_fixed_J']}；在该点u1贡献类型={d['u1_combination']}，u2贡献类型={d['u2_combination']}。只描述这个既定见证，不把各模态独立峰相加，也不从一次见证推广所有时刻。", '',
        f"D在0→J的反对称外力输入功={d['minus_direct_input_work_0_J']:.12g}，器件对该分量有符号功={d['minus_device_work_0_J']:.12g}，背景耗散={d['minus_background_dissipation_0_J']:.12g}，末反对称主体能={d['E_minus_bare_at_J']:.12g}，模态能变减梯形功残差={d['minus_energy_work_residual_0_J']:+.9g}。在本裸主体投影中，器件力项向无直接外力输入的反对称坐标传递功；这不是认定真实工程高阶模态、独立线性解或最优布局。", '',
        '## 功率身份与梯形账本', '',
        '逐点核模态u/v重构、E++E−=主体动能加弹性势能、外力功率相加、背景功率相加，以及P+dev+P−dev=−Fv2。所有时刻的最大残差和浮点尺度均列JSON；通过仅表示这一代数投影的程序一致性。', '',
        '两分支均只在0/N/J/6N出8行同刻快照。功账本对0→N、0→J、0→6N各列两模态，共12行，采用原细网格复合梯形并保留符号。每行含模态能变、外力功、器件功、背景耗散、原样积分余差；并保留两模态器件合功+串联储能变+原RK4器件耗散、梯形耗散版本及原RK4输入/背景比较诊断。', '',
        f"全部小账本中最大|模态能变−梯形功|={out['max_abs_modal_energy_trap_work_residual']:.9g}；最大|两模态器件合功+串联储能变+原RK4耗散|={out['max_abs_device_work_storage_original_RK4diss_residual']:.9g}。这些有限网格积分余差没有补0，也不当真实积分误差上界、ODE误差或闭合证明。", '',
        '相同外力不意味着U/D输入功相同，未强行归一或计算工程减幅率。物理原型为两接地质量和耦合弹簧，非通常两层剪切楼。全部数组只读留本地，没有另存时程；源/协议SHA前后相同。新目录完成冻结，交主控独审，其他角色/共享/Git不改。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={n:sha(H/n) for n in ['same_time_modal_snapshots.csv','modal_signed_work_ledger.csv','report.md']}
    (H/'summary_r018.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'run_record_r018.json').write_text(json.dumps({'actual_command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,
        'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],'python':sys.version,'numpy':np.__version__,
        'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r018.json'),'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','fixed_J_signed_contributions','branch_projection_diagnostics','max_abs_modal_energy_trap_work_residual','max_abs_device_work_storage_original_RK4diss_residual','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        failure={'evidence_id':'M-EXP-R018','status':'failed_frozen_modal_diagnostic_no_reselection','failed_utc':datetime.now(timezone.utc).isoformat(),'error':repr(exc),'context':CONTEXT,'traceback':traceback.format_exc()}
        with (H/'failure_r018.json').open('x',encoding='utf-8') as f:json.dump(failure,f,ensure_ascii=False,indent=2)
        raise
