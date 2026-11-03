from pathlib import Path
import json,datetime,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
p=S/'status.json';st=json.loads(p.read_text(encoding='utf-8'));assert not st['checkpoint_open'];st.update({'checkpoint_open':True,'checkpoint':'R002','checkpoint_started_at':now});p.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','claims.md','runs.md','next-task.md','final-summary.md','final-summary-prepared-v001.md','普通中文研究说明.md','final-exact-change-contract.json','final-review-adoption.md','prepare_final_contract.py','root-v003-source-adoption.json','root-final-word-identity.json','root-final-word-visual-review.json','check_final_word.py','accept_delivery.py','checkpoint_R002.py','rounds/R002.md','git-R001-receipt.json','git-R001-verification-issue.json','git-R001-remote-recovery.json','roles/audit/review_v002_text.py','roles/audit/R002/freeze.json','roles/audit/R002/text-checks.json','roles/audit/R002/v002-final-correctness-review.md','roles/writing/SHW3X-SHW4X-辅助分析资料-v002.md','roles/writing/R003-shareable-manifest.json']
paths=[S/n for n in names]
share=json.loads((S/'roles/writing/R003-shareable-manifest.json').read_text(encoding='utf-8'))
for x in share['files']:
 q=Path(x['path']);assert hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256'];paths.append(q)
P=R/'papers/damping-output-boundaries/manuscript';paths += [P/'p06-sh3-sh4-session023-v003.md',P/'p06-sh3-sh4-session023-论文审阅稿-v003.docx']
items=[{'relative':q.relative_to(R).as_posix(),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in paths]
cfg={'checkpoint':'R002','message':'P06 session023: deliver reviewed SH3 SH4 comparison manuscript and Word','files':items,'checks':['Final v003 and supplement match preapproved exact replacement hashes','Author and root independently actually viewed all10final pages','Six editable tables115 numeric cells,43 nativeOMML,3originalfigures and new/oldlinks verified','Root rechecked all initial source/handoff SHA unchanged','R001 remote readback recovered to exact local SHA without repush; initial TLS receipts preserved','All science stopped; only final sync and formal automation closure remain','Explicit frozen small-file whitelist excludes caches/diff/raw/thirdpartyfulltext/old dirty']}
mp=S/'git-R002-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R002-receipt.json').read_text(encoding='utf-8'));st.update({'checkpoint_open':False,'git':{'last_checkpoint':'R002','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']}});p.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
