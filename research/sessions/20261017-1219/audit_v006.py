"""Read-only manuscript identity/structure comparison; no source regeneration."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MAN = ROOT/'papers/damping-output-boundaries/manuscript'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

old = (MAN/'theory-draft-v005.md').read_text('utf-8')
new = (MAN/'theory-draft-v006.md').read_text('utf-8')
assert sha(MAN/'theory-draft-v006.md') == '7c40bc8f602293b8e1d9789a6ad7cb71fd67e2fbe7776ad26379ce160c50b9f1'
assert sha(MAN/'theory-figure-evidence-map-v006.json') == 'cdacfca9fb202e40e019771c5b4968a219705c33f5240650de296f2f73e82802'
main = new.split('## 附录 A')[0]
headings = re.findall(r'^## ([1-5])\s', main, re.M)
assert headings == list('12345'), headings
old_images = re.findall(r'!\[[^\n]*\]\([^\n]*\)', old)
new_images = re.findall(r'!\[[^\n]*\]\([^\n]*\)', new)
assert len(old_images) == 2 and old_images == new_images
old_formulae = dict(re.findall(r'\$\$(.*?)\\tag\{(\d+)\}\$\$', old, re.S))
new_formulae = dict(re.findall(r'\$\$(.*?)\\tag\{(\d+)\}\$\$', new, re.S))
# Each tuple above is formula->tag: invert for direct comparisons.
old_formulae = {v:k for k,v in old_formulae.items()}
new_formulae = {v:k for k,v in new_formulae.items()}
for number in range(1,14):
    assert old_formulae[str(number)] == new_formulae[str(number if number <= 10 else number+1)], number
old_appendix = old.split('## 附录 A',1)[1].split('## 参考文献',1)[0]
new_appendix = new.split('## 附录 A',1)[1].split('## 附录 G',1)[0]
old_appendix = old_appendix.replace('本节使用与式（12）相同', '本节使用与式（13）相同')
old_appendix = old_appendix.replace('原L1输入类桥接及式（12）', '原L1输入类桥接及式（13）')
old_appendix = old_appendix.replace('合并，证明式（13）。', '合并，证明式（14）。')
assert old_appendix.strip() == new_appendix.strip(), 'Unexpected old appendix edits'
tags = re.findall(r'\\tag\{([^}]+)\}', new)
expected = [str(i) for i in range(1,15)]
for prefix, count in [('A',10),('B',14),('C',4),('D',4),('E',15),('F',10),('G',14)]:
    expected += [prefix+str(i) for i in range(1,count+1)]
assert tags == expected and len(tags) == len(set(tags)) == 85
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
walk(json.loads((MAN/'theory-figure-evidence-map-v006.json').read_text('utf-8')))
freeze = ROOT/'papers/damping-output-boundaries/research/roles/writing/theory-session002/frozen-v006.json'
for item in json.loads(freeze.read_text('utf-8'))['files']:
    assert sha(ROOT/item['path']) == item['sha256']
report = {'checked_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
          'manuscript_sha256': sha(MAN/'theory-draft-v006.md'),
          'mapping_sha256': sha(MAN/'theory-figure-evidence-map-v006.json'),
          'same_two_image_references': True, 'five_main_sections': headings,
          'old_13_formula_bodies_preserved': True,
          'old_appendices_A_F_only_expected_internal_reference_changes': True,
          'ordered_unique_equation_labels': len(tags), 'mapping_identities_matched': len(identities),
          'frozen_four_files_matched': True,
          'scope': 'Read-only root identity/structure audit, not mathematical proof or novelty certification'}
(HERE/'v006-root-identity-audit.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(report,ensure_ascii=False))
