from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[4];O=H/'R002';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig')as f:return list(csv.DictReader(f))
def table(name,rr):
 p=O/name;assert not p.exists()
 with p.open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def js(name,d):
 p=O/name;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
W=R.parent/'W5-重燃双塔连体';B=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';D=W/'research/maxwell-20261017/experiments/R001/core-cache'
mb=json.loads((B/'manifest.json').read_text(encoding='utf-8'));md=json.loads((D/'manifest.json').read_text(encoding='utf-8'));tb=mb['tables']['Story Forces'];td=md['tables']['Story Forces'];cb=tb.get('columns',tb.get('value_columns'));cd=td.get('columns',td.get('value_columns'))
pb=B/tb['cache'];pd=D/td['cache'];pq=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
old72=R/'research/sessions/20261103-1700/roles/response/actual-versus-baseline-time-peak-72.csv';old24=R/'research/sessions/20261103-1458/roles/response/native-device-layer-timing-24.csv'
case='RH4Y';axis='Y';story='Story10';old=next(r for r in read(old72)if r['Story']==story and r['Case']==case);tim=next(r for r in read(old24)if r['Story']==story and r['Case']==case)
sources=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in [B/'manifest.json',D/'manifest.json',pb,pd,pq,old72,old24]]
key=lambda g:tuple(g['keys'][x]for x in ['Output Case','Story','Location']);kb={key(g):k for k,g in tb['groups'].items()};kd={key(g):k for k,g in td['groups'].items()};k=(case,story,'Bottom')
with np.load(pb,allow_pickle=False)as zb,np.load(pd,allow_pickle=False)as zd,np.load(pq,allow_pickle=False)as zq:
 ab=zb[kb[k]];ad=zd[kd[k]];aq=zq[f'{story}__{case}__{axis}'];t=ab[:,cb.index('Time')];b=ab[:,cb.index('V'+axis)];d=ad[:,cd.index('V'+axis)];q=aq[:,2]
 assert np.array_equal(t,ad[:,cd.index('Time')])and np.array_equal(t,aq[:,0])and np.array_equal(d,aq[:,1])and np.array_equal(ad[:,cd.index('SourceRow')],aq[:,5])
 assert np.isfinite(ab).all()and np.isfinite(ad).all()and np.isfinite(aq).all()and np.all(np.diff(t)>0)
 ib=int(np.argmax(abs(b)));idd=int(np.argmax(abs(d)));iq=int(np.argmax(abs(q)));pB=float(abs(b[ib]));pD=float(abs(d[idd]));pQ=float(abs(q[iq]));sig=float(np.sign(b[ib]))
 for value,field in [(pB,'P_B_kN'),(pD,'P_D_kN'),(float(t[ib]),'t_B_s'),(float(t[idd]),'t_D_s')]:assert abs(value-float(old[field]))<1e-9
 assert abs(pQ-float(tim['QD_abs_peak_kN']))<1e-9 and t[iq]==float(tim['t_QD_peak_s'])and abs(q[idd]-float(tim['QD_signed_at_QT_peak_kN']))<1e-9
 anchors=[]
 for label,ii in [('tB',ib),('tD',idd),('tQD',iq)]:
  anchors.append({'Case':case,'Axis':axis,'Story':story,'anchor':label,'time_s':float(t[ii]),'B_QT_signed_kN':float(b[ii]),'D_QT_signed_kN':float(d[ii]),'QD_signed_J_resisting_kN':float(q[ii]),
    'QD_abs_over_own_abs_peak_percent':100*abs(float(q[ii]))/pQ,'QD_signed_over_own_abs_peak_percent':100*float(q[ii])/pQ,'D_QT_abs_over_own_abs_peak_percent':100*abs(float(d[ii]))/pD,'B_QT_abs_over_own_abs_peak_percent':100*abs(float(b[ii]))/pB,
    'B_SourceRow':int(ab[ii,cb.index('SourceRow')]),'D_SourceRow':int(ad[ii,cd.index('SourceRow')]),'QD_combo_matches_D_SourceRow':True,'scope':'Simultaneous native outputs; no QS or causal component subtraction'})
 S=pB-sig*float(d[ib]);M=pD-sig*float(d[ib]);A=abs(float(d[ib]));drop=pB-pD
 result={'Case':case,'Axis':axis,'Story':story,'n_saved':len(t),'P_B_kN':pB,'P_D_kN':pD,'P_QD_abs_kN':pQ,'t_B_s':float(t[ib]),'t_D_s':float(t[idd]),'t_QD_s':float(t[iq]),
  'B_signed_at_tB_kN':float(b[ib]),'D_signed_at_tB_kN':float(d[ib]),'D_signed_at_tD_kN':float(d[idd]),'B_signed_at_tD_kN':float(b[idd]),'QD_signed_at_tB_kN':float(q[ib]),'QD_signed_at_tD_kN':float(q[idd]),
  'sigma_B_peak':int(sig),'old_direction_signed_weakening_S_kN':S,'own_peak_selection_recovery_M_kN':M,'P_B_minus_P_D_kN':drop,'S_minus_M_identity_residual_kN':S-M-drop,
  'r_at_percent':100*(1-A/pB),'r_D_peak_percent':100*(1-pD/pB),'d_pp':100*(pD-A)/pB,'D_at_tB_same_sign_as_B_peak':bool(np.sign(d[ib])==sig),'D_own_peak_same_sign_as_B_peak':bool(np.sign(d[idd])==sig),
  't_D_minus_t_B_s':float(t[idd]-t[ib]),'t_QD_minus_t_D_s':float(t[iq]-t[idd]),'QD_abs_at_tB_over_own_peak_percent':100*abs(float(q[ib]))/pQ,'QD_abs_at_tD_over_own_peak_percent':100*abs(float(q[idd]))/pQ,
  'scope':'Actual saved-curve peak accounting; not a causal phase share or damper-generated new-peak proof'}
 assert abs(result['S_minus_M_identity_residual_kN'])<1e-9
 assert abs(result['d_pp']-float(old['d_pp']))<1e-10
table('Story10-RH4Y-three-times-3.csv',anchors);table('Story10-RH4Y-peak-accounting-1.csv',[result]);assert all(sha(Path(x['path']))==x['sha256']for x in sources)
js('numeric-summary.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'selection':'Root selected max absolute B/D peak-time shift among complete native-P Story8-11 × six cases, using prior frozen24/72; this role adds exactly one new group','result':result,'all_full_grids_and_QT_columns_exact':True,'sources':sources,'new_ODE_or_fits':0,'raw_workbook_reads':0})
names=['Story10-RH4Y-three-times-3.csv','Story10-RH4Y-peak-accounting-1.csv','numeric-summary.json']
js('numeric-delivery-manifest.json',{'status':'frozen-await-independent-audit','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'files':[{'relative':(O/n).relative_to(R).as_posix(),'bytes':(O/n).stat().st_size,'sha256':sha(O/n)}for n in names]+[{'relative':Path(__file__).relative_to(R).as_posix(),'bytes':Path(__file__).stat().st_size,'sha256':sha(Path(__file__))}]})
print(json.dumps(result,ensure_ascii=False))
