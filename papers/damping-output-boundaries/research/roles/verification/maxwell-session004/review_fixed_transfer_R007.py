"""Independent fixed-parameter scalar transfer review; no Excel/NumPy/refitting.

Reads frozen local full CSVs, writes only a four-row metric/worst-point JSON.
"""
import argparse
import csv
import hashlib
import json
import math
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def csv_rows(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def norm2(x): return math.fsum(v*v for v in x)


def run(experiment, out):
    out.mkdir(parents=True, exist_ok=False)
    work=experiment/'R003-cross-case-transfer'
    protocol_path=work/'protocol.json'
    assert digest(protocol_path)=='84fe57efb19cf7dbbeb8b8ef5deb0f432eee3dacf41e0f21c29a5cc89d620fae'
    summary_path=work/'transfer_summary_r003.json'
    assert digest(summary_path)=='13a955378a4e30f5920dd332f9e748a9a82ceb6321484f1d6ade28452fda1395'
    source=json.loads(summary_path.read_text(encoding='utf-8'))
    protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
    assert digest(work/'check_fixed_transfer.py')==source['code_sha256']
    for item in source['outputs']: assert digest(work/item['file'])==item['sha256']
    for item in source['source_documents']: assert digest(Path(item['path']))==item['sha256']
    training=(work/protocol['training_summary']).resolve()
    assert digest(training)==protocol['training_summary_sha256']
    trained=json.loads(training.read_text(encoding='utf-8'))['best_grid_row']
    alpha=float(protocol['fixed_parameters']['alpha'])
    a=float(protocol['fixed_parameters']['a_m_per_kN']);b=float(protocol['fixed_parameters']['b_m_per_s_kN_power_inverse_alpha'])
    assert (alpha,a,b)==(trained['alpha'],trained['a_m_per_kN'],trained['b_m_per_s_kN_power_inverse_alpha'])
    assert alpha==.3 and a==2.0006042528243313e-6 and b==1.1798190016520894e-9
    targets=[tuple(x) for x in protocol['targets']]
    assert set(targets)=={('K2','SHW4X'),('K2','SHW7X'),('K5','SHW4X'),('K5','SHW7X')}
    full=csv_rows(work/'local_all_residuals_r003.csv');assert len(full)==11294
    refs={(r['Link'],r['Case'],float(r['t_s'])):r for r in full};assert len(refs)==len(full)
    metric_refs={(r['Link'],r['Case']):r for r in csv_rows(work/'transfer_metrics_r003.csv')}
    worst=csv_rows(work/'worst_points_r003.csv');assert len(worst)==20
    small=[];input_paths=[];all_diffs=[]
    for link,case in targets:
        path=work/f'local_input_{link}_{case}_r003.csv';input_paths.append(path)
        rows=csv_rows(path);n=2951 if case=='SHW4X' else 2696
        assert len(rows)==n
        times=[float(r['t_s']) for r in rows]
        assert all(t==i*.02 for i,t in enumerate(times))
        assert times[0]==0 and times[-1]==(59 if case=='SHW4X' else 53.9)
        assert all((r['Link'],r['Story'],r['Case'])==(link,'Story11',case) for r in rows)
        F=[float(r['P_I_kN']) for r in rows];d=[float(r['U1_m']) for r in rows]
        assert all(math.isfinite(v) for column in [times,F,d] for v in column)
        assert all(float(r['P_I_kN'])==float(r['P_J_kN']) for r in rows)
        unit_error=max(abs(float(r['U1_m'])-float(r['U1_mm'])/1000) for r in rows)
        assert unit_error==0
        for name in ['force_I_row','force_J_row','deformation_row']:
            rr=[int(r[name]) for r in rows];assert all(y>x for x,y in zip(rr,rr[1:]))
        for r in rows:
            assert int(r['force_J_row'])==int(r['force_I_row'])+1
            assert r['P_I_cell']=='I'+r['force_I_row'] and r['P_J_cell']=='I'+r['force_J_row']
            assert r['U1_cell']=='H'+r['deformation_row']
        power=1/alpha
        g=[math.copysign(abs(f)**power,f) if f else 0. for f in F]
        integral=[0.];total=compensation=0.
        for i in range(1,n):
            increment=math.fsum((g[i-1],g[i]))*(times[i]-times[i-1])/2
            adjusted=increment-compensation;new=total+adjusted
            compensation=(new-total)-adjusted;total=new;integral.append(total)
        target=[v-d[0] for v in d]
        prediction=[math.fsum((a*(f-F[0]),b*j)) for f,j in zip(F,integral)]
        error=[p-y for p,y in zip(prediction,target)]
        rmse=math.sqrt(norm2(error)/n);rms=math.sqrt(norm2(target)/n)
        metrics={'Link':link,'Case':case,'n':n,'alpha_fixed':alpha,'a_fixed':a,'b_fixed':b,
                 'F0_kN_observed':F[0],'d0_m_observed':d[0],
                 'zero_force_points_retained':sum(v==0 for v in F),'max_abs_force_kN':max(map(abs,F)),
                 'RMSE_m':rmse,'RMSE_mm':1000*rmse,'MAE_m':math.fsum(map(abs,error))/n,
                 'max_abs_residual_m':max(map(abs,error)),'mean_residual_m':math.fsum(error)/n,
                 'end_residual_m':error[-1],'delta_d_RMS_m':rms,'RMSE_over_delta_d_RMS':rmse/rms}
        assert set(metrics)==set(metric_refs[(link,case)])
        for name,v in metrics.items():
            ref=metric_refs[(link,case)][name]
            if isinstance(v,str):assert v==ref
            else:assert math.isclose(v,float(ref),abs_tol=1e-18,rel_tol=2e-8),(link,case,name)
        max_pred_difference=max_residual_difference=0.
        for i,r in enumerate(rows):
            rr=refs[(link,case,times[i])]
            assert all(rr[name]==v for name,v in r.items()),'Raw input/source metadata changed in residual file'
            assert math.isclose(target[i],float(rr['observed_delta_d_m']),abs_tol=1e-20,rel_tol=1e-12)
            pd=abs(prediction[i]-float(rr['fixed_model_predicted_delta_d_m']))
            ed=abs(error[i]-float(rr['residual_pred_minus_data_m']))
            assert pd<2e-14 and ed<2e-14
            max_pred_difference=max(max_pred_difference,pd);max_residual_difference=max(max_residual_difference,ed)
        indices=sorted(range(n),key=lambda i:(-abs(error[i]),times[i]))[:5]
        provided=[r for r in worst if (r['Link'],r['Case'])==(link,case)]
        assert len(provided)==5
        assert [float(r['t_s']) for r in provided]==[times[i] for i in indices]
        for i,rr in zip(indices,provided):
            assert all(rr[name]==v for name,v in rows[i].items())
            assert math.isclose(error[i],float(rr['residual_pred_minus_data_m']),abs_tol=2e-14,rel_tol=1e-10)
        worst5=[{'t_s':times[i],'residual_m':error[i],'P_I_kN':F[i],'observed_delta_d_m':target[i],
                 'predicted_delta_d_m':prediction[i],'P_I_cell':rows[i]['P_I_cell'],
                 'U1_cell':rows[i]['U1_cell']} for i in indices]
        small.append({'metrics':metrics,'unit_conversion_max_error_m':unit_error,
                      'max_prediction_difference_from_source_m':max_pred_difference,
                      'max_residual_difference_from_source_m':max_residual_difference,'worst_five':worst5,
                      'source_row_ranges':{k:[int(rows[0][k]),int(rows[-1][k])] for k in ['force_I_row','force_J_row','deformation_row']}})
        all_diffs.append(max_residual_difference)
    assert sum(x['metrics']['n'] for x in small)==11294
    files=input_paths+[protocol_path,summary_path,work/'check_fixed_transfer.py',work/'run_record_r003.json',
                      work/'transfer_metrics_r003.csv',work/'local_all_residuals_r003.csv',work/'worst_points_r003.csv',
                      experiment/'R003-固定参数跨工况迁移.md',training]
    record={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,
            'script_sha256':digest(Path(__file__)),'python':platform.python_version(),
            'method':'Independent standard-library scalar signed power, Kahan cumulative trapezoid, math.fsum metrics; no fit/NumPy/source script invocation.',
            'fixed_parameters':{'alpha':alpha,'a':a,'b':b},'all_point_residuals_checked':11294,
            'worst_points_checked':20,'maximum_residual_difference_m':max(all_diffs),'groups':small,
            'source_workbook_sha256_inherited_not_rehashed':source['raw_source_sha256'],
            'inputs':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files],
            'limits':['Given-native-force conditional constitutive transfer, not earthquake-input forward response prediction.',
                      'Input/event independence, actual database port/mass mapping and all88 uniform parameters not certified.',
                      'No independent raw-XLSX extraction repeated; only frozen local inputs checked.',
                      'Full arrays remain local, no output time-history arrays written.']}
    (out/'review_summary.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'checks_passed':True,'all_point_residuals_checked':11294,'maximum_residual_difference_m':max(all_diffs),
                      'groups':[{'metrics':g['metrics'],'worst':g['worst_five'][0]} for g in small]},ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--experiment',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args();run(a.experiment,a.out)
