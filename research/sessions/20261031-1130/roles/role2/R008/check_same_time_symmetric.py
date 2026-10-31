import os
os.environ['OPENBLAS_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,csv,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SRC=S/'roles/role4/R008'
START=datetime.fromisoformat('2026-10-31T12:45:37+08:00');DEADLINE=START+timedelta(minutes=12)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R008 deadline')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def table(n,x):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(x[0]),lineterminator='\n');wr.writeheader();wr.writerows(x)
def decompose(a5,a8,v5,v8):
    pos=(a5>0)&(a8>0);both=(a5==0)&(a8==0);one=~(pos|both)
    da=np.zeros_like(v5);dh=np.zeros_like(v5);d0=np.zeros_like(v5)
    h5=v5[pos]/a5[pos];h8=v8[pos]/a8[pos]
    da[pos]=(a8[pos]-a5[pos])*(h8+h5)/2
    dh[pos]=(a8[pos]+a5[pos])*(h8-h5)/2
    d0[one]=(v8-v5)[one]
    return da,dh,d0,both,one
gate();mf=json.loads((SRC/'delivery-manifest.json').read_text(encoding='utf-8'))
for e in mf['outputs']+mf['inputs']:
    p=Path(e['path']) if 'path' in e else SRC/e['name'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
theory=S/'roles/role1/R006/manifest.json';tm=json.loads(theory.read_text(encoding='utf-8'))
for e in tm['files']:
    p=Path(e['path']);assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
tot=rows(SRC/'all12-threewaves-two-native-anchors-symmetric-change-72.csv');tlookup={(x['Case'],x['Story'],x['anchor']):x for x in tot}
components=rows(SRC/'fixed5-and-remaining295-symmetric-components-432.csv');clookup={(x['Case'],x['Story'],x['anchor'],x['component']):x for x in components}
ind=[];comp=[];inderr={};indchecks=0
def compare_selected(x,ref):
    global indchecks
    if 'Mode' in x:
        assert (ref['Mode']=='' and x['Mode'] is None) or (x['Mode'] is not None and int(ref['Mode'])==x['Mode'])
    for k,v in x.items():
        if k not in ref or k in ('Case','Story','anchor','component','Mode'):continue
        if isinstance(v,bool):assert str(v)==ref[k];continue
        if isinstance(v,str):assert v==ref[k];continue
        if v is None:assert ref[k]=='';continue
        e=abs(float(v)-float(ref[k]));inderr[k]=max(inderr.get(k,0.),e);assert e<1e-8*max(1,abs(float(ref[k]))),(k,e);indchecks+=1
for case in ('SHW3X','SHW4X','RH4X'):
    gate();q={};native={};y={};amp={}
    for zeta in (.05,.08):
        e=next(e for e in mf['inputs'] if 'factorized-reference.npz' in e['path'] and ('actual300-'+case+'-z'+str(zeta)+'-') in e['path'])
        with np.load(e['path'],allow_pickle=False) as z:
            if zeta==.05:t=z['t'].copy();w=z['omega'].copy();B=z['B_direct'][[4,11]].copy()
            else:assert np.array_equal(t,z['t']) and np.array_equal(w,z['omega']) and np.array_equal(B,z['B_direct'][[4,11]])
            q[zeta]=z['s_unitGamma'];native[zeta]=[z['shear_native_'+st+'_kN'].copy() for st in ('Story5','Story12')]
            y[zeta]=(q[zeta]*w**2)@B.T/1000
            amp[zeta]=np.max(abs(q[zeta]),axis=0)[None,:]*abs(B)*w**2/1000
    for j,story in enumerate(('Story5','Story12')):
        top=np.lexsort((np.arange(1,301),-amp[.05][j]))[:5];names=['fixed5_rank'+str(k+1) for k in range(5)]+['remaining295']
        p5=float(max(abs(y[.05][:,j])));p8=float(max(abs(y[.08][:,j])))
        for anchor,zref in [('native5_abspeak',.05),('native8_abspeak',.08)]:
            i=int(np.argmax(abs(native[zref][j])));v5=q[.05][i]*w**2*B[j]/1000;v8=q[.08][i]*w**2*B[j]/1000
            da,dh,d0,both,one=decompose(amp[.05][j],amp[.08][j],v5,v8)
            y5=float(sum(v5));y8=float(sum(v8));sigma=int(np.sign(y5));assert sigma!=0
            a=float(sum(da));hh=float(sum(dh));un=float(sum(d0));wo=sigma*(y5-y8);flip=2*max(0.,-sigma*y8);absolute=abs(y5)-abs(y8);loss5=p5-abs(y5);loss8=p8-abs(y8)
            assert abs((a+hh+un)-(y8-y5))<1e-8 and abs(absolute-(wo-flip))<1e-8 and abs((p5-p8)-(absolute+loss5-loss8))<1e-8
            x={'Case':case,'Story':story,'anchor':anchor,'time_s':float(t[i]),'y5_ref_signed_kN':y5,'y8_ref_signed_kN':y8,'delta_y_ref_signed_kN':y8-y5,'amplitude_change_sum_kN':a,'normalized_waveform_change_sum_kN':hh,'zero_amplitude_unallocated_delta_sum_kN':un,'closure_delta_minus_terms_kN':y8-y5-a-hh-un,'sigma5_reference':sigma,'old_direction_amplitude_weakening_kN':-sigma*a,'old_direction_waveform_weakening_kN':-sigma*hh,'old_direction_unallocated_weakening_kN':-sigma*un,'old_direction_total_weakening_kN':wo,'reference_absolute_weakening_kN':absolute,'state_totals_opposite_sign':y5*y8<0,'old_direction_is_absolute_weakening':sigma*y8>=0,'both_zero_amplitude_modes':int(sum(both)),'one_zero_amplitude_modes':int(sum(one)),'top5_fixed5_modes':';'.join(str(k+1) for k in top),'native5_absolute_at_same_time_kN':float(abs(native[.05][j][i])),'native8_absolute_at_same_time_kN':float(abs(native[.08][j][i])),'sign_reversal_correction_kN':flip,'reference_peak5_minus_peak8_kN':p5-p8,'reference5_anchor_loss_kN':loss5,'reference8_anchor_loss_kN':loss8,'peak_anchor_loss_identity_error_kN':p5-p8-absolute-loss5+loss8}
            compare_selected(x,tlookup[case,story,anchor]);ind.append(x)
            for k,name in enumerate(names):
                mask=np.zeros(300,dtype=bool)
                if k<5:mask[top[k]]=True
                else:mask[:]=True;mask[top]=False
                vv5=float(sum(v5[mask]));vv8=float(sum(v8[mask]));aa=float(sum(da[mask]));hhr=float(sum(dh[mask]));uu=float(sum(d0[mask]))
                c={'Case':case,'Story':story,'anchor':anchor,'time_s':float(t[i]),'component':name,'Mode':int(top[k]+1) if k<5 else None,'mode_count':int(sum(mask)),'v5_signed_ref_kN':vv5,'v8_signed_ref_kN':vv8,'delta_v_signed_ref_kN':vv8-vv5,'amplitude_change_term_kN':aa,'normalized_waveform_change_term_kN':hhr,'unallocated_zero_amplitude_delta_kN':uu,'sigma5_all300':sigma,'old_direction_amplitude_weakening_kN':-sigma*aa,'old_direction_waveform_weakening_kN':-sigma*hhr,'old_direction_unallocated_weakening_kN':-sigma*uu}
                compare_selected(c,clookup[case,story,anchor,name]);comp.append(c)
table('independent-priority-symmetric-anchors-12.csv',ind);table('independent-priority-top5-rest-components-72.csv',comp)
save('selected-checks.json',{'completed':now().isoformat(),'anchor_rows':12,'component_rows':72,'numeric_checks':indchecks,'max_abs_differences':inderr,'must_count':0,'scope':'A recomputed from frozen factor s and B, then per-mode symmetric split before grouping; not group-waveform renormalization'})
# Other points are audited from frozen scalar primitives, not newly produced states.
mode_sums={};group_sums={};seen={};numeric=0;maxerr=0.;zero_both=0;zero_one=0
def ck(a,b):
    global numeric,maxerr
    e=abs(float(a)-float(b));maxerr=max(maxerr,e);assert e<1e-8*max(1,abs(float(b))),(a,b,e);numeric+=1
for e in mf['outputs']:
    name=e['name']
    if not name.endswith('-mode-change-1800.csv'):continue
    gate();case,anchor=name.split('-')[:2]
    for x in rows(SRC/name):
        key=(case,x['Story'],anchor);mode=int(x['Mode']);assert mode not in seen.setdefault(key,set());seen[key].add(mode)
        A5=float(x['A5_kN']);A8=float(x['A8_kN']);v5=float(x['v5_kN']);v8=float(x['v8_kN'])
        if A5>0 and A8>0:assert x['amplitude_status']=='positive_both'
        da,dh,d0,both,one=decompose(np.array([A5]),np.array([A8]),np.array([v5]),np.array([v8]));a=float(da[0]);hh=float(dh[0]);u=float(d0[0])
        ck(float(x['delta_v_kN']),v8-v5);ck(float(x['amplitude_change_kN']),a);ck(float(x['normalized_waveform_change_kN']),hh);ck(float(x['unallocated_delta_kN']),u);ck(v8-v5,a+hh+u)
        if A5>0:ck(float(x['h5']),v5/A5)
        else:assert x['h5']==''
        if A8>0:ck(float(x['h8']),v8/A8)
        else:assert x['h8']==''
        zero_both+=bool(both[0]);zero_one+=bool(one[0]);top=[int(v) for v in tlookup[key]['top5_fixed5_modes'].split(';')]
        assert (x['top5_fixed5']=='True')==(mode in top)
        label='fixed5_rank'+str(top.index(mode)+1) if mode in top else 'remaining295'
        vals=np.array([v5,v8,v8-v5,a,hh,u]);mode_sums.setdefault(key,np.zeros(6));mode_sums[key]+=vals
        gkey=(*key,label);group_sums.setdefault(gkey,[np.zeros(6),0]);group_sums[gkey][0]+=vals;group_sums[gkey][1]+=1
assert len(seen)==72 and all(len(v)==300 for v in seen.values()) and len(group_sums)==432
group_audit=[];anchor_audit=[];flips=0;sigzero=0;wave_negative=0
for key,(v,n) in group_sums.items():
    ref=clookup[key];sigma=int(ref['sigma5_all300']);assert n==int(ref['mode_count'])
    for j,k in enumerate(['v5_signed_ref_kN','v8_signed_ref_kN','delta_v_signed_ref_kN','amplitude_change_term_kN','normalized_waveform_change_term_kN','unallocated_zero_amplitude_delta_kN']):ck(v[j],float(ref[k]))
    for j,k in [(3,'old_direction_amplitude_weakening_kN'),(4,'old_direction_waveform_weakening_kN'),(5,'old_direction_unallocated_weakening_kN')]:ck(-sigma*v[j],float(ref[k]))
    group_audit.append({'Case':key[0],'Story':key[1],'anchor':key[2],'component':key[3],'mode_count':n,'formula_group_sum_pass':True})
upc={(x['Case'],x['Story']):x for x in rows(S/'roles/role4/R005/all12-threewaves-UPC-paired-36.csv')}
for key,v in mode_sums.items():
    ref=tlookup[key];sigma=int(np.sign(v[0]));assert sigma==int(ref['sigma5_reference']);sigzero+=sigma==0;flips+=v[0]*v[1]<0
    for j,k in enumerate(['y5_ref_signed_kN','y8_ref_signed_kN','delta_y_ref_signed_kN','amplitude_change_sum_kN','normalized_waveform_change_sum_kN','zero_amplitude_unallocated_delta_sum_kN']):ck(v[j],float(ref[k]))
    for j,k in [(3,'old_direction_amplitude_weakening_kN'),(4,'old_direction_waveform_weakening_kN'),(5,'old_direction_unallocated_weakening_kN')]:ck(-sigma*v[j],float(ref[k]))
    wo=sigma*(v[0]-v[1]);correct=2*max(0.,-sigma*v[1]);absweak=abs(v[0])-abs(v[1]);ck(wo,float(ref['old_direction_total_weakening_kN']));ck(absweak,float(ref['reference_absolute_weakening_kN']));ck(absweak,wo-correct)
    p5=float(upc[key[0],key[1]]['P5_reference_peak_kN']);p8=float(upc[key[0],key[1]]['P8_reference_peak_kN']);l5=p5-abs(v[0]);l8=p8-abs(v[1]);assert l5>=-1e-8 and l8>=-1e-8;ck(p5-p8,absweak+l5-l8)
    assert ref['state_totals_opposite_sign']==str(v[0]*v[1]<0) and ref['old_direction_is_absolute_weakening']==str(sigma!=0 and sigma*v[1]>=0)
    wave_negative+=(-sigma*v[4])<0
    anchor_audit.append({'Case':key[0],'Story':key[1],'anchor':key[2],'sigma5':sigma,'old_direction_W_kN':wo,'sign_reversal_correction_kN':correct,'absolute_weakening_kN':absweak,'anchor_loss5_kN':l5,'anchor_loss8_kN':l8,'same_time_and_peak_loss_formula_pass':True})
table('all72-anchor-formula-audit.csv',anchor_audit);table('all432-component-group-audit.csv',group_audit)
# Fixed scalar checks cover branches absent from the current all-positive-amplitude sample.
a,h,u,b,o=decompose(np.array([0.,0.]),np.array([0.,2.]),np.array([0.,0.]),np.array([0.,1.]));assert np.array_equal(a,[0.,0.]) and np.array_equal(h,[0.,0.]) and np.array_equal(u,[0.,1.])
assert (2-(-3))-2*max(0.,-1*(-3))==abs(2)-abs(-3)==-1
flips=int(flips);sigzero=int(sigzero);wave_negative=int(wave_negative)
save('all-table-algebra-checks.json',{'completed':now().isoformat(),'mode_points':sum(len(v) for v in seen.values()),'anchors':72,'components':432,'scalar_formula_checks':numeric,'max_abs_formula_or_sum_error_kN':maxerr,'zero_amplitude_both_points':zero_both,'zero_amplitude_one_points':zero_one,'opposite_sum_sign_anchors':flips,'zero_old_sign_anchors':sigzero,'negative_projected_waveform_anchors':wave_negative,'fixed_scalar_zero_and_flip_policy_checks':True,'must_count':0,'scope':'all per-mode scalar identities and component sums; independent factorized state reconstruction only 12 priority anchors','foreign_code_imported':False,'new_ODE_or_physical_counterexample_scan':False})
print(json.dumps(json.loads((O/'selected-checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
print(json.dumps(json.loads((O/'all-table-algebra-checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
