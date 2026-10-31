import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R004';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rule=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));Ns=rule['deduplicated_Ns'];L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 assert (O/n).stat().st_size<1000000
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
massrates={N:next(d['cumulative_native_UX_at_N'] for d in rule['requested_schemes'] if d['N']==N) for N in Ns};states={N:[] for N in Ns};saved={};arraypaths=[];max300match=0.;maxviolation=0.
for source in rule['inputs']:
 path=Path(source['path']);assert sha(path)==source['sha256']
 if path.suffix!='.npz':continue
 case=path.name.split('-')[1];z=float(path.name.split('-z')[1].split('-')[0])
 with np.load(path,allow_pickle=False) as a:
  t=a['t'];g=a['s_unitGamma']*a['omega']**2;B=a['B_direct'];Y=a['shear_elastic_inertia_predicted_kN'];vout=np.empty((len(t),12,len(Ns)))
  for st in range(1,13):
   story='Story'+str(st);terms=g*B[st-1]/1000;cum=np.cumsum(terms,axis=1);full=cum[:,-1];max300match=max(max300match,float(np.max(abs(full-Y[:,st-1]))));assert np.max(abs(full-Y[:,st-1]))<1e-8
   amp=np.max(abs(terms),axis=0);U=math.fsum(amp);Pfull=float(np.max(abs(full)));ifull=int(np.argmax(abs(full)));native=a['shear_native_'+story+'_kN'];Pnative=float(np.max(abs(native)));inative=int(np.argmax(abs(native)));dref=float(np.linalg.norm(full));dnative=float(np.linalg.norm(native))
   for ni,N in enumerate(Ns):
    vn=cum[:,N-1];vout[:,st-1,ni]=vn;PN=float(np.max(abs(vn)));iN=int(np.argmax(abs(vn)));UN=math.fsum(amp[:N]);T=math.fsum(amp[N:]);dinf=float(np.max(abs(full-vn)));maxviolation=max(maxviolation,dinf-T);assert dinf<=T+1e-8
    scale=T/(PN-T) if PN>T else None;peakrel=abs(PN-Pfull)/Pfull;assert scale is None or peakrel<=scale+1e-12
    row=dict(N=N,native_UX_cumulative_mass_ratio=massrates[N],Case=case,zeta=z,Story=story,signed_NRMSE_vs_full300_reference=float(np.linalg.norm(vn-full)/dref),peakN_kN=PN,peak300_kN=Pfull,peakN_over_peak300_minus1=PN/Pfull-1,absolute_peak_difference_vs_full300_kN=abs(PN-Pfull),peakN_time_s=float(t[iN]),peak300_time_s=float(t[ifull]),peak_time_shift_Nminus300_s=float(t[iN]-t[ifull]),U_N_kN=UN,U300_kN=U,U_N_over_U300=UN/U,tail_independent_peak_sum_T_kN=T,max_abs_curve_Nminus300_kN=dinf,curve_tail_inequality_pass=bool(dinf<=T+1e-8),relative_peak_scale_full300_only=scale,relative_peak_scale_status='defined' if scale is not None else 'undefined_PN_le_T',peakN_native_absolute_curve_NRMSE=float(np.linalg.norm(abs(vn)-abs(native))/dnative),native_peak_kN=Pnative,peakN_over_native_peak_minus1=PN/Pnative-1,native_peak_time_s=float(t[inative]),native_signed_at_Npeak_kN=float(native[iN]),prediction_signed_at_native_peak_kN=float(vn[inative]),scope='physical prefix vs defined300 reference; native absolute only; no fullFE bound')
    states[N].append(row);saved[case,z,story,N]=row
  out=L/f'prefixes-{case}-z{z:g}.npz';np.savez_compressed(out,t=t,Ns=np.array(Ns),V_elastic_prefix_kN=vout);arraypaths.append(dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out)))
ratios={N:[] for N in Ns}
for N in Ns:
 for case in ['SHW3X','SHW4X','RH4X']:
  for st in range(1,13):
   story='Story'+str(st);a=saved[case,.05,story,N];b=saved[case,.08,story,N];P5=a['peakN_kN'];P8=b['peakN_kN'];T5=a['tail_independent_peak_sum_T_kN'];T8=b['tail_independent_peak_sum_T_kN'];rfull=b['peak300_kN']/a['peak300_kN'];rn=b['native_peak_kN']/a['native_peak_kN'];valid=P5>T5
   lo=max(0,P8-T8)/(P5+T5) if valid else None;hi=(P8+T8)/(P5-T5) if valid else None;inside=lo-1e-12<=rfull<=hi+1e-12 if valid else None;assert inside is not False
   ratios[N].append(dict(N=N,native_UX_cumulative_mass_ratio=massrates[N],Case=case,Story=story,PN5_kN=P5,PN8_kN=P8,T5_kN=T5,T8_kN=T8,prefix_peak_ratio_8over5=P8/P5,full300_peak_ratio_8over5=rfull,native_peak_ratio_8over5=rn,prefix_peak_decrease_percent=100*(1-P8/P5),full300_peak_decrease_percent=100*(1-rfull),native_peak_decrease_percent=100*(1-rn),prefix_minus_full300_decrease_percentage_points=100*(rfull-P8/P5),prefix_minus_native_decrease_percentage_points=100*(rn-P8/P5),ratio_interval_lower_full300_only=lo,ratio_interval_upper_full300_only=hi,interval_width=hi-lo if valid else None,interval_status='defined' if valid else 'undefined_PN5_le_T5',full300_ratio_in_interval=inside,scope='tail interval inside defined300 linear reference only; not actual FE guarantee'))
summary=[]
for N in Ns:
 rr=states[N];pp=ratios[N];cs(f'N{N}-all12-threewaves-twozeta-convergence-72.csv',rr);cs(f'N{N}-all12-threewaves-peakratio-intervals-36.csv',pp)
 summary.append(dict(N=N,native_UX_cumulative_mass_ratio=massrates[N],state_rows=len(rr),max_signed_NRMSE_vs_full300=max(d['signed_NRMSE_vs_full300_reference'] for d in rr),max_abs_peak_relative_difference_vs_full300=max(abs(d['peakN_over_peak300_minus1']) for d in rr),minimum_layer_envelope_retention=min(d['U_N_over_U300'] for d in rr),max_native_absolute_curve_NRMSE=max(d['peakN_native_absolute_curve_NRMSE'] for d in rr),max_abs_peak_relative_difference_vs_native=max(abs(d['peakN_over_native_peak_minus1']) for d in rr),undefined_relative_peak_scale_states=sum(d['relative_peak_scale_full300_only'] is None for d in rr),undefined_peakratio_intervals=sum(d['interval_status']!='defined' for d in pp),max_abs_peak_decrease_difference_vs_full300_pp=max(abs(d['prefix_minus_full300_decrease_percentage_points']) for d in pp),scope='all predeclared schemes retained, no output selection'))
cs('all-N-engineering-convergence-summary-5.csv',summary);cs('Story5-Story12-all-N-state-convergence-60.csv',[d for N in Ns for d in states[N] if d['Story'] in ['Story5','Story12']]);cs('Story5-Story12-all-N-peakratio-intervals-30.csv',[d for N in Ns for d in ratios[N] if d['Story'] in ['Story5','Story12']])
js('results.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),Ns=Ns,state_rows_total=sum(map(len,states.values())),paired_ratio_rows_total=sum(map(len,ratios.values())),summary=summary,max_full300_rebuild_difference_vs_R004_kN=max300match,max_curve_tail_violation_before_tolerance_kN=maxviolation,all_tail_inequalities_pass=True,all_defined_ratio_intervals_contain_full300=True,local_only_arrays=arraypaths,sources_unchanged=all(sha(Path(d['path']))==d['sha256'] for d in rule['inputs']),no_new_ODE_fit_or_scheme_selection=True))
print(json.dumps(dict(summary=summary,max_full300_difference=max300match,max_tail_violation=maxviolation,arrays=len(arraypaths)),ensure_ascii=False,indent=2))
