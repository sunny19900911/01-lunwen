from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
O=Path(__file__).resolve().parent;R=O.parents[5];D=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016';S=R/'research/sessions'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def csvout(n,rr):
 with (O/n).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
meta=json.loads((O/'direct-small-table-inspection.json').read_text(encoding='utf-8'))
actual=Path(meta['actual_controlled']['path']);cmdir=S/'20261022-1856/roles/role4/R001';cmfile=cmdir/'local-cache/CM-signed-all300-5400.csv';massfile=S/'20261021-2157/roles/role4/R005/old-CM-mass-coordinate-new-mode-key-join-18.csv';original=Path('E:/!!!!!!!!TO HOME/20261021/模态的位移角.xlsx')
sources=[actual,cmfile,massfile,original,Path(meta['old_plus3']['path']),Path(meta['old_baseline5']['path'])]
bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
assert sha(original)=='aa593ff61d6e61d40535d177f52b068c23cd920adba9a76ba29676e67afc8f8a'
oldmanifest=json.loads((cmdir/'delivery-manifest.json').read_text(encoding='utf-8'))
assert sha(cmfile)==next(x['sha256'] for x in oldmanifest['files'] if x['name'].replace('\\','/')=='local-cache/CM-signed-all300-5400.csv' or x['name']=='CM-signed-all300-5400.csv')
cm=read(cmfile);mass=read(massfile);assert len(cm)==5400 and len(mass)==18
massmap={(d['Story'],d['Diaphragm']):d for d in mass};keys=set(massmap)
assert all({(d['Story'],d['Diaphragm']) for d in cm if int(d['Mode'])==m}==keys for m in range(1,301))
assert {d['CaseType'] for d in cm}=={'LinModRitz'} and {d['OutputCase'] for d in cm}=={'Modal'}
dd=json.loads(actual.read_text(encoding='utf-8-sig'))
def table(d,n):return {int(x[1][1]):dict(SourceRow=x[0],**dict(zip(d[n][1][1],x[1]))) for x in d[n][3:] if x[1][0]=='Modal'}
pf=table(dd,'Modal Participation Factors');rat=table(dd,'Modal Participating Mass Ratios');freq=table(dd,'Modal Periods And Frequencies')
tot={ax:sum(float(d['old_Mass'+ax+'_kg']) for d in mass) for ax in ['X','Y']}
checks=[];examples=[];norms=[]
for mode in range(1,301):
 mm=float(pf[mode]['ModalMass']);rshape=[d for d in cm if int(d['Mode'])==mode]
 for ax in ['X','Y']:
  s=sum(float(massmap[d['Story'],d['Diaphragm']]['old_Mass'+ax+'_kg'])*float(d['U'+ax+'_converted_m']) for d in rshape)
  factor=float(pf[mode]['U'+ax]);ratio=float(rat[mode]['U'+ax]);mu=ratio*tot[ax];mref=1000*mm;mu_from=s*s/mref
  rel=abs(mu_from/mu-1) if mu else None
  checks.append(dict(Mode=mode,Axis=ax,S_old18_mass_newCM_kg_m=s,actual_native_PF=factor,PF_native_unit='kN-m; raw value retained, not interpreted as Gamma or converted to S',actual_native_ModalMass=mm,ModalMass_native_unit='kN-m-s2',ModalMass_times1000_kg_m2=mref,effective_mass_conditional_ratio_times_oldtotal_kg=mu,effective_mass_oldmass_projection_over_actual_mref_kg=mu_from,conditional_effective_mass_relative_difference=rel,empirical_abs_S_over_abs_native_PF=abs(s/factor) if factor else None,actual_mass_ratio=ratio,old18_mass_total_kg=tot[ax],actual_PF_SourceRow=pf[mode]['SourceRow'],actual_ratio_SourceRow=rat[mode]['SourceRow'],status='cross-source conditional consistency; not same-source mass certification'))
  if mode in [2,10,13]:
   for cut in [1,5,12]:
    above=[d for d in rshape if int(d['Story'][5:])>=cut];ss=sum(float(massmap[d['Story'],d['Diaphragm']]['old_Mass'+ax+'_kg'])*float(d['U'+ax+'_converted_m']) for d in above);B=mu*ss/s if s else None
    examples.append(dict(Mode=mode,Axis=ax,cut_story='Story'+str(cut),selected_CMs=len(above),S_all_oldmass_CM_kg_m=s,S_above_oldmass_CM_kg_m=ss,conditional_effective_mass_ratio_times_oldtotal_kg=mu,B_candidate_kg=B,B_candidate_kN_per_m_s2=B/1000 if B is not None else None,actual_period_s=freq[mode]['Period'],actual_CaseType='LinModRitz',CM_SourceRows=';'.join(d['SourceRow'] for d in above),oldmass_SourceRows=';'.join(massmap[d['Story'],d['Diaphragm']]['old_mass_SourceRow'] for d in above),actual_PF_SourceRow=pf[mode]['SourceRow'],actual_ratio_SourceRow=rat[mode]['SourceRow'],same_source_mass_confirmed=False,classification='conditional inertia projection only; not true full-FE elastic story shear'))
csvout('cross-source-mass-projection-diagnostics-600.csv',checks)
csvout('conditional-mass-projection-examples-18.csv',examples)
selected=[d for d in cm if int(d['Mode']) in [2,10,13]];csvout('actual-CM-signed-selected2-10-13-54.csv',selected)
csvout('old-D-directional-mass-and-key-coverage-18.csv',mass)
periodcmp=[]
for label in ['actual_controlled','old_plus3','old_baseline5']:
 d=json.loads(Path(meta[label]['path']).read_text(encoding='utf-8-sig'));f=table(d,'Modal Periods And Frequencies');p=table(d,'Modal Participation Factors');rr=table(d,'Modal Participating Mass Ratios')
 for mode in [1,2,3,10,13,300]:periodcmp.append(dict(dataset=label,Mode=mode,Period_s=f[mode]['Period'],omega_rad_s=f[mode]['CircFreq'],PF_UX=p[mode]['UX'],PF_UY=p[mode]['UY'],mass_ratio_UX=rr[mode]['UX'],mass_ratio_UY=rr[mode]['UY'],PF_SourceRow=p[mode]['SourceRow'],period_SourceRow=f[mode]['SourceRow'],ratio_SourceRow=rr[mode]['SourceRow'],case_type_from_CM='LinModRitz' if label=='actual_controlled' else 'check response manifest; frequency table itself has no type field'))
csvout('modal-basis-identity-numeric-comparison-18.csv',periodcmp)
summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),source_bindings=bindings,original_modal_XLSX_reextracted=False,full_CM_cache_rows=5400,modes=300,diaphragms_per_mode=18,CaseType='LinModRitz',actual_CM_and_period_PF_basis_binding='human same unmodified model and same Modal confirmation; participation tables in same controlled_small_tables export',actual_mass_distribution_table_present=False,old_mass_total_kg=tot,max_conditional_effective_mass_relative_difference=max(d['conditional_effective_mass_relative_difference'] for d in checks),top_projection_defects=sorted(checks,key=lambda d:d['conditional_effective_mass_relative_difference'],reverse=True)[:5],selected_projection_checks=[d for d in checks if d['Mode'] in [2,10,13]],conditional_examples=examples,source_hashes_unchanged=all(sha(p)==b['sha256'] for p,b in zip(sources,bindings)))
(O/'results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in ['source_bindings','conditional_examples','selected_projection_checks']},ensure_ascii=False,indent=2))
