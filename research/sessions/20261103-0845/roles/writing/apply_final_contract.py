from pathlib import Path
import json,hashlib,datetime,difflib
H=Path(__file__).resolve().parent;S=H.parents[1];R=H.parents[4]
c=json.loads((S/'final-exact-change-contract.json').read_text(encoding='utf-8'))
rows=[]
for key in ['main','supplement']:
 d=c[key];src=R/d['source'];dst=R/d['target'];assert not dst.exists()
 old=src.read_text(encoding='utf-8');new=old
 for a,b in d['replacements']:
  assert new.count(a)==1,(key,a,new.count(a));new=new.replace(a,b)
 raw=new.encode('utf-8');assert len(raw)==d['expected_bytes'] and hashlib.sha256(raw).hexdigest()==d['expected_sha256']
 dst.write_bytes(raw)
 (H/f'R003-{key}-exact.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=src.name,tofile=dst.name)),encoding='utf-8')
 rows.append({'kind':key,'path':str(dst),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
report={'written_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'root_contract_match':True,'files':rows,'marker_not_yet_run':True}
(H/'R003-source-identity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
