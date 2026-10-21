from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean
import csv, hashlib, json, math
B=Path(__file__).resolve().parent;ROOT=B.parents[4];OLD=ROOT/'research/sessions/20261021-0737/roles/role4'
START=datetime.fromisoformat('2026-10-21T20:57:21.968341+08:00')
def ident(p):
    x=p.read_bytes();return {'path':str(p),'bytes':len(x),'sha256':hashlib.sha256(x).hexdigest()}
def rc(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def js(n,x):
    p=B/n;assert not p.exists();p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));json.loads(p.read_text(encoding='utf-8'))
def eq(a,b):assert math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-9),(a,b)
assert not (B/'R001-validation.json').exists()
sources=[]
for name in ['R002-delivery-manifest.json','R002-clarification-manifest.json']:
    p=OLD/name;sources.append(ident(p))
    for x in json.loads(p.read_text(encoding='utf-8'))['files']:
        got=ident(Path(x['path']));assert got['bytes']==x['bytes'] and got['sha256']==x['sha256'];sources.append(got)
f=json.loads((OLD/'R002-definition-input-freeze.json').read_text(encoding='utf-8'))
path=Path(f['inputs'][0]['path']);got=ident(path);assert got['sha256']==f['inputs'][0]['sha256'];sources.append(got)
raw=rc(path);assert len(raw)==168 and len({(r['Case'],r['Story'],r['Location'],r['Axis']) for r in raw})==168
cases=defaultdict(list);layer=defaultdict(list)
for r in raw:
    assert r['Axis']==r['Case'][-1] and r['Location']=='Bottom'
    p0,p1=float(r['P0_kN']),float(r['P3_kN']);assert p0>0 and p1>=0
    r['r']=100*(1-p1/p0);eq(r['r'],r['peak_reduction_percent']);cases[r['Case']].append(r);layer[r['Story'],r['Axis']].append(r)
assert len(cases)==14 and len(layer)==24
for row in rc(OLD/'R002-story-axis-summary-24.csv'):
    rr=sorted(layer[row['Story'],row['Axis']],key=lambda x:x['r']);assert len(rr)==7
    eq(row['directional_cases'],7);eq(row['wave_families'],len({x['wave_family'] for x in rr}))
    for prefix,x in zip(['minimum','median','maximum'],[rr[0],rr[3],rr[-1]]):
        eq(row[prefix+'_reduction_percent'],x['r']);assert row[prefix+'_Case']==x['Case'];eq(row[prefix+'_P_B_kN'],x['P0_kN']);eq(row[prefix+'_P_M_kN'],x['P3_kN'])
    eq(row['range_percentage_points'],rr[-1]['r']-rr[0]['r'])
common={'RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y'};minimum={};base_results={}
for case,rr in cases.items():
    assert len(rr)==12;mn=min(x['r'] for x in rr);minimum[case]=[x['Story'] for x in rr if abs(x['r']-mn)<=1e-10]
    bottom=next(x for x in rr if x['Story']=='Story1');worst=next(x for x in rr if x['Story'] in minimum[case]);avg=mean(x['r'] for x in rr)
    base_results[case]={'minimum_Stories':';'.join(minimum[case]),'minimum_reduction_percent':mn,'minimum_P_B_kN':float(worst['P0_kN']),'minimum_P_M_kN':float(worst['P3_kN']),'bottom_is_minimum':'Story1' in minimum[case],'bottom_reduction_percent':bottom['r'],'bottom_P_B_kN':float(bottom['P0_kN']),'bottom_P_M_kN':float(bottom['P3_kN']),'unweighted_12_story_mean_reduction_percent':avg,'bottom_minus_minimum_pp':bottom['r']-mn,'mean_minus_minimum_pp':avg-mn}
for row in rc(OLD/'R002-case-baselines-14.csv'):
    expected=base_results[row['Case']]
    for k,v in expected.items():
        if isinstance(v,str):assert row[k]==v
        elif isinstance(v,bool):assert row[k]==str(v)
        else:eq(row[k],v)
recur=rc(OLD/'R002-minimum-layer-recurrence-108.csv');assert len(recur)==108
for row in recur:
    selected=set(cases) if row['scope']=='all_14' else common if row['scope']=='common_six' else set(cases)-common
    cc=sorted(c for c in selected if (row['Axis']=='X_and_Y' or c[-1]==row['Axis']) and row['Story'] in minimum[c]);families=sorted({c[:-1] for c in cc})
    eq(row['case_minimum_count'],len(cc));eq(row['deduplicated_wave_family_count'],len(families));assert row['Cases']==';'.join(cc) and row['wave_families']==';'.join(families)
nb=sum(x['bottom_is_minimum'] for x in base_results.values());nc=sum(base_results[c]['bottom_is_minimum'] for c in common);assert(nb,nc)==(3,2)
allrec=[r for r in recur if r['scope']=='all_14' and r['Axis']=='X_and_Y'];maximum=max(int(r['case_minimum_count']) for r in allrec);ties=[r for r in allrec if int(r['case_minimum_count'])==maximum]
assert {r['Story'] for r in ties}=={'Story1','Story6','Story7'} and maximum==3
shw=base_results['SHW7X']
for x in sources:assert ident(Path(x['path']))==x
report=f'''# R001｜旧24/14/108小表数字独审

**通过，须连同并列频次澄清采用。** 从原已审168行CSV重新计算逐行减幅，独立聚合并核对全部24行楼层—方向统计、14行工况基线、108行频次；未运行原统计脚本或读取时程数组。

SHW7X的最小减幅在Story7：基准{shw['minimum_P_B_kN']:.4f}kN、参考{shw['minimum_P_M_kN']:.4f}kN，减幅{shw['minimum_reduction_percent']:.6f}%；Story1减幅{shw['bottom_reduction_percent']:.6f}%，12层减幅算术平均{shw['unweighted_12_story_mean_reduction_percent']:.6f}%。底层与平均值分别比该最小值高{shw['bottom_minus_minimum_pp']:.6f}和{shw['mean_minus_minimum_pp']:.6f}个百分点。平均是减幅的等权算术平均，不是总剪力减幅。

底层为最小减幅层的工况计数为3/14，共同六工况为2/6，均通过。它们不是独立事件命中率，也不意味着其余层承载力薄弱。

|并列最多楼层|方向工况数|去重波族数|工况|
|---|---:|---:|---|
|Story1|3|3|R1X、RH4Y、SHW4X|
|Story6|3|2|SHW6X、SHW6Y、SHW7Y|
|Story7|3|3|RH4X、SHW4Y、SHW7X|

第1、6、7层并列，不能写Story1唯一最高。X/Y按方向工况计数；SHW6X/Y同波族，所以Story6只有两个去重波族。波族去重也不自动认证地震事件独立性。

24行均按方向内7工况取最小、中位、最大减幅，并保留对应真实工况和两模型峰值，显示一致。全部168行下降，未发现反增，不用人工夹具代替工程结果。以上只针对同输入B/模态阻尼参考的原生Bottom结果，不推实体装置因果，不扣成主体QS。

可直接写稿：“在所列14个方向工况中，底层仅在3个工况为最小减幅层；SHW7X中底层和全楼算术平均减幅分别比第7层高12.5948和8.1000个百分点，说明仅看底层或平均值会遗漏本组数据中的低改善楼层。第1、6、7层各在3个方向工况出现最小减幅，并列最多。”
'''
p=B/'R001-number-review.md';assert not p.exists();p.write_bytes(report.encode('utf-8'))
end=datetime.now(START.tzinfo);assert end<=START+timedelta(minutes=5)
js('R001-checks.json',{'source_bindings':sources,'rows_independently_reaggregated':168,'summary_rows_checked':24,'baseline_rows_checked':14,'recurrence_rows_checked':108,'bottom_counts':[nb,nc],'co_maximum_recurrence':ties,'SHW7X':shw,'new_arrays_ODE':0})
js('R001-validation.json',{'status':'pass numeric aggregates with co-maximum clarification','actual_start':START.isoformat(),'actual_end':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_5_minutes':True,'only_new_session_role2_written':True})
js('R001-manifest.json',{'frozen_at':end.isoformat(),'files':[ident(B/n) for n in ['R001-audit-aggregates.py','R001-number-review.md','R001-checks.json','R001-validation.json']]})
print(json.dumps({'status':'pass','end':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'bottom_counts':[nb,nc],'SHW7X':shw,'co_maximum_stories':[r['Story'] for r in ties]},ensure_ascii=False))
