from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np
import csv,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[4]
D=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016';B=D/'原生0数据缓存'
START=datetime.fromisoformat('2026-10-20T11:30:53+00:00');DEADLINE=START+timedelta(minutes=8)
def now():return datetime.now(timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert now()<DEADLINE
m0=json.loads((B/'manifest.json').read_text(encoding='utf-8'));m3=json.loads((D/'response_cache_manifest.json').read_text(encoding='utf-8'))
t0=m0['tables']['Story Forces'];t3=m3['tables']['Story Forces'];c0=t0.get('columns',t0.get('value_columns'));c3=t3.get('columns',t3.get('value_columns'))
paths=[B/'manifest.json',D/'response_cache_manifest.json',B/t0['cache'],D/t3['cache'],D/'native_paired_validation.json']
inputs=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
js('R002-input-freeze.json',{'utc':now().isoformat(),'start_utc':START.isoformat(),'deadline_utc':DEADLINE.isoformat(),'code_sha256':sha(Path(__file__)),'inputs':inputs,'scope':'native Bottom shear label0/3; six common cases first; no modal decomposition or QS claim','peak':'max(abs(saved native output)); relative change=(P3-P0)/P0; small denominator<=1e-10kN unresolved','time_shift':'t_peak3-t_peak0; same peak time does not prove same response phase','source0_sha256':m0['sha256'],'source3_sha256':m3['sha256']})
def key(g):return tuple(g['keys'][s] for s in ['Output Case','Story','Location'])
k0={key(g):k for k,g in t0['groups'].items()};k3={key(g):k for k,g in t3['groups'].items()};assert k0.keys()==k3.keys() and len(k0)==168
common={'RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y'};rows=[];main=[];checks=[]
with np.load(B/t0['cache'],allow_pickle=False) as z0,np.load(D/t3['cache'],allow_pickle=False) as z3:
 for phase in [True,False]:
  for case,story,loc in sorted(k0,key=lambda k:(k[0],int(k[1][5:]))):
   if (case in common)!=phase:continue
   assert now()<DEADLINE
   a=z0[k0[case,story,loc]];b=z3[k3[case,story,loc]];tt=a[:,c0.index('Time')]
   assert loc=='Bottom' and np.array_equal(tt,b[:,c3.index('Time')]) and np.all(np.diff(tt)>0) and np.isfinite(a).all() and np.isfinite(b).all()
   checks.append({'Case':case,'Story':story,'Location':loc,'full_time_pair_equal':True,'n':len(tt)})
   for axis in ['X','Y']:
    y0=a[:,c0.index('V'+axis)];y3=b[:,c3.index('V'+axis)];i=int(np.argmax(abs(y0)));j=int(np.argmax(abs(y3)));p0=float(abs(y0[i]));p3=float(abs(y3[j]));ok=p0>1e-10;s=float(np.sign(y0[i]));direct=s*float(y3[i]-y0[i]);migration=p3-s*float(y3[i])
    assert migration>=-1e-10 and abs((p3-p0)-direct-migration)<1e-9
    row={'Case':case,'wave_family':case[:-1],'input_direction':case[-1],'Story':story,'Location':loc,'Axis':axis,'input_main_axis':case[-1]==axis,'common_with_physical_model':phase,'P0_kN':p0,'P3_kN':p3,'signed0_at_own_peak_kN':float(y0[i]),'signed3_at_own_peak_kN':float(y3[j]),'t_peak0_s':float(tt[i]),'t_peak3_s':float(tt[j]),'peak_time_shift_s':float(tt[j]-tt[i]),'peak_change_kN':p3-p0,'peak_change_percent':100*(p3-p0)/p0 if ok else None,'peak_reduction_percent':100*(1-p3/p0) if ok else None,'denominator_resolved':ok,'label3_at_label0_peak_kN':float(y3[i]),'same_time_signed_change_kN':direct,'repeak_recovery_kN':migration,'source_row0':int(a[i,c0.index('SourceRow')]),'source_row3':int(b[j,c3.index('SourceRow')]),'n_points':len(tt),'t0_s':float(tt[0]),'t1_s':float(tt[-1]),'scope':'native QT label0/label3 output comparison; not isolated main-structure QS or identified modal contribution'}
    rows.append(row)
    if case[-1]==axis:main.append(row)
  if phase:
   cs('R002-common-six-main-axis-72.csv',main);print('FIRST_TABLE_SAVED '+now().isoformat()+' rows='+str(len(main)),flush=True)
cs('R002-all14-main-axis-168.csv',main);cs('R002-all14-two-axis-336.csv',rows)
rank=sorted([r for r in main if r['denominator_resolved']],key=lambda r:r['peak_reduction_percent']);cs('R002-least-reduction-main-axis.csv',rank[:24])
bycase=[]
for case in sorted({r['Case'] for r in main}):
 rr=[r for r in main if r['Case']==case];lo=min(rr,key=lambda r:r['peak_reduction_percent']);hi=max(rr,key=lambda r:r['peak_reduction_percent'])
 bycase.append({'Case':case,'least_reduction_Story':lo['Story'],'least_reduction_percent':lo['peak_reduction_percent'],'least_peak_time_shift_s':lo['peak_time_shift_s'],'most_reduction_Story':hi['Story'],'most_reduction_percent':hi['peak_reduction_percent'],'amplified_story_count':sum(r['peak_change_kN']>1e-9 for r in rr),'max_abs_peak_time_shift_s':max(abs(r['peak_time_shift_s']) for r in rr)})
cs('R002-by-case-14.csv',bycase)
assert len(checks)==168 and len(main)==168 and len(rows)==336
assert all(sha(Path(x['path']))==x['sha256'] for x in inputs)
stats={'finished_utc':now().isoformat(),'paired_groups':len(checks),'main_axis_rows':len(main),'two_axis_rows':len(rows),'main_axis_amplified_rows':sum(r['peak_change_kN']>1e-9 for r in main),'common_six_amplified_main_rows':sum(r['peak_change_kN']>1e-9 for r in main if r['common_with_physical_model']),'main_axis_reduction_percent_range':[rank[0]['peak_reduction_percent'],rank[-1]['peak_reduction_percent']],'largest_peak_time_shift_s':max(abs(r['peak_time_shift_s']) for r in main),'checks':checks}
js('R002-result.json',stats)
lines=['# R002：标签0/3原生楼层剪力峰值与峰时比较','','直接从既有两态Story Forces缓存计算全部14工况×12层，保留Bottom与原生QT身份。先交与实体模型共同六工况的72行主方向表，再保存全部168行主方向、336行两方向。没有频带分析、模态占比或求解。','',f"主方向峰减幅范围为{rank[0]['peak_reduction_percent']:.6f}%—{rank[-1]['peak_reduction_percent']:.6f}%；反增记录{stats['main_axis_amplified_rows']}/168，共同六工况反增{stats['common_six_amplified_main_rows']}/72。不存在反例也是本次结果，不据此推断所有模型/输入均下降。最大绝对峰时迁移{stats['largest_peak_time_shift_s']:.4f}s。",'','下降最少记录：','', '|工况|层|P0/kN|P3/kN|减幅/%|峰时0→3/s|','|---|---|---:|---:|---:|---|']
for r in rank[:8]:lines.append(f"|{r['Case']}|{r['Story']}|{r['P0_kN']:.4f}|{r['P3_kN']:.4f}|{r['peak_reduction_percent']:.6f}|{r['t_peak0_s']:.2f}→{r['t_peak3_s']:.2f}|")
lines+=['','峰变化定义(P3−P0)/P0，减幅为1−P3/P0。两个峰分别在各自原生记录时刻取得，时间差不是相位角。另保留旧峰同刻变化与重新寻峰恢复量，其和等于P3−P0；没有用独立峰相减代替同刻分量。绝对分母≤1e−10kN留空，不加epsilon。','', '168组时间逐点相同、有限且递增，输入配对复用已核14工况清单；缓存运行前后SHA一致。标签0未认证为零阻尼，标签3的实际逐阶阻尼未由本表落实。原生QT的Link包含性/主体QS分离未由此认证。','', '下一问题：选共同六工况中减幅最少的一层，检查同刻上下截面剪力及总峰时迁移；先描述真实输出，再以明确的简化模态参考解释，不将观察直接归因某一阶。']
(O/'R002-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
end=now();js('R002-delivery-manifest.json',{'status':'frozen','start_utc':START.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_8min':end<=DEADLINE,'new_workbook_reads':0,'solver_runs':0,'new_modal_decompositions':0,'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R002*')) if p.is_file()]})
print(json.dumps({k:stats[k] for k in stats if k!='checks'},ensure_ascii=False));print('FROZEN '+end.isoformat(),flush=True)
