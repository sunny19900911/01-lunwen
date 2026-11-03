"""Independent evaluation of four frozen Story5 reference states; no ODE or fit."""
from pathlib import Path
import csv,datetime,hashlib,json,math,sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
OUT=HERE/'R001'
OUT.mkdir(exist_ok=False)
started=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
OLD=ROOT/'research/sessions/20261031-1130/roles/role4'
HAND=ROOT/'research/handoffs/p06-sh3-sh4-20261103'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
    (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
registry=json.loads((OLD/'R004/results.json').read_text(encoding='utf-8'))
sources={}
for src in registry['arrays_local_only']:
    p=Path(src['path'])
    for case in ('SHW3X','SHW4X'):
        if case in p.name:
            z=.05 if '-z0.05-' in p.name else .08
            sources[case,z]=(p,src['sha256'])
assert len(sources)==4
rows=[];sums=[];checks=[];modes=[];source_info=[];common=None;input_by_case={}
for (case,z),(p,expected) in sorted(sources.items()):
    assert sha(p)==expected
    with np.load(p,allow_pickle=False) as a:
        t=a['t'];n=a['shear_native_Story5_kN'];s=a['s_unitGamma'];b=a['B_direct'][4];w=a['omega']
        assert len(w)==300 and len(n)==len(t)==len(s)
        assert np.all(np.isfinite(n)) and np.all(np.isfinite(s))
        assert np.all(np.diff(t)>0) and np.max(abs(np.diff(t)-.02))<1e-9
        assert np.all(s[0]==0)
        if common is None:common=(w.copy(),a['B_direct'].copy())
        else:assert np.array_equal(w,common[0]) and np.array_equal(a['B_direct'],common[1])
        if case in input_by_case:
            assert np.array_equal(t,input_by_case[case][0]) and np.array_equal(a['ag'],input_by_case[case][1])
        else:input_by_case[case]=(t.copy(),a['ag'].copy())
        # Independent evaluation: separate weighted column accumulation and scalar fsum.
        weights=np.array([float(b[k])*float(w[k])*float(w[k])/1000.0 for k in range(300)])
        curve=np.zeros(len(t))
        for k in range(300):curve+=weights[k]*s[:,k]
        idx=int(np.flatnonzero(abs(n)==np.max(abs(n)))[0])
        per_mode=[float(weights[k]*s[idx,k]) for k in range(300)]
        total_at_peak=math.fsum(per_mode)
        iref=int(np.argmax(abs(curve)))
        max_native=float(np.max(abs(n)))
        numerator=math.fsum(float(x)**2 for x in abs(curve)-abs(n))
        denominator=math.fsum(float(x)**2 for x in n)
        row={'Case':case,'zeta':z,'Story':5,'native_peak_time_s':float(t[idx]),
             'native_peak_signed_kN':float(n[idx]),'native_peak_abs_kN':max_native,
             'reference_at_native_peak_signed_kN':total_at_peak,
             'reference_peak_abs_kN':float(np.max(abs(curve))),
             'reference_peak_time_s':float(t[iref]),
             'reference_peak_error_percent':100*(float(np.max(abs(curve)))/max_native-1),
             'absolute_curve_NRMSE_percent':100*math.sqrt(numerator/denominator),
             'reference_mode2_kN':per_mode[1],'reference_mode10_kN':per_mode[9],
             'reference_mode13_kN':per_mode[12],
             'reference_modes1to3_kN':math.fsum(per_mode[:3]),
             'reference_modes4to300_kN':math.fsum(per_mode[3:]),
             'mode2_over_reference_total_percent':100*per_mode[1]/total_at_peak}
        rows.append(row)
        checks.append({'Case':case,'zeta':z,'grid_step_s':.02,'point_count':len(t),
                       'first_argmax_rule':'first exact absolute maximum saved sample',
                       'max_curve_vs_saved_reference_kN':float(np.max(abs(curve-a['shear_elastic_inertia_predicted_kN'][:,4]))),
                       'sum_at_native_peak_closure_kN':total_at_peak-float(curve[idx]),
                       'native_and_reference_peak_sign_opposite':bool(n[idx]*total_at_peak<0)})
        for k,x in enumerate(per_mode):modes.append({'Case':case,'zeta':z,'Mode':k+1,'time_s':float(t[idx]),'reference_signed_shear_kN':x})
    source_info.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'unchanged':sha(p)==expected})

def csvout(n,r):
    with (OUT/n).open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)

# Freeze independent values before importing handoff numerical tables.
csvout('independent-story5-four-states.csv',rows)
csvout('independent-story5-all300-at-native-peaks.csv',modes)
save('independent-first-freeze.json',{'started':started,'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'script_handoff_table_imported':False,'prior_context_included_handoff_values':True,'audit_is_blind':False,'rows':rows,'checks':checks,'sources':source_info})
with (HAND/'story5-reference-checks-4.csv').open(encoding='utf-8-sig') as f:provided=list(csv.DictReader(f))
comparisons=[]
for own in rows:
    other=next(x for x in provided if x['Case']==own['Case'] and float(x['zeta'])==own['zeta'])
    for key,value in own.items():
        if key=='Case':continue
        assert key in other
        e=float(value)-float(other[key]);tol=1e-8 if 'kN' in key else 1e-10
        assert abs(e)<=tol,(key,e)
        comparisons.append({'Case':own['Case'],'zeta':own['zeta'],'field':key,'independent':value,'handoff':float(other[key]),'difference':e})
csvout('handoff-numeric-comparison.csv',comparisons)
delta=[]
for z in (.05,.08):
    a=next(x for x in rows if x['Case']=='SHW3X' and x['zeta']==z)
    b=next(x for x in rows if x['Case']=='SHW4X' and x['zeta']==z)
    delta.append({'zeta':z,'native_abs_peak_SH4_minus_SH3_kN':b['native_peak_abs_kN']-a['native_peak_abs_kN'],
                  'reference_at_own_native_peak_difference_kN':b['reference_at_native_peak_signed_kN']-a['reference_at_native_peak_signed_kN'],
                  'mode2_difference_kN':b['reference_mode2_kN']-a['reference_mode2_kN'],
                  'mode10_difference_kN':b['reference_mode10_kN']-a['reference_mode10_kN'],
                  'mode13_difference_kN':b['reference_mode13_kN']-a['reference_mode13_kN'],
                  'modes4to300_difference_kN':b['reference_modes4to300_kN']-a['reference_modes4to300_kN'],
                  'scope':'Different input own peak times; reference composition comparison, not same-time causal attribution.'})
csvout('between-input-at-own-peak-comparison.csv',delta)
assert all(x['unchanged'] for x in source_info)
result={'started':started,'completed':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'exit_code':0,'script_sha256':sha(Path(__file__)),'states':rows,'checks':checks,'between_input':delta,'comparison_fields':len(comparisons),'max_absolute_difference':max(abs(x['difference']) for x in comparisons),'must':0,'all_sources_unchanged':all(x['unchanged'] for x in source_info),'no_new_ODE':True,'no_fit':True,'B_source':'R002 identified18CM directional masses plus actual300Ritz modal shapes/frequencies; not shear regression or direct old-D-mass splice.','interpretation':'Conditional reference does not support mode10/13 same-direction dominance of SHW4X Story5. Native unique modal attribution remains unresolved.'}
save('results.json',result)
print(json.dumps({'completed':result['completed'],'must':0,'comparison_fields':len(comparisons),'max_absolute_difference':result['max_absolute_difference'],'between_input':delta},ensure_ascii=False))
