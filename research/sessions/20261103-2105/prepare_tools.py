from pathlib import Path
import hashlib,json,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];old=R/'research/sessions/20261103-1853'
for name in ['build_word.py','math_omml.py','render_review.py']:
 p=S/'word'/name;p.parent.mkdir(exist_ok=True)
 assert not p.exists();p.write_bytes((old/'word'/name).read_bytes())
for name in ['publish_checkpoint.py','make_checkpoint.py']:
 t=(old/name).read_text(encoding='utf-8').replace('p06-actual-timing-session027-','p06-control-check-session028-').replace('P06 actual-scheme main analysis','P06 two-dimensional control checks')
 p=S/name;assert not p.exists();p.write_text(t,encoding='utf-8',newline='\n')
p=S/'check_final_word.py';assert not p.exists();p.write_bytes((old/p.name).read_bytes())
src=R/'papers/damping-output-boundaries/manuscript/p06-actual-timing-session027-v004.md'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='f56b44fc5172778261364253e69eb8fa324f97af148e0fdd968e50b3dbe15a71'
(S/'source-freeze.json').write_text(json.dumps({'at':datetime.datetime.now().astimezone().isoformat(),'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'old_scientific_and_word_bytes_preserved':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('New task tools prepared; no DOCX authoring or marker executed.')
