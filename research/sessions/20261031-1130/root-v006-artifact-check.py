from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,re,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
p=R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-v006.md'
b=p.read_bytes();txt=b.decode('utf-8')
assert hashlib.sha256(b).hexdigest()=='cb301790edae381adb5da3edde6709f63190de07c434e6906a8bccbad158029e'
links=[]
for href in re.findall(r'\]\(([^)]+)\)',txt):
 q=(p.parent/href).resolve();assert q.is_file()
 links.append(dict(href=href,exists=True,bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest()))
assert len(links)==4 and sum(x['href'].endswith('.png') for x in links)==3
for q in json.loads((S/'roles/role5/R006/manifest.json').read_text())['artifacts']:
 a=Path(q['path']);assert a.stat().st_size==q['bytes'] and hashlib.sha256(a.read_bytes()).hexdigest()==q['sha256']
assert txt.count('$$')==22
out=dict(actual=datetime.now(timezone(timedelta(hours=8))).isoformat(),manuscript_bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),links=links,manifest_hashes_verified=True,display_equations=11,root_read_scope='full manuscript andS1 incl omittedsection5 reread; definitions/counts/same-time-vs-ownpeak/Y andfiguregrouping checked',independent_final_review='role2R010 dispatched13:31, pending; do not claimfinalreview passed',Word_created=False)
(S/'root-v006-artifact-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['actual','manuscript_bytes','sha256','display_equations']},ensure_ascii=False))
