"""Identity and format closure only. No numerical or author-candidate access."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources'];assert len(sources)==5 and all(rec(Path(x['path']))==x for x in sources)
prior_path=ROLE/'R041-fixed-D-appendix-integration/validation.json'
assert rec(prior_path)['sha256']=='37e86200be88f9ec01db54da96caf17023c1c259ede4c52cf8ebc7881105f69a'
prior=read(prior_path)
old=prior['frozen_R001_R040']+[{'run_file':str(prior_path.relative_to(ROLE)).replace('\\','/'),'sha256':rec(prior_path)['sha256'],'outputs_verified':len(prior['outputs'])}]
total=0
for x in old:
    p=ROLE/x['run_file'];assert rec(p)['sha256']==x['sha256'];d=read(p)
    outputs=d.get('outputs',[d['report']] if 'report' in d else []);assert len(outputs)==x['outputs_verified']
    assert all(rec(Path(y['path']))==y for y in outputs);total+=len(outputs)
assert len(old)==41 and total==161
extra=prior['additional_R040_postcomparison_freeze'];assert rec(Path(extra['path']))==extra
assert all(rec(Path(x['path']))==x for x in read(Path(extra['path']))['outputs'])
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');text=b.decode('utf-8')
    assert all(x==x.rstrip() for x in text.splitlines())
    if p.suffix=='.json':json.loads(text)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T04:59:37+08:00'
write('closure_checks.json',{'at':at,'protocol_required_changes':0,'independent_symbolic_derivation':True,'p_q_conjugacy_force_norm_weights_units_reviewed':True,'same_alpha_cross_device_Holder_reviewed':True,'physical_kernel_and_full_force_pairing_reviewed':True,'initial_state_missing_terms_infinite_tail_acceleration_boundaries_reviewed':True,'new_author_candidate_read':False,'source_SHA_unchanged':True,'prior_records_verified':41,'prior_outputs_verified':161,'R040_postcomparison_outputs_verified':3,'numeric_arrays_ODE_sweep_search_or_new_fulltext':False,'UTF8_LF_JSON_whitespace_passed':True})
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R042','session':'20261017-2109','started_at':'2026-10-18T04:51:37.185518+08:00','frozen_at':at,'deadline':'2026-10-18T04:59:37+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','root_candidate_required_changes':0,'status':'independent conditional Holder consequence frozen before author comparison','author_candidate_reviewed':False,'accepted_scope':'True dissipation to force Lp and finite-window complete-physical-Green displacement-difference Holder bounds, optional common-alpha total-energy bound, same-window peak error band only. Classical tools; no novelty, prediction or engineering admission.','source_records_verified':5,'frozen_prior_records_verified':41,'frozen_prior_small_outputs_verified':161,'frozen_R001_R041':old,'additional_R040_postcomparison_freeze':extra,'additional_R040_postcomparison_outputs_verified':3,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'sources':len(sources),'old_records':41,'old_outputs':161,'new_outputs':len(outputs),'report':rec(HERE/'report.md'),'checks':rec(HERE/'closure_checks.json'),'validation':rec(HERE/'validation.json')},ensure_ascii=False))
