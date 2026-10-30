from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R002'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=[P/'models-small-N36.json',P/'fixed-output-coefficients-N36-144.csv',P/'local-cache/N36-elastic-two-rcond-traces.npz',P/'delivery-manifest.json']
bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in src]
manifest=json.loads(src[3].read_text(encoding='utf-8'))
assert bindings[2]['sha256']==manifest['local_only_array']['sha256']
for p,b in zip(src[:2],bindings[:2]): assert next(d['sha256'] for d in manifest['files'] if d['name']==p.name)==b['sha256']
variant='N36_elastic_rc1e-10';model=json.loads(src[0].read_text(encoding='utf-8'))[variant];raw=np.array(model['raw_output_coef']);assert raw.shape==(36,2) and np.isfinite(raw).all() and np.all(raw!=0)
cr=list(csv.DictReader(src[1].open(encoding='utf-8-sig')));omega=[]
for ir in range(36):
    r=[d for d in cr if d['variant']==variant and int(d['Mode'])==ir+1];assert len(r)==2
    w={float(d['omega_rad_s']) for d in r};assert len(w)==1;omega.append(w.pop())
    for j,st in enumerate(['Story5','Story12']):assert float(next(d['raw_signed_output_coefficient'] for d in r if d['Story']==st))==raw[ir,j]
cases=['SHW3X','SHW4X','RH4X'];stories=['Story5','Story12'];rows=[];checks=[];worst_recover_abs=worst_recover_rel=worst_ratio=worst_shape=worst_scale=0.
pick=np.argmax(abs(raw),axis=1)
with np.load(src[2],allow_pickle=False) as a:
    required={f'{variant}__{c}__{s}__z{z:g}__{q}' for c in cases for s in stories for z in [.05,.08] for q in ['terms','t']}
    assert required.issubset(a.files)
    for case in cases:
        recovered={};story_metrics={};time=None;pairchecks=[]
        for z in [.05,.08]:
            terms=[];tt=None
            for j,s in enumerate(stories):
                tag=f'{variant}__{case}__{s}__z{z:g}__';term=a[tag+'terms'];t=a[tag+'t']
                assert term.shape==(len(t),36) and np.isfinite(term).all() and np.isfinite(t).all()
                if tt is not None:assert np.array_equal(tt,t)
                tt=t.copy();terms.append(term.copy())
            if time is not None:assert np.array_equal(tt,time)
            time=tt;assert np.allclose(np.diff(time),.02,atol=1e-9,rtol=0)
            g0=terms[0]/raw[:,0];g1=terms[1]/raw[:,1]
            err=np.max(abs(g0-g1),axis=0);den=np.maximum(np.max(abs(g0),axis=0),np.max(abs(g1),axis=0));rel=err/np.maximum(den,1e-300)
            assert float(rel.max())<1e-12
            worst_recover_abs=max(worst_recover_abs,float(err.max()));worst_recover_rel=max(worst_recover_rel,float(rel.max()))
            recovered[z]=np.where(pick[None,:]==0,g0,g1)
            for ir in range(36):checks.append(dict(Case=case,Mode=ir+1,zeta=z,two_story_max_abs_error_m_s2=float(err[ir]),two_story_relative_Linf_error=float(rel[ir])))
            story_metrics[z]=terms
        g5=recovered[.05];g8=recovered[.08]
        A5=np.max(abs(g5),axis=0);A8=np.max(abs(g8),axis=0);assert np.all(A5>0) and np.all(A8>0)
        rat=A8/A5;sh=np.linalg.norm(g8/A8-g5/A5,axis=0)/np.linalg.norm(g5/A5,axis=0)
        for j in range(2):
            v5=story_metrics[.05][j];v8=story_metrics[.08][j];B5=np.max(abs(v5),axis=0);B8=np.max(abs(v8),axis=0)
            rat2=B8/B5;sh2=np.linalg.norm(v8/B8-v5/B5,axis=0)/np.linalg.norm(v5/B5,axis=0)
            worst_ratio=max(worst_ratio,float(np.max(abs(rat-rat2))));worst_shape=max(worst_shape,float(np.max(abs(sh-sh2))))
        h5=-3.7*g5;h8=-3.7*g8;C5=np.max(abs(h5),axis=0);C8=np.max(abs(h8),axis=0)
        worst_scale=max(worst_scale,float(np.max(abs(C8/C5-rat))),float(np.max(abs(np.linalg.norm(h8/C8-h5/C5,axis=0)/np.linalg.norm(h5/C5,axis=0)-sh))))
        for ir in range(36):
            i=int(np.argmax(abs(g5[:,ir])));j=int(np.argmax(abs(g8[:,ir])));cc=[d for d in checks if d['Case']==case and d['Mode']==ir+1]
            rows.append(dict(Case=case,Mode=ir+1,omega_rad_s=omega[ir],period_s=2*math.pi/omega[ir],recovery_source=stories[int(pick[ir])],A5_g_m_s2=float(A5[ir]),A8_g_m_s2=float(A8[ir]),A8_over_A5=float(rat[ir]),peak_amplitude_decrease_percent=float(100*(1-rat[ir])),A8_greater_A5=bool(rat[ir]>1),peak5_time_s=float(time[i]),peak8_time_s=float(time[j]),peak_time_shift_s=float(time[j]-time[i]),g5_at_own_abspeak_m_s2=float(g5[i,ir]),g8_at_own_abspeak_m_s2=float(g8[j,ir]),normalized_waveform_relative_L2=float(sh[ir]),two_story_recovery_max_abs_error_m_s2=max(d['two_story_max_abs_error_m_s2'] for d in cc),two_story_recovery_relative_Linf=max(d['two_story_relative_Linf_error'] for d in cc),samples=len(time),kernel='g=omega^2*q_unitGamma; not floor shear contribution'))
def csvout(n,rr):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
csvout('modal-unit-kernel-change-108.csv',rows)
csvout('two-story-kernel-recovery-checks-216.csv',checks)
spread=[]
for ir in range(36):
    rr=[d for d in rows if d['Mode']==ir+1];mx=max(rr,key=lambda d:d['A8_over_A5']);mn=min(rr,key=lambda d:d['A8_over_A5'])
    spread.append(dict(Mode=ir+1,omega_rad_s=omega[ir],period_s=2*math.pi/omega[ir],min_ratio=mn['A8_over_A5'],min_ratio_case=mn['Case'],max_ratio=mx['A8_over_A5'],max_ratio_case=mx['Case'],ratio_range=mx['A8_over_A5']-mn['A8_over_A5']))
csvout('across-wave-amplitude-ratio-range-36.csv',spread)
compact=lambda d:{k:d[k] for k in ['Case','Mode','A8_over_A5','peak_amplitude_decrease_percent','peak5_time_s','peak8_time_s','normalized_waveform_relative_L2']}
summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),rows=108,recovery_checks=216,all_input_bindings=bindings,cache_keys_confirmed=True,all_two_layer_coefficients_nonzero=True,minimum_absolute_raw_coef=float(np.min(abs(raw))),recovery_choice_counts={s:int(sum(pick==j)) for j,s in enumerate(stories)},max_two_story_recovery_abs_error_m_s2=worst_recover_abs,max_two_story_recovery_relative_Linf=worst_recover_rel,max_invariant_ratio_error_from_independent_story_terms=worst_ratio,max_invariant_shape_error_from_independent_story_terms=worst_shape,max_negative_rescale_invariance_error=worst_scale,first3=[compact(d) for d in rows if d['Mode']<=3],max_attenuation_top5=[compact(d) for d in sorted(rows,key=lambda d:d['A8_over_A5'])[:5]],max_amplitude_ratio_top5=[compact(d) for d in sorted(rows,key=lambda d:d['A8_over_A5'],reverse=True)[:5]],largest_across_wave_ratio_range_top5=sorted(spread,key=lambda d:d['ratio_range'],reverse=True)[:5],counterincrease_rows=[compact(d) for d in rows if d['A8_greater_A5']],counterincrease_count=sum(d['A8_greater_A5'] for d in rows),sources_unchanged=all(sha(p)==b['sha256'] for p,b in zip(src,bindings)),no_ODE_or_fit=True,no_full_kernel_arrays_output=True)
assert summary['sources_unchanged'] and worst_ratio<1e-12 and worst_shape<1e-12 and worst_scale<1e-12
(O/'results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='all_input_bindings'},ensure_ascii=False,indent=2))
