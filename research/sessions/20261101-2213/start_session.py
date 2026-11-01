from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'status.json').exists(),'Existing controller: recover instead'
for n in ['rounds','roles/role1','roles/role2','roles/role3','roles/role4','roles/role5','roles/role6']: (S/n).mkdir(parents=True,exist_ok=True)
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
start='2026-11-01T22:13:31+08:00';end='2026-11-02T04:13:31+08:00'
ids=['01a14756-7b7b-72a0-b079-e6c7874fc120','01a14756-7fe0-75f3-8671-bcd59e413052','01a14756-8408-7732-8d29-3380fcaeb7bb','01a14756-8805-7a42-b910-ae973f55d73e','01a14756-8bd0-7dc2-8362-fc1eab28af64','01a14a00-809e-7612-a7a4-889ab1e55f0d']
js(S/'authorization-evidence.json',dict(actual_read=now,source='latest direct human message in root chat',text='当前最有价值的提升，是让方法真正帮助工程师提前判断，按这个目标，展开6个小时循环，多角色，15分钟提交github交流，写论文，开始干，要按主线写，不要写外围，不要写防御性语言。',scope='new six-hour predictive-modal-damping research, six existing rolechats/cross-review, normal15minGitHub; notnewchats/solver/paid/submission',start=start,deadline=end))
plan='''# 六小时主线 用基准响应提前判断增阻尼后的楼层剪力

固定窗口2026-11-01 22:13:31至2026-11-02 04:13:31 Asia/Shanghai，UTC2026-11-01T20:13:31Z截止。最后一小时03:13:31起集中成稿，不从唤醒重算。会话021独立于已关闭020，不修改旧冻结稿或旧active-session。

## 唯一研究问题

使用基准ζ0=.05的模态运动及结构参数，提前预测候选阻尼取值下哪些层剪力改善有限、哪些层需要完整复算；实际Maxwell、布置调整、CM修补不是主攻。不把已获得完整候选响应后的U/C恒等记账包装成提前预测。

第一候选是基准点阻尼灵敏度及有限增量预测。s满足Lζs=-ag；z=∂ζs满足Lζz=-2ωsdot；可研究二阶w满足Lζw=-4ωzdot。一/二阶预测再按固定物理B加权求整窗最大值，不只在旧峰时刻代入。推导残差与可用的响应误差区间，对近等高峰、反号、抵消及较大δ寻找失败。灵敏度/三角不等式经典基础不称首创，工程预测可靠性与适用条件才是候选贡献。

## 预测和验证隔离

角色4唯一生产数值。先读取020的5%单位核/ω/B和既有输入，冻结只用基准信息的公式、参数和预测。旧8%响应已历史看过，只作已知案例验证，不称盲测。候选新目标ζ=.06/.07/.10/.12及δ负向敏感性只在预测冻结后逐批生成参考真值，是否采用更小目标按冻结规则与失败证据决定，不能按好结果删样本。每次只新增一个有区分力的实验。

误差评价同时包含峰值、低改善楼层漏判、不利响应漏判、区间覆盖/宽度和方法工作量。不以覆盖全部但毫无判别力的宽区间认成功；不假称计算提速。工程目标Dreq为输入参数，以10%作为演示值、D<0作为不利分支，均非规范阈值。模型/事件分组，X/Y同三函数两方向不是六独立事件，不随机拆时刻。公开结构/地震记录若可取得须先核出处/单位/身份，不能把合成输入称实震或生成参数模型称独立真实建筑。

先用当前300阶线性模型跑通预测链，再扩公开基准/独立输入。对比整体阻尼折减近似、少阶预测、旧峰时刻灵敏度与整窗预测，统一目标和精度/计算口径；完整求解只作参考真值。既有软件绝对曲线吻合与实际FNA逐阶唯一分开；方法正文简写必要模型条件，审核/失败日志另存。

## 角色和所有权

复用六个已授权聊天，见threads.json；notLoaded不是active，先真实快照后正式sendmessage唤起，不创建新聊天/子代理/W5。角色1少量候选与解析；2独立正确性/反例/数值审；3最近邻原文和公开基准线索；4唯一数据/新数值；5唯一新damping-prediction-session021-vNNN稿与最终Word；6工程决策规则/公平基线/创新覆盖。所有角色只写本会话自己role目录，作者独占新稿，主控共享账本/Git/调度。理论数值先交2、原文交1/5、审后交5，不以多数意见证明。active不重派，完成idle后一项8—12min，必要15min，全部受硬截止。每30min新稿/选题卡有实质增量，连续三轮无新主线证据换具体检验，不做重复外围审稿。

首轮先实算/冻结小结果再设置唯一主控15min正式自动化。末小时输出双语摘要、方法、真实预测算例、解析解释、工程步骤/结论、引用与Word；documents渲染逐页实际查看，不能只有文件存在。用户不希望防御性语言，正文采用工程常用表达；必要假定不删除，过程/细节另附。

## Git和停止

用户本轮新授权15min常规GitHub提交交流，仅主控显式白名单本会话冻结小文本代码CSV图和session021新稿/Word。排除所有local-cache、原Excel/EDB、完整时程/节点/大数组、外部论文全文、账户字段及旧12trackeddirty/unknown5E-07。不整目录stage，不收在写文件。核内容/diff/check/暂存blobSHA后普通commit/push origin/main；命令级代理http://127.0.0.1:17890，缺身份仅命令级Codex Paper Lab <codex-paper-lab@localhost.invalid>，lsremote核；失败每点最多一次重试，留真实待推，不强推/重置/改全局/读凭据/等登录。旧git/automation3/4保持PAUSED，旧git2和automation5已删不重启。

原件只读、不重提635/358MB、不ETABS/YJK求解或模型API、不付费投稿上传原件、不扫描无关304/305软件目录。04:13:31停止新科研，收在途已落盘关键增量/最终稿/普通中文/真实缺口与最终Git，正式暂停并读回后删除本轮自动化。可因完成提前收束，明确实际时间，不虚称满六小时连续运行。只重要发现/关键失败/用户必须决定/结束通知，例行留文件。
'''
(S/'plan.md').write_text(plan,encoding='utf-8')
js(S/'status.json',dict(session='20261101-2213',session_number=21,phase='first-predictor-experiment',start=start,deadline=end,deadline_utc='2026-11-01T20:13:31Z',writing_start='2026-11-02T03:13:31+08:00',checkpoint='R001-start',checkpoint_open=False,active_plan='plan.md',no_new_scientific_dispatch=False,last_actual=now,automation='not yetcreated; firstmanualscience beforeformalcreate',git_authorized=True,initial_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),old_tracked_dirty=12,next_task='formal firstlimited tasks to actualidle/notLoaded sixchats, thencollect realresults; notscheduledclaim beforetoolsuccess'))
js(S/'threads.json',dict(session='20261101-2213',threads=[dict(role='role'+str(i+1),threadId=id,task='R001 pendingformaldispatch',cursor=None) for i,id in enumerate(ids)]))
(S/'claims.md').write_text('# 主张账本021\n\nC021-01 proposed/analytic-derivation：基准模态阻尼灵敏度可组成候选ζ的楼层峰预测；须核残差、近重峰与有限增量，不由旧U/C恒等认定。\nC021-02 proposed/numerical-test：整窗预测较仅旧峰时刻的预测降低重要楼层误判；冻结算法后验证。\nC021-03 proposed/engineering-method：在给定Dreq和预测区间下，区分改善不足、满足目标、需复算；宽区间/大量弃权作为失败记录。\n',encoding='utf-8')
(S/'runs.md').write_text('# 实际运行记录021\n\n'+now+' 新授权/时钟/技能/旧脏状态已读；六历史聊天实际notLoaded或idle，无在途研究；远端8f60d93...一致。尚未派工/调度或新数值结果。\n',encoding='utf-8')
(S/'rounds/R001.md').write_text('# R001启动\n\n固定主线基准响应→候选阻尼的楼层峰预测→工程复算建议。历史解释作为起点，不重复完整旧300生产或把预测精度填成旧重构精度。实际任务与结果后续追加。\n',encoding='utf-8')
old=(R/'research/sessions/20261031-1130/publish_checkpoint.py').read_text(encoding='utf-8');old=old.replace("startswith('physical-modal-shear-session020-')","startswith('damping-prediction-session021-')")
(S/'publish_checkpoint.py').write_text(old,encoding='utf-8')
print(json.dumps(dict(created=str(S),time=now,start=start,deadline=end),ensure_ascii=False))
