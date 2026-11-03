from pathlib import Path
import csv,json,hashlib,datetime
import numpy as np

H=Path(__file__).resolve().parent;R=H.parents[4];W=R.parent/'W5-重燃双塔连体';D=W/'02-数据/增阻尼多目标研究-20261016'
CASE=['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
sources=[]
def bind(p):
    sources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
    return p
base=load(bind(D/'native0_small_tables.json'));modal=load(bind(D/'small_tables.json'))
actual_path=W/'research/maxwell-20261017/roles/experiments/metadata/controlled_small_tables.json'
actual=load(bind(actual_path));inventory=load(bind(actual_path.with_name('metadata_inventory.json')))
invnames=[k for k in inventory['sheets'] if k!='Program Control']
missing=['Functions - TH - User Defined','Load Cases - TH - Nonlin Modal','Centers Of Mass And Rigidity']
assert all(k not in invnames for k in missing)

table='Load Cases - TH - Nonlin Modal';head=base[table][1][1]
assert head==modal[table][1][1]
validcols=[i for i,k in enumerate(head) if k not in ['GUID','Notes']]
def cases(model):return {rr[0]:dict(zip(head,rr)) for _,rr in model[table][3:]}
bcase=cases(base);mcase=cases(modal)
case_rows=[]
for c in CASE:
    a=bcase[c];b=mcase[c];assert all(a.get(head[j])==b.get(head[j]) for j in validcols)
    case_rows.append({k:a.get(k) for k in ['Name','Mass Source','Initial Condition','Load Type','Load Name','Function','Trans Accel SF','Time Factor','Arrival Time','Angle','Modal Case','Motion Type','Number Steps','Step Size','Max Substep','Min Substep']})
cm='Centers Of Mass And Rigidity'
assert base[cm]==modal[cm]
bh=base[cm][1][1];cmold={(rr[bh.index('Story')],rr[bh.index('Diaphragm')],axis):float(rr[bh.index('Mass '+axis)])for _,rr in base[cm][3:] for axis in ['X','Y']}
identified=R/'research/sessions/20261031-1130/roles/role4/R002/identified-versus-old-directional-masses-36.csv'
bind(identified);mr=list(csv.DictReader(identified.open(encoding='utf-8-sig')))
assert len(mr)==36
mass=[]
for rr in mr:
    k=(rr['Story'],rr['Diaphragm'],rr['Axis']);old=cmold[k];value=float(rr['identified_mass_kg'])
    mass.append({'Story':k[0],'Diaphragm':k[1],'Axis':k[2],'baseline_CM_mass_kg':old,'actual_CM_identified_mass_kg':value,'relative_difference':(value-old)/old})

folders={'baseline':D/'原生0数据缓存','actual':W/'research/maxwell-20261017/experiments/R001/core-cache'}
groups={};meta={};cache_before={}
for label,folder in folders.items():
    manifest=load(bind(folder/'manifest.json'));t=manifest['tables']['Story Accelerations'];p=folder/t['cache'];cache_before[label]=sha(bind(p));meta[label]=t
    selected={}
    with np.load(p,allow_pickle=False)as z:
        for key,info in t['groups'].items():
            keys=info['keys']
            if keys.get('Story')=='Base' and keys.get('Output Case')in CASE:
                selected[keys['Output Case']]=z[key]
                assert keys['Case Type']=='NonModHist'
    assert set(selected)==set(CASE);groups[label]=selected
assert meta['baseline']['columns']==meta['actual']['columns']
assert meta['baseline']['headers']==meta['actual']['headers']
assert meta['baseline']['units']==meta['actual']['units']
component_rows=[];time_rows=[]
for c in CASE:
    a=groups['baseline'][c];b=groups['actual'][c]
    assert a.shape==b.shape and np.array_equal(a[:,0],b[:,0])
    assert np.isfinite(a).all()and np.isfinite(b).all()and np.all(np.diff(a[:,0])>0)
    time_rows.append({'Case':c,'n':len(a),'t0_s':float(a[0,0]),'t1_s':float(a[-1,0]),'grid_exact':True,'baseline_first_source_row':int(a[0,-1]),'actual_first_source_row':int(b[0,-1])})
    for j,field in enumerate(meta['actual']['columns'][1:7],1):
        d=float(np.max(np.abs(a[:,j]-b[:,j])));assert d==0
        component_rows.append({'Case':c,'component':field,'n':len(a),'maximum_abs_difference':d,'all_samples_exact':True,'baseline_peak_abs':float(np.max(np.abs(a[:,j]))),'actual_peak_abs':float(np.max(np.abs(b[:,j])))})
for label,folder in folders.items():assert cache_before[label]==sha(folder/meta[label]['cache'])
for name,rows in [('base-sample-comparison-36.csv',component_rows),('common-case-settings-BM-6.csv',case_rows),('CM-directional-mass-comparison-36.csv',mass),('base-grid-comparison-6.csv',time_rows)]:
    with (H/name).open('x',encoding='utf-8',newline='')as f:
        cw=csv.DictWriter(f,fieldnames=list(rows[0]));cw.writeheader();cw.writerows(rows)

modal_period={}
for label,model in [('B',base),('M',modal),('D',actual)]:
    hh=model['Modal Periods And Frequencies'][1][1]
    pp={int(rr[hh.index('Mode')]):float(rr[hh.index('Period')])for _,rr in model['Modal Periods And Frequencies'][3:]}
    modal_period[label]=pp
common_modal={'first3_exact':all(modal_period['B'][i]==modal_period['D'][i] for i in range(1,4)),'max_abs_period_difference_BD_s':max(abs(modal_period['B'][i]-modal_period['D'][i])for i in range(1,301)),'periods_at_2_10_13':{k:{i:v[i]for i in [2,10,13]} for k,v in modal_period.items()}}
result={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'sources':sources,'actual_export_inventory_non_account_sheet_names':invnames,'actual_absent_export_tables':missing,'common_cases':CASE,'BM_case_settings_exact_excluding_GUID_notes':True,'BM_CM_table_exact':True,'actual_base_vs_baseline_components_exact':36,'actual_base_vs_baseline_rows':sum(x['n']for x in time_rows),'time_grids':time_rows,'max_relative_directional_CM_mass_difference':max(abs(r['relative_difference'])for r in mass),'mass_comparison_scope':'18 CM concentrated directional masses, inherited identification already independently reviewed; this run joins them to B/M CM table, not a new FE mass identification','modal_period_comparison':common_modal,'actual_case_type':'NonModHist from all six Base groups','actual_background_damping':'not exported in selected inventory; do not assert5% solely by default or model label','actual_scale_time_initial_solver_settings':'not exported; effective Base samples match at every saved time but internal interpolation/substep and initial-state settings are not thereby shown equal','verdict':'Allow reported scheme-to-baseline software peak reduction r_D=1-P_D/P_B on the six common saved-input cases, and compare both governing-input selectors within that identical six-case subset. This is a comparison of provided model states, not isolated causal effect of damping alone, not proof of equal per-mode damping, full M/K identity or unique QS.','new_reads':{'raw_workbooks':0,'response_ODE_or_fit':0,'Base_input_npz_groups':12,'full_node_arrays':0},'status':'frozen'}
(H/'pairing-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k]for k in ['actual_base_vs_baseline_components_exact','actual_base_vs_baseline_rows','max_relative_directional_CM_mass_difference','modal_period_comparison','verdict']},ensure_ascii=False))
