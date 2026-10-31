import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R004';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 assert (O/n).stat().st_size<1000000
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=json.loads((P/'results.json').read_text(encoding='utf-8'));ff=[d for d in read(P/'shear-two-operator-absolute-diagnostics-144.csv') if d['operator']=='elastic_inertia'];sources=[Path(d['path']) for d in old['arrays_local_only']]+[P/'shear-two-operator-absolute-diagnostics-144.csv',P/'results.json'];bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
for d in old['arrays_local_only']:assert sha(Path(d['path']))==d['sha256']
groups=[('mode1to3',0,3),('mode4to9',3,9),('mode10to13',9,13),('mode14to300',13,300)]
js('input-rules-freeze.json',dict(start_observed_utc='2026-10-31T04:17:58+00:00',deadline_utc='2026-10-31T04:29:58+00:00',frozen_utc=datetime.now(timezone.utc).isoformat(),inputs=bindings,definition='v_srζ=B_sr*omega_r^2*s_rζ/1000, a_rζ=max_t abs(v), Uζ=sum_r a, Pζ=max_t abs(sum_r v), Cζ=Pζ/Uζ',weights='a_r5/U5; fixed top5 ranked descending 5% weight, ties increasing Mode; all300 per state retained',groups=[dict(name=n,first_mode=i+1,last_mode=j) for n,i,j in groups],anchors='predicted5 peak, predicted8 peak, native5 absolute peak, native8 absolute peak; evaluate both zeta at all four anchor times, even duplicate times retain labels',native_policy='native absolute peaks and decrease only; signed modal terms always reference positive rcut^TKu; eta unknown, no sign trials',reference_scope='physical-source elastic inertia-projection linear reference, not unique native FNA decomposition',no_new_ODE_fit_or_CM_metric_recalculation=True))
pairs=[];anchors=[];dominance=[];maxidentity=maxclosure=maxgroup=maxoldP=0.;modefiles=[]
for case in ['SHW3X','SHW4X','RH4X']:
 src5=next(Path(d['path']) for d in old['arrays_local_only'] if f'-{case}-z0.05-' in d['path']);src8=next(Path(d['path']) for d in old['arrays_local_only'] if f'-{case}-z0.08-' in d['path'])
 with np.load(src5,allow_pickle=False) as a5,np.load(src8,allow_pickle=False) as a8:
  t=a5['t'];assert np.array_equal(t,a8['t']);B=a5['B_direct'];assert np.array_equal(B,a8['B_direct']) and np.array_equal(a5['omega'],a8['omega']);omega=a5['omega'];kern={.05:a5['s_unitGamma']*omega**2,.08:a8['s_unitGamma']*omega**2};stored={.05:a5['shear_elastic_inertia_predicted_kN'],.08:a8['shear_elastic_inertia_predicted_kN']};allmoderows={.05:[],.08:[]}
  for storynum in range(1,13):
   story='Story'+str(storynum);j=storynum-1;terms={z:K*B[j][None,:]/1000 for z,K in kern.items()};sums={z:x.sum(axis=1) for z,x in terms.items()};ap={z:np.max(abs(x),axis=0) for z,x in terms.items()};apindex={z:np.argmax(abs(x),axis=0) for z,x in terms.items()};U={z:float(a.sum()) for z,a in ap.items()};ip={z:int(np.argmax(abs(x))) for z,x in sums.items()};Pp={z:float(abs(sums[z][ip[z]])) for z in [.05,.08]};C={z:Pp[z]/U[z] for z in [.05,.08]}
   assert all(0<C[z]<=1+1e-12 for z in [.05,.08]);toporder=np.lexsort((np.arange(300),-ap[.05]));rank=np.empty(300,dtype=int);rank[toporder]=np.arange(1,301);top=toporder[:5];remaining=np.array([i for i in range(300) if i not in set(top)]);assert len(remaining)==295
   native={.05:a5['shear_native_'+story+'_kN'],.08:a8['shear_native_'+story+'_kN']};ni={z:int(np.argmax(abs(v))) for z,v in native.items()};Pn={z:float(abs(native[z][ni[z]])) for z in [.05,.08]}
   for z in [.05,.08]:
    dd=next(d for d in ff if d['Case']==case and float(d['zeta'])==z and d['Story']==story);assert abs(float(t[ni[z]])-float(dd['native_peak_time_s']))<1e-9;maxoldP=max(maxoldP,abs(Pp[z]-float(dd['predicted_absolute_peak'])));assert np.max(abs(sums[z]-stored[z][:,j]))<1e-8
    for ir in range(300):allmoderows[z].append(dict(Story=story,Mode=ir+1,reference_mode_abs_peak_kN=float(ap[z][ir]),single_peak_time_s=float(t[apindex[z][ir]]),weight_this_zeta=float(ap[z][ir]/U[z]),fixed_5pct_weight=float(ap[.05][ir]/U[.05]),fixed_5pct_rank=int(rank[ir]),top5_fixed_from_5pct=bool(rank[ir]<=5)))
   prat=Pp[.08]/Pp[.05];urat=U[.08]/U[.05];crat=C[.08]/C[.05];ident=prat-urat*crat;maxidentity=max(maxidentity,abs(ident))
   d=dict(Case=case,Story=story,U5_sum_single_mode_peaks_kN=U[.05],U8_sum_single_mode_peaks_kN=U[.08],P5_reference_peak_kN=Pp[.05],P8_reference_peak_kN=Pp[.08],C5_PoverU=C[.05],C8_PoverU=C[.08],U8_over_U5=urat,C8_over_C5=crat,P8_over_P5=prat,UPC_ratio_identity_error=ident,reference_peak_decrease_percent=100*(1-prat),native_peak5_kN=Pn[.05],native_peak8_kN=Pn[.08],native_peak_decrease_percent=100*(1-Pn[.08]/Pn[.05]),reference_minus_native_decrease_percentage_points=100*(Pn[.08]/Pn[.05]-prat),predicted5_peak_s=float(t[ip[.05]]),predicted8_peak_s=float(t[ip[.08]]),native5_peak_s=float(t[ni[.05]]),native8_peak_s=float(t[ni[.08]]),top5_modes_fixed5=';'.join(str(i+1) for i in top),scope='elastic inertia reference UPC, not native FNA unique modal decomposition');pairs.append(d)
   dominance.append(dict(Case=case,Story=story,top5_modes_fixed5=d['top5_modes_fixed5'],top5_sum_5pct_envelope_weights=float(sum(ap[.05][top])/U[.05]),top5_sum_8pct_own_envelope_weights=float(sum(ap[.08][top])/U[.08]),remaining295_sum_5pct_envelope_weights=float(sum(ap[.05][remaining])/U[.05]),remaining295_sum_8pct_own_envelope_weights=float(sum(ap[.08][remaining])/U[.08]),scope='independent single-mode envelope weights, not same-time force shares'))
   anchoridx=[('predicted_peak_5pct',ip[.05]),('predicted_peak_8pct',ip[.08]),('native_abspeak_5pct',ni[.05]),('native_abspeak_8pct',ni[.08])]
   for label,it in anchoridx:
    for z in [.05,.08]:
     vv=terms[z][it];total=float(sums[z][it]);rest=float(vv[remaining].sum());ad=dict(Case=case,Story=story,zeta=z,anchor=label,time_s=float(t[it]),reference_sum_signed_kN=total,native_signed_value_kN=float(native[z][it]),native_abs_value_kN=float(abs(native[z][it])),top5_signed_sum_kN=float(vv[top].sum()),remaining295_signed_sum_kN=rest)
     for k,ir in enumerate(top,1):ad[f'fixed5_rank{k}_Mode']=int(ir+1);ad[f'fixed5_rank{k}_signed_ref_kN']=float(vv[ir])
     for name,start,end in groups:ad[name+'_signed_ref_sum_kN']=float(vv[start:end].sum())
     maxclosure=max(maxclosure,abs(ad['top5_signed_sum_kN']+rest-total));maxgroup=max(maxgroup,abs(sum(ad[n+'_signed_ref_sum_kN'] for n,_,_ in groups)-total));ad['scope']='all signed terms are prediction positive; native eta unverified';anchors.append(ad)
  for z,rr in allmoderows.items():
   fn=f'mode-envelopes-{case}-z{z:g}-3600.csv';cs(fn,rr);modefiles.append(dict(name=fn,rows=len(rr),bytes=(O/fn).stat().st_size))
cs('all12-threewaves-UPC-paired-36.csv',pairs);cs('all12-fixed5-top5-envelope-summary-36.csv',dominance);cs('all12-four-anchors-both-zeta-signed-reference-288.csv',anchors);cs('Story5-Story12-UPC-priority-6.csv',[d for d in pairs if d['Story'] in ['Story5','Story12']]);cs('Story5-Story12-signed-reference-priority-48.csv',[d for d in anchors if d['Story'] in ['Story5','Story12']])
js('results.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),pairs=36,all_mode_envelope_rows=21600,per_state_files=modefiles,anchor_rows=288,priority_pair_rows=6,priority_anchor_rows=48,max_UPC_identity_error=maxidentity,max_top5_plus_remaining_closure_kN=maxclosure,max_fixed_groups_closure_kN=maxgroup,max_reference_peak_difference_vs_R004_kN=maxoldP,source_hashes_unchanged=all(sha(p)==b['sha256'] for p,b in zip(sources,bindings)),groups_fixed_before_data=['1-3','4-9','10-13','14-300'],all_arrays_stay_in_R004_local_cache=True,no_new_ODE_fit_or_CM_recheck=True))
print(json.dumps(dict(pairs=36,max_UPC_identity_error=maxidentity,max_top5_remaining_closure=maxclosure,max_groups_closure=maxgroup,priority=[d for d in pairs if d['Story'] in ['Story5','Story12']],per_state_files=modefiles),ensure_ascii=False,indent=2))
