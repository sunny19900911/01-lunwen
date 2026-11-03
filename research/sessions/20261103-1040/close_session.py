from pathlib import Path
import json,datetime,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def load(n):return json.loads((S/n).read_text(encoding='utf-8'))
def put(n,o):(S/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not load('automation-deleted-actual-readback.json')['current_config_exists']
assert load('git-R001-receipt.json')['remote_equals_local']
st=load('status.json');assert not st['checkpoint_open'];st.update({'phase':'closed-complete','closed_at':now,'completed_before_deadline':True,'current_task':'Complete:313character section and10page Word accepted; delivery R001 synced and verified; current heartbeat deleted, delayed p06-4 remainsPAUSED.','checkpoint':'CLOSE','checkpoint_open':False})
st['automation'].update({'state':'DELETED','formal_pause_view_actual_readback':True,'formal_delete_absence_verified':True});put('status.json',st)
with (S/'final-summary.md').open('a',encoding='utf-8') as f:f.write('\n## 实际关闭与最终同步\n\n实际关闭时间'+now+'。本轮按问题完成情况提前结束，未用满150分钟，不声称连续准时跑满。正文/Word交付提交fbe0fd09294e19c0757c88e50a31e8a7dec7144f已普通push且lsremote核一致。p06-150正式pause/view/实际配置回读后delete并核配置不存在；旧git/automation-3/automation-4及原延时p06-4均PAUSED且未恢复。CLOSE仅行政回执同步，结果以git-CLOSE-receipt.json为准；不再派研究。\n')
with (S/'claims.md').open('a',encoding='utf-8') as f:f.write('\n- C02 reviewed/not-established：六条无条件高阶根因/低阶上限/调频优序/曲率布置/启动/承载兜底未由本稿建立，未写为结论；一般条件反例与原页范围见auditR001和literatureR001。\n- C03 reviewed/supported-as-conditional-guidance：最终313汉字三视角经一次终审和原页依据支持，只有复核建议，不构成实测最优方案或安全验算。根精确契约、原文保留与最终Word全10页QA通过。\n')
with (S/'runs.md').open('a',encoding='utf-8') as f:f.write('\n- '+now+' 作者11:12:34冻，根已实际看最终10页并独立115数字/43OMML/3图/链接gate通过；科学没有新计算。交付fbe0fd0已核远端。正式pause/view/实读/delete/不存在验证完成，旧4项PAUSED，提前收束。\n')
with (S/'topic-cards/T001.md').open('a',encoding='utf-8') as f:f.write('\n最终：313汉字、仅6.1一节，三视角保留而无新处方，已有原页和一次终审通过；MD/Word按原数据主线完成，原科学内容不变。无新数值，研究已提前关闭。\n')
(S/'next-task.md').write_text('# 本轮完成\n\n'+now+' closed-complete。313汉字新节与10页Word已冻结，根全部页实际看/身份检查通过，R001交付fbe0fd0已正常Git同步核远端。本轮p06-150正式删除且不存在，原延时p06-4及旧3项PAUSED。只有CLOSE行政同步回执，不重启旧任务/预算/作者或调度，不重跑receipt。\n',encoding='utf-8')
(S/'rounds/CLOSE.md').write_text('# 本轮关闭\n\n'+now+' 短节、依据/收窄、MD/Word及全页QA已完成，交付已同步。正式调度关闭，旧延时任务不恢复。CLOSE仅行政小文件。\n',encoding='utf-8')
names=['status.json','claims.md','runs.md','next-task.md','final-summary.md','topic-cards/T001.md','rounds/CLOSE.md','git-R001-receipt.json','automation-pause-tool-receipt.json','automation-paused-actual-readback.json','automation-delete-tool-receipt.json','automation-deleted-actual-readback.json','close_session.py']
items=[{'relative':(S/n).relative_to(R).as_posix(),'sha256':hashlib.sha256((S/n).read_bytes()).hexdigest()} for n in names]
cfg={'checkpoint':'CLOSE','message':'P06 session024: record verified delivery and close design reflection task','files':items,'checks':['R001 final Word/source delivery already synced and exact remote SHA verified','Current heartbeat formally paused/viewed/read back/deleted/absence verified','Old3 and delayedp06-4 stayPAUSED; latest immediate authorization honored','Science and10page actualQA complete; early closure within fixed window','Administrative small-file whitelist only; no raw/cache/old dirty']}
mp=S/'git-CLOSE-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=load('git-CLOSE-receipt.json');st['git']={'last_checkpoint':'CLOSE','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local'],'Word_delivery_verified_commit':'fbe0fd09294e19c0757c88e50a31e8a7dec7144f'};put('status.json',st)
print(json.dumps({'closed_at':now,'HEAD':rec['HEAD'],'remote_verified':rec['remote_equals_local'],'automation_deleted':True}))
