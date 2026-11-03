from pathlib import Path
import hashlib,json,ast
H=Path(__file__).resolve().parent;R=H.parents[4]
old=R/'research/sessions/20261102-1917/roles/role5/R004'
s=(old/'build_word.py').read_text(encoding='utf-8')
before="  if idx==1:widths=[2.1,2.5,2.0,3.0,3.0,2.4]\n  if idx==2:widths=[2.1,2.0,2.6,2.6,2.0,3.7]\n  if idx==3:widths=[1.4,3.1,3.1,2.3,3.8,2.5]"
after="""  header=cells[0]
  if header[0]=='方向/楼层':widths=[2.1,2.5,2.0,3.0,3.0,2.4]
  elif header[:2]==['工况','楼层']:widths=[2.1,2.0,2.6,2.6,2.0,3.7]
  elif header==['量','SHW3X','SHW4X']:widths=[8.0,4.5,4.5]
  elif len(header)==6 and header[1].startswith('QT'):widths=[1.4,3.1,3.1,2.3,3.8,2.5]
""".rstrip()
assert s.count(before)==1;s=s.replace(before,after)
before="   p=doc.add_paragraph(line[2:],style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;continue"
after="""   title=line[2:];p=doc.add_paragraph(style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
   if '结构' in title:
    first,last=title.split('结构',1);p.add_run(first+'结构').add_break();p.add_run(last)
   else:p.add_run(title)
   continue"""
assert s.count(before)==1;s=s.replace(before,after)
s=s.replace("(len(cells)<=6 and i<len(cells)-1)","(len(cells)<=8 and i<len(cells)-1)")
ast.parse(s)
for name,raw in [('build_word.py',s.encode('utf-8')),('math_omml.py',(old/'math_omml.py').read_bytes()),('render_review.py',(old/'render_review.py').read_bytes())]:
 p=H/name;assert not p.exists();p.write_bytes(raw)
print(json.dumps({'builder_ready':True,'table_widths':'header-based, not old hard indexes','title_break':'after 结构','native_math_reused':True,'marker_not_yet_run':True}))
