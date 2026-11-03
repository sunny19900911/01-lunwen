from pathlib import Path
import csv,json,hashlib,math,datetime
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[4];W=R.parent/'W5-重燃双塔连体'
dirs={'B':W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存','D':W/'research/maxwell-20261017/experiments/R001/core-cache'}
cases={w+a for w in ['RH4','SHW4','SHW7'] for a in ['X','Y']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources={};meta={};groups={};arr={};cols={}
for model,d in dirs.items():
 for name in ['manifest.json','Story_Forces.npz']:
  p=d/name;sources[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size}
 m=json.loads((d/'manifest.json').read_text(encoding='utf-8'))['tables']['Story Forces'];meta[model]=m
 cols[model]=m['columns'];arr[model]=np.load(d/m['cache'],allow_pickle=False)
 for field in ['VX','VY']:assert m['units'][m['headers'].index(field)]=='kN'
 g={}
 for k,v in m['groups'].items():
  q=v['keys']
  if q.get('Location')=='Bottom' and q.get('Output Case')in cases:
   z=(q['Output Case'],q['Story']);assert z not in g;g[z]=k
 assert len(g)==72;groups[model]=g
assert set(groups['B'])==set(groups['D'])
out=[]
for case,story in sorted(groups['B'],key=lambda x:(x[0],int(x[1][5:]))):
 axis=case[-1];b=arr['B'][groups['B'][case,story]];d=arr['D'][groups['D'][case,story]]
 tb=b[:,cols['B'].index('Time')];td=d[:,cols['D'].index('Time')]
 assert np.array_equal(tb,td) and bool(np.all(np.diff(tb)>0))
 yb=b[:,cols['B'].index('V'+axis)];yd=d[:,cols['D'].index('V'+axis)]
 assert np.isfinite(yb).all() and np.isfinite(yd).all()
 pb=float(np.max(np.abs(yb)));pd=float(np.max(np.abs(yd)));assert pb>0
 ib=int(np.flatnonzero(np.abs(yb)==pb)[0]);id_=int(np.flatnonzero(np.abs(yd)==pd)[0])
 a=float(abs(yd[ib]));rp=100*(1-pd/pb);rat=100*(1-a/pb);delta=100*(pd-a)/pb
 assert delta>=0 and abs((rat-delta)-rp)<1e-12
 out.append({'Case':case,'Axis':axis,'Story':story,'P_B_kN':pb,'P_D_kN':pd,'B_signed_at_own_peak_kN':float(yb[ib]),'D_signed_at_own_peak_kN':float(yd[id_]),'t_B_s':float(tb[ib]),'t_D_s':float(td[id_]),'D_at_tB_signed_kN':float(yd[ib]),'A_abs_D_at_tB_kN':a,'r_peak_percent':rp,'r_at_percent':rat,'d_pp':delta,'absolute_peak_time_shift_s':abs(float(tb[ib])-float(td[id_])),'same_saved_peak_time':float(tb[ib])==float(td[id_]),'n_saved':len(tb),'t_start_s':float(tb[0]),'t_end_s':float(tb[-1]),'B_peak_source_row':int(b[ib,cols['B'].index('SourceRow')]),'D_peak_source_row':int(d[id_,cols['D'].index('SourceRow')]),'D_source_row_at_B_peak':int(d[ib,cols['D'].index('SourceRow')]),'B_tied_abs_peak_count':int(np.count_nonzero(np.abs(yb)==pb)),'D_tied_abs_peak_count':int(np.count_nonzero(np.abs(yd)==pd))})
for a in arr.values():a.close()
producer=R/'research/sessions/20261103-1700/roles/response/actual-versus-baseline-time-peak-72.csv'
pp={(x['Case'],x['Story']):x for x in csv.DictReader(producer.open(encoding='utf-8-sig'))}
assert len(pp)==72
maxerr=0.;count=0
for x in out:
 p=pp[x['Case'],x['Story']]
 for k,v in x.items():
  if isinstance(v,str):assert v==p[k]
  elif isinstance(v,bool):assert v==(p[k]=='True')
  else:
   e=abs(v-float(p[k]));maxerr=max(e,maxerr);assert e<1e-9,(k,v,p[k])
  count+=1
 assert p['Location']=='Bottom' and p['unit_force']=='kN' and p['unit_time']=='s' and p['saved_time_axes_exact']=='True'
def quant(a,p):
 s=sorted(a);ix=(len(s)-1)*p;lo=math.floor(ix);hi=math.ceil(ix)
 return s[lo]+(ix-lo)*(s[hi]-s[lo])
ds=[x['d_pp']for x in out];q={'d_median_pp':quant(ds,.5),'d_95percentile_pp':quant(ds,.95),'d_max_pp':max(ds),'max_d_record':max(out,key=lambda x:x['d_pp']),'minimum_d_pp':min(ds),'same_peak_time_count':sum(x['same_saved_peak_time']for x in out),'zero_d_count':sum(x['d_pp']==0 for x in out),'max_time_shift_s':max(x['absolute_peak_time_shift_s']for x in out),'tied_B_record_count':sum(x['B_tied_abs_peak_count']>1 for x in out),'tied_D_record_count':sum(x['D_tied_abs_peak_count']>1 for x in out)}
# Independently derived quantiles above do not borrow the production summary implementation.
with(H/'independent-actual-time-peak-72.csv').open('x',encoding='utf-8',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
for model,d in dirs.items():
 for name in ['manifest.json','Story_Forces.npz']:
  p=d/name;assert sha(p)==sources[str(p)]['sha256']
result={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'sources':sources,'scope':'Exactly72 matching Bottom main-axis groups from existing B/D caches; no raw Excel, ODE, fits or isolated QS','numeric_implementation':'Independent NumPy arrays, explicit first tied maximum with flatnonzero and sorted linear quantile formula','producer_fields_checked':count,'producer_max_abs_difference':maxerr,'all72_saved_grids_exact':True,'statistics':q,'must':0}
(H/'actual-cache-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
