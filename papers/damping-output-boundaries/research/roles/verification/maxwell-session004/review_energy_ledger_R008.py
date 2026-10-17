"""Independent stdlib discrete ledger and summation-by-parts review; no XLSX/fit."""
import argparse
import csv
import hashlib
import json
import math
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def readcsv(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def prefix(values):
    result = []; total = correction = 0.
    for x in values:
        y = x-correction; new = total+y
        correction = (new-total)-y; total = new; result.append(total)
    return result


def run(source, out):
    expected = {
        'report.md': 'b831a5e6fd83091b14c14e7cec6cfe9958f5df061acc9c67312499653255f141',
        'protocol.json': '282ee343c11eb77dff3d4dfc1562ff4614c78d6a8724a7f335481673c5050ab9',
        'check_discrete_ledger.py': '57d320564788cea5363667102bf7e0ce022be2059b7f0e535ca1faaf9ac8e17f',
        'ledger_summary_r004.json': '16f80834f7ea0cfef2474d4ec28780f8a1762bb042e28aa38a0da61e227f1109',
        'run_record_r004.json': '76f71cb626aa80e40f179679e0342e35e8f0715e88aaa42ca0c91def27676274'}
    files = [source/k for k in expected]
    for name, checksum in expected.items(): assert sha(source/name) == checksum, name
    protocol = json.loads((source/'protocol.json').read_text(encoding='utf-8'))
    original = json.loads((source/'ledger_summary_r004.json').read_text(encoding='utf-8'))
    for item in original['outputs']:
        p = source/item['file']; assert sha(p) == item['sha256'] and p.stat().st_size == item['bytes']; files.append(p)
    parameters = (source/protocol['fixed_parameter_summary']).resolve(); files.append(parameters)
    assert sha(parameters) == protocol['parameter_summary_sha256']
    trained = json.loads(parameters.read_text(encoding='utf-8'))['best_grid_row']
    alpha = float(protocol['parameters']['alpha']); a = float(protocol['parameters']['a_m_per_kN'])
    b = float(protocol['parameters']['b_m_per_s_kN_power_inverse_alpha'])
    assert (alpha,a,b) == (.3,2.0006042528243313e-6,1.1798190016520894e-9)
    assert (alpha,a,b) == (trained['alpha'],trained['a_m_per_kN'],trained['b_m_per_s_kN_power_inverse_alpha'])
    inputs = protocol['inputs']; assert len(inputs) == 6
    assert {(x['Link'],x['Case']) for x in inputs} == {(l,c) for l in ['K2','K5'] for c in ['RH4X','SHW4X','SHW7X']}
    for item in inputs:
        path = (source/item['path']).resolve(); assert sha(path) == item['sha256']; files.append(path)
    input_snapshot = [{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
    allref = readcsv(source/'local_all_interval_ledger_r004.csv'); assert len(allref) == 16290
    refs = {(x['Link'],x['Case'],int(x['interval_index'])):x for x in allref}; assert len(refs) == 16290
    winref = readcsv(source/'all_1s_windows_r004.csv'); assert len(winref) == 326
    windows = {(x['Link'],x['Case'],float(x['window_start_s'])):x for x in winref}; assert len(windows) == 326
    worstwin = readcsv(source/'worst_1s_windows_r004.csv'); worstint = readcsv(source/'worst_intervals_r004.csv')
    assert len(worstwin) == len(worstint) == 18
    sums = {(x['Link'],x['Case']):x for x in readcsv(source/'six_record_energy_summary_r004.csv')}; assert len(sums) == 6
    differences = {}
    def compare(ours, theirs):
        assert set(ours) == set(theirs), (set(ours)-set(theirs),set(theirs)-set(ours))
        for name, value in ours.items():
            if isinstance(value,str): assert value == theirs[name]
            elif isinstance(value,int): assert value == int(theirs[name]), (name,value,theirs[name])
            else:
                difference = abs(value-float(theirs[name])); differences[name] = max(differences.get(name,0),difference)
                tolerance = 2e-13 if 'cumulative' in name else 2e-14
                assert difference <= tolerance+2e-10*abs(float(theirs[name])), (name,value,theirs[name])
    result = []; count_intervals = count_windows = 0
    for item in inputs:
        link, case = item['Link'], item['Case']; raw = readcsv(source/item['path'])
        n = {'RH4X':2501,'SHW4X':2951,'SHW7X':2696}[case]; assert len(raw) == n
        t = [float(x['t_s']) for x in raw]; f = [float(x['P_I_kN']) for x in raw]; d = [float(x['U1_m']) for x in raw]
        assert all(ti == i*.02 for i,ti in enumerate(t))
        assert all(math.isfinite(v) for col in [t,f,d] for v in col)
        assert all((x['Link'],x['Case'],x['Story']) == (link,case,'Story11') for x in raw)
        assert all(float(x['P_J_kN']) == f[i] and float(x['U1_mm'])/1000 == d[i] for i,x in enumerate(raw))
        h = [math.copysign(abs(v)**(1/alpha),v) if v else 0. for v in f]
        ih = [0.]+prefix([(t[i+1]-t[i])*math.fsum((h[i],h[i+1]))/2 for i in range(n-1)])
        residual = [math.fsum((a*(f[i]-f[0]),b*ih[i],-(d[i]-d[0]))) for i in range(n)]
        w=[]; us=[]; dp=[]; df=[]; prod=[]; rw=[]; adjoint=[]; ident=[]; sbp_interval=[]
        for i in range(n-1):
            f0,f1 = f[i:i+2]; h0,h1 = h[i:i+2]; dt = t[i+1]-t[i]
            fav = math.fsum((f0,f1))/2; deltaf = f1-f0
            wi = fav*(d[i+1]-d[i]); ui = a*deltaf*fav
            di = b*dt*math.fsum((f0*h0,f1*h1))/2
            pi = (b*dt/4)*deltaf*(h1-h0)
            ri = fav*(residual[i+1]-residual[i]); qi = math.fsum((residual[i],residual[i+1]))*deltaf/2
            w.append(wi);us.append(ui);dp.append(wi-ui);df.append(di);prod.append(pi);rw.append(ri);adjoint.append(qi)
            ident.append(math.fsum((di,-(wi-ui),-pi,-ri)))
            sbp_interval.append(math.fsum((ri,-f1*residual[i+1],f0*residual[i],qi)))
        cw,cf,cp,cr,cq = [prefix(x) for x in [w,df,prod,rw,adjoint]]
        cgap = [math.fsum((cf[i],-cw[i],a*(f[i+1]**2-f[0]**2)/2)) for i in range(n-1)]
        ci = [math.fsum((cgap[i],-cp[i],-cr[i])) for i in range(n-1)]
        csbp = [math.fsum((cr[i],-f[i+1]*residual[i+1],f[0]*residual[0],cq[i])) for i in range(n-1)]
        local = []
        for i in range(n-1):
            z = {'Link':link,'Case':case,'interval_index':i,'t_start_s':t[i],'t_end_s':t[i+1],
                 'Wtrap_increment_kNm':w[i],'Delta_Us_increment_conditional_kNm':us[i],
                 'Dport_increment_conditional_kNm':dp[i],'Dforce_trap_increment_model_kNm':df[i],
                 'energy_gap_increment_kNm':df[i]-dp[i],'product_increment_kNm':prod[i],
                 'residual_work_increment_kNm':rw[i],'identity_residual_increment_kNm':ident[i],
                 'cumulative_energy_gap_kNm':cgap[i],'cumulative_identity_residual_kNm':ci[i]}
            compare(z,refs[(link,case,i)]);local.append(z)
        W=math.fsum(w); U=a*(f[-1]**2-f[0]**2)/2; Dp=W-U; Df=math.fsum(df)
        P=math.fsum(prod); R=math.fsum(rw); Q=math.fsum(adjoint); boundary=f[-1]*residual[-1]-f[0]*residual[0]
        imax=max(range(n-1),key=lambda i:abs(cgap[i])); imin=min(range(n-1),key=lambda i:dp[i])
        tolerance=1e-12*max(1,abs(W),abs(Df))
        row={'Link':link,'Case':case,'n_points':n,'n_intervals':n-1,'Wtrap_native_kNm':W,
             'Delta_Us_conditional_kNm':U,'Dport_conditional_kNm':Dp,'Dforce_trap_model_kNm':Df,
             'Dforce_minus_Dport_kNm':Df-Dp,'discrete_product_term_kNm':P,'regression_residual_work_kNm':R,
             'rhs_product_plus_residual_work_kNm':P+R,'total_identity_residual_kNm':math.fsum((Df,-Dp,-P,-R)),
             'gap_over_abs_Dport_percent':100*(Df-Dp)/abs(Dp),'max_interval_identity_abs_kNm':max(map(abs,ident)),
             'max_cumulative_identity_abs_kNm':max(map(abs,ci)),'max_abs_cumulative_gap_kNm':abs(cgap[imax]),
             'max_cumulative_gap_signed_kNm':cgap[imax],'max_cumulative_gap_at_s':t[imax+1],
             'negative_Dport_increment_count_unclipped':sum(x<0 for x in dp),'minimum_Dport_increment_kNm':dp[imin],
             'minimum_Dport_interval_start_s':t[imin],'minimum_Dport_interval_end_s':t[imin+1],
             'min_product_increment_kNm':min(prod),'arithmetic_tolerance_kNm_not_continuous_bound':tolerance}
        compare(row,sums[(link,case)])
        from_summary = next(x for x in original['records'] if (x['Link'],x['Case']) == (link,case));compare(row,from_summary)
        wins=[]; sbp_windows=[]
        for start in range(0,n-1,50):
            end=min(start+50,n-1);sl=slice(start,end)
            z={'Link':link,'Case':case,'window_start_s':t[start],'window_end_s':t[end],'n_intervals':end-start,
               'Wtrap_kNm':math.fsum(w[sl]),'Delta_Us_conditional_kNm':math.fsum(us[sl]),
               'Dport_conditional_kNm':math.fsum(dp[sl]),'Dforce_trap_model_kNm':math.fsum(df[sl]),
               'energy_gap_kNm':math.fsum(df[i]-dp[i] for i in range(start,end)),
               'product_term_kNm':math.fsum(prod[sl]),'residual_work_kNm':math.fsum(rw[sl]),
               'identity_residual_kNm':math.fsum(ident[sl]),'negative_Dport_increment_count':sum(x<0 for x in dp[sl])}
            compare(z,windows[(link,case,t[start])]);wins.append(z)
            sbp_windows.append(math.fsum((math.fsum(rw[sl]),-f[end]*residual[end],f[start]*residual[start],math.fsum(adjoint[sl]))))
        sortedwins=sorted(wins,key=lambda z:(-abs(z['energy_gap_kNm']),z['window_start_s']))[:3]
        sortedints=sorted(local,key=lambda z:(-abs(z['energy_gap_increment_kNm']),z['interval_index']))[:3]
        for ours,provided in [(sortedwins,[x for x in worstwin if (x['Link'],x['Case'])==(link,case)]),
                              (sortedints,[x for x in worstint if (x['Link'],x['Case'])==(link,case)])]:
            assert len(provided)==3
            for x,y in zip(ours,provided):compare(x,y)
        sbp_error=math.fsum((R,-boundary,Q))
        assert min(prod)>=0 and max(map(abs,ident))<tolerance and max(map(abs,ci))<tolerance
        assert max(abs(sbp_error),max(map(abs,sbp_interval)),max(map(abs,sbp_windows)),max(map(abs,csbp)))<tolerance
        result.append({'record':row,'sbp':{'residual_work_direct_kNm':R,'boundary_Fr_kNm':boundary,
            'sum_ravg_deltaF_kNm':Q,'residual_work_boundary_minus_sum_kNm':boundary-Q,'full_identity_residual_kNm':sbp_error,
            'max_interval_identity_abs_kNm':max(map(abs,sbp_interval)),'max_window_identity_abs_kNm':max(map(abs,sbp_windows)),
            'max_prefix_identity_abs_kNm':max(map(abs,csbp))},'worst_three_windows':sortedwins,'worst_three_intervals':sortedints,
            'minimum_Dport_source_cells':{'start_P':raw[imin]['P_I_cell'],'end_P':raw[imin+1]['P_I_cell'],
                'start_U1':raw[imin]['U1_cell'],'end_U1':raw[imin+1]['U1_cell']},'windows_checked':len(wins)})
        count_intervals+=n-1;count_windows+=len(wins)
    assert (count_intervals,count_windows)==(16290,326)
    for item in input_snapshot:
        p=Path(item['path']);assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes']
    record={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,
            'python':platform.python_version(),'script_sha256':sha(Path(__file__)),
            'method':'stdlib scalar powers, Kahan prefix integrals, fsum, factored spring increments; no source execution/NumPy/fit/XLSX',
            'fixed_parameters':{'alpha':alpha,'a':a,'b':b},'intervals_checked':count_intervals,'windows_checked':count_windows,
            'worst_windows_checked':18,'worst_intervals_checked':18,'maximum_source_difference_by_field':differences,
            'records':result,'inputs_before_and_after':input_snapshot,
            'limits':['Conditional model arithmetic only; no true dissipation, all88, engineering reduction or innovation certification.',
                      'Summation by parts is a classical discrete identity, not a continuous quadrature error bound.',
                      'Small displacement RMSE alone does not imply small residual work; signed cancellation retained.',
                      'Full interval arrays read locally; no new full-array outputs or uploads.']}
    out.mkdir(parents=True,exist_ok=True);target=out/'review_summary.json';assert not target.exists()
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'checks_passed':True,'recorded_at':record['recorded_at'],'intervals':count_intervals,'windows':count_windows,
        'rows':[{'Link':x['record']['Link'],'Case':x['record']['Case'],'gap':x['record']['Dforce_minus_Dport_kNm'],
                 'product':x['record']['discrete_product_term_kNm'],'residual_work':x['record']['regression_residual_work_kNm'],
                 'negative_count':x['record']['negative_Dport_increment_count_unclipped'],'sbp':x['sbp']} for x in result]},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();run(args.source,args.out)
