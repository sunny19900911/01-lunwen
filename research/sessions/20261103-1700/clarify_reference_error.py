from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
p=R/'papers/damping-output-boundaries/manuscript/p06-actual-main-session026-v002.md'
s=p.read_text(encoding='utf-8')
old='参照合成与软件绝对峰的相对差分别为0.00245%和0.00806%；项的符号按参照方向保留。'
new='相对差以软件绝对峰为分母，按参照合成绝对值与软件峰之差的未舍入值计算，分别为0.00245%和0.00806%；项的符号按参照方向保留。'
assert s.count(old)==1;t=s.replace(old,new)
out=p.with_name('p06-actual-main-session026-v003.md');assert not out.exists();out.write_text(t,encoding='utf-8',newline='\n')
sha=hashlib.sha256(out.read_bytes()).hexdigest()
record={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'output':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':sha,'old':old,'new':new,'scientific_values_changed':False,'reason':'Independent numeric final review optional reproducibility clarification; numerator is absolute-value comparison, not signed error.'}
(S/'final-precision-adoption.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=S/'word/author_word.py';txt=a.read_text(encoding='utf-8').replace('p06-actual-main-session026-v002.md','p06-actual-main-session026-v003.md').replace('p06-actual-main-session026-论文审阅稿-v002.docx','p06-actual-main-session026-论文审阅稿-v003.docx').replace('1ac98674b427c660650a0a80685e6445ee671ef649a5f21a9f036f1cc6bf6835',sha)
assert not (S/'word/local-cache/marker-receipt.json').exists();a.write_text(txt,encoding='utf-8',newline='\n')
st=json.loads((S/'status.json').read_text(encoding='utf-8'));st['scientific_manuscript']=record['output'];st['scientific_sha256']=sha;(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
