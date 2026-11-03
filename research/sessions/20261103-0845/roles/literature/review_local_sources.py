from pathlib import Path
import json,hashlib,datetime
import pypdfium2 as pdfium

OUT=Path(__file__).resolve().parent
R=OUT.parents[4]
C=OUT/'local-cache';C.mkdir(exist_ok=True)
sources=[('Liu2004',R.parent/'W6-重燃强连接双塔/01-文献/参考文献-Liu2004-性能目标与模态阻尼配置.pdf','9e8a3b997f91d57a0f816b0e9f859cc8f00d1d7510aa2b7eb1e1eb15b14a1d17',list(range(15,20)),66),('Song2008',R.parent/'W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/MCEER-08-0005.pdf','941a58f7a8e88975405ccfdfeea412a42d9f982ca7ff3c6a055a93c8c25fda48',list(range(123,128)), -18)]
result={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':[]}
for key,p,expected,pages,offset in sources:
 actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==expected,(p,actual)
 doc=pdfium.PdfDocument(p);texts=[];record={'key':key,'path':str(p),'bytes':p.stat().st_size,'sha256':actual,'pdf_pages':len(doc),'extracted_pages':[],'rendered_pages':[]}
 for n in pages:
  page=doc[n-1];text=page.get_textpage().get_text_range();texts.append(f'\n===PDF {n}; PRINT {n+offset}===\n{text}')
  dest=C/f'{key}-pdf{n}-print{n+offset}.png';assert not dest.exists()
  page.render(scale=1.5).to_pil().save(dest)
  record['extracted_pages'].append({'pdf':n,'print':n+offset,'characters':len(text)})
  record['rendered_pages'].append(str(dest.relative_to(OUT)))
 (C/f'{key}-selected-pages.txt').write_text(''.join(texts),encoding='utf-8')
 record['source_unchanged_after']=hashlib.sha256(p.read_bytes()).hexdigest()==expected
 result['sources'].append(record)
result['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'source-read-record.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
