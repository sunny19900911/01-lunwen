
from pathlib import Path
from datetime import datetime,timezone,timedelta
import re,json,hashlib,zipfile
from lxml import etree
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from math_omml import parse_math,el,container

import argparse
from docx.opc.constants import RELATIONSHIP_TYPE as RT

# Exact frozen-source spans. Explicit braces protect operands from the legacy
# heuristic that cannot distinguish adjacent unbraced subscripts.
EXPLICIT_INLINE_MATH = {
 'M=diag(1,1.2,.8)':r'M=\operatorname{diag}(1,1.2,.8)',
 'K=[[2.4,−1,0],[−1,1.7,−.7],[0,−.7,.7]]':r'K=\begin{bmatrix}2.4&-1&0\\-1&1.7&-.7\\0&-.7&.7\end{bmatrix}',
 'QD=Σn_eP':r'Q_D=\sum n_e P',
 'ℓ_s':r'\ell_s',
 'P_B':r'P_B', 'P_M':r'P_M', 't_B':r't_B', 't_M':r't_M',
 'r_peak':r'r_{\mathrm{peak}}', 'r_at':r'r_{\mathrm{at}}',
 'c_r':r'c_r', 'c_V':r'c_V',

 'V₀[n]=ΣB_srω_r²s_r⁰[n]/u_F':r'V_0[n]=\sum B_{sr}\omega_r^2s_r^0[n]/u_F',
 'V_ζ[n]=ΣB_srω_r²z_r[n]/u_F':r'V_\zeta[n]=\sum B_{sr}\omega_r^2z_r[n]/u_F',
 'P₀=max_n|V₀[n]|':r'P_0=\max_n|V_0[n]|',
 'Σc=S':r'\sum c=S',
 'P̂_s=max|V̂_s|':r'\widehat P_s=\max|\widehat V_s|',
 'D̂_s=100(1−P̂_s/P₀)%':r'\widehat D_s=100(1-\widehat P_s/P_0)\%',
 'p_r=max_t|v_r(t)|':r'p_r=\max_t|v_r(t)|',
 'U=Σ_rp_r':r'U=\sum_r p_r',
 'P=max_t|Σ_rv_r(t)|':r'P=\max_t|\sum_r v_r(t)|',
 'E_s=max E_s(t)':r'E_s=\max E_s(t)',
 '[max(0,P̂_s−E_s),P̂_s+E_s]':r'[\max(0,\widehat P_s-E_s),\widehat P_s+E_s]',
 'J₁,s=2Σ|B_sr|ω_r‖ż_r‖∞/u_F':r'J_{1,s}=2\sum|B_{sr}|\omega_r\|\dot z_r\|_\infty/u_F',
 'J₂,s=Σ|B_sr|ω_r‖ẇ_r‖∞/u_F':r'J_{2,s}=\sum|B_{sr}|\omega_r\|\dot w_r\|_\infty/u_F',
 'e_P=100(P̂−P_ref)/P_ref':r'e_P=100(\widehat P-P_{\mathrm{ref}})/P_{\mathrm{ref}}',
 'e_D=D̂−D_ref':r'e_D=\widehat D-D_{\mathrm{ref}}',
 'ΣBω²s':r'\sum B\omega^2s',
 'P_s,env=max_eP_s,e':r'P_{s,\mathrm{env}}=\max_e P_{s,e}',
 'P_s,0env=max_eP_s,e0':r'P_{s,0\mathrm{env}}=\max_e P_{s,e0}',
 '[L_s,e,U_s,e]':r'[L_{s,e},U_{s,e}]',
 'P_s,e':r'P_{s,e}',
}

def inspect_source(source):
 s=source.read_text(encoding='utf-8')
 displays=re.findall(r'\$\$([\s\S]*?)\$\$',s)
 tables=[];current=[]
 for line in s.splitlines()+['']:
  if line.startswith('|'):current.append(line)
  elif current:
   cells=[[c.strip() for c in v.strip('|').split('|')] for v in current]
   cells.pop(1);n=len(cells[0]);assert all(len(v)==n for v in cells)
   weights={2:[8,9],3:[7,5,5],4:[6.5,3.5,3.5,3.5],5:[3,3,4,3,4],6:[1.5,3.2,3.2,3.2,3.2,2.7],7:[1.1,2.1,2.1,3,2,3.3,3.4]}[n]
   widths=[v*17/sum(weights) for v in weights]
   tables.append({'block':len(tables)+1,'columns':n,'rows':len(cells),'header':cells[0],'widths_cm':widths});current=[]
 images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s)
 return s,{'display_math':len(displays),'table_blocks':len(tables),'numbered_tables':len(re.findall(r'\*\*表\d+ ',s)),'images':len(images)}, {'tables':tables,'figure_width_cm':15.8},displays

def build(source,target,report_path,*,layout=None,authoring_enabled=False):
 if not authoring_enabled:raise RuntimeError('Authoring disabled: use a successful marker receipt and explicit --author only after final review')
 source=Path(source).resolve();target=Path(target).resolve();report_path=Path(report_path).resolve()
 if target.exists():raise FileExistsError(target)
 s,expected,default_layout,_=inspect_source(source);layout=layout or default_layout

 doc=Document()
 sec=doc.sections[0]
 sec.page_width=Pt(595.3);sec.page_height=Pt(841.9)
 sec.top_margin=Pt(76.55);sec.bottom_margin=Pt(56.7);sec.left_margin=Pt(56.7);sec.right_margin=Pt(56.7)
 sec.footer_distance=Pt(42.55);sec.header_distance=Pt(42.55)
 def font(obj,size=11,bold=False,east='SimSun'):
  obj.font.name='Times New Roman';obj.font.size=Pt(size);obj.font.bold=bold;obj.font.color.rgb=RGBColor(0,0,0)
  rp=obj._element.get_or_add_rPr();rf=rp.find(qn('w:rFonts'))
  if rf is None:rf=el('w:rFonts');rp.insert(0,rf)
  for k,v in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia',east)]:rf.set(qn('w:'+k),v)
 for name,size,bold,east in [('Normal',10.5,False,'SimSun'),('Title',22,False,'SimSun'),('Subtitle',10.5,True,'SimSun'),('Heading 1',10.5,True,'SimHei'),('Heading 2',10.5,True,'SimHei'),('Caption',9,False,'SimSun')]:
  st=doc.styles[name];font(st,size,bold,east)
  pf=st.paragraph_format;pf.space_after=Pt(0);pf.line_spacing=1.0
  if name.startswith('Heading'):pf.keep_with_next=True;pf.space_before=Pt(5);pf.space_after=Pt(3)
  if name=='Normal':pf.line_spacing=1.0;pf.space_after=Pt(0);pf.first_line_indent=Pt(21);pf.widow_control=True
  if name=='Title':pf.space_after=Pt(9);pf.line_spacing=1.2
 for b in list(doc.styles.element.iter(qn('w:pBdr'))):b.getparent().remove(b)
 doc.core_properties.last_modified_by='';doc.core_properties.author='';doc.core_properties.title=s.splitlines()[0][2:];doc.core_properties.subject='结构工程论文审阅稿';doc.core_properties.comments=''
 mp=el('m:mathPr');mp.append(el('m:mathFont',**{'m:val':'Cambria Math'}));doc.settings.element.append(mp)
 footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
 field=el('w:fldSimple',**{'w:instr':'PAGE'});rr=el('w:r');tt=el('w:t');tt.text='1';rr.append(tt);field.append(rr);footer._p.append(field)
 body_started=False
 current_columns=1
 def set_columns(count):
  nonlocal current_columns
  if current_columns==count:return
  st=doc.add_section(WD_SECTION_START.CONTINUOUS)
  cols=st._sectPr.find(qn('w:cols'))
  if cols is None:cols=el('w:cols');st._sectPr.append(cols)
  cols.set(qn('w:num'),str(count));cols.set(qn('w:space'),'720')
  grid=st._sectPr.find(qn('w:docGrid'))
  if grid is None:grid=el('w:docGrid');st._sectPr.append(grid)
  grid.set(qn('w:type'),'lines');grid.set(qn('w:linePitch'),'315')
  current_columns=count
 for st in doc.sections:
  grid=el('w:docGrid',**{'w:type':'lines','w:linePitch':'315'});st._sectPr.append(grid)
 eqs=[];inlinecount=0;tables=[];images=[]
 pattern=re.compile(r'(\*\*.*?\*\*|\$[^$]+\$|\[[^]]+\]\([^)]+\))')

 def add_plain_or_math(p,value,size=11,bold=False):
  nonlocal inlinecount
  # Exact symbol grammar: one-letter indices unless explicitly grouped.
  # Adjacent operands never become part of an unbraced index.
  token_re=re.compile(r"(?:[A-Za-zΑ-ωℓΣ][A-Za-z0-9Α-ωℓΣ_^'=<>≤≥−+×·|/()[\]{}²³⁻¹₂₃₅₈₀₁₇ᵀ]*_[A-Za-z0-9]+(?:[,_A-Za-z0-9=<>≤≥−+|/()[\]{}.]*)|[A-Za-zΑ-ωℓΣ]+_[A-Za-z0-9]+)")
  at=0
  for mt in token_re.finditer(value):
   token=mt.group()
   if mt.start()>at:
    r=p.add_run(value[at:mt.start()]);font(r,size,bold)
   raw=token
   raw=re.sub(r'_([A-Za-z]+)',lambda m:'_{'+m.group(1)+'}',raw)
   raw=raw.replace('ᵀ','^T').replace('²','^2').replace('³','^3')
   om=el('m:oMath')
   for node in parse_math(raw):om.append(node)
   p._p.append(om);inlinecount+=1;at=mt.end()
  if at<len(value):
   r=p.add_run(value[at:]);font(r,size,bold)

 def inline(p,text,size=None):
  nonlocal inlinecount
  pieces=re.split(r'(\$[^$]+\$)',text)
  literals=sorted(EXPLICIT_INLINE_MATH,key=len,reverse=True)
  exact=re.compile('|'.join(re.escape(v) for v in literals))
  for pi in range(0,len(pieces),2):
   pieces[pi]=exact.sub(lambda mt:'$'+EXPLICIT_INLINE_MATH[mt.group()]+'$',pieces[pi])
  text=''.join(pieces)
  text=text.replace('K=[[2,−1],[−1,1]]',r'$K=\begin{bmatrix}2&-1\\-1&1\end{bmatrix}$').replace('M=I₂',r'$M=I_2$')
  text=text.replace('a_sr,ζ',r'$a_{sr,\zeta}$').replace('a_g=sin(√2t)',r'$a_g=\sin(\sqrt{2}t)$')
  pos=0
  for mt in pattern.finditer(text):
   if mt.start()>pos:add_plain_or_math(p,text[pos:mt.start()],size or 10.5)
   token=mt.group()
   if token.startswith('$'):
    om=el('m:oMath')
    for x in parse_math(token[1:-1]):om.append(x)
    p._p.append(om);inlinecount+=1
   elif token.startswith('**'):add_plain_or_math(p,token[2:-2],size or 10.5,True)
   else:
    label=token[1:token.index(']')]
    link=token[token.index('](')+2:-1].strip('<>')
    destination=link if link.startswith(('https://','http://')) else (source.parent/link).resolve().as_uri()
    rid=p.part.relate_to(destination,RT.HYPERLINK,is_external=True)
    hyperlink=el('w:hyperlink',**{'r:id':rid})
    run=p.add_run(label);font(run,size or 10.5);run.font.color.rgb=RGBColor.from_string('0563C1');run.font.underline=True
    hyperlink.append(run._r);p._p.append(hyperlink)
   pos=mt.end()
  if pos<len(text):add_plain_or_math(p,text[pos:],size or 10.5)

 def para(text,english=False):
  p=doc.add_paragraph()
  if english:p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.line_spacing=1.0
  inline(p,text,9 if english or not body_started else 10.5)
  return p
 def equation(raw):
  raw=raw.replace('\\big','')
  parts=[x.strip() for x in re.split(r'\\(?:qquad|quad)\b',raw) if x.strip()]
  p=doc.add_paragraph();p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
  p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(7);p.paragraph_format.line_spacing=1.0;p.paragraph_format.keep_together=True
  om=el('m:oMath')
  if len(parts)>1:
   arr=el('m:eqArr');pr=el('m:eqArrPr');pr.append(el('m:baseJc',**{'m:val':'center'}));arr.append(pr)
   for part in parts:arr.append(container('m:e',parse_math(part)))
   om.append(arr)
  else:
   for x in parse_math(raw):om.append(x)
  p._p.append(om)
  r=p.add_run('  ('+str(len(eqs)+1)+')');font(r,9)
  eqs.append(raw)
 def table(lines):
  cells=[[x.strip() for x in a.strip('|').split('|')] for a in lines];cells.pop(1)
  n=len(cells[0]);assert all(len(x)==n for x in cells)
  idx=len(tables)
  widths=layout['tables'][idx]['widths_cm']
  header=cells[0]
  if header[0]=='方向/楼层':widths=[2.1,2.5,2.0,3.0,3.0,2.4]
  elif header[:2]==['工况','楼层']:widths=[2.1,2.0,2.6,2.6,2.0,3.7]
  elif header==['量','SHW3X','SHW4X']:widths=[8.0,4.5,4.5]
  elif len(header)==6 and header[1].startswith('QT'):widths=[1.4,3.1,3.1,2.3,3.8,2.5]
  scale=17.0/sum(widths);widths=[w*scale for w in widths]
  t=doc.add_table(rows=0,cols=n);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
  for j,w in enumerate(widths):t.columns[j].width=Cm(w)
  borders=el('w:tblBorders')
  for edge in ['top','left','bottom','right','insideH','insideV']:borders.append(el('w:'+edge,**{'w:val':'single','w:sz':'4','w:color':'D9D9D9'}))
  t._tbl.tblPr.append(borders)
  margins=el('w:tblCellMar')
  for edge,val in [('top',65),('bottom',65),('left',90),('right',90)]:margins.append(el('w:'+edge,**{'w:w':val,'w:type':'dxa'}))
  t._tbl.tblPr.append(margins)
  for i,data in enumerate(cells):
   row=t.add_row();row._tr.get_or_add_trPr().append(el('w:cantSplit'))
   if i==0:row._tr.get_or_add_trPr().append(el('w:tblHeader'))
   for j,value in enumerate(data):
    cell=row.cells[j];cell.width=Cm(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    if i==0:cell._tc.get_or_add_tcPr().append(el('w:shd',**{'w:fill':'E7EEF5'}))
    p=cell.paragraphs[0];p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.space_before=Pt(1);p.paragraph_format.space_after=Pt(1);p.paragraph_format.line_spacing=1.12
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next=(i==0 or (len(cells)<=8 and i<len(cells)-1))
    inline(p,value,8.5)
    if i==0:
     for r in p.runs:r.bold=True
  tables.append(cells)
  p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=Pt(3);p.add_run().font.size=Pt(3)
 lines=s.splitlines();i=0;inEnglish=False
 while i<len(lines):
  line=lines[i].strip();i+=1
  if not line:continue
  if line.startswith('$$'):
   set_columns(1)
   raw=line[2:]
   while not raw.rstrip().endswith('$$'):
    raw+='\n'+lines[i];i+=1
   equation(raw.rstrip()[:-2]);set_columns(2);continue
  if line.startswith('|'):
   ls=[line]
   while i<len(lines) and lines[i].strip().startswith('|'):ls.append(lines[i].strip());i+=1
   table(ls);set_columns(2);continue
  if line.startswith('!['):
   set_columns(1)
   m=re.fullmatch(r'!\[([^]]+)\]\(([^)]+)\)',line);img=(source.parent/m.group(2)).resolve();assert img.exists()
   p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.keep_with_next=True;p.paragraph_format.line_spacing=1.0
   p.add_run().add_picture(str(img),width=Cm(layout.get('figure_width_cm',15.5)));images.append(str(img));continue
  if line.startswith('**') and line.endswith('**') and i<6 and re.search(r'[A-Za-z]{3}',line):
   p=doc.add_paragraph(line[2:-2],style='Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;continue
  if line.startswith('# '):
   title=line[2:];p=doc.add_paragraph(style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
   if '结构' in title:
    first,last=title.split('结构',1);p.add_run(first+'结构').add_break();p.add_run(last)
   else:p.add_run(title)
   continue
  if line.startswith('## '):
   text=line[3:]
   if text.startswith('1 '):body_started=True;set_columns(2)
   if text.startswith('Effects of'):
    p=doc.add_paragraph(text,style='Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;inEnglish=True
   else:doc.add_heading(text,level=1);inEnglish=(text=='Abstract')
   continue
  if line.startswith('### '):doc.add_heading(line[4:],level=2);continue
  if line.startswith('**表'):
   set_columns(1)
   p=doc.add_paragraph(line[2:-2],style='Caption');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.keep_with_next=True;continue
  if line.startswith('**图'):
   p=doc.add_paragraph(style='Caption');inline(p,line,9);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.keep_with_next=False;set_columns(2);continue
  if re.match(r'^图\d+ ',line):
   p=doc.add_paragraph(style='Caption');inline(p,line,9);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);set_columns(2);continue
  if re.match(r'^\[\d+\]',line):
   p=para(line,True);p.paragraph_format.left_indent=Pt(18);p.paragraph_format.first_line_indent=Pt(-18)
   for r in p.runs:font(r,9)
  else:
   p=para(line,inEnglish or line.startswith('**关键词') or line.startswith('**Keywords'))
   if line.startswith('（'):p.paragraph_format.keep_together=True
   nxt=next((v.strip() for v in lines[i:] if v.strip()),'')
   if nxt.startswith('$$'):p.paragraph_format.keep_with_next=True
 assert len(eqs)==expected['display_math'] and len(tables)==expected['table_blocks'] and len(images)==expected['images']
 doc.save(target)
 with zipfile.ZipFile(target) as z:
  root=etree.fromstring(z.read('word/document.xml'))
  ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
  visible=''.join(root.xpath('//w:t/text() | //m:t/text()',namespaces=ns))
  assert not re.search(r'\\[A-Za-z]+|\$\$',visible)
  assert len(root.xpath('//w:tbl',namespaces=ns))==expected['table_blocks']
  mathcount=len(root.xpath('//m:oMath',namespaces=ns))
 report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'display_math_sources':eqs,'display_math':len(eqs),'inline_math':inlinecount,'serialized_OMML':mathcount,'editable_tables':len(tables),'images':images,'all_math_native_OMML':True,'no_raw_latex_in_docx':True}
 report['hyperlink_relationships']=[rel.target_ref for rel in doc.part.rels.values() if rel.reltype==RT.HYPERLINK]
 report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))


def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path)
 ap.add_argument('--report',type=Path,required=True);ap.add_argument('--layout',type=Path)
 ap.add_argument('--author',action='store_true');ap.add_argument('--marker-receipt',type=Path)
 args=ap.parse_args()
 s,counts,layout,displays=inspect_source(args.input)
 if not args.author:
  out=args.report.parent;out.mkdir(parents=True,exist_ok=True)
  results=[]
  for i,raw in enumerate(displays,1):
   normalized=raw.replace('\\big','')
   parts=[v.strip() for v in re.split(r'\\(?:qquad|quad)\b',normalized) if v.strip()]
   om=el('m:oMath')
   if len(parts)>1:
    arr=el('m:eqArr');pr=el('m:eqArrPr');pr.append(el('m:baseJc',**{'m:val':'center'}));arr.append(pr)
    for part in parts:arr.append(container('m:e',parse_math(part)))
    om.append(arr)
   else:
    for node in parse_math(normalized):om.append(node)
   path=out/f'display-{i:02d}.omml.xml';path.write_bytes(etree.tostring(om,encoding='utf-8',xml_declaration=True))
   etree.fromstring(path.read_bytes())
   results.append({'index':i,'source':raw,'xml':str(path),'native':True,'text':''.join(om.itertext())})
  args.report.write_text(json.dumps({'mode':'XML-only preflight; no DOCX','input':str(args.input),'counts':counts,'display_results':results,'layout':layout},ensure_ascii=False,indent=2),encoding='utf-8')
  return
 if not args.output or not args.marker_receipt or not args.marker_receipt.is_file():ap.error('--author requires --output and successful marker stdout receipt; marker is external and runs exactly once')
 if args.layout:layout=json.loads(args.layout.read_text(encoding='utf-8'))
 build(args.input,args.output,args.report,layout=layout,authoring_enabled=True)

if __name__=='__main__':main()
