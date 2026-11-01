from pathlib import Path
import argparse,json,zipfile,hashlib,re,datetime
from urllib.parse import unquote,urlsplit
from lxml import etree
ap=argparse.ArgumentParser();ap.add_argument('--docx',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);args=ap.parse_args()
S=Path(__file__).resolve().parent;R=S.parents[2]
source=R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v010.md'
text=source.read_text(encoding='utf8');contract=json.loads((S/'roles/role5/R012/word-content-contract.json').read_text(encoding='utf8'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','r':'http://schemas.openxmlformats.org/package/2006/relationships'}
blocks=[];lines=text.splitlines();i=0
while i<len(lines):
 if lines[i].strip().startswith('|'):
  a=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   a.append([x.strip() for x in lines[i].strip().strip('|').split('|')]);i+=1
  a.pop(1);blocks.append(a)
 else:i+=1
with zipfile.ZipFile(args.docx)as z:
 root=etree.fromstring(z.read('word/document.xml'));rels=etree.fromstring(z.read('word/_rels/document.xml.rels'))
 tables=root.xpath('//w:tbl',namespaces=ns);assert len(tables)==len(blocks)==15
 numeric_fields=0
 for index,(table,raw)in enumerate(zip(tables,blocks),1):
  rows=table.xpath('./w:tr',namespaces=ns);assert len(rows)==len(raw),(index,'rowcount')
  for j,(row,values)in enumerate(zip(rows,raw)):
   cells=row.xpath('./w:tc',namespaces=ns);assert len(cells)==len(values),(index,j,'colcount')
   for k,(cell,value)in enumerate(zip(cells,values)):
    # Compare literal numeric cells; prose and math labels remain subject to visual inspection.
    if re.fullmatch(r'[+−\-]?\d+(?:\.\d+)?(?:%|/\d+)?',value):
     actual=''.join(cell.xpath('.//w:t/text()|.//m:t/text()',namespaces=ns))
     assert actual.replace('−','-')==value.replace('−','-'),(index,j,k,actual,value)
     numeric_fields+=1
 targets=[x.get('Target') for x in rels if x.get('Type','').endswith('/hyperlink')]
 assert all(x in targets for x in contract['required_clickable_reference_targets'])
 local_paths=[]
 for target in targets:
  if target.startswith(('http://','https://')):continue
  value=unquote(urlsplit(target).path)if target.startswith('file:')else unquote(target)
  if re.match(r'^/[A-Za-z]:/',value):value=value[1:]
  q=Path(value)
  if not q.is_absolute():q=args.docx.parent/q
  local_paths.append(q.resolve())
 assert Path(contract['required_local_supplement_entry']).resolve()in local_paths
 assert Path(contract['required_local_supplement_entry']).is_file()
 assert root.xpath('count(//w:hyperlink)',namespaces=ns)>=5
 math_count=int(root.xpath('count(//m:oMath)',namespaces=ns));assert math_count>=10
 media=[n for n in z.namelist()if n.startswith('word/media/')and not n.endswith('/')];assert len(media)==3
 expected=[]
 for relative in re.findall(r'!\[[^]]*\]\(([^)]+)\)',text):expected.append(hashlib.sha256((source.parent/relative).resolve().read_bytes()).hexdigest())
 actual_media=[hashlib.sha256(z.read(n)).hexdigest()for n in media]
 assert sorted(expected)==sorted(actual_media)
 assert not root.xpath('//w:pStyle[@w:val="Title"]/../w:pBdr',namespaces=ns)
 result={'checked_at':datetime.datetime.now().astimezone().isoformat(),'docx':str(args.docx.resolve()),'bytes':args.docx.stat().st_size,'sha256':hashlib.sha256(args.docx.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'table_blocks_exact':15,'literal_numeric_cells_exact':numeric_fields,'native_math_count':math_count,'three_original_figures_hash_match':True,'hyperlink_targets':targets,'all_four_external_citations_clickable':True,'local_S1_target_resolves_and_exists':True,'visual_qa':'Separate mandatory gate: root must actually inspect every final rendered page. This OOXML check alone does not certify layout.'}
 args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
