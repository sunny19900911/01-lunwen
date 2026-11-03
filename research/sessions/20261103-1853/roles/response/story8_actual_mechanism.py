from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
import numpy as np
H=Path(__file__).resolve().parent;H.mkdir(parents=True,exist_ok=True);R=H.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvread(p):
 with p.open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
def write(name,rr):
 p=H/name;assert not p.exists()
 with p.open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def js(name,d):
 p=H/name;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
W=R.parent/'W5-重燃双塔连体'
B=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';D=W/'research/maxwell-20261017/experiments/R001/core-cache'
mb=json.loads((B/'manifest.json').read_text(encoding='utf-8'));md=json.loads((D/'manifest.json').read_text(encoding='utf-8'))
tb=mb['tables']['Story Forces'];td=md['tables']['Story Forces'];cb=tb.get('columns',tb.get('value_columns'));cd=td.get('columns',td.get('value_columns'))
pb=B/tb['cache'];pd=D/td['cache'];pq=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
old72=R/'research/sessions/20261103-1700/roles/response/actual-versus-baseline-time-peak-72.csv'
oldtiming=R/'research/sessions/20261103-1458/roles/response/Story8-native-device-timing-6.csv'
old8={r['Case']:r for r in csvread(old72)if r['Story']=='Story8'}
oldt={r['Case']:r for r in csvread(oldtiming)}
inputs=[B/'manifest.json',D/'manifest.json',pb,pd,pq,old72,oldtiming]
sources=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in inputs]
js('input-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'code_sha256':sha(Path(__file__)),'sources':sources,'scope':'Story8 six actual inputs; native B/D total Bottom shear and independently geometry-projected actual QD; no QS subtraction'})
key=lambda g:tuple(g['keys'][x]for x in ['Output Case','Story','Location'])
kb={key(g):k for k,g in tb['groups'].items()};kd={key(g):k for k,g in td['groups'].items()}
anchors=[];summaries=[];full_checks=[]
with np.load(pb,allow_pickle=False)as zb,np.load(pd,allow_pickle=False)as zd,np.load(pq,allow_pickle=False)as zq:
 for case in ['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']:
  axis=case[-1];k=(case,'Story8','Bottom');ab=zb[kb[k]];ad=zd[kd[k]];aq=zq[f'Story8__{case}__{axis}']
  t=ab[:,cb.index('Time')];tD=ad[:,cd.index('Time')];tQ=aq[:,0]
  assert np.array_equal(t,tD)and np.array_equal(t,tQ)and np.all(np.diff(t)>0)
  b=ab[:,cb.index('V'+axis)];d=ad[:,cd.index('V'+axis)];q=aq[:,2]
  assert np.array_equal(d,aq[:,1])and np.array_equal(ad[:,cd.index('SourceRow')],aq[:,5])
  assert np.isfinite(b).all()and np.isfinite(d).all()and np.isfinite(q).all()
  ib=int(np.argmax(abs(b)));idd=int(np.argmax(abs(d)));iq=int(np.argmax(abs(q)));pB=float(abs(b[ib]));pD=float(abs(d[idd]));pQ=float(abs(q[iq]));sig=float(np.sign(b[ib]));old=old8[case];tim=oldt[case]
  for value,field in [(pB,'P_B_kN'),(pD,'P_D_kN'),(float(t[ib]),'t_B_s'),(float(t[idd]),'t_D_s')]:assert abs(value-float(old[field]))<1e-9
  assert abs(pQ-float(tim['QD_abs_peak_kN']))<1e-9 and t[iq]==float(tim['t_QD_peak_s'])
  assert abs(float(q[idd])-float(tim['QD_signed_at_QT_peak_kN']))<1e-9
  A=abs(float(d[ib]));rpeak=100*(1-pD/pB);rat=100*(1-A/pB);dp=100*(pD-A)/pB
  S=pB-sig*float(d[ib]);M=pD-sig*float(d[ib]);peakdrop=pB-pD
  assert abs(peakdrop-S+M)<1e-9 and M>=-1e-9
  assert abs(rat-dp-rpeak)<1e-10
  for label,ii in [('tB',ib),('tD',idd),('tQD',iq)]:
   anchors.append({'Case':case,'Axis':axis,'Story':'Story8','anchor':label,'time_s':float(t[ii]),
     'B_QT_signed_kN':float(b[ii]),'D_QT_signed_kN':float(d[ii]),'QD_signed_J_resisting_kN':float(q[ii]),
     'B_QT_abs_kN':abs(float(b[ii])),'D_QT_abs_kN':abs(float(d[ii])),
     'QD_abs_over_own_abs_peak_percent':100*abs(float(q[ii]))/pQ,
     'QD_signed_over_own_abs_peak_percent':100*float(q[ii])/pQ,
     'D_QT_abs_over_own_abs_peak_percent':100*abs(float(d[ii]))/pD,
     'B_QT_abs_over_own_abs_peak_percent':100*abs(float(b[ii]))/pB,
     'QD_over_same_D_QT_signed_ratio':float(q[ii]/d[ii])if d[ii]!=0 else None,
     'B_SourceRow':int(ab[ii,cb.index('SourceRow')]),'D_SourceRow':int(ad[ii,cd.index('SourceRow')]),
     'QD_combo_matches_D_SourceRow':int(aq[ii,5])==int(ad[ii,cd.index('SourceRow')]),
     'scope':'Saved simultaneous native outputs; QD=sum nP J-end structural internal resisting force, external force opposite; no QS or causal contribution ratio'})
  summaries.append({'Case':case,'Axis':axis,'Story':'Story8','n_saved':len(t),'P_B_kN':pB,'P_D_kN':pD,'P_QD_abs_kN':pQ,
    't_B_s':float(t[ib]),'t_D_s':float(t[idd]),'t_QD_s':float(t[iq]),
    'B_signed_at_tB_kN':float(b[ib]),'D_signed_at_tB_kN':float(d[ib]),'D_signed_at_tD_kN':float(d[idd]),
    'B_signed_at_tD_kN':float(b[idd]),'QD_signed_at_tB_kN':float(q[ib]),'QD_signed_at_tD_kN':float(q[idd]),
    'sigma_B_peak':int(sig),'old_direction_signed_weakening_S_kN':S,'own_peak_selection_recovery_M_kN':M,
    'P_B_minus_P_D_kN':peakdrop,'S_minus_M_identity_residual_kN':S-M-peakdrop,
    'abs_old_time_drop_kN':pB-A,'abs_repeak_recovery_kN':pD-A,'r_at_percent':rat,'r_D_peak_percent':rpeak,'d_pp':dp,
    'D_at_tB_same_sign_as_B_peak':bool(np.sign(d[ib])==sig),'D_own_peak_same_sign_as_B_peak':bool(np.sign(d[idd])==sig),
    't_D_minus_t_B_s':float(t[idd]-t[ib]),'t_QD_minus_t_D_s':float(t[iq]-t[idd]),
    'QD_abs_at_tB_over_own_peak_percent':100*abs(float(q[ib]))/pQ,
    'QD_abs_at_tD_over_own_peak_percent':100*abs(float(q[idd]))/pQ,
    'scope':'Peak accounting identity, not decomposition of physical causes or subtraction of damper force from QT'})
  full_checks.append({'Case':case,'B_D_QD_saved_grids_exact':True,'QD_combo_D_full_QT_values_exact':True,'D_source_row_column_exact':True,'prior_peak_summaries_match':True,'B_cache_key':kb[k],'D_cache_key':kd[k],'QD_cache_key':f'Story8__{case}__{axis}'})
assert len(anchors)==18 and len(summaries)==6
write('Story8-native-three-times-18.csv',anchors);write('Story8-actual-peak-accounting-6.csv',summaries)
assert all(sha(Path(q['path']))==q['sha256']for q in sources)
summary={'finished_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'rows_anchor':18,'rows_case':6,'all_six_inputs_retained':True,
 'full_checks':full_checks,'cases':summaries,'source_hashes_unchanged':True,'reference_M_arrays_read':0,'raw_workbook_reads':0,'new_ODE_or_fits':0,
 'B_D_own_peak_sign_switch_count':sum(not r['D_own_peak_same_sign_as_B_peak']for r in summaries),'all_new_peaks_at_different_saved_times':all(r['t_D_s']!=r['t_B_s']for r in summaries)}
js('Story8-mechanism-summary.json',summary)
lines=['# 第8层实际数据：原峰降低、自身控制峰及装置同刻出力','','全六工况保留。仅读已缓存的B、D各6组Story Forces和已审QD组合6组。B/D/QD保存时刻逐点一致，组合内QT完整列与原生D完整列逐值相等，源行列一致；不从QT扣QD生成主体QS。',
 '', '## 原峰降低与新控制峰的取值关系','','记σB为基准控制峰的符号。沿该方向，S=PB−σB·D(tB)，M=PD−σB·D(tB)，故PB−PD=S−M。S描述原控制时刻沿基准方向的响应降低；M描述D自身绝对峰比该时刻同向值更大的部分。它们是实际保存曲线的峰值记账，不是物理原因分解；M也不是装置造成新峰的证明。另保留绝对值定义的r_at/d。','',
 '|工况|tB/s|tD/s|基准峰PB/kN|D(tB)/kN|D自身峰有符号/kN|S/kN|M/kN|PB−PD/kN|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in summaries:lines.append(f"|{r['Case']}|{r['t_B_s']:.2f}|{r['t_D_s']:.2f}|{r['P_B_kN']:.4f}|{r['D_signed_at_tB_kN']:+.4f}|{r['D_signed_at_tD_kN']:+.4f}|{r['old_direction_signed_weakening_S_kN']:.4f}|{r['own_peak_selection_recovery_M_kN']:.4f}|{r['P_B_minus_P_D_kN']:.4f}|")
lines+=['', '## 装置出力是否同刻','','|工况|tQD/s|QD自身绝对峰/kN|tB时QD/kN|tD时QD/kN|tB时绝对值/自身峰/%|tD时绝对值/自身峰/%|','|---|---:|---:|---:|---:|---:|---:|']
for r in summaries:lines.append(f"|{r['Case']}|{r['t_QD_s']:.2f}|{r['P_QD_abs_kN']:.4f}|{r['QD_signed_at_tB_kN']:+.4f}|{r['QD_signed_at_tD_kN']:+.4f}|{r['QD_abs_at_tB_over_own_peak_percent']:.4f}|{r['QD_abs_at_tD_over_own_peak_percent']:.4f}|")
lines+=['',f"六工况B与D各自控制峰的符号改变为{summary['B_D_own_peak_sign_switch_count']}/6项；各自峰时均有变化。应按实际数据描述这个结果，不把峰时变化称纯相位或把新控制峰归因为QD。","","完整三时刻18行包含B/D有符号QT、QD、源行、相对自身峰的比例，以及两状态峰值选择恒等式6行。装置比是出力读数，不称减震贡献率或效率。相关模型对应条件沿用主稿的数据范围说明。"]
(H/'Story8-actual-mechanism-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'rows18':18,'cases':summaries[:1]+summaries[-2:-1],'sign_switch_count':summary['B_D_own_peak_sign_switch_count']},ensure_ascii=False))
