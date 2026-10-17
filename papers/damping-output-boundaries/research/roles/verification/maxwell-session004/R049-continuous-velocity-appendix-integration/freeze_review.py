"""Finite text identities and static QA only; does not execute author programs."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[6]
P='papers/damping-output-boundaries/'
V=P+'research/roles/verification/maxwell-session004/'
A=P+'research/roles/ideation/maxwell-session004/R034-continuous-velocity-endpoints/'
W=P+'research/roles/writing/maxwell-session004/continuous-velocity-endpoints-v001/'
R=V+'R048-continuous-velocity-independent/'
APP=P+'manuscript/maxwell-continuous-velocity-endpoints-v001.md'
ADOPT='research/sessions/20261017-2109/C042-adoption-v001.json'
START='2026-10-18T06:02:19.427055+08:00'
DEADLINE='2026-10-18T06:08:19.427055+08:00'
ITEMS=[
    (APP,'current full text'),(W+'freeze.json','current complete metadata'),
    (ADOPT,'current complete adoption metadata'),
    (A+'report.md','previous full text; current identity only'),
    (A+'artifact-manifest.json','previous full metadata; current identity only'),
    (A+'validation.json','previous full metadata; current identity only'),
    (R+'report.md','current full text'),(R+'validation.json','current complete metadata'),
    (R+'post-freeze-comparison/report.md','current full text'),
    (R+'post-freeze-comparison/validation.json','previous full metadata; current identity only'),
    (V+'非零末力耗散峰力区间独审-R017.md','earlier reviewed full text; current identity only'),
    (P+'manuscript/maxwell-fixed-dissipation-peak-appendix-v002.md','earlier reviewed full text; current identity only'),
]

def rec(path):
    b=(ROOT/path).read_bytes()
    b.decode('utf-8')
    return {'path':path,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def put(n,obj):
    (OUT/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

sources=[dict(rec(p),read_level=level) for p,level in ITEMS]
by_path={x['path']:x for x in sources}
assert by_path[APP]['sha256']=='3de22587466e7546385db5c8109e1ab855fc8124c053e183c50f90e5925cf47f'
assert by_path[W+'freeze.json']['sha256']=='84618b3c04f6e48985670f29f7070c9c646b73b01bcab80bbc86f32689d9e4ba'
adoption=json.loads((ROOT/ADOPT).read_text(encoding='utf-8'))
assert adoption['claim']=='M-C042' and adoption['status']=='supported' and adoption['review']=='reviewed'
for p,level in ITEMS:
    if p in adoption['checked_identities']:
        assert by_path[p]['sha256']==adoption['checked_identities'][p],p
author_freeze=json.loads((ROOT/(W+'freeze.json')).read_text(encoding='utf-8'))
entry=next(x for x in author_freeze['files'] if x['path'].replace('\\','/').endswith('/'+Path(APP).name))
assert entry['bytes']==by_path[APP]['bytes'] and entry['sha256']==by_path[APP]['sha256']
put('source-freeze.json',{'started_at':START,'sources':sources,'identity_count':len(sources),
    'recursive_history_verification':False,'author_programs_read_or_run':False})
text=(ROOT/APP).read_text(encoding='utf-8')
tags=re.findall(r'\\tag\{(\d+)\}',text)
sections=re.findall(r'^## [1-4] ',text,re.M)
assert tags==['1','2','3','4','5','6'] and len(sections)==4
assert '\r' not in text and not any(line.rstrip()!=line for line in text.splitlines())
links=re.findall(r'\]\(([^)]+)\)',text)
for link in links:
    assert ((ROOT/APP).parent/link).resolve().is_file(),link
for p,level in ITEMS:
    assert rec(p)=={k:by_path[p][k] for k in ('path','bytes','sha256')}
json.loads((OUT/'findings.json').read_text(encoding='utf-8'))
frozen=datetime.now().astimezone().isoformat()
assert datetime.fromisoformat(frozen)<=datetime.fromisoformat(DEADLINE)
put('validation.json',{'round':'R049','started_at':START,'limit_seconds':360,'task_deadline':DEADLINE,
    'frozen_at':frozen,'within_limit':True,'global_deadline':'2026-10-18T07:09:45+08:00',
    'finite_source_identities':len(sources),'finite_sources_unchanged':True,
    'static_QA':{'sections':len(sections),'equation_tags':tags,'links_exist':len(links),'utf8_lf':True,'trailing_whitespace':False},
    'math_review':'manual mathematical integration; static QA is only ancillary',
    'must_fix_count':0,'new_ODE_numerics_arrays_sources':False,'old_shared_manuscript_Git_modified':False,
    'outputs':[rec((OUT/n).relative_to(ROOT).as_posix()) for n in ['report.md','findings.json','freeze_review.py','source-freeze.json']]})
json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
print(json.dumps({'frozen_at':frozen,'report':rec((OUT/'report.md').relative_to(ROOT).as_posix()),
    'validation':rec((OUT/'validation.json').relative_to(ROOT).as_posix())},ensure_ascii=False,indent=2))
