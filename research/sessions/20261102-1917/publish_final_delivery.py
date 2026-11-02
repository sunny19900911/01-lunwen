from pathlib import Path
import json,datetime,hashlib,sys,subprocess,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
deleted=read(S/'automation-deleted-actual-readback.json');assert not deleted['p06_config_exists']
status=read(S/'status.json');status.update({'phase':'closed-budget','closed_at':now,'checkpoint_open':False,'current_task':'Research stopped; immutable deliverables accepted; automation deleted; final normal sync receipt is authoritative.'});status['automation'].update({'state':'DELETED','formal_pause_verified':True,'formal_delete_verified':True});put(S/'status.json',status)
threads=read(S/'threads.json')
for t in threads['threads']:
 if t['role']=='role5':t.update({'cursor':'824ab043-4970-4d4a-8fa8-7ed81ac611bc:138','actual_status':'active-final-reply-after-file-freeze','task':'R004 files frozen21:40:18; no further edits requested; root independent9-page QA completed','last_actual':now})
put(S/'threads.json',threads)
with (S/'final-summary.md').open('a',encoding='utf-8') as f:f.write('\n实际行政关闭时间：'+now+'。硬截止后仅完成冻结件验收记录、正式暂停/删除及最后普通同步；没有新科研或改稿。作者文件已冻结但聊天最终回复仍active，如实保留，不认其个人全页QA完成。\n')
with (S/'runs.md').open('a',encoding='utf-8') as f:f.write('\n- FINAL '+now+'：根独立只读Word快照9页全部实际看完，字节与作者21:40:18冻结件一致；科学截止后仅行政。正式pause/view/actualreadback/delete/不存在验证完成，旧三项PAUSED。最后普通同步见git-FINAL-receipt.json。\n')
(S/'next-task.md').write_text('# 本轮已关闭\n\n'+now+'，closed-budget。禁止恢复本轮科研。最终Word、科学MD和完整工程表已冻结，根独立9页QA完成；轻微标题换行及真实投稿缺项见final-summary.md。p06-150正式删除并核不存在，旧三项PAUSED。最终正常Git结果见git-FINAL-receipt.json，不重复运行既有receipt。\n',encoding='utf-8')
names=['status.json','threads.json','runs.md','next-task.md','final-summary.md','rounds/FINAL.md','root-word-candidate-snapshot.json','root-word-candidate1-identity.json','root-word-all-pages-review.json','root-final-word-adoption.json','prepare_final_delivery.py','finalize_session.py','publish_final_delivery.py','publish_checkpoint.py','resume_R006_staged.py','R006-local-validation-recovery.json','git-R006-receipt.json','automation-pause-tool-receipt.json','automation-paused-actual-readback.json','automation-delete-tool-receipt.json','automation-deleted-actual-readback.json','roles/role5/R004/freeze.json','roles/role5/R004/one-page.md','roles/role5/R004/build_word.py','roles/role5/R004/configure_builder.py','roles/role5/R004/exact_v003.py','roles/role5/R004/freeze_progress.py','roles/role5/R004/math_omml.py','roles/role5/R004/render_review.py']
paths=[S/n for n in names]
paths += [R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-论文审阅稿-v003.docx']
items=[]
for p in paths:
 b=p.read_bytes()
 if p.suffix=='.json':json.loads(b.decode('utf-8'))
 if p.suffix=='.py':ast.parse(b.decode('utf-8'))
 items.append({'relative':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(b).hexdigest()})
manifest=S/'git-FINAL-manifest.json';assert not manifest.exists()
put(manifest,{'checkpoint':'FINAL','message':'P06 session022: deliver reviewed engineering manuscript and close research window','files':items,'checks':['Same author-frozen Word SHA as root immutable render; all9 pages actually viewed','Five editable tables100 numeric cells,43 native math objects,3 original figures and links verified','Final source exact three-paragraph contract accepted; no new science after freeze','Author finite-task overrun and incomplete personal visual QA preserved; root completed independent QA','Title cosmetic line balance retained and submission pending items disclosed','Formal pause,view,actual config readback,delete and absence verified; old three automations PAUSED','Explicit small-file whitelist; caches,diff,raw data,third-party works,old dirty files excluded']})
p=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(manifest)],cwd=R)
if p.returncode:raise SystemExit(p.returncode)
rec=read(S/'git-FINAL-receipt.json');status['git']={'last_checkpoint':'FINAL','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']};put(S/'status.json',status)
print(json.dumps({'closed_at':now,'HEAD':rec['HEAD'],'remote_verified':rec['remote_equals_local'],'automation_deleted':True}))
