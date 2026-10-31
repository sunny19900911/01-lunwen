import os
os.environ['OPENBLAS_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,csv
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SRC=S/'roles/role4/R004'
DEADLINE=datetime.fromisoformat('2026-10-31T12:30:14+08:00');now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R005 RK4 deadline')
gate();mf=json.loads((SRC/'delivery-manifest-v002.json').read_text(encoding='utf-8'))
meta=Path(next(x['path'] for x in mf['inputs'] if x['path'].endswith('controlled_small_tables.json')))
small=json.loads(meta.read_text(encoding='utf-8'));tab=small['Modal Periods And Frequencies'];h=tab[1][1]
wm={int(x[h.index('Mode')]):float(x[h.index('CircFreq')]) for _,x in tab[3:]};modes=(2,10,13)
w=np.array([wm[k] for k in modes]*2);zetas=np.array([.05]*3+[.08]*3)
cfgp=Path(next(x['path'] for x in mf['inputs'] if x['path'].endswith('input-config.json')));cfg=json.loads(cfgp.read_text(encoding='utf-8'))
with np.load(cfg['derived_npz'],allow_pickle=False) as z:
    ag=z[cfg['cases']['SHW3X']['ag_key']].copy();t=z[cfg['cases']['SHW3X']['t_key']].copy()
refs=[];vrefs=[]
for zeta in (.05,.08):
    p=next(x['path'] for x in mf['local_only_arrays'] if ('actual300-SHW3X-z'+str(zeta)+'-') in x['path'])
    with np.load(p,allow_pickle=False) as z:
        assert np.array_equal(t,z['t']) and np.array_equal(ag,z['ag'])
        idx=np.array(modes)-1;assert np.array_equal(z['omega'][idx],w[:3])
        refs.append(z['s_unitGamma'][:,idx].copy());vrefs.append(z['sdot_unitGamma'][:,idx].copy())
reference=np.column_stack(refs);vreference=np.column_stack(vrefs)
assert np.allclose(np.diff(t),.02,rtol=0,atol=1e-12)
def rk4(sub):
    q=np.zeros(6);v=q.copy();Q=np.zeros((len(t),6));V=Q.copy();step=.02/sub;half=step/2;c=2*zetas*w;k=w*w
    for i in range(len(t)-1):
        if i%100==0:gate()
        da=(ag[i+1]-ag[i])/sub
        for j in range(sub):
            a0=ag[i]+j*da;am=a0+da/2;aend=a0+da
            a1=-c*v-k*q-a0
            q2=q+half*v;v2=v+half*a1;a2=-c*v2-k*q2-am
            q3=q+half*v2;v3=v+half*a2;a3=-c*v3-k*q3-am
            q4=q+step*v3;v4=v+step*a3;a4=-c*v4-k*q4-aend
            q=q+(step/6)*(v+2*v2+2*v3+v4)
            v=v+(step/6)*(a1+2*a2+2*a3+a4)
        Q[i+1]=q;V[i+1]=v
    return Q,V
Q16,V16=rk4(16);Q32,V32=rk4(32);out=[]
for j in range(6):
    nq16=float(np.linalg.norm(Q16[:,j]-reference[:,j])/np.linalg.norm(reference[:,j]));nq32=float(np.linalg.norm(Q32[:,j]-reference[:,j])/np.linalg.norm(reference[:,j]));nv16=float(np.linalg.norm(V16[:,j]-vreference[:,j])/np.linalg.norm(vreference[:,j]));nv32=float(np.linalg.norm(V32[:,j]-vreference[:,j])/np.linalg.norm(vreference[:,j]))
    assert nq32<1e-7 and nv32<1e-7
    if nq16>1e-12:assert nq32<.2*nq16
    if nv16>1e-12:assert nv32<.2*nv16
    out.append({'Case':'SHW3X','Mode':modes[j%3],'zeta':float(zetas[j]),'omega':float(w[j]),'RK4_substeps_coarse':16,'RK4_substeps_fine':32,'q_NRMSE_coarse':nq16,'q_NRMSE_fine':nq32,'v_NRMSE_coarse':nv16,'v_NRMSE_fine':nv32,'q_coarse_over_fine_error':nq16/nq32,'v_coarse_over_fine_error':nv16/nv32,'q_max_abs_error_fine_m':float(max(abs(Q32[:,j]-reference[:,j]))),'v_max_abs_error_fine_m_per_s':float(max(abs(V32[:,j]-vreference[:,j]))),'q_peak_time_saved_s':float(t[np.argmax(abs(reference[:,j]))]),'q_peak_time_RK4_s':float(t[np.argmax(abs(Q32[:,j]))])})
with (O/'independent-RK4-unit-checks-6.csv').open('x',encoding='utf-8',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');wr.writeheader();wr.writerows(out)
result={'completed':now().isoformat(),'cases':6,'new_modal_integrations':'six SHW3X unit kernels only, two RK4 refinements, not six sets of 300 modes','method':'own classical fourth-order RK4, fixed piecewise-linear ag interpolation inside each .02-s native interval','fine_step_seconds':.02/32,'zero_initial_and_nonzero_ag0_retained':True,'max_q_NRMSE_fine':max(x['q_NRMSE_fine'] for x in out),'max_v_NRMSE_fine':max(x['v_NRMSE_fine'] for x in out),'min_q_error_refinement_ratio':min(x['q_coarse_over_fine_error'] for x in out),'max_q_absolute_error_m':max(x['q_max_abs_error_fine_m'] for x in out),'max_v_absolute_error_m_per_s':max(x['v_max_abs_error_fine_m_per_s'] for x in out),'must_count':0,'foreign_integrator_or_script_imported':False,'unit_arrays_exported':False}
with (O/'RK4-checks.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
