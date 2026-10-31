
from pathlib import Path
import importlib.util,subprocess,sys,json,datetime
import pypdfium2 as pdfium
O=Path(__file__).resolve().parent
skill=Path(r'C:/Users/mj528/.codex/plugins/cache/openai-primary-runtime/documents/26.1025.11240/skills/documents/render_docx.py')
spec=importlib.util.spec_from_file_location('packaged_document_renderer',skill)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def word_convert(doc_path,user_profile,convert_tmp_dir,stem,verbose=False):
 target=str(Path(convert_tmp_dir)/(stem+'.pdf'))
 p=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(O/'export_word_pdf.ps1'),str(Path(doc_path).resolve()),target],capture_output=True,text=True,timeout=55)
 if p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
 if not Path(target).exists():raise RuntimeError('Word did not export PDF')
 return target,'Fallback: hidden Microsoft Word COM PDF export; '+p.stdout
def raster(pdf_path,dpi=150,fmt='png',thread_count=1,output_folder=None,paths_only=True,output_file='page',**kwargs):
 doc=pdfium.PdfDocument(pdf_path)
 output=[]
 for i in range(len(doc)):
  page=doc[i];bitmap=page.render(scale=dpi/72)
  dest=Path(output_folder)/(f'page0001-{i+1:02d}.png')
  bitmap.to_pil().save(dest)
  bitmap.close();page.close();output.append(str(dest))
 count=len(doc);doc.close()
 (O/'render-engine.json').write_text(json.dumps({'packaged_renderer':str(skill),'converter':'hidden Microsoft Word COM PDF export','rasterizer':'bundled pypdfium2','pages':count,'dpi':dpi,'initial_canonical_attempt':'failed: LibreOffice soffice.exe unavailable; no user LibreOffice used','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return output
m.convert_to_pdf=word_convert
m.convert_from_path=raster
m.main()
