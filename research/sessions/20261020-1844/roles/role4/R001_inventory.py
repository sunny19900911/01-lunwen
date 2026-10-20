from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[4];W=R.parent/'W5-重燃双塔连体';D=W/'02-数据/增阻尼多目标研究-20261016';C=W/'research/maxwell-20261017/experiments/R001/core-cache';M=W/'research/maxwell-20261017/roles/experiments/metadata'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sources=[('baseline_label0',D/'原生0数据缓存/manifest.json',D/'native0_small_tables.json'),('modal_added_label3',D/'response_cache_manifest.json',D/'small_tables.json'),('physical_devices',C/'manifest.json',M/'controlled_small_tables.json')]
records=[];tables=[];modes=[];bindings=[]
for model,mp,sp in sources:
 man=load(mp);small=load(sp);bindings.extend([{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [mp,sp]])
 periods=small['Modal Periods And Frequencies'];mass=small['Modal Participating Mass Ratios'];pf=small['Modal Participation Factors'];ph=periods[1][1];mh=mass[1][1];fh=pf[1][1]
 cases=sorted({g['keys']['Output Case'] for g in man['tables']['Base Reactions']['groups'].values()})
 records.append({'model':model,'source_sha256':man['sha256'],'source_bytes':man.get('bytes'),'cached_cases':';'.join(cases),'case_count':len(cases),'period_modes':len(periods)-3,'mass_participation_modes':len(mass)-3,'signed_native_participation_factor_modes':len(pf)-3,'node_mode_shape_vectors_available':False,'modal_coordinate_histories_available':False,'story_modal_shear_histories_available':False,'complete_all_node_displacement_velocity_available':False,'global_response_cache_available':True,'physical_Link_P_U1_complete_unique_records':192 if model=='physical_devices' else 'not established from these caches','actual_background_damping_values_available':False,'input_pairing_status':'baseline_label0 versus modal_added_label3 matched in frozen native_paired_validation.json; physical_devices not certified paired here','exact_native_modal_shear_decomposition_possible_now':False})
 for name,t in man['tables'].items():
  groups=list(t['groups'].values());cols=t.get('columns',t.get('value_columns'))
  tables.append({'model':model,'table':name,'groups':len(groups),'native_rows':t.get('data_rows',t.get('all_data_rows')),'columns':';'.join(cols),'cache_path':str(mp.parent/t['cache']),'cache_exists':(mp.parent/t['cache']).exists(),'time_scope':'per-group metadata in manifest; sparse Drift is not time-filled'})
 for i in range(3):
  v=periods[i+3][1];mu=mass[i+3][1];pa=pf[i+3][1]
  row={'model':model,'mode':int(v[ph.index('Mode')]),'period_s':v[ph.index('Period')],'frequency_Hz':v[ph.index('Frequency')],'native_source_row':periods[i+3][0]}
  for axis in ['UX','UY','RZ']:
   row['mass_ratio_'+axis]=mu[mh.index(axis)];row['native_participation_factor_'+axis]=pa[fh.index(axis)]
  row['scope']='native summary factors; not node vectors, mode amplitude histories or story shear shares';modes.append(row)
cs('R001-three-model-availability.csv',records);cs('R001-response-cache-table-index.csv',tables);cs('R001-first-three-modal-summary.csv',modes)
validation=D/'native_paired_validation.json';audit=R/'papers/damping-output-boundaries/research/roles/experiments/verification-session003/modal-damping-summary.json';mi=M/'metadata_inventory.json'
for p in [validation,audit,mi]:bindings.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
v=load(validation);a=load(audit);meta=load(mi)
save('R001-model-availability.json',{'finished_utc':datetime.now(timezone.utc).isoformat(),'models':records,'input_identity_0_vs_3':{'existing_audit':str(validation),'case_count':len(v['matched_grids_and_inputs']),'all_reported_same_input_samples':all(x['same_input_all_samples'] for x in v['matched_grids_and_inputs']),'settings_equal_excluding_GUID_notes':v['metadata']['load_case_settings_equal_excluding_GUID_notes']},'physical_model_native_inventory_has_node_mode_shapes':any('Mode Shape' in n for n in meta['sheets']),'physical_model_native_joint_velocity_table_truncated':meta['sheets']['Joint Velocities - Absolute']['reaches_excel_row_limit'],'limits':['0 label is not proof of zero damping; 3 label is not native proof of total or added modal damping values','all models have 300 modal summary rows but lack signed node vectors and q_r(t); exact real-building modal story shear decomposition is unavailable','prior modal_reference_states.npz and identified output coefficients are fitted/reference states, not native modal contributions; not read in this task','global frequency/mass agreement does not prove full M/K, mode-vector, damping or local shear equivalence; physical-device high modes differ','frequency bands, mass ratios and participation factors cannot be renamed mode-wise shear shares'],'inputs':bindings,'new_workbook_reads':0,'new_modal_decompositions':0})
print(json.dumps({'models':len(records),'table_index_rows':len(tables),'modal_summary_rows':len(modes),'baseline_to_3_matching_cases':len(v['matched_grids_and_inputs'])},ensure_ascii=False))
