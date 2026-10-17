"""Small identity closure of static comparison; no numerical rerun."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;PARENT=HERE.parent;ROLE=PARENT.parent
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R030-dissipation-modal-output-bound'
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'comparison-freeze.json').exists()
assert rec(AUTHOR/'report.md')['sha256']=='78722bbbd78ffd8e3ad725cfec16648997d1548ab7e505754a7997733f45c288'
assert rec(PARENT/'validation.json')['sha256']=='e7aa95c6c3980998ab2975e1fcffbe91ffdeee83995a3eb84666005e90d840cd'
own=read(PARENT/'validation.json');assert len(own['outputs'])==5
assert all(rec(Path(x['path']))==x for x in own['outputs'])
assert all(rec(Path(x['path']))==x for x in read(PARENT/'source-freeze.json')['sources'])
for x in read(AUTHOR/'artifact-manifest.json')['artifacts']:
    actual=rec(AUTHOR/x['file']);assert actual['bytes']==x['bytes'] and actual['sha256']==x['sha256']
total=0
for x in own['frozen_R001_R041']:
    p=ROLE/x['run_file'];assert rec(p)['sha256']==x['sha256'];d=read(p)
    outs=d.get('outputs',[d['report']] if 'report' in d else []);assert len(outs)==x['outputs_verified']
    assert all(rec(Path(y['path']))==y for y in outs);total+=len(outs)
assert total==161
extra=own['additional_R040_postcomparison_freeze'];assert rec(Path(extra['path']))==extra
assert all(rec(Path(x['path']))==x for x in read(Path(extra['path']))['outputs'])
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T04:59:37+08:00'
write('comparison.json',{'at':at,'first_author_report_read_at':'2026-10-18T04:57:38+08:00','required_changes':0,'mathematically_equivalent':True,'continuous_displacement_Linfinity_equals_finite_window_sup':True,'author_static_residual_counterexample_valid':True,'author_sources':[rec(AUTHOR/n) for n in ['report.md','artifact-manifest.json','validation.json']],'author_six_manifest_outputs_verified':True,'original_independent_five_outputs_and_sources_unchanged':True,'old_41_records_161_outputs_and_R040_extra_unchanged':True,'new_proof_numeric_arrays_ODE_or_source_MIT_read':False})
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');s=b.decode('utf-8');assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
write('comparison-freeze.json',{'at':at,'deadline':'2026-10-18T04:59:37+08:00','required_changes':0,'original_independent_validation':rec(PARENT/'validation.json'),'outputs':[rec(p) for p in sorted(HERE.iterdir()) if p.is_file()]})
print(json.dumps({'required_changes':0,'report':rec(HERE/'report.md'),'record':rec(HERE/'comparison.json'),'freeze':rec(HERE/'comparison-freeze.json')},ensure_ascii=False))
