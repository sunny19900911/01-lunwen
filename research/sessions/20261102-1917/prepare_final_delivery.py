from pathlib import Path
import json, hashlib, datetime

S=Path(__file__).resolve().parent
R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
word=R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-论文审阅稿-v003.docx'
expected='1b8063e1599c94a312eb96c29aa8cc50a3bb8bac8b2adce0b477269517492431'
assert hashlib.sha256(word.read_bytes()).hexdigest()==expected, 'Changed candidate requires new review'
qa={'reviewed_at':now,'word_sha256':expected,'word_bytes':word.stat().st_size,'pages_actually_viewed':list(range(1,10)), 'root_independent_render':'root-word-review/local-cache/candidate1/render', 'identity_gate':'root-word-candidate1-identity.json', 'numeric_table_cells':100,'native_OMML':43,'data_tables':5,'original_figures':3,'scientific_or_formula_defects_found':0,'readable':True,'visual_notes':['Title last line contains only two Chinese characters; cosmetic balance could improve, no clipping or loss of content.','Table 3 continues on page 5 with repeated headers; all rows readable.','Page 7 native K matrix and modal sum preserve all operands.','References continue onto page 9; no placeholder author information.'], 'approval_scope':'Scientific review manuscript; final author freeze and exact same byte identity required before publication.'}
(S/'root-word-all-pages-review.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=S/'R006-local-validation-recovery.json'
d=json.loads(p.read_text(encoding='utf-8'))
d['subsequent_whitespace_check']={'failure':'Standard unified-diff blank context lines contain a single space; cached whitespace check rejected the diff.','repair':'Only the exact owned new diff path was unstaged with git restore --staged; frozen author bytes unchanged; remaining approved blob hashes checked before normal commit/push.','receipt':'git-R006-receipt.json','success_HEAD':'123fccf6aa0b87dcab6700884efec4ac923807ae','force_reset_or_other_index_changes':False}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'time':now,'root_all_pages_reviewed':True,'word_sha256':expected}))
