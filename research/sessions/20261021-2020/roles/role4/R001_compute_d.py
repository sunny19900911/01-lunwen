from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
O=Path(__file__).resolve().parent;R=O.parents[4];S=R/'research/sessions/20261020-1844/roles/role4/R002-all14-main-axis-168.csv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
start=datetime.now(timezone.utc);source_sha=sha(S)
save('R001-input-definition.json',{'utc':start.isoformat(),'source':str(S),'source_sha256':source_sha,'code_sha256':sha(Path(__file__)),'definitions':'A=abs(V_M(t_B)); r_at=100*(1-A/PB); d_pp=100*(PM-A)/PB; r_peak=100*(1-PM/PB)','inequality_tolerance_kN':'1e-10*max(1,PM)','identity_tolerance_pp':1e-10,'quantiles':'linear interpolation at (n-1)*p','tie_scope':'reuse previously selected first saved absolute peak t_B; not an all-tied-times audit','scope':'frozen 168 matched B/M native Bottom records; no arrays, fits, ODE or actual-device comparison'})
with S.open(encoding='utf-8-sig',newline='') as f:raw=list(csv.DictReader(f))
rows=[]
for line,r in enumerate(raw,2):
 pb=float(r['P0_kN']);pm=float(r['P3_kN']);a=abs(float(r['label3_at_label0_peak_kN']));assert pb>0 and a<=pm+1e-10*max(1,pm)
 rat=100*(1-a/pb);d=100*(pm-a)/pb;rp=100*(1-pm/pb);err=rp-(rat-d);assert abs(err)<=1e-10 and abs(rp-float(r['peak_reduction_percent']))<=1e-10
 rows.append({'Case':r['Case'],'Story':r['Story'],'Axis':r['Axis'],'Location':r['Location'],'P_B_kN':pb,'P_M_kN':pm,'V_M_at_tB_signed_kN':float(r['label3_at_label0_peak_kN']),'A_abs_V_M_at_tB_kN':a,'t_B_s':float(r['t_peak0_s']),'t_M_s':float(r['t_peak3_s']),'r_at_percent':rat,'d_pp':d,'r_peak_percent':rp,'identity_residual_pp':err,'source_CSV_line':line,'source_row_B_peak':r['source_row0'],'source_row_M_peak':r['source_row3']})
assert len(rows)==168 and len({(r['Case'],r['Story']) for r in rows})==168 and sha(S)==source_sha
with (O/'R001-d-168.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
ordered=sorted(rows,key=lambda r:r['d_pp']);v=[r['d_pp'] for r in ordered]
def q(p):
 z=(len(v)-1)*p;i=int(math.floor(z));j=int(math.ceil(z));return v[i]+(v[j]-v[i])*(z-i)
end=datetime.now(timezone.utc);result={'status':'computed_pending_independent_numeric_review','start_utc':start.isoformat(),'finished_utc':end.isoformat(),'execution_seconds':(end-start).total_seconds(),'rows':168,'source_sha256':source_sha,'d_pp_quantiles':{str(p):q(p) for p in [0,.25,.5,.75,.9,.95,1]},'minimum':ordered[0],'maximum':ordered[-1],'top_five':ordered[-5:][::-1],'max_identity_residual_pp':max(abs(r['identity_residual_pp']) for r in rows),'negative_d_rows':sum(r['d_pp']<0 for r in rows),'all_tied_peak_times_audited':False,'new_arrays_or_ODE':0}
save('R001-d-summary.json',result)
save('R001-delivery-manifest.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'status':result['status'],'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R001*')) if p.is_file()]})
print(json.dumps({'quantiles':result['d_pp_quantiles'],'maximum':result['maximum'],'minimum':result['minimum'],'rows':168,'residual':result['max_identity_residual_pp'],'finished_utc':end.isoformat()},ensure_ascii=False))
