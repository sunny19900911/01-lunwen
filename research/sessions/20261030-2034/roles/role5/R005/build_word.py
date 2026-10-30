
from pathlib import Path
from datetime import datetime,timezone,timedelta
import re,json,hashlib,zipfile
from lxml import etree
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from math_omml import parse_math,el,container
O=Path(__file__).resolve().parent
R=O.parents[5]
M=R/'papers/damping-output-boundaries/manuscript'
source=M/'damping-superposition-session019-v005.md'
target=M/'damping-superposition-session019-v005.docx'
if datetime.now(timezone(timedelta(hours=8)))>=datetime.fromisoformat('2026-10-30T22:23:40+08:00'):raise SystemExit('deadline')
s=source.read_text(encoding='utf-8')
assert s.count('$$')==10
doc=Document()
sec=doc.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.top_margin=Cm(2.2);sec.bottom_margin=Cm(2.0);sec.left_margin=Cm(2.2);sec.right_margin=Cm(2.2)
sec.footer_distance=Cm(1.0)
def font(obj,size=11,bold=False,east='SimSun'):
 obj.font.name='Times New Roman';obj.font.size=Pt(size);obj.font.bold=bold;obj.font.color.rgb=RGBColor(0,0,0)
 rp=obj._element.get_or_add_rPr();rf=rp.find(qn('w:rFonts'))
 if rf is None:rf=el('w:rFonts');rp.insert(0,rf)
 for k,v in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia',east)]:rf.set(qn('w:'+k),v)
for name,size,bold,east in [('Normal',11,False,'SimSun'),('Title',17,True,'SimHei'),('Subtitle',11.5,True,'SimSun'),('Heading 1',13,True,'SimHei'),('Heading 2',11.5,True,'SimHei'),('Caption',10,False,'SimSun')]:
 st=doc.styles[name];font(st,size,bold,east)
 pf=st.paragraph_format;pf.space_after=Pt(4);pf.line_spacing=1.15
 if name.startswith('Heading'):pf.keep_with_next=True;pf.space_before=Pt(9);pf.space_after=Pt(5)
 if name=='Normal':pf.line_spacing=Pt(18);pf.first_line_indent=Pt(22);pf.widow_control=True
 if name=='Title':pf.space_after=Pt(9);pf.line_spacing=1.2
for b in list(doc.styles.element.iter(qn('w:pBdr'))):b.getparent().remove(b)
doc.core_properties.author='';doc.core_properties.title=s.splitlines()[0][2:];doc.core_properties.subject='结构工程论文审阅稿';doc.core_properties.comments=''
mp=el('m:mathPr');mp.append(el('m:mathFont',**{'m:val':'Cambria Math'}));doc.settings.element.append(mp)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=el('w:fldSimple',**{'w:instr':'PAGE'});rr=el('w:r');tt=el('w:t');tt.text='1';rr.append(tt);field.append(rr);footer._p.append(field)
eqs=[];inlinecount=0;tables=[];images=[]
pattern=re.compile(r'(\*\*.*?\*\*|\$[^$]+\$|\[[^]]+\]\([^)]+\))')
def inline(p,text,size=None):
 global inlinecount
 pos=0
 for m in pattern.finditer(text):
  if m.start()>pos:
   r=p.add_run(text[pos:m.start()]);font(r,size or 11)
  token=m.group()
  if token.startswith('$'):
   om=el('m:oMath')
   for x in parse_math(token[1:-1]):om.append(x)
   p._p.append(om);inlinecount+=1
  else:
   if token.startswith('**'):value=token[2:-2];bold=True
   else:value=token[1:token.index(']')];bold=False
   r=p.add_run(value);font(r,size or 11,bold)
  pos=m.end()
 if pos<len(text):
  r=p.add_run(text[pos:]);font(r,size or 11)
def para(text,english=False):
 p=doc.add_paragraph()
 if english:p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.line_spacing=1.13
 inline(p,text,10.5 if english else 11)
 return p
def equation(raw):
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
 r=p.add_run('  ('+str(len(eqs)+1)+')');font(r,10)
 eqs.append(raw)
def table(lines):
 cells=[[x.strip() for x in a.strip('|').split('|')] for a in lines];cells.pop(1)
 n=len(cells[0]);assert all(len(x)==n for x in cells)
 idx=len(tables)
 widths=[[1.3,5.1,5.1,5.1],[2.0,4.8,4.8,5.0],[3.5,3.1,1.9,2.7,2.7,2.7],[3.1,6.7,6.8]][idx]
 scale=16.6/sum(widths);widths=[w*scale for w in widths]
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
   inline(p,value,10)
   if i==0:
    for r in p.runs:r.bold=True
 tables.append(cells)
 p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=Pt(3);p.add_run().font.size=Pt(3)
lines=s.splitlines();i=0;inEnglish=False
while i<len(lines):
 line=lines[i].strip();i+=1
 if not line:continue
 if line.startswith('$$'):equation(line[2:-2]);continue
 if line.startswith('|'):
  ls=[line]
  while i<len(lines) and lines[i].strip().startswith('|'):ls.append(lines[i].strip());i+=1
  table(ls);continue
 if line.startswith('!['):
  m=re.fullmatch(r'!\[([^]]+)\]\(([^)]+)\)',line);img=(source.parent/m.group(2)).resolve();assert img.exists()
  p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.keep_with_next=True;p.paragraph_format.line_spacing=1.0
  p.add_run().add_picture(str(img),width=Cm(15.7));images.append(str(img));continue
 if line.startswith('# '):
  p=doc.add_paragraph(line[2:],style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;continue
 if line.startswith('## '):
  text=line[3:]
  if text.startswith('Effects of'):
   p=doc.add_paragraph(text,style='Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;inEnglish=True
  else:doc.add_heading(text,level=1);inEnglish=False
  continue
 if line.startswith('### '):doc.add_heading(line[4:],level=2);continue
 if line.startswith('**表'):
  p=doc.add_paragraph(line[2:-2],style='Caption');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.keep_with_next=True;continue
 if re.match(r'^图\d',line):
  p=doc.add_paragraph(line,style='Caption');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);p.paragraph_format.keep_with_next=False;continue
 if re.match(r'^\[\d+\]',line):
  p=para(line,True);p.paragraph_format.left_indent=Pt(18);p.paragraph_format.first_line_indent=Pt(-18)
  for r in p.runs:font(r,10)
 else:
  p=para(line,inEnglish or line.startswith('**关键词') or line.startswith('**Keywords'))
  if line.startswith('（'):p.paragraph_format.keep_together=True
  nxt=next((v.strip() for v in lines[i:] if v.strip()),'')
  if nxt.startswith('$$'):p.paragraph_format.keep_with_next=True
assert len(eqs)==5 and len(tables)==4 and len(images)==2
doc.save(target)
with zipfile.ZipFile(target) as z:
 root=etree.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 visible=''.join(root.xpath('//w:t/text() | //m:t/text()',namespaces=ns))
 assert not re.search(r'\\[A-Za-z]+|\$\$',visible)
 assert len(root.xpath('//w:tbl',namespaces=ns))==4
 mathcount=len(root.xpath('//m:oMath',namespaces=ns))
report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'display_math':len(eqs),'inline_math':inlinecount,'serialized_OMML':mathcount,'editable_tables':len(tables),'images':images,'all_math_native_OMML':True,'no_raw_latex_in_docx':True}
(O/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))

