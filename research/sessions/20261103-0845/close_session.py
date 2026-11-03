from pathlib import Path
import json,datetime,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def load(n):return json.loads((S/n).read_text(encoding='utf-8'))
def put(n,x):(S/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not load('automation-deleted-actual-readback.json')['p06_current_config_exists']
st=load('status.json');assert not st['checkpoint_open'];assert load('git-R002-receipt.json')['remote_equals_local']
st.update({'phase':'closed-complete','closed_at':now,'completed_before_deadline':True,'current_task':'Complete: reviewed final MD, Word and supplement; Word/source R002 synced and verified; automation formally deleted. Administrative CLOSE receipt authoritative.','checkpoint':'CLOSE','checkpoint_open':False})
st['automation'].update({'state':'DELETED','formal_pause_view_readback':True,'formal_delete_absence_verified':True});put('status.json',st)
with (S/'final-summary.md').open('a',encoding='utf-8') as f:f.write('\n## 实际关闭及最终同步\n\n实际关闭时间'+now+'，完成后提前收束，未用满150分钟，也不声称连续准时跑满。正式R002交付提交76c0b95aa42c74a00fb958bce2077730df95a657已push并lsremote核一致；同清单首次远端预检因TLS在stage之前失败，恢复同一清单一次成功，未改科学源。p06-sh3-sh4-150已正式暂停/view、实际配置核回读并正式删除/实际不存在验证；旧git、automation-3、automation-4保持PAUSED。后续仅CLOSE行政小文件同步，结果见git-CLOSE-receipt.json，不恢复研究或新建唤醒。\n')
with (S/'runs.md').open('a',encoding='utf-8') as f:f.write('\n- '+now+' R003作者09:27:21冻，根全部10页实际看完且独立gate115数值/43OMML/3图/链接通过。R002交付76c0b95远端一致。当前正式pause/view/实际读回/delete/不存在验证全部成功，旧3 PAUSED；完成后提前结束，无新科研。\n')
(S/'next-task.md').write_text('# 本轮已完成\n\n'+now+' closed-complete。固定150分钟为上限，完成后提前关闭。最终科学源/Word/辅助资料已冻结、根10页实际QA通过，R002交付已正常Git同步并核远端。p06-sh3-sh4-150正式删除并核不存在，旧3项PAUSED。仅剩CLOSE行政同步收据，不恢复旧任务、作者或自动化；既有receipt不重复运行。\n',encoding='utf-8')
(S/'rounds/CLOSE.md').write_text('# 本轮关闭\n\n'+now+' 成果/独审/Word全页QA已完成，正式调度关闭并验证。交付已在76c0b95提交核远端，CLOSE只含行政回执/状态。旧全部原件保持。\n',encoding='utf-8')
names=['status.json','runs.md','next-task.md','final-summary.md','rounds/CLOSE.md','R002-prestage-TLS-recovery.json','git-R002-receipt.json','automation-pause-tool-receipt.json','automation-paused-actual-readback.json','automation-delete-tool-receipt.json','automation-deleted-actual-readback.json','close_session.py']
files=[{'relative':(S/n).relative_to(R).as_posix(),'sha256':hashlib.sha256((S/n).read_bytes()).hexdigest()} for n in names]
cfg={'checkpoint':'CLOSE','message':'P06 session023: record verified delivery and formal automation closure','files':files,'checks':['Final Word and source delivery R002 already verified on origin/main','Formal pause/view/config readback/delete/absence verified; old3 PAUSED','Science complete and10pages actually reviewed; early closure within fixed window','Administrative small-file-only checkpoint; no active/old/raw/cache files']}
mp=S/'git-CLOSE-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=load('git-CLOSE-receipt.json');st['git']={'last_checkpoint':'CLOSE','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local'],'scientific_Word_delivery_verified_commit':'76c0b95aa42c74a00fb958bce2077730df95a657'};put('status.json',st)
print(json.dumps({'closed_at':now,'HEAD':rec['HEAD'],'remote_verified':rec['remote_equals_local'],'automation_deleted':True}))
