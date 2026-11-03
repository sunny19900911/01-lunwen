from pathlib import Path
import json,hashlib,datetime,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
src=R/'papers/damping-output-boundaries/manuscript/p06-actual-main-session026-v003.md'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='2aae66c26effa5c5436cd0b08cb883ead63d5f0ed12ffd88f47a9400a24cc370'
(S/'local-cache').mkdir(exist_ok=True)
(S/'local-cache/initial-git-status.txt').write_text(subprocess.check_output(['git','status','--short'],cwd=R).decode('utf-8',errors='replace'),encoding='utf-8')
(S/'plan.md').write_text('''# 实际5.2节与真实模态恢复的有限推进

用户本轮批准：5.2完整使用实际B/D模型结果，解释原控制峰降低、实际方案自身峰如何重新控制、装置出力是否与需求同时出现；争取恢复实际非线性q并核第2/13阶剪力。首次真实核钟2026-11-03 18:52:46+08，正式角色接续约18:56，不恢复旧窗口或设置无限后台研究。

## 本轮结束条件

完成实际时程对比和独审，重写5.2并合并4.3重复装置时序，旧300阶机制移至补充资料。针对q只完成一项有区分力的有限恢复诊断：先查原生q与动力学所需资料；若无直接q，实际18CM同基质量投影并在旧已知q_ref上检验混叠。不得用低误差或两阶截断拟合冒充真实FNA q；有足够证据才保留强逐阶结论。交新MD、实际逐页QA Word和真实后续缺口后结束。

## 有限数据范围

response先核第8层全六工况tB/tD/tQD的18行与峰值差额，再以旧72表客观筛选具有完整P的第8—11层24项最大峰时差，选RH4Y第10层（16.62→21.64，5.02s）追加一组。新图第8层RH4X（近原峰）与第10层RH4Y（重选控制时段），不得因旧预期强称第8层跨波包换峰。所有原六项保留。

modal只用已有actual300形状、18CM时程、同源质量/PF和旧参考q缓存；不读全节点/原大Excel，不新300ODE、拟合或求解。允许再用同权重投影B/D2、13阶作运动观测诊断，不能将其直接转成实际逐阶剪力。完整P只有32/88，完整端点模态与非线性广义力覆盖逐项检查。

## 所有权与流程

根唯一写主稿/共享账本/Git；response只roles/response，modal只roles/modal，audit只roles/audit。所有旧会话/稿件保留。数据先冻结后独审，根接已审数字写稿；不以多数意见替代证明。科学主要结果完成后不凑重复轮次。

新稿前缀p06-actual-timing-session027-。正常Git沿本任务已明确授权，仅根显式白名单当前会话冻结文本/小表/代码/图和新稿/最终Word；排除任何local-cache、原件、大数组、第三方全文及旧脏文件。命令级代理、暂存blob校验、普通push/lsremote核，不force/reset/登录或凭据。无求解器/模型API/收费/投稿。
''',encoding='utf-8',newline='\n')
(S/'status.json').write_text(json.dumps({'phase':'actual-timing-and-modal-recovery-diagnostic','started_at':'2026-11-03T18:52:46+08:00','recorded_at':now,'checkpoint_open':False,'source':src.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'main_author':'root','agents':['p06_actual_response','p06_actual_pairing','p06_actual_audit'],'no_solver':True,'no_new_ODE':True,'automation_created':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'claims.md').write_text('''# 本轮主张

- C01 testing：实际第8层六记录全时刻对照及装置同刻力；峰降低量与重新选峰差额仅记账，不是纯相位/装置直接贡献。
- C02 testing：RH4Y第10层是完整P24项中峰时变化最大，使用实际B/D/QD说明控制时段重新选择；不预设QD造成换峰。
- C03 testing：争取实际q2/13恢复。CM观测投影、真实q、旧线性q_ref分别标识；观察子空间非唯一不否定所有动态路径，但动态路径需完整输入及非线性模态广义力。
- C04 unresolved：真实目标逐阶剪力合成还需一致输出恢复/切口关系，B惯性投影不自动等于实际剪力算子。
''',encoding='utf-8',newline='\n')
(S/'runs.md').write_text(f'# 运行与去重\n\n首次核钟18:52:46+08；约18:56正式接续三个原子代理。{now}落盘计划。复用1700冻结72和旧缓存，不重跑旧rank36/300线性ODE。Story8先冻18行，再新增单一Story10RH4Y，输出按R002隔离；根筛选直接用旧72表，无新响应生产。\n',encoding='utf-8',newline='\n')
print(json.dumps({'at':now,'source':src.name,'bytes':src.stat().st_size},ensure_ascii=False))
