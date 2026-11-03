from pathlib import Path
import json,hashlib,re,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
p=R/'papers/damping-output-boundaries/manuscript/p06-actual-main-session026-v001.md'
b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='a11102490ebe100d8bdf91069bd1460364c4a9c5bfd677c0b8b956c7dec7dcdb'
s=b.decode('utf-8');old='不将其中的模态项写成实际非线性方案的逐阶实测分担';new='其中的模态项不作为实际非线性方案的原生逐阶剪力'
assert s.count(old)==1;t=s.replace(old,new)
for pattern in [r'\$\$.*?\$\$',r'^\|.*$',r'!\[[^\]]*\]\([^)]+\)']:
    assert re.findall(pattern,s,re.S if pattern.startswith('\\$') else re.M)==re.findall(pattern,t,re.S if pattern.startswith('\\$') else re.M)
out=p.with_name('p06-actual-main-session026-v002.md');assert not out.exists();out.write_text(t,encoding='utf-8',newline='\n')
record={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source_sha256':hashlib.sha256(b).hexdigest(),'output':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'must':0,'adopted_optional':{'old':old,'new':new},'all_tables_equations_figures_unchanged':True,'reviews':['roles/audit/draft-final-checks.json','roles/method/final-review.md']}
(S/'final-text-adoption.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
st=json.loads((S/'status.json').read_text(encoding='utf-8'));st.update({'phase':'word-production','no_new_numeric_experiments':True,'no_new_scientific_dispatch':True,'scientific_manuscript':record['output'],'scientific_sha256':record['sha256']});(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
oldscript=(R/'research/sessions/20261103-1458/word/author_word.py').read_text(encoding='utf-8')
oldscript=oldscript.replace('p06-actual-damper-session025-v002.md','p06-actual-main-session026-v002.md').replace('p06-actual-damper-session025-论文审阅稿-v002.docx','p06-actual-main-session026-论文审阅稿-v002.docx').replace('f5e12aa1a68cfa5a81473a8f1ef09fc4540cbf1e10207a25ca976834794d0a87',record['sha256'])
author=S/'word/author_word.py';assert not author.exists();author.write_text(oldscript,encoding='utf-8',newline='\n')
print(json.dumps(record,ensure_ascii=False))
