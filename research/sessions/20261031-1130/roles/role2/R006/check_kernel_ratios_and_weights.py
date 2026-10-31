from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';FWD=S/'roles/role4/R004';UPC=S/'roles/role4/R005'
START=datetime.fromisoformat('2026-10-31T12:28:28+08:00');DEADLINE=START+timedelta(minutes=10)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R006 deadline')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def table(n,x):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(x[0]),lineterminator='\n');w.writeheader();w.writerows(x)
gate();fm=json.loads((FWD/'delivery-manifest-v002.json').read_text(encoding='utf-8'));um=json.loads((UPC/'delivery-manifest.json').read_text(encoding='utf-8'))
for e in um['outputs']:
    p=UPC/e['name'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
theory=S/'roles/role1/R004/manifest.json';tm=json.loads(theory.read_text(encoding='utf-8'))
for e in tm['files']:
    p=Path(e['path']);assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
cases=('SHW3X','SHW4X','RH4X');modes=(2,10,13,18);idx=np.array(modes)-1
kernel=[];bycase={};selected_B={}
for case in cases:
    gate();amplitudes={};times={}
    for zeta in (.05,.08):
        e=next(x for x in fm['local_only_arrays'] if ('actual300-'+case+'-z'+str(zeta)+'-') in x['path']);p=Path(e['path'])
        assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
        with np.load(p,allow_pickle=False) as z:
            q=z['s_unitGamma'][:,idx];w=z['omega'][idx];t=z['t'];g=q*w**2
            amplitudes[zeta]=np.max(abs(g),axis=0);times[zeta]=t[np.argmax(abs(g),axis=0)]
            if zeta==.05:selected_B[case]=z['B_direct'][np.array([4,11])][:,idx]
            else:assert np.array_equal(selected_B[case],z['B_direct'][np.array([4,11])][:,idx])
    bycase[case]=amplitudes
    for j,mode in enumerate(modes):
        a5=float(amplitudes[.05][j]);a8=float(amplitudes[.08][j]);rho=a8/a5 if a5>0 else None
        kernel.append({'Case':case,'Mode':mode,'omega_rad_s':float(w[j]),'A5_unit_g_m_per_s2':a5,'A8_unit_g_m_per_s2':a8,'rho_A8_over_A5':rho,'peak_decrease_percent':100*(1-rho) if rho is not None else None,'peak5_s':float(times[.05][j]),'peak8_s':float(times[.08][j]),'zero_baseline_amplitude':a5==0})
table('actual-unit-kernel-ratios-12.csv',kernel)
priority=rows(UPC/'Story5-Story12-UPC-priority-6.csv');pr={(x['Case'],x['Story']):x for x in priority}
selected=[];topweights=[];partial=[];comparisons=0
for case in cases:
    # Read the existing scalar peak tables; do not recompute their 21600 peaks.
    source={}
    for zeta in (.05,.08):
        source[zeta]={(x['Story'],int(x['Mode'])):x for x in rows(UPC/f'mode-envelopes-{case}-z{zeta}-3600.csv') if x['Story'] in ('Story5','Story12')}
    for si,story in enumerate(('Story5','Story12')):
        row=pr[case,story];U5=float(row['U5_sum_single_mode_peaks_kN']);ru=float(row['U8_over_U5']);rc=float(row['C8_over_C5']);rp=float(row['P8_over_P5'])
        assert U5>0 and abs(ru*rc-rp)<1e-13
        sumw=0.;sumwr=0.;selected_drop=0.
        for j,mode in enumerate(modes):
            a=source[.05][story,mode];b=source[.08][story,mode];w5=float(a['fixed_5pct_weight']);rho=float(bycase[case][.08][j]/bycase[case][.05][j])
            a5=float(a['reference_mode_abs_peak_kN']);a8=float(b['reference_mode_abs_peak_kN'])
            expected5=abs(selected_B[case][si,j])*bycase[case][.05][j]/1000;expected8=abs(selected_B[case][si,j])*bycase[case][.08][j]/1000
            assert abs(a5-expected5)<1e-9*max(1,abs(a5)) and abs(a8-expected8)<1e-9*max(1,abs(a8))
            assert a5>0 and abs(a8/a5-rho)<1e-12 and abs(w5-a5/U5)<1e-13
            comparisons+=4;sumw+=w5;sumwr+=w5*rho;selected_drop+=w5*(1-rho)
            selected.append({'Case':case,'Story':story,'Mode':mode,'w5_independent_peak_budget':w5,'common_layer_rho_from_unit_kernel':rho,'w5_times_rho':w5*rho,'weighted_budget_decrease_percentage_points':100*w5*(1-rho),'existing_fixed5_rank':int(a['fixed_5pct_rank'])})
        for mode in [int(x) for x in row['top5_modes_fixed5'].split(';')]:
            x=source[.05][story,mode]
            assert x['top5_fixed_from_5pct']=='True'
            topweights.append({'Case':case,'Story':story,'Mode':mode,'fixed5_rank':int(x['fixed_5pct_rank']),'fixed5_envelope_weight':float(x['fixed_5pct_weight'])})
        partial.append({'Case':case,'Story':story,'selected_modes':'2;10;13;18','sum_selected_w5':sumw,'sum_selected_w5_rho':sumwr,'remaining296_w5':1-sumw,'remaining296_weighted_rho_budget':ru-sumwr,'selected_weighted_U_decrease_percentage_points':100*selected_drop,'remaining296_U_decrease_percentage_points':100*((1-ru)-selected_drop),'U8_over_U5':ru,'C8_over_C5':rc,'P8_over_P5':rp,'reference_peak_decrease_percent':100*(1-rp),'native_peak_decrease_percent':float(row['native_peak_decrease_percent'])})
table('selected-mode-envelope-weights-24.csv',selected);table('published-top5-weights-30.csv',topweights);table('priority-layer-budget-and-combination-6.csv',partial)
ordering={case:sorted([{'Mode':x['Mode'],'decrease_percent':x['peak_decrease_percent']} for x in kernel if x['Case']==case],key=lambda x:x['decrease_percent'],reverse=True) for case in cases}
save('checks.json',{'completed':now().isoformat(),'kernel_pairs':12,'kernel_modes':modes,'zero_A5_count':sum(x['zero_baseline_amplitude'] for x in kernel),'selected_layer_mode_pairs':24,'selected_scalar_checks':comparisons,'priority_layer_pairs':6,'must_count':0,'selected_decrease_order_by_wave':ordering,'identity_conditions':'U5>0 and every used A5>0, otherwise add sum_{A5=0}|B|A8/(1000 U5); do not divide by zero','beta_sign_invariance':'v and summed y multiplied by the same nonzero sign leaves v/y unchanged when y!=0; no native modal-force identity inferred','recomputed_all21600_peaks':False,'new_ODE_or_fit':False,'foreign_code_imported':False,'sources':{'forward_manifest_v002_sha256':sha(FWD/'delivery-manifest-v002.json'),'UPC_manifest_sha256':sha(UPC/'delivery-manifest.json'),'role1_manifest_sha256':sha(theory)}})
print(json.dumps({'completed':now().isoformat(),'kernel':kernel,'priority':partial,'ordering':ordering},ensure_ascii=False))
