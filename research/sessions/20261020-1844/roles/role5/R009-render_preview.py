"""Render a native Word PDF to individual page PNGs. Run after native export, then view every page."""
from pathlib import Path
import argparse,hashlib,json
import pypdfium2 as pdfium
ap=argparse.ArgumentParser()
ap.add_argument('--pdf',required=True,type=Path)
ap.add_argument('--out-dir',required=True,type=Path)
ap.add_argument('--scale',type=float,default=2)
args=ap.parse_args()
pdf=args.pdf.resolve();out=args.out_dir.resolve()
if not pdf.is_file():raise FileNotFoundError(pdf)
if out.exists():raise FileExistsError(out)
if not 1<=args.scale<=4:ap.error('scale must be 1..4')
out.mkdir()
p=pdfium.PdfDocument(str(pdf));pages=[]
for i,page in enumerate(p):
    png=out/f'page-{i+1:02}.png'
    image=page.render(scale=args.scale).to_pil();image.save(png)
    pages.append({'page':i+1,'png':str(png),'width':image.width,'height':image.height,
                  'text':page.get_textpage().get_text_range(),'actually_viewed':False})
report={'pdf':str(pdf),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
        'renderer':'pypdfium2 from bundled runtime','scale':args.scale,'pages':pages,
        'all_pages_visually_verified':False}
(out/'render-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pages':len(pages),'directory':str(out),'visual_review_required':True},ensure_ascii=False))
