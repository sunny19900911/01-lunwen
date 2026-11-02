from pathlib import Path
O=Path(__file__).resolve().parent
p=O/'build_word.py';s=p.read_text(encoding='utf-8')
s=s.replace('from docx.enum.text import WD_ALIGN_PARAGRAPH','from docx.enum.text import WD_ALIGN_PARAGRAPH\nfrom docx.enum.section import WD_SECTION_START')
s=s.replace("s,expected,default_layout,_=inspect_source(source);layout=layout or default_layout","s,expected,default_layout,_=inspect_source(source);layout=layout or default_layout")
s=s.replace("sec.page_width=Cm(21.59);sec.page_height=Cm(27.94)","sec.page_width=Pt(595.3);sec.page_height=Pt(841.9)")
s=s.replace("sec.top_margin=Cm(2.0);sec.bottom_margin=Cm(1.9);sec.left_margin=Cm(2.25);sec.right_margin=Cm(2.25)","sec.top_margin=Pt(76.55);sec.bottom_margin=Pt(56.7);sec.left_margin=Pt(56.7);sec.right_margin=Pt(56.7)")
s=s.replace("sec.footer_distance=Cm(1.0)","sec.footer_distance=Pt(42.55);sec.header_distance=Pt(42.55)")
s=s.replace("('Normal',11,False,'SimSun'),('Title',17,True,'SimHei'),('Subtitle',11.5,True,'SimSun'),('Heading 1',13,True,'SimHei'),('Heading 2',11.5,True,'SimHei'),('Caption',10,False,'SimSun')","('Normal',10.5,False,'SimSun'),('Title',22,False,'SimSun'),('Subtitle',10.5,True,'SimSun'),('Heading 1',10.5,True,'SimHei'),('Heading 2',10.5,True,'SimHei'),('Caption',9,False,'SimSun')")
s=s.replace("pf.line_spacing=1.15","pf.line_spacing=1.0").replace("pf.space_after=Pt(4)","pf.space_after=Pt(0)")
s=s.replace("pf.space_before=Pt(9);pf.space_after=Pt(5)","pf.space_before=Pt(5);pf.space_after=Pt(3)")
s=s.replace("pf.space_after=Pt(3);pf.first_line_indent=Pt(22)","pf.space_after=Pt(0);pf.first_line_indent=Pt(21)")
s=s.replace("p.paragraph_format.line_spacing=1.13","p.paragraph_format.line_spacing=1.0")
s=s.replace("inline(p,text,10.5 if english else 11)","inline(p,text,9 if english or not body_started else 10.5)")
s=s.replace("font(r,10)","font(r,9)")
s=s.replace("size or 11","size or 10.5")
s=s.replace("widths=layout['tables'][idx]['widths_cm']\n  if idx==2:widths=[2.05,2.25,2.55,.95,2.75,3,2.45]","widths=layout['tables'][idx]['widths_cm']\n  if idx==1:widths=[2.1,2.5,2.0,3.0,3.0,2.4]\n  if idx==2:widths=[2.1,2.0,2.6,2.6,2.0,3.7]\n  if idx==3:widths=[1.4,3.1,3.1,2.3,3.8,2.5]")
s=s.replace("inline(p,value,9.5)","inline(p,value,8.5)")
s=s.replace("inline(p,line,9.5)","inline(p,line,9)")
s=s.replace("layout.get('figure_width_cm',15.8)","layout.get('figure_width_cm',15.5)")
s=s.replace("font(r,size or 10.5)","font(r,size or 10.5)")
start=s.index('  nonlocal inlinecount\n  # Mathematical tokens only;')
end=s.index('\n def inline(p,text,size=None):',start)
s=s[:start]+'''  nonlocal inlinecount
  # Exact symbol grammar: one-letter indices unless explicitly grouped.
  # Adjacent operands never become part of an unbraced index.
  token_re=re.compile(r"(?:[A-Za-zΑ-ωℓΣ][A-Za-z0-9Α-ωℓΣ_^'=<>≤≥−+×·|/()[\\]{}²³⁻¹₂₃₅₈₀₁₇ᵀ]*_[A-Za-z0-9]+(?:[,_A-Za-z0-9=<>≤≥−+|/()[\\]{}.]*)|[A-Za-zΑ-ωℓΣ]+_[A-Za-z0-9]+)")
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
''' +s[end:]
# Source-specific mathematics are explicitly braced before token processing.
insert="""
 'M=diag(1,1.2,.8)':r'M=\\operatorname{diag}(1,1.2,.8)',
 'K=[[2.4,−1,0],[−1,1.7,−.7],[0,−.7,.7]]':r'K=\\begin{bmatrix}2.4&-1&0\\\\-1&1.7&-.7\\\\0&-.7&.7\\end{bmatrix}',
 'QD=Σn_eP':r'Q_D=\\sum n_e P',
 'ℓ_s':r'\\ell_s',
 'P_B':r'P_B', 'P_M':r'P_M', 't_B':r't_B', 't_M':r't_M',
 'r_peak':r'r_{\\mathrm{peak}}', 'r_at':r'r_{\\mathrm{at}}',
 'c_r':r'c_r', 'c_V':r'c_V',
"""
s=s.replace('EXPLICIT_INLINE_MATH = {','EXPLICIT_INLINE_MATH = {'+insert)
# Substitute literals only in prose spans; never alter existing $...$.
s=s.replace("  for literal,latex in EXPLICIT_INLINE_MATH.items():\n   text=text.replace(literal,'$'+latex+'$')", "  pieces=re.split(r'(\\$[^$]+\\$)',text)\n  literals=sorted(EXPLICIT_INLINE_MATH,key=len,reverse=True)\n  exact=re.compile('|'.join(re.escape(v) for v in literals))\n  for pi in range(0,len(pieces),2):\n   pieces[pi]=exact.sub(lambda mt:'$'+EXPLICIT_INLINE_MATH[mt.group()]+'$',pieces[pi])\n  text=''.join(pieces)")
# Continuous column sections; wide equations, tables and figures use full width.
anchor=' eqs=[];inlinecount=0;tables=[];images=[]'
s=s.replace(anchor,''' body_started=False
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
''' +anchor)
s=s.replace("  if line.startswith('$$'):\n   raw=line[2:]","  if line.startswith('$$'):\n   set_columns(1)\n   raw=line[2:]")
s=s.replace("   equation(raw.rstrip()[:-2]);continue","   equation(raw.rstrip()[:-2]);set_columns(2);continue")
s=s.replace("   table(ls);continue","   table(ls);set_columns(2);continue")
s=s.replace("  if line.startswith('!['):\n   m=", "  if line.startswith('!['):\n   set_columns(1)\n   m=")
s=s.replace("  if line.startswith('## '):\n   text=line[3:]","  if line.startswith('## '):\n   text=line[3:]\n   if text.startswith('1 '):body_started=True;set_columns(2)")
s=s.replace("  if line.startswith('**表'):\n   p=", "  if line.startswith('**表'):\n   set_columns(1)\n   p=")
s=s.replace("p.paragraph_format.keep_with_next=False;continue","p.paragraph_format.keep_with_next=False;set_columns(2);continue")
# MD figure captions are plain '图n', not bold; preserve their pair and restore columns.
s=s.replace("  if re.match(r'^\\[\\d+\\]',line):", "  if re.match(r'^图\\d+ ',line):\n   p=doc.add_paragraph(style='Caption');inline(p,line,9);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Pt(0);set_columns(2);continue\n  if re.match(r'^\\[\\d+\\]',line):")
p.write_text(s,encoding='utf-8')
