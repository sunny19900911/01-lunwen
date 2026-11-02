"""Create the new, human-authorized P06 session without touching old evidence."""
from pathlib import Path
import json, hashlib, subprocess
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
S = Path(__file__).resolve().parent
def save(name, value):
    p = S / name
    if p.exists():
        raise FileExistsError(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n' if not isinstance(value,str) else value, encoding='utf-8')

start='2026-11-02T19:17:23+08:00'
deadline='2026-11-02T21:47:23+08:00'
source=ROOT/'papers/damping-output-boundaries/manuscript/jgjg-session011-v004.md'
oldword=source.with_name('jgjg-session011-论文审阅稿-v004-排版稿.docx')
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'c30cbbccecc21be395ad9cf55de3f842f806cfea8372b72d180d240a3e532b7a'
assert hashlib.sha256(oldword.read_bytes()).hexdigest() == '2844e66450e65ec489e33f3e1c1db82f9abab5800aa52c363549bb20cfd0f998'
save('authorization-evidence.json', {'source_thread':'01a19bc4-95ce-77b3-875a-089a1dd7366c','actual_read':'read_thread, latest human userMessage 2026-11-02','human_quote':'这个逻辑发给论文研究主控，十小时循环对话框，开始新一轮论文研究；把p06进行深化，多角色循环讨论，15分钟上传github，只做主线，时间150分钟','scope':['P06深化','六既有角色跨聊派工与交流','15分钟普通GitHub同步','150分钟固定预算'],'start':start,'deadline':deadline})
save('plan.md', f'''# P06工程主线深化（session022）

固定窗口：{start} 至 {deadline}；21:02:23起最后45分钟集中成稿和Word；可完成后提前关闭，不重算窗口。

## 唯一主线
目标《建筑结构》。以双塔连体结构逐层、多输入剪力复核为中心：底层/平均值漏掉哪些楼层，原峰时读数高估多少，如何用常规输出形成含绝对需求的工程复核表。旧P06完整阅读并核原件SHA；旧稿和评测目录只读。

## 成功判据
1. 已有168条可信同输入比较整合为工程复核表：楼层/方向/输入，成对峰值，减幅，原峰时偏差，控制时刻，需查看内容。明确需求包络与最小减幅可由不同输入控制，不机械拼成一条记录。
2. 补清14方向工况独立性、输入/缩放/保存网格及模型配对已知和缺项；Bottom软件剪力定义短写，不擅自扣主体力。
3. 工程中心的新科学Markdown及可编辑Word；保留一节简洁机制，补实际有支持的文献至现行要求，核官方模板。渲染逐页实际查看，公式/数字与源稿一致。

## 分工和冻结
六既有角色：1方法，2独审，3原文/官方模板，4唯一派生数表，5唯一作者及Word，6工程流程。各只写本session/roles/roleN；作者独占manuscript/p06-engineering-session022-vNNN.md及Word。主控单写共享账本/轮次/选题卡/Git/调度。实际active不重派，有限8—12分钟任务必要15分钟，完成idle才派下一项；理论和数值经2独核后纳稿。每15分钟真实交流，30分钟有稿件增量。连续三轮无主线新证据则改具体检验或收束。

## 边界
不新布局、不P11预测/灵敏度、不CM修补、不重复大Excel/ODE/参数扫。实体装置只独立描述，不推因果减幅；d为评价恒等差非相位；三层H2人工高阶例非天然波一般率；后验删阶非重求基。真实期刊外审未提供，不伪称。原始数据只读，不ETABS/YJK/API/付费/投稿/凭据。

## 同步及关闭
本轮人类明确授权15分钟普通commit/push。根显式白名单只收本轮冻结可审小文本/脚本/CSV/图/新稿Word；排除local-cache、原数据、大数组、第三方全文、评测目录及所有旧dirty。核暂存blobSHA和远端，普通push命令级代理，失败每点最多重试一次，不强推/reset/读凭据或改全局。截止停新科研，只必要收集独审/交付/最后同步；正式暂停、view、实配置回读后删除本轮heartbeat，旧自动化保持不变。
''')
save('status.json', {'session':'20261102-1917','phase':'R001-active','start':start,'deadline':deadline,'final_writing_start':'2026-11-02T21:02:23+08:00','checkpoint_open':False,'no_new_scientific_dispatch':False,'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'automation':{'state':'not-created-yet'},'current_task':'首轮有限工程方法/数据契约/文献/稿件增量','git':{'pending_push':False}})
ids=['01a14756-7b7b-72a0-b079-e6c7874fc120','01a14756-7fe0-75f3-8671-bcd59e413052','01a14756-8408-7732-8d29-3380fcaeb7bb','01a14756-8805-7a42-b910-ae973f55d73e','01a14756-8bd0-7dc2-8362-fc1eab28af64','01a14a00-809e-7612-a7a4-889ab1e55f0d']
cursors=['a4ac1686-5034-48ef-9e7c-fe6208750c15:33','11a056de-2e65-48d9-90d8-2d3233b00402:100','3e1edb6e-1082-4df0-a7b1-358e7b877471:28','18d108d1-c129-40a5-b347-658f1f0c4b89:74','824ab043-4970-4d4a-8fa8-7ed81ac611bc:112','6334fe63-a9e8-4b7f-b356-e2608cd0403d:39']
save('threads.json',{'session':'20261102-1917','threads':[{'role':f'role{i+1}','threadId':x,'cursor':cursors[i],'actual_status':'notLoaded' if i in (1,2) else 'idle','task':'R001待正式派发'} for i,x in enumerate(ids)]})
save('claims.md','''# 本轮证据账本

- C01 已有P06：底层最小减幅仅3/14，168条减幅6.8513—30.5458%。旧审过；本轮只作工程整合，新增表冻结后独核。
- C02 d=(PM−|VM(tB)|)/PB≥0是共同保存网格恒等差，非相位因果。旧审过。
- C03 候选工程复核表应区分最小减幅输入与绝对需求控制输入；没有承载力资料不输出安全排序。proposed，待角色1/2/6对照。
- C04 同输入逐样本配对不自动认证全M/K/设置一致；实体装置模型不混入因果减幅。已知条件保留。
''')
save('runs.md', '# 真实运行记录\n\n- 19:17:23核真实时间，读取评测聊天原始人类授权。\n- 完整读P06-v004及20261021-2020最终总结；两个源SHA匹配。\n- 六角色实际wait快照：1/4/5/6 idle，2/3 notLoaded，最后turn均completed；允许本轮正式派发。\n- 旧git/automation3/4仍PAUSED，无本轮自动化，尚未声称建立。\n')
save('rounds/R001-start.md','# R001首轮\n\n先建可检查首轮，派6个既有角色单项有限任务。主控已完整读旧稿并确定工程增量：原表保留最小减幅控制输入，但还需并列需求包络控制输入和两者是否一致；不得只凭百分比给承载风险排序。旧图3已在P06内，不再重复新增同一图。\n')
save('initial-git-status.txt',subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8').stdout)
print(json.dumps({'session':str(S),'start':start,'deadline':deadline,'sources_sha_verified':True},ensure_ascii=False))
