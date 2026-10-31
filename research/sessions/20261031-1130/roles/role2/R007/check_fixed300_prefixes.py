import os
os.environ['OPENBLAS_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SRC=S/'roles/role4/R007'
START=datetime.fromisoformat('2026-10-31T12:36:14+08:00');DEADLINE=START+timedelta(minutes=12)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R007 deadline')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def table(n,x):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(x[0]),lineterminator='\n');wr.writeheader();wr.writerows(x)
gate();mf=json.loads((SRC/'delivery-manifest-v002.json').read_text(encoding='utf-8'))
for entry in mf['outputs']+mf['inputs']:
    p=Path(entry['path']) if 'path' in entry else SRC/entry['name'];assert p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256']
mp=Path(next(e['path'] for e in mf['inputs'] if e['path'].endswith('controlled_small_tables.json')))
d=json.loads(mp.read_text(encoding='utf-8'))['Modal Participating Mass Ratios'];h=d[1][1]
raw={int(x[h.index('Mode')]):x for _,x in d[3:] if x[h.index('Case')]=='Modal'};mu=np.array([float(raw[i][h.index('UX')]) for i in range(1,301)]);cum=np.cumsum(mu)
assert max(abs(cum-np.array([float(raw[i][h.index('SumUX')]) for i in range(1,301)])))<2e-14
Ns=[int(np.flatnonzero(cum>=threshold)[0])+1 for threshold in (.9,.95,.99)]
assert Ns==[10,10,173];unique=sorted(set(Ns+[13,18,300]));assert unique==[10,13,18,173,300]
table('independent-native-mass-cumulative-300.csv',[{'Mode':i+1,'mu_UX':float(mu[i]),'cumulative_native_UX':float(cum[i])} for i in range(300)])
save('independent-N-selection.json',{'completed':now().isoformat(),'thresholds':[.9,.95,.99],'first_crossings':Ns,'unique_Ns':unique,'cumulative_at_N':{str(i):float(cum[i-1]) for i in unique},'native_ratios_not_renormalized_to_300':True})
state_target={(x['Case'],float(x['zeta']),x['Story']):x for x in rows(SRC/'N10-all12-threewaves-twozeta-convergence-72.csv')};states=[]
for case in ('SHW3X','SHW4X','RH4X'):
    for zeta in (.05,.08):
        gate();e=next(e for e in mf['inputs'] if 'factorized-reference.npz' in e['path'] and ('actual300-'+case+'-z'+str(zeta)+'-') in e['path'])
        with np.load(e['path'],allow_pickle=False) as z:
            t=z['t'];s=z['s_unitGamma'];w=z['omega'];b=z['B_direct'][[4,11]]
            g=s*w**2;full=g@b.T/1000;prefix=g[:,:10]@b[:,:10].T/1000
            amps=np.max(abs(g),axis=0)[None,:]*abs(b)/1000
            for j,story in enumerate(('Story5','Story12')):
                y=prefix[:,j];f=full[:,j];native=z['shear_native_'+story+'_kN'];p=float(max(abs(y)));pfull=float(max(abs(f)));pnative=float(max(abs(native)))
                ip=int(np.argmax(abs(y)));iff=int(np.argmax(abs(f)));inn=int(np.argmax(abs(native)))
                un=float(sum(amps[j,:10]));uall=float(sum(amps[j]));tail=float(sum(amps[j,10:]));err=float(max(abs(y-f)))
                assert err<=tail+1e-8
                scale=tail/(p-tail) if p>tail else None
                x={'N':10,'native_UX_cumulative_mass_ratio':float(cum[9]),'Case':case,'zeta':zeta,'Story':story,'signed_NRMSE_vs_full300_reference':float(np.linalg.norm(y-f)/np.linalg.norm(f)),'peakN_kN':p,'peak300_kN':pfull,'peakN_over_peak300_minus1':p/pfull-1,'absolute_peak_difference_vs_full300_kN':abs(p-pfull),'peakN_time_s':float(t[ip]),'peak300_time_s':float(t[iff]),'peak_time_shift_Nminus300_s':float(t[ip]-t[iff]),'U_N_kN':un,'U300_kN':uall,'U_N_over_U300':un/uall,'tail_independent_peak_sum_T_kN':tail,'max_abs_curve_Nminus300_kN':err,'relative_peak_scale_full300_only':scale,'relative_peak_scale_status':'defined' if scale is not None else 'undefined_PN_le_T','peakN_native_absolute_curve_NRMSE':float(np.linalg.norm(abs(y)-abs(native))/np.linalg.norm(native)),'native_peak_kN':pnative,'peakN_over_native_peak_minus1':p/pnative-1,'native_peak_time_s':float(t[inn]),'native_signed_at_Npeak_kN':float(native[ip]),'prediction_signed_at_native_peak_kN':float(y[inn])}
                states.append(x)
table('independent-N10-priority-states-12.csv',states)
errors={};checks=0
for x in states:
    ref=state_target[x['Case'],x['zeta'],x['Story']]
    for k,v in x.items():
        if k in ('N','Case','zeta','Story'):continue
        if isinstance(v,str):assert v==ref[k];continue
        if v is None:assert ref[k]=='';continue
        er=abs(v-float(ref[k]));errors[k]=max(errors.get(k,0.),er);assert er<1e-8*max(1,abs(float(ref[k]))),(k,x,er);checks+=1
paired=[]
for case in ('SHW3X','SHW4X','RH4X'):
    for story in ('Story5','Story12'):
        a=next(x for x in states if x['Case']==case and x['Story']==story and x['zeta']==.05);b=next(x for x in states if x['Case']==case and x['Story']==story and x['zeta']==.08)
        pn=a['peakN_kN'];p8=b['peakN_kN'];t5=a['tail_independent_peak_sum_T_kN'];t8=b['tail_independent_peak_sum_T_kN'];defined=pn>t5
        lo=max(0,p8-t8)/(pn+t5) if defined else None;hi=(p8+t8)/(pn-t5) if defined else None
        ratio=p8/pn;rfull=b['peak300_kN']/a['peak300_kN'];rn=b['native_peak_kN']/a['native_peak_kN']
        paired.append({'N':10,'Case':case,'Story':story,'prefix_peak_ratio_8over5':ratio,'full300_peak_ratio_8over5':rfull,'native_peak_ratio_8over5':rn,'prefix_peak_decrease_percent':100*(1-ratio),'full300_peak_decrease_percent':100*(1-rfull),'native_peak_decrease_percent':100*(1-rn),'prefix_minus_full300_decrease_percentage_points':100*(rfull-ratio),'prefix_minus_native_decrease_percentage_points':100*(rn-ratio),'ratio_interval_lower_full300_only':lo,'ratio_interval_upper_full300_only':hi,'interval_width':hi-lo if defined else None,'interval_status':'defined' if defined else 'undefined_PN5_le_T5'})
table('independent-N10-priority-pairs-6.csv',paired)
pt={(x['Case'],x['Story']):x for x in rows(SRC/'N10-all12-threewaves-peakratio-intervals-36.csv')}
for x in paired:
    ref=pt[x['Case'],x['Story']]
    for k,v in x.items():
        if k in ('N','Case','Story'):continue
        if isinstance(v,str):assert v==ref[k];continue
        if v is None:assert ref[k]=='';continue
        er=abs(v-float(ref[k]));errors[k]=max(errors.get(k,0.),er);assert er<1e-8*max(1,abs(float(ref[k])));checks+=1
save('selected-reconstruction-checks.json',{'completed':now().isoformat(),'N10_states':12,'N10_pairs':6,'numeric_checks':checks,'max_abs_differences':errors,'must_count':0,'worst_peak_error_selected':max(states,key=lambda x:abs(x['peakN_over_peak300_minus1'])),'worst_decrease_error_selected':max(paired,key=lambda x:abs(x['prefix_minus_full300_decrease_percentage_points'])),'fixed300_prefix_only':True,'new_ODE_or_Ritz_solve':False})
# Formula audit for all small-table rows, without claiming array validation outside the selected subset.
count=0;state_audit=[];pair_audit=[];undef_s=0;undef_p=0;maxgap=0
def close(a,b):
    global count
    assert abs(a-b)<1e-8*max(1,abs(b)),(a,b);count+=1
for n in unique:
    gate();sr=rows(SRC/f'N{n}-all12-threewaves-twozeta-convergence-72.csv');assert len(sr)==72
    lookup={(x['Case'],x['Story'],float(x['zeta'])):x for x in sr}
    for x in sr:
        p=float(x['peakN_kN']);pf=float(x['peak300_kN']);un=float(x['U_N_kN']);uf=float(x['U300_kN']);tail=float(x['tail_independent_peak_sum_T_kN']);delta=float(x['max_abs_curve_Nminus300_kN']);native=float(x['native_peak_kN'])
        close(float(x['native_UX_cumulative_mass_ratio']),float(cum[n-1]));close(float(x['peakN_over_peak300_minus1']),p/pf-1);close(float(x['absolute_peak_difference_vs_full300_kN']),abs(p-pf));close(float(x['peak_time_shift_Nminus300_s']),float(x['peakN_time_s'])-float(x['peak300_time_s']));close(float(x['U_N_over_U300']),un/uf);close(tail,uf-un);close(float(x['peakN_over_native_peak_minus1']),p/native-1)
        assert delta<=tail+1e-8 and x['curve_tail_inequality_pass']=='True';maxgap=max(maxgap,delta-tail)
        defined=p>tail
        if defined:assert x['relative_peak_scale_status']=='defined';close(float(x['relative_peak_scale_full300_only']),tail/(p-tail));assert abs(p/pf-1)<=tail/(p-tail)+1e-8
        else:assert x['relative_peak_scale_status']=='undefined_PN_le_T' and x['relative_peak_scale_full300_only']=='';undef_s+=1
        state_audit.append({'N':n,'Case':x['Case'],'zeta':x['zeta'],'Story':x['Story'],'tail_inequality_gap_kN':delta-tail,'relative_scale_defined':defined,'formula_pass':True})
    pr=rows(SRC/f'N{n}-all12-threewaves-peakratio-intervals-36.csv');assert len(pr)==36
    for x in pr:
        a=lookup[x['Case'],x['Story'],.05];b=lookup[x['Case'],x['Story'],.08];p5=float(a['peakN_kN']);p8=float(b['peakN_kN']);t5=float(a['tail_independent_peak_sum_T_kN']);t8=float(b['tail_independent_peak_sum_T_kN']);rp=p8/p5;rf=float(b['peak300_kN'])/float(a['peak300_kN']);rn=float(b['native_peak_kN'])/float(a['native_peak_kN'])
        for k,v in [('PN5_kN',p5),('PN8_kN',p8),('T5_kN',t5),('T8_kN',t8),('prefix_peak_ratio_8over5',rp),('full300_peak_ratio_8over5',rf),('native_peak_ratio_8over5',rn),('prefix_peak_decrease_percent',100*(1-rp)),('full300_peak_decrease_percent',100*(1-rf)),('native_peak_decrease_percent',100*(1-rn)),('prefix_minus_full300_decrease_percentage_points',100*(rf-rp)),('prefix_minus_native_decrease_percentage_points',100*(rn-rp))]:close(float(x[k]),v)
        defined=p5>t5
        if defined:
            lo=max(0,p8-t8)/(p5+t5);hi=(p8+t8)/(p5-t5)
            assert x['interval_status']=='defined' and x['full300_ratio_in_interval']=='True' and lo-1e-10<=rf<=hi+1e-10
            close(float(x['ratio_interval_lower_full300_only']),lo);close(float(x['ratio_interval_upper_full300_only']),hi);close(float(x['interval_width']),hi-lo)
        else:
            assert x['interval_status']=='undefined_PN5_le_T5' and all(x[k]=='' for k in ['ratio_interval_lower_full300_only','ratio_interval_upper_full300_only','interval_width','full300_ratio_in_interval']);undef_p+=1
        pair_audit.append({'N':n,'Case':x['Case'],'Story':x['Story'],'interval_defined':defined,'formula_pass':True})
table('all360-state-formula-audit.csv',state_audit);table('all180-pair-formula-audit.csv',pair_audit)
assert undef_s==5 and undef_p==2
save('all-table-formula-checks.json',{'completed':now().isoformat(),'state_rows':len(state_audit),'pair_rows':len(pair_audit),'scalar_formula_checks':count,'undefined_relative_scale_states':undef_s,'undefined_peakratio_pairs':undef_p,'max_raw_tail_gap_kN':maxgap,'must_count':0,'scope':'all small-table algebra and flags; independent prefix/output reconstruction only the 12 selected N10 states','bound_domain':'same fixed300 reference and stored time grid/window, not FE, infinite modes or new-N ETABS Ritz'})
print(json.dumps(json.loads((O/'selected-reconstruction-checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
print(json.dumps(json.loads((O/'all-table-formula-checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
