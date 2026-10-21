from pathlib import Path
import re,copy,hashlib,json,zipfile
from lxml import etree
R=Path(r'E:\11-工作\001-workbuddy spaceV1\001-workbuddy space\109-论文写作\01-lunwen');O=R/'research/sessions/20261021-2020/roles/role5';M=R/'papers/damping-output-boundaries/manuscript'
src=M/'jgjg-session011-论文审阅稿-v004-r2.docx';out=M/'jgjg-session011-论文审阅稿-v004-排版稿.docx'
assert not out.exists()
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';NS={'w':W}
qn=lambda n:'{'+W+'}'+n
pattern=re.compile(r'(?<![A-Za-z0-9])([PMVt])_([BM](?:,s,c)?)|(?<![A-Za-z0-9])(r)_(at|peak)|(?<![A-Za-z0-9])(n)_(e)(?![a-z])')
with zipfile.ZipFile(src) as z:
 original=z.read('word/document.xml');root=etree.fromstring(original)
 original_visible=''.join(root.xpath('//w:t/text()',namespaces=NS))
 counts={};refs=False
 for p in root.xpath('//w:body//w:p',namespaces=NS):
  text=''.join(p.xpath('.//w:t/text()',namespaces=NS))
  if text.strip()=='参考文献':refs=True
  if refs:continue
  for run in list(p.xpath('./w:r',namespaces=NS)):
   ts=run.findall(qn('t'))
   if len(ts)!=1 or any(x.tag not in [qn('rPr'),qn('t')] for x in run):continue
   text=ts[0].text or ''
   if '://' in text:continue
   hits=list(pattern.finditer(text))
   if not hits:continue
   parent=run.getparent();index=parent.index(run);parts=[];pos=0
   def piece(value,sub=False):
    if not value:return
    rr=etree.Element(qn('r'));pr=run.find(qn('rPr'))
    if pr is not None:rr.append(copy.deepcopy(pr))
    if sub:
     rp=rr.find(qn('rPr'))
     if rp is None:rp=etree.SubElement(rr,qn('rPr'))
     for old in list(rp.findall(qn('vertAlign'))):rp.remove(old)
     va=etree.SubElement(rp,qn('vertAlign'));va.set(qn('val'),'subscript')
    tt=etree.SubElement(rr,qn('t'));tt.set('{http://www.w3.org/XML/1998/namespace}space','preserve');tt.text=value;parts.append(rr)
   for hit in hits:
    piece(text[pos:hit.start()])
    groups=hit.groups();base=groups[0] or groups[2] or groups[4];sub=groups[1] or groups[3] or groups[5]
    piece(base);piece(sub,True);counts[hit.group()]=counts.get(hit.group(),0)+1;pos=hit.end()
   piece(text[pos:]);parent.remove(run)
   for off,rr in enumerate(parts):parent.insert(index+off,rr)
 new_visible=''.join(root.xpath('//w:t/text()',namespaces=NS))
 assert re.findall(r'\d+(?:\.\d+)?',original_visible)==re.findall(r'\d+(?:\.\d+)?',new_visible)
 assert original_visible.split('参考文献',1)[1]==new_visible.split('参考文献',1)[1]
 altered=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as dest:
  for item in z.infolist():dest.writestr(item,altered if item.filename=='word/document.xml' else z.read(item.filename))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'input':str(src),'input_sha256':sha(src),'output':str(out),'output_sha256':sha(out),'variable_counts':counts,'all_numeric_strings_identical':True,'references_identical':True,'all_other_package_parts_identical':True,'source_md_unchanged':sha(M/'jgjg-session011-v004.md')=='c30cbbccecc21be395ad9cf55de3f842f806cfea8372b72d180d240a3e532b7a'}
(O/'R002-variable-format-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
