"""Freeze the independent answer before any new author candidate is read."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();ROLE=ROOT/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004';HERE=Path(__file__).resolve().parent
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources']
assert len(sources)==5 and all(record(Path(s['path']))==s for s in sources)
assert read(HERE/'checks.json')['all_passed'] and not read(HERE/'checks.json')['new_role1_candidate_read']
prior_path=ROLE/'R039-finite-observation-neighbor-review/validation.json'
assert record(prior_path)['sha256']=='2a5017b5d6cfef3671a6db46754e364dd98898eb8532d2dec19efaeff37b1708'
prior=read(prior_path)
old=prior['frozen_R001_R038']+[{'run_file':str(prior_path.relative_to(ROLE)).replace('\\','/'),'sha256':record(prior_path)['sha256'],'outputs_verified':len(prior['outputs'])}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outputs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outputs)==item['outputs_verified']
    for out in outputs:assert record(Path(out['path']))==out
    total+=len(outputs)
assert len(old)==39 and total==146
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n')
    s=b.decode('utf-8');assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T04:36:58+08:00'
write('closure_checks.json',{'at':at,'root_candidate_mathematical_required_changes':0,'new_role1_candidate_read_before_freeze':False,'source_records_verified':5,'all_sources_unchanged':True,'old_records_verified':39,'old_small_outputs_verified':146,'all_old_SHA_unchanged':True,'tiny_Fraction_checks_passed':True,'UTF8_LF_JSON_whitespace_passed':True,'no_new_author_verdict_yet':True,'no_trajectory_array_parameter_sweep_or_external_search':True})
outputs=[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R040','session':'20261017-2109','started_at':'2026-10-18T04:26:58+08:00','frozen_at':at,'deadline':'2026-10-18T04:36:58+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','status':'independent conditional solution frozen before author comparison','root_candidate_required_changes':0,'author_candidate_reviewed':False,'accepted_scope':'Classical exact fixed-D peak interval inverse of already audited M-C018, with restricted inverse domains and minimum-time singleton; original measurable bounded velocity/free terminal delta conditions remain. No novelty or engineering admission.','source_records_verified':len(sources),'frozen_prior_records_verified':39,'frozen_prior_small_outputs_verified':146,'frozen_R001_R039':old,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'sources':len(sources),'prior_records':39,'prior_outputs':146,'new_outputs':len(outputs),'report':record(HERE/'report.md'),'checks':record(HERE/'checks.json'),'validation':record(HERE/'validation.json')},ensure_ascii=False))
