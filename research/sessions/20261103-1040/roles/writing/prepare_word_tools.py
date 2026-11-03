from pathlib import Path
import ast,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[4];old=R/'research/sessions/20261103-0845/roles/writing'
names=['build_word.py','math_omml.py','render_review.py']
for n in names:
 p=H/n;assert not p.exists();b=(old/n).read_bytes();ast.parse(b.decode('utf-8'));p.write_bytes(b)
s=(old/'author_word.py').read_text(encoding='utf-8')
s=s.replace('p06-sh3-sh4-session023-v003.md','p06-design-reflection-session024-v002.md').replace('p06-sh3-sh4-session023-论文审阅稿-v003.docx','p06-design-reflection-session024-论文审阅稿-v002.docx').replace('a16f4e6893f4f96b94ed5ef312f4b396682db68c254b104345bbadb22b21a310','750b1dcc8fa38014d45307cec124c6ef83058a063b32a5bee7ba7c1bd95f1324').replace("'--operation-kind','create'","'--operation-kind','edit'")
ast.parse(s);assert not (H/'author_word.py').exists();(H/'author_word.py').write_text(s,encoding='utf-8')
print(json.dumps({'safe023_tools_copied':names,'new_authoring_kind':'edit','marker_not_yet_run':True}))
