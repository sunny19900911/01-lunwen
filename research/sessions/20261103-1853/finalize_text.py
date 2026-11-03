from pathlib import Path
import datetime,json,hashlib,re
S=Path(__file__).resolve().parent;R=S.parents[2]
p=R/'papers/damping-output-boundaries/manuscript/p06-actual-timing-session027-v001.md'
b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='2a703d4b763b720f9f6bb5c44eadb442bafae66b5d134b3904ffcbdd07647938'
text=b.decode('utf-8')
changes=[
 ('本节直接比较实际方案D与基准B的原生时程，不再用模态增阻尼参考解释实际方案。','比较实际方案D与基准B的原生时程，分别检查原控制时段、自身控制峰和装置出力。'),
 ('该关系直接核对已得到的两状态时程，说明控制时刻为何重新选择。','该关系直接核对已得到的两状态时程，说明两个时刻的大小关系如何改变。'),
 ('工程解释应回到实际两状态的竞争时段，并继续核查对应运动与装置出力。','工程解释应回到实际两状态中两处接近峰所在时段，并继续核查对应运动与装置出力。')]
for old,new in changes:assert text.count(old)==1;text=text.replace(old,new)
source=b.decode('utf-8')
for pat,flags in [(r'^\|.*$',re.M),(r'\$\$.*?\$\$',re.S),(r'!\[[^\]]*\]\([^)]+\)',0)]:assert re.findall(pat,source,flags)==re.findall(pat,text,flags)
out=p.with_name('p06-actual-timing-session027-v002.md');assert not out.exists();out.write_text(text,encoding='utf-8',newline='\n')
record={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source_sha256':hashlib.sha256(b).hexdigest(),'output':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changes':[{'old':x,'new':y} for x,y in changes],'all_tables_equations_figures_unchanged':True,'reason':'Adopted optional final wording and removed draft-revision history from scientific prose.'}
(S/'final-text-adoption.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
previous=(R/'research/sessions/20261103-1700/word/author_word.py').read_text(encoding='utf-8')
script=previous.replace('p06-actual-main-session026-v003.md','p06-actual-timing-session027-v002.md').replace('p06-actual-main-session026-论文审阅稿-v003.docx','p06-actual-timing-session027-论文审阅稿-v002.docx').replace('2aae66c26effa5c5436cd0b08cb883ead63d5f0ed12ffd88f47a9400a24cc370',record['sha256'])
wp=S/'word/author_word.py';assert not wp.exists();wp.write_text(script,encoding='utf-8',newline='\n')
st=json.loads((S/'status.json').read_text(encoding='utf-8'));st.update({'phase':'final-review-and-word-production','no_new_numeric_experiments':True,'no_new_scientific_dispatch':True,'scientific_manuscript':record['output'],'scientific_sha256':record['sha256'],'actual_q_recovery':'CM projection completed; exact actual q and shear reconstruction not closed'});(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
