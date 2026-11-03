from pathlib import Path
import pypdfium2 as pdfium
import hashlib,json,datetime
P=Path(__file__).resolve().parent;R=P.parents[4];C=P/'local-cache';C.mkdir(exist_ok=True)
B=R.parent/'W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence'
sources=[('Londono2014',B/'Londono2014-WRRO_81371.pdf','cf7e469e0897cb095fa45274d5ff98c0269d68eb2084d128bc4c6775817a0a1d',[4,5,6,7,8],1997),('Conde2021',B/'Conde2021-applsci-11-03089.pdf','a7dd7754cb9840eefada8b698067a956a31cf392645979755cbfddadd78cadef',[3,4,6,7,8],0)]
out={'at':datetime.datetime.now().astimezone().isoformat(),'sources':[]}
for key,p,expected,pages,offset in sources:
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
 doc=pdfium.PdfDocument(p);blocks=[]
 for n in pages:
  page=doc[n-1];blocks.append(f'\n===PDF{n} / PRINT{n+offset}===\n'+page.get_textpage().get_text_range())
  dest=C/f'{key}-pdf{n}.png';assert not dest.exists();page.render(scale=1.5).to_pil().save(dest)
 (C/f'{key}-selected.txt').write_text(''.join(blocks),encoding='utf-8')
 out['sources'].append({'key':key,'path':str(p),'bytes':p.stat().st_size,'sha256':expected,'PDF_page_count':len(doc),'extracted_and_rendered_PDF_pages':pages,'print_page_offset':offset,'unchanged_after':hashlib.sha256(p.read_bytes()).hexdigest()==expected})
(P/'source-read-record.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
