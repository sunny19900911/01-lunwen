from pathlib import Path
from datetime import datetime,timezone,timedelta
from collections import defaultdict
import numpy as np
import json,csv,hashlib
O=Path(__file__).resolve().parent;R=O.parents[4];S=R/'research/sessions/20261019-2045';P=R/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution';C=R.parent/'W5-重燃双塔连体/research/maxwell-20261017/experiments/R001/core-cache'
START=datetime.fromisoformat('2026-10-20T11:52:45+00:00');DEADLINE=START+timedelta(minutes=10)
def now():return datetime.now(timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rc(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths=[P/'local_history_manifest_r006.json',P/'local_paired_histories_r006.npz',C/'manifest.json',C/'Story_Forces.npz',C/'Base_Reactions.npz',S/'roles/data/R001-link-geometry-88.csv',S/'roles/audit/R002-native-horizontal-review.md']
bindings=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
js('R005-input-freeze.json',{'utc':now().isoformat(),'code_sha256':sha(Path(__file__)),'start_utc':START.isoformat(),'deadline_utc':DEADLINE.isoformat(),'inputs':bindings,'force_convention':'n points actual low I to high J; +nP is J-node structural internal resisting term; physical force exerted on J is -nP. One P per device; I/J equal scalar records not added.','scope':'coverage of frozen 192 records then Story8 native force timing only; no QS subtraction, nominal law or phase-angle claim'})
hm=json.loads(paths[0].read_text(encoding='utf-8'));cm=json.loads((C/'manifest.json').read_text(encoding='utf-8'));geom={(r['Story'],r['Link']):r for r in rc(paths[5])};groups=defaultdict(list)
for a in hm['arrays']:groups[a['Story'],a['Case']].append(a)
assert len(hm['arrays'])==192 and len(groups)==24 and {s for s,c in groups}=={'Story8','Story9','Story10','Story11'}
sf=cm['tables']['Story Forces'];bc=cm['tables']['Base Reactions'];skeys={(g['keys']['Story'],g['keys']['Output Case']):k for k,g in sf['groups'].items()};bkeys={g['keys']['Output Case']:k for k,g in bc['groups'].items()}
coverage=[];summary=[];devices=[]
with np.load(P/'local_paired_histories_r006.npz',allow_pickle=False) as zz,np.load(C/sf['cache'],allow_pickle=False) as sz,np.load(C/bc['cache'],allow_pickle=False) as bz:
 for (story,case),records in sorted(groups.items()):
  assert now()<DEADLINE
  qtarr=sz[skeys[story,case]];t=qtarr[:,sf['columns'].index('Time')];assert np.array_equal(t,bz[bkeys[case]][:,bc['columns'].index('Time')])
  assert len(records)==8 and {a['Link'] for a in records}=={link for s,link in geom if s==story}
  for a in records:
   ar=zz[a['key']];col=a['columns'];assert np.isfinite(ar).all() and np.array_equal(t,ar[:,col.index('t_s')]) and np.array_equal(ar[:,col.index('P_I_kN')],ar[:,col.index('P_J_kN')]);assert np.allclose(ar[:,col.index('U1_m')],.001*ar[:,col.index('U1_mm')],rtol=1e-14,atol=1e-16)
   g=geom[story,a['Link']];assert float(g['I_Z_m'])<float(g['J_Z_m'])
  coverage.append({'Story':story,'Case':case,'complete_devices':8,'P_I_equals_P_J_once':True,'time_matches_Base_and_Story_exactly':True,'P_U1_finite':True,'n_points':len(t),'t0_s':float(t[0]),'t1_s':float(t[-1]),'geometry_matches':True})
 for case in ['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']:
  story='Story8';axis=case[-1];a0=sz[skeys[story,case]];t=a0[:,sf['columns'].index('Time')];qt=a0[:,sf['columns'].index('V'+axis)];records=sorted(groups[story,case],key=lambda r:r['Link']);parts=[];data=[]
  for a in records:
   ar=zz[a['key']];col=a['columns'];g=geom[story,a['Link']];n=float(g['n'+axis.lower()]);p=ar[:,col.index('P_I_kN')];u=ar[:,col.index('U1_mm')];parts.append(n*p);data.append((a,ar,col,g,n,p,u))
  qd=np.sum(parts,axis=0);it=int(np.argmax(abs(qt)));id=int(np.argmax(abs(qd)));pt=float(abs(qt[it]));pd=float(abs(qd[id]));assert pd>1e-10
  summary.append({'Story':story,'Case':case,'Axis':axis,'devices_total':8,'nonzero_axis_devices':sum(abs(v[4])>1e-12 for v in data),'QT_peak_abs_kN':pt,'QT_signed_at_peak_kN':float(qt[it]),'t_QT_peak_s':float(t[it]),'QT_peak_SourceRow':int(a0[it,sf['columns'].index('SourceRow')]),'QD_J_resisting_peak_abs_kN':pd,'QD_J_resisting_signed_at_own_peak_kN':float(qd[id]),'t_QD_abs_peak_s':float(t[id]),'t_QD_minus_t_QT_s':float(t[id]-t[it]),'QD_J_resisting_at_QT_peak_kN':float(qd[it]),'QD_J_external_at_QT_peak_kN':float(-qd[it]),'QD_at_QT_signed_percent_own_abs_peak':100*float(qd[it])/pd,'QD_at_QT_abs_percent_own_abs_peak':100*abs(float(qd[it]))/pd,'QT_signed_at_QD_abs_peak_kN':float(qt[id]),'QT_at_QD_abs_percent_own_abs_peak':100*abs(float(qt[id]))/pt,'scope':'native P projected at upper J internal resisting side; not QS or change between models'})
  for q,(a,ar,col,g,n,p,u) in zip(parts,data):
   iq=int(np.argmax(abs(q)));ip=int(np.argmax(abs(p)));iu=int(np.argmax(abs(u)));qp=float(abs(q[iq]));active=qp>1e-10
   devices.append({'Story':story,'Case':case,'Axis':axis,'Link':a['Link'],'I_Point':g['I_Point'],'J_Point':g['J_Point'],'n_axis':n,'axis_projection_nonzero':abs(n)>1e-12,'P_abs_peak_kN':float(abs(p[ip])),'t_P_peak_s':float(t[ip]),'U1_abs_peak_total_mm':float(abs(u[iu])),'t_U1_peak_s':float(t[iu]),'qJ_resisting_abs_peak_kN':qp,'t_qJ_abs_peak_s':float(t[iq]) if active else None,'t_QT_peak_s':float(t[it]),'P_at_QT_peak_kN':float(p[it]),'U1_total_at_QT_peak_mm':float(u[it]),'qJ_resisting_at_QT_peak_kN':float(q[it]),'qJ_external_at_QT_peak_kN':float(-q[it]),'q_at_QT_signed_percent_device_own_abs_peak':100*float(q[it])/qp if active else None,'q_at_QT_abs_percent_device_own_abs_peak':100*abs(float(q[it]))/qp if active else None,'q_at_QT_signed_percent_layer_QD_abs_peak':100*float(q[it])/pd,'qJ_resisting_at_layer_QD_peak_kN':float(q[id]),'P_SourceRow_at_QT_peak':int(ar[it,col.index('force_I_row')]),'U1_SourceRow_at_QT_peak':int(ar[it,col.index('deformation_row')]),'geometry_SourceRow':g['link_source_row']})
  assert abs(sum(r['qJ_resisting_at_QT_peak_kN'] for r in devices if r['Case']==case)-qd[it])<1e-10
  if case=='RH4Y':
   cs('R005-first-two-layer-summary.csv',summary);cs('R005-first-two-device-at-QT-peak-16.csv',devices);print('FIRST_TWO_CASES_SAVED '+now().isoformat(),flush=True)
cs('R005-coverage-24.csv',coverage);cs('R005-Story8-six-layer-summary.csv',summary);cs('R005-Story8-device-at-QT-peak-48.csv',devices)
assert len(coverage)==24 and len(summary)==6 and len(devices)==48 and all(sha(Path(x['path']))==x['sha256'] for x in bindings)
lines=['# R005：真实装置力与楼层剪力的峰时对照','','已核Story8—11各8只×六工况完整，共32只/192条P-U1记录；I/J为同一轴力标量，只计一次。全部与Base及同层QT时间轴逐点相同，未插值补零。首两例与六例小表均已交付，不保存/上传时程数组。','', '选Story8，上端J高于I，n由I指向J。本表QD=Σn_axis P为J端结构内力抵抗项；装置对J节点的外力为−QD。P为真实原生轴力，非名义本构。Bottom的侧别、正方向与Link包含关系尚未由此闭合，不作QT±QD的主体扣力。','', '|工况|QT绝对峰/kN|QT峰时/s|QD绝对峰/kN|QD峰时/s|QT峰时QD/kN|占QD自身峰绝对值/%|QD峰时QT/kN|','|---|---:|---:|---:|---:|---:|---:|---:|']
for r in summary:lines.append(f"|{r['Case']}|{r['QT_peak_abs_kN']:.4f}|{r['t_QT_peak_s']:.2f}|{r['QD_J_resisting_peak_abs_kN']:.4f}|{r['t_QD_abs_peak_s']:.2f}|{r['QD_J_resisting_at_QT_peak_kN']:.4f}|{r['QD_at_QT_abs_percent_own_abs_peak']:.4f}|{r['QT_signed_at_QD_abs_peak_kN']:.4f}|")
lines+=['','逐只表保留8只带符号分力及其各自峰比例、P/U1同刻值、原生源行；每个主方向仅4只非零投影，另外4只投影为零，分母为零的自身峰比例留空。不得将这些留空补成“0%利用率”。合力比例以合力自身绝对峰作分母，不能与各器件自身峰比例混用。','', '峰时差只是两个保存时程控制时刻的差，不是相位角。QT峰时装置合力未达自身峰说明两种输出的最大值并不同步，但不能单凭此认定减震因果或分出某阶模态。没有把32只覆盖推广为全88只力已齐。','', '下一问题：将其中一例与同模型局部运动的时序并列，先核功共轭与运动定义；总U1包含串簧变形，不能直接称黏壶速度。']
(O/'R005-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
end=now();js('R005-delivery-manifest.json',{'status':'frozen','start_utc':START.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_10min':end<=DEADLINE,'arrays_uploaded':False,'raw_workbook_reads':0,'solver_runs':0,'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R005*')) if p.is_file()]})
print(json.dumps({'summary':summary[:2],'coverage_groups':24,'frozen':end.isoformat(),'seconds':(end-START).total_seconds()},ensure_ascii=False))
