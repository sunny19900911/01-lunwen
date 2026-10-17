from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;PARENT=HERE.parent
A=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R033-input-budget-dissipation-corollary'
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'comparison-freeze.json').exists()
assert rec(A/'report.md')['sha256']=='d2cc1282f84395d8087d534fc19f6322f02d65800b5410c3344b152f171eec27'
assert rec(PARENT/'validation.json')['sha256']=='1e25a33653299179d08549313547f659e636689aab53c0da7a8a0a16e1377848'
assert all(rec(Path(x['path']))==x for x in read(PARENT/'validation.json')['outputs'])
assert all(rec(Path(x['path']))==x for x in read(PARENT/'source-freeze.json')['sources'])
m=read(A/'artifact-manifest.json')
for name in ['report.md','validation.json']:
    x=next(x for x in m['artifacts'] if x['file']==name);actual=rec(A/name)
    assert actual['bytes']==x['bytes'] and actual['sha256']==x['sha256']
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T05:33:50+08:00'
write('comparison.json',{'at':at,'started_at':'2026-10-18T05:32:20.624003+08:00','required_changes':0,'mathematically_equivalent':True,'J_not_assumed_monotone_and_E_only_not_used_for_D':True,'Range_zero_regularization_and_redundancy_limits_passed':True,'own_five_outputs_nine_sources_unchanged':True,'old_180_packages_rescanned':False,'author_only_report_manifest_validation_accessed':True,'author_records':[rec(A/n) for n in ['report.md','artifact-manifest.json','validation.json']],'new_proof_numeric_or_data_runs':False})
write('comparison-freeze.json',{'at':at,'deadline':'2026-10-18T05:33:50+08:00','required_changes':0,'independent_validation':rec(PARENT/'validation.json'),'outputs':[rec(p) for p in sorted(HERE.iterdir()) if p.is_file()]})
print(json.dumps({'required_changes':0,'frozen_at':at,'report':rec(HERE/'report.md'),'record':rec(HERE/'comparison.json'),'freeze':rec(HERE/'comparison-freeze.json')},ensure_ascii=False))
