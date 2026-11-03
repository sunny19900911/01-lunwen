from pathlib import Path
import json,datetime,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
p=S/'status.json';st=json.loads(p.read_text(encoding='utf-8'));assert not st['checkpoint_open'];st.update({'checkpoint_open':True,'checkpoint':'R001','checkpoint_started_at':now});p.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','claims.md','runs.md','next-task.md','final-summary.md','用户意见采用与收窄说明.md','root-R001-evidence-adoption.json','root-editorial-suggestions.md','final-review-adoption.md','final-exact-change-contract.json','prepare_final_contract.py','root-final-source-adoption.json','check_final_word.py','root-final-word-identity.json','root-final-word-visual-review.json','accept_delivery.py','checkpoint_R001.py','rounds/R001.md','roles/audit/review_reflection_v001.py','roles/audit/R002/freeze.json','roles/audit/R002/text-checks.json','roles/audit/R002/v001-short-section-final-review.md','roles/literature/R001-brace-and-Maxwell-review.md','roles/literature/freeze.json','roles/literature/source-read-record.json','roles/literature/read_local024.py','roles/literature/freeze_R001.py','roles/writing/R002-shareable-manifest.json']
paths=[S/n for n in names]
for x in json.loads((S/'roles/writing/R002-shareable-manifest.json').read_text(encoding='utf-8'))['files']:
 q=Path(x['path']);assert hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256'];paths.append(q)
P=R/'papers/damping-output-boundaries/manuscript';paths += [P/'p06-design-reflection-session024-v002.md',P/'p06-design-reflection-session024-论文审阅稿-v002.docx']
items=[{'relative':q.relative_to(R).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in paths]
cfg={'checkpoint':'R001','message':'P06 session024: deliver restrained engineering reflection and reviewed Word','files':items,'checks':['Final313CJK section matches root exact3phrase contract and independent review','All preexisting MD scientific content restores byte-for-byte after removing new section','Author and root actually viewed final10pages; root6table115numeric/43OMML/3figures/links checked','Primary-source role actually viewed11pages of existing local papers; no web or experiments','User six suggestions preserved in separate evidence-narrowing note, no unsupported design prescription','All source/author files frozen; no cache/diff/raw/fulltext/templates/old dirty included']}
mp=S/'git-R001-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R001-receipt.json').read_text(encoding='utf-8'));st.update({'checkpoint_open':False,'git':{'last_checkpoint':'R001','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']}});p.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
