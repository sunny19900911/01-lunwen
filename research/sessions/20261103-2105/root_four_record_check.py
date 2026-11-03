from pathlib import Path
import numpy as np,json,csv,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
q=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
rows=[]
with np.load(q,allow_pickle=False)as z:
 for st in [8,10]:
  for case in ['RH4X','RH4Y']:
   a=z[f'Story{st}__{case}__{case[-1]}'];t,qt,qd=a[:,0],a[:,1],a[:,2]
   assert np.allclose(qt-qd,a[:,3],atol=1e-12)and np.allclose(qt+qd,a[:,4],atol=1e-12)
   k=int(np.argmax(abs(qt)))
   rows.append({'Story':st,'Case':case,'time_QT_peak_s':float(t[k]),'QT_kN':float(qt[k]),'QD_J_resisting_kN':float(qd[k]),'QT_minus_QD_kN':float(qt[k]-qd[k]),'QT_plus_QD_kN':float(qt[k]+qd[k]),'SourceRow':int(a[k,5]),'peak_abs_QT_kN':float(max(abs(qt))),'peak_abs_QT_minus_QD_kN':float(max(abs(qt-qd))),'peak_abs_QT_plus_QD_kN':float(max(abs(qt+qd)))})
p=S/'root-four-records.csv';assert not p.exists()
with p.open('x',encoding='utf-8',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(S/'root-four-record-check.json').write_text(json.dumps({'source_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'records':rows,'arithmetic_confirmed':True,'independent_cut_force_available_in_this_check':False,'QS_identified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False))
