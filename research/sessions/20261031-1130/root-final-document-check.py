from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,zipfile,re
from lxml import etree
S=Path(__file__).resolve().parent;R=S.parents[2];A=S/'roles/role5/R007'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((A/'manifest.json').read_text())
for x in manifest['artifacts']:
 p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
old=R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-v006.md'
new=R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-v007.md'
doc=R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-论文审阅稿-v007.docx'
expected=old.read_text(encoding='utf-8').replace('/role5/R006/supplement-S1.md','/role5/R007/supplement-S1.md').replace('输出第一层1 N/m弹簧的弹性力。比较','输出第一层1 N/m弹簧的弹性力。两个模态均取相同阻尼比ζ。比较')
assert new.read_text(encoding='utf-8')==expected
oldS=(S/'roles/role5/R006/supplement-S1.md').read_text(encoding='utf-8')
assert (A/'supplement-S1.md').read_text(encoding='utf-8')==oldS.replace('峰比区间另要求5%分母为正','峰比区间另要求P_N^5>T_N^5，使分母P_N^5−T_N^5>0')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
with zipfile.ZipFile(doc) as z:
 root=etree.fromstring(z.read('word/document.xml'))
 tables=root.findall('.//w:tbl',ns);math=root.findall('.//m:oMath',ns)
 assert len(tables)==6 and len(math)==77
 media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
 for x in json.loads((S/'roles/role5/R006/figure-source-map.json').read_text())['figures']:assert x['png_sha256'] in media
 text=''.join(root.xpath('//w:t/text()|//m:t/text()',namespaces=ns));assert '\\underbrace' not in text and '$$' not in text
 expected_tables=[];group=[]
 for line in new.read_text(encoding='utf-8').splitlines()+['']:
  if line.startswith('|') and line.endswith('|'):
   cells=[v.strip() for v in line.strip('|').split('|')]
   if not all(re.fullmatch(r':?-+:?',v) for v in cells):group.append(cells)
  elif group:expected_tables.append(group);group=[]
 assert len(expected_tables)==6
 cells_checked=0
 for raw,t in zip(expected_tables,tables):
  rows=t.findall('w:tr',ns);assert len(rows)==len(raw)
  for erow,row in zip(raw,rows):
   acells=row.findall('w:tc',ns);assert len(acells)==len(erow)
   for e,c in zip(erow,acells):
    a=''.join(c.xpath('.//w:t/text()|.//m:t/text()',namespaces=ns));assert a==e,(e,a)
    cells_checked+=1
qa=json.loads((A/'QA.json').read_text());assert len(qa['page_reviews'])==11
for x in qa['page_reviews']:
 p=A/'local-cache/render-v3'/('page-'+str(x['page'])+'.png');assert sha(p)==x['png_sha256']
result=dict(actual=datetime.now(timezone(timedelta(hours=8))).isoformat(),status='accepted final document',docx_sha256=sha(doc),markdown_sha256=sha(new),author_manifest_files_verified=len(manifest['artifacts']),exact_text_changes_verified=True,editable_tables=6,native_math_objects=77,table_cells_independently_compared=cells_checked,approved_embedded_figures=3,root_actual_pages_viewed=list(range(1,12)),root_visual_result='all11 pages readable; formulas/matrix/tables andfigures intact; no clipping/blankmiddlepages',render_fallback='canonical soffice unavailable; hidden WordCOM PDF export andpypdfium2 raster; packagedrender main used; retainedfailure log',new_scientific_checks=False)
(S/'root-final-document-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
