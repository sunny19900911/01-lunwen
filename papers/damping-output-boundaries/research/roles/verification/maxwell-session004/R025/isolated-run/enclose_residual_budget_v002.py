"""Candidate outward residual enclosure on frozen endpoints; no ODE rerun."""
from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time,traceback
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='2501ac448057cd453e562ca86af2397cfa5397a1b9bda8f9d1009a4b43ceefbd'
CONTEXT={}
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    started=time.perf_counter();assert not (H/'summary_r015.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs']
    assert all(sha(x['path'])==x['sha256'] for x in refs.values())
    sys.path.insert(0,str(Path(refs['helper']['path']).parent))
    import outward_float_v002 as helper
    assert Path(helper.__file__).resolve()==Path(refs['helper']['path']).resolve()
    degree_rejections=0
    for bad in [2.0,3.0,Fraction(2,1),'2',True]:
        for func,arg in [(helper.root_endpoint,.1),(helper.root,helper.I.point(.1))]:
            try:func(arg,bad)
            except TypeError:degree_rejections+=1
            else:raise ArithmeticError('v002 non-builtin-int root degree unexpectedly accepted')
    assert degree_rejections==10
    I=helper.I;up=helper.up;down=helper.down;ZERO=I.point(0);ONE=I.point(1);TWO=I.point(2);THREE=I.point(3);HALF=I.point(.5)
    def absi(x):
        if x.lo>=0:return x
        if x.hi<=0:return I(-x.hi,-x.lo)
        return I(0,max(-x.lo,x.hi))
    def pair(x):return [x.lo,x.hi]
    N=16384;steps=6*N;h=I.rational(Fraction(20,N))*helper.PI;H4=h*I.rational(Fraction(1,4));invh=ONE/h
    KD=I.rational(Fraction(1001,1000));KO=I.rational(Fraction(-1,1000))
    w=helper.root(I.rational(Fraction(501,500)),2);CD=(ONE+w)/20;CO=(ONE-w)/20
    rlo=Fraction('1.7151372034229');rhi=Fraction('1.7151372034230')
    cubic=lambda x:x**3-3*x+Fraction(1,10)
    clo,chi=cubic(rlo),cubic(rhi);derivative_lower=3*rlo*rlo-3
    assert clo<0<chi and derivative_lower>0
    r=I(I.rational(rlo).lo,I.rational(rhi).hi);kappa=3*(r**2)-ONE-(r**3)/10;c=kappa/(r**3)
    assert 7<kappa.lo<=kappa.hi<8 and c.lo>0
    invkh=ONE/(kappa*h)
    with np.load(refs['endpoint_cache']['path'],allow_pickle=False) as z:
        # Only this array is decoded. Stored t and old diagnostics are unused.
        endpoints=z['endpoints'];assert endpoints.dtype==np.float64 and endpoints.shape==(98305,6)
        states=endpoints[:,1:6].copy()
    assert np.isfinite(states).all() and np.all(states[0]==0.)
    max_u1=float(max(abs(states[:,0])));abs_u2_T=abs(float(states[N,1]))
    prefix_hi=None;total_hi=0.;blocks=[];block={'mid':0.,'variation':0.,'total':0.};max_step=0.;max_Lg=0.
    rnames=['r_u1','r_u2','r_v1','r_v2','r_F'];residual_max={k:{'abs_upper':0.,'segment':None,'enclosure':None} for k in rnames}
    block_rmax={k:0. for k in rnames};last_block_start=0
    for n in range(steps):
        if n%4096==0:
            CONTEXT.update({'last_segment':n,'total_upper_so_far':total_hi,'elapsed_seconds':time.perf_counter()-started})
            print(json.dumps({'stage':'outward_segments','n':n,'I_upper_so_far':total_hi,'elapsed_s':time.perf_counter()-started}),flush=True)
            if time.perf_counter()-started>600:raise TimeoutError('Frozen interval runtime600s exceeded')
        left=[I.point(float(x)) for x in states[n]];right=[I.point(float(x)) for x in states[n+1]]
        Du1,Du2=right[0]-left[0],right[1]-left[1];Dv1,Dv2=right[2]-left[2],right[3]-left[3];DF=right[4]-left[4]
        um1,um2=(left[0]+right[0])*HALF,(left[1]+right[1])*HALF
        vm1,vm2=(left[2]+right[2])*HALF,(left[3]+right[3])*HALF;Fm=(left[4]+right[4])*HALF
        forcing=helper.sin_pi_ratio(20*n+10,N) if n<N else ZERO
        ru1,ru2=Du1*invh-vm1,Du2*invh-vm2
        rv1=Dv1*invh+CD*vm1+CO*vm2+KD*um1+KO*um2+Fm-forcing
        rv2=Dv2*invh+CD*vm2+CO*vm1+KD*um2+KO*um1-forcing
        rF=DF*invkh-vm1+helper.g_power_10_3(Fm,c)
        residuals=[ru1,ru2,rv1,rv2,rF]
        for name,value in zip(rnames,residuals):
            hi=value.abs_upper();block_rmax[name]=max(block_rmax[name],hi)
            if hi>residual_max[name]['abs_upper']:residual_max[name]={'abs_upper':hi,'segment':n,'enclosure':pair(value)}
        Fmax=max(abs(float(states[n,4])),abs(float(states[n+1,4])))
        Lg=helper.g_derivative_upper(Fmax,c);max_Lg=max(max_Lg,Lg)
        mid_budget=h*(KD*(absi(ru1)+absi(ru2))+absi(rv1)+absi(rv2)+THREE*absi(rF))
        lin1=CD*Dv1+CO*Dv2+KD*Du1+KO*Du2+DF;lin2=CD*Dv2+CO*Dv1+KD*Du2+KO*Du1
        input_variation=TWO*h if n<N else ZERO
        var_budget=H4*(KD*(absi(Dv1)+absi(Dv2))+absi(lin1)+absi(lin2)+input_variation+THREE*(absi(Dv1)+I.point(Lg)*absi(DF)))
        segment_budget=mid_budget+var_budget
        if segment_budget.hi<0:raise ArithmeticError('Negative budget upper endpoint')
        total_hi=up(total_hi+segment_budget.hi);max_step=max(max_step,segment_budget.hi)
        block['mid']=up(block['mid']+mid_budget.hi);block['variation']=up(block['variation']+var_budget.hi);block['total']=up(block['total']+segment_budget.hi)
        if n+1==N:prefix_hi=total_hi
        if (n+1)%N==0:
            blocks.append({'block_T_index':(n+1)//N,'first_segment':last_block_start,'last_segment':n,'n_segments':N,
                'midpoint_budget_sum_upper':block['mid'],'variation_budget_sum_upper':block['variation'],'block_budget_sum_upper':block['total'],
                'global_I_upper_at_block_end':total_hi,**{'max_abs_upper_'+k:v for k,v in block_rmax.items()}})
            last_block_start=n+1;block={'mid':0.,'variation':0.,'total':0.};block_rmax={k:0. for k in rnames}
    u1,u2,v1,v2,F=[I.point(float(x)) for x in states[-1]]
    Ekin=(v1**2+v2**2)/2;Ephysical=(KD*(u1**2+u2**2)+2*KO*u1*u2)/2;Espring=(F**2)/(2*kappa);E=Ekin+Ephysical+Espring
    assert E.hi>0 and E.lo>0
    sqrt_tail=helper.root(TWO*I.point(E.hi),2)
    Uearly=up(max_u1+total_hi);Utail=up(sqrt_tail.hi+total_hi);Lfixed=down(abs_u2_T-prefix_hi);gap=down(Lfixed-max(Uearly,Utail))
    candidate={'status':'candidate_only_pending_math_helper_implementation_reviews','I_prefix_T_upper_candidate':prefix_hi,'I_total_6T_upper_candidate':total_hi,
        'exact_stored_maxnode_abs_uh1':max_u1,'exact_stored_abs_uh2_N':abs_u2_T,'terminal_E_interval_candidate':pair(E),'tail_sqrt_interval_candidate':pair(sqrt_tail),
        'early_upper_candidate':Uearly,'tail_upper_candidate':Utail,'fixed_T_lower_candidate':Lfixed,'gap_lower_candidate':gap,'strict_gap_comparison':gap>0,
        'not_proof_until_three_reviews':True}
    params={'N':N,'n_segments':steps,'h_interval':pair(h),'PI_interval':pair(helper.PI),'r_rational_lower':str(rlo),'r_rational_upper':str(rhi),
        'cubic_lower_exact':str(clo),'cubic_upper_exact':str(chi),'cubic_derivative_lower_exact':str(derivative_lower),
        'r_interval':pair(r),'kappa_interval':pair(kappa),'c_interval':pair(c),'Kdiag_interval':pair(KD),'Koff_interval':pair(KO),
        'sqrt501over500_interval':pair(w),'Cdiag_interval':pair(CD),'Coff_interval':pair(CO)}
    checks={'only_endpoints_decoded_no_cached_t_or_old_diagnostics_used':True,'all_initial_stored_states_exact_zero':True,
        'exact_Fraction_cubic_signs_and_monotonicity_passed':True,'kappa_enclosed_strictly_between7and8':True,
        'all98304_residual_segments_outward_evaluated':len(blocks)==6,'global_sum_every_step_upward':True,
        'all_source_and_own_protocol_SHA_unchanged':all(sha(x['path'])==x['sha256'] for x in refs.values()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below600seconds':time.perf_counter()-started<600};assert all(checks.values())
    contracts={'binary64':'helper round-to-nearest IEEEbinary64 assertion; finite basic operations widened bynextafter; external helperreview pending',
        'trajectory':'np.load allow_pickleFalse, float64 u/v/F promoted to exactbinaryfloat points; cachet ignored, no oldFm/residual used',
        'model':'rationalK; w exactsqrt enclosure; exactcubic signs/derivative plusrinterval; kappa/c interval expressions include paramdependence',
        'pi_grid_sin':'helperMachin alternating rationalPI bounds; h=PI*20/N; exactintegerphase sin_pi_ratio for n<N, exactzero thereafter',
        'g_and_Lg':'helper signed10/3 power via exactFraction-certified cube-root endpoints; endpointmaxF exact; helperg_derivative_upper',
        'midpoint':'true arithmetic midpoint of exact storedendpoint floats enclosed inI; no relianceon internal root orroundedmethodmidpoint',
        'residual_budget':'Every ru/rv/rF and h/h4norm term inI; abs spanszero handledwithoutdiscard; never preset residuals to0',
        'sum':'total_hi=up(previous_hi+segment_budget.hi) everysegment; same prefixatN, no floatmath.fsum substitute',
        'terminal':'trueK/kappa interval quadraticenergy, candidateEupper .hi; root(2Eupper,2) exactendpoint verification, candidate comparisons up/down',
        'review_gate':'MathR024, helperR016 and independent implementation audit allrequired; thisrun doesnot declare theorem/fulltailproof.'}
    out={'evidence_id':'M-EXP-R015','status':'candidate_outward_residual_enclosure_pending_three_reviews','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-started,'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'source_refs':refs,
        'candidate_bounds':candidate,'parameter_enclosures':params,'residual_enclosure_diagnostics':residual_max,'maximum_Lg_upper':max_Lg,'maximum_segment_budget_upper':max_step,
        'terminal_energy_component_intervals':{'kinetic':pair(Ekin),'physical_elastic':pair(Ephysical),'device_spring':pair(Espring),'total':pair(E)},
        'contracts':contracts,'checks':checks,'no_new_ODE_arrays_or_cache_files':True}
    write('six_block_outward_budget.csv',blocks)
    lines=['# M-EXP-R015：向外残差包络候选实现','',
        '状态：candidate，等待数学、helper及实现三项独审。程序完成不等于证明；下列带方向的计算仍依赖helper和实现合同审核，不提前宣称全尾/全峰认证。', '',
        '只读已冻R014 NPZ的endpoints，取u/v/F精确binary64端点。未使用其时间列、旧分段float残差、Lg或内部Fm；无ODE重算、改步数或改参数。真实网格重建为h=20pi/16384的包络，中点输入用精确整数相位sin(pi*(20n+10)/N)，停载后为0。', '',
        f"I_prefix(T)候选上端={prefix_hi:.17g}，I_total(6T)候选上端={total_hi:.17g}；精确存储maxnode|uh1|={max_u1:.17g}、固定T的|uh2_N|={abs_u2_T:.17g}。", '',
        f"early候选上端={Uearly:.17g}，tail候选上端={Utail:.17g}，固定T候选下端={Lfixed:.17g}；gap候选下端={gap:.17g}，strictgap比较={gap>0}。该布尔量仅为待审候选比较。", '',
        f"末E包络候选=[{E.lo:.17g},{E.hi:.17g}]，sqrt(2Eupper)包络候选={pair(sqrt_tail)}，完整动能/主体弹性/器件储能包络见JSON。", '',
        'K用1001/1000与−1/1000，w用sqrt(501/500)，Cdiag=(1+w)/20、Coff=(1−w)/20。先以Fraction验证给定r有理括区的三次多项式异号及区间导数正，再包络kappa/c并核7<kappa<8。pi、sin、10/3幂、导数上端、平方根均由冻结helper提供对应显式合同；未信任libm直接返回上界。', '',
        '各段Du/Dv/DF和精确端点算术中点在I中重建，三残差不置零。h/h4全部预算项向外计算，每一步以up(prev_hi+step_hi)累加；六块小表保留中点/变化预算及残差最大上端，未以能量余额替换状态误差。参数、网格输入、根/幂、总和与末能的逐层合同在JSON。', '',
        '来源SHA前后核不变，helper只导入未修改，旧缓存只读。本项未新增完整数组或缓存、图、依赖、原表/ETABS调用或Git修改。候选数学成立、helper合同成立、实现无误仍是分开的门；全部完成后只能由主控按独审范围决定是否认证这个无量纲合成例，不能外推实际建筑或器件参数。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={n:sha(H/n) for n in ['six_block_outward_budget.csv','report.md']}
    (H/'summary_r015.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    run={'actual_command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],
        'python':sys.version,'numpy_decoder':np.__version__,'IEEE_contract':{'radix':sys.float_info.radix,'mant_dig':sys.float_info.mant_dig,'max_exp':sys.float_info.max_exp,'rounds':sys.float_info.rounds},
        'helper_sha256':sha(refs['helper']['path']),'actual_loaded_helper_file':str(Path(helper.__file__).resolve()),'degree_guard_rejections_checked':degree_rejections,'degree_contract':'All successful root calls pass v002 builtinint2/3 guards; no float/Fraction/string/bool degree in residual chain','code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r015.json'),'checks':checks}
    (H/'run_record_r015.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'elapsed_seconds':out['elapsed_seconds'],'candidate_bounds':candidate,'checks':checks},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        failure={'evidence_id':'M-EXP-R015','status':'failed_candidate_outward_run_no_retry','failed_utc':datetime.now(timezone.utc).isoformat(),'error':repr(exc),'context':CONTEXT,'traceback':traceback.format_exc()}
        with (H/'failure_r015.json').open('x',encoding='utf-8') as f:json.dump(failure,f,ensure_ascii=False,indent=2)
        raise
