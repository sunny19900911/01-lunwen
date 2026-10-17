"""Verify only small identities, file format and preserved frozen records."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();ROLE=ROOT/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004';HERE=Path(__file__).resolve().parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources']
assert len(sources)==12 and all(rec(Path(s['path']))==s for s in sources)
assert read(HERE/'checks.json')['all_passed']
prior_path=ROLE/'R038-midpoint-independent-fine-replay/validation.json'
assert rec(prior_path)['sha256']=='bffab13414c3c2013c963c22d2b611243ca29969e80def052a99cb809af9e2e9'
prior=read(prior_path)
old=prior['frozen_R001_R037']+[{'run_file':str(prior_path.relative_to(ROLE)).replace('\\','/'),'sha256':rec(prior_path)['sha256'],'outputs_verified':len(prior['outputs'])}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert rec(p)['sha256']==item['sha256']
    d=read(p);outputs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outputs)==item['outputs_verified']
    for out in outputs:assert rec(Path(out['path']))==out
    total+=len(outputs)
assert len(old)==38 and total==140
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n')
    text=b.decode('utf-8');assert all(line==line.rstrip() for line in text.splitlines())
    if p.suffix=='.json':json.loads(text)
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
assert at<'2026-10-18T04:20:45+08:00'
checks={'at':at,'required_changes':0,'twelve_small_sources_unchanged':True,'prior_records_verified':38,'prior_small_outputs_verified':140,'all_prior_frozen_SHA_unchanged':True,'own_tiny_fraction_checks_passed':True,'UTF8_LF_final_newline_trailing_whitespace_JSON_passed':True,'same_finite_window_gap':'7.459103975104','same_finite_window_estimator_lower_bound':'3.729551987552','scope':'Conditional mathematics only; no trajectories, arrays, NPZ, author execution, external search, Git or shared edits.'}
write('closure_checks.json',checks)
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R039','session':'20261017-2109','started_at':'2026-10-18T04:11:46+08:00','frozen_at':at,'deadline':'2026-10-18T04:20:45+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','required_changes':0,'status':'conditional mathematical audit passed','accepted_scope':'Six finite-observation bounds, same nonzero parameter quantifiers, deterministic bounded-error intersection and two-point lower bound; inherited same-window peak-gap corollary. Original C025/C033 model/arithmetic contracts remain. No novelty or engineering admission.','source_records_verified':len(sources),'sources_unchanged':True,'frozen_prior_records_verified':38,'frozen_prior_small_outputs_verified':140,'frozen_R001_R038':old,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'sources':len(sources),'prior_records':38,'prior_outputs':140,'new_outputs':len(outputs),'report':rec(HERE/'report.md'),'checks':rec(HERE/'checks.json'),'validation':rec(HERE/'validation.json')},ensure_ascii=False))
