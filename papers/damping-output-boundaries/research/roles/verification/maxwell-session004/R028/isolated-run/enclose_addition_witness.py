"""One fixed outward prefix witness, candidate pending math/U/implementation audit."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
import csv,hashlib,json,sys,time,traceback
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='18c6fd3916fd9fb74e181ec7b89f6000f197c707fe980897502cc6885c0bf371'
CONTEXT={}
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def readcsv(f):
    with Path(f).open(encoding='utf-8',newline='') as x:return list(csv.DictReader(x))
def main():
    started=time.perf_counter();assert not (H/'summary_r017.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs'];N=p['fixed_N'];J=p['fixed_J']
    assert N==16384 and J==16529 and all(sha(x['path'])==x['sha256'] for x in refs.values())
    root=json.loads(Path(refs['addition_model']['path']).read_text(encoding='utf-8'))
    assert root['M']==[[1,0],[0,1]] and root['K']==[[2,-1],[-1,2]] and root['Maxwell']=={'kappa':8,'c':10,'alpha':'3/10','B':[0,1],'equation':'Fdot=kappa*(B*v-sign(F)*(abs(F)/c)^(10/3))'}
    sm=json.loads(Path(refs['R016_summary']['path']).read_text(encoding='utf-8'))
    row=next(x for x in sm['four_actual_runs'] if x['branch']=='D' and x['N_steps_per_T']==N)
    csvrow=next(x for x in readcsv(refs['four_run_small_CSV']['path']) if x['branch']=='D' and int(x['N_steps_per_T'])==N)
    witness=json.loads(row['u1_peak_witness_json']);csvw=json.loads(csvrow['u1_peak_witness_json'])
    assert witness==csvw and float(csvrow['u1_sampled_abs_peak'])==row['u1_sampled_abs_peak']
    with np.load(refs['local_cache']['path'],allow_pickle=False) as z:
        a=z['D_N16384'];assert a.dtype==np.float64 and a.shape==(98305,9)
        actual_first=int(np.argmax(abs(a[:,1])))
        assert actual_first==J and float(a[J,1])==witness['first_signed_value'] and abs(float(a[J,1]))==row['u1_sampled_abs_peak']
        assert float(a[J,0])==witness['first_time'] and int(round(witness['first_time']/row['dt']))==J
        cached_identity_time=float(a[J,0]);signed_value=float(a[J,1]);states=a[:J+1,1:6].copy()
    assert np.isfinite(states).all() and np.all(states[0]==0.)
    identity={'fixed_J':J,'cache_first_abs_u1_argmax':actual_first,'signed_stored_u1_at_J':signed_value,
        'absolute_stored_u1_at_J':abs(signed_value),'cached_time_identity_only':cached_identity_time,'summary_CSV_cache_exact_match':True,
        'no_reselection':True,'cache_W_Db_Dd_unused':True}
    # Only after the fixed identity gate, construct the new model's intervals.
    sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(refs['helper']['path']).parent))
    import outward_float_v002 as helper
    assert Path(helper.__file__).resolve()==Path(refs['helper']['path']).resolve()
    I=helper.I;up=helper.up;down=helper.down;ZERO=I.point(0);ONE=I.point(1);TWO=I.point(2);THREE=I.point(3);HALF=I.point(.5)
    def absi(x):
        if x.lo>=0:return x
        if x.hi<=0:return I(-x.hi,-x.lo)
        return I(0,max(-x.lo,x.hi))
    def pair(x):return [x.lo,x.hi]
    sqrt3=helper.root(I.point(3),2);omega=helper.root(TWO,2)
    KD=TWO;KO=I.point(-1);CD=(ONE+sqrt3)/20;CO=(ONE-sqrt3)/20;kappa=I.point(8);c=I.point(10)
    h=(20*helper.PI)/(omega*N);H4=h*I.rational(Fraction(1,4));invh=ONE/h;invkh=ONE/(kappa*h)
    input_variation=TWO*h*omega  # Kept for EVERY segment, including n>=N.
    Ihi=0.;max_Lg=0.;max_step=0.;blocks=[];partial={'mid':0.,'variation':0.,'total':0.};first=0
    rnames=['r_u1','r_u2','r_v1','r_v2','r_F'];rmax={name:{'abs_upper':0.,'segment':None,'interval':None} for name in rnames};brmax={name:0. for name in rnames}
    for n in range(J):
        if n%4096==0:
            CONTEXT.update({'segment':n,'I_upper_so_far':Ihi,'elapsed_seconds':time.perf_counter()-started})
            print(json.dumps({'stage':'fixed_prefix_outward','n':n,'I_upper_so_far':Ihi,'elapsed_s':time.perf_counter()-started}),flush=True)
            if time.perf_counter()-started>480:raise TimeoutError('Frozen runtime480s exceeded')
        l=[I.point(float(x)) for x in states[n]];r=[I.point(float(x)) for x in states[n+1]]
        Du1,Du2=r[0]-l[0],r[1]-l[1];Dv1,Dv2=r[2]-l[2],r[3]-l[3];DF=r[4]-l[4]
        um1,um2=(l[0]+r[0])*HALF,(l[1]+r[1])*HALF;vm1,vm2=(l[2]+r[2])*HALF,(l[3]+r[3])*HALF;Fm=(l[4]+r[4])*HALF
        fmid=helper.sin_pi_ratio(20*n+10,N) if n<N else ZERO
        ru1,ru2=Du1*invh-vm1,Du2*invh-vm2
        rv1=Dv1*invh+CD*vm1+CO*vm2+KD*um1+KO*um2-fmid
        rv2=Dv2*invh+CD*vm2+CO*vm1+KD*um2+KO*um1+Fm-fmid
        rF=DF*invkh-vm2+helper.g_power_10_3(Fm,c)
        for name,value in zip(rnames,[ru1,ru2,rv1,rv2,rF]):
            hi=value.abs_upper();brmax[name]=max(brmax[name],hi)
            if hi>rmax[name]['abs_upper']:rmax[name]={'abs_upper':hi,'segment':n,'interval':pair(value)}
        maxF=max(abs(float(states[n,4])),abs(float(states[n+1,4])))
        Lg=helper.g_derivative_upper(maxF,c);max_Lg=max(max_Lg,Lg)
        mid_budget=h*(TWO*(absi(ru1)+absi(ru2))+absi(rv1)+absi(rv2)+THREE*absi(rF))
        lin1=CD*Dv1+CO*Dv2+KD*Du1+KO*Du2;lin2=CD*Dv2+CO*Dv1+KD*Du2+KO*Du1+DF
        variation=H4*(TWO*(absi(Dv1)+absi(Dv2))+absi(lin1)+absi(lin2)+input_variation+THREE*(absi(Dv2)+I.point(Lg)*absi(DF)))
        step=mid_budget+variation
        if step.hi<0:raise ArithmeticError('Negative budget upper endpoint')
        Ihi=up(Ihi+step.hi);max_step=max(max_step,step.hi)
        partial['mid']=up(partial['mid']+mid_budget.hi);partial['variation']=up(partial['variation']+variation.hi);partial['total']=up(partial['total']+step.hi)
        if n+1 in [N,J]:
            blocks.append({'first_segment':first,'last_segment':n,'n_segments':n+1-first,'before_or_after_input_stop':'input_active' if n<N else 'post_input_stop',
                'midpoint_budget_upper':partial['mid'],'variation_budget_upper':partial['variation'],'block_total_upper':partial['total'],'prefix_I_upper':Ihi,
                **{'max_abs_upper_'+name:hi for name,hi in brmax.items()},'global_Lipschitz_term_retained':True})
            first=n+1;partial={'mid':0.,'variation':0.,'total':0.};brmax={name:0. for name in rnames}
    stored_abs=abs(signed_value);lower=down(stored_abs-Ihi);threshold=I.rational(Fraction(241,100));gap=down(lower-threshold.hi)
    candidate={'status':'candidate_pending_new_math_implementation_and_U_fulltime_review','I_J_upper_candidate':Ihi,'exact_stored_abs_u1_J':stored_abs,
        'D_fixed_witness_lower_candidate':lower,'U_candidate_threshold_exact':'241/100','U_threshold_outward_interval':pair(threshold),
        'gap_lower_candidate_against_U_threshold_hi':gap,'witness_candidate_exceeds_U_candidate':lower>threshold.hi,
        'not_true_D_peak_claim':True,'not_D_tail_end_claim':True,'not_proof_without_U_R020_and_reviews':True}
    parameters={'N':N,'J':J,'true_h_interval':pair(h),'true_T_interval':pair(N*h),'true_witness_time_interval':pair(J*h),
        'PI_interval':pair(helper.PI),'sqrt2_input_omega_interval':pair(omega),'sqrt3_interval':pair(sqrt3),
        'Kdiag':pair(KD),'Koff':pair(KO),'Cdiag':pair(CD),'Coff':pair(CO),'kappa':pair(kappa),'c':pair(c),
        'alpha_exact':'3/10','q_exact':'10/3','B':[0,1],'residual_norm_weights':[2,1,3],'S_K_exact':'2/3','output_error_coefficient_conservatively_used':1}
    checks={'fixed_index_and_signed_value_identity_gate_passed':True,'all_initial_stored_states_exact_zero':True,
        'only_D_state_columns_and_exact_rebuilt_grid_used':True,'all16529_prefix_segments_outward_evaluated':sum(b['n_segments'] for b in blocks)==J,
        'new_K_C_B_kappa_and_2_1_3_weights_used':True,'global_2h_sqrt2_input_term_retained_after_T':True,'upward_sum_every_segment':True,
        'all_source_and_protocol_SHA_unchanged':all(sha(x['path'])==x['sha256'] for x in refs.values()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below480seconds':time.perf_counter()-started<480};assert all(checks.values())
    with (H/'prefix_outward_blocks.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(blocks[0]));w.writeheader();w.writerows(blocks)
    out={'evidence_id':'M-EXP-R017','status':'candidate_only_pending_protocol_and_full_implementation_independent_reviews','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-started,'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'source_refs':refs,
        'actual_loaded_helper_file':str(Path(helper.__file__).resolve()),'actual_loaded_helper_sha256':sha(helper.__file__),
        'helper_root_degree_contract':'Explicitsqrt builtinint2, g/Lg internalcuberoot builtinint3; v002 guarded APIs; helper root-designated reviewed, no new helper certification asserted',
        'identity_gate':identity,'model_and_time_intervals':parameters,'candidate_witness_bounds':candidate,'residual_upper_diagnostics':rmax,
        'maximum_Lg_upper':max_Lg,'maximum_step_budget_upper':max_step,'blocks':blocks,'checks':checks,
        'contracts':{'trajectory':'Exact binary64 states from fixedcache, PL onrebuilttruegrid; nointernalODEFm oroldbudgets',
            'input':'sin_pi_ratio(20n+10,N) beforeN,exact0 after; 2h*omega globalLipschitzvariation retained allJ segments',
            'model':'ExactM/K/kappa/c and intervalsqrt3C; B=e2; nolegacy1.001or7<kappa<8 assumption',
            'residual':'Fullru/rv/rF plusallh/h4terms inI; g/Lg byfrozenhelperv002; noenergybalance substitute',
            'sum_and_witness':'Everysegmentup(prev+stephi); lowerdown(absstored-Ihi), exactrational2.41 upperendpoint forcomparison',
            'review_gate':'Newprotocolmath and implementation audit plusUfulltimeboundR020/independentreview required. Candidate notproof/engineeringresult.'}}
    lines=['# M-EXP-R017：新增器件的固定见证前缀包络候选','',
        '状态：candidate，待新协议数学与完整实现独审；U的候选全时上界2.41尚待R020及独审。当前程序成功或候选不等式为真均不提前颁发证明，也不作工程结果。', '',
        '首先精确核对R016小CSV、JSON与缓存D_N16384：首个u1绝对峰索引为固定J=16529，有符号节点值及缓存时间标签完全相同，未改选其他点。时间标签仅核身份；包络中真h=20pi/(sqrt2*N)，不拿缓存t列当真实网格。只读u/v/F，不用W/Db/Dd作误差或能量证据。', '',
        f"精确存储u1_J={signed_value:.17g}，真见证时间候选区间={pair(J*h)}。前J段I_J候选上端={Ihi:.17g}，D固定见证幅值候选下端={lower:.17g}。", '',
        f"只与待审U候选241/100比较，其向外区间={pair(threshold)}；差的候选下端={gap:.17g}，候选比较为{lower>threshold.hi}。这不宣布t*是真实D峰或尾段结束；只在U全时界及误差框架/实现都被独审接纳后才能组合推论。", '',
        '模型重新构造为M=I、Kdiag=2/Koff=−1、Cdiag=(1+sqrt3)/20/Coff=(1−sqrt3)/20、B=(0,1)、kappa=8、c=10，alpha=3/10。每段完整ru/rv/rF从精确存储端点的算术中点及差重建，norm权用2/1/3，未抄旧例1.001、kappa或时间常数。', '',
        '输入中点相位精确为pi*(20n+10)/N，由helper.sin_pi_ratio包络；n>=N输入0，但协议规定的全局2h*sqrt2变化项仍在停载后145段保留。g与Lg、h/h4项及总前缀逐层向外，每段up(prev_hi+step_hi)。见证下界用down(absstored-I_J)，阈值用精确有理241/100的上端作保守比较。未用旧浮点预算、中点理想零残差或能量余额代替状态误差。', '',
        '参数/时间包络、每层机器合同、残差上端极值与分段位置、两块预算、源SHA及实际加载helperv002路径/SHA见小JSON。helper仅builtin int2/3计算域；继承其完整机器合同，不把有限硬件探针认成全历史模式证明。', '',
        '无新ODE、输入/参数/网格/见证搜索、完整数组输出或新缓存。NPZ源留本地，旧结果不改。该两接地质量耦合算例不是普通二层剪切结构或真实ETABS，无创新性/工程因果主张。冻结后停止，由主控安排独审。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={n:sha(H/n) for n in ['prefix_outward_blocks.csv','report.md']}
    (H/'summary_r017.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'run_record_r017.json').write_text(json.dumps({'actual_command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,
        'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],'python':sys.version,'numpy_decoder':np.__version__,
        'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r017.json'),'helper_sha256':sha(helper.__file__),
        'IEEE_contract':{'radix':sys.float_info.radix,'mant_dig':sys.float_info.mant_dig,'max_exp':sys.float_info.max_exp,'rounds':sys.float_info.rounds},'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'elapsed_seconds':out['elapsed_seconds'],'identity_gate':identity,'candidate_witness_bounds':candidate,'checks':checks},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        failure={'evidence_id':'M-EXP-R017','status':'failed_fixed_witness_candidate_no_reselection','failed_utc':datetime.now(timezone.utc).isoformat(),
            'error':repr(exc),'context':CONTEXT,'traceback':traceback.format_exc()}
        with (H/'failure_r017.json').open('x',encoding='utf-8') as f:json.dump(failure,f,ensure_ascii=False,indent=2)
        raise
