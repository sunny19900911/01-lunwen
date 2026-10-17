"""Independent 192-record stdlib review; NumPy only decodes frozen paired NPZ."""
import argparse
import csv
import hashlib
import json
import math
import platform
from collections import defaultdict
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


def packed(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))


def run(source,out):
    expected={'report.md':'dcc918095f28780f3810cdce51a984d638677379f7e43dad2369f4e284211b38',
              'device_record_summary_r006.csv':'8d359f9c86b544aaa6c573618a375eef7beb8f02070dc223f2802ce3fe31864d',
              'local_paired_histories_r006.npz':'65be34f8125e5e7f2aee90ebe5a4b2612cfe717d84abf0886789a1bc75709340',
              'delivery_manifest_r006.json':'a059cd405c89b8861f57bb8a5af8e68a2b241173673de1fb4efd28d702cd7e6d'}
    for name,checksum in expected.items():assert sha(source/name)==checksum,name
    delivery=json.loads((source/'delivery_manifest_r006.json').read_text(encoding='utf-8'))
    files=[source/'delivery_manifest_r006.json']
    for x in delivery['files']:
        f=source/x['name'];assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes'];files.append(f)
    p=json.loads((source/'protocol.json').read_text(encoding='utf-8'))
    for x in [p['coverage_ref'],p['training_ref']]+p['crosschecks']:
        f=Path(x['path']);assert sha(f)==x['sha256'];files.append(f)
    snapshots=[{'path':str(f.resolve()),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]
    trained=json.loads(Path(p['training_ref']['path']).read_text(encoding='utf-8'))['best_grid_row']
    alpha=p['fixed_parameters']['alpha'];a=p['fixed_parameters']['a_m_per_kN'];b=p['fixed_parameters']['b']
    assert (alpha,a,b)==(.3,2.0006042528243313e-6,1.1798190016520894e-9)
    assert (alpha,a,b)==(trained['alpha'],trained['a_m_per_kN'],trained['b_m_per_s_kN_power_inverse_alpha'])
    coverage=readcsv(Path(p['coverage_ref']['path']));bylink=defaultdict(list)
    for x in coverage:bylink[x['Link']].append(x)
    cases=p['cases'];assert cases==['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']
    common={link for link,rr in bylink.items() if len(rr)==6 and {x['Case'] for x in rr}==set(cases) and all(x['complete_export_grid']=='True' for x in rr)}
    targets={(x['Link'],x['Case']):x for x in p['targets']};assert len(targets)==192
    assert {key[0] for key in targets}==common and len(common)==32 and 'K12' not in common
    assert {key for key in targets}=={(link,case) for link in common for case in cases}
    for story in p['stories']:assert len({x['Link'] for x in p['targets'] if x['Story']==story})==8
    manifest=json.loads((source/'local_history_manifest_r006.json').read_text(encoding='utf-8'))
    descriptors={x['key']:x for x in manifest['arrays']};assert len(descriptors)==192
    columns=['t_s','P_I_kN','P_J_kN','U1_mm','U1_m','force_I_row','force_J_row','deformation_row']
    assert p['paired_columns']==columns
    refs={(x['Link'],x['Case']):x for x in readcsv(source/'device_record_summary_r006.csv')};assert len(refs)==192
    six={};cross_counts={}
    for ref in p['crosschecks']:
        old=readcsv(Path(ref['path']));key=(old[0]['Link'],old[0]['Case']);assert key not in six;six[key]=old
    differences={};point_count=interval_count=0;results=[];diagnostics=[]
    def compare(ours,theirs):
        assert set(ours)==set(theirs),(set(ours)-set(theirs),set(theirs)-set(ours))
        for k,v in ours.items():
            ref=theirs[k]
            if k.endswith('_json'):assert json.loads(v)==json.loads(ref),(k,v,ref)
            elif isinstance(v,bool):assert v==(ref=='True'),(k,v,ref)
            elif isinstance(v,int):assert v==int(ref),(k,v,ref)
            elif isinstance(v,str):assert v==ref,(k,v,ref)
            else:
                diff=abs(v-float(ref));differences[k]=max(differences.get(k,0),diff)
                assert diff<=2e-13+abs(float(ref))*2e-11,(k,v,ref)
    with np.load(source/'local_paired_histories_r006.npz',allow_pickle=False) as arrays:
        assert set(arrays.files)==set(descriptors)=={link+'__'+case for link,case in targets}
        for key,target in targets.items():
            link,case=key;name=link+'__'+case;description=descriptors[name]
            assert (description['Link'],description['Case'],description['Story'])==(link,case,target['Story'])
            assert description['columns']==columns
            data=arrays[name].tolist();n=int(target['expected_n']);assert description['shape']==[n,8] and len(data)==n
            assert n=={'RH4X':2501,'RH4Y':2501,'SHW4X':2951,'SHW4Y':2951,'SHW7X':2696,'SHW7Y':2696}[case]
            assert all(len(row)==8 and all(math.isfinite(v) for v in row) for row in data)
            t=[x[0] for x in data];f=[x[1] for x in data];mm=[x[3] for x in data];d=[x[4] for x in data]
            assert all(ti==i*.02 for i,ti in enumerate(t))
            assert all(x[1]==x[2] and x[3]/1000==x[4] for x in data)
            for col,field,stride in [(5,'P_I_source_rows',2),(6,'P_J_source_rows',2),(7,'U_source_rows',1)]:
                rows=[x[col] for x in data];assert all(v==int(v) and v>=4 for v in rows)
                assert [int(rows[0]),int(rows[-1])]==json.loads(target[field])
                assert all(v==rows[0]+i*stride for i,v in enumerate(rows))
            assert all(x[6]==x[5]+1 for x in data)
            if key in six:
                old=six[key];assert len(old)==n
                for i,x in enumerate(old):
                    assert (x['Link'],x['Case'],x['Story'])==(link,case,target['Story'])
                    assert [float(x[c]) for c in columns]==data[i]
                    assert x['P_I_cell']=='I'+str(int(data[i][5])) and x['P_J_cell']=='I'+str(int(data[i][6]))
                    assert x['U1_cell']=='H'+str(int(data[i][7]))
                cross_counts[name]=n
            h=[math.copysign(abs(v)**(1/alpha),v) if v else 0. for v in f]
            ih=[0.]+prefix([(t[i+1]-t[i])*math.fsum((h[i],h[i+1]))/2 for i in range(n-1)])
            residual=[math.fsum((a*(f[i]-f[0]),b*ih[i],-(d[i]-d[0]))) for i in range(n)]
            w=[];us=[];dp=[];df=[];prod=[];rw=[];identity=[]
            for i in range(n-1):
                avg=math.fsum((f[i],f[i+1]))/2;dt=t[i+1]-t[i]
                wi=avg*(d[i+1]-d[i]);ui=a*(f[i+1]-f[i])*avg
                di=b*dt*math.fsum((f[i]*h[i],f[i+1]*h[i+1]))/2
                pi=b*dt*(f[i+1]-f[i])*(h[i+1]-h[i])/4
                ri=avg*(residual[i+1]-residual[i]);dpi=wi-ui
                w.append(wi);us.append(ui);dp.append(dpi);df.append(di);prod.append(pi);rw.append(ri)
                identity.append(math.fsum((di,-dpi,-pi,-ri)))
            W=math.fsum(w);U=a*(f[-1]**2-f[0]**2)/2;D=W-U;Df=math.fsum(df);P=math.fsum(prod);R=math.fsum(rw)
            total_identity=math.fsum((Df,-D,-P,-R));tol=1e-12*max(1,abs(W),abs(Df))
            assert min(prod)>=0 and abs(total_identity)<tol and max(map(abs,identity))<tol
            maxf=max(map(abs,f));maxu=max(map(abs,mm));imin=min(range(n-1),key=lambda i:dp[i])
            force=[{'t_s':t[i],'signed_P_kN':f[i],'P_I_cell':'I'+str(int(data[i][5])),
                    'P_J_cell':'I'+str(int(data[i][6]))} for i in range(n) if abs(f[i])==maxf]
            deform=[{'t_s':t[i],'signed_U1_mm':mm[i],'U1_cell':'H'+str(int(data[i][7]))} for i in range(n) if abs(mm[i])==maxu]
            row={'Link':link,'Story':target['Story'],'Case':case,'n_points':n,'max_abs_native_P_kN':maxf,
                 'force_peak_controllers_json':packed(force),'max_abs_native_U1_mm':maxu,'U1_peak_controllers_json':packed(deform),
                 'Wtrap_native_kNm':W,'DeltaUs_conditional_kNm':U,'Dport_conditional_kNm':D,'Dforce_trap_model_kNm':Df,
                 'Dforce_minus_Dport_kNm':Df-D,'discrete_product_kNm':P,'regression_residual_work_kNm':R,
                 'identity_residual_kNm':total_identity,'max_interval_identity_abs_kNm':max(map(abs,identity)),
                 'negative_Dport_increment_count_unclipped':sum(v<0 for v in dp),'minimum_Dport_increment_kNm':dp[imin],
                 'minimum_Dport_interval_start_s':t[imin],'minimum_Dport_interval_end_s':t[imin+1],
                 'all_three_streams_complete':True,'I_J_pointwise_equal':True,'local_array_key':name}
            compare(row,refs[key]);results.append(row)
            diagnostics.append({'Link':link,'Case':case,'initial_force_kN':f[0],'initial_displacement_m':d[0],
                'minimum_product_increment_kNm':min(prod),'arithmetic_tolerance_kNm':tol,
                'minimum_Dport_P_I_cells':['I'+str(int(data[imin][5])),'I'+str(int(data[imin+1][5]))],
                'minimum_Dport_U1_cells':['H'+str(int(data[imin][7])),'H'+str(int(data[imin+1][7]))]})
            point_count+=n;interval_count+=n-1
    assert (point_count,interval_count)==(521472,521280) and len(cross_counts)==6 and sum(cross_counts.values())==16296
    ranks=[];groups=[];boundary_ties=0
    for case in cases:
        for story in p['stories']:
            group=[x for x in results if (x['Case'],x['Story'])==(case,story)];assert len(group)==8
            summary={'Case':case,'Story':story,'n_devices':8,
                'force_range_kN':[min(x['max_abs_native_P_kN'] for x in group),max(x['max_abs_native_P_kN'] for x in group)],
                'Wtrap_range_kNm':[min(x['Wtrap_native_kNm'] for x in group),max(x['Wtrap_native_kNm'] for x in group)],
                'Dport_range_kNm':[min(x['Dport_conditional_kNm'] for x in group),max(x['Dport_conditional_kNm'] for x in group)]}
            for metric in ['max_abs_native_P_kN','Dport_conditional_kNm']:
                ordered=sorted(group,key=lambda x:(-x[metric],int(x['Link'][1:])));hi=ordered[1][metric];lo=ordered[6][metric]
                summary[metric+'_cutoffs']={'top2_minimum':hi,'bottom2_maximum':lo}
                for side in ['top2','bottom2']:
                    chosen=[x for x in ordered if x[metric]>=hi] if side=='top2' else [x for x in ordered if x[metric]<=lo]
                    boundary_ties+=len(chosen)>2;summary[metric+'_'+side]=[x['Link'] for x in chosen]
                    for x in chosen:
                        ranks.append({'Case':case,'Story':story,'metric':metric,'side_with_exact_boundary_ties':side,
                            'rank_desc_competition':1+sum(y[metric]>x[metric] for y in group),'Link':x['Link'],'value':x[metric],
                            'max_abs_native_P_kN':x['max_abs_native_P_kN'],'Wtrap_native_kNm':x['Wtrap_native_kNm'],'Dport_conditional_kNm':x['Dport_conditional_kNm']})
            groups.append(summary)
    rankref=readcsv(source/'within_story_rank_extremes_r006.csv');assert len(rankref)==len(ranks)==192
    for x,y in zip(ranks,rankref):compare(x,y)
    report=(source/'report.md').read_text(encoding='utf-8');report_rows=[]
    for line in report.splitlines():
        if line.startswith('| '):
            cells=[x.strip() for x in line.strip('|').split('|')]
            if len(cells) in [5,6] and cells[0] in cases and cells[1] in p['stories']:report_rows.append(cells)
    assert len(report_rows)==48
    def show(values):return '\u3001'.join(values)
    def span(values):return '\u2013'.join(format(v,'.7g') for v in values)
    for i,x in enumerate(groups):
        assert report_rows[i]==[x['Case'],x['Story'],span(x['force_range_kN']),show(x['max_abs_native_P_kN_top2']),show(x['max_abs_native_P_kN_bottom2'])]
        assert report_rows[i+24]==[x['Case'],x['Story'],span(x['Wtrap_range_kNm']),span(x['Dport_range_kNm']),
                                 show(x['Dport_conditional_kNm_top2']),show(x['Dport_conditional_kNm_bottom2'])]
    for x in snapshots:
        f=Path(x['path']);assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes']
    result={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,'python':platform.python_version(),
        'numpy_decode_version':np.__version__,'script_sha256':sha(Path(__file__)),
        'method':'NumPy decode/to-list only; scalar signed powers, Kahan cumulative trapezoid, factored spring increments and math.fsum; no source code invocation/Excel/fit.',
        'fixed_parameters':{'alpha':alpha,'a':a,'b':b},'groups_checked':192,'devices_checked':32,'paired_points_checked':point_count,
        'intervals_checked':interval_count,'rank_rows_checked':len(ranks),'case_story_groups_checked':24,'report_distribution_rows_checked':48,
        'six_frozen_CSV_exact_eight_column_crosschecks':cross_counts,'maximum_source_difference_by_field':differences,
        'max_abs_total_identity_residual_kNm':max(abs(x['identity_residual_kNm']) for x in results),
        'max_interval_identity_abs_kNm':max(x['max_interval_identity_abs_kNm'] for x in results),
        'negative_Dport_increment_groups':sum(x['negative_Dport_increment_count_unclipped']>0 for x in results),
        'exact_rank_boundary_tie_selections':boundary_ties,'force_peak_tie_groups':sum(len(json.loads(x['force_peak_controllers_json']))>1 for x in results),
        'U1_peak_tie_groups':sum(len(json.loads(x['U1_peak_controllers_json']))>1 for x in results),
        'records':results,'record_diagnostics':diagnostics,'case_story_rank_summary':groups,'inputs_before_and_after':snapshots,
        'source_workbook_identity_inherited_not_reread':{'sha256':p['source_sha256'],'bytes':p['source_bytes']},
        'limits':['Frozen NPZ arithmetic review, not another original-sheet reader; tail extra/duplicate exclusions inherited from same-SHA R001.',
                  'Fixed fitted parameters and P/U1 physical port remain conditional; no true dissipation/all88/global direction/event/layout/reduction certification.',
                  'Classical discrete model identity does not bound continuous integration error or independently validate physics.',
                  'Source R006 candidate only; downstream affine intervals/manuscript not reviewed. Full histories local only; no new time-history arrays/upload.']}
    out.mkdir(parents=True,exist_ok=True);target=out/'review_summary.json';assert not target.exists()
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ['recorded_at','checks_passed','groups_checked','paired_points_checked','intervals_checked','rank_rows_checked',
        'max_abs_total_identity_residual_kNm','max_interval_identity_abs_kNm','negative_Dport_increment_groups','exact_rank_boundary_tie_selections',
        'force_peak_tie_groups','U1_peak_tie_groups','maximum_source_difference_by_field']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();run(args.source,args.out)
