"""Frozen descriptive floor record peaks from three existing CSI caches only."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json, sys, time
import numpy as np

HERE=Path(__file__).resolve().parent
PROTOCOL_SHA='c22487c9550eb6c3b06c9daef89737eda405ace2cf6c0688757e92bbec23e73c'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def packed(v): return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def writecsv(name,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    start=time.perf_counter(); assert not (HERE/'summary_r005.json').exists(),'Frozen output exists'
    assert sha(HERE/'protocol.json')==PROTOCOL_SHA
    p=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'));cache=Path(p['cache_dir'])
    assert sha(cache/'manifest.json')==p['coverage_manifest']['sha256']
    m=json.loads((cache/'manifest.json').read_text(encoding='utf-8'))
    group_rows=[]; store={}; metadata_omitted=['Label','X','Y','Z']
    for table,ref in p['inputs'].items():
        assert sha(cache/ref['file'])==ref['sha256']
        meta=m['tables'][table];columns=meta['columns']; unit_by_header=dict(zip(meta['headers'],meta['units']))
        with np.load(cache/ref['file'],allow_pickle=False) as arrays:
            for gid,g in meta['groups'].items():
                keys=g['keys'];case=keys['Output Case'];story=keys['Story']
                if case not in p['cases'] or story not in p['stories']:continue
                component=p['mapping'][case[-1]][table]
                if table=='Story Forces' and keys.get('Location')!='Bottom':continue
                if table=='Story Drifts' and keys.get('Direction')!=component:continue
                valuecol='Drift' if table=='Story Drifts' else component
                if valuecol not in columns:
                    store.setdefault((table,case,story),[]).append({'status':'unmatched_field','component':component});continue
                a=arrays[gid]; t=a[:,columns.index('Time')]; y=a[:,columns.index(valuecol)]; source=a[:,columns.index('SourceRow')]
                expected_n,expected_end=p['expected_grid'][case]; tol=p['grid_absolute_tolerance_s']; expected=np.arange(expected_n)*p['time_step_s']
                finite=bool(np.isfinite(a).all());unique=len(np.unique(t));increasing=bool(np.all(np.diff(t)>0))
                complete=bool(finite and len(t)==expected_n and increasing and np.max(np.abs(t-expected))<=tol)
                ongrid=bool(np.isfinite(t).all() and np.all(np.abs(t/p['time_step_s']-np.rint(t/p['time_step_s']))<1e-8) and np.all(t>=-tol) and np.all(t<=expected_end+tol))
                magnitude=float(np.max(np.abs(y))) if finite else None
                ii=np.flatnonzero(np.abs(y)==magnitude) if finite else []
                diaphragm=keys.get('Diaphragm','')
                controllers=[{'diaphragm':diaphragm,'t_s':float(t[i]),'signed_value':float(y[i]),'source_row':int(source[i])} for i in ii]
                row={'table':table,'group_id':gid,'Case':case,'Story':story,'component':component,'Diaphragm':diaphragm,
                    'Location':keys.get('Location',''),'unit':unit_by_header.get(valuecol) or 'export_unit_blank',
                    'n_exported':len(t),'n_unique_times':unique,'n_expected':expected_n,'missing_grid_time_count':expected_n-unique if ongrid else '',
                    't_first_s':float(t[0]),'t_last_s':float(t[-1]),'finite':finite,'strictly_increasing':increasing,'all_times_on_expected_grid':ongrid,
                    'complete_expected_grid':complete,'abs_record_peak':magnitude,'peak_controller_count':len(controllers),'peak_controllers_json':packed(controllers),
                    'source_row_first':int(source[0]),'source_row_last':int(source[-1]),
                    'Label_status':'not_preserved_in_cache' if table=='Story Drifts' else 'not_applicable',
                    'coordinates_status':'not_preserved_in_cache' if table=='Story Drifts' else 'not_applicable'}
                group_rows.append(row)
                store.setdefault((table,case,story),[]).append({'status':'ok' if finite else 'nonfinite_unavailable','peak':magnitude,'controllers':controllers,'coverage':row})
    floors=[];ranks=[];compare=[]
    tables={'shear':'Story Forces','cm':'Diaphragm CM Displacements','drift':'Story Drifts'}
    for case in p['cases']:
        cf=[]
        for story in p['stories']:
            row={'Case':case,'Story':story,'case_suffix_analysis_direction_only':case[-1]}
            for short,table in tables.items():
                groups=store.get((table,case,story),[])
                ok=bool(groups and all(g['status']=='ok' for g in groups))
                peak=max(g['peak'] for g in groups) if ok else None
                controllers=[c for g in groups if ok and g['peak']==peak for c in g['controllers']]
                row.update({short+'_abs_record_peak':peak,short+'_unit':groups[0]['coverage']['unit'] if ok else '',
                    short+'_status':'available' if ok else 'unmatched_or_unavailable',short+'_n_groups':len(groups),
                    short+'_all_groups_complete':bool(ok and all(g['coverage']['complete_expected_grid'] for g in groups)),
                    short+'_n_exported':sum(g['coverage']['n_exported'] for g in groups) if ok else 0,
                    short+'_controllers_json':packed(controllers)})
            row.update({'drift_scope':'exported_records_only_not_full_history_peak','drift_Label':'','drift_X_m':'','drift_Y_m':'','drift_Z_m':'',
                'drift_locator_status':'Label_and_coordinates_not_preserved_in_cache; see controller SourceRow'})
            floors.append(row);cf.append(row)
        sets={};maxsets={}
        for short in tables:
            available=[r for r in cf if r[short+'_abs_record_peak'] is not None]
            ordered=sorted(available,key=lambda r:(-r[short+'_abs_record_peak'],int(r['Story'][5:])))
            cutoff=ordered[min(2,len(ordered)-1)][short+'_abs_record_peak'] if ordered else None
            selected=[r for r in ordered if r[short+'_abs_record_peak']>=cutoff] if ordered else []
            sets[short]=[r['Story'] for r in selected]
            maxsets[short]=[r['Story'] for r in ordered if r[short+'_abs_record_peak']==ordered[0][short+'_abs_record_peak']] if ordered else []
            for r in selected:
                val=r[short+'_abs_record_peak'];rank=1+sum(x[short+'_abs_record_peak']>val for x in available)
                ranks.append({'Case':case,'metric':short,'rank_competition':rank,'Story':r['Story'],'abs_record_peak':val,'unit':r[short+'_unit'],
                    'all_groups_complete':r[short+'_all_groups_complete'],'controllers_json':r[short+'_controllers_json'],
                    'scope':'sparse_exported_drift_only' if short=='drift' else 'record_peak'})
        main_complete=all(r['shear_all_groups_complete'] and r['cm_all_groups_complete'] for r in cf)
        overlap=sorted(set(sets['shear'])&set(sets['cm']),key=lambda s:int(s[5:]))
        gaps=[abs(int(s[5:])-int(c[5:])) for s in maxsets['shear'] for c in maxsets['cm']]
        compare.append({'Case':case,'main_comparison_eligible':main_complete,'shear_top3_including_ties_json':packed(sets['shear']),
            'cm_top3_including_ties_json':packed(sets['cm']),'intersection_json':packed(overlap),'intersection_n':len(overlap),
            'shear_max_floor_set_json':packed(maxsets['shear']),'cm_max_floor_set_json':packed(maxsets['cm']),
            'max_floor_absolute_index_gaps_json':packed(gaps),'drift_top3_separate_sparse_json':packed(sets['drift'])})
    outputs=[('floor_record_peaks_r005.csv',floors),('diaphragm_record_peaks_r005.csv',[r for r in group_rows if r['table']=='Diaphragm CM Displacements']),
        ('mapped_group_coverage_r005.csv',group_rows),('top3_floor_ranks_r005.csv',ranks),('main_metric_comparison_r005.csv',compare)]
    checks={'72_floor_rows':len(floors)==72,'108_separate_CM_groups':sum(r['table']=='Diaphragm CM Displacements' for r in group_rows)==108,
        '72_bottom_shear_groups':sum(r['table']=='Story Forces' and r['Location']=='Bottom' for r in group_rows)==72,
        '72_mapped_drift_groups':sum(r['table']=='Story Drifts' for r in group_rows)==72,
        'all_selected_values_finite':all(r['finite'] for r in group_rows),'all_shear_and_CM_complete':all(c['main_comparison_eligible'] for c in compare),
        'all_source_hashes_unchanged':all(sha(cache/r['file'])==r['sha256'] for r in p['inputs'].values()) and sha(cache/'manifest.json')==p['coverage_manifest']['sha256'],
        'protocol_unchanged':sha(HERE/'protocol.json')==PROTOCOL_SHA,'runtime_below_480s':time.perf_counter()-start<480}
    assert all(checks.values()),checks
    for name,rows in outputs:writecsv(name,rows)
    summary={'evidence_id':p['evidence_id'],'review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
        'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'source_refs':p['inputs'],'coverage_manifest':p['coverage_manifest'],
        'row_counts':{name:len(rows) for name,rows in outputs},'comparisons':compare,'checks':checks,
        'drift_missing_grid_counts':sorted({r['missing_grid_time_count'] for r in group_rows if r['table']=='Story Drifts'}),
        'drift_complete_groups':sum(r['complete_expected_grid'] for r in group_rows if r['table']=='Story Drifts'),
        'drift_metadata_not_preserved':metadata_omitted,'output_sha256':{name:sha(HERE/name) for name,_ in outputs}}
    (HERE/'summary_r005.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    run={'command_argv':sys.argv,'python':sys.version,'numpy':np.__version__,'finished_utc':summary['finished_utc'],'elapsed_seconds':summary['elapsed_seconds'],
        'exit_code_after_checks':0,'protocol_sha256':PROTOCOL_SHA,'code_sha256':summary['code_sha256'],'summary_sha256':sha(HERE/'summary_r005.json'),'checks':checks}
    (HERE/'run_record_r005.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
