from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,tomllib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R007-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap=json.loads((S/'R007-actual-snapshot.json').read_text())
t=json.loads((S/'threads.json').read_text())
for x in t['threads']:
 p=next(z for z in snap['threads'] if z['role']==x['role'])
 x.update(cursor=p['cursor'],actual_status=p['actual_status'],last_actual=snap['actual'])
 x['task']='R006/v006 sole author formally dispatched13:20, max20min freeze13:40' if x['role']=='role5' else ('closed own90min budget13:11:38; R010frozen13:12:13, no restart' if x['role']=='role3' else 'frozen idle; no new numeric research')
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text())
d.update(last_actual=now,phase='manuscript-integration-and-final-review',checkpoint='R007-writing',checkpoint_open=True,no_new_numeric_experiments=True,recovery_file='rounds/R007.md')
d['scientific_status']['Y_direction']='reviewed role2R009 frozen13:05:29; rootfullread onepage/manifest13:20,5292checks0must;216CMsigned/144VY diagnostics/180timegroups/36UPC andpeakpairs; no newODE; same3functionstwoaxes not6events'
d['scientific_status']['combined_validation']='432CM signed maxNRMSE.443101625%;144 E shearabsolute curves max.669154128%,peak.235170328%;72 peakreductionpairs maxdifference.196533pp; fullFE/FNA signed attribution notcertified'
d['current_tasks']={x['role']:x['task'] for x in t['threads']}
d['next_checkpoint']='Collect soleauthor v006 actualfreeze by13:40; root fullread/figurelinks/scienceidentities then one finalbounded role2 manuscript review; Word onlyafter acceptedtext withdocuments render/perpageQA. No newnumericresearch; R008Git near13:37 includesfrozenonly. Deadline15:30:11 unchanged.'
js(S/'status.json',d)
with(S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC020-15 supported/conditional direction-output validation, reviewed: role2R009 5292 numeric checks0must, independently rebuilt GammaY/BY withnativeVY; root readformalreport13:20. Combined432CMsigned and144Eabsolute histories, maxNRMSE.443101625%/.669154128%;72peakreductionpairs maxdifference.196533pp. Same3functions in2directions, not6indepquakes; no actualFNAq/fullFE/signη upgrade.\n')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR007 '+now+': adoptedfinalYindependentaudit; role3own90minclosed; six actualsnapshots saved, authoronly v00620min integration dispatched13:20, no newscientific experiment.\n')
(S/'rounds/R007.md').write_text('# R007｜两方向输出检验完成，进入完整图文稿\n\n实际记录'+now+'。根已全文读②R009正式报告/manifest，5292数字0must；Y与X合计432条CM有符号位移、144条E剪力绝对值曲线及72对降幅已审。最大曲线NRMSE分别.443101625%/.669154128%，最大峰降差.196533个百分点。保留Q对照、软件力方向及完整FE/FNA解释条件，不扩大成实际非线性逐阶唯一恢复。\n\n③R010交接索引已根全文读，其90min窗口13:11:38终止、13:12:13行政封存，不重新派工。六聊天13:20快照均idle；仅⑤正式接R006/v00620min，最晚13:40统一整合三图、同刻幅值/波形解释、Y辅助与双语正文。无新数值实验。冻结后根全文核与一次独立新稿审核，再Word渲染逐页QA。固定15:30:11截止。\n\n本点仅已冻②R009、③R010与共享检查点白名单Git，不收在写⑤。旧11tracked脏文件、unknown5E-07、local-cache不动。\n',encoding='utf-8')
cfgpath=Path('C:/Users/mj528/.codex/automations/git-2/automation.toml');b=cfgpath.read_bytes();cfg=tomllib.loads(b.decode())
assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=MINUTELY;INTERVAL=15;UNTIL=20261031T074511Z'
assert '13:20' in cfg['prompt'] and 'R007' in cfg['prompt']
js(S/'automation-R007-update-receipt.json',dict(actual=now,id='git-2',status=cfg['status'],rrule=cfg['rrule'],target_thread_id=cfg['target_thread_id'],actual_config_sha256=hashlib.sha256(b).hexdigest(),formal_update_success=True,formal_view_success=True))
files=[]
for role,rr in [('role2','R009'),('role3','R010')]:
 base=S/'roles'/role/rr
 assert (base/'manifest.json').exists() or (base/'freeze.json').exists()
 for p in base.rglob('*'):
  if p.is_file() and 'local-cache' not in p.parts and p.suffix in ['.md','.json','.csv','.py'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R007.py','status.json','threads.json','claims.md','runs.md','rounds/R007.md','R007-actual-snapshot.json','automation-R007-update-receipt.json','git-R006-receipt.json']:files.append(S/n)
js(S/'git-R007-publication.json',dict(checkpoint='R007',time=now,message='research: validate two-direction modal predictions and integrate engineering manuscript',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps(dict(time=now,files=len(set(files))),ensure_ascii=False))
