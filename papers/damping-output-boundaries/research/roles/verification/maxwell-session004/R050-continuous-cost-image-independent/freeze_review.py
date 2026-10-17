"""R050 finite text metadata only; no author program, scientific data, or ODE."""
from pathlib import Path
from datetime import datetime
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[6]
S='research/sessions/20261017-2109/'
R='papers/damping-output-boundaries/research/roles/verification/maxwell-session004/R048-continuous-velocity-independent/'
START='2026-10-18T06:24:37.286329+08:00'
DEADLINE='2026-10-18T06:32:37.286329+08:00'
ITEMS=[
    (S+'continuous-velocity-cost-image-protocol-v001.md','current full protocol text'),
    (S+'C042-adoption-v001.json','current complete adoption metadata; cited source list not recursively read'),
    (R+'report.md','current full old independent proof; C042 endpoint and continuity lemmas reused, not re-proved'),
    (R+'validation.json','current complete identity metadata'),
]

def rec(p):
    data=(ROOT/p).read_bytes()
    data.decode('utf-8')
    return {'path':p,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def put(n,obj):
    (OUT/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

sources=[dict(rec(p),read_level=level) for p,level in ITEMS]
adoption=json.loads((ROOT/(S+'C042-adoption-v001.json')).read_text(encoding='utf-8'))
assert adoption['claim']=='M-C042' and adoption['status']=='supported' and adoption['review']=='reviewed'
for p,level in ITEMS:
    if p in adoption['checked_identities']:
        assert rec(p)['sha256']==adoption['checked_identities'][p]
assert rec(R+'report.md')['sha256']=='fb2868540d569662bf991a1147ff26f98b8022aae2c6d0730c66f4bf68287312'
assert rec(R+'validation.json')['sha256']=='92de4674a3f5e1bd32c115f9f6d5374f1f1fb7160abc183816c921ffe04be19e'
put('source-freeze.json',{'started_at':START,'sources':sources,'finite_identity_count':4,
    'new_R035_or_root_candidate_read':False,'recursive_history_scan':False})
checks=json.loads((OUT/'closure_checks.json').read_text(encoding='utf-8'))
assert checks['logical_gaps_found']==0
for name in ['report.md','closure_checks.json']:
    data=(OUT/name).read_bytes()
    txt=data.decode('utf-8')
    assert '\r' not in txt and not any(line.rstrip()!=line for line in txt.splitlines())
for source in sources:
    assert rec(source['path'])=={k:source[k] for k in ('path','bytes','sha256')}
frozen=datetime.now().astimezone().isoformat()
assert datetime.fromisoformat(frozen)<=datetime.fromisoformat(DEADLINE)
put('validation.json',{'round':'R050','started_at':START,'frozen_at':frozen,'limit_seconds':480,
    'task_deadline':DEADLINE,'within_limit':True,'global_deadline':'2026-10-18T07:09:45+08:00',
    'finite_sources_unchanged':True,'finite_identity_count':4,
    'independent_before_official_author_comparison':True,
    'conclusion':'Full cost image is (Dmin,Dmax) for T>tmin; singleton for T=tmin; empty for T<tmin.',
    'math_validation':'symbolic proof; metadata checks are ancillary only',
    'old_shared_manuscript_Git_modified':False,'new_ODE_numerics_or_data_arrays':False,
    'outputs':[rec((OUT/n).relative_to(ROOT).as_posix()) for n in ['report.md','closure_checks.json','freeze_review.py','source-freeze.json']]})
for name in ['source-freeze.json','validation.json']:
    json.loads((OUT/name).read_text(encoding='utf-8'))
print(json.dumps({'frozen_at':frozen,'report':rec((OUT/'report.md').relative_to(ROOT).as_posix()),
    'validation':rec((OUT/'validation.json').relative_to(ROOT).as_posix())},ensure_ascii=False,indent=2))
