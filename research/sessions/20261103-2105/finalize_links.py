from pathlib import Path
import json,hashlib,re
S=Path(__file__).resolve().parent;R=S.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-control-check-session028-v002.md';out=M/'p06-control-check-session028-v003.md';assert not out.exists()
t=src.read_text(encoding='utf-8');old='../../../research/sessions/20261103-2105/roles/response/four-record-QT-QD-difference.png';new='../../../research/sessions/20261103-2105/figures/four-record-QT-QD-difference-v002.png'
assert t.count(old)==1;t=t.replace(old,new)
for target in re.findall(r'\]\(([^)]+)\)',t):
 if not target.startswith(('http:','https:')):assert (out.parent/target).resolve().exists(),target
out.write_text(t,encoding='utf-8',newline='\n')
(S/'final-link-check-v003.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'final_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'only_approved_figure_path_changed':t.replace(new,old)==src.read_text(encoding='utf-8'),'all_local_links_exist':True,'figure_original_viewed':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out)
