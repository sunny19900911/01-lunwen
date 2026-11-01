from pathlib import Path
import argparse,subprocess,sys,os,json
import pypdfium2 as pdfium
SKILL=Path(r'C:/Users/mj528/.codex/plugins/cache/openai-primary-runtime/documents/26.1025.11240/skills/documents/render_docx.py')
PS_SCRIPT=r"""
$ErrorActionPreference='Stop'
$word=$null
$doc=$null
$closeSave=$false
try {
 $word=New-Object -ComObject Word.Application
 $word.Visible=$false
 $word.DisplayAlerts=0
 $src=$env:CODEX_DOCX_RENDER_INPUT
 $pdf=$env:CODEX_DOCX_RENDER_PDF
 $confirm=$false
 $readonly=$true
 $doc=$word.Documents.Open([ref]$src,[ref]$confirm,[ref]$readonly)
 $doc.ExportAsFixedFormat($pdf,17)
} finally {
 try {
  if($null -ne $doc){try{$doc.Close([ref]$closeSave)}finally{[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)}}
 } finally {
  if($null -ne $word){try{$word.Quit([ref]$closeSave)}finally{[void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)}}
 }
}
"""
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True)
 ap.add_argument('--allow-word-fallback',action='store_true');ap.add_argument('--dpi',type=int,default=150)
 args=ap.parse_args();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
 canonical=subprocess.run([sys.executable,str(SKILL),str(args.input.resolve()),'--output_dir',str(out),'--emit_pdf'],capture_output=True,text=True,timeout=120)
 log=out/'canonical-render.log';log.write_text(canonical.stdout+'\n'+canonical.stderr,encoding='utf-8')
 if canonical.returncode==0 and list(out.glob('page-*.png')):return
 if not args.allow_word_fallback:raise RuntimeError(f'Canonical render failed; inspect {log}')
 pdf=out/(args.input.stem+'.pdf');env=os.environ.copy();env['CODEX_DOCX_RENDER_INPUT']=str(args.input.resolve());env['CODEX_DOCX_RENDER_PDF']=str(pdf)
 result=subprocess.run(['powershell.exe','-NoProfile','-Command',PS_SCRIPT],env=env,capture_output=True,text=True,timeout=120)
 (out/'word-render.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
 if result.returncode!=0 or not pdf.is_file():raise RuntimeError('Word PDF export failed; see word-render.log')
 doc=pdfium.PdfDocument(str(pdf));pages=[]
 for i in range(len(doc)):
  page=doc[i];bitmap=page.render(scale=args.dpi/72);target=out/f'page-{i+1}.png'
  bitmap.to_pil().save(target);bitmap.close();page.close();pages.append(str(target))
 doc.close()
 (out/'render-report.json').write_text(json.dumps({'converter':'independent hidden Word COM after logged canonical failure','rasterizer':'bundled PDFium','dpi':args.dpi,'pages':pages,'actual_visual_review_required':True},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
