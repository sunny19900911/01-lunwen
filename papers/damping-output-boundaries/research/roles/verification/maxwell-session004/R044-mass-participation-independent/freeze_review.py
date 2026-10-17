"""Small identity closure; never follows certificate references to raw data."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources'];assert len(sources)==6 and all(rec(Path(x['path']))==x for x in sources)
assert read(HERE/'checks.json')['all_passed'] and not read(HERE/'checks.json')['new_R032_candidate_read']
prior_path=ROLE/'R043-compact-v004-math-integration/validation.json'
assert rec(prior_path)['sha256']=='18f47c4a1a6300d64cdffd3619003e2354a2325dee885cd0e087497e7aac5624'
prior=read(prior_path)
old=prior['frozen_R001_R042']+[{'run_file':str(prior_path.relative_to(ROLE)).replace('\\','/'),'sha256':rec(prior_path)['sha256'],'outputs_verified':len(prior['outputs'])}]
total=0
for x in old:
    p=ROLE/x['run_file'];assert rec(p)['sha256']==x['sha256'];d=read(p)
    outs=d.get('outputs',[d['report']] if 'report' in d else []);assert len(outs)==x['outputs_verified']
    assert all(rec(Path(y['path']))==y for y in outs);total+=len(outs)
assert len(old)==43 and total==174
extra=prior['additional_postcomparison_freezes']
for x in extra:
    assert rec(Path(x['path']))==x and all(rec(Path(y['path']))==y for y in read(Path(x['path']))['outputs'])
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');s=b.decode('utf-8');assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T05:21:06+08:00'
write('closure_checks.json',{'at':at,'root_candidate_required_changes':0,'independent_exact_modal_and_threshold_algebra_passed':True,'fixed_witness_and_original_machine_contract_retained':True,'fixed_u1_universal_lower_bound_explicitly_rejected':True,'six_sources_unchanged':True,'old_43_records_174_outputs_and_six_postcomparison_outputs_unchanged':True,'new_R032_candidate_read':False,'NPZ_or_history_opened_or_hashed':False,'new_ODE_arrays_data_scan_or_literature':False,'UTF8_LF_JSON_whitespace_passed':True})
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R044','session':'20261017-2109','started_at':'2026-10-18T05:14:06.207583+08:00','frozen_at':at,'deadline':'2026-10-18T05:21:06+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','root_candidate_required_changes':0,'status':'independent conditional mass-participation corollary frozen before author comparison','author_candidate_reviewed':False,'accepted_scope':'Exact mass fraction / port projection and geometric reconstruction error lower bounds at the already certified C027/C028 true witness only, with unchanged full model/machine contracts. No fixed-u1 universal bound, new mechanism, actual FNA/ETABS/300-mode or engineering admission.','source_records_verified':6,'frozen_prior_records_verified':43,'frozen_prior_small_outputs_verified':174,'frozen_R001_R043':old,'additional_postcomparison_freezes':extra,'additional_postcomparison_outputs_verified':6,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'sources':6,'old_records':43,'old_outputs':174,'new_outputs':len(outputs),'report':rec(HERE/'report.md'),'checks':rec(HERE/'checks.json'),'validation':rec(HERE/'validation.json')},ensure_ascii=False))
