from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
p=R/'papers/damping-output-boundaries/manuscript/p06-actual-timing-session027-v002.md'
text=p.read_text(encoding='utf-8');old='当两时刻降低量之差大于原需求差时，后一时刻在实际方案中更大。';new='当两时刻降低量之差大于原需求差时，t₂时刻在实际方案中更大。'
assert text.count(old)==1;text=text.replace(old,new)
out=p.with_name('p06-actual-timing-session027-v003.md');assert not out.exists();out.write_text(text,encoding='utf-8',newline='\n')
sha=hashlib.sha256(out.read_bytes()).hexdigest()
a=S/'补充A-线性机制与实际模态恢复.md';b=a.read_text(encoding='utf-8');newb=b.replace('### 主导模态项与反向抵消的机制解释','### A1.1 主导模态项与反向抵消的机制解释').replace('### 5.3 目标层内力与模态数量检查','### A1.2 目标层内力与模态数量检查').replace('表7','表A1')
a.write_text(newb,encoding='utf-8',newline='\n')
w=S/'word/author_word.py';s=w.read_text(encoding='utf-8');assert not (S/'word/local-cache/marker-receipt.json').exists();s=s.replace('p06-actual-timing-session027-v002.md','p06-actual-timing-session027-v003.md').replace('p06-actual-timing-session027-论文审阅稿-v002.docx','p06-actual-timing-session027-论文审阅稿-v003.docx').replace('1a16772c55cfc6d3cb66985729ef9c130a34d6e74c817e59a1e93484deee6103',sha);w.write_text(s,encoding='utf-8',newline='\n')
record={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'output':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':sha,'old':old,'new':new,'reason':'t2 means actual-scheme peak, which need not occur later than t1 in clock time; appendix headings renumbered A1.1/A1.2/TableA1. No scientific values changed.'}
(S/'final-time-label-adoption.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
st=json.loads((S/'status.json').read_text(encoding='utf-8'));st['scientific_manuscript']=record['output'];st['scientific_sha256']=sha;(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
