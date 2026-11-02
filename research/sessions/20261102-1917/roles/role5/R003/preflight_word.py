"""Read-only source/template inspection and XML preflight. Never writes DOCX."""
from pathlib import Path
import json,re,hashlib,py_compile
from datetime import datetime,timezone,timedelta
from lxml import etree
from math_omml import parse_math,el
import docx,pypdfium2
O=Path(__file__).resolve().parent; S=O.parents[2]; R=O.parents[5]; C=O/'local-cache'
source=R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-v002.md'
template=S/'roles/role3/R001/local-cache/建筑结构-正刊排版模板-2024.4.28.doc'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((C/'template-audit.json').read_text(encoding='utf-8-sig'))
raw=source.read_text(encoding='utf-8')
formulas=re.findall(r'\$\$([\s\S]*?)\$\$',raw)
extra={
 'K_matrix':r'K=\begin{bmatrix}2.4&-1&0\\-1&1.7&-.7\\0&-.7&.7\end{bmatrix}',
 'M_matrix':r'M=\operatorname{diag}(1,1.2,.8)',
 'device_sum':r'Q_D=\sum n_e P',
 'PBPM_fraction':r'r_{\mathrm{peak}}=1-\frac{P_M}{P_B}',
 'time_bias':r'd=\frac{P_M-|V_M(t_B)|}{P_B}',
 'argmin_operand':r'c_r\in\operatorname{argmin}_{c\in C}r_{\mathrm{peak},s,a,c}',
 'argmax_operand':r'c_V\in\operatorname{argmax}_{c\in C}P_{M,s,a,c}',
 'modal_shear_operand':r'V_s(t)=\sum_r(\ell_s^T\phi_r)q_r(t)',
}
results=[]
for name,latex in [(f'display-{i:02d}',s) for i,s in enumerate(formulas,1)]+list(extra.items()):
 n=el('m:oMath')
 for item in parse_math(latex):n.append(item)
 p=C/(name+'.xml');p.write_bytes(etree.tostring(n,encoding='utf-8',xml_declaration=True,pretty_print=True))
 etree.fromstring(p.read_bytes())
 results.append({'name':name,'latex':latex,'XML':str(p),'text':''.join(n.itertext()),'XML_well_formed':True})
for name in ['math_omml.py','render_review.py',Path(__file__).name]:py_compile.compile(str(O/name),doraise=True)
pdf=pypdfium2.PdfDocument(str(C/'template-reference.pdf'));page_count=len(pdf)
for i in range(page_count):
 p=pdf[i];b=p.render(scale=100/72);b.to_pil().save(C/f'template-page-{i+1}.png');b.close();p.close()
pdf.close()
now=datetime.now(timezone(timedelta(hours=8)));start=datetime.fromisoformat('2026-11-02T20:14:35+08:00')
summary={'status':'prepared-partial-frozen-idle','first_tool_time':start.isoformat(),'frozen_at':now.isoformat(timespec='seconds'),'elapsed_since_first_tool_seconds':(now-start).total_seconds(),'template_sha256':sha(template),'template_bytes':template.stat().st_size,'template_pages':page_count,'template_sections':audit['sections'],'template_read_only':audit['read_only'],'AutomationSecurity':audit['automation_security'],'Word_version':audit['word_version'],'source_sha256':sha(source),'source_display_equations':len(formulas),'XML_preflight':results,'bundled_python':str(Path(__import__('sys').executable)),'python_docx_available':True,'PDFium_available':True,'estimated_manuscript_pages':{'minimum':9,'maximum':12,'basis':'A4 dual columns 47-line grid; 5 full-width tables and 3 figures, unrendered estimate only'},'Word_created':False,'marker_executed':False,'template_PNGs_actually_viewed':False,'final_document_QA_passed':False,'pending':['Template pages exported but not yet actually viewed','No manuscript authoring performed; source must advance to root-adopted v003','Template-derived builder and preserve-only package gates still need authoring-task implementation','Macro-disabled read-only COM conversion from DOC to working DOCX permitted only after authoring dispatch and one successful marker','Final canonical rendering, fallback if needed, and every final page visual review remain']}
(O/'freeze.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paragraphs=audit['paragraphs'];roles=[]
for p in paragraphs:
 if any(x in p['text'] for x in ['二号','小四','小五','五号','四号','关键词','参考文献','正文']):roles.append(p)
(C/'template-role-evidence.json').write_text(json.dumps(roles,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'artifact.md').write_text(f'''# 官方模板执行契约 预备版\n\n参考 `{template}`，SHA `{sha(template)}`。只读提取及PDF导出完成，未转换为DOCX，未改原件。模板共{page_count}页；节/段落排版证据见local-cache/template-audit.json及template-role-evidence.json。模板PNG尚未实际查看，模板蒸馏门尚未通过。\n\n主文预计9—12页，仅按内容量估计。A4上2.7cm、其余2cm，页眉脚1.5cm，47行网格；题摘单栏，正文双栏；表图通过连续分节转通栏并恢复双栏。最终以实际模板sections参数与页图为准；不得重新采用旧Letter通用样式。正文预计五号宋体、英数TNR，题22pt、作者12pt仿宋，实际各角色字号见模板提取记录，不编造作者或基金、DOI。\n\n源v002仅作数学预备；之后绑定主控采用v003的真实SHA。5个display与K/M矩阵、QD求和、argmin/max和分母已做原生OMML XML预检，详见freeze.json。最终须逐式查操作数，不以XML可解析或对象数量替代正确性。全部行内数学采用明确映射，不能复用旧贪婪下标正则。\n\n可编辑正文与表格；表2六列8条记录（另有表头），其余表按源；3图和图注配对。模板真实表格/图/节模式须先看模板全部页。正文作者身份槽留空；删除模板示例作者/基金/假DOI，不将示例残留到正文。\n\n已备math_omml.py和render_review.py，后者先实际调用canonical renderer，失败留日志后才--allow-word-fallback；fallback AutomationSecurity=3、hidden、ReadOnly、仅关闭自建对象，无ExecutionPolicy参数和kill。模板检查失败尝试不改变原件。尚未编完模板派生正文builder，不把预备当authoring或QA。\n\n真实制作获派后：首次authoring前marker成功一次；只在本轮cache内转换/复制模板；构建后检查正文/表格/所有小数/5display/行内数学/3图hash/附录实际链接/作者空，再render、每页原分辨率view；修后重新渲染最终字节。\n''',encoding='utf-8')
print(json.dumps({'frozen_at':summary['frozen_at'],'elapsed':summary['elapsed_since_first_tool_seconds'],'template_pages':page_count,'sections':audit['sections'],'XML_math_blocks':len(results),'Word_created':False},ensure_ascii=False))
