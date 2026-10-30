from pathlib import Path
import json,hashlib,datetime,zipfile,ast
from lxml import etree
S=Path(__file__).resolve().parent;R=S.parents[2];A=S/'roles/role5/R005'
mf=json.loads((A/'manifest.json').read_text(encoding='utf-8'))
checks=[]
for q in mf['artifacts']:
 p=Path(q['path']);b=p.read_bytes();assert len(b)==q['bytes'] and hashlib.sha256(b).hexdigest()==q['sha256']
 checks.append({'name':p.name,'sha256':q['sha256']})
md=R/'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v005.md'
word=md.with_suffix('.docx');text=md.read_text(encoding='utf-8')
assert '本文的定量结果仅针对基准5%与直接模态8%的对照' in text
assert '用经过误差与截断比较的有限阶输出参照检查组合变化' in text
assert '在这一输出参照中，主组峰幅变化与软件总峰削弱的量级相近' in text
assert '6.355%' in text and '29.106%' in text and '5.06' in text
with zipfile.ZipFile(word)as z:
 root=etree.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
 math=len(root.xpath('//m:oMath',namespaces=ns));tables=len(root.xpath('//w:tbl',namespaces=ns));images=len(root.xpath('//a:blip',namespaces=ns))
 assert math==25 and tables==4 and images==2
pages=[]
for n in range(1,8):
 p=A/f'local-cache/render-final/page-{n}.png';assert p.exists();pages.append({'page':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'root_actual_view_image':'viewed at original resolution; legible formulas/tables/figures, no clipping or overlap'})
ast.parse((S/'publish_checkpoint.py').read_text(encoding='utf-8'))
d={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'science_markdown_root_full_read':True,'author_manifest_artifacts_verified':checks,'three_final_phrase_changes_adopted':True,'native_OMML':math,'editable_tables':tables,'figures':images,'page_count':7,'root_actual_pages_viewed':pages,'render_engine':'hidden Microsoft Word PDF export + bundled pypdfium2; packaged render_docx attempted but soffice missing','initial_image_line_spacing_clipping_fixed':True,'status':'review Word accepted; not claimed journal-ready submission or complete physical modal attribution','MD_sha256':hashlib.sha256(md.read_bytes()).hexdigest(),'Word_sha256':hashlib.sha256(word.read_bytes()).hexdigest(),'local_cache_not_for_upload':True}
(S/'root-final-document-QA.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'pages':7,'OMML':math,'tables':tables,'figures':images,'Word_sha256':d['Word_sha256']},ensure_ascii=False))
