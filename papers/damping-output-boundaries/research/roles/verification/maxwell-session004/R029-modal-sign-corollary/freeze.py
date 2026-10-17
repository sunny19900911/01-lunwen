"""Read-only prior/source integrity verification and local R029 manifest."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')
assert all(record(Path(x['path']))==x for x in sources)
r28=ROLE/'R028/R028-review-validation.json'
assert record(r28)['sha256']=='3d1e8b8fc71457f14015c4cb980f31bb97f45e488be592c96e667e1481f8348d'
old=read(r28)['frozen_R001_R027']+[{'run_file':'R028/R028-review-validation.json','sha256':record(r28)['sha256'],'outputs_verified':2}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==28 and total==82
e28=read(ROLE/'R028/R028-proof-evidence.json')
for x in e28['artifacts']:assert record(Path(x['path']))==x
for x in e28['source_records']:assert record(Path(x['path']))==x
c=read(HERE/'checks.json');assert c['all_candidate_thresholds_passed']
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T02:38:40+08:00'
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();text=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b,p
        assert all(line==line.rstrip() for line in text.splitlines()),p
out={'review':'R029','session':'20261017-2109','started_at':'2026-10-18T02:30:40+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T02:38:40+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'candidate_thresholds_all_passed':True,'accepted_scope':'Conditional C027 fixed-J bare-modal signs/superposition and exact continuous cumulative device-work corollary; original certificate machine/model/data contracts inherited.',
 'source_records_verified':len(sources),'sources_unchanged':True,'frozen_prior_records_verified':28,'frozen_prior_outputs_verified':82,'R028_supplementary_artifacts_and_original_source_records_unchanged':True,'frozen_R001_R028':old,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'Error ellipsoid, modal equations/force signs and strict true-work inequalities','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Independent Fraction node/threshold checks with rational sqrt2/sqrt3 bounds','required_changes':0},{'agent':'audit_double_mode','scope':'Independent full-state-radius and passive modal energy argument challenge','required_changes':0}],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_or_trailing_whitespace':True,'no_16529_replay_ODE_or_real_engineering_read':True,'no_numerical_work_quadrature':True,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'prior_records':28,'prior_outputs':82,'sources':len(sources),'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
