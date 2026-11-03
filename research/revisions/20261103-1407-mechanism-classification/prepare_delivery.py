from pathlib import Path
import hashlib,json,ast
H=Path(__file__).resolve().parent;R=H.parents[2];W=H/'word';W.mkdir(exist_ok=True)
old=R/'research/sessions/20261103-1040'
for n in ['build_word.py','math_omml.py','render_review.py']:
    p=W/n;assert not p.exists();b=(old/'roles/writing'/n).read_bytes();ast.parse(b.decode('utf-8'));p.write_bytes(b)
p=H/'check_final_word.py';assert not p.exists();p.write_bytes((old/'check_final_word.py').read_bytes())
src=R/'papers/damping-output-boundaries/manuscript/p06-mechanism-classification-v001.md'
s=(old/'roles/writing/author_word.py').read_text(encoding='utf-8')
s=s.replace('H.parents[4]','H.parents[3]').replace('p06-design-reflection-session024-v002.md',src.name).replace('p06-design-reflection-session024-论文审阅稿-v002.docx','p06-mechanism-classification-论文审阅稿-v001.docx').replace('750b1dcc8fa38014d45307cec124c6ef83058a063b32a5bee7ba7c1bd95f1324',hashlib.sha256(src.read_bytes()).hexdigest())
ast.parse(s);(W/'author_word.py').write_text(s,encoding='utf-8',newline='\n')
s=(old/'publish_checkpoint.py').read_text(encoding='utf-8')
s=s.replace("p.is_relative_to(S) or p.is_relative_to(R/'research/handoffs/p06-design-reflection-20261103') or (p.parent==R/'papers/damping-output-boundaries/manuscript' and p.name.startswith('p06-design-reflection-session024-'))","p.is_relative_to(S) or (p.parent==R/'papers/damping-output-boundaries/manuscript' and p.name.startswith('p06-mechanism-classification-'))")
s=s.replace("'.svg','.png','.docx'","'.svg','.png','.docx','.diff'")
ast.parse(s);(H/'publish_checkpoint.py').write_text(s,encoding='utf-8',newline='\n')
print(json.dumps({'prepared_word_helpers':True,'marker_run':False,'docx_authored':False,'publisher_whitelist':'current revision and p06-mechanism-classification-* only'}))
