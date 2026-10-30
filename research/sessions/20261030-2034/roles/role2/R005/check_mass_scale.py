from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,csv,hashlib,math
O=Path(__file__).parent; R=O.parents[5]; S=R/'research/sessions/20261030-2034'
START=datetime.fromisoformat('2026-10-30T21:30:29+08:00'); DEADLINE=START+timedelta(minutes=10)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R005 deadline')
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def csvout(n,rs):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gate();sources=[]
for rd in ('R002','R003'):
    d=S/'roles/role4'/rd;p=d/'delivery-manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
    for e in m['files']:
        gate();b=(d/e['name']).read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
    sources.append({'path':str(p),'sha256':sha(p),'frozen':m['frozen_Asia_Shanghai']})
mp=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016/native0_small_tables.json'
assert sha(mp)=='20815b312c71b0c4e8260573752faccbd922c40d84e28bc2549becfca880a972'
small=json.loads(mp.read_text(encoding='utf-8'));sources.append({'path':str(mp),'sha256':sha(mp)})
mt=small['Centers Of Mass And Rigidity']; h=mt[1][1]; unit=mt[2][1]
assert unit[h.index('Mass X')]=='kg'
massrows=[];storymass={i:0. for i in range(1,13)}
for sr,row in mt[3:]:
    st=int(row[h.index('Story')].removeprefix('Story'));m=float(row[h.index('Mass X')])
    storymass[st]+=m
    massrows.append({'source_excel_row':sr,'Story':'Story'+str(st),'Diaphragm':row[h.index('Diaphragm')],'MassX_kg':m,'MassX_tonnes':m/1000})
total=math.fsum(x['MassX_kg'] for x in massrows)
# Independently reconcile the bottom cumulative mass of each diaphragm, avoiding double counting cumulative rows.
cumulative=math.fsum(float(row[h.index('Cum Mass X')]) for _,row in mt[3:] if (row[h.index('Story')],row[h.index('Diaphragm')]) in [('Story1','D1'),('Story3','D2')])
assert math.isclose(total,cumulative,rel_tol=1e-14)
pt=small['Modal Participating Mass Ratios'];ph=pt[1][1]; modes={}
for sr,row in pt[3:]:
    k=int(row[ph.index('Mode')]);mu=float(row[ph.index('UX')])
    if k<=36:
        assert row[ph.index('Case')]=='Modal' and 0<=mu<=1
        modes[k]={'Mode':k,'source_excel_row':sr,'Period_s':float(row[ph.index('Period')]),'mu_UX':mu,'cumulative_mu_UX':float(row[ph.index('SumUX')]),'m_eff_using_table_mass_tonnes':mu*total/1000}
assert len(modes)==36
assert math.isclose(math.fsum(v['mu_UX'] for v in modes.values()),modes[36]['cumulative_mu_UX'],rel_tol=1e-12)
modelp=S/'roles/role4/R003/all12-models-small.json';model=json.loads(modelp.read_text(encoding='utf-8'))['N36'];a=model['raw_coef_all12'];stories=model['Story_order']
oldp=S/'roles/role4/R002/models-small-N36.json';old=json.loads(oldp.read_text(encoding='utf-8'))
for rc in ('N36_elastic_rc1e-10','N36_elastic_rc1e-08'):
    for k in range(36):
        for j,st in enumerate(('Story5','Story12')):assert a[k][stories.index(st)]==old[rc]['raw_output_coef'][k][j]
sources.extend({'path':str(p),'sha256':sha(p)} for p in (modelp,oldp))
csvout('mass-source-18.csv',massrows)
csvout('modal-mass-reference-36.csv',list(modes.values()))
sr=[]
for st in range(1,13):
    ms=math.fsum(storymass[i] for i in range(st,13))
    sr.append({'Story':'Story'+str(st),'local_mass_kg':storymass[st],'mass_at_and_above_kg':ms,'mass_at_and_above_tonnes':ms/1000,'table_total_mass_kg':total})
csvout('story-mass-reference-12.csv',sr)
cr=[]
for k in range(1,37):
    for j,story in enumerate(stories):
        gate();b=float(a[k-1][j]);ms=next(x['mass_at_and_above_tonnes'] for x in sr if x['Story']==story)
        ref=math.sqrt(ms*modes[k]['m_eff_using_table_mass_tonnes'])
        cr.append({'Story':story,'Mode':k,'group':'1to12' if k<=12 else '13to36','raw_output_coef_tonnes':b,'abs_coef_over_table_total_mass':abs(b)/(total/1000),'mu_UX':modes[k]['mu_UX'],'conditional_sqrt_Ms_meff_tonnes_NOT_certified_bound':ref,'coef_over_conditional_reference_NOT_proven_violation':abs(b)/ref if ref else None})
csvout('coefficient-mass-diagnostics-432.csv',cr)
worst=[]
for story in stories:
    ww=max((x for x in cr if x['Story']==story),key=lambda x:abs(x['raw_output_coef_tonnes']));worst.append(ww)
csvout('maximum-coefficient-per-story-12.csv',worst)
maxrow=max(cr,key=lambda x:abs(x['raw_output_coef_tonnes']))
save('input-freeze.json',{'started':START.isoformat(),'deadline':DEADLINE.isoformat(),'sources':sources,'no_fit':True,'no_large_array_read':True,'units':'kN/(m/s^2) = 1000 kg = tonne','mass_scope':'sum of native0 Centers Of Mass And Rigidity Mass X, not certified full M matrix','conditional_reference':'sqrt(M_s * (mu_UX * M_table)); not a certified bound for ETABS reported Bottom VX'})
save('results.json',{'completed':now().isoformat(),'table_total_MassX_kg':total,'table_total_MassX_tonnes':total/1000,'independent_cumulative_sum_kg':cumulative,'mass_rows':len(massrows),'modes':len(modes),'sum_mu_UX_36':math.fsum(v['mu_UX'] for v in modes.values()),'coefficient_cells':len(cr),'old_two_stories_exact_checks':144,'max_coefficient':maxrow,'low12_max_abs_coef_over_table_mass':max(x['abs_coef_over_table_total_mass'] for x in cr if x['Mode']<=12),'high24_max_abs_coef_over_table_mass':max(x['abs_coef_over_table_total_mass'] for x in cr if x['Mode']>12),'conditional_exceedance_counts_not_proven_physical_violations':{g:sum(x['coef_over_conditional_reference_NOT_proven_violation']>1 for x in cr if x['group']==g) for g in ('1to12','13to36')}})
print(json.dumps(json.loads((O/'results.json').read_text(encoding='utf-8')),ensure_ascii=False))
