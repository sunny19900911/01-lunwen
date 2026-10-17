"""Classical discrete Maxwell energy ledger on six frozen histories; no fit or Excel."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time
import numpy as np

HERE=Path(__file__).resolve().parent
PROTOCOL_SHA='282ee343c11eb77dff3d4dfc1562ff4614c78d6a8724a7f335481673c5050ab9'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def total(x):return math.fsum(float(v) for v in x)
def writecsv(name,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    start=time.perf_counter();prot=HERE/'protocol.json';assert sha(prot)==PROTOCOL_SHA
    p=json.loads(prot.read_text(encoding='utf-8'));out=HERE/'ledger_summary_r004.json';assert not out.exists(),'Frozen output exists'
    param_path=(HERE/p['fixed_parameter_summary']).resolve();assert sha(param_path)==p['parameter_summary_sha256']
    fixed=json.loads(param_path.read_text(encoding='utf-8'))['best_grid_row']
    alpha=float(p['parameters']['alpha']);a=float(p['parameters']['a_m_per_kN']);b=float(p['parameters']['b_m_per_s_kN_power_inverse_alpha'])
    assert (alpha,a,b)==(fixed['alpha'],fixed['a_m_per_kN'],fixed['b_m_per_s_kN_power_inverse_alpha'])
    summary=[];all_windows=[];worst_windows=[];worst_intervals=[];intervals=[];input_refs=[];per_record_checks=[]
    for item in p['inputs']:
        path=(HERE/item['path']).resolve();assert sha(path)==item['sha256'];input_refs.append({'path':str(path),'sha256':item['sha256']})
        with path.open(encoding='utf-8',newline='') as f:raw=list(csv.DictReader(f))
        t=np.array([float(r['t_s']) for r in raw]);F=np.array([float(r['P_I_kN']) for r in raw]);J=np.array([float(r['P_J_kN']) for r in raw])
        d=np.array([float(r['U1_m']) for r in raw]);mm=np.array([float(r['U1_mm']) for r in raw]);dt=np.diff(t)
        assert np.array_equal(F,J) and np.array_equal(mm/1000,d) and np.isfinite(np.c_[t,F,d]).all()
        assert np.all(dt>0) and np.max(abs(dt-.02))<1e-10
        assert len(raw)=={'RH4X':2501,'SHW4X':2951,'SHW7X':2696}[item['Case']]
        h=np.sign(F)*abs(F)**(1/alpha)
        ih=np.r_[0.,np.cumsum(dt*(h[1:]+h[:-1])/2)]
        pred=a*(F-F[0])+b*ih;r=pred-(d-d[0]);Fav=(F[1:]+F[:-1])/2
        w=Fav*np.diff(d);us=(a/2)*np.diff(F*F);dp=w-us
        df=b*dt*(F[1:]*h[1:]+F[:-1]*h[:-1])/2
        product=(b/4)*dt*np.diff(F)*np.diff(h);rwork=Fav*np.diff(r)
        gap=df-dp;identity=gap-product-rwork
        W=total(w);endpoint_us=a*(F[-1]**2-F[0]**2)/2;Dport=W-endpoint_us;Dforce=total(df)
        prod_total=total(product);rwork_total=total(rwork);full_identity=(Dforce-Dport)-(prod_total+rwork_total)
        cum_gap=np.cumsum(df)-(np.cumsum(w)-a*(F[1:]**2-F[0]**2)/2)
        cum_identity=cum_gap-(np.cumsum(product)+np.cumsum(rwork))
        maxcum=int(np.argmax(abs(cum_gap)));minport=int(np.argmin(dp));scale=max(1.,abs(W),abs(Dforce));tol=1e-12*scale
        rec={'Link':item['Link'],'Case':item['Case'],'n_points':len(raw),'n_intervals':len(dt),
            'Wtrap_native_kNm':W,'Delta_Us_conditional_kNm':endpoint_us,'Dport_conditional_kNm':Dport,
            'Dforce_trap_model_kNm':Dforce,'Dforce_minus_Dport_kNm':Dforce-Dport,
            'discrete_product_term_kNm':prod_total,'regression_residual_work_kNm':rwork_total,
            'rhs_product_plus_residual_work_kNm':prod_total+rwork_total,
            'total_identity_residual_kNm':full_identity,
            'gap_over_abs_Dport_percent':100*(Dforce-Dport)/abs(Dport) if Dport else None,
            'max_interval_identity_abs_kNm':float(max(abs(identity))),
            'max_cumulative_identity_abs_kNm':float(max(abs(cum_identity))),
            'max_abs_cumulative_gap_kNm':float(abs(cum_gap[maxcum])),
            'max_cumulative_gap_signed_kNm':float(cum_gap[maxcum]),'max_cumulative_gap_at_s':float(t[maxcum+1]),
            'negative_Dport_increment_count_unclipped':int(sum(dp<0)),
            'minimum_Dport_increment_kNm':float(dp[minport]),'minimum_Dport_interval_start_s':float(t[minport]),
            'minimum_Dport_interval_end_s':float(t[minport+1]),
            'min_product_increment_kNm':float(min(product)),
            'arithmetic_tolerance_kNm_not_continuous_bound':tol}
        summary.append(rec)
        keys=(np.rint(t[:-1]*100).astype(int)//100)
        win=[]
        for key in sorted(set(keys)):
            ii=np.flatnonzero(keys==key);first,last=int(ii[0]),int(ii[-1])
            z={'Link':item['Link'],'Case':item['Case'],'window_start_s':float(t[first]),'window_end_s':float(t[last+1]),
                'n_intervals':len(ii),'Wtrap_kNm':total(w[ii]),'Delta_Us_conditional_kNm':total(us[ii]),
                'Dport_conditional_kNm':total(dp[ii]),'Dforce_trap_model_kNm':total(df[ii]),
                'energy_gap_kNm':total(gap[ii]),'product_term_kNm':total(product[ii]),'residual_work_kNm':total(rwork[ii]),
                'identity_residual_kNm':total(identity[ii]),'negative_Dport_increment_count':int(sum(dp[ii]<0))}
            win.append(z)
        assert sum(z['n_intervals'] for z in win)==len(dt)
        all_windows+=win;worst_windows+=sorted(win,key=lambda z:abs(z['energy_gap_kNm']),reverse=True)[:3]
        local=[]
        for i in range(len(dt)):
            z={'Link':item['Link'],'Case':item['Case'],'interval_index':i,
                't_start_s':float(t[i]),'t_end_s':float(t[i+1]),
                'Wtrap_increment_kNm':float(w[i]),'Delta_Us_increment_conditional_kNm':float(us[i]),
                'Dport_increment_conditional_kNm':float(dp[i]),'Dforce_trap_increment_model_kNm':float(df[i]),
                'energy_gap_increment_kNm':float(gap[i]),'product_increment_kNm':float(product[i]),
                'residual_work_increment_kNm':float(rwork[i]),'identity_residual_increment_kNm':float(identity[i]),
                'cumulative_energy_gap_kNm':float(cum_gap[i]),'cumulative_identity_residual_kNm':float(cum_identity[i])}
            local.append(z)
        intervals+=local;worst_intervals+=sorted(local,key=lambda z:abs(z['energy_gap_increment_kNm']),reverse=True)[:3]
        per_record_checks.append(abs(full_identity)<tol and max(abs(identity))<tol and max(abs(cum_identity))<tol and min(product)>=0)
    checks={'six_prespecified_records_only':len(summary)==6,'all_16290_intervals_retained':len(intervals)==16290,
        'all_326_fixed_windows_including_partial_tail':len(all_windows)==326,
        'all_discrete_identity_checks_within_floating_tolerance':all(per_record_checks),
        'nonnegative_product_terms_without_clipping':all(z['min_product_increment_kNm']>=0 for z in summary),
        'all_input_and_parameter_hashes_unchanged':all(sha(z['path'])==z['sha256'] for z in input_refs) and sha(param_path)==p['parameter_summary_sha256'],
        'protocol_unchanged':sha(prot)==PROTOCOL_SHA,'runtime_below_480_seconds':time.perf_counter()-start<480}
    writecsv('six_record_energy_summary_r004.csv',summary);writecsv('all_1s_windows_r004.csv',all_windows)
    writecsv('worst_1s_windows_r004.csv',worst_windows);writecsv('worst_intervals_r004.csv',worst_intervals)
    writecsv('local_all_interval_ledger_r004.csv',intervals)
    result={'evidence_id':p['evidence_id'],'review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-start,'code_sha256':sha(__file__),'protocol_sha256':PROTOCOL_SHA,
        'fixed_parameters':p['parameters'],'input_refs':input_refs,'parameter_summary_sha256':sha(param_path),
        'records':summary,'worst_windows':worst_windows,'checks':checks,
        'outputs':[{'file':name,'bytes':(HERE/name).stat().st_size,'sha256':sha(HERE/name)} for name in
            ['six_record_energy_summary_r004.csv','all_1s_windows_r004.csv','worst_1s_windows_r004.csv','worst_intervals_r004.csv','local_all_interval_ledger_r004.csv']],
        'interpretation':p['limits'],'local_files_policy':'Full interval ledger remains local. Master decides Git whitelist; small summaries/scripts only by default. No six-record total energy was computed.'}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    record={'evidence_id':p['evidence_id'],'review_status':'candidate','command_argv':[sys.executable,str(Path(__file__).resolve())],
        'finished_utc':result['finished_utc'],'elapsed_seconds':result['elapsed_seconds'],'python':sys.version,'numpy':np.__version__,
        'exit_code_after_checks':0 if all(checks.values()) else 1,'protocol_last_write_utc':datetime.fromtimestamp(prot.stat().st_mtime,timezone.utc).isoformat(),
        'code_sha256':sha(__file__),'summary_sha256':sha(out),'input_refs':input_refs,'checks':checks}
    (HERE/'run_record_r004.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'records':summary,'worst_window_each_record':[z for z in worst_windows[::3]],'checks':checks,'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())
if __name__=='__main__':sys.stdout.reconfigure(encoding='utf-8');main()
