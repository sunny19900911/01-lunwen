from pathlib import Path
import zipfile,json,hashlib,re
from lxml import etree as E
H=Path(__file__).resolve().parent;R=H.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-actual-damper-session025-v003.md';dst=src.with_name('p06-actual-damper-session025-v004.md')
source_doc=M/'p06-actual-damper-session025-论文审阅稿-v003.docx';target_doc=source_doc.with_name('p06-actual-damper-session025-论文审阅稿-v004.docx')
old='4.3.2 共有六工况的分层响应与两类控制输入';new='4.3.2 分层响应与两类控制输入'
s=src.read_text(encoding='utf-8');assert s.count(old)==1 and not dst.exists() and not target_doc.exists()
t=s.replace(old,new);dst.write_text(t,encoding='utf-8',newline='\n')
assert re.findall(r'(?:^\|.*\n)+',s,re.M)==re.findall(r'(?:^\|.*\n)+',t,re.M)
assert json.loads((H/'word/local-cache/marker-receipt.json').read_text(encoding='utf-8'))['success_count']==1
with zipfile.ZipFile(source_doc) as z:
    entries=[(n,z.read(n.filename)) for n in z.infolist()]
root=E.fromstring(next(b for n,b in entries if n.filename=='word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
nodes=root.findall('.//w:t',ns);matched=[x for x in nodes if x.text==old];assert len(matched)==1;matched[0].text=new
with zipfile.ZipFile(target_doc,'x',compression=zipfile.ZIP_DEFLATED) as out:
    for n,b in entries:
        out.writestr(n,E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True) if n.filename=='word/document.xml' else b)
with zipfile.ZipFile(source_doc) as a,zipfile.ZipFile(target_doc) as b:
    changed=[x for x in a.namelist() if a.read(x)!=b.read(x)]
assert changed==['word/document.xml']
d={'source':dst.relative_to(R).as_posix(),'source_bytes':dst.stat().st_size,'source_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'docx':target_doc.relative_to(R).as_posix(),'docx_bytes':target_doc.stat().st_size,'docx_sha256':hashlib.sha256(target_doc.read_bytes()).hexdigest(),'edit':{'from':old,'to':new,'count':1},'only_package_part_changed':changed,'scientific_values_figures_math_unchanged':True,'marker_success_count_still':1,'reason':'Avoid final single-character line in subsection heading observed on final render page8'}
(H/'final-heading-format-check.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(d,ensure_ascii=False))
