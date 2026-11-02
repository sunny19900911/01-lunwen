from pathlib import Path
import json,hashlib,difflib
from datetime import datetime,timezone,timedelta
O=Path(__file__).resolve().parent;S=O.parents[2];R=O.parents[5];M=R/'papers/damping-output-boundaries/manuscript'
C=O/'local-cache';C.mkdir(exist_ok=True)
contract=json.loads((S/'v003-exact-change-contract.json').read_text(encoding='utf-8-sig'))
src=M/'p06-engineering-session022-v002.md';dest=M/'p06-engineering-session022-v003.md'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(src)==contract['source_sha256'] and not dest.exists()
old=src.read_text(encoding='utf-8');new=old
for c in contract['changes']:
 assert new.count(c['old'])==1
 new=new.replace(c['old'],c['new'])
dest.write_bytes(new.encode('utf-8'))
assert sha(dest)==contract['expected_v003_sha256'] and dest.stat().st_size==contract['expected_v003_bytes']
(O/'v002-to-v003.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(src),tofile=str(dest))),encoding='utf-8')
report={'time':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'output':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'exact_contract_match':True,'changes':3,'source_unchanged':sha(src)==contract['source_sha256']}
(O/'v003-identity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
