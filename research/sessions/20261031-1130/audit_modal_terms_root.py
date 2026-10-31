"""Independent check of the frozen modal terms; no integration or output fit."""
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
S=Path(__file__).resolve().parent;A=S/'roles/role4/R004';B=S/'roles/role4/R005';O=S/'root-R004-term-audit';O.mkdir(exist_ok=False)
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
man=json.loads((B/'delivery-manifest.json').read_text());out=man.get('outputs',man.get('files',[]))
for x in out:
 p=B/x.get('name',x.get('path',''))
 if p.is_file()and 'sha256'in x:assert sha(p)==x['sha256']
source=json.loads((A/'results.json').read_text())['arrays_local_only'];pairs={(d['Case'],d['Story']):d for d in read(B/'all12-threewaves-UPC-paired-36.csv')};anchors=read(B/'all12-four-anchors-both-zeta-signed-reference-288.csv')
write('input-freeze.json',dict(time_utc=datetime.now(timezone.utc).isoformat(),source_manifest_sha256=sha(B/'delivery-manifest.json'),cases=['SHW3X','SHW4X','RH4X'],independent_script_sha256=sha(Path(__file__)),scope='reconstruct all modal terms from frozen unit response factors; no production code imports, integration, output fit or native raw extraction'))
max_peak=max_U=max_P=max_identity=max_anchor=max_rest=0.;checked=0;summary=[]
for case in ['SHW3X','SHW4X','RH4X']:
 calc={}
 for z in [.05,.08]:
  rec=next(d for d in source if f'-{case}-z{z:g}-'in d['path']);path=Path(rec['path']);assert sha(path)==rec['sha256']
  env=read(B/f'mode-envelopes-{case}-z{z:g}-3600.csv');emap={(d['Story'],int(d['Mode'])):d for d in env};assert len(emap)==3600
  with np.load(path,allow_pickle=False)as ar:
   t=ar['t'];s=ar['s_unitGamma'];w=ar['omega'];coef=ar['B_direct'];kernel=s*w**2
   for i in range(12):
    story=f'Story{i+1}';v=kernel*(coef[i]/1000);peaks=np.linalg.norm(v,ord=np.inf,axis=0);y=np.add.reduce(v,axis=1);U=float(np.add.reduce(peaks));P=float(np.linalg.norm(y,ord=np.inf));C=P/U
    for r in range(300):
     e=emap[story,r+1];max_peak=max(max_peak,abs(peaks[r]-float(e['reference_mode_abs_peak_kN'])));assert abs(float(e['weight_this_zeta'])-peaks[r]/U)<1e-12;checked+=1
    row=pairs[case,story];max_U=max(max_U,abs(U-float(row['U5_sum_single_mode_peaks_kN'if z==.05 else 'U8_sum_single_mode_peaks_kN'])));max_P=max(max_P,abs(P-float(row['P5_reference_peak_kN'if z==.05 else 'P8_reference_peak_kN'])))
    if z==.05:top=np.lexsort((np.arange(300),-peaks))[:5];assert ';'.join(str(r+1)for r in top)==row['top5_modes_fixed5']
    else:top=np.array([int(x)-1 for x in row['top5_modes_fixed5'].split(';')])
    rest=[r for r in range(300)if r not in top]
    for ad in [d for d in anchors if d['Case']==case and d['Story']==story and float(d['zeta'])==z]:
     ix=np.flatnonzero(np.isclose(t,float(ad['time_s']),rtol=0,atol=1e-10));assert len(ix)==1;j=int(ix[0]);max_anchor=max(max_anchor,abs(y[j]-float(ad['reference_sum_signed_kN'])));max_rest=max(max_rest,abs(v[j,rest].sum()-float(ad['remaining295_signed_sum_kN'])))
     for k,r in enumerate(top,1):assert int(ad[f'fixed5_rank{k}_Mode'])==r+1;assert abs(v[j,r]-float(ad[f'fixed5_rank{k}_signed_ref_kN']))<1e-8
    calc[z,story]=(U,P,C)
 for i in range(1,13):
  st=f'Story{i}';u5,p5,c5=calc[.05,st];u8,p8,c8=calc[.08,st];dif=abs(p8/p5-(u8/u5)*(c8/c5));max_identity=max(max_identity,dif);row=pairs[case,st];assert abs(float(row['U8_over_U5'])-u8/u5)<1e-12;assert abs(float(row['C8_over_C5'])-c8/c5)<1e-12;assert abs(float(row['P8_over_P5'])-p8/p5)<1e-12
  summary.append(dict(Case=case,Story=st,U8_U5=u8/u5,C8_C5=c8/c5,P8_P5=p8/p5,reference_reduction_pct=100*(1-p8/p5),reference_minus_native_reduction_pp=float(row['reference_minus_native_decrease_percentage_points'])))
assert max(max_peak,max_U,max_P,max_anchor,max_rest)<1e-8 and checked==21600
result=dict(completed_utc=datetime.now(timezone.utc).isoformat(),single_modal_peak_checks=checked,pairs=36,anchor_rows=len(anchors),max_modal_peak_abs_difference_kN=max_peak,max_U_abs_difference_kN=max_U,max_P_abs_difference_kN=max_P,max_anchor_sum_difference_kN=max_anchor,max_remaining295_sum_difference_kN=max_rest,max_UPC_identity_error=max_identity,max_observed_reference_native_peak_reduction_difference_pp=max(abs(d['reference_minus_native_reduction_pp'])for d in summary),scope='independent factorized reference-term audit only; original native responses/ODE separately audited by role2R005',must_changes=0)
write('checks.json',result)
with(O/'independent-pairs-36.csv').open('x',encoding='utf-8',newline='')as f:ww=csv.DictWriter(f,fieldnames=list(summary[0]));ww.writeheader();ww.writerows(summary)
write('manifest.json',dict(files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p))for p in O.iterdir()if p.is_file()]))
print(json.dumps(result,ensure_ascii=False))
