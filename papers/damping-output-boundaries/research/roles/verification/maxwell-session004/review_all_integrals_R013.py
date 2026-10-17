"""Independent fixed-integral review under pre-frozen R013 inputs/rules."""
import argparse
import csv
import hashlib
import json
import math
import platform
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def prefix(values):
    out=[];total=correction=0.
    for v in values:
        y=v-correction;new=total+y;correction=(new-total)-y;total=new;out.append(total)
    return out


def rms(values):return math.hypot(*values)/math.sqrt(len(values))


def relative(rmse,denominator):
    return (None,'undefined_zero_denominator') if denominator==0 else (rmse/denominator,'defined')


def worst(group):
    ordered=sorted([x for x in group if x['relative_RMSE'] is not None],key=lambda x:(-x['relative_RMSE'],int(x['Link'][1:])))
    if not ordered:return []
    cutoff=ordered[min(1,len(ordered)-1)]['relative_RMSE']
    return [x for x in ordered if x['relative_RMSE']>=cutoff]


def run(source,review_protocol,out):
    assert sha(review_protocol)=='df8fc9c355c4ed4943827c80dd9b9f757789c1cb7ea1db3327e7e8b5bc2a06e2'
    frozen=json.loads(review_protocol.read_text(encoding='utf-8'))
    for x in frozen['inputs']:
        p=Path(x['path']);assert sha(p)==x['sha256'] and p.stat().st_size==x['bytes']
    p=json.loads((source/'protocol.json').read_text(encoding='utf-8'));refs={k:Path(v['path']) for k,v in p['inputs'].items()}
    assert sha(source/'protocol.json')==frozen['source_protocol_sha256']=='8dd93c139aff83e515b8d7bc837cc33ca7bce4630452d52ecfa3cefff9d3e952'
    assert p['only_training_record']==['K2','RH4X']
    alpha=p['fixed_parameters']['alpha'];a=p['fixed_parameters']['a_m_per_kN'];b=p['fixed_parameters']['b']
    training=json.loads(refs['R002_training'].read_text(encoding='utf-8'))['best_grid_row']
    assert (alpha,a,b)==(.3,2.0006042528243313e-6,1.1798190016520894e-9)
    assert (alpha,a,b)==(training['alpha'],training['a_m_per_kN'],training['b_m_per_s_kN_power_inverse_alpha'])
    # Explicit finite semantics checks, before reading actual numeric arrays.
    assert relative(0.,0.)==(None,'undefined_zero_denominator') and relative(1.,0.)==(None,'undefined_zero_denominator')
    assert relative(0.,2.)==(0.,'defined')
    assert worst([{'Link':'K1','relative_RMSE':None}])==[]
    synthetic=[{'Link':'K1','relative_RMSE':3.},{'Link':'K2','relative_RMSE':2.},{'Link':'K3','relative_RMSE':2.},{'Link':'K4','relative_RMSE':None}]
    assert len(worst(synthetic))==3
    manifest=json.loads(refs['array_manifest'].read_text(encoding='utf-8'));assert len(manifest['arrays'])==192
    original=readcsv(source/'all_device_integral_metrics_r007.csv');assert len(original)==192
    oldrows={(x['Link'],x['Case']):x for x in original};assert len(oldrows)==192
    six={}
    for x in p['six_CSV_crosschecks']:
        rr=readcsv(Path(x['file']));key=rr[0]['Link']+'__'+rr[0]['Case'];assert key not in six;six[key]=rr
    differences={};control_differences={}
    def number(name,v,ref,bucket):
        if v is None:assert ref is None or ref=='';return
        if name in ['t_s','t0_s','t1_s','P_I_kN','U1_m','observed_delta_d_m']:assert v==float(ref),(name,v,ref);return
        diff=abs(v-float(ref));bucket[name]=max(bucket.get(name,0),diff)
        tol=2e-12 if name in ['relative_RMSE','relative_RMSE_percent'] else 2e-14
        assert math.isclose(v,float(ref),abs_tol=tol,rel_tol=1e-9),(name,v,ref)
    def compare(x,y):
        assert set(x)==set(y),(set(x)-set(y),set(y)-set(x))
        for name,v in x.items():
            if name=='max_residual_controllers_json':
                ours=json.loads(v);theirs=json.loads(y[name]);assert len(ours)==len(theirs)
                for c,d in zip(ours,theirs):
                    assert set(c)==set(d)
                    for k,value in c.items():
                        if isinstance(value,str):assert value==d[k]
                        else:number(k,value,d[k],control_differences)
            elif isinstance(v,str):assert v==y[name],(name,v,y[name])
            elif isinstance(v,int):assert v==int(y[name])
            else:number(name,v,y[name],differences)
    columns=['t_s','P_I_kN','P_J_kN','U1_mm','U1_m','force_I_row','force_J_row','deformation_row']
    records=[];point_count=0;cross={};npz_stat=refs['paired_npz'].stat()
    with np.load(refs['paired_npz'],allow_pickle=False) as arrays:
        assert set(arrays.files)=={x['key'] for x in manifest['arrays']}
        for meta in manifest['arrays']:
            assert meta['columns']==columns
            data=arrays[meta['key']].tolist();n=len(data);case=meta['Case'];link=meta['Link']
            assert meta['shape']==[n,8] and n=={'RH4X':2501,'RH4Y':2501,'SHW4X':2951,'SHW4Y':2951,'SHW7X':2696,'SHW7Y':2696}[case]
            assert all(len(row)==8 and all(math.isfinite(v) for v in row) for row in data)
            t=[x[0] for x in data];f=[x[1] for x in data];d=[x[4] for x in data]
            assert all(v==i*.02 for i,v in enumerate(t)) and all(x[1]==x[2] and x[3]/1000==x[4] for x in data)
            for col,stride in [(5,2),(6,2),(7,1)]:assert all(x[col]==int(x[col]) and x[col]==data[0][col]+i*stride for i,x in enumerate(data))
            assert all(x[6]==x[5]+1 for x in data)
            if meta['key'] in six:
                old=six[meta['key']];assert len(old)==n
                for i,x in enumerate(old):
                    assert [float(x[c]) for c in columns]==data[i] and (x['Link'],x['Case'],x['Story'])==(link,case,meta['Story'])
                    assert x['P_I_cell']=='I'+str(int(data[i][5])) and x['P_J_cell']=='I'+str(int(data[i][6])) and x['U1_cell']=='H'+str(int(data[i][7]))
                cross[meta['key']]=n
            h=[math.copysign(abs(v)**(1/alpha),v) if v else 0. for v in f]
            integral=[0.]+prefix([(t[i+1]-t[i])*math.fsum((h[i],h[i+1]))/2 for i in range(n-1)])
            observed=[v-d[0] for v in d]
            pred=[math.fsum((a*(f[i]-f[0]),b*integral[i])) for i in range(n)]
            residual=[pred[i]-observed[i] for i in range(n)]
            denominator=rms(observed);rmse=rms(residual);ratio,status=relative(rmse,denominator);maxabs=max(map(abs,residual))
            controls=[{'t_s':t[i],'signed_residual_m':residual[i],'observed_delta_d_m':observed[i],'predicted_delta_d_m':pred[i],
                'P_I_kN':f[i],'U1_m':d[i],'P_I_cell':'I'+str(int(data[i][5])),'P_J_cell':'I'+str(int(data[i][6])),
                'U1_cell':'H'+str(int(data[i][7]))} for i in range(n) if abs(residual[i])==maxabs]
            row={'Link':link,'Story':meta['Story'],'Case':case,'record_role':'sole_training_record' if (link,case)==('K2','RH4X') else 'same_model_conditional_check',
                'n_points':n,'t0_s':t[0],'t1_s':t[-1],'zero_force_points_retained':sum(v==0 for v in f),'F0_kN_observed':f[0],'d0_m_observed':d[0],
                'delta_d_RMS_m':denominator,'RMSE_m':rmse,'MAE_m':math.fsum(map(abs,residual))/n,'max_abs_residual_m':maxabs,
                'max_residual_controllers_json':json.dumps(controls,separators=(',',':')),'mean_residual_m':math.fsum(residual)/n,
                'end_residual_m':residual[-1],'relative_RMSE':ratio,'relative_RMSE_percent':None if ratio is None else ratio*100,
                'relative_RMSE_status':status,'local_array_key':meta['key']}
            compare(row,oldrows[(link,case)]);records.append(row);point_count+=n
    assert point_count==521472 and len(cross)==6 and sum(cross.values())==16296
    assert sum(x['record_role']=='sole_training_record' for x in records)==1
    lookup={(x['Link'],x['Case']):x for x in records};cross_metrics=[]
    def metric_check(label,key,expected):
        diff={}
        for field,ref in expected.items():
            v=lookup[key][field];tol=2e-12 if field=='relative_RMSE' else 2e-14
            assert math.isclose(v,float(ref),abs_tol=tol,rel_tol=1e-9);diff[field]=v-float(ref)
        cross_metrics.append({'reference':label,'Link':key[0],'Case':key[1],'differences':diff})
    for label,fit in [('R002',training),('R004',json.loads(refs['R004_review_numbers'].read_text(encoding='utf-8'))['best_grid_row'])]:
        for link in ['K2','K5']:
            pre='K2_' if link=='K2' else 'K5_transfer_'
            expected={k:fit[pre+k] for k in ['RMSE_m','MAE_m','max_abs_residual_m','mean_residual_m','end_residual_m']}
            expected.update({'delta_d_RMS_m':fit[pre+'y_RMS_m'],'relative_RMSE':fit[pre+'RMSE_over_y_RMS']});metric_check(label,(link,'RH4X'),expected)
    for label,old in [('R003',readcsv(refs['R003_metrics'])),('R007',[x['metrics'] for x in json.loads(refs['R007_review_numbers'].read_text(encoding='utf-8'))['groups']])]:
        for x in old:
            expected={k:x[k] for k in ['RMSE_m','MAE_m','max_abs_residual_m','mean_residual_m','end_residual_m','delta_d_RMS_m']}
            expected['relative_RMSE']=x['RMSE_over_delta_d_RMS'];metric_check(label,(x['Link'],x['Case']),expected)
    assert len(cross_metrics)==12
    worstrows=[];case_summary=[];author_summary=json.loads((source/'summary_r007.json').read_text(encoding='utf-8'))
    for case in p['cases']:
        group=[x for x in records if x['Case']==case];assert len(group)==32
        chosen=worst(group);defined=[x for x in group if x['relative_RMSE'] is not None]
        for x in chosen:worstrows.append({'case_relative_error_rank':1+sum(y['relative_RMSE']>x['relative_RMSE'] for y in defined),**x})
        c={'Case':case,'n_groups':32,'undefined_ratio_count':32-len(defined),'relative_RMSE_min':min((x['relative_RMSE'] for x in defined),default=None),
            'relative_RMSE_max':max((x['relative_RMSE'] for x in defined),default=None),'RMSE_m_min':min(x['RMSE_m'] for x in group),
            'RMSE_m_max':max(x['RMSE_m'] for x in group),'worst2_with_exact_ties':[x['Link'] for x in chosen]}
        old=next(x for x in author_summary['case_summaries'] if x['Case']==case)
        assert c.keys()==old.keys()
        for k,v in c.items():
            if isinstance(v,float):number(k,v,old[k],differences)
            else:assert v==old[k]
        case_summary.append(c)
    old=readcsv(source/'worst2_by_case_r007.csv');assert len(old)==len(worstrows)==12
    for x,y in zip(worstrows,old):compare(x,y)
    # Verify actual rounded report ranges and all displayed worst-point locators.
    lines=[line for line in (source/'report.md').read_text(encoding='utf-8').splitlines() if line.startswith('| ')]
    for c in case_summary:
        line=next(line for line in lines if line.startswith('| '+c['Case']+' | 32 |'))
        expected=[c['Case'],'32',format(100*c['relative_RMSE_min'],'.6g')+'\u2013'+format(100*c['relative_RMSE_max'],'.6g'),
            format(c['RMSE_m_min'],'.6g')+'\u2013'+format(c['RMSE_m_max'],'.6g'),str(c['undefined_ratio_count']),'\u3001'.join(c['worst2_with_exact_ties'])]
        assert [v.strip() for v in line.strip('|').split('|')]==expected
    for r in worstrows:
        cells=[r['Case'],r['Link']+'/'+r['Story']]+[format(r[k],'.6g') for k in ['delta_d_RMS_m','RMSE_m','relative_RMSE_percent','max_abs_residual_m']]
        controls=json.loads(r['max_residual_controllers_json'])
        cells+=['; '.join(format(x['t_s'],'.8g')+' / '+format(x['signed_residual_m'],'+.6g') for x in controls),
                '; '.join(x['P_I_cell']+'/'+x['U1_cell'] for x in controls)]
        assert any([v.strip() for v in line.strip('|').split('|')]==cells for line in lines)
    for x in frozen['inputs']:
        f=Path(x['path']);assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes']
    after=refs['paired_npz'].stat();assert (npz_stat.st_size,npz_stat.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    result={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,'script_sha256':sha(Path(__file__)),
        'review_protocol_sha256':sha(review_protocol),'rules_frozen_at':frozen['frozen_at_before_new_numeric_decode'],
        'python':platform.python_version(),'numpy_decode_version':np.__version__,
        'method':'NPZ decode only; independent scalar powers, Kahan cumulative trapezoid, fsum errors and hypot RMS. No author calculate/fit/Excel.',
        'groups_checked':192,'paired_points_checked':point_count,'training_records':1,'same_model_conditional_checks':191,
        'maximum_metric_difference_from_source_by_field':differences,'maximum_controller_difference_by_field':control_differences,
        'max_residual_tie_groups':sum(len(json.loads(x['max_residual_controllers_json']))>1 for x in records),
        'undefined_relative_ratio_groups':sum(x['relative_RMSE'] is None for x in records),'worst_record_rows_checked':12,
        'ranking_cutoff_tie_expansion_cases':sum(len(worst([x for x in records if x['Case']==case]))>2 for case in p['cases']),
        'zero_denominator_and_exact_rank_tie_synthetic_checks':True,'six_CSV_crosschecks':cross,'old_metric_crosschecks':cross_metrics,
        'case_summaries':case_summary,'records':records,'worst_records':worstrows,'failures':[],
        'inputs_before_and_after':frozen['inputs'],'limits':['Given observed force conditional integral check; not earthquake-input forward prediction or independent/unseen event validation.',
            'Only K2/RH4X is training; all other191 same-model checks, including previously used records.',
            'Absolute errors, RMS denominators, signed bias and failure/undefined states retained; no engineering acceptance threshold.',
            'True parameters/port/mass/current software/whole88/convergence/physical energy/causal reduction remain uncertified; tail coverage inherits R001.',
            'No original Excel/author script/refit/new full arrays/upload/shared/Git actions.']}
    out.mkdir(parents=True,exist_ok=True);target=out/'review_summary.json';assert not target.exists()
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ['recorded_at','checks_passed','groups_checked','paired_points_checked','max_residual_tie_groups',
        'undefined_relative_ratio_groups','ranking_cutoff_tie_expansion_cases','maximum_metric_difference_from_source_by_field','maximum_controller_difference_by_field','case_summaries']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,type=Path);parser.add_argument('--review-protocol',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();run(args.source,args.review_protocol,args.out)
