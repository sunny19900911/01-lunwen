"""Check v007 against frozen v006 without executing scientific calculations."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAN = ROOT/'papers/damping-output-boundaries/manuscript'
WRITING = ROOT/'papers/damping-output-boundaries/research/roles/writing/theory-session002'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

freeze = json.loads((WRITING/'frozen-v007.json').read_text('utf-8'))
for item in freeze['files']:
    assert sha(ROOT/item['path']) == item['sha256'], item['path']
old = (MAN/'theory-draft-v006.md').read_text('utf-8')
new = (MAN/'theory-draft-v007.md').read_text('utf-8')
assert re.findall(r'^## ([1-5])\s', new.split('## 附录 A')[0], re.M) == list('12345')
images = lambda text: re.findall(r'!\[[^\n]*\]\([^\n]*\)', text)
assert len(images(old)) == 2 and images(old) == images(new)
formulae = lambda text: {tag:body for body,tag in re.findall(r'\$\$(.*?)\\tag\{(\d+)\}\$\$', text, re.S)}
assert formulae(old) == formulae(new), 'Existing main formula bodies or labels changed'
old_appendix = old.split('## 附录 A',1)[1].split('## 参考文献',1)[0]
new_appendix = new.split('## 附录 A',1)[1].split('## 附录 H',1)[0]
assert old_appendix.strip() == new_appendix.strip(), 'Unexpected changes in A-G'
old_refs = old.split('## 参考文献',1)[1].strip()
new_refs = new.split('## 参考文献',1)[1].strip()
assert new_refs.split('[8]',1)[0].strip() == old_refs, 'Original references1-7 changed'
assert '10.1115/1.4067639' in new_refs.split('[8]',1)[1]
tags = re.findall(r'\\tag\{([^}]+)\}', new)
old_tags = re.findall(r'\\tag\{([^}]+)\}', old)
h_tags = tags[len(old_tags):]
assert tags[:len(old_tags)] == old_tags
assert h_tags and h_tags == ['H'+str(i) for i in range(1,len(h_tags)+1)]
assert len(tags) == len(set(tags))
identities = []
def walk(node):
    if isinstance(node,dict):
        if 'path' in node and 'sha256' in node:
            p = Path(node['path'])
            p = p if p.is_absolute() else ROOT/p
            assert sha(p) == node['sha256'], node['path']
            if 'bytes' in node:
                assert p.stat().st_size == node['bytes']
            identities.append(node['path'])
        for value in node.values():
            walk(value)
    elif isinstance(node,list):
        for value in node:
            walk(value)
walk(json.loads((MAN/'theory-figure-evidence-map-v007.json').read_text('utf-8')))
report = {'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
          'manuscript_sha256':sha(MAN/'theory-draft-v007.md'),
          'mapping_sha256':sha(MAN/'theory-figure-evidence-map-v007.json'),
          'frozen_files_matched':True,'five_main_sections':True,'same_two_image_references':True,
          'old_main_formulae_and_tags_unchanged':True,'appendices_A_G_unchanged':True,
          'original_references1_7_unchanged':True,'reference8_DOI_present':True,
          'all_ordered_unique_equation_labels':len(tags),'new_H_labels':len(h_tags),
          'mapping_identities_matched':len(identities),
          'scope':'Read-only identity/structure audit, not independent proof or novelty adjudication'}
(HERE/'v007-root-identity-audit.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(report,ensure_ascii=False))
