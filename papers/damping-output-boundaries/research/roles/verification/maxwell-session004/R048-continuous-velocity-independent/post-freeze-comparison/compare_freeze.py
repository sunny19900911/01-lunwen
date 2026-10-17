from pathlib import Path
from datetime import datetime
import hashlib
import json

OUT = Path(__file__).resolve().parent
OWN = OUT.parent
ROOT = OWN.parents[6]
AUTHOR = ROOT / 'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R034-continuous-velocity-endpoints'
START = '2026-10-18T05:53:29.349391+08:00'
DEADLINE = '2026-10-18T05:54:59.349391+08:00'

def rec(p):
    b=p.read_bytes()
    b.decode('utf-8')
    return {'path':p.relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def put(n,x):
    (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

author=[rec(AUTHOR/n) for n in ['report.md','artifact-manifest.json','validation.json']]
assert author[0]['sha256']=='f1fcbbb2f3e97c058b7e81c067f30b502520ccbd864140673668708af52dbe11'
assert author[1]['sha256']=='094ca1682aee6987027713c624484a299ca6fa34612f6073e643d52d6aa942e1'
manifest=json.loads((AUTHOR/'artifact-manifest.json').read_text(encoding='utf-8'))
for item in author[::2]:
    entry=next(x for x in manifest['files'] if x['path']==Path(item['path']).name)
    assert entry['sha256']==item['sha256'] and entry['bytes']==item['bytes']
json.loads((AUTHOR/'validation.json').read_text(encoding='utf-8'))
ownvalidation=json.loads((OWN/'validation.json').read_text(encoding='utf-8'))
own=[]
for old in ownvalidation['outputs']:
    current=rec(ROOT/old['path'])
    assert current==old
    own.append(current)
own.append(rec(OWN/'validation.json'))
assert own[-1]['sha256']=='92de4674a3f5e1bd32c115f9f6d5374f1f1fb7160abc183816c921ffe04be19e'
sources=json.loads((OWN/'source-freeze.json').read_text(encoding='utf-8'))['sources']
for old in sources:
    assert rec(ROOT/old['path'])==old
put('comparison_checks.json',{'author':author,'original_R048':own,'specified_sources_unchanged':sources,
    'manual_symbolic_comparison':{'signed_Psi_identity_and_rigidity':'consistent','upper_time_equality':'consistent','lower_exact_terminal_ramp':'consistent','upper_exact_terminal_ramp':'consistent','L1_and_cost_constants':'consistent; tighter bound is compatible','degeneracy_and_scope':'consistent'},
    'new_required_changes':0,'mathematical_conflicts':0,'root_candidate_read':False,'old_history_scanned':False,'new_ODE_or_numerics':False})
frozen=datetime.now().astimezone().isoformat()
assert datetime.fromisoformat(frozen)<=datetime.fromisoformat(DEADLINE)
put('validation.json',{'started_at':START,'limit_seconds':90,'deadline':DEADLINE,'frozen_at':frozen,
    'within_limit':True,'original_R048_and_author_unchanged':True,'global_deadline':'2026-10-18T07:09:45+08:00',
    'outputs':[rec(OUT/n) for n in ['report.md','compare_freeze.py','comparison_checks.json']]})
for n in ['comparison_checks.json','validation.json']:
    json.loads((OUT/n).read_text(encoding='utf-8'))
print(json.dumps({'frozen_at':frozen,'report':rec(OUT/'report.md'),'validation':rec(OUT/'validation.json')},ensure_ascii=False,indent=2))
