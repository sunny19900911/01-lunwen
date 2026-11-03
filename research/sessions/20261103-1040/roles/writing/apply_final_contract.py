from pathlib import Path
import json,hashlib,datetime,difflib,re
H=Path(__file__).resolve().parent;R=H.parents[4];S=H.parents[1]
c=json.loads((S/'final-exact-change-contract.json').read_text(encoding='utf-8'))
src=R/c['source'];dst=R/c['target'];assert not dst.exists()
old=src.read_text(encoding='utf-8');new=old
for a,b in c['replacements']:
 assert new.count(a)==1,(a,new.count(a));new=new.replace(a,b)
raw=new.encode('utf-8');assert len(raw)==c['expected_bytes'] and hashlib.sha256(raw).hexdigest()==c['expected_sha256']
section=new[new.index('### 6.1 工程启示与设计反思'):new.index('## 7 结论')]
body=section.split('\n\n',1)[1].strip();assert len(re.findall(r'[\u4e00-\u9fff]',body))==c['expected_CJK']
base=(R/'papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-v003.md').read_bytes()
assert new.replace(section,'',1).encode('utf-8')==base
dst.write_bytes(raw);short=H/'工程启示与设计反思-最终短节.md';assert not short.exists();short.write_text(section,encoding='utf-8')
(H/'v001-to-v002.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=src.name,tofile=dst.name)),encoding='utf-8')
d={'at':datetime.datetime.now().astimezone().isoformat(),'exact_contract_match':True,'source':str(dst),'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),'short_section':str(short),'short_section_bytes':short.stat().st_size,'short_section_sha256':hashlib.sha256(short.read_bytes()).hexdigest(),'short_section_CJK':len(re.findall(r'[\u4e00-\u9fff]',body)),'remove_section_restores023_source_byte_for_byte':True,'marker_not_yet_run':True}
(H/'R002-source-identity.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
