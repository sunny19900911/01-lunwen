from pathlib import Path
from collections import Counter
import hashlib,json,re,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
p=R/'papers/damping-output-boundaries/manuscript/p06-actual-timing-session027-v003.md'
src=p.read_text(encoding='utf-8');assert hashlib.sha256(p.read_bytes()).hexdigest()=='61bce79bc063aa05deef28508cdd0189d93341162cca58475d64481402e7fb18'
i=src.index('![图4 ');j=src.index('**表7 ',i);block=src[i:j]
body=src[:i]+src[j:];k=body.index('**表6 ');text=body[:k]+block+body[k:]
assert Counter(''.join(src.split()))==Counter(''.join(text.split()))
assert re.findall(r'\$\$.*?\$\$',src,re.S)==re.findall(r'\$\$.*?\$\$',text,re.S)
assert re.findall(r'^\|.*$',src,re.M)==re.findall(r'^\|.*$',text,re.M)
assert re.findall(r'!\[[^\]]*\]\([^)]+\)',src)==re.findall(r'!\[[^\]]*\]\([^)]+\)',text)
out=p.with_name('p06-actual-timing-session027-v004.md');assert not out.exists();out.write_text(text,encoding='utf-8',newline='\n')
record={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'output':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'change':'Move the unchanged B/D/QD figure and caption before Table6 so the large figure need not force a 5cm gap after the preceding two-column explanation. No font/image size changes.','all_nonwhitespace_characters_preserved':True,'tables_equations_figure_order_preserved':True}
(S/'layout-reflow-check.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
