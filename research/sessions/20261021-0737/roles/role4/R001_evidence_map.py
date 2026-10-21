from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,statistics as st
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[4];OLD=R/'research/sessions/20261020-1844/roles/role4'
START=datetime.fromisoformat('2026-10-20T23:42:38+00:00');DEADLINE=START+timedelta(minutes=10)
def now():return datetime.now(timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rc(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
names=['R002-all14-main-axis-168.csv','R002-common-six-main-axis-72.csv','R004-caption-and-observations.md'];bindings=[{'path':str(OLD/n),'bytes':(OLD/n).stat().st_size,'sha256':sha(OLD/n)} for n in names]
js('R001-definition-input-freeze.json',{'utc':now().isoformat(),'start_utc':START.isoformat(),'deadline_utc':DEADLINE.isoformat(),'code_sha256':sha(Path(__file__)),'inputs':bindings,'definitions':{'reduction_percent':'100*(1-P_M/P_B); reuse frozen native Bottom absolute peaks kN; P_B is baseline, P_M is modal-damping reference','story_axis_summary':'7 directional cases per axis; minimum, median and maximum with actual matching case and both absolute peaks; median is middle of 7 sorted actual observations','case_minimum':'minimum over 12 layers; ties within 1e-10 percentage points all retained','bottom_baseline':'same-case Story1 reduction only','mean_baseline':'unweighted arithmetic mean of 12 layer reduction percentages; not a total-building force reduction','baseline_omission_gap':'baseline reduction minus actual least layer reduction, percentage points; descriptive contrast, no pass/fail threshold','recurrence':'report directional-case counts and deduplicated wave-family counts separately','groups':'common RH4/SHW4/SHW7 X/Y six cases versus remaining R1/SHW3/SHW5/SHW6 X/Y eight; no holdout or independent-test designation'},'exclude':'no fitting, native arrays, new ODE, spectral/modal decomposition, actual-device causal comparison or formal candidate algorithm'})
raw=rc(OLD/names[0]);common=rc(OLD/names[1]);assert len(raw)==168 and len(common)==72
key=lambda r:(r['Case'],r['Story']);base={key(r):r for r in raw};assert len(base)==168 and all(base[key(r)]==r for r in common)
cc={r['Case'] for r in common};cases=sorted({r['Case'] for r in raw});rows=[]
for i,r in enumerate(raw,2):
 assert now()<DEADLINE
 assert r['Location']=='Bottom' and r['input_main_axis']=='True' and r['denominator_resolved']=='True'
 b=float(r['P0_kN']);m=float(r['P3_kN']);v=float(r['peak_reduction_percent']);assert b>1e-10 and abs(v-100*(1-m/b))<1e-10
 rows.append({**r,'source_CSV_line':i,'input_scope':'common_three_families' if r['Case'] in cc else 'other_four_families','model_comparison':'baseline versus modal-damping reference; native Bottom QT, not isolated QS'})
cs('R001-all14-evidence-map-168.csv',rows)
summ=[]
for axis in ['X','Y']:
 for s in range(1,13):
  rr=sorted([r for r in rows if r['Axis']==axis and r['Story']=='Story'+str(s)],key=lambda r:(float(r['peak_reduction_percent']),r['Case']));assert len(rr)==7
  out={'Story':'Story'+str(s),'Axis':axis,'directional_cases':7,'wave_families':7}
  for name,r in zip(['minimum','median','maximum'],[rr[0],rr[3],rr[-1]]):
   out.update({name+'_reduction_percent':float(r['peak_reduction_percent']),name+'_Case':r['Case'],name+'_input_scope':r['input_scope'],name+'_P_B_kN':float(r['P0_kN']),name+'_P_M_kN':float(r['P3_kN'])})
  out['range_percentage_points']=out['maximum_reduction_percent']-out['minimum_reduction_percent'];summ.append(out)
cs('R001-story-axis-summary-24.csv',summ)
comparisons=[];minimum_records=[]
for case in cases:
 rr=[r for r in rows if r['Case']==case];assert len(rr)==12
 mn=min(float(r['peak_reduction_percent']) for r in rr);worst=[r for r in rr if abs(float(r['peak_reduction_percent'])-mn)<=1e-10];bottom=next(r for r in rr if r['Story']=='Story1');mean=float(np.mean([float(r['peak_reduction_percent']) for r in rr]));wr=worst[0]
 comparisons.append({'Case':case,'Axis':case[-1],'wave_family':case[:-1],'input_scope':wr['input_scope'],'minimum_Stories':';'.join(r['Story'] for r in worst),'minimum_reduction_percent':mn,'minimum_P_B_kN':float(wr['P0_kN']),'minimum_P_M_kN':float(wr['P3_kN']),'bottom_is_minimum':any(r['Story']=='Story1' for r in worst),'bottom_reduction_percent':float(bottom['peak_reduction_percent']),'bottom_P_B_kN':float(bottom['P0_kN']),'bottom_P_M_kN':float(bottom['P3_kN']),'unweighted_12_story_mean_reduction_percent':mean,'bottom_minus_minimum_pp':float(bottom['peak_reduction_percent'])-mn,'mean_minus_minimum_pp':mean-mn})
 minimum_records.extend(worst)
cs('R001-case-baselines-14.csv',comparisons)
freq=[]
for scope,select in [('all_14',cases),('common_six',sorted(cc)),('other_eight',sorted(set(cases)-cc))]:
 for axis in ['X','Y','X_and_Y']:
  for s in range(1,13):
   rr=[r for r in minimum_records if r['Case'] in select and (axis=='X_and_Y' or r['Axis']==axis) and r['Story']=='Story'+str(s)]
   freq.append({'scope':scope,'Axis':axis,'Story':'Story'+str(s),'case_minimum_count':len(rr),'deduplicated_wave_family_count':len({r['wave_family'] for r in rr}),'Cases':';'.join(sorted(r['Case'] for r in rr)),'wave_families':';'.join(sorted({r['wave_family'] for r in rr}))})
cs('R001-minimum-layer-recurrence-108.csv',freq)
bottom_example=max(comparisons,key=lambda r:r['bottom_minus_minimum_pp']);mean_example=max(comparisons,key=lambda r:r['mean_minus_minimum_pp']);repeated=max([r for r in freq if r['scope']=='all_14' and r['Axis']=='X_and_Y'],key=lambda r:r['case_minimum_count']);n_bottom=sum(r['bottom_is_minimum'] for r in comparisons);n_common_bottom=sum(r['bottom_is_minimum'] for r in comparisons if r['Case'] in cc)
result={'finished_utc':now().isoformat(),'rows_preserved':168,'common_rows':72,'other_rows':96,'all14_bottom_is_minimum_count':n_bottom,'common6_bottom_is_minimum_count':n_common_bottom,'most_recurrent_minimum_layer':repeated,'bottom_omission_example':bottom_example,'mean_omission_example':mean_example,'new_fit_or_ODE':0,'new_raw_or_array_reads':0}
js('R001-results.json',result)
def example(r):return f"{r['Case']}：{r['minimum_Stories']}减幅{r['minimum_reduction_percent']:.4f}%（基准{r['minimum_P_B_kN']:.4f}kN、参考{r['minimum_P_M_kN']:.4f}kN）；底层为{r['bottom_reduction_percent']:.4f}%，12层不加权平均为{r['unweighted_12_story_mean_reduction_percent']:.4f}%。"
text=f'''# R001 工程证据地图与两个简单基线

已有14工况×12层168条原生Bottom主方向剪力峰全部保留。按方向分别统计每层7工况的最小、中位和最大减幅，并列对应工况和两模型绝对峰；中位值来自7条实际记录的中间一条，不合成新的响应峰。共同RH4/SHW4/SHW7三波族六方向工况与其余四波族八工况逐行标记，不称训练/独立测试。

## 对工程评价的直接启示

底层恰为最小减幅层的工况为{n_bottom}/14；共同六工况为{n_common_bottom}/6。因此，只看底层不能稳定定位本组数据中改善较少的楼层。跨输入重复出现最多的是{repeated['Story']}，见于{repeated['case_minimum_count']}个方向工况、{repeated['deduplicated_wave_family_count']}个去重波族；次数不解释为独立验证样本数。

底层评价遗漏的具体例子：{example(bottom_example)} 底层减幅比该工况最小层高{bottom_example['bottom_minus_minimum_pp']:.4f}个百分点。

全楼平均评价遗漏的具体例子：{example(mean_example)} 平均值比最小层高{mean_example['mean_minus_minimum_pp']:.4f}个百分点。这里的“全楼平均”仅为12个楼层减幅的算术平均，不是质量加权指标、总剪力减幅或任一时刻的受力预算。

## 使用步骤及交付

先按同模型基准/参考与同输入配对，保留各自完整时程绝对峰；再逐层检查，按X/Y分别查看多输入最小—中位—最大范围；同时把每工况最小层与底层及简单平均并列，保留分歧与不利层。改善较少不等于承载力薄弱，也不是改布局建议。

24行分层统计见R001-story-axis-summary-24.csv；14工况基线比较见R001-case-baselines-14.csv；分组/分方向重复出现记录见108行R001-minimum-layer-recurrence-108.csv；全部168行见R001-all14-evidence-map-168.csv。小表只描述基准与增加模态阻尼参考模型的原生QT变化，不扣成主体QS，不归因实际装置，不分解真实模态。正式候选定义待角色①提出、角色②审核后另算。

本项只有冻结CSV的统计汇总，未读大表/时程数组，未拟合或运行ODE。源表SHA、预先定义和代码SHA见R001-definition-input-freeze.json。实际命令为捆绑Python -X utf8 R001_evidence_map.py；执行退出0，运行记录及冻结时点见交付清单。
'''
(O/'R001-engineering-note.md').write_text(text,encoding='utf-8')
assert all(sha(Path(b['path']))==b['sha256'] for b in bindings)
for n,c in [('R001-all14-evidence-map-168.csv',168),('R001-story-axis-summary-24.csv',24),('R001-case-baselines-14.csv',14),('R001-minimum-layer-recurrence-108.csv',108)]:assert len(rc(O/n))==c
end=now();js('R001-delivery-manifest.json',{'status':'frozen','start_utc':START.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_10min':end<=DEADLINE,'exit_code':0,'python_executable':'C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','command':'python -X utf8 R001_evidence_map.py','numpy':np.__version__,'source_hashes_unchanged':True,'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R001*')) if p.is_file()]})
print(json.dumps(result,ensure_ascii=False));print('FROZEN '+end.isoformat())
