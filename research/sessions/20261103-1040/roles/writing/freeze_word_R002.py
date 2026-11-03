from pathlib import Path
import hashlib,json,datetime,re,zipfile
from lxml import etree
H=Path(__file__).resolve().parent;R=H.parents[4];C=H/'local-cache'
src=R/'papers/damping-output-boundaries/manuscript/p06-design-reflection-session024-v002.md'
word=src.with_name('p06-design-reflection-session024-论文审阅稿-v002.docx')
oldmd=src.with_name('p06-sh3-sh4-session023-v003.md');oldword=src.with_name('p06-sh3-sh4-session023-论文审阅稿-v003.docx')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def visible(p):
 with zipfile.ZipFile(p) as z:r=etree.fromstring(z.read('word/document.xml'))
 return ''.join(r.xpath('//w:t/text() | //m:t/text()',namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}))
assert sha(src)=='750b1dcc8fa38014d45307cec124c6ef83058a063b32a5bee7ba7c1bd95f1324'
assert sha(word)=='01ba17a6c9734c5c601835198af74919b3697a094ab1aa6e8bc33ceb3c0ba701'
assert sha(oldmd)=='a16f4e6893f4f96b94ed5ef312f4b396682db68c254b104345bbadb22b21a310'
assert sha(oldword)=='df41034546824b89c1d43eb5fe59eb660a432bbce5d6f8dfb048e99e135e55a8'
section=src.read_text(encoding='utf-8').split('### 6.1 工程启示与设计反思\n\n',1)[1].split('## 7 结论',1)[0]
added='6.1 工程启示与设计反思'+''.join(section.splitlines())
v=visible(word);assert v.count(added)==1
assert v.replace(added,'',1)==visible(oldword),'Other visible document text changed'
gate=json.loads((C/'content-identity-v1.json').read_text(encoding='utf-8'));assert gate['docx_sha256']==sha(word)
marker=json.loads((C/'marker-receipt.json').read_text(encoding='utf-8'));assert marker['success_count']==1 and marker['exit_code']==0
render=json.loads((C/'render-v1/render-report.json').read_text(encoding='utf-8'));assert len(render['pages'])==10
notes={1:'Title balanced after 结构, bilingual abstracts and original first-page body readable.',2:'Original range table1 and body readable.',3:'Native equations1—4, selectors and baseline denominators visible, no lost operands.',4:'Mainline table2 and17.10/11.51percent sentence unchanged and readable.',5:'Original common-six table3 stays whole; figure1 and auxiliary heading readable.',6:'Auxiliary table4 complete, software absolute peaks and signed reference items clear; sign/model caveat and real supplement link retained. Original figure2 moves to next page without reducing label size.',7:'Original figure2/caption and table5 readable, signs/times intact.',8:'Original figure3, native K matrix, q/phi modal sum and table6 intact.',9:'New6.1 begins top of right column after implementation steps in reading order, all313Chinese characters readable, heading accompanied by full first paragraph; conclusion follows without clipping.',10:'Remaining conclusions and all ten references readable in two columns.'}
pages=[{'page':i,'path':str(C/f'render-v1/page-{i}.png'),'sha256':sha(C/f'render-v1/page-{i}.png'),'actually_viewed_original_detail':True,'visual_pass':True,'notes':notes[i]}for i in range(1,11)]
now=datetime.datetime.now().astimezone().isoformat()
d={'task':'session024/writing/R002','status':'frozen-completed','actual_start':'2026-11-03T11:06:39+08:00','frozen_at':now,'finite_deadline':'2026-11-03T11:31:00+08:00','source':str(src),'source_bytes':src.stat().st_size,'source_sha256':sha(src),'word':str(word),'word_bytes':word.stat().st_size,'word_sha256':sha(word),'final_short_section_CJK':313,'all_preexisting_visible_Word_text_unchanged':True,'old023_MD_and_Word_unchanged':True,'marker_success_count':1,'marker_at':marker['at'],'native_editable_tables':6,'numeric_table_cells_checked':gate['numeric_table_cells_checked'],'native_display_equations':5,'native_OMML_count':gate['native_OMML_count'],'original_images':len(gate['source_figures_unchanged']),'supplement_real_links_gate_passed':True,'author_metadata_empty':gate['author_metadata_empty'],'all_pages_actually_viewed':True,'pages':pages,'render_method':render['converter']+' + '+render['rasterizer'],'render_safety':'Canonical actual missingLO log, own hidden COM AutomationSecurity3/ReadOnly/only own objects closed; no ExecutionPolicy override or process kill.','science_or_source_mutation_during_layout':False,'blocking_layout_issues':[],'nonblocking_layout_note':'Existing page6 whitespace before next full-width original figure retained to preserve labels.','local_only':['rendered page PNGs','PDF','canonical/Word render logs','marker stdout/stderr','unified diff']}
(H/'R002-Word-freeze.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=['apply_final_contract.py','R002-source-identity.json','工程启示与设计反思-最终短节.md','prepare_word_tools.py','author_word.py','build_word.py','math_omml.py','render_review.py','freeze_word_R002.py','R002-Word-freeze.json']
(H/'R002-shareable-manifest.json').write_text(json.dumps({'files':[{'path':str(H/n),'bytes':(H/n).stat().st_size,'sha256':sha(H/n)}for n in files]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:d[k]for k in ['frozen_at','word_bytes','word_sha256','all_pages_actually_viewed','all_preexisting_visible_Word_text_unchanged']},ensure_ascii=False))
