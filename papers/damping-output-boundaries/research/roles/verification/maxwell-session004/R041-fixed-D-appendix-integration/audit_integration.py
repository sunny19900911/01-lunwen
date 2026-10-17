"""Static integration and identity QA only; no new mathematical computation."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
ROLE=HERE.parent
DRAFT=ROOT/'papers/damping-output-boundaries/manuscript/maxwell-fixed-dissipation-peak-appendix-v001.md'
WRITING=ROOT/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/fixed-dissipation-peak-appendix-v001'
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'source-freeze.json').exists()
assert record(DRAFT)=={'path':str(DRAFT.resolve()),'bytes':6726,'sha256':'31f1d60317f94fc7b7b60a01e523f415b21c464682a5c6d4f77ebce1c2ea5741'}
assert record(WRITING/'freeze.json')['sha256']=='bb813d41172305bf80f12f5591a3e63b8b88bdfa34889fba0c7950f42b0d2e9d'
sources=[DRAFT]+[WRITING/n for n in ['freeze.json','input-freeze.json','evidence-map.json','validation.json','report.md']]+[
 ROOT/'research/sessions/20261017-2109/R020-C038-adoption.json',
 ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R029-fixed-dissipation-peak-inverse/report.md',
 ROLE/'R040-fixed-D-inverse-independent/report.md',
 ROLE/'R040-fixed-D-inverse-independent/validation.json',
 ROLE/'R040-fixed-D-inverse-independent/post-freeze-comparison/report.md',
 ROLE/'R040-fixed-D-inverse-independent/post-freeze-comparison/comparison-freeze.json',
 ROLE/'非零末力耗散峰力区间独审-R017.md',
 ROOT/'research/sessions/20261017-2109/fixed-dissipation-peak-inverse-protocol-v001.md']
write('source-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T04:47:04.593875+08:00','deadline':'2026-10-18T04:55:04+08:00','global_deadline':'2026-10-18T07:09:45+08:00','sources':[record(p) for p in sources],'in_progress_R025_example_not_read':True})
frozen=read(WRITING/'freeze.json')
assert all(record(Path(x['path']))==x for x in frozen['files'])
authorinputs=read(WRITING/'input-freeze.json')
for x in authorinputs['direct_sources']:
    actual=record(Path(x['path']));assert all(actual[k]==x[k] for k in ['path','bytes','sha256'])
oldmanifests=authorinputs['old_frozen_manifests']
assert len(oldmanifests)==22 and all(record(Path(x['path']))==x for x in oldmanifests)
adoption=read(ROOT/'research/sessions/20261017-2109/R020-C038-adoption.json')
assert adoption['adopted_claim']=='M-C038' and adoption['status']=='supported' and adoption['review_status']=='reviewed'
previous=ROLE/'R040-fixed-D-inverse-independent/validation.json'
assert record(previous)['sha256']=='7afa29be7d15d5deb0ce02eddee95b4b09e664f6de7d2cdba22b0c69d72c7a29'
d=read(previous)
old=d['frozen_R001_R039']+[{'run_file':str(previous.relative_to(ROLE)).replace('\\','/'),'sha256':record(previous)['sha256'],'outputs_verified':len(d['outputs'])}]
total=0
for x in old:
    p=ROLE/x['run_file'];assert record(p)['sha256']==x['sha256'];prior=read(p)
    outputs=prior.get('outputs',[prior['report']] if 'report' in prior else [])
    assert len(outputs)==x['outputs_verified']
    assert all(record(Path(y['path']))==y for y in outputs);total+=len(outputs)
assert len(old)==40 and total==154
comparison=ROLE/'R040-fixed-D-inverse-independent/post-freeze-comparison/comparison-freeze.json'
assert record(comparison)['sha256']=='dc4fba48a1aebbb52b0d9998bf8bb1cd8a5ff4bf200643d028a0ca79c48737de'
assert all(record(Path(x['path']))==x for x in read(comparison)['outputs'])
text=DRAFT.read_text(encoding='utf-8')
assert re.findall(r'\\tag\{(\d+)\}',text)==list('1234567')
assert text.count('$$')==14
lines=text.splitlines();sep=next(i for i,line in enumerate(lines) if line=='|---|---|')
table=[]
for line in lines[sep+1:]:
    if not line.startswith('|'):break
    table.append(line)
assert len(table)==6 and all(line.count('|')==3 for line in table)
links=re.findall(r'\[[^\]]*\]\(([^)]+)\)',text)
assert len(links)==7
assert all((DRAFT.parent/link).resolve().is_file() for link in links)
binary=DRAFT.read_bytes();assert b'\r' not in binary and not binary.startswith(b'\xef\xbb\xbf') and binary.endswith(b'\n')
assert all(line==line.rstrip() for line in lines)
checks={'required_changes':0,'review_type':'Static integration against admitted C038, not a new proof or numeric test','manual_semantic_checks':{'seven_equations_transcribed_correctly':True,'six_table_branches_cover_admitted_cases':True,'self_contained_functions_and_admissible_class':True,'canonical_D0_is_Uh_not_independent_Lh_alias':True,'domain_empty_before_inverse':True,'minimum_time_singleton_separate':True,'restricted_inverse_images_and_parameter_clipping':True,'zero_right_slope_strict_monotonicity':True,'each_M_construction_and_degenerate_segments':True,'W_subtract_terminal_storage':True,'classic_and_publication_engineering_boundaries':True},'automated_static_checks':{'seven_tags_1to7':True,'six_table_rows_two_columns':True,'seven_local_links_resolve':True,'UTF8_LF_no_BOM_whitespace':True,'fourteen_sources_frozen':len(sources)==14,'writer_five_files_and_eight_direct_sources_unchanged':True,'writer_22_old_manifests_unchanged':True,'old_40_records_154_outputs_unchanged':True,'R040_postcomparison_three_outputs_unchanged':True},'in_progress_R025_example_read':False,'new_proof_numerics_trajectories_arrays_or_parameter_sweep':False}
write('checks.json',checks)
write('prior-preservation.json',{'frozen_R001_R040':old,'main_record_count':40,'main_output_count':154,'R040_comparison_freeze':record(comparison),'R040_comparison_outputs_verified':3,'writer_old_manifests_verified':22})
print(json.dumps({'required_changes':0,'source_records':len(sources),'equations':7,'table_rows':6,'links':len(links),'old_records':40,'old_outputs':154,'postcomparison_outputs':3}))
