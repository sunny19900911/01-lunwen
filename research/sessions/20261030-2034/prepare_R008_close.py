from pathlib import Path
import json,datetime,hashlib,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
deadline=datetime.datetime.fromisoformat('2026-10-30T22:34:43+08:00')
assert now>=deadline,'Before hard deadline: only prepare, do not claim budget closed'
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
assert st['session']=='20261030-2034' and st['no_new_scientific_dispatch']
assert st['phase']!='closed-budget','Already closed: do not repeat'
stop=json.loads((S/'automation-final-stop-receipt.json').read_text(encoding='utf-8'))
assert stop['paused_actual_verified'] and stop['delete_tool_success']
sn=json.loads((S/'actual-final-snapshot.json').read_text(encoding='utf-8'))
assert len(sn)==6 and all(x['poll']['thread']['status']['type']=='idle'for x in sn)
for k in ['final_word','final_manuscript']:
 p=R/st[k]['relative'];assert hashlib.sha256(p.read_bytes()).hexdigest()==st[k]['sha256']
qa=json.loads((S/'root-final-document-QA.json').read_text(encoding='utf-8'))
assert len(qa['root_actual_pages_viewed'])==7
st.update(phase='closed-budget',last_actual=now.isoformat(),actual_closed_at=now.isoformat(),checkpoint='R008-final',checkpoint_open=False,no_new_scientific_dispatch=True,automation='automation-5 paused/view/config verified then deleted; no future wakeups',research_window_complete=True,scientific_objective_complete=False,recovery_file='final-summary.md')
st['primary_task']='Closed fixed two-hour research window; no remaining authorized science; true floor-by-mode attribution unresolved'
st['next_checkpoint']='None: do not restart. Final push result is local git-R008-receipt.json; if server error persists keep pending commits without login or force.'
st['git']['publication']='Final R008 local checkpoint and normal push about to execute; use actual final receipt, not forecast'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
th=json.loads((S/'threads.json').read_text(encoding='utf-8'));by={x['id']:x['poll']for x in sn}
for q in th['threads']:
 p=by[q['threadId']];q.update(cursor=p['cursor'],actual_status=p['thread']['status'],task='completed; no new task after budget',last_snapshot=now.isoformat())
(S/'threads.json').write_text(json.dumps(th,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=f'''# 两小时主线研究最终总结

固定窗口：2026-10-30 20:34:43—22:34:43 Asia/Shanghai。实际行政关闭时间：{now.isoformat()}。科学内容及Word于22:16:35冻结，随后只有交付检查和行政操作，没有延长科研、重新拟合或派工。

## 交付入口

- [Word审阅稿](../../../papers/damping-output-boundaries/manuscript/damping-superposition-session019-v005.docx)：7页、25处可编辑公式、4张可编辑表格、2幅图。作者和主控均实际查看全部7页。
- [科学正文](../../../papers/damping-output-boundaries/manuscript/damping-superposition-session019-v005.md)。
- [普通中文研究说明](普通中文研究说明.md)。
- [逐页检查记录](root-final-document-QA.json)。完整渲染PDF/PNG只供本地QA，不作为用户交付或Git大图页。

这是工程论文审阅稿，未冒称完成全部投稿格式、作者身份或真实逐阶力学归因。

## 主线取得的实质结果

1. 结构M/K和地震输入保持不变，研究对象为模态阻尼5%直接增至8%。未再以阻尼器位置或装置失效预设原因，也未恢复布置优化、CM修补或索新表。
2. 相同阻尼增量确实产生不同阶的响应变化。36阶×3波108项单位参与运动已计算；前12阶×3波36项由独立N12缓存核验，72峰时一致。SHW3X下第3/9阶峰幅分别减小6.3546%/29.1063%。两阻尼状态共同的非零参与/输出倍率在比值中消去；Γ为零时实际该模态不受激，指标不是楼层分担比例。
3. 软件全12层、三条X向输入的36组剪力峰均降低，范围6.851%—29.173%，改善最小的楼层随输入变化。5%两波确定的系数固定用于8%，整波留出和跨阻尼48条记录、288个关键数值经独算；第11层RH4X仍有5.06s峰时偏差，未删去不利样本。
4. 全部36组满足P5-P8=D-M。D是原控制峰时沿原符号的降低量，M为新全程绝对峰相对该同向值的非负修正。20组控制峰时改变，16组在本数据中未变且M=0，3组换号；并列峰的一般情况不将两者视为等价。RH4X第1层22.9625%-3.6748%=19.2877%，屋顶SHW4X31.9149%-2.7415%=29.1734%。恒等核算不叫纯相位、能量或因果份额。

## 尚未闭合与不能扩大之处

各层真实的逐阶剪力分担仍未完全确定。高逆拟合系数出现巨量正负相消，最大系数约已知方向楼板质量的14833倍。Cauchy量级界有明确弹性输出与同质量坐标条件，当前没有认证实际完整M和Bottom VX算子，因此既不把拟合相消称真实高阶作用，也不称实际有限元结果已证明违反物理界。准确复算总曲线不等于物理归阶唯一。

本文已补上增阻尼→各阶幅值/波形变化的实数中段，并核实楼层整体差异与控制峰变化；没有宣称整条真实逐层模态因果链完全闭合。实际非线性Maxwell仅讨论与统一模态增阻尼的区别，本轮无新定量等效认证。不再要求用户提供新表。

## 文献与数值边界

沿用两份已核一手资料：Song等MCEER-08-0005的弹性/含阻尼剪力定义，CSI Analysis Reference Manual2016Rev15的模态时程及具体输出截断检查。单频幅比由经典方程自推，0.625—1不用于任意地震瞬态或楼层合成峰。没有排尽全部同条件先例，不称首次或算法优势，不承诺期刊命中率。三条已见X向输入是回顾性资料，SHW3未改名为SHW7，非新独立工程试验。

## 协作、文件与同步

六个既有角色实际状态均idle；推导、独核、原文、数据、唯一作者和工程解释已交叉交流并留档。实际时间和迟到检查点均如实记录，没有伪称每15分钟精确准时执行。未创建新聊天/第二主控，未求解ETABS、付费、投稿、读凭据或上传原始数据。旧9项tracked脏改、旧稿及未知文件保持。

R001—R006已正常推送并核远端SHA。R007最终稿及Word已本地提交499025d006544f27e4119b2a541b88ba7bb2c35f，曾两次遇GitHub服务器Internal Server Error，故没有把该次失败说成上传成功。R008按原授权作最后正常白名单检查点并尝试一轮推送及至多一次重试；其实际成功或待推状态以随后生成的本地git-R008-receipt.json及ls-remote核验为准，不预报成功。若仍失败保留本地提交，不强推、不开登录、不索凭据。

automation-5已先正式暂停、view及实际配置核验，再按完成后heartbeat规范删除，停止后续唤醒；工具回执保存。旧git、automation-3、automation-4仍PAUSED。到此关闭本轮，不自动重启。
'''
(S/'final-summary.md').write_text(summary,encoding='utf-8')
card='''# 主线最终边界
已达：增加统一模态阻尼后不同阶运动幅值/波形变化的可辨识比值；全楼三波软件剪力峰降差异；控制峰时与正负峰重选的精确核算；完整工程审阅稿及实际逐页核过的Word。
未达：每层真实物理振型对剪力的唯一分担，以及真实Maxwell装置等效于统一模态增量的定量证明。高拟合巨项不能用作已通主线。没有用新布置或外围计算替代该缺口。
窗口到期结束，后续任务需要新的人类指令，不自行重启或要求新数据。不评估或承诺期刊命中率。
'''
(S/'topic-cards/T019-v003-final.md').write_text(card,encoding='utf-8')
(S/'rounds/R008.md').write_text(f'# R008行政关闭\n实际{now.isoformat()}，硬截止后仅正式自动化停止、总结、冻结身份核验和正常白名单Git。六角色idle，不派新科学任务。\n最终Word/MD源SHA与已核7页QA一致；普通中文说明和真实未闭合点齐。R007服务器500失败保留，最后R008只正常push，最多再试一次，不强推或读凭据。\n',encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write(f'\nR008 administrative close {now.isoformat()}, research frozen22:16:35, no budget extension; final SHA verified, automation paused+verified+deleted, final normal push pending actual receipt.\n')
with (S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nFINAL: bounded research window closed; C019-09 unit-kernel ratios reviewed, C019-10 native peak accounting reviewed. Real story-by-mode physical attribution unresolved; do not upgrade fit precision or mass diagnostic to proof.\n')
paths=[S/n for n in ['status.json','threads.json','claims.md','runs.md','final-summary.md','普通中文研究说明.md','topic-cards/T019-v003-final.md','rounds/R008.md','rounds/R008-close-handoff.md','actual-final-snapshot.json','git-R007-receipt.json','automation-final-stop-receipt.json','old-automation-paused-check-final.json','prepare_R008_close.py','record_R008_handoff.py','publish_checkpoint.py']]
files=[]
for p in sorted(set(paths),key=str):
 assert p.is_file()and'local-cache'not in p.parts and p.stat().st_size<1048576
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
cfg={'checkpoint':'R008','time':now.isoformat(),'message':'research: close two-hour modal damping study and record final boundaries','resume_pending_receipt':(S/'git-R007-receipt.json').relative_to(R).as_posix(),'files':files}
with (S/'git-R008-publication.json').open('x',encoding='utf-8')as f:json.dump(cfg,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'closed':now.isoformat(),'files':len(files)},ensure_ascii=False))
