"""Prespecified no-time-differentiation Maxwell profile; K2 train, K5 transfer only."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json, platform, sys, time
import numpy as np

HERE=Path(__file__).resolve().parent
PROTOCOL_SHA='8c7e2733c30a9090a442d3861193c3e27ef7f7ba5688542c2afc8597ff364719'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writecsv(name,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def load(p):
    with p.open(encoding='utf-8',newline='') as f:r=list(csv.DictReader(f))
    t=np.array([float(x['t_s']) for x in r]);F=np.array([float(x['P_I_kN']) for x in r]);d=np.array([float(x['U1_m']) for x in r])
    assert len(r)==2501 and np.all(np.diff(t)>0) and np.isfinite(np.c_[t,F,d]).all()
    return {'t':t,'F':F,'d':d,'y':d-d[0]}
def design(data,alpha):
    F=data['F'];g=np.sign(F)*abs(F)**(1/alpha)
    integ=np.r_[0.,np.cumsum((g[1:]+g[:-1])/2*np.diff(data['t']))]
    return np.c_[F-F[0],integ]
def rank_info(X):
    norms=np.linalg.norm(X,axis=0);assert np.all(norms>0)
    Z=X/norms
    s=np.linalg.svd(X,compute_uv=False);ss=np.linalg.svd(Z,compute_uv=False)
    rank=int(sum(s>np.finfo(float).eps*max(X.shape)*s[0]));rs=int(sum(ss>np.finfo(float).eps*max(X.shape)*ss[0]))
    return norms,Z,{'raw_rank':rank,'scaled_rank':rs,'raw_smax':float(s[0]),'raw_smin':float(s[-1]),
        'raw_condition':float(s[0]/s[-1]),'scaled_smax':float(ss[0]),'scaled_smin':float(ss[-1]),
        'scaled_condition':float(ss[0]/ss[-1]),'column1_norm':float(norms[0]),'column2_norm':float(norms[1])}
def nnls2(X,y):
    norms,Z,info=rank_info(X);uncon=np.linalg.lstsq(Z,y,rcond=None)[0]
    choices=[]
    if np.all(uncon>=0):choices.append(('interior' if np.all(uncon>0) else 'interior_zero_boundary',uncon))
    choices += [('a_only_b_zero',np.array([max(0.,float(Z[:,0]@y)),0.])),
                ('b_only_a_zero',np.array([0.,max(0.,float(Z[:,1]@y))])),('both_zero',np.zeros(2))]
    active,scaled=min(choices,key=lambda c:float(np.sum((Z@c[1]-y)**2)))
    return scaled/norms,uncon/norms,active,info
def metrics(y,pred):
    e=pred-y;rmse=float(np.sqrt(np.mean(e*e)));rms=float(np.sqrt(np.mean(y*y)))
    return {'RMSE_m':rmse,'RMSE_mm':1000*rmse,'MAE_m':float(np.mean(abs(e))),
        'max_abs_residual_m':float(max(abs(e))),'mean_residual_m':float(np.mean(e)),
        'end_residual_m':float(e[-1]),'y_RMS_m':rms,'RMSE_over_y_RMS':rmse/rms if rms else None,
        'SSE_m2':float(e@e)}
def parameters(ab,alpha):
    a,b=map(float,ab)
    return {'a_m_per_kN':a,'b_m_per_s_kN_power_inverse_alpha':b,
        'k_kN_per_m':1/a if a>0 else None,'c_kN_s_per_m_power_alpha':b**(-alpha) if b>0 else None,
        'strictly_positive_finite_parameters':bool(a>0 and b>0)}
def main():
    start=time.perf_counter();prot=HERE/'protocol.json';assert sha(prot)==PROTOCOL_SHA
    p=json.loads(prot.read_text(encoding='utf-8'));out=HERE/'fit_summary_r002.json';assert not out.exists(),'Frozen output exists'
    inputs=[(HERE/x['path']).resolve() for x in p['inputs']]
    assert all(sha(path)==item['sha256'] for path,item in zip(inputs,p['inputs']))
    train,test=map(load,inputs);profile=[]
    for i in range(10,101):
        alpha=i/50;X=design(train,alpha);Xt=design(test,alpha)
        ab,uncon,active,info=nnls2(X,train['y']);_,_,testinfo=rank_info(Xt)
        m=metrics(train['y'],X@ab);mt=metrics(test['y'],Xt@ab)
        row={'alpha':alpha,**parameters(ab,alpha),'active_set':active,
             'unconstrained_a':float(uncon[0]),'unconstrained_b':float(uncon[1])}
        row.update({'K2_'+k:v for k,v in info.items()});row.update({'K2_'+k:v for k,v in m.items()})
        row.update({'K5_transfer_'+k:v for k,v in mt.items()})
        row.update({'K5_design_'+k:v for k,v in testinfo.items()});profile.append(row)
    best=min(profile,key=lambda r:r['K2_SSE_m2']);alpha=best['alpha'];ab=np.array([best['a_m_per_kN'],best['b_m_per_s_kN_power_inverse_alpha']])
    ranges={}
    for fraction in [.01,.05,.10]:
        selected=[r for r in profile if r['K2_RMSE_m']<=best['K2_RMSE_m']*(1+fraction)]
        ranges[str(fraction)]={'alpha_values':[r['alpha'] for r in selected],'alpha_min':min(r['alpha'] for r in selected),
            'alpha_max':max(r['alpha'] for r in selected),'span':max(r['alpha'] for r in selected)-min(r['alpha'] for r in selected),
            'a_range':[min(r['a_m_per_kN'] for r in selected),max(r['a_m_per_kN'] for r in selected)],
            'b_range':[min(r['b_m_per_s_kN_power_inverse_alpha'] for r in selected),max(r['b_m_per_s_kN_power_inverse_alpha'] for r in selected)]}
    conditional=[];residuals=[]
    shot=p['optional_screenshot_check'];sa=shot['alpha'];sab=np.array([1/shot['k_assumed_kN_per_m'],shot['c_assumed_kN_s_over_m_power_alpha']**(-1/sa)])
    for device,data in [('K2',train),('K5',test)]:
        pred=design(data,alpha)@ab;spred=design(data,sa)@sab
        conditional.append({'device':device,'assumed_k_kN_per_m':500000,'assumed_c':477,'assumed_alpha':sa,
            'units_are_conditional_not_verified_property':True,**metrics(data['y'],spred)})
        for j,t in enumerate(data['t']):
            residuals.append({'device':device,'case':'RH4X','t_s':float(t),'native_P_I_kN':float(data['F'][j]),
                'native_U1_m':float(data['d'][j]),'delta_U1_m':float(data['y'][j]),
                'K2_selected_model_predicted_delta_U1_m':float(pred[j]),'residual_pred_minus_data_m':float(pred[j]-data['y'][j]),
                'screenshot_conditional_predicted_delta_U1_m':float(spred[j])})
    writecsv('alpha_profile_r002.csv',profile);writecsv('all_point_residuals_r002.csv',residuals);writecsv('screenshot_conditional_residuals_r002.csv',conditional)
    checks={'all_91_prespecified_alphas':len(profile)==91 and profile[0]['alpha']==.2 and profile[-1]['alpha']==2.,
        'all_5002_input_points_retained':len(residuals)==5002,'all_constrained_coefficients_nonnegative':all(r['a_m_per_kN']>=0 and r['b_m_per_s_kN_power_inverse_alpha']>=0 for r in profile),
        'both_designs_full_scaled_rank_every_alpha':all(r['K2_scaled_rank']==2 and r['K5_design_scaled_rank']==2 for r in profile),
        'all_profile_metrics_finite':all(np.isfinite(r['K2_RMSE_m']) and np.isfinite(r['K5_transfer_RMSE_m']) for r in profile),
        'input_and_protocol_hashes_unchanged':sha(prot)==PROTOCOL_SHA and all(sha(path)==item['sha256'] for path,item in zip(inputs,p['inputs'])),
        'runtime_below_480_seconds':time.perf_counter()-start<480}
    summary={'evidence_id':p['evidence_id'],'review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-start,'code_sha256':sha(__file__),'protocol_sha256':PROTOCOL_SHA,
        'selected_by':'K2 SSE only; K5 never used for selection','best_grid_row':best,'descriptive_profile_sets':ranges,
        'broad_5pct_set_by_prespecified_span_rule':ranges['0.05']['span']>=.20,'alpha_grid_boundary_selected':alpha in [.2,2.],
        'active_set_counts':{name:sum(r['active_set']==name for r in profile) for name in sorted({r['active_set'] for r in profile})},
        'screenshot_conditional_metrics':conditional,'checks':checks,
        'input_sizes':{'K2':len(train['t']),'K5':len(test['t'])},
        'zero_force_samples':{'K2':int(sum(train['F']==0)),'K5':int(sum(test['F']==0))},
        'no_time_differentiation_no_sign_flip_no_Excel_read':True,
        'interpretation':'Nonnegative closure NNLS; boundary solutions do not identify finite positive k/c. Profile sets are descriptive, not confidence intervals. Full linear rank is conditional on alpha and does not establish unique physical nonlinear parameters. Force conjugacy and attached-mass effects remain independent conditions. K5 is same-wave other-device checking, not independent-earthquake validation.'}
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    files=[Path(__file__),prot,out,HERE/'alpha_profile_r002.csv',HERE/'all_point_residuals_r002.csv',HERE/'screenshot_conditional_residuals_r002.csv']
    record={'evidence_id':p['evidence_id'],'review_status':'candidate','command_argv':[sys.executable,str(Path(__file__).resolve())],
        'finished_utc':summary['finished_utc'],'elapsed_seconds':summary['elapsed_seconds'],'exit_code_after_checks':0 if all(checks.values()) else 1,
        'python':platform.python_version(),'numpy':np.__version__,'protocol_file_last_write_utc':datetime.fromtimestamp(prot.stat().st_mtime,timezone.utc).isoformat(),
        'inputs':p['inputs'],'files':[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f)} for f in files],'checks':checks}
    (HERE/'run_record_r002.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'best':best,'profile_sets':ranges,'active_sets':summary['active_set_counts'],'conditional_screenshot':conditional,'checks':checks,'elapsed_seconds':summary['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())
if __name__=='__main__':sys.stdout.reconfigure(encoding='utf-8');main()
