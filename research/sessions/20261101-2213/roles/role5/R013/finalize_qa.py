from pathlib import Path
import json, hashlib, re, zipfile
from datetime import datetime, timezone, timedelta
from lxml import etree

O=Path(__file__).resolve().parent
S=O.parents[2]
R=S.parents[2]
M=R/'papers/damping-output-boundaries/manuscript'
src=M/'damping-prediction-session021-v010.md'
s1=O.parent/'R012/supplement-S1.md'
doc=M/'damping-prediction-session021-论文审阅稿-v010.docx'
cache=O/'local-cache'
render=cache/'render-v2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
def visible(n): return ''.join(n.xpath('.//w:t/text()|.//m:t/text()',namespaces=ns))
raw=src.read_text(encoding='utf-8')
clean=re.sub(r'!\[[^\]]*\]\([^)]+\)','',raw)
clean=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',clean)
blocks=[]; block=[]
for line in raw.splitlines()+['']:
    if line.strip().startswith('|'):
        cells=[c.strip() for c in line.strip().strip('|').split('|')]
        if not all(re.fullmatch(r'[:\-\s]+',c) for c in cells): block.append(cells)
    elif block: blocks.append(block); block=[]
with zipfile.ZipFile(doc) as z:
    root=etree.fromstring(z.read('word/document.xml'))
    rels=etree.fromstring(z.read('word/_rels/document.xml.rels'))
    targets=[n.get('Target') for n in rels if n.get('Type','').endswith('/hyperlink')]
    out=visible(root)
    tables=[[[visible(c) for c in row.findall('w:tc',ns)] for row in t.findall('w:tr',ns)] for t in root.findall('.//w:tbl',ns)]
    norm=lambda s:re.sub(r'[\s_{}^]','',s)
    mismatches=[]
    for i,(a,b) in enumerate(zip(blocks,tables),1):
        if [[norm(c) for c in row] for row in a]!=[[norm(c) for c in row] for row in b]: mismatches.append(i)
    maths=len(root.findall('.//m:oMath',ns))
    displays=[]
    for p in root.findall('.//w:p',ns):
        if p.find('.//m:oMath',ns) is not None:
            match=re.search(r'\((\d+)\)\s*$',visible(p))
            if match and int(match.group(1))<=10: displays.append(int(match.group(1)))
    media=[n for n in z.namelist() if n.startswith('word/media/')]
    images=[{'name':n,'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in media]
    core=etree.fromstring(z.read('docProps/core.xml'))
    author=core.find('{http://purl.org/dc/elements/1.1/}creator')
    blank=author is None or not author.text
cn=lambda s:''.join(re.findall(r'[\u4e00-\u9fff]',s))
now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
qa={'frozen_at':now,'source_sha256':sha(src),'S1_sha256':sha(s1),'output_sha256':sha(doc),'output_bytes':doc.stat().st_size,'Chinese_chars_source':len(cn(clean)),'Chinese_chars_output':len(cn(out)),'Chinese_sequence_exact':cn(clean)==cn(out),'editable_tables':len(tables),'source_table_blocks':len(blocks),'cell_mismatch_tables':mismatches,'native_OMML_count':maths,'display_equation_numbers':displays,'hyperlink_targets':targets,'unique_external_URL_count':len(set(t for t in targets if t.startswith('https://'))),'S1_local_link_exists':s1.exists() and s1.as_uri() in targets,'images':images,'author_blank':blank}
assert qa['source_sha256']=='64ee1567ee775cdcf30aa28734ae0bb5003706970fddb708d5fa3afb648c942d'
assert qa['S1_sha256']=='a56f931c32ddfaa5fbadbda6a45e4063ebf494903556d3b3f56e9875a3b47f5a'
assert qa['output_sha256']=='b266932700e1c518215732026526c06275e5632aeebf54a8960ff548b36d8eb9'
assert qa['Chinese_sequence_exact'] and not mismatches and len(tables)==15
assert displays==list(range(1,11)) and len(media)==3 and blank
assert qa['unique_external_URL_count']==4 and qa['S1_local_link_exists']
pages=[{'page':n,'path':str(render/f'page-{n}.png'),'sha256':sha(render/f'page-{n}.png'),'actually_viewed_at_original_resolution':True,'clipping_or_unreadable_content_found':False} for n in range(1,17)]
visual={'frozen_at':now,'docx_sha256':sha(doc),'render':'render-v2','all_final_pages_actually_viewed':True,'page_count':16,'pages':pages,'repairs':['Table 3 column widths prevent numeric wrapping','Short tables kept together; header follows first data row','Two inline maximum expressions rebuilt as native OMML'],'canonical_render':'Actual failure retained: LibreOffice soffice.exe missing','fallback':'Own hidden Word COM instance exported PDF; bundled PDFium rendered at 150 dpi; no ExecutionPolicy override or process kill','review_note':'Pages 1–8 reviewed before context compaction; pages 9–16 reviewed after compaction. Truncated 9–12 multi-image call was not counted; those pages were viewed again in two-page calls.'}
save(O/'QA.json',qa)
save(O/'visual-QA.json',visual)
manifest={'task':'R013 editable Word creation from frozen v010','status':'complete','actual_start':'2026-11-02T01:20:08+08:00','frozen_at':now,'root_expected_freeze':'2026-11-02T01:34:00+08:00','marker_success_count':1,'marker_receipt':str(cache/'marker-receipt.json'),'output':str(doc),'output_bytes':doc.stat().st_size,'output_sha256':sha(doc),'main_source':str(src),'main_source_sha256':sha(src),'S1_source':str(s1),'S1_source_sha256':sha(s1),'scientific_source_files_unchanged':True,'QA':'QA.json','visual_QA':'visual-QA.json','render_report':str(render/'render-report.json'),'canonical_log':str(render/'canonical-render.log'),'fallback_log':str(render/'word-render.log'),'scripts':['build_word.py','math_omml.py','render_review.py','finalize_qa.py'],'final_page_count':16,'all_final_pages_viewed':True}
save(O/'manifest.json',manifest)
(O/'one-page.md').write_text(f'''# R013 Word 交付\n\n完成并冻结于 {now}。正文采用冻结 v010，S1 采用 R012，二者 SHA256 复核一致且未修改。\n\n最终 Word：`{doc}`\n\n- 共 16 页，最终 render-v2 全部页 PNG 已按原分辨率实际查看。\n- 15 张可编辑表格（13 张编号表、2 张决策表）、10 个编号独立公式，合计 {maths} 个原生 OMML 公式对象、3 张图。\n- 4 个外部实际超链接及真实可用的本地 S1 超链接；作者为空。\n- 正文中文序列与来源一致（8701 字）；15 张表的逐单元格内容一致。\n- 仅修复表格分页、数值换行、两处行内最大值表达式的 Word 原生数学排版。\n- 标记仅成功运行一次。canonical renderer 实际失败日志已保留，原因是缺少 soffice.exe；随后仅用自有隐藏 Word COM 实例导出 PDF，再由 PDFium 栅格化。未使用 ExecutionPolicy 参数，未终止其他 Word 进程。\n- DOCX SHA256：`{sha(doc)}`。源稿和 S1、链接清单、最终页哈希与视觉记录详见 manifest.json、QA.json、visual-QA.json。\n\n可交 root 再看最终页图；本轮未修改科学内容，未开展额外计算或文献检索。\n''',encoding='utf-8')
print(json.dumps({'status':'complete','frozen_at':now,'QA':qa},ensure_ascii=False,indent=2))
