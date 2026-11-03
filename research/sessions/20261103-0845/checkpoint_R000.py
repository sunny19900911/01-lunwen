from pathlib import Path
import json,datetime,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
status=json.loads((S/'status.json').read_text(encoding='utf-8'));assert not status['checkpoint_open'];status.update({'checkpoint_open':True,'checkpoint':'R000','checkpoint_started_at':now});(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'rounds/R000.md').write_text('# 首轮实质启动\n\n'+now+'：实际read_thread核最新两人类消息，范围SHW3X/SHW4X第5层辅助核查；新150分钟08:45:53—11:15:53。根完整读旧P06与handoff，核v003源SHA，四状态300项和/成对PBPM减幅预核通过，仍待独审。三子代理audit/literature/writing已正式并行R001；不启动任何旧聊天任务。唯一heartbeat p06-sh3-sh4-150正式create/view/实配置ACTIVE。首次create因缺destination被拒，补明确当前thread后成功，无重复项。\n\n候选反证：交接固定300线性参照不支持第10/13同向主导，不能升级为原生物理因果。首轮同步交接小包仅标候选与复算来源；未审稿/在写文件不收。\n',encoding='utf-8')
(S/'topic-cards/T001.md').write_text('# P06工程评价深化\n\n保持主线：同输入配对，逐层多输入区分最小改善与最大绝对需求。新增SH3/SH4只核查一种候选解释。当前hand-off反对高阶10/13主导，独审前不认定。先例模态方法复用，不以机制支线争创新。成功是可信解释及工程用法清楚，不要求预设成立。下一采纳独审与原页后唯一作者整合一小节。\n',encoding='utf-8')
names=['plan.md','status.json','authorization-evidence.json','input-manifest.json','claims.md','runs.md','next-task.md','threads.json','root_engineering_precheck.py','root-R001-engineering-precheck.json','automation-create-tool-receipt.json','automation-actual-readback.json','publish_checkpoint.py','checkpoint_R000.py','rounds/R000.md','topic-cards/T001.md']
paths=[S/n for n in names]
H=R/'research/handoffs/p06-sh3-sh4-20261103'
paths += [H/n for n in ['任务与证据交接.md','recompute_comparison.py','results.json','story5-reference-checks-4.csv','story5-all300-signed-reference-1200.csv','independent-frozen-CSV-checks-20.csv','all12-reference-checks-48.csv','story5-between-input-comparison-2.csv']]
items=[{'relative':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
cfg={'checkpoint':'R000','message':'P06 session023: launch focused SH3 SH4 mechanism review','files':items,'checks':['Human corrected SH3/SH4 and new150minute roles/Git authorization actually read','Old v003 scientific and Word SHA preserved; no oldwindow restored','Root paired-output arithmetic and four300term sums checked; independent audit pending','Handoff package is candidate/reference, not native causal decomposition','Three finite agents dispatched; no active manuscript included','Formal unique heartbeat create/view/actual configuration verified; prior3 paused','Explicit small-file whitelist; no cache/raw/fulltimeseries/thirdpartyfulltext/old dirty']}
mp=S/'git-R000-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R000-receipt.json').read_text(encoding='utf-8'));status.update({'checkpoint_open':False,'git':{'last_checkpoint':'R000','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']}});(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
