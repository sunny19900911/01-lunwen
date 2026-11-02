from pathlib import Path
from decimal import Decimal as D,getcontext
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,re,collections
getcontext().prec=40
O=Path(__file__).resolve().parent;S=O.parents[2];R=S/'roles/role4/R001';ROOT=O.parents[5]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
ind=json.loads((O/'independent-selections-before-comparison.json').read_text(encoding='utf-8'))
key=lambda a:(a['Case'],a['Story'],a['Axis'],a['Location'])
ii={key(a):a for a in ind['records']};gg={(g['Story'],g['Axis']):g for g in ind['selectors']}
counts=collections.Counter();maxdiff=collections.defaultdict(lambda:D(0));checked=[]
def ck(where,actual,want,kind='number',tol='1e-9'):
    counts[kind]+=1
    if kind=='text':assert str(actual)==str(want),(where,actual,want)
    else:
        delta=abs(D(str(actual))-D(str(want)));maxdiff[kind]=max(maxdiff[kind],delta)
        assert delta<=D(tol),(where,actual,want,delta)
    checked.append(where)
mf=[]
for name,items in [('delivery-manifest.json','files'),('delivery-manifest-v002.json','additive_files')]:
    p=R/name;m=json.loads(p.read_text(encoding='utf-8'))
    for a in m[items]:
        q=Path(a['path']);assert sha(q)==a['sha256'] and q.stat().st_size==a['bytes']
    mf.append({'path':str(p),'sha256':sha(p),'verified_files':len(m[items])})
assert mf[0]['sha256']=='7717f21e0cf552ff40d92931d46cd3756f2a3355f7fb25fb8b92c5d18103f535'
assert mf[1]['sha256']=='01f62c35f41baf966b98a320733548ea53a61d070ffdc6ad5d1aeaee20515935'
v1=rd(R/'engineering-review-by-story-direction-24.csv');v2=rd(R/'engineering-review-by-story-direction-24-v002.csv')
assert len(v1)==len(v2)==24
v2index={(x['Story'],x['Axis']):x for x in v2};assert set(v2index)==set(gg)
oldD=ROOT/'research/sessions/20261021-2020/roles/role4/R001-d-168.csv'
assert sha(oldD)=='a97a9995809af82858c274c87d1ff15164e54ab858e65fd195c7cf2a53e99d6b'
di={key(r):(i,r) for i,r in enumerate(rd(oldD),2)}
for row in v1:
    k=(row['Story'],row['Axis']);g=gg[k];new=v2index[k]
    for name,value in row.items():ck('unchanged/'+str(k)+'/'+name,new[name],value,'text')
    ck(str(k)+'/case_count',row['case_count'],7)
    ck(str(k)+'/Location',row['Location'],'Bottom','text')
    for prefix,selector,tiefield in [('minimum_r','minr','minimum_r_all_case_ties'),('reference_demand','maxPM','reference_max_PM_all_case_ties')]:
        a=g[selector][0];ck(str(k)+'/'+tiefield,row[tiefield],';'.join(sorted(x['Case'] for x in g[selector])),'text')
        ck(str(k)+'/'+prefix+'/Case',row[prefix+'_case'],a['Case'],'text')
        for tail,src in [('PB_kN','PB'),('PM_kN','PM'),('r_percent','r'),('r_at_percent','rat'),('d_pp','d'),('tB_s','tB'),('tM_s','tM')]:
            ck(str(k)+'/'+prefix+'/'+tail,row[prefix+'_'+tail],a[src], 'force' if src in ['PB','PM'] else 'ratio_or_time')
        ck(str(k)+'/'+prefix+'/d_source_line',row[prefix+'_d_source_line'],di[key(a)][0])
        for tail,src in [('original_peak_source_row_B','source_row_B'),('original_peak_source_row_M','source_row_M')]:
            ck(str(k)+'/'+prefix+'/'+tail,row[prefix+'_'+tail],a[src],'text')
        for tail,src in [('VM_at_tB_signed_kN','VM_at_tB'),('A_abs_VM_at_tB_kN','A')]:ck(str(k)+'/'+prefix+'/'+tail,new[prefix+'_'+tail],a[src],'force')
        assert 'not supplied' in new[prefix+'_VM_tB_native_row']
    ck(str(k)+'/same controllers',row['same_minimum_r_and_reference_demand_case'],str(g['minr'][0]['Case']==g['maxPM'][0]['Case']),'text')
    rr=[a for a in ind['records'] if a['Story']==row['Story'] and a['Axis']==row['Axis']]
    ck(str(k)+'/median',row['median_r_percent'],g['median_r'],'ratio_or_time')
    ck(str(k)+'/maxr',row['maximum_r_percent'],max(D(x['r']) for x in rr),'ratio_or_time')
    for prefix,sel in [('maxPB','maxPB'),('maxd','maxd')]:
        a=g[sel][0];ck(str(k)+'/'+prefix+'/ties',new[prefix+'_all_ties'],';'.join(sorted(x['Case'] for x in g[sel])),'text')
        ck(str(k)+'/'+prefix+'/case',new[prefix+'_case'],a['Case'],'text')
        for tail,src in [('PB_kN','PB'),('PM_kN','PM'),('r_percent','r'),('r_at_percent','rat'),('d_pp','d'),('VM_at_tB_signed_kN','VM_at_tB'),('A_abs_VM_at_tB_kN','A'),('tB_s','tB'),('tM_s','tM')]:
            ck(str(k)+'/'+prefix+'/'+tail,new[prefix+'_'+tail],a[src],'force' if src in ['PB','PM','VM_at_tB','A'] else 'ratio_or_time')
        ck(str(k)+'/'+prefix+'/source_d_line',new[prefix+'_source_d_line'],di[key(a)][0])
        for tail,src in [('source_B_peak_row','source_row_B'),('source_M_own_peak_row','source_row_M')]:ck(str(k)+'/'+prefix+'/'+tail,new[prefix+'_'+tail],a[src],'text')
        assert 'not supplied' in new[prefix+'_VM_tB_native_row']
    ck(str(k)+'/maxPB',row['baseline_envelope_PBmax_kN'],g['maxPB'][0]['PB'],'force')
    ck(str(k)+'/maxPM',row['reference_envelope_PMmax_kN'],g['maxPM'][0]['PM'],'force')
    ck(str(k)+'/maxPB_ties',row['baseline_envelope_all_case_ties'],g['maxPB'][0]['Case'],'text')
    # Check the extra envelope column as a distinct diagnostic, never a paired r.
    env=100*(1-D(g['maxPM'][0]['PM'])/D(g['maxPB'][0]['PB']))
    ck(str(k)+'/envelope_ratio',row['independent_envelope_reduction_percent'],env,'ratio_or_time')
    ck(str(k)+'/envelope_same',row['envelope_pair_is_same_case'],str(g['maxPM'][0]['Case']==g['maxPB'][0]['Case']),'text')
    ck(str(k)+'/tie_peak_flag',new['all_tied_baseline_peaks_audited'],'False','text')
screen=rd(R/'bottom-and-mean-screening-by-case-14.csv');cc={a['Case']:a for a in ind['cases']};assert len(screen)==14
for x in screen:
    a=cc[x['Case']];rs=[r for r in ind['records'] if r['Case']==x['Case']];mi=D(a['min_records'][0]['r']);bo=D(a['bottom']['r']);mean=D(a['mean'])
    for field,value in [('minimum_r_percent',mi),('bottom_r_percent',bo),('mean12_r_percent',mean),('bottom_minus_min_pp',a['bottom_minus_min']),('mean_minus_min_pp',a['mean_minus_min']),('maximum_d_pp',max(D(r['d']) for r in rs)),('maximum_abs_peak_time_shift_s',max(abs(D(r['tM'])-D(r['tB'])) for r in rs))]:ck(x['Case']+'/'+field,x[field],value,'ratio_or_time')
    ck(x['Case']+'/minimum_stories',x['minimum_stories'],';'.join(sorted(r['Story'] for r in a['min_records'])),'text')
    ck(x['Case']+'/bottom_is_minimum',x['bottom_is_minimum'],str(bo==mi),'text')
    for f,v in [('stories_below_bottom_count',sum(D(r['r'])<bo-D('1e-10') for r in rs)),('stories_below_mean_count',sum(D(r['r'])<mean-D('1e-10') for r in rs))]:ck(x['Case']+'/'+f,x[f],v)
trace=rd(R/'paired-record-evidence-168.csv');assert len(trace)==len({key(x) for x in trace})==168
aliases={'P_B_kN':'PB','P_M_kN':'PM','V_M_at_tB_signed_kN':'VM_at_tB','A_abs_V_M_at_tB_kN':'A','t_B_s':'tB','t_M_s':'tM','r_at_percent':'rat','d_pp':'d','r_peak_percent':'r'}
for x in trace:
    a=ii[key(x)]
    for f,s in aliases.items():ck(str(key(x))+'/'+f,x[f],a[s],'force' if s in ['PB','PM','VM_at_tB','A'] else 'ratio_or_time')
    for f,s in [('source_row_B_peak','source_row_B'),('source_row_M_peak','source_row_M'),('wave_family','wave_family'),('n_saved','n_points')]:ck(str(key(x))+'/'+f,x[f],a[s],'text')
    ck(str(key(x))+'/source_d_line',x['source_d_line'],di[key(x)][0])
    ck(str(key(x))+'/source_CSV_line',x['source_CSV_line'],a['source_CSV_line'])
    for f,s in [('t_start_s','t0_s'),('t_end_s','t1_s')]:ck(str(key(x))+'/'+f,x[f],a[s],'ratio_or_time')
    ck(str(key(x))+'/tieflag',x['all_tied_baseline_peaks_audited'],'False','text')
    ck(str(key(x))+'/unit',x['force_unit'],'kN','text');ck(str(key(x))+'/source_sha',x['source_d_sha256'],sha(oldD),'text')
    ck(str(key(x))+'/parent_sha',x['source_parent168_sha256'],ind['input']['sha256'],'text')
    assert 'not supplied' in x['native_VM_tB_row'] and 'do not reuse' in x['native_VM_tB_row']
    assert x['pair_id']=='Blabel0_Mlabel3_native_c14e71ab_c2107333'
    assert x['model_M_label']=='modal_added_label3' and x['model_B_label']=='baseline_label0'
    assert x['baseline_peak_selection']=='first previously saved maximum'
    assert x['Case'] in x['review_entry'] and x['Story'] in x['review_entry']
mdrows=[line.strip('|').split('|') for line in (R/'engineering-review-table-24.md').read_text(encoding='utf-8').splitlines() if line.startswith('|')][2:]
assert len(mdrows)==24
for x in mdrows:
    axis,story=x[0].split('/');g=gg[(story,axis)]
    for sel,casecol,rcol,forcecol in [('minr',1,2,3),('maxPM',4,6,5)]:
        a=g[sel][0];ck('Markdown/'+story+'/'+axis+'/'+sel+'/case',x[casecol],a['Case'],'text')
        ck('Markdown/'+story+'/'+axis+'/'+sel+'/r',x[rcol],a['r'],'display_ratio','0.0000500001')
        for value,f in zip(x[forcecol].split('/'),['PB','PM']):ck('Markdown/'+story+'/'+axis+'/'+sel+'/'+f,value.strip(),a[f],'display_force','0.00500001')
ex=json.loads((R/'two-engineering-examples.json').read_text(encoding='utf-8'))
def excheck(x,a,label):
    for f,s in [('PB_kN','PB'),('PM_kN','PM'),('r_percent','r'),('d_pp','d'),('tB_s','tB'),('tM_s','tM')]:ck(label+'/'+f,x[f],a[s],'example')
excheck(ex[0],ii[('SHW7X','Story7','X','Bottom')],'exampleSHW7X')
ck('exampleSHW7X/bottom',ex[0]['bottom_r_percent'],cc['SHW7X']['bottom']['r'],'example')
ck('exampleSHW7X/mean',ex[0]['mean_r_percent'],cc['SHW7X']['mean'],'example')
g=gg[('Story5','X')]
for field,sel in [('minimum_reduction','minr'),('reference_demand','maxPM')]:
    ck('exampleStory5/'+field+'/Case',ex[1][field]['Case'],g[sel][0]['Case'],'text');excheck(ex[1][field],g[sel][0],'exampleStory5/'+field)
small=json.loads((R/'small-results-summary.json').read_text(encoding='utf-8'))
for f,want in [('control_key_differences',ind['minr_vs_maxPM_different_groups']),('baseline_and_reference_envelope_control_differences',ind['maxPB_vs_maxPM_different_groups']),('rows',168),('engineering_rows',24),('cases',14)]:ck('summary/'+f,small[f],want)
# Validate only selected small inherited metadata, not response/state arrays.
freeze=json.loads((R/'input-rules-freeze.json').read_text(encoding='utf-8'));meta_path=Path(freeze['inputs'][2]['path']);assert sha(meta_path)==freeze['inputs'][2]['sha256']
metadata=json.loads(meta_path.read_text(encoding='utf-8'));mi={a['case']:a for a in metadata['matched_grids_and_inputs']}
for a in rd(R/'paired-input-and-output-metadata-14.csv'):
    m=mi[a['Case']];ck(a['Case']+'/metadata/n',a['saved_n'],m['n']);ck(a['Case']+'/metadata/PGA',a['PGA_mm_per_s2'],m['PGA_mm_s2'])
    ck(a['Case']+'/metadata/tend',a['saved_t1_s'],m['t_end']);assert m['same_input_all_samples']
    assert a['same_input_all_samples_historically_verified']=='True'
    assert 'not available' in a['internal_integration_dt'] and 'not exposed' in a['numeric_scale_and_time_scale_factors']
out={'completed_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'producer_manifests':mf,
 'minr_vs_maxPM_different_groups':ind['minr_vs_maxPM_different_groups'],'maxPB_vs_maxPM_different_groups':ind['maxPB_vs_maxPM_different_groups'],
 'strict_tie_groups':ind['strict_tie_groups'],'check_counts':dict(counts),'max_difference_by_kind':dict(maxdiff),
 'all_check_locations':checked,'main_rows':24,'screening_rows':14,'trace_rows':168,'Markdown_rows':24,
 'v001_columns_unchanged_in_v002':True,'all_four_control_groups_match_independent_selection':True,
 'must_numeric_or_pairing_items':0,'extra_envelope_ratio':'arithmetic passes; optional appendix diagnostic with independent PB/PM controls, not a same-input record or the engineering main objective',
 'no_producer_script_executed':True,'raw_arrays_read':False,'new_ODE':0}
with (O/'frozen-table-comparison.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2,default=str)
print(json.dumps({k:v for k,v in out.items() if k!='all_check_locations'},ensure_ascii=False,indent=2,default=str))
