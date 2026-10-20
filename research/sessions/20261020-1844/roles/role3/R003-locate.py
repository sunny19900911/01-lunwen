from pathlib import Path
from pypdf import PdfReader
import re,json
p=Path(__file__).resolve().parent;c=p/'R003-local-cache';f=Path(r'E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/W5-重燃双塔连体/research/maxwell-20261017/roles/verification/csi-analysis-reference-2016.pdf');r=PdfReader(f);out=[]
for n in range(388,404):
 s=r.pages[n-1].extract_text() or '';(c/f'CSI-p{n}.txt').write_text(s,encoding='utf-8')
 for term in ['ninety','90 percent','90%','residual','missing','static correction','truncat','participating mass','participation ratio','100 percent']:
  for m in list(re.finditer(re.escape(term),s,re.I))[:4]:out.append({'pdf_page':n,'term':term,'context':s[max(0,m.start()-130):m.end()+230]})
(c/'CSI-selected-hits.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
