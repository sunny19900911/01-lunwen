"""NumPy only decodes frozen NPZ; scalar Python independently checks peaks/ranks."""
import argparse
import csv
import hashlib
import json
import math
import platform
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))


def packed(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))


def same(ours,theirs):
    assert set(ours)==set(theirs),(set(ours)-set(theirs),set(theirs)-set(ours))
    for k,v in ours.items():
        ref=theirs[k]
        if k.endswith('_json'): assert json.loads(v)==json.loads(ref),(k,v,ref)
        elif isinstance(v,bool): assert v==(ref if isinstance(ref,bool) else ref=='True'),(k,v,ref)
        elif isinstance(v,(int,float)): assert v==float(ref),(k,v,ref)
        else: assert v==ref,(k,v,ref)


def run(source,out):
    assert sha(source/'report.md')=='7b93bbcfee088ecf1862835b2a2e12944c38b494865d0849ed8010d1c6335d37'
    assert sha(source/'protocol.json')=='c22487c9550eb6c3b06c9daef89737eda405ace2cf6c0688757e92bbec23e73c'
    assert sha(source/'delivery_manifest_r005.json')=='7defe31bfca11c3bfbb53891a859288fcb1d832a0b39ba2148b0744fafdbe2c7'
    delivery=json.loads((source/'delivery_manifest_r005.json').read_text(encoding='utf-8'))
    files=[source/'delivery_manifest_r005.json']
    for x in delivery['files']:
        f=source/x['name'];assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes'];files.append(f)
    p=json.loads((source/'protocol.json').read_text(encoding='utf-8'));cache=Path(p['cache_dir'])
    manifest_path=cache/p['coverage_manifest']['file'];assert sha(manifest_path)==p['coverage_manifest']['sha256'];files.append(manifest_path)
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['sha256']==p['source_xlsx_identity_inherited_only']['sha256']
    assert manifest['bytes']==p['source_xlsx_identity_inherited_only']['bytes']
    for ref in p['inputs'].values():
        f=cache/ref['file'];assert sha(f)==ref['sha256'];files.append(f)
    before=[{'path':str(f.resolve()),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]
    assert p['cases']==['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']
    assert p['stories']==['Story'+str(i) for i in range(1,13)]
    assert p['mapping']=={'X':{'Story Forces':'VX','Diaphragm CM Displacements':'UX','Story Drifts':'X'},
                          'Y':{'Story Forces':'VY','Diaphragm CM Displacements':'UY','Story Drifts':'Y'}}
    assert p['time_step_s']==.02 and p['grid_absolute_tolerance_s']==1e-10
    groups=[];buckets=defaultdict(list);selected_points=0
    for table,ref in p['inputs'].items():
        meta=manifest['tables'][table];schema=p['schema_before_values'][table]
        for key in ['columns','key_columns','headers','units']:assert meta[key]==schema[key],(table,key)
        columns=meta['columns'];units=dict(zip(meta['headers'],meta['units']))
        if table=='Story Drifts':assert all(k not in columns for k in ['Label','X','Y','Z']) and units['Drift'] is None
        with np.load(cache/ref['file'],allow_pickle=False) as arrays:
            assert set(arrays.files)==set(meta['groups'])
            for gid,g in meta['groups'].items():
                keys=g['keys'];case=keys['Output Case'];story=keys['Story'];assert keys['Case Type']=='NonModHist'
                if case not in p['cases'] or story not in p['stories']:continue
                component=p['mapping'][case[-1]][table]
                if table=='Story Forces' and keys.get('Location')!='Bottom':continue
                if table=='Story Drifts' and keys.get('Direction')!=component:continue
                valuecol='Drift' if table=='Story Drifts' else component;assert valuecol in columns
                # No NumPy numerical reductions, sorting, slicing or interpolation.
                data=arrays[gid].tolist();assert all(len(row)==len(columns) for row in data)
                assert all(math.isfinite(value) for row in data for value in row)
                ti=columns.index('Time');yi=columns.index(valuecol);si=columns.index('SourceRow')
                t=[row[ti] for row in data];y=[row[yi] for row in data];sr=[row[si] for row in data]
                assert all(value==int(value) and value>=4 for value in sr)
                n,expected_end=p['expected_grid'][case];unique=set(t)
                increasing=all(t[i]<t[i+1] for i in range(len(t)-1))
                ongrid=all(abs(v/.02-round(v/.02))<1e-8 and -1e-10<=v<=expected_end+1e-10 for v in t)
                missing=sorted(set(range(n))-{round(v/.02) for v in t})
                complete=len(t)==n and increasing and all(abs(v-i*.02)<=1e-10 for i,v in enumerate(t))
                peak=max(abs(v) for v in y);diaphragm=keys.get('Diaphragm','')
                controllers=[{'diaphragm':diaphragm,'t_s':t[i],'signed_value':y[i],'source_row':int(sr[i])}
                             for i in range(len(t)) if abs(y[i])==peak]
                row={'table':table,'group_id':gid,'Case':case,'Story':story,'component':component,'Diaphragm':diaphragm,
                    'Location':keys.get('Location',''),'unit':units.get(valuecol) or 'export_unit_blank',
                    'n_exported':len(t),'n_unique_times':len(unique),'n_expected':n,'missing_grid_time_count':len(missing) if ongrid else '',
                    't_first_s':t[0],'t_last_s':t[-1],'finite':True,'strictly_increasing':increasing,
                    'all_times_on_expected_grid':ongrid,'complete_expected_grid':complete,'abs_record_peak':peak,
                    'peak_controller_count':len(controllers),'peak_controllers_json':packed(controllers),
                    'source_row_first':int(sr[0]),'source_row_last':int(sr[-1]),
                    'Label_status':'not_preserved_in_cache' if table=='Story Drifts' else 'not_applicable',
                    'coordinates_status':'not_preserved_in_cache' if table=='Story Drifts' else 'not_applicable'}
                assert g['n']==len(data) and g['n_unique']==len(unique)
                assert g['t0']==t[0] and g['t1']==t[-1] and g['strictly_increasing']==increasing and g['finite']
                assert increasing and ongrid and len(unique)==len(t)
                groups.append(row);buckets[(table,case,story)].append(row);selected_points+=len(t)
    reference=rows(source/'mapped_group_coverage_r005.csv');assert len(reference)==len(groups)==252
    refs={(x['table'],x['group_id']):x for x in reference};assert len(refs)==252
    for row in groups:same(row,refs[(row['table'],row['group_id'])])
    cm=[x for x in groups if x['table']=='Diaphragm CM Displacements'];assert len(cm)==108
    refs={x['group_id']:x for x in rows(source/'diaphragm_record_peaks_r005.csv')};assert len(refs)==108
    for row in cm:same(row,refs[row['group_id']])
    floors=[];metrics={'shear':'Story Forces','cm':'Diaphragm CM Displacements','drift':'Story Drifts'}
    for case in p['cases']:
        for story in p['stories']:
            row={'Case':case,'Story':story,'case_suffix_analysis_direction_only':case[-1]}
            for short,table in metrics.items():
                gs=buckets[(table,case,story)];assert gs
                peak=max(x['abs_record_peak'] for x in gs)
                controllers=[c for x in gs if x['abs_record_peak']==peak for c in json.loads(x['peak_controllers_json'])]
                row.update({short+'_abs_record_peak':peak,short+'_unit':gs[0]['unit'],short+'_status':'available',
                    short+'_n_groups':len(gs),short+'_all_groups_complete':all(x['complete_expected_grid'] for x in gs),
                    short+'_n_exported':sum(x['n_exported'] for x in gs),short+'_controllers_json':packed(controllers)})
            row.update({'drift_scope':'exported_records_only_not_full_history_peak','drift_Label':'','drift_X_m':'','drift_Y_m':'','drift_Z_m':'',
                        'drift_locator_status':'Label_and_coordinates_not_preserved_in_cache; see controller SourceRow'})
            floors.append(row)
    refs={(x['Case'],x['Story']):x for x in rows(source/'floor_record_peaks_r005.csv')};assert len(refs)==len(floors)==72
    compact={(x['Case'],x['Story']):x for x in rows(source/'floor_three_metric_table_r005.csv')};assert len(compact)==72
    for row in floors:
        same(row,refs[(row['Case'],row['Story'])])
        small={'Case':row['Case'],'Story':row['Story'],'Bottom_shear_abs_record_peak_kN':row['shear_abs_record_peak'],
               'CM_abs_record_peak_mm':row['cm_abs_record_peak'],'Drift_exported_abs_record_peak_unit_blank':row['drift_abs_record_peak'],
               'shear_and_CM_complete':row['shear_all_groups_complete'] and row['cm_all_groups_complete'],
               'Drift_scope':'exported_records_only; Label/coordinates unavailable'}
        same(small,compact[(row['Case'],row['Story'])])
    ranks=[];comparisons=[];boundary=[];global_controllers=[];diaphragms={}
    for case in p['cases']:
        selected={};maxsets={};cf=[x for x in floors if x['Case']==case]
        diaphragms[case]={s:[x['Diaphragm'] for x in buckets[('Diaphragm CM Displacements',case,s)]] for s in p['stories']}
        for metric in metrics:
            field=metric+'_abs_record_peak';values=sorted((x[field] for x in cf),reverse=True);cutoff=values[2]
            chosen=sorted([x for x in cf if x[field]>=cutoff],key=lambda x:(-x[field],int(x['Story'][5:])))
            selected[metric]=[x['Story'] for x in chosen]
            maxsets[metric]=[x['Story'] for x in chosen if x[field]==values[0]]
            boundary.append({'Case':case,'metric':metric,'third_floor_value':cutoff,'boundary_equal_count':values.count(cutoff),
                             'selected_count':len(chosen),'fourth_floor_value':values[3]})
            for x in chosen:
                rank=1+sum(v>x[field] for v in values)
                ranks.append({'Case':case,'metric':metric,'rank_competition':rank,'Story':x['Story'],'abs_record_peak':x[field],
                              'unit':x[metric+'_unit'],'all_groups_complete':x[metric+'_all_groups_complete'],
                              'controllers_json':x[metric+'_controllers_json'],'scope':'sparse_exported_drift_only' if metric=='drift' else 'record_peak'})
                if rank==1:global_controllers.append({'Case':case,'metric':metric,'Story':x['Story'],
                                                     'controllers':json.loads(x[metric+'_controllers_json'])})
        overlap=sorted(set(selected['shear'])&set(selected['cm']),key=lambda x:int(x[5:]))
        row={'Case':case,'main_comparison_eligible':all(x['shear_all_groups_complete'] and x['cm_all_groups_complete'] for x in cf),
             'shear_top3_including_ties_json':packed(selected['shear']),'cm_top3_including_ties_json':packed(selected['cm']),
             'intersection_json':packed(overlap),'intersection_n':len(overlap),'shear_max_floor_set_json':packed(maxsets['shear']),
             'cm_max_floor_set_json':packed(maxsets['cm']),
             'max_floor_absolute_index_gaps_json':packed([abs(int(s[5:])-int(c[5:])) for s in maxsets['shear'] for c in maxsets['cm']]),
             'drift_top3_separate_sparse_json':packed(selected['drift'])}
        comparisons.append(row)
    refs={(x['Case'],x['metric'],x['Story']):x for x in rows(source/'top3_floor_ranks_r005.csv')};assert len(refs)==len(ranks)==54
    for row in ranks:same(row,refs[(row['Case'],row['metric'],row['Story'])])
    refs={x['Case']:x for x in rows(source/'main_metric_comparison_r005.csv')};assert len(refs)==6
    summary=json.loads((source/'summary_r005.json').read_text(encoding='utf-8'))
    for row in comparisons:
        same(row,refs[row['Case']]);same(row,next(x for x in summary['comparisons'] if x['Case']==row['Case']))
    drift=[x for x in groups if x['table']=='Story Drifts'];assert len(drift)==72
    missing=sorted({x['missing_grid_time_count'] for x in drift});assert missing==summary['drift_missing_grid_counts']
    assert not any(x['complete_expected_grid'] for x in drift) and min(missing)==1 and max(missing)==21
    assert all(x['complete_expected_grid'] for x in groups if x['table']!='Story Drifts')
    report=(source/'report.md').read_text(encoding='utf-8')
    report_floor_lines=[line for line in report.splitlines() if line.startswith('| Story')];assert len(report_floor_lines)==72
    for x,line in zip(floors,report_floor_lines):
        cells=[v.strip() for v in line.strip('|').split('|')]
        assert cells==[x['Story']]+[format(x[k+'_abs_record_peak'],'.8g') for k in metrics]
    report_locators=[]
    for line in report.splitlines():
        if not line.startswith('| '):continue
        cells=[v.strip() for v in line.strip('|').split('|')]
        if len(cells)==7 and cells[1] in metrics:report_locators.append(cells)
    expected=[]
    for case in p['cases']:
        for metric in metrics:
            for x in global_controllers:
                if (x['Case'],x['metric'])!=(case,metric):continue
                for c in x['controllers']:
                    expected.append([case,metric,x['Story'],c['diaphragm'] or '\u2014',format(c['t_s'],'.8g'),format(c['signed_value'],'.9g'),str(c['source_row'])])
    assert report_locators==expected
    for x in before:
        f=Path(x['path']);assert sha(f)==x['sha256'] and f.stat().st_size==x['bytes']
    result={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,
        'python':platform.python_version(),'numpy_decode_version':np.__version__,'script_sha256':sha(Path(__file__)),
        'method':'NumPy load(...,allow_pickle=False) and tolist only; scalar Python finite/grid/max/exact ties/diaphragm pooling/ranking.',
        'counts':{'mapped_groups':len(groups),'Bottom_shear_groups':len(groups)-len(cm)-len(drift),'CM_groups':len(cm),
                  'mapped_Drift_groups':len(drift),'selected_record_points':selected_points,'floor_rows':len(floors),
                  'top3_rows':len(ranks),'main_comparison_rows':len(comparisons),'report_floor_numeric_cells':216,'report_global_locator_rows':len(expected)},
        'comparisons':comparisons,'third_rank_boundaries':boundary,'global_peak_controllers':global_controllers,
        'CM_actual_diaphragms_by_case_story':diaphragms,'Drift_missing_grid_counts':missing,
        'Drift_missing_count_histogram':{str(n):sum(x['missing_grid_time_count']==n for x in drift) for n in missing},
        'Drift_complete_groups':0,'exact_source_field_differences':0,
        'group_peak_controller_tie_groups':sum(x['peak_controller_count']>1 for x in groups),
        'third_rank_boundary_tie_cases':sum(x['boundary_equal_count']>1 for x in boundary),
        'inputs_before_and_after':before,
        'limits':['Single-model descriptive output locations only, no reduction/layout superiority/innovation certification.',
                  'Case suffix is mapping convention, not certified excitation direction.',
                  'Drift is exported-record maximum only; 1-21 missing grid steps, unknown unit, Label/XYZ absent from cache.',
                  'Raw XLSX identity inherited from manifest, not reread or rehashed; no full-array outputs or uploads.']}
    out.mkdir(parents=True,exist_ok=True);target=out/'review_summary.json';assert not target.exists()
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ['recorded_at','checks_passed','counts','Drift_missing_grid_counts',
        'group_peak_controller_tie_groups','third_rank_boundary_tie_cases','comparisons']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();run(args.source,args.out)
