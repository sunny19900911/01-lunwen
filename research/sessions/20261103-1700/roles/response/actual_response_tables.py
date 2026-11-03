from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,statistics,math
import numpy as np
H=Path(__file__).resolve().parent;H.mkdir(parents=True,exist_ok=True);R=H.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def table(name,rows):
 p=H/name;assert not p.exists()
 with p.open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(name,obj):
 p=H/name;assert not p.exists();p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prior=R/'research/sessions/20261103-1458/roles/response/three-model-common-six-records-72.csv'
priorrows=read(prior);assert len(priorrows)==72
W=R.parent/'W5-重燃双塔连体'
B=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存'
D=W/'research/maxwell-20261017/experiments/R001/core-cache'
mb=json.loads((B/'manifest.json').read_text(encoding='utf-8'));md=json.loads((D/'manifest.json').read_text(encoding='utf-8'))
tb=mb['tables']['Story Forces'];td=md['tables']['Story Forces'];cb=tb.get('columns',tb.get('value_columns'));cd=td.get('columns',td.get('value_columns'))
pb=B/tb['cache'];pd=D/td['cache']
inputs=[prior,B/'manifest.json',D/'manifest.json',pb,pd]
sources=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in inputs]
js('input-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'code_sha256':sha(Path(__file__)),'inputs':sources,'scope':'Actual configured-device model D versus baseline B; six shared cases; preserved Bottom VX/VY outputs; no M reference borrowed'})
def key(g):return tuple(g['keys'][x]for x in ['Output Case','Story','Location'])
kb={key(g):k for k,g in tb['groups'].items()};kd={key(g):k for k,g in td['groups'].items()}
rows=[]
with np.load(pb,allow_pickle=False)as zb,np.load(pd,allow_pickle=False)as zd:
 for old in sorted(priorrows,key=lambda r:(r['Case'],int(r['Story'][5:]))):
  case,story,axis=old['Case'],old['Story'],old['Axis'];k=(case,story,'Bottom')
  assert old['Location']=='Bottom' and old['units']=='kN'
  ab=zb[kb[k]];ad=zd[kd[k]];t=ab[:,cb.index('Time')];tt=ad[:,cd.index('Time')]
  assert np.array_equal(t,tt),(case,story,'time axes unequal')
  assert np.all(np.diff(t)>0)and np.isfinite(ab).all()and np.isfinite(ad).all()
  yb=ab[:,cb.index('V'+axis)];yd=ad[:,cd.index('V'+axis)]
  ib=int(np.argmax(abs(yb)));idd=int(np.argmax(abs(yd)));pB=float(abs(yb[ib]));pD=float(abs(yd[idd]));assert pB>0
  assert abs(pB-float(old['P_B_kN']))<1e-9 and abs(pD-float(old['P_D_kN']))<1e-9
  assert float(t[ib])==float(old['t_B_s'])and float(t[idd])==float(old['t_D_s'])
  A=float(abs(yd[ib]));rpeak=100*(1-pD/pB);rat=100*(1-A/pB);d=100*(pD-A)/pB
  assert d>=-1e-12 and abs(rat-d-rpeak)<1e-11
  rows.append({'Case':case,'wave_family':case[:-1],'Axis':axis,'Story':story,'Location':'Bottom','unit_force':'kN','unit_time':'s',
    'P_B_kN':pB,'P_D_kN':pD,'B_signed_at_own_peak_kN':float(yb[ib]),'D_signed_at_own_peak_kN':float(yd[idd]),
    't_B_s':float(t[ib]),'t_D_s':float(t[idd]),'D_at_tB_signed_kN':float(yd[ib]),'A_abs_D_at_tB_kN':A,
    'r_peak_percent':rpeak,'r_at_percent':rat,'d_pp':d,'identity_residual_pp':rat-d-rpeak,
    'absolute_peak_time_shift_s':abs(float(t[idd]-t[ib])),'same_saved_peak_time':bool(t[ib]==t[idd]),
    'n_saved':len(t),'t_start_s':float(t[0]),'t_end_s':float(t[-1]),'saved_time_axes_exact':True,
    'B_peak_source_row':int(ab[ib,cb.index('SourceRow')]),'D_peak_source_row':int(ad[idd,cd.index('SourceRow')]),
    'D_source_row_at_B_peak':int(ad[ib,cd.index('SourceRow')]),'B_cache_key':kb[k],'D_cache_key':kd[k],
    'B_tied_abs_peak_count':int(np.sum(abs(yb)==pB)),'D_tied_abs_peak_count':int(np.sum(abs(yd)==pD)),
    'peak_selection':'first saved absolute maximum; all tied counts retained',
    'scope':'Existing native baseline B and actual-device D model outputs; not uniform modal reference or isolated QS; model/input correspondence per companion audit'})
assert len(rows)==72 and len({(r['Case'],r['Story'],r['Axis'])for r in rows})==72
table('actual-versus-baseline-time-peak-72.csv',rows)
ranges=[]
for axis in ['X','Y']:
 for story in range(1,13):
  g=sorted([r for r in rows if r['Axis']==axis and r['Story']==f'Story{story}'],key=lambda r:r['Case'])
  assert len(g)==3;lo=min(g,key=lambda r:r['r_peak_percent']);hi=max(g,key=lambda r:r['r_peak_percent']);ordered=sorted(g,key=lambda r:r['r_peak_percent']);med=ordered[1];dem=max(g,key=lambda r:r['P_D_kN'])
  ranges.append({'Axis':axis,'Story':f'Story{story}','n_cases':3,
   'min_reduction_percent':lo['r_peak_percent'],'min_case':lo['Case'],'median_reduction_percent':med['r_peak_percent'],'median_case':med['Case'],
   'max_reduction_percent':hi['r_peak_percent'],'max_case':hi['Case'],
   'P_B_at_min_kN':lo['P_B_kN'],'P_D_at_min_kN':lo['P_D_kN'],'t_B_at_min_s':lo['t_B_s'],'t_D_at_min_s':lo['t_D_s'],'d_at_min_pp':lo['d_pp'],
   'demand_control_case':dem['Case'],'P_D_max_kN':dem['P_D_kN'],'r_at_demand_control_percent':dem['r_peak_percent'],
   'improvement_and_demand_controls_differ':lo['Case']!=dem['Case']})
table('actual-layer-direction-ranges-24.csv',ranges)
screen=[]
for case in sorted({r['Case']for r in rows}):
 g=[r for r in rows if r['Case']==case];assert len(g)==12
 lo=min(g,key=lambda r:r['r_peak_percent']);bottom=next(r for r in g if r['Story']=='Story1');mean=statistics.fmean(r['r_peak_percent']for r in g)
 screen.append({'Case':case,'Axis':case[-1],'least_reduction_Story':lo['Story'],'least_reduction_percent':lo['r_peak_percent'],
  'bottom_reduction_percent':bottom['r_peak_percent'],'mean_12_story_reduction_percent':mean,
  'bottom_minus_least_pp':bottom['r_peak_percent']-lo['r_peak_percent'],'mean_minus_least_pp':mean-lo['r_peak_percent'],
  'bottom_is_minimum_story':bottom['r_peak_percent']==lo['r_peak_percent'],'scope':'Arithmetic mean of 12 story reduction percentages, not reduction of total shear'})
table('actual-bottom-mean-screening-6.csv',screen)
ds=sorted(r['d_pp']for r in rows)
def pct(q):
 pos=(len(ds)-1)*q;i=int(pos);a=pos-i
 return ds[i]*(1-a)+ds[min(i+1,len(ds)-1)]*a
summary={'finished_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'source_inputs':sources,'rows':72,'range_groups':24,'all_72_saved_time_axes_exact':True,
 'B_D_native_peaks_match_1458_reviewed72':True,'r_peak_min_percent':min(r['r_peak_percent']for r in rows),'r_peak_max_percent':max(r['r_peak_percent']for r in rows),
 'd_min_pp':min(ds),'d_median_pp':statistics.median(ds),'d_95_percentile_pp':pct(.95),'d_max_pp':max(ds),
 'd_zero_count_exact':sum(r['d_pp']==0 for r in rows),'same_saved_peak_time_count':sum(r['same_saved_peak_time']for r in rows),
 'max_abs_peak_time_shift_s':max(r['absolute_peak_time_shift_s']for r in rows),
 'd_max_record':max(rows,key=lambda r:r['d_pp']),'least_reduction_record':min(rows,key=lambda r:r['r_peak_percent']),
 'bottom_min_count':sum(r['bottom_is_minimum_story']for r in screen),'bottom_mean_screening':screen,
 'largest_bottom_miss_case':max(screen,key=lambda r:r['bottom_minus_least_pp']),
 'largest_mean_miss_case':max(screen,key=lambda r:r['mean_minus_least_pp']),
 'dual_control_differ_groups':sum(r['improvement_and_demand_controls_differ']for r in ranges),
 'independent_events_claimed':False,'new_solver_runs':0,'source_workbook_reads':0,'saved_full_output_arrays':False,'native_cache_arrays_read':144}
assert all(sha(Path(q['path']))==q['sha256']for q in sources)
js('actual-response-summary.json',summary)
lines=['# 实际88只阻尼器模型的逐层剪力评价','','本轮以实际布置阻尼器模型D为工程主方案，与同名共有六工况的基准B比较。没有借用均匀增加模态阻尼的M输出。三模型对应条件由配套核查说明提供；本表直接保留两模型原生Bottom剪力，不扣除Link生成主体QS。','',
 f"72条主方向记录全部保存轴逐点一致，原生峰值与上一轮已审72表逐值一致。实际D相对B峰减幅范围{summary['r_peak_min_percent']:.6f}%—{summary['r_peak_max_percent']:.6f}%。24个楼层—方向组中，改善最小与绝对需求最大输入不同的为{summary['dual_control_differ_groups']}组。",'',
 '## 底层及平均减幅为何需要逐层补查','', '|工况|改善最小层|最小减幅/%|底层减幅/%|十二层算术平均/%|底层高出/百分点|平均高出/百分点|','|---|---|---:|---:|---:|---:|---:|']
for q in screen:lines.append(f"|{q['Case']}|{q['least_reduction_Story']}|{q['least_reduction_percent']:.4f}|{q['bottom_reduction_percent']:.4f}|{q['mean_12_story_reduction_percent']:.4f}|{q['bottom_minus_least_pp']:.4f}|{q['mean_minus_least_pp']:.4f}|")
dm=summary['d_max_record'];lines+=['',f"六工况中底层恰为最小减幅层的{summary['bottom_min_count']}项；十二层减幅算术平均不是总剪力减幅。",'',
 '## 原峰时评价高估量','', f"按实际D时程，d中位数{summary['d_median_pp']:.6f}个百分点，95%线性插值分位{summary['d_95_percentile_pp']:.6f}个百分点，最大{summary['d_max_pp']:.6f}个百分点。最大项为{dm['Case']} {dm['Story']}：PB={dm['P_B_kN']:.6f}kN，PD={dm['P_D_kN']:.6f}kN，原基准峰时D={dm['D_at_tB_signed_kN']:.6f}kN；r_at={dm['r_at_percent']:.6f}%，r_peak={dm['r_peak_percent']:.6f}%，d={dm['d_pp']:.6f}个百分点，峰时{dm['t_B_s']:.2f}→{dm['t_D_s']:.2f}s。",'',
 f"保存峰时相同为{summary['same_saved_peak_time_count']}/72项，d严格为0为{summary['d_zero_count_exact']}/72项，二者不是相同判断。全部记录保留并列峰数并取首次保存峰；d是网格上评价时刻造成的差，不是纯相位因果贡献。",'',
 '完整数据：actual-versus-baseline-time-peak-72.csv；分层范围：actual-layer-direction-ranges-24.csv；底层/平均对照：actual-bottom-mean-screening-6.csv。输入指纹与实际读取范围见input-freeze.json。']
(H/'actual-response-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:summary[k]for k in ['rows','all_72_saved_time_axes_exact','r_peak_min_percent','r_peak_max_percent','d_median_pp','d_95_percentile_pp','d_max_pp','bottom_min_count','dual_control_differ_groups','largest_bottom_miss_case','d_max_record']},ensure_ascii=False))
