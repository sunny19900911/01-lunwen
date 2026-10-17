"""Independent small-file/tiny scalar algebra review; never execute target or access NPZ."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime,timezone,timedelta
import csv,hashlib,json,math
H=Path(__file__).resolve().parent
S=H.parents[2]/'experiments/maxwell-session004/R023-forward-midpoint-synthetic'
def read(n):return json.loads((S/n).read_text(encoding='utf-8'))
def sha(p):
    p=Path(p);assert p.suffix.lower()!='.npz'
    return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,p,d=None):checks.append({'name':n,'pass':bool(p),'detail':d})
rules=json.loads((H/'input-rules-R024.json').read_text(encoding='utf-8'))
for e in rules['inputs']:
    p=Path(e['path']);ck('input:'+p.parent.name+'/'+p.name,sha(p)==e['sha256'] and p.stat().st_size==e['bytes'])
for e in read('delivery_manifest.json')['files']:
    p=Path(e['path']);ck('manifest:'+p.name,sha(p)==e['sha256'] and p.stat().st_size==e['bytes'])
for e in read('pre_run_freeze.json')['files']:ck('prerun:'+Path(e['path']).name,sha(e['path'])==e['sha256'])
ps,pf,ss=read('prediction_summary.json'),read('prediction_freeze.json'),read('summary.json')
ck('predictions_unchanged',ps['predictions']==ss['predictions'])
for k,n in [('code_sha256','forward_midpoint.py'),('protocol_sha256','protocol.json'),('prediction_summary_sha256','prediction_summary.json'),('snapshots_sha256','prediction_fixed_snapshots.csv'),('residual_blocks_sha256','six_block_increment_residuals.csv')]:ck('freeze:'+k,pf[k]==sha(S/n))
ev=read('reference_read_order.json')['events'];names=[x['event'] for x in ev]
ck('event_order',names.index('both_prediction_summaries_snapshots_and_hashes_persisted')<names.index('reference_hash_access_start')<names.index('D_N16384_reference_read_complete'))
ck('clock_nondecreasing',all(x['monotonic_ns']<=y['monotonic_ns'] for x,y in zip(ev,ev[1:])))
ck('reference_flags',not ps['reference_accessed'] and pf['reference_not_accessed'] and pf['both_predictions_complete'] and ss['model_input_only_predictions'])
def rows(n):
    with (S/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
pr,cr,br=rows('prediction_fixed_snapshots.csv'),rows('comparison_fixed_snapshots.csv'),rows('six_block_increment_residuals.csv')
ck('row_counts',len(pr)==len(cr)==7 and len(br)==12)
for p,c in zip(pr,cr):
    N,n=int(p['N']),int(p['node']);tag=f'{N}:{n}'
    ck('snapshot_unchanged:'+tag,all(c[k]==v for k,v in p.items()))
    ck('refnode:'+tag,int(c['reference_node'])==n*(2 if N==8192 else 1))
    for k in ['u1','u2','F']:ck('error:'+tag+':'+k,float(c[k+'_error'])==float(c[k])-float(c['reference_'+k]))
    u1,u2,v1,v2,F=(float(p[k]) for k in ['u1','u2','v1','v2','F'])
    E=u1*u1+u2*u2-u1*u2+.5*(v1*v1+v2*v2)+F*F/16
    ck('energy:'+tag,abs(E-float(p['E']))<1e-14)
    bal=E+float(p['physical_background_dissipation'])+float(p['physical_device_dissipation'])-float(p['input_work'])
    ck('balance:'+tag,abs(bal-float(p['actual_cumulative_balance']))<3e-14)
scalar=[];exact=[]
cd,co=(1+math.sqrt(3))/20,(1-math.sqrt(3))/20
for r in ps['predictions']:
    N,h=r['N'],r['h'];half=h/2
    ck('memory_SHA_record_only:'+str(N),r['memory_trajectory_sha256']==pf['memory_trajectory_sha256'][str(N)])
    ck('indices:'+str(N),[int(p['node']) for p in pr if int(p['N'])==N]==r['fixed_indices'])
    ck('midpoint_semantics:'+str(N),r['dissipation_midpoints']=='actual endpoint averages' and not r['BE_numerical_dissipation_formula_used'])
    A=1+half*cd+2*half*half;B=half*co-half*half
    d=.5*(1/(A+B)+1/(A-B));o=.5*(1/(A+B)-1/(A-B));ar=.125+half*half*d
    ck('inverse_spectral:'+str(N),abs(d-r['S_h'])<3e-16 and abs(o-r['A_inverse'][0][1])<3e-16 and abs(ar-r['a_F'])<3e-16 and half==r['a_half'])
    blocks=[b for b in br if int(b['N'])==N]
    ck('six_blocks:'+str(N),[int(b['block_T']) for b in blocks]==list(range(1,7)))
    for k,v in r['complete_endpoint_increment_residuals'].items():
        ck('block_residual_max:'+str(N)+':'+k,max(float(b[k]) for b in blocks)==v['max_abs'] and abs(v['signed_at_max'])==v['max_abs'] and 0<v['right_node_at_max']<=r['steps'] and 0<=v['nonzero_count']<=r['steps'])
    for j,k in enumerate(['kinematic_residual_work_sum','momentum_residual_work_sum','constitutive_residual_work_sum']):
        ck('block_work_sum:'+str(N)+':'+k,math.isclose(sum(float(b[k]) for b in blocks),r['signed_residual_work_sums'][j],rel_tol=2e-12,abs_tol=1e-24))
    ck('balance_defect:'+str(N),r['actual_terminal_balance']-sum(r['signed_residual_work_sums'])==r['terminal_balance_minus_summed_residual_work'])
    ck('root_vs_const_record:'+str(N),r['max_abs_half_constitutive_residual_minus_scalar_root_residual']<1e-14)
    for b in [-.7,0.,.7]:
        lo,hi=sorted((0.,b/ar));initial=(lo,hi)
        def fun(x):return ar*x+half*math.copysign((abs(x)/10)**(10/3),x)-b
        for _ in range(60):
            x=(lo+hi)/2
            if fun(x)>0:hi=x
            else:lo=x
        x=(lo+hi)/2;res=fun(x)
        scalar.append({'N':N,'b':b,'root':x,'residual':res})
        ck('isolated_scalar_root:'+str(N)+':'+str(b),fun(initial[0])<=0<=fun(initial[1]) and initial[0]<=x<=initial[1] and abs(res)<=1e-11*max(1,abs(b)))
    # Exact rational evaluation at arbitrary endpoints, not an ODE step.
    # Fbar=10 -> g(Fbar)=1 exactly; C uses exact rational values of stored cd/co.
    hh=Q(h);C0,C1=Q(cd),Q(co);u0=[Q(1,10),Q(-1,5)];u1=[Q(3,25),Q(-201,1000)]
    v0=[Q(3,10),Q(-2,5)];v1=[Q(29,100),Q(-41,100)];F0,F1=Q(7),Q(13);fm=Q(1,3)
    ub=[(x+y)/2 for x,y in zip(u0,u1)];vb=[(x+y)/2 for x,y in zip(v0,v1)];Fb=(F0+F1)/2
    Ku=[2*ub[0]-ub[1],-ub[0]+2*ub[1]]
    ru=[u1[i]-u0[i]-hh*vb[i] for i in range(2)]
    rp=[v1[i]-v0[i]+hh*(C0*vb[i]+C1*vb[1-i]+Ku[i]+(Fb if i==1 else 0)-fm) for i in range(2)]
    rF=(F1-F0)/8-hh*(vb[1]-1)
    def energy(u,v,F):return u[0]**2+u[1]**2-u[0]*u[1]+sum(x*x for x in v)/2+F*F/16
    balance=energy(u1,v1,F1)-energy(u0,v0,F0)+hh*(C0*sum(x*x for x in vb)+2*C1*vb[0]*vb[1]+Fb)-hh*fm*sum(vb)
    power=sum(Ku[i]*ru[i]+vb[i]*rp[i] for i in range(2))+Fb*rF
    ck('exact_endpoint_energy_identity:'+str(N),balance==power)
    # Independently check the algebraic factor two with arbitrary internal state.
    aa=hh/2;Sh=Q(d);zm=Q(2,7);Fm=Q(10);Fold=Q(7);vbar=zm-aa*Sh*Fm
    root=(Q(1,8)+aa*aa*Sh)*Fm+aa-(Fold/8+aa*zm)
    rf=(2*Fm-2*Fold)/8-hh*(vbar-1)
    ck('exact_root_half_rF:'+str(N),root==rf/2)
    exact.append({'N':N,'arbitrary_endpoint_identity_exact':balance==power,'root_equals_half_rF_exact':root==rf/2})
ck('J_not_faked',ss['J_fine_index']==16529 and ss['J_coarse_index'] is None and ss['J_coarse_grid_coordinate']==8264.5)
be=json.loads((S.parent/'R022-forward-BE-synthetic/summary.json').read_text(encoding='utf-8'))
ck('old_BE_fail_retained',be['fine_u1_u2_maxerror_below_point1']=={'u1':False,'u2':True} and not ss['BE_trajectory_pointwise_comparison_performed'])
for label,group in ss['BE_small_summary_comparison_only'].items():
    for name,metrics in group.items():
        for metric,e in metrics.items():ck('BE_stats_only:'+label+':'+name+':'+metric,e['BE']==be['comparison'][label][name][metric] and e['midpoint']==ss['comparison'][label][name][metric] and e['midpoint_less_than_BE']==(e['midpoint']<e['BE']))
for name in ['u1','u2','F']:
    for metric in ['max_abs_error','RMS_error']:
        coarse=ss['comparison']['coarse_vs_reference_on_49153_common_nodes'][name][metric];fine=ss['comparison']['fine_vs_reference_on_49153_common_nodes'][name][metric]
        ck('improvement:'+name+':'+metric,ss['coarse_to_fine_improvement_on_common_grid'][name][metric]==(fine<coarse))
for name in ['u1','u2']:ck('gate:'+name,ss['fine_u1_u2_maxerror_below_point1'][name]==(ss['comparison']['fine_vs_reference_on_98305_all_nodes'][name]['max_abs_error']<.1))
result={'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'scope':'only specified small files, six isolated scalar roots, two 2x2 inverse checks, two arbitrary-endpoint rational energy identities and two factor-two identities; target never executed','checks':checks,'check_count':len(checks),'failed_checks':[x for x in checks if not x['pass']],'scalar_challenges':scalar,'exact_algebra_challenges':exact,'alltime_max_RMS_independently_recomputed':False,'NPZ_array_identity_reverified':False}
(H/'small-challenges-R024.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'failed':result['failed_checks'],'scalar_max_abs_residual':max(abs(x['residual']) for x in scalar)},ensure_ascii=False))
