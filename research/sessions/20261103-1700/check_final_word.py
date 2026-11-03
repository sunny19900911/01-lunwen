"""Read-only final P06 DOCX identity gate; visual review remains separate."""
from pathlib import Path
from decimal import Decimal
import argparse, hashlib, json, re, zipfile
from lxml import etree as E

ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--docx',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';M='http://schemas.openxmlformats.org/officeDocument/2006/math';NS={'w':W,'m':M}
def sha(b):return hashlib.sha256(b).hexdigest()
def text(el):
 return ''.join(n.text or '' for n in el.iter() if n.tag in ['{'+W+'}t','{'+M+'}t'])
def nums(t):
 return tuple(Decimal(x) for x in re.findall(r'[-+]?(?:\d+(?:\.\d+)?|\.\d+)',t.replace('−','-').replace('–','-')))
def cases(t):return re.findall(r'(?:SHW\d+|RH\d+|R\d+)[XY]',t)
md=a.source.read_text(encoding='utf-8');source_bytes=a.source.read_bytes();tables=[];current=[]
for line in md.splitlines()+['']:
 if line.startswith('|'):
  row=[x.strip() for x in line.strip().strip('|').split('|')]
  if not all(re.fullmatch(r'[:\- ]+',x) for x in row):current.append(row)
 elif current:
  tables.append(current);current=[]
with zipfile.ZipFile(a.docx) as z:
 doc=E.fromstring(z.read('word/document.xml'));rels=E.fromstring(z.read('word/_rels/document.xml.rels'))
 actual=[]
 for tb in doc.findall('.//w:tbl',NS):
  actual.append([[text(tc) for tc in tr.findall('w:tc',NS)] for tr in tb.findall('w:tr',NS)])
 matches=[];used=set();checked=0
 for source in tables:
  chosen=None
  for ix,target in enumerate(actual):
   if ix in used or len(target)!=len(source) or any(len(x)!=len(y) for x,y in zip(source,target)):continue
   ok=True
   for sr,tr in zip(source[1:],target[1:]):
    for sv,tv in zip(sr,tr):
     if nums(sv)!=nums(tv) or cases(sv)!=cases(tv):ok=False
   if ok:chosen=ix;break
  assert chosen is not None,('Source table has no exact numeric/key match',source[0])
  used.add(chosen);checked+=sum(bool(nums(v)) for row in source[1:] for v in row)
  matches.append({'source_header':source[0],'docx_table_index':chosen,'rows_including_header':len(source),'cols':len(source[0])})
 source_images=[]
 for label,target in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)',md):
  p=(a.source.parent/target).resolve();assert p.is_file();source_images.append({'label':label,'sha256':sha(p.read_bytes())})
 media={n:sha(z.read(n)) for n in z.namelist() if n.startswith('word/media/') and not n.endswith('/')}
 assert set(media.values())=={x['sha256'] for x in source_images},'Original figure bytes changed or unexpected raster formulas'
 math=doc.findall('.//m:oMath',NS);flat=[''.join(text(x).split()) for x in math];allmath=' '.join(flat)
 assert len(math)>=len(re.findall(r'\$\$(.*?)\$\$',md,re.S)), 'Missing native math'
 assert any('argmin' in x and 'argmax' in x and 'P' in x and 'D' in x for x in flat),'Selectors or PM operand missing'
 fractions=doc.findall('.//m:f',NS);pairs=[]
 for f in fractions:
  nu=f.find('m:num',NS);de=f.find('m:den',NS)
  if nu is not None and de is not None:pairs.append((''.join(text(nu).split()),''.join(text(de).split())))
 assert any('PD' in n and d=='PB' for n,d in pairs),'Peak ratio numerator/denominator lost'
 assert any('PD' in n and 'A' in n and d=='PB' for n,d in pairs),'d numerator or baseline denominator lost'
 assert any('V' in x and 'q' in x and ('φ' in x or 'ϕ' in x) for x in flat),'Modal shear summand lost q or phi'
 if 'bmatrix' in md:assert doc.findall('.//m:m',NS),'Native K matrix missing'
 links=[dict(x.attrib) for x in rels if x.attrib.get('Type','').endswith('/hyperlink')]
 assert any('20261103-1700' in x.get('Target','') for x in links),'Current complete engineering supplementary link missing'
 assert any('engineering-data-and-full-tables' in x.get('Target','') for x in links),'Engineering supplementary hyperlink missing'
 if 'SHW3X-SHW4X-辅助分析资料-v002.md' in md:
  assert any('SHW3X-SHW4X-' in x.get('Target','') and 'v002.md' in x.get('Target','') for x in links),'New auxiliary supplement hyperlink missing'
 core=E.fromstring(z.read('docProps/core.xml'))
 creators=core.findall('{http://purl.org/dc/elements/1.1/}creator')+core.findall('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy')
 assert all(not (x.text or '').strip() for x in creators),'Author metadata must stay blank until supplied by human'
 sections=[]
 for s in doc.findall('.//w:sectPr',NS):
  size=s.find('w:pgSz',NS);marg=s.find('w:pgMar',NS);cols=s.find('w:cols',NS);grid=s.find('w:docGrid',NS)
  assert size is not None and abs(int(size.get('{'+W+'}w'))-11906)<=10 and abs(int(size.get('{'+W+'}h'))-16838)<=10,'A4 page size required'
  assert marg is not None
  for k,expected in [('top',1531),('bottom',1134),('left',1134),('right',1134)]:assert abs(int(marg.get('{'+W+'}'+k))-expected)<=20,'Official-reference margins mismatch'
  sections.append({'columns':int(cols.get('{'+W+'}num','1')) if cols is not None else 1,'column_gap_twips':cols.get('{'+W+'}space') if cols is not None else None,'grid_line_pitch_twips':grid.get('{'+W+'}linePitch') if grid is not None else None})
 assert {1,2}<={s['columns'] for s in sections},'Single-column front matter and two-column body required'
 result={'source':str(a.source.resolve()),'source_sha256':sha(source_bytes),'docx':str(a.docx.resolve()),'docx_bytes':a.docx.stat().st_size,'docx_sha256':sha(a.docx.read_bytes()),'source_tables_matched':matches,'numeric_table_cells_checked':checked,'native_OMML_count':len(math),'native_fractions':len(fractions),'native_matrices':len(doc.findall('.//m:m',NS)),'source_figures_unchanged':source_images,'embedded_media':media,'hyperlinks':links,'author_metadata_empty':True,'A4_and_official_reference_margins':True,'section_layouts':sections,'visual_QA_separate_required':True}
 assert not a.out.exists(),'Keep prior verification output'
 a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:result[k] for k in ['docx_sha256','docx_bytes','numeric_table_cells_checked','native_OMML_count']},ensure_ascii=False))
