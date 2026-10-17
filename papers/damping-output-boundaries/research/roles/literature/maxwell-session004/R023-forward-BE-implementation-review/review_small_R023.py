"""Own tiny scalar/small-file checks; never import or execute target, never touch NPZ."""
from pathlib import Path
import csv, hashlib, json, math
from datetime import datetime, timezone, timedelta

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[2] / 'experiments' / 'maxwell-session004' / 'R022-forward-BE-synthetic'
def read(name):
    return json.loads((SRC/name).read_text(encoding='utf-8'))
def sha(path):
    assert Path(path).suffix.lower() != '.npz'
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
checks = []
def check(name, passed, detail=None):
    checks.append({'name':name, 'pass':bool(passed), 'detail':detail})

rules = json.loads((HERE/'input-rules-R023.json').read_text(encoding='utf-8'))
for entry in rules['inputs']:
    path = Path(entry['path'])
    check('input_unchanged:'+path.name, sha(path)==entry['sha256'] and path.stat().st_size==entry['bytes'])
for entry in read('delivery_manifest.json')['files']:
    path = Path(entry['path'])
    check('delivery_binding:'+path.name, sha(path)==entry['sha256'] and path.stat().st_size==entry['bytes'])
for entry in read('pre_run_freeze.json')['files']:
    check('pre_run_binding:'+Path(entry['path']).name, sha(entry['path'])==entry['sha256'])

ps, pf, summary = read('prediction_summary.json'), read('prediction_freeze.json'), read('summary.json')
check('prediction_summary_preserved', ps['predictions']==summary['predictions'])
for key, filename in [('code_sha256','forward_be.py'),('protocol_sha256','protocol.json'),('prediction_summary_sha256','prediction_summary.json'),('fixed_snapshots_sha256','prediction_fixed_snapshots.csv')]:
    check('prediction_freeze:'+key, pf[key]==sha(SRC/filename))
for run in ps['predictions']:
    check('memory_sha_records_only:'+str(run['N']), pf['memory_trajectory_sha256'][str(run['N'])]==run['memory_trajectory_sha256'])
events = read('reference_read_order.json')['events']
check('event_clock_nondecreasing', all(a['monotonic_ns']<=b['monotonic_ns'] for a,b in zip(events,events[1:])))
names = [x['event'] for x in events]
check('event_list_order', names.index('both_predictions_and_hashes_on_disk_before_reference')<names.index('reference_hash_access_start')<names.index('D_N16384_reference_read_complete'))
check('prediction_reference_flags', not ps['reference_accessed'] and pf['both_predictions_complete'] and pf['reference_not_yet_accessed'] and not summary['reference_used_in_prediction'])

with (SRC/'prediction_fixed_snapshots.csv').open(encoding='utf-8-sig',newline='') as f:
    pred=list(csv.DictReader(f))
with (SRC/'comparison_fixed_snapshots.csv').open(encoding='utf-8-sig',newline='') as f:
    comp=list(csv.DictReader(f))
check('seven_snapshots',len(pred)==len(comp)==7)
for p,c in zip(pred,comp):
    tag=p['N']+':'+p['node']
    check('unchanged_snapshot:'+tag,all(c[k]==v for k,v in p.items()))
    n,N=int(p['node']),int(p['N'])
    check('reference_index:'+tag,int(c['reference_index'])==n*(2 if N==8192 else 1))
    for key in ['u1','u2','F']:
        check('snapshot_error:'+tag+':'+key,float(c[key+'_error'])==float(c[key])-float(c['reference_'+key]))
    u1,u2,v1,v2,F=(float(p[k]) for k in ['u1','u2','v1','v2','F'])
    E=u1*u1+u2*u2-u1*u2+.5*(v1*v1+v2*v2)+F*F/16
    check('snapshot_energy:'+tag, math.isclose(E,float(p['E']),abs_tol=1e-14))
    bal=E+sum(float(p[k]) for k in ['D_background','D_device','D_numerical_u','D_numerical_v','D_numerical_F'])-float(p['W_input'])
    check('snapshot_balance:'+tag,abs(bal-float(p['actual_cumulative_balance']))<=3e-14)
for run in ps['predictions']:
    N=run['N']
    check('snapshot_indices:'+str(N),[int(p['node']) for p in pred if int(p['N'])==N]==run['fixed_indices'])
check('J_only_fine',summary['J_fine_index']==16529 and summary['J_coarse_index'] is None and summary['J_coarse_grid_coordinate']==8264.5)
common0=summary['comparison']['coarse_vs_reference_on_49153_common_nodes']
common1=summary['comparison']['fine_vs_reference_on_49153_common_nodes']
fine=summary['comparison']['fine_vs_reference_on_98305_all_nodes']
for key in ['u1','u2','F']:
    for metric in ['max_abs_error','RMS_error']:
        check('improvement_boolean:'+key+':'+metric,summary['coarse_to_fine_improvement_on_common_grid'][key][metric]==(common1[key][metric]<common0[key][metric]))
for key in ['u1','u2']:
    check('fixed_point1_gate:'+key,summary['fine_u1_u2_maxerror_below_point1'][key]==(fine[key]['max_abs_error']<.1))
check('fixed_gate_fail_retained',summary['fine_u1_u2_maxerror_below_point1']=={'u1':False,'u2':True})

# Two independent 2x2 matrix checks and six stand-alone scalar roots only.
# The loops below do not advance a trajectory or consume any reference data.
cd,co=(1+math.sqrt(3))/20,(1-math.sqrt(3))/20
scalar=[]
for run in ps['predictions']:
    h=run['h']; A=1+h*cd+2*h*h; B=h*co-h*h
    # Eigenvalue inverse construction independent of target determinant formula.
    d=.5*(1/(A+B)+1/(A-B)); o=.5*(1/(A+B)-1/(A-B))
    a=.125+h*h*d
    check('inverse_eigenvalues:'+str(run['N']),abs(d-run['S_h'])<3e-16 and abs(o-run['A_inverse'][0][1])<3e-16 and abs(a-run['a'])<3e-16)
    for b in [-.7,0.,.7]:
        lo,hi=sorted([0.,b/a]); flo=a*lo+h*math.copysign((abs(lo)/10)**(10/3),lo)-b
        fhi=a*hi+h*math.copysign((abs(hi)/10)**(10/3),hi)-b
        # Independent 60 scalar halvings (not the target rootsolve function).
        for _ in range(60):
            mid=(lo+hi)/2
            fm=a*mid+h*math.copysign((abs(mid)/10)**(10/3),mid)-b
            if fm>0: hi=mid
            else: lo=mid
        x=(lo+hi)/2
        residual=a*x+h*math.copysign((abs(x)/10)**(10/3),x)-b
        scalar.append({'N':run['N'],'b':b,'root':x,'residual':residual,'bracket_signs':[flo,fhi]})
        check('scalar_bracket_gate:'+str(run['N'])+':'+str(b),flo<=0<=fhi and min(0,b/a)<=x<=max(0,b/a) and abs(residual)<=1e-11*max(1,abs(b)))

result={'scope':'small-file transcriptions and six independent scalar roots/two 2x2 matrices only; no target execution, NPZ stat/read/hash/decode, or all-time recomputation',
        'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks':checks,'check_count':len(checks),'failed_checks':[x for x in checks if not x['pass']],'scalar_challenges':scalar,
        'reference_identity':'Inherited declared SHA; no array identity reverified','whole_time_statistics':'Transcription/control-flow only, not independently recomputed'}
(HERE/'small-challenges-R023.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'check_count':len(checks),'failed_checks':result['failed_checks'],'scalar_max_abs_residual':max(abs(x['residual']) for x in scalar)},ensure_ascii=False))
