from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
import numpy as np
H=Path(__file__).resolve().parent;H.mkdir(parents=True,exist_ok=True);R=H.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def table(n,rr):
 p=H/n;assert not p.exists()
 with p.open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
W=R.parent/'W5-重燃双塔连体';B=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';D=W/'research/maxwell-20261017/experiments/R001/core-cache'
mb=json.loads((B/'manifest.json').read_text(encoding='utf-8'));md=json.loads((D/'manifest.json').read_text(encoding='utf-8'));tb=mb['tables']['Story Forces'];td=md['tables']['Story Forces'];cb=tb.get('columns',tb.get('value_columns'));cd=td.get('columns',td.get('value_columns'))
pb=B/tb['cache'];pd=D/td['cache'];pq=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
inputs=[B/'manifest.json',D/'manifest.json',pb,pd,pq]
sources=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in inputs]
kf=lambda g:tuple(g['keys'][x]for x in ['Output Case','Story','Location']);kb={kf(g):k for k,g in tb['groups'].items()};kd={kf(g):k for k,g in td['groups'].items()}
anchors=[];metrics=[];sensitive=[];checks=[]
with np.load(pb,allow_pickle=False)as zb,np.load(pd,allow_pickle=False)as zd,np.load(pq,allow_pickle=False)as zq:
 for story in ['Story8','Story10']:
  for case in ['RH4X','RH4Y']:
   axis=case[-1];key=(case,story,'Bottom');ab=zb[kb[key]];ad=zd[kd[key]];aq=zq[f'{story}__{case}__{axis}']
   t=ab[:,cb.index('Time')];b=ab[:,cb.index('V'+axis)];qt=ad[:,cd.index('V'+axis)];qd=aq[:,2]
   assert len(t)==2501 and np.array_equal(t,ad[:,cd.index('Time')])and np.array_equal(t,aq[:,0])and np.array_equal(qt,aq[:,1])and np.array_equal(ad[:,cd.index('SourceRow')],aq[:,5])
   assert np.isfinite(ab).all()and np.isfinite(ad).all()and np.isfinite(aq).all()and np.all(np.diff(t)>0)
   minus=qt-qd;plus=qt+qd
   assert np.array_equal(minus,aq[:,3])and np.array_equal(plus,aq[:,4])
   ib=int(np.argmax(abs(b)));idt=int(np.argmax(abs(qt)));iq=int(np.argmax(abs(qd)));im=int(np.argmax(abs(minus)));ip=int(np.argmax(abs(plus)))
   for label,ii in [('tB',ib),('tD',idt),('tQD',iq)]:
    anchors.append({'Story':story,'Case':case,'Axis':axis,'anchor':label,'time_s':float(t[ii]),'B_QT_signed_kN':float(b[ii]),'QT_D_signed_kN':float(qt[ii]),'QD_J_resisting_signed_kN':float(qd[ii]),'QT_minus_QD_algebraic_kN':float(minus[ii]),'QT_plus_QD_algebraic_kN':float(plus[ii]),
     'B_SourceRow':int(ab[ii,cb.index('SourceRow')]),'D_QT_SourceRow':int(ad[ii,cd.index('SourceRow')]),'QD_combo_D_SourceRow_exact':True,'scope':'QT-QD and QT+QD are same-time algebraic outputs, not identified main-structure QS'})
   tvqt=float(np.sum(abs(np.diff(qt))));pkqt=float(max(abs(qt)));rmsqt=float(np.sqrt(np.mean(qt*qt)))
   for name,arr in [('QT',qt),('QD',qd),('QT_minus_QD',minus),('QT_plus_QD',plus)]:
    ii=int(np.argmax(abs(arr)));pk=float(abs(arr[ii]));tv=float(np.sum(abs(np.diff(arr))));rms=float(np.sqrt(np.mean(arr*arr)))
    metrics.append({'Story':story,'Case':case,'Axis':axis,'quantity':name,'n_saved':len(t),'t0_s':float(t[0]),'t1_s':float(t[-1]),'abs_peak_kN':pk,'signed_at_abs_peak_kN':float(arr[ii]),'peak_time_s':float(t[ii]),'source_D_row_at_peak':int(ad[ii,cd.index('SourceRow')]),
     'RMS_kN':rms,'total_variation_kN':tv,'TV_definition':'sum absolute successive saved-sample differences; no smoothing','TV_over_own_abs_peak':tv/pk,'TV_over_QT_TV':tv/tvqt,'abs_peak_over_QT_abs_peak':pk/pkqt,'RMS_over_QT_RMS':rms/rmsqt,
     'scope':'Numerical curve descriptors only; no smoothness-based cut inclusion or QS recognition'})
   sensitive.append({'Story':story,'Case':case,'Axis':axis,'QT_abs_peak_kN':pkqt,'t_QT_s':float(t[idt]),'QD_abs_peak_kN':float(max(abs(qd))),'t_QD_s':float(t[iq]),
     'QT_minus_QD_abs_peak_kN':float(abs(minus[im])),'t_minus_s':float(t[im]),'minus_peak_over_QT':float(abs(minus[im]))/pkqt,
     'QT_plus_QD_abs_peak_kN':float(abs(plus[ip])),'t_plus_s':float(t[ip]),'plus_peak_over_QT':float(abs(plus[ip]))/pkqt,
     'scope':'Both signs retained; cannot choose favorable sign to identify physical main-structure shear'})
   checks.append({'Story':story,'Case':case,'n_saved':len(t),'all_three_time_axes_exact':True,'QD_combo_QT_full_column_exact':True,'D_SourceRow_column_exact':True,'both_algebraic_columns_equal_prior_saved_combo_exact':True,'B_cache_key':kb[key],'D_cache_key':kd[key],'QD_combo_key':f'{story}__{case}__{axis}'})
assert len(anchors)==12 and len(metrics)==16 and len(sensitive)==4
table('same-time-QT-QD-algebra-12.csv',anchors);table('at-actual-QT-peak-4.csv',[r for r in anchors if r['anchor']=='tD']);table('curve-peak-variation-16.csv',metrics);table('plus-minus-direction-sensitivity-4.csv',sensitive)
assert all(sha(Path(x['path']))==x['sha256']for x in sources)
summary={'status':'numeric-frozen-await-independent-audit','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'actual_first_clock':'2026-11-03T21:49:18+08:00','sources':sources,'checks':checks,
 'raw_workbook_reads':0,'new_ODE_fit_solver':0,'frame_or_sectioncut_independent_reference':'Not present in the supplied paired-layer cache or Story Forces manifests used in this task; no independent frame/sectioncut same-freebody closure established here.',
 'physical_scope':'QD=sum nP at J upper end is structural internal resisting term; external nodal force opposite; native Story Forces Bottom cut sign/Link inclusion remains unproven by these arithmetic curves.',
 'no_smoothing':True,'tD_four_rows':[r for r in anchors if r['anchor']=='tD'],'variation_descriptors_not_a_physical_QS_test':True}
(H/'numeric-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['four_record_arithmetic.py','same-time-QT-QD-algebra-12.csv','at-actual-QT-peak-4.csv','curve-peak-variation-16.csv','plus-minus-direction-sensitivity-4.csv','numeric-summary.json']
manifest={'status':summary['status'],'at':summary['at'],'files':[{'relative':(H/n).relative_to(R).as_posix(),'bytes':(H/n).stat().st_size,'sha256':sha(H/n)}for n in names]}
(H/'numeric-delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'at':summary['at'],'rows12':12,'tD_rows':summary['tD_four_rows'],'source_group_count':4},ensure_ascii=False))
