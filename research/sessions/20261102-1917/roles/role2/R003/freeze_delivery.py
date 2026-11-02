from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inp=json.loads((O/'input-freeze.json').read_text(encoding='utf-8'))
for d in inp['files']:
    p=Path(d['path']);assert p.stat().st_size==d['bytes'] and sha(p)==d['sha256']
c=json.loads((O/'finite-text-table-checks.json').read_text(encoding='utf-8'))
assert c['numeric_display_checks']==502 and c['representative_control_rows']==8 and c['appendix_control_rows']==48
t=(O/'final-content-review.md').read_text(encoding='utf-8');assert '�' not in t
width=None
for line in t.splitlines():
    if line.startswith('|'):
        n=len(line.strip('|').split('|'))
        if width is None:width=n
        assert n==width,line
    else:width=None
now=datetime.now(timezone(timedelta(hours=8)));start=datetime.fromisoformat(inp['actual_start'])
out={'task':'session022-role2-R003','actual_start':start.isoformat(),'actual_freeze':now.isoformat(),
 'elapsed_seconds':(now-start).total_seconds(),'within8min':(now-start).total_seconds()<=480,
 'within10min':(now-start).total_seconds()<=600,'must':0,'should':0,'optional':0,'replacement_sentences_required':False,
 'full_main_lines_read':237,'full_appendix_lines_read':130,'finite_display_checks':502,
 'author_inputs_unchanged':True,'new_scientific_production_or_search':False,'raw_arrays_read':False,
 'no_repeat_R002_full_audit':True,'post_freeze_coordination':'one result message to controller only; idle',
 'fixed_session_deadline':'2026-11-02T21:47:23+08:00',
 'files':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']}
with (O/'delivery-manifest.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in out.items() if k!='files'},ensure_ascii=False,indent=2));print('manifest_sha256',sha(O/'delivery-manifest.json'))
