"""R051 finite text identities/static QA; no author program or history scan."""
from pathlib import Path
from datetime import datetime
import hashlib,json,re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[6]
P='papers/damping-output-boundaries/'
R=P+'research/roles/verification/maxwell-session004/R050-continuous-cost-image-independent/'
W=P+'research/roles/writing/maxwell-session004/continuous-cost-image-v001/'
APP=P+'manuscript/maxwell-continuous-cost-image-v001.md'
ADOPT='research/sessions/20261017-2109/C043-adoption-v001.json'
START='2026-10-18T06:35:06.219497+08:00'
DEADLINE='2026-10-18T06:39:06.219497+08:00'
ITEMS=[(APP,'current full supplement text'),(W+'freeze.json','current complete freeze metadata; other listed files not recursively read'),
    (ADOPT,'current complete adoption metadata; history not recursively read'),
    (R+'report.md','current full old independent proof'),(R+'validation.json','current complete identity metadata'),
    (R+'post-freeze-comparison/report.md','current full old comparison report'),
    (R+'post-freeze-comparison/validation.json','current complete identity metadata')]

def rec(p):
    b=(ROOT/p).read_bytes();b.decode('utf-8')
    return {'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def put(n,obj):
    (OUT/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

sources=[dict(rec(p),read_level=level) for p,level in ITEMS]
by_path={x['path']:x for x in sources}
assert by_path[APP]['sha256']=='23acaade3bf7b6916f526a9182e7c669368e8888fec966d951ea601cd5173734'
assert by_path[W+'freeze.json']['sha256']=='30067f5395bb99218baad4b4e352dfd29f352032b64ef80e8be8b7ee5669434f'
adoption=json.loads((ROOT/ADOPT).read_text(encoding='utf-8'))
assert adoption['claim']=='M-C043' and adoption['status']=='supported' and adoption['review']=='reviewed'
matched=0
for p,level in ITEMS:
    if p in adoption['checked_identities']:
        assert by_path[p]['sha256']==adoption['checked_identities'][p]
        matched+=1
assert matched==4
writer=json.loads((ROOT/(W+'freeze.json')).read_text(encoding='utf-8'))
entry=next(x for x in writer['files'] if x['path'].replace('\\','/').endswith('/'+Path(APP).name))
assert entry['sha256']==by_path[APP]['sha256'] and entry['bytes']==by_path[APP]['bytes']
put('source-freeze.json',{'started_at':START,'sources':sources,'finite_identity_count':7,'adoption_identities_matched':matched,
    'author_programs_or_historical_source_list_read':False})
text=(ROOT/APP).read_text(encoding='utf-8')
sections=re.findall(r'^## [1-4] ',text,re.M)
tags=re.findall(r'\\tag\{(\d+)\}',text)
assert len(sections)==4 and tags==['1','2','3','4','5']
assert '\r' not in text and not any(line.rstrip()!=line for line in text.splitlines())
links=re.findall(r'\]\(([^)]+)\)',text)
assert len(links)==4
for link in links:
    assert ((ROOT/APP).parent/link).resolve().is_file(),link
report=(OUT/'report.md').read_text(encoding='utf-8')
table=[line for line in report.splitlines() if line.startswith('|')]
assert len(table)==8 and all(line.count('|')==4 for line in table)
assert all('||' not in line for line in table)
for source in sources:
    assert rec(source['path'])=={k:source[k] for k in ('path','bytes','sha256')}
json.loads((OUT/'findings.json').read_text(encoding='utf-8'))
frozen=datetime.now().astimezone().isoformat()
assert datetime.fromisoformat(frozen)<=datetime.fromisoformat(DEADLINE)
put('validation.json',{'round':'R051','started_at':START,'limit_seconds':240,'task_deadline':DEADLINE,'frozen_at':frozen,
    'within_limit':True,'global_deadline':'2026-10-18T07:09:45+08:00','finite_sources_unchanged':True,
    'finite_identity_count':7,'adoption_identities_matched':matched,'must_fix_count':0,
    'math_review':'manual transcription and scope integration; static QA ancillary only',
    'static_QA':{'sections':len(sections),'equation_tags':tags,'local_links_exist':len(links),'utf8_LF':True,'report_table_columns':3,'table_norm_Unicode':True},
    'new_proof_ODE_numerics_data_arrays':False,'old_shared_manuscript_Git_modified':False,
    'outputs':[rec((OUT/n).relative_to(ROOT).as_posix()) for n in ['report.md','findings.json','freeze_review.py','source-freeze.json']]})
json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
print(json.dumps({'frozen_at':frozen,'report':rec((OUT/'report.md').relative_to(ROOT).as_posix()),
    'validation':rec((OUT/'validation.json').relative_to(ROOT).as_posix())},ensure_ascii=False,indent=2))
