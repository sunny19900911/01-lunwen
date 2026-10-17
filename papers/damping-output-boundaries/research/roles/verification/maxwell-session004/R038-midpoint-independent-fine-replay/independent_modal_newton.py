"""One frozen fine-grid modal/Newton replay; author code is never opened/imported."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,hashlib,json,math,sys,time,traceback
import numpy as np
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R023-forward-midpoint-synthetic'
ROOTPROTO=ROOT/'research/sessions/20261017-2109/independent-midpoint-fine-replay-protocol-v001.md'
CONTEXT={'phase':'preflight'}
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(name,o):(HERE/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def csvwrite(name,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    start=time.perf_counter();assert not (HERE/'prediction_freeze.json').exists()
    assert record(ROOTPROTO)['sha256']=='0a294150fc9ca93be9dec70d798717e9f5dd35ce351d9145b3d3c2b00f44b361'
    ap=read(AUTHOR/'protocol.json')  # Allowed path/identity only; no author states/results.
    N=16384;steps=6*N;rt2=math.sqrt(2);rt3=math.sqrt(3);T=20*math.pi/rt2;h=T/N;a=h/2
    scale=1/rt2;beta=(scale,-scale);lam=(1.,3.);damp=(.1,.1*rt3)
    den=tuple(1+a*d+a*a*k for d,k in zip(damp,lam));S=sum(b*b/dd for b,dd in zip(beta,den));af=1/8+a*a*S
    ownprotocol={'N':N,'steps':steps,'initial':'all zero','h':h,'T':T,'a':a,'model':'fixed C027 D physical K eigenvalues1/3, C=.1sqrtK, B=e2,kappa8,c10,alpha3/10',
       'method':'mass-normalized symmetric/antisymmetric modal elimination; shared force; nonnegative magnitude safeguarded Newton',
       'root_tolerance':1e-13,'root_max_iterations':80,'statistics_and_snapshot_absolute_difference_gate':1e-6,'displacement_gate':.1,
       'deadline':'2026-10-18T04:05:02+08:00','source_root_protocol':record(ROOTPROTO),'author_protocol_path_identity':record(AUTHOR/'protocol.json'),
       'reference_declared_not_read':{'path':ap['reference_path'],'sha256':ap['reference_sha256']},'no_other_grid_or_tuning':True}
    write('run_protocol.json',ownprotocol)
    pre={'at':now(),'argv':[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve())],'sources':[record(ROOTPROTO),record(AUTHOR/'protocol.json'),record(Path(__file__)),record(HERE/'run_protocol.json')],
       'reference_or_author_summary_snapshots_not_opened':True,'python':sys.version,'numpy':np.__version__}
    write('pre_run_freeze.json',pre);events=[{'event':'code_protocol_frozen_before_prediction','at':now()}]
    context_max={};maxroot=0.;maxiterations=0;fallbacks=0
    def g(x):return math.copysign((abs(x)/10)**(10/3),x) if x else 0.
    def root(b,n):
        nonlocal maxroot,maxiterations,fallbacks
        target=abs(b);tol=1e-13*max(1.,target)
        if target==0:return 0.
        lo=0.;hi=target/af;x=hi
        for it in range(1,81):
            r=af*x+a*(x/10)**(10/3)-target
            if abs(r)<=tol:
                maxroot=max(maxroot,abs(r)/max(1.,target));maxiterations=max(maxiterations,it)
                return math.copysign(x,b)
            if r>0:hi=x
            else:lo=x
            derivative=af+(a/3)*(x/10)**(7/3)
            candidate=x-r/derivative
            if not lo<candidate<hi or candidate==x:
                candidate=(lo+hi)/2;fallbacks+=1
            if candidate==x:raise ArithmeticError(f'Newton/bracket stagnation above residual gate at step {n}')
            x=candidate
        raise ArithmeticError(f'80-iteration fixed root gate failure at step {n}')
    prediction=np.zeros((steps+1,6),dtype='<f8');q0=q1=p0=p1=force=0.
    Cd=(1+rt3)/20;Co=(1-rt3)/20;Eprevious=0.;W=Db=Dd=0.;maxbalance=maxcum=maxidentity=0.
    maxres=[0.]*5;maxwork=[0.]*3;snapshots=[];indices={0,N,16529,steps}
    def energy(row):
        _,u1,u2,v1,v2,F=row;return .5*(2*u1*u1+2*u2*u2-2*u1*u2+v1*v1+v2*v2+F*F/8)
    for n in range(steps):
        if n%4096==0:
            CONTEXT.update({'phase':'prediction_only','node':n,'elapsed_seconds':time.perf_counter()-start})
            if now()>ownprotocol['deadline'] or time.perf_counter()-start>660:raise TimeoutError('Frozen task/runtime limit')
        old=prediction[n];forcing=math.sin(rt2*((n+.5)*h)) if n<N else 0.
        z0=(p0+a*(rt2*forcing-lam[0]*q0))/den[0];z1=(p1-a*lam[1]*q1)/den[1]
        b=force/8+a*(beta[0]*z0+beta[1]*z1);Fm=root(b,n)
        pm0=z0-a*beta[0]*Fm/den[0];pm1=z1-a*beta[1]*Fm/den[1]
        q0+=h*pm0;q1+=h*pm1;p0=2*pm0-p0;p1=2*pm1-p1;force=2*Fm-force
        prediction[n+1]=[(n+1)*h,scale*(q0+q1),scale*(q0-q1),scale*(p0+p1),scale*(p0-p1),force]
        new=prediction[n+1]
        u1,u2,v1,v2,Fbar=[float((x+y)/2) for x,y in zip(old[1:],new[1:])]
        du1,du2,dv1,dv2,dF=[float(y-x) for x,y in zip(old[1:],new[1:])]
        ru1=du1-h*v1;ru2=du2-h*v2
        rv1=dv1+h*(Cd*v1+Co*v2+2*u1-u2-forcing)
        rv2=dv2+h*(Cd*v2+Co*v1+2*u2-u1+Fbar-forcing)
        rf=dF/8-h*(v2-g(Fbar));res=[ru1,ru2,rv1,rv2,rf]
        maxres=[max(x,abs(y)) for x,y in zip(maxres,res)]
        work=[(2*u1-u2)*ru1+(2*u2-u1)*ru2,v1*rv1+v2*rv2,Fbar*rf]
        maxwork=[max(x,abs(y)) for x,y in zip(maxwork,work)]
        wi=h*(v1+v2)*forcing;db=h*(Cd*(v1*v1+v2*v2)+2*Co*v1*v2);dd=h*Fbar*g(Fbar)
        Enew=energy(new);balance=Enew-Eprevious+db+dd-wi
        W+=wi;Db+=db;Dd+=dd;maxbalance=max(maxbalance,abs(balance));maxcum=max(maxcum,abs(Enew+Db+Dd-W))
        maxidentity=max(maxidentity,abs(balance-sum(work)));Eprevious=Enew
    assert np.isfinite(prediction).all()
    for n in sorted(indices):snapshots.append({'N':N,'node':n,**dict(zip(['time','u1','u2','v1','v2','F'],map(float,prediction[n])))})
    csvwrite('prediction_four_snapshots.csv',snapshots)
    predsha=hashlib.sha256(prediction.tobytes(order='C')).hexdigest()
    predsummary={'N':N,'nodes':steps+1,'h':h,'T':T,'trajectory_columns':['t','u1','u2','v1','v2','F'],'memory_trajectory_sha256':predsha,'array_saved':False,
       'modal_coefficients':{'lambda':lam,'damping':damp,'beta':beta,'den':den,'S':S,'af':af},'maximum_root_scaled_residual':maxroot,'maximum_root_iterations':maxiterations,'Newton_bisection_protections':fallbacks,
       'energy_diagnostics':{'terminal_E':Eprevious,'E0':0.,'input_work':W,'background_dissipation':Db,'device_dissipation':Dd,'terminal_balance':Eprevious+Db+Dd-W,'max_abs_step_balance':maxbalance,'max_abs_cumulative_balance':maxcum,'max_abs_increment_residuals_ru1_ru2_rv1_rv2_rF':maxres,'max_abs_three_residual_work_terms':maxwork,'max_abs_energy_minus_residual_work':maxidentity},
       'prediction_completed_before_any_reference_or_author_results_read':True,'completed_at':now()}
    write('prediction_summary.json',predsummary)
    write('prediction_freeze.json',{'at':now(),'trajectory_sha256':predsha,'small_outputs':[record(HERE/'prediction_summary.json'),record(HERE/'prediction_four_snapshots.csv')],'code_sha256':record(Path(__file__))['sha256']})
    events.append({'event':'all98305_predictions_and_SHA_frozen','at':now()});write('read_order.json',events)
    # Only now hash/decode the single permitted synthetic reference member.
    CONTEXT['phase']='reference_comparison';reference=Path(ap['reference_path']);events.append({'event':'reference_hash_start','at':now()})
    refrecord=record(reference);assert refrecord['sha256']==ap['reference_sha256']=='6adf4f158d320c84f7cfa2cbab2c8cfce34d86839573cbf82a027a88681a6a62'
    with np.load(reference,allow_pickle=False) as archive:
        target=archive['D_N16384'];assert target.shape==(98305,9) and target.dtype==np.float64
    assert np.isfinite(target).all() and np.array_equal(prediction[:,0],target[:,0])
    events.append({'event':'reference_D_N16384_only_decoded','at':now(),'source':refrecord})
    metrics={}
    for name,col in [('u1',1),('u2',2),('F',5)]:
        errors=prediction[:,col]-target[:,col];k=int(np.argmax(np.abs(errors)))
        metrics[name]={'max_abs_error':float(abs(errors[k])),'RMS_error':math.sqrt(math.fsum(float(x)*float(x) for x in errors)/len(errors)),
          'max_witness':{'node':k,'time':float(prediction[k,0]),'signed_error':float(errors[k]),'prediction':float(prediction[k,col]),'reference':float(target[k,col])}}
    write('reference_metrics.json',{'N':N,'nodes':steps+1,'metrics':metrics,'u1_u2_maxerror_below_point1':{key:metrics[key]['max_abs_error']<.1 for key in ['u1','u2']},'reference':refrecord})
    events.append({'event':'independent_full_reference_statistics_saved','at':now()});write('read_order.json',events)
    # Author small results read last; solver source is never read or imported.
    CONTEXT['phase']='author_small_comparison';events.append({'event':'author_small_results_first_read','at':now()})
    author=read(AUTHOR/'summary.json')
    with (AUTHOR/'prediction_fixed_snapshots.csv').open(encoding='utf-8',newline='') as f:authorrows=list(csv.DictReader(f))
    write('author_small_schema.json',{'summary_keys':list(author),'snapshot_headers':list(authorrows[0]),'sources':[record(AUTHOR/'summary.json'),record(AUTHOR/'prediction_fixed_snapshots.csv')]})
    authorstats=author['comparison']['fine_vs_reference_on_98305_all_nodes']
    statchecks=[]
    for name in ['u1','u2','F']:
        for field in ['max_abs_error','RMS_error']:
            diff=abs(metrics[name][field]-authorstats[name][field]);statchecks.append({'output':name,'statistic':field,'difference':diff,'passed':diff<1e-6})
    def get(row,aliases):
        for name in aliases:
            if name in row:return row[name]
        raise KeyError(f'Unknown author snapshot fields: {list(row)} need {aliases}')
    pointchecks=[]
    for own in snapshots:
        candidates=[r for r in authorrows if int(get(r,['N','N_steps_per_T']))==N and int(get(r,['node','node_index','index']))==own['node']]
        assert len(candidates)==1
        other=candidates[0]
        for field in ['u1','u2','v1','v2','F']:
            value=float(get(other,[field]));diff=abs(own[field]-value);pointchecks.append({'node':own['node'],'state':field,'difference':diff,'passed':diff<1e-6})
    comparison={'statistic_checks':statchecks,'snapshot_state_checks':pointchecks,'all_six_statistics_passed':all(x['passed'] for x in statchecks),'all_twenty_snapshot_values_passed':all(x['passed'] for x in pointchecks),'fixed_difference_gate':1e-6}
    write('author_comparison.json',comparison);events.append({'event':'all_fixed_comparison_gates_saved','at':now()});write('read_order.json',events)
    assert all(record(Path(x['path']))==x for x in pre['sources'])
    write('run_record.json',{'exit_code':0,'completed_at':now(),'elapsed_seconds':time.perf_counter()-start,'prediction_only_no_author_or_reference_input':True,'all_source_preflight_SHA_unchanged':True,'comparison':comparison,'independent_finite_replay_only':True})
    print(json.dumps({'elapsed_seconds':time.perf_counter()-start,'metrics':metrics,'root_max':maxroot,'root_iterations':maxiterations,'stats_match':comparison['all_six_statistics_passed'],'snapshots_match':comparison['all_twenty_snapshot_values_passed']}))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        write('failure.json',{'at':now(),'error':repr(exc),'context':CONTEXT,'traceback':traceback.format_exc(),'no_retry_or_retuning':True})
        raise
