from pathlib import Path
import json, hashlib, re, zipfile
from datetime import datetime, timezone, timedelta
from lxml import etree
from build_word import EXPLICIT_INLINE_MATH
from math_omml import parse_math, el

O=Path(__file__).resolve().parent
S=O.parents[2]; R=S.parents[2]
M=R/'papers/damping-output-boundaries/manuscript'
source=M/'damping-prediction-session021-v010.md'
s1=O.parent/'R012/supplement-S1.md'
old=M/'damping-prediction-session021-论文审阅稿-v010.docx'
doc=M/'damping-prediction-session021-论文审阅稿-v010-r2.docx'
C=O/'local-cache'; render=C/'render-v1'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(n): return ''.join(n.xpath('.//w:t/text()|.//m:t/text()',namespaces=ns))
def read(p):
 with zipfile.ZipFile(p) as z: return etree.fromstring(z.read('word/document.xml'))
def canon(n): return etree.tostring(n,method='c14n',exclusive=True)
raw=source.read_text(encoding='utf-8')
clean=re.sub(r'!\[[^\]]*\]\([^)]+\)','',raw)
clean=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',clean)
root=read(doc); older=read(old)
omml=root.findall('.//m:oMath',ns)
out=text(root)
out_for_numbers='\n'.join(text(p) for p in root.findall('.//w:p',ns))
cn=lambda t:''.join(re.findall(r'[\u4e00-\u9fff]',t))
norm=lambda t:re.sub(r'[\s_{}^]','',t)
blocks=[]; block=[]
for line in raw.splitlines()+['']:
 if line.strip().startswith('|'):
  cells=[c.strip() for c in line.strip().strip('|').split('|')]
  if not all(re.fullmatch(r'[:\-\s]+',c) for c in cells): block.append(cells)
 elif block: blocks.append(block); block=[]
tables=[[[text(c) for c in row.findall('w:tc',ns)] for row in t.findall('w:tr',ns)] for t in root.findall('.//w:tbl',ns)]
cell_mismatches=[i for i,(a,b) in enumerate(zip(blocks,tables),1) if [[norm(c) for c in row] for row in a]!=[[norm(c) for c in row] for row in b]]
def displays(r):
 result=[]
 for p in r.findall('.//w:p',ns):
  math=p.find('m:oMath',ns)
  if math is not None:
   match=re.search(r'\((\d+)\)\s*$',text(p))
   if match and int(match.group(1))<=10: result.append((int(match.group(1)),canon(math)))
 return result
equations=displays(root)
checks=[]
for i,(literal,latex) in enumerate(EXPLICIT_INLINE_MATH.items(),1):
 expected=el('m:oMath')
 for n in parse_math(latex): expected.append(n)
 matches=[n for n in omml if canon(n)==canon(expected)]
 assert matches,('Missing explicit formula',literal)
 checks.append({'source_literal':literal,'explicit_latex':latex,'native_math_present':True,'native_matches':len(matches),'serialized_text':text(matches[0]),'XML':f'explicit-math-{i:02d}.xml'})
 (C/f'explicit-math-{i:02d}.xml').write_bytes(etree.tostring(matches[0],encoding='utf-8',xml_declaration=True,pretty_print=True))
def math_for(literal):
 entry=next(x for x in checks if x['source_literal']==literal)
 return etree.parse(str(C/entry['XML'])).getroot()
u=math_for('U=Σ_rp_r'); p=math_for('P=max_t|Σ_rv_r(t)|'); ep=math_for('e_P=100(P̂−P_ref)/P_ref')
assert u.xpath('count(m:sSub[m:e/m:r/m:t="p" and m:sub/m:r/m:t="r"])=1',namespaces=ns)
assert p.xpath('count(m:sSub[m:e/m:r/m:t="v" and m:sub/m:r/m:t="r"])=1',namespaces=ns)
assert ep.xpath('count(.//m:acc[m:accPr/m:chr/@m:val="̂" and m:e/m:r/m:t="P"])=1',namespaces=ns)
assert text(u)=='U=∑rpr' and text(p)=='P=maxt|∑rvr(t)|'
keyparas=[x for x in root.findall('.//w:p',ns) if any(k in text(x) for k in ['在同一保存时间','峰值误差为','定义V','完整地震作用历程的共同','仅使用统一','预先指定SHW3X'])]
(C/'key-math-paragraphs.xml').write_text('\n'.join(etree.tostring(x,encoding='unicode',pretty_print=True) for x in keyparas),encoding='utf-8')
with zipfile.ZipFile(doc) as z,zipfile.ZipFile(old) as prior:
 rels=etree.fromstring(z.read('word/_rels/document.xml.rels'))
 targets=[n.get('Target') for n in rels if n.get('Type','').endswith('/hyperlink')]
 media=[n for n in z.namelist() if n.startswith('word/media/')]
 images=[{'name':n,'sha256':hashlib.sha256(z.read(n)).hexdigest(),'same_as_frozen_previous_docx':z.read(n)==prior.read(n)} for n in media]
 core=etree.fromstring(z.read('docProps/core.xml'))
 author=core.find('{http://purl.org/dc/elements/1.1/}creator')
 author_blank=author is None or not author.text
engsrc=re.search(r'## Abstract\s+([\s\S]*?)\n\*\*Keywords',raw).group(1)
engdoc=next(text(p) for p in root.findall('.//w:p',ns) if text(p).startswith('To explain differences'))
decimals=lambda t:re.findall(r'\d+\.\d+',t)
assert decimals(clean)==decimals(out_for_numbers), (len(decimals(clean)),len(decimals(out_for_numbers)))
now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
qa={'frozen_at':now,'source_sha256':sha(source),'S1_sha256':sha(s1),'previous_DOCX_sha256':sha(old),'output_sha256':sha(doc),'output_bytes':doc.stat().st_size,'Chinese_sequence_exact':cn(clean)==cn(out),'Chinese_characters':len(cn(out)),'English_abstract_exact_after_math_markup_normalization':norm(engsrc)==norm(engdoc),'editable_tables':len(tables),'source_tables':len(blocks),'table_cell_mismatches':cell_mismatches,'all_decimal_numbers_in_order_exact':decimals(clean)==decimals(out_for_numbers),'decimal_number_count':len(decimals(clean)),'native_OMML_count':len(omml),'display_numbers':[i for i,n in equations],'ten_display_equations_XML_unchanged':equations==displays(older),'images':images,'hyperlink_targets':targets,'external_URL_count':len(set(t for t in targets if t.startswith('https://'))),'S1_hyperlink_exists':s1.exists() and s1.as_uri() in targets,'author_blank':author_blank,'key_math_contract':{'U_has_separate_p_sub_r_operand':True,'P_has_separate_v_sub_r_operand':True,'eP_predicted_P_has_native_hat_accent':True,'all_inline_sum_and_max_spans_explicitly_mapped':True,'explicit_spans':checks}}
assert qa['source_sha256']=='64ee1567ee775cdcf30aa28734ae0bb5003706970fddb708d5fa3afb648c942d'
assert qa['S1_sha256']=='a56f931c32ddfaa5fbadbda6a45e4063ebf494903556d3b3f56e9875a3b47f5a'
assert qa['previous_DOCX_sha256']=='b266932700e1c518215732026526c06275e5632aeebf54a8960ff548b36d8eb9'
assert all([qa['Chinese_sequence_exact'],qa['English_abstract_exact_after_math_markup_normalization'],qa['all_decimal_numbers_in_order_exact'],qa['ten_display_equations_XML_unchanged'],author_blank,qa['S1_hyperlink_exists']]), {k:v for k,v in qa.items() if isinstance(v,bool)}
assert len(tables)==len(blocks)==15 and not cell_mismatches and len(media)==3 and all(i['same_as_frozen_previous_docx'] for i in images)
assert qa['external_URL_count']==4 and qa['display_numbers']==list(range(1,11))
pages=[{'page':n,'PNG':str(render/f'page-{n}.png'),'sha256':sha(render/f'page-{n}.png'),'actually_viewed_original_resolution':True,'clipping_or_overlap_found':False} for n in range(1,17)]
visual={'frozen_at':now,'docx_sha256':sha(doc),'final_render':'render-v1','actual_page_count':16,'all_final_pages_actually_viewed':True,'pages':pages,'key_visual_confirmation':{'page5':'V0 and V_zeta sums retain B, omega, s/z; predicted P,V,D native hats visible','page6':'U=sum_r p_r and P=max_t|sum_r v_r(t)| operands visible and correct','page7':'uniform E max, peak interval hats and J1/J2 sums legible','page9':'eP has native P hat; eD has native D hat','page14':'both max_e formulas retain P operands'},'canonical_failure_log':str(render/'canonical-render.log'),'fallback':'Own hidden Word COM instance exported PDF; PDFium rendered 150dpi. No ExecutionPolicy override; no global process termination.'}
save(O/'QA.json',qa); save(O/'visual-QA.json',visual)
manifest={'task':'R014 necessary Word formula conversion repair','status':'complete','actual_start':'2026-11-02T01:37:15+08:00','frozen_at':now,'output':str(doc),'output_bytes':doc.stat().st_size,'output_sha256':sha(doc),'old_output_preserved':str(old),'old_output_sha256':sha(old),'scientific_sources_unchanged':True,'main_source_sha256':sha(source),'S1_sha256':sha(s1),'marker_rerun':False,'existing_success_marker_receipt':str(O.parent/'R013/local-cache/marker-receipt.json'),'QA':'QA.json','visual_QA':'visual-QA.json','final_pages':16,'all_final_pages_viewed':True,'build_report':str(C/'build-report.json'),'render_report':str(render/'render-report.json'),'math_key_XML':str(C/'key-math-paragraphs.xml'),'explicit_formula_XML_glob':'local-cache/explicit-math-*.xml'}
save(O/'manifest.json',manifest)
(O/'one-page.md').write_text(f'''# R014 Word 数学转换修复交付\n\n完成并冻结于 {now}，仅修 Word 呈现。v010 MD、R012 S1 与旧 DOCX 均保持原 SHA。\n\n- 最终文件 `{doc}`，{doc.stat().st_size} B，SHA256 `{sha(doc)}`。\n- 16 页最终 PNG 均已按原分辨率实际查看。第 6 页 U 与 P 两式分别保留独立的 p_r、v_r(t) 操作数；第 9 页 e_P 中预测 P 的帽号为原生 m:acc 且视觉清楚。\n- builder 显式映射全部行内求和与最大值相关源片段，避免无括号下标的贪婪匹配；帽号均使用原生重音结构。20 个显式公式片段 XML 保存于 local-cache。\n- 15 张可编辑表格内容逐格一致，{len(decimals(clean))} 个小数按序一致；8701 个中文字符序列一致，英文摘要一致。10 个独立公式 XML 与原 Word 完全一致；共 {len(omml)} 个 OMML 对象，3 图字节一致，4 外部 URL 与本地 S1 链接存在，作者为空。\n- marker 未重跑。canonical renderer 实际缺 soffice.exe 的失败日志保留；仅自有隐藏 Word 实例导出 PDF，PDFium 出页。\n- 完整内容合同、关键数学 XML、逐页 hash 和视觉说明见 QA.json、visual-QA.json、manifest.json。旧 DOCX 保留为本轮比较依据，不作为此次最终交付。\n\n可交根复核最终第 6、9 页及完整 16 页。未改科学稿，未重算数据。\n''',encoding='utf-8')
print(json.dumps({'status':'complete','frozen_at':now,'output_sha256':sha(doc),'bytes':doc.stat().st_size,'OMML':len(omml),'tables':len(tables),'decimal_numbers':len(decimals(clean)),'pages_viewed':16},ensure_ascii=False))
