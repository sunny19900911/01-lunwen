from pathlib import Path
import hashlib,json,re,ast,datetime
H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'papers/damping-output-boundaries/manuscript/p06-mechanism-classification-v001.md'
dst=src.with_name('p06-mechanism-classification-v002.md')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='39cda7f74e8d214ab0cbdc57abf22c98390224b9c2eb912cea919b8ca1f9bcf9'
s=src.read_text(encoding='utf-8');old='前者帮助解释改善为何受限';new='前者说明剪力下降为何会被部分抵消'
assert s.count(old)==1 and not dst.exists()
t=s.replace(old,new);dst.write_text(t,encoding='utf-8',newline='\n')
links=[]
for path in re.findall(r'\]\(([^)]+)\)',t):
    if '://' in path:continue
    p=(dst.parent/path).resolve();assert p.is_file(),p;links.append(path)
oldsha=hashlib.sha256(src.read_bytes()).hexdigest();newsha=hashlib.sha256(dst.read_bytes()).hexdigest()
author=H/'word/author_word.py'
a=author.read_text(encoding='utf-8').replace(src.name,dst.name).replace('论文审阅稿-v001.docx','论文审阅稿-v002.docx').replace(oldsha,newsha)
ast.parse(a);author.write_text(a,encoding='utf-8',newline='\n')
d={'at':datetime.datetime.now().astimezone().isoformat(),'reviewed_v001_sha256':oldsha,'final_v002_sha256':newsha,'final_bytes':dst.stat().st_size,'exact_edit':{'from':old,'to':new,'count':1},'all_other_bytes_identical':t.replace(new,old)==s,'local_links_exist':links,'adopted_reviews':['roles/audit/targeted-final-review.md','roles/engineering/final-review.md'],'scientific_numbers_unchanged_since_review':True,'word_marker_not_yet_run':True}
(H/'final-text-adoption.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
