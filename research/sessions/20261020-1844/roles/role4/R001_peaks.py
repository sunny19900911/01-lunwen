from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import csv,json,hashlib
O=Path(__file__).resolve().parent
R=O.parents[4];C=R.parent/'W5-重燃双塔连体/research/maxwell-20261017/experiments/R001/core-cache'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def js(n,x):
 p=O/n;assert not p.exists(),p;p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cs(n,rows):
 p=O/n;assert not p.exists(),p
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
m=json.loads((C/'manifest.json').read_text(encoding='utf-8'))
paths=[C/'manifest.json',C/'Story_Forces.npz',C/'Story_Drifts.npz',C/'Base_Reactions.npz']
js('R001-input-freeze.json',{'utc':now(),'code_sha256':sha(Path(__file__)),'numpy':np.__version__,'source_sha256':m['sha256'],'scope':'existing controlled native saved peaks; no workbook/solver/fill/interpolation/modal attribution','inputs':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]})
base=m['tables']['Base Reactions'];btime={}
with np.load(C/base['cache'],allow_pickle=False) as z:
 for k,g in base['groups'].items():btime[g['keys']['Output Case']]=z[k][:,base['columns'].index('Time')]
checks=[];shear=[];drift=[]
for name in ['Story Forces','Story Drifts']:
 tab=m['tables'][name];col=tab['columns']
 with np.load(C/tab['cache'],allow_pickle=False) as z:
  for k,g in tab['groups'].items():
   a=z[k];t=a[:,col.index('Time')];case=g['keys']['Output Case'];bt=btime[case]
   assert np.isfinite(a).all() and np.all(np.diff(t)>0)
   subset=bool(np.all(np.isin(np.round(t,8),np.round(bt,8))));exact=bool(np.array_equal(t,bt));assert subset
   r={'Story':g['keys']['Story'],'Case':case,'wave_family':case[:-1],'input_direction':case[-1],'Case_Type':g['keys']['Case Type'],'n_native':len(t),'n_base':len(bt),'coverage_fraction':len(t)/len(bt),'t0_s':float(t[0]),'t1_s':float(t[-1]),'exact_base_grid':exact,'all_times_in_base_grid':subset}
   if name=='Story Forces':r.update(Location=g['keys']['Location']);assert exact and r['Location']=='Bottom'
   else:r.update(Axis=g['keys']['Direction'],input_main_axis=case[-1]==g['keys']['Direction'])
   for field in (['VX','VY'] if name=='Story Forces' else ['Drift']):
    y=a[:,col.index(field)];i=int(np.argmax(abs(y)));r.update({field+'_peak_abs':float(abs(y[i])),field+'_signed_at_peak':float(y[i]),field+'_peak_t_s':float(t[i]),field+'_peak_SourceRow':int(a[i,col.index('SourceRow')])})
   r['units']='kN' if name=='Story Forces' else 'dimensionless drift ratio'
   r['scope']='native Bottom Story Forces; Link inclusion/sign unverified' if name=='Story Forces' else 'native recorded spatial-envelope peak; sparse time output; not fixed endpoint signal'
   (shear if name=='Story Forces' else drift).append(r)
   checks.append({'table':name,'key':k,'finite_unique_increasing':True,'base_subset':subset,'base_exact':exact})
  if name=='Story Forces':cs('R001-story-forces-72.csv',shear);print('FIRST_TABLE_SAVED '+now()+' rows='+str(len(shear)),flush=True)
  else:cs('R001-story-drifts-144.csv',drift)
assert len(shear)==72 and len(drift)==144
summary=[]
for case in sorted(btime):
 axis=case[-1];ss=[r for r in shear if r['Case']==case];dd=[r for r in drift if r['Case']==case and r['Axis']==axis];sp=max(ss,key=lambda r:r['V'+axis+'_peak_abs']);dp=max(dd,key=lambda r:r['Drift_peak_abs'])
 summary.append({'Case':case,'wave_family':case[:-1],'Axis':axis,'QT_control_Story':sp['Story'],'QT_peak_kN':sp['V'+axis+'_peak_abs'],'QT_peak_t_s':sp['V'+axis+'_peak_t_s'],'QT_peak_SourceRow':sp['V'+axis+'_peak_SourceRow'],'Drift_control_Story':dp['Story'],'Drift_peak_ratio':dp['Drift_peak_abs'],'Drift_peak_t_s':dp['Drift_peak_t_s'],'Drift_peak_SourceRow':dp['Drift_peak_SourceRow']})
cs('R001-main-axis-controls-6.csv',summary)
js('R001-peak-results.json',{'finished_utc':now(),'story_force_groups':len(shear),'story_drift_groups':len(drift),'force_rows':m['tables']['Story Forces']['data_rows'],'drift_rows':m['tables']['Story Drifts']['data_rows'],'checks':checks,'controls':summary,'drift_sparse_groups':sum(not r['exact_base_grid'] for r in drift),'raw_workbooks_read':0,'solver_runs':0,'modal_decompositions':0})
print(json.dumps(summary,ensure_ascii=False),flush=True)
