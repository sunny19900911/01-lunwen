"""Independent standard-library Maxwell integral profile: scalar/Kahan + Gram solve.

No import/call of the experiment solver; no Excel reads or new records.
"""
import argparse
import csv
import hashlib
import json
import math
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))


def inner(a, b): return math.fsum(x * y for x, y in zip(a, b))


def design(data, alpha):
    f = data['F']; t = data['t']; power = 1 / alpha
    g = [math.copysign(abs(x) ** power, x) if x else 0.0 for x in f]
    cumulative = [0.0]; total = compensation = 0.0
    for i in range(1, len(f)):
        increment = math.fsum((g[i-1], g[i])) * (t[i] - t[i-1]) / 2
        adjusted = increment - compensation; newer = total + adjusted
        compensation = (newer - total) - adjusted; total = newer; cumulative.append(total)
    return [x - f[0] for x in f], cumulative


def singular_info(x, y):
    a, b, c = inner(x, x), inner(y, y), inner(x, y)
    largest = (a + b + math.hypot(a - b, 2*c)) / 2
    smallest = (a*b - c*c) / largest
    assert smallest > 0
    s1, s2 = math.sqrt(largest), math.sqrt(smallest)
    rank = int(s1 > math.ulp(1.0) * len(x) * s1) + int(s2 > math.ulp(1.0) * len(x) * s1)
    return s1, s2, rank


def diagnostics(x, y):
    nx, ny = math.sqrt(inner(x, x)), math.sqrt(inner(y, y))
    z1, z2 = [v/nx for v in x], [v/ny for v in y]
    r1, r2, rank = singular_info(x, y); s1, s2, srank = singular_info(z1, z2)
    return z1, z2, {'raw_rank': rank, 'scaled_rank': srank, 'raw_smax': r1, 'raw_smin': r2,
                         'raw_condition': r1/r2, 'scaled_smax': s1, 'scaled_smin': s2,
                         'scaled_condition': s1/s2, 'column1_norm': nx, 'column2_norm': ny}


def predict(x, y, a, b): return [math.fsum((a*u, b*v)) for u, v in zip(x, y)]


def metrics(target, predicted):
    e = [p-y for p, y in zip(predicted, target)]; n = len(e)
    sse = inner(e, e); rmse = math.sqrt(sse/n); rms = math.sqrt(inner(target, target)/n)
    return {'RMSE_m': rmse, 'RMSE_mm': 1000*rmse, 'MAE_m': math.fsum(map(abs, e))/n,
            'max_abs_residual_m': max(map(abs, e)), 'mean_residual_m': math.fsum(e)/n,
            'end_residual_m': e[-1], 'y_RMS_m': rms, 'RMSE_over_y_RMS': rmse/rms,
            'SSE_m2': sse}


def fit(x, y, target):
    z1, z2, info = diagnostics(x, y)
    g11, g22, g12 = inner(z1, z1), inner(z2, z2), inner(z1, z2)
    h1, h2 = inner(z1, target), inner(z2, target)
    determinant = g11*g22 - g12*g12
    assert determinant > 0
    u = (h1*g22 - h2*g12) / determinant
    v = (h2*g11 - h1*g12) / determinant
    candidates = [('both_zero', 0., 0.), ('a_only_b_zero', max(h1/g11, 0.), 0.),
                  ('b_only_a_zero', 0., max(h2/g22, 0.))]
    if u >= 0 and v >= 0: candidates.append(('interior' if u > 0 and v > 0 else 'interior_zero_boundary', u, v))
    evaluated = [(inner(e := [math.fsum((aa*p, bb*q, -t)) for p, q, t in zip(z1, z2, target)], e),
                  name, aa, bb) for name, aa, bb in candidates]
    _, active, aa, bb = min(evaluated)
    return aa/info['column1_norm'], bb/info['column2_norm'], u/info['column1_norm'], v/info['column2_norm'], active, info


def run(experiment, out):
    out.mkdir(parents=True, exist_ok=False)
    work = experiment / 'R002-integral-regression'
    protocol = json.loads((work/'protocol.json').read_text(encoding='utf-8'))
    assert sha(work/'protocol.json') == '8c7e2733c30a9090a442d3861193c3e27ef7f7ba5688542c2afc8597ff364719'
    assert sha(experiment/'R002-条件积分回归诊断.md') == '08c4b9e5f9c9c44d88a344565bd2e34f53fe9f39f2b63beb6892d13f5b1adaeb'
    author_run = json.loads((work/'run_record_r002.json').read_text(encoding='utf-8'))
    for item in author_run['files']: assert sha(work/item['file']) == item['sha256']
    inputs = [(work/x['path']).resolve() for x in protocol['inputs']]
    assert all(sha(p) == meta['sha256'] for p, meta in zip(inputs, protocol['inputs']))
    data = {}; conversion_errors = {}; zero_counts = {}
    for device, p in zip(('K2', 'K5'), inputs):
        rr = rows(p); assert len(rr) == 2501
        assert all(r['Link'] == device and r['Case'] == 'RH4X' for r in rr)
        t = [float(r['t_s']) for r in rr]; f = [float(r['P_I_kN']) for r in rr]
        d = [float(r['U1_m']) for r in rr]
        assert all(math.isfinite(v) for column in [t,f,d] for v in column)
        assert all(t[i] == i*.02 for i in range(2501))
        assert all(float(r['P_I_kN']) == float(r['P_J_kN']) for r in rr)
        conversion_errors[device] = max(abs(float(r['U1_m']) - float(r['U1_mm'])/1000) for r in rr)
        assert conversion_errors[device] < 1e-18
        zero_counts[device] = sum(v == 0 for v in f)
        data[device] = {'t':t, 'F':f, 'd':d, 'y':[x-d[0] for x in d]}
    references = rows(work/'alpha_profile_r002.csv'); assert len(references) == 91
    profile = []; maximum_relative_difference = 0.; maximum_absolute_difference = 0.

    def compare(value, ref, field):
        nonlocal maximum_relative_difference, maximum_absolute_difference
        if isinstance(value, bool): assert str(value) == ref
        elif isinstance(value, str): assert value == ref
        else:
            ref = float(ref); absolute = abs(value-ref)
            maximum_absolute_difference = max(maximum_absolute_difference, absolute)
            maximum_relative_difference = max(maximum_relative_difference, absolute/max(abs(ref),1e-300))
            atol = 1e-25 if field in ['a_m_per_kN','b_m_per_s_kN_power_inverse_alpha','unconstrained_a','unconstrained_b'] else 1e-18
            assert math.isclose(value, ref, abs_tol=atol, rel_tol=2e-8), (field,value,ref)
    for i, ref in zip(range(10,101), references):
        alpha = i/50; assert alpha == float(ref['alpha'])
        x,y = design(data['K2'],alpha); xt,yt = design(data['K5'],alpha)
        a,b,ua,ub,active,info = fit(x,y,data['K2']['y'])
        _,_,testinfo = diagnostics(xt,yt)
        row = {'alpha':alpha, 'a_m_per_kN':a, 'b_m_per_s_kN_power_inverse_alpha':b,
               'k_kN_per_m':1/a if a>0 else None, 'c_kN_s_per_m_power_alpha':b**(-alpha) if b>0 else None,
               'strictly_positive_finite_parameters':a>0 and b>0, 'active_set':active,
               'unconstrained_a':ua, 'unconstrained_b':ub}
        row.update({'K2_'+k:v for k,v in info.items()})
        row.update({'K2_'+k:v for k,v in metrics(data['K2']['y'],predict(x,y,a,b)).items()})
        row.update({'K5_transfer_'+k:v for k,v in metrics(data['K5']['y'],predict(xt,yt,a,b)).items()})
        row.update({'K5_design_'+k:v for k,v in testinfo.items()})
        assert set(row) == set(ref)
        for k,v in row.items(): compare(v,ref[k],k)
        profile.append(row)
    best = min(profile,key=lambda r:r['K2_SSE_m2'])
    summary = json.loads((work/'fit_summary_r002.json').read_text(encoding='utf-8'))
    assert best['alpha'] == summary['best_grid_row']['alpha'] == .3
    sets = {str(q):[r['alpha'] for r in profile if r['K2_RMSE_m'] <= best['K2_RMSE_m']*(1+q)] for q in [.01,.05,.1]}
    assert all(v == summary['descriptive_profile_sets'][k]['alpha_values'] for k,v in sets.items())
    assert all(r['active_set']=='interior' and r['K2_scaled_rank']==r['K5_design_scaled_rank']==2 for r in profile)
    residual_refs = rows(work/'all_point_residuals_r002.csv'); assert len(residual_refs)==5002
    residual_map = {(r['device'],float(r['t_s'])):r for r in residual_refs}; assert len(residual_map)==5002
    point_max_difference = {}; conditional_metrics = {}
    shot = protocol['optional_screenshot_check']; sa=shot['alpha']
    for device in ('K2','K5'):
        dd=data[device];x,y=design(dd,best['alpha']);p=predict(x,y,best['a_m_per_kN'],best['b_m_per_s_kN_power_inverse_alpha'])
        sx,sy=design(dd,sa);sp=predict(sx,sy,1/shot['k_assumed_kN_per_m'],shot['c_assumed_kN_s_over_m_power_alpha']**(-1/sa))
        largest=0.
        for j,t in enumerate(dd['t']):
            rr=residual_map[(device,t)];assert rr['case']=='RH4X'
            expected={'native_P_I_kN':dd['F'][j],'native_U1_m':dd['d'][j],'delta_U1_m':dd['y'][j],
                      'K2_selected_model_predicted_delta_U1_m':p[j], 'residual_pred_minus_data_m':p[j]-dd['y'][j],
                      'screenshot_conditional_predicted_delta_U1_m':sp[j]}
            for k,v in expected.items():
                difference=abs(v-float(rr[k]));largest=max(largest,difference)
                assert math.isclose(v,float(rr[k]),abs_tol=2e-14,rel_tol=1e-10),(device,j,k)
        point_max_difference[device]=largest
        conditional_metrics[device]=metrics(dd['y'],sp)
        ref=next(r for r in summary['screenshot_conditional_metrics'] if r['device']==device)
        for k,v in conditional_metrics[device].items(): compare(v,str(ref[k]),k)
    with (out/'review_alpha_profile.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(profile[0]),lineterminator='\n');w.writeheader();w.writerows(profile)
    files=inputs+[experiment/'R002-条件积分回归诊断.md']+[work/n for n in ['protocol.json','fit_integral_model.py','fit_summary_r002.json',
          'run_record_r002.json','alpha_profile_r002.csv','all_point_residuals_r002.csv','screenshot_conditional_residuals_r002.csv']]
    record={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,
            'method':'Python scalar signed power; compensated cumulative trapezoid; analytical 2x2 scaled Gram NNLS active sets; singular values via stable Gram eigenvalues. No NumPy/lstsq/SVD solver reused.',
            'python':platform.python_version(),'script_sha256':sha(Path(__file__)),'alpha_count':len(profile),
            'selected_by':'K2 SSE only; K5 coefficients never refit','best_grid_row':best,'descriptive_sets':sets,
            'all_profile_fields_checked':True,'all_point_rows_checked':5002,'point_max_absolute_difference_m':point_max_difference,
            'maximum_relative_profile_numeric_difference':maximum_relative_difference,'maximum_absolute_profile_numeric_difference_mixed_units':maximum_absolute_difference,
            'unit_conversion_max_error_m':conversion_errors,'zero_force_rows_retained':zero_counts,'screenshot_conditional_metrics':conditional_metrics,
            'inputs':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],
            'limits':['Conditional native-P integral relation; force conjugacy/mass interface not certified.',
                      'Same RH4X other device is not independent-earthquake validation.',
                      'Finite alpha-grid minimum and fixed-alpha rank do not prove true or globally unique physical parameters.']}
    (out/'review_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:record[k] for k in ['checks_passed','alpha_count','best_grid_row','descriptive_sets','point_max_absolute_difference_m','maximum_relative_profile_numeric_difference','unit_conversion_max_error_m']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--experiment',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args();run(a.experiment,a.out)
