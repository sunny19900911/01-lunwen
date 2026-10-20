from pathlib import Path
import json,hashlib,re
p=Path(__file__).resolve().parent;repo=p.parents[4];f=repo/'papers/damping-output-boundaries/manuscript/modal-shear-session009-v008.md';b=f.read_bytes();s=b.decode('utf-8-sig');lines=s.splitlines();split=next(i for i,l in enumerate(lines) if l.strip()=='## 参考文献');refs={};ref_lines={}
for i,l in enumerate(lines[split+1:],split+2):
 m=re.match(r'^\[(\d+)\]\s+(.+)$',l)
 if m:refs[int(m[1])]=m[2];ref_lines[int(m[1])]=i
body='\n'.join(lines[:split]);tokens=[];excluded=[];first=[]
for m in re.finditer(r'\[(\d+(?:\s*[,，–—-]\s*\d+)*)\]',body):
 line=body.count('\n',0,m.start())+1;content=lines[line-1];nums=[]
 for piece in re.split(r'[,，]',m[1]):
  rr=re.split(r'[–—-]',piece);nums.extend(range(int(rr[0]),int(rr[-1])+1) if len(rr)>1 else [int(rr[0])])
 if nums==[0,200] and '积分' in content:excluded.append({'token':m[0],'line':line,'reason':'integration time interval'});continue
 tokens.append({'token':m[0],'line':line,'expanded':nums,'paragraph':content})
 for n in nums:
  if n not in first:first.append(n)
expected={1:['SONG J, CHU Y L, LIANG Z, LEE G C','2008','MCEER-08-0005'],2:['LONDOÑO J M, WAGG D J, NEILD S A','2014,43:1999–2013','10.1002/eqe.2433'],3:['CONDE J, BERNABEU A','2021,11:3089','10.3390/app11073089'],4:['COMPUTERS & STRUCTURES, INC.','Rev.15','Berkeley','2016','ISO#GEN062708M1']}
z={'input':{'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},'reference_payloads':refs,'reference_lines':ref_lines,'first_citation_order':first,'body_citations':tokens,'excluded_non_citations':excluded,'all_expected_fields_present':{n:all(x in refs.get(n,'') for x in fields) for n,fields in expected.items()},'all_citations_resolve':all(n in refs for t in tokens for n in t['expanded']),'first_order_sequential':first==[1,2,3,4],'all_references_cited':set(first)==set(refs),'priority_or_scarcity_terms':[{'line':i,'text':l} for i,l in enumerate(lines,1) if re.search('首次|研究较少|少有人|填补空白|尚无研究|鲜有研究',l)]}
(p/'R004-citation-checks.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in z.items() if k not in ['reference_payloads','body_citations']},ensure_ascii=False,indent=2));print(json.dumps([{'token':t['token'],'line':t['line']} for t in tokens],ensure_ascii=False))
