from pathlib import Path
import csv,json,hashlib,datetime
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[4];W=R.parent/'W5-重燃双塔连体'
db=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';dd=W/'research/maxwell-20261017/experiments/R001/core-cache'
combo_path=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rc(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
sources=[db/'manifest.json',dd/'manifest.json',db/'Story_Forces.npz',dd/'Story_Forces.npz',combo_path]
before={str(p):{'sha256':sha(p),'bytes':p.stat().st_size}for p in sources}
man={x:json.loads((p/'manifest.json').read_text(encoding='utf-8'))['tables']['Story Forces']for x,p in [('B',db),('D',dd)]}
zz={x:np.load(p/'Story_Forces.npz',allow_pickle=False)for x,p in [('B',db),('D',dd)]}
cz=np.load(combo_path,allow_pickle=False)
keys={x:{(v['keys']['Output Case'],v['keys']['Story']):k for k,v in m['groups'].items()if v['keys'].get('Location')=='Bottom'}for x,m in man.items()}
cases=[('Story8',c)for c in ['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']]+[('Story10','RH4Y')]
allrows=[];account=[]
for story,case in cases:
 axis=case[-1];ab=zz['B'][keys['B'][case,story]];ad=zz['D'][keys['D'][case,story]];cc=cz[story+'__'+case+'__'+axis]
 cb=man['B']['columns'];cd=man['D']['columns'];t=ab[:,cb.index('Time')]
 yb=ab[:,cb.index('V'+axis)];yd=ad[:,cd.index('V'+axis)];f=cc[:,2]
 assert np.array_equal(t,ad[:,cd.index('Time')]) and np.array_equal(t,cc[:,0])
 assert np.array_equal(yd,cc[:,1]) and np.array_equal(ad[:,cd.index('SourceRow')],cc[:,5])
 def peak(y):return int(np.flatnonzero(np.abs(y)==np.max(np.abs(y)))[0])
 ib=peak(yb);id_=peak(yd);iq=peak(f);pb=float(abs(yb[ib]));pd=float(abs(yd[id_]));pf=float(abs(f[iq]));sig=int(np.sign(yb[ib]))
 for label,i in [('tB',ib),('tD',id_),('tQD',iq)]:
  allrows.append({'Case':case,'Axis':axis,'Story':story,'anchor':label,'time_s':float(t[i]),'B_QT_signed_kN':float(yb[i]),'D_QT_signed_kN':float(yd[i]),'QD_signed_J_resisting_kN':float(f[i]),'B_QT_abs_kN':float(abs(yb[i])),'D_QT_abs_kN':float(abs(yd[i])),'QD_abs_over_own_abs_peak_percent':100*float(abs(f[i]))/pf,'QD_signed_over_own_abs_peak_percent':100*float(f[i])/pf,'D_QT_abs_over_own_abs_peak_percent':100*float(abs(yd[i]))/pd,'B_QT_abs_over_own_abs_peak_percent':100*float(abs(yb[i]))/pb,'QD_over_same_D_QT_signed_ratio':float(f[i]/yd[i]),'B_SourceRow':int(ab[i,cb.index('SourceRow')]),'D_SourceRow':int(ad[i,cd.index('SourceRow')]),'QD_combo_matches_D_SourceRow':True})
 s=pb-sig*float(yd[ib]);m=pd-sig*float(yd[ib]);a=float(abs(yd[ib]))
 assert abs((s-m)-(pb-pd))<1e-9 and m>=0
 account.append({'Case':case,'Axis':axis,'Story':story,'n_saved':len(t),'P_B_kN':pb,'P_D_kN':pd,'P_QD_abs_kN':pf,'t_B_s':float(t[ib]),'t_D_s':float(t[id_]),'t_QD_s':float(t[iq]),'B_signed_at_tB_kN':float(yb[ib]),'D_signed_at_tB_kN':float(yd[ib]),'D_signed_at_tD_kN':float(yd[id_]),'B_signed_at_tD_kN':float(yb[id_]),'QD_signed_at_tB_kN':float(f[ib]),'QD_signed_at_tD_kN':float(f[id_]),'sigma_B_peak':sig,'old_direction_signed_weakening_S_kN':s,'own_peak_selection_recovery_M_kN':m,'P_B_minus_P_D_kN':pb-pd,'S_minus_M_identity_residual_kN':s-m-(pb-pd),'abs_old_time_drop_kN':pb-a,'abs_repeak_recovery_kN':pd-a,'r_at_percent':100*(1-a/pb),'r_D_peak_percent':100*(1-pd/pb),'d_pp':100*(pd-a)/pb,'D_at_tB_same_sign_as_B_peak':int(np.sign(yd[ib]))==sig,'D_own_peak_same_sign_as_B_peak':int(np.sign(yd[id_]))==sig,'t_D_minus_t_B_s':float(t[id_]-t[ib]),'t_QD_minus_t_D_s':float(t[iq]-t[id_]),'QD_abs_at_tB_over_own_peak_percent':100*float(abs(f[ib]))/pf,'QD_abs_at_tD_over_own_peak_percent':100*float(abs(f[id_]))/pf})
for z in zz.values():z.close()
cz.close()
P=H.parent/'response';freeze=json.loads((P/'numeric-delivery-manifest.json').read_text(encoding='utf-8'));assert freeze['status'].startswith('numbers-frozen')
freeze2=json.loads((P/'R002/numeric-delivery-manifest.json').read_text(encoding='utf-8'));assert freeze2['status'].startswith('frozen')
pr=rc(P/'Story8-native-three-times-18.csv')+rc(P/'R002/Story10-RH4Y-three-times-3.csv')
pa=rc(P/'Story8-actual-peak-accounting-6.csv')+rc(P/'R002/Story10-RH4Y-peak-accounting-1.csv')
rk={(x['Story'],x['Case'],x['anchor']):x for x in pr};ak={(x['Story'],x['Case']):x for x in pa}
fields=0;err=0.
for records,lookup,key in [(allrows,rk,lambda x:(x['Story'],x['Case'],x['anchor'])),(account,ak,lambda x:(x['Story'],x['Case']))]:
 for x in records:
  p=lookup[key(x)]
  for k,v in x.items():
   if k not in p:continue
   if isinstance(v,str):assert v==p[k],(k,v,p[k])
   elif isinstance(v,bool):assert v==(p[k]=='True')
   else:
    e=abs(v-float(p[k]));err=max(err,e);assert e<1e-9,(k,v,p[k])
   fields+=1
for name,data in [('independent-three-times-21.csv',allrows),('independent-peak-accounting-7.csv',account)]:
 with(H/name).open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
assert before=={str(p):{'sha256':sha(p),'bytes':p.stat().st_size}for p in sources}
result={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'sources':before,'method':'Independent cache slicing of seven layer-case records; direct native B/D columns plus preserved nP combo; old combo schema read, production algorithms not imported or read','rows':21,'accounting_cases':7,'producer_fields_checked':fields,'max_abs_field_difference':err,'Story8_cases':[x for x in account if x['Story']=='Story8'],'Story10_RH4Y':next(x for x in account if x['Story']=='Story10'),'all_seven_old_and_new_D_peak_sign_same_as_B_peak':all(x['D_at_tB_same_sign_as_B_peak']and x['D_own_peak_same_sign_as_B_peak']for x in account),'Story8_max_abs_B_D_time_shift_s':max(abs(x['t_D_minus_t_B_s'])for x in account if x['Story']=='Story8'),'must':0,'scope':'S-M is peak accounting, not modal/phase/causal attribution; QD is J-end internal resisting convention, not isolated QS'}
(H/'actual-sametime-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k]for k in ['rows','accounting_cases','producer_fields_checked','max_abs_field_difference','Story8_max_abs_B_D_time_shift_s','Story10_RH4Y','must']},ensure_ascii=False))
