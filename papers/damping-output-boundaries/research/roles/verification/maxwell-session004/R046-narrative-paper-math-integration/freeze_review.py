"""Freeze focused review including its required correction, without source edits."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources'];assert len(sources)==15 and all(rec(Path(x['path']))==x for x in sources)
findings=read(HERE/'findings.json');assert findings['required_changes']==1 and findings['formula_changes_required']==0
assert read(HERE/'checks.json')['static_pass_does_not_override_mathematical_finding']
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');s=b.decode('utf-8');assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T05:41:14+08:00'
write('closure_checks.json',{'at':at,'required_changes':1,'formula_changes_required':0,'all_fifteen_sources_unchanged':True,'focused_static_QA_passed':True,'narrative_integration_acceptance':'Terminology revision required; conditional formulas otherwise checked.','old_180_packages_scanned':False,'new_proof_ODE_arrays_data_or_author_execution':False,'manuscript_source_shared_Git_writes':False,'before_seven_minute_deadline':True})
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R046','session':'20261017-2109','started_at':'2026-10-18T05:34:14.620466+08:00','frozen_at':at,'deadline':'2026-10-18T05:41:14+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','status':'one mathematical-terminology correction required; formulas otherwise pass focused integration review','required_changes':1,'formula_changes_required':0,'required_finding_id':'R046-M1','accepted_scope':'Ten formulas, device admissible class and full interval construction, C039 structural conditions and C025 conditional numerical inheritance only. Engineering table and contribution/primary-source reviews excluded.','source_records_verified':15,'sources_unchanged':True,'all_prior_history_rescanned':False,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':1,'formula_changes_required':0,'frozen_at':at,'sources':15,'new_outputs':len(outputs),'report':rec(HERE/'report.md'),'findings':rec(HERE/'findings.json'),'validation':rec(HERE/'validation.json')},ensure_ascii=False))
