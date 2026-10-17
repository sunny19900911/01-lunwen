"""Metadata/format closure of a symbolic reuse audit; no scientific computation."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources'];assert len(sources)==9 and all(rec(Path(x['path']))==x for x in sources)
prior_path=ROLE/'R044-mass-participation-independent/validation.json'
assert rec(prior_path)['sha256']=='252e903ce853260691973d6d3949098b23861f66d6269d56b114b70baf9ae2f0'
prior=read(prior_path)
old=prior['frozen_R001_R043']+[{'run_file':str(prior_path.relative_to(ROLE)).replace('\\','/'),'sha256':rec(prior_path)['sha256'],'outputs_verified':len(prior['outputs'])}]
total=0
for x in old:
    p=ROLE/x['run_file'];assert rec(p)['sha256']==x['sha256'];d=read(p)
    outputs=d.get('outputs',[d['report']] if 'report' in d else []);assert len(outputs)==x['outputs_verified']
    assert all(rec(Path(y['path']))==y for y in outputs);total+=len(outputs)
assert len(old)==44 and total==180
extra=prior['additional_postcomparison_freezes']+[rec(ROLE/'R044-mass-participation-independent/post-freeze-comparison/comparison-freeze.json')]
assert extra[-1]['sha256']=='9efefae63b2298d2428f41f008884cc094fbc452d0e25d039e4aeb70211e6b87'
for x in extra:assert rec(Path(x['path']))==x and all(rec(Path(y['path']))==y for y in read(Path(x['path']))['outputs'])
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');s=b.decode('utf-8');assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T05:33:50+08:00'
write('closure_checks.json',{'at':at,'root_candidate_required_changes':0,'review_type':'Pure symbolic reuse and composition, no numeric test','J_joint_budget_and_L1_zero_regularization_checked':True,'C_pseudoinverse_Range_gate_checked':True,'complete_E0_support_work_and_physical_operator_checked':True,'C039_substitution_and_redundancy_checked':True,'old_tools_reused_not_claimed_new':True,'new_counterparty_package_read':False,'nine_sources_unchanged':True,'prior_records_verified':44,'prior_outputs_verified':180,'additional_postcomparison_outputs_verified':9,'no_arrays_ODE_data_numerical_examples_or_search':True,'UTF8_LF_JSON_whitespace_passed':True})
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R045','session':'20261017-2109','started_at':'2026-10-18T05:26:02.880167+08:00','protocol_started_at':'2026-10-18T05:25:50.718195+08:00','frozen_at':at,'conservative_deadline':'2026-10-18T05:33:50+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','root_candidate_required_changes':0,'status':'independent classical input-budget corollary frozen before author comparison','author_candidate_reviewed':False,'accepted_scope':'Joint E+Dtot L2/Range and L1 budgets with complete E0, conditional C039 substitution, direct versus reference-plus-error minimum with explicit redundancy. Old tools reused; no novelty/engineering or layout-order admission.','source_records_verified':9,'frozen_prior_records_verified':44,'frozen_prior_small_outputs_verified':180,'frozen_R001_R044':old,'additional_postcomparison_freezes':extra,'additional_postcomparison_outputs_verified':9,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'sources':9,'old_records':44,'old_outputs':180,'new_outputs':len(outputs),'report':rec(HERE/'report.md'),'checks':rec(HERE/'closure_checks.json'),'validation':rec(HERE/'validation.json')},ensure_ascii=False))
