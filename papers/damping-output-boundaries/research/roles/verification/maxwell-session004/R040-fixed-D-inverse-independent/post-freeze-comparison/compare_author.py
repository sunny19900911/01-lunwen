"""Identity/format closure for manual static comparison, no numeric rerun."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;PARENT=HERE.parent
ROLE=PARENT.parent;AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R029-fixed-dissipation-peak-inverse'
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'comparison-freeze.json').exists()
assert rec(AUTHOR/'report.md')['sha256']=='c6cc612de443a58642a20d7cdb10a054fb00d051d827a33f2f44b1ac0fcdc910'
assert rec(PARENT/'validation.json')['sha256']=='7afa29be7d15d5deb0ce02eddee95b4b09e664f6de7d2cdba22b0c69d72c7a29'
own=read(PARENT/'validation.json')
for out in own['outputs']:assert rec(Path(out['path']))==out
assert len(own['outputs'])==8
assert all(rec(Path(s['path']))==s for s in read(PARENT/'source-freeze.json')['sources'])
total=0
for item in own['frozen_R001_R039']:
    p=ROLE/item['run_file'];assert rec(p)['sha256']==item['sha256']
    d=read(p);outputs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outputs)==item['outputs_verified']
    for out in outputs:assert rec(Path(out['path']))==out
    total+=len(outputs)
assert total==146
for x in read(AUTHOR/'artifact-manifest.json')['artifacts']:
    r=rec(AUTHOR/x['file']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
for x in read(AUTHOR/'source-freeze.json')['sources']:
    r=rec(ROOT/x['path']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T04:36:58+08:00'
write('comparison.json',{'at':at,'required_changes':0,'mathematically_equivalent':True,'first_author_report_read_at':'2026-10-18T04:32:50+08:00','independent_freeze_precedes_author_first_read':True,'independent_validation':rec(PARENT/'validation.json'),'author_small_sources':[rec(p) for p in sorted(AUTHOR.iterdir()) if p.is_file()],'all_author_manifest_and_source_SHA_verified':True,'original_R040_eight_outputs_unchanged':True,'old_39_records_146_outputs_unchanged':True,'symbol_mapping':{'independent_D0':'author_D_min = L(h)','independent_Dh':'author_D0 = U(h)','independent_DT':'author_D_max = L(M_T) = U(M_T)'},'numeric_rerun':False,'scope':'Static finite comparison only; no arrays, trajectories, parameter sweep, external search, old/shared/manuscript/Git writes.'})
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');s=b.decode('utf-8')
    assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='comparison-freeze.json']
write('comparison-freeze.json',{'frozen_at':at,'deadline':'2026-10-18T04:36:58+08:00','required_changes':0,'comparison_completed':True,'original_independent_R040_validation':rec(PARENT/'validation.json'),'original_R040_outputs_verified':8,'prior_39_small_outputs_verified':146,'outputs':outputs})
print(json.dumps({'required_changes':0,'comparison_report':rec(HERE/'report.md'),'comparison_record':rec(HERE/'comparison.json'),'freeze':rec(HERE/'comparison-freeze.json')},ensure_ascii=False))
