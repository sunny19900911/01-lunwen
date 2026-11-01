from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
rules=json.loads((O/'input-method-freeze.json').read_text(encoding='utf-8'));result=json.loads((O/'results.json').read_text(encoding='utf-8'));fr=json.loads((O/'baseline-S-and-modal-sources-freeze.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);assert all(sha(Path(d['path']))==d['sha256'] for d in fr['files']);main=rd(O/'baseline-sensitivity-ranked-floors-15.csv');control=rd(O/'right-controller-modal-source-summary-15.csv');modes=rd(O/'all-mode-signed-sensitivity-sources-3636.csv');top=rd(O/'top5-signed-sensitivity-sources-75.csv');near=rd(O/'near1pct-saved-grid-branches.csv');branches=rd(O/'top5-distinct-local-peaks-per-floor-75.csv');checks=rd(O/'closure-and-branch-verification-15.csv');Sdiff=Pdiff=0.
privatebase=Path(rules['inputs'][0]['path']);privatesens=Path(rules['inputs'][1]['path']);pub=Path(rules['inputs'][2]['path'])
with np.load(privatebase,allow_pickle=False) as a:tp=a['t'].copy();s0p=a['s_unitGamma'].copy();omp=a['omega'].copy();Bp=a['B_direct'].copy()
with np.load(privatesens,allow_pickle=False) as a:Zp=a['z_unit'].copy()
with np.load(pub,allow_pickle=False) as a:tu=a['t'].copy();s0u=a['s_unit'].copy();omu=a['omega'].copy();Bu=a['B'].copy();Zu=a['z_unit'].copy()
for case,t,s0,Z,w,B,div in [('SHW3X_fixed300',tp,s0p,Zp,omp,Bp,1000.),('publicExample5_H-E12140',tu,s0u,Zu,omu,Bu,1.)]:
    # Alternative multiplication order agrees and retains all controlling indices.
    V=(s0*w**2)@B.T/div;VZ=(Z*w**2)@B.T/div
    for j in range(B.shape[0]):
        r=next(d for d in main if d['Case']==case and d['Story']==f'Story{j+1}');pk=float(np.max(abs(V[:,j])));A=np.flatnonzero(abs(V[:,j])==pk);g=np.sign(V[:,j])*VZ[:,j];pp=float(np.max(g[A]));Sc=-pp/pk;Sdiff=max(Sdiff,abs(Sc-float(r['S_percent_per_damping_pp'])));Pdiff=max(Pdiff,abs(pk-float(r['P0'])));assert ';'.join(str(int(n)) for n in A[g[A]==pp])==r['right_controller_indices']
        rr=[d for d in control if d['Case']==case and d['Story']==r['Story']]
        for c in rr:
            mm=[d for d in modes if d['Case']==case and d['Story']==r['Story'] and d['controller_number']==c['controller_number']];assert len(mm)==len(w);vals=np.array([float(d['c_improvement_percent_per_damping_pp']) for d in mm]);assert abs(vals.sum()-Sc)<1e-11;selected=sorted(mm,key=lambda d:-abs(float(d['c_improvement_percent_per_damping_pp'])))[:5];tt=[d for d in top if d['Case']==case and d['Story']==r['Story'] and d['controller_number']==c['controller_number']];assert [d['Mode'] for d in selected]==[d['Mode'] for d in tt];assert abs(float(c['top5_c_sum'])+float(c['remaining_signed_c_sum'])-Sc)<1e-11
assert Sdiff<1e-11 and Pdiff<1e-8
for c in ['SHW3X_fixed300','publicExample5_H-E12140']:
    rr=[d for d in main if d['Case']==c]
    for d in rr:assert int(d['slow_improvement_rank'])==1+sum(float(e['S_percent_per_damping_pp'])<float(d['S_percent_per_damping_pp']) for e in rr)
assert max(float(d['relative_branch_check_error']) for d in checks)<1e-6
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),floors=15,all_mode_rows=len(modes),top5_rows=len(top),alternative_projection_S_max_abs_difference=Sdiff,alternative_projection_peak_max_abs_difference_force=Pdiff,exact_controller_indices_identical=True,all_modal_closures_pass=True,top5_selection_by_abs_c_pass=True,global_sign_invariance_max_difference=result['max_global_sign_flip_error'],linear_branch_max_check_relative_error=result['max_linear_branch_check_error'],finite_rank_cases=8,finite_rank_all_inversions_zero=all(d['strict_order_inversions']==0 for d in result['rank_validation']),source_and_baseline_freeze_hashes_unchanged=True,new_ODE=0,independent_role2_math_or_numerical_audit_not_replaced=True)
js('verification.json',verification)
for case,suffix in [('SHW3X_fixed300','private12'),('publicExample5_H-E12140','public3')]:
    lines=[f'# {case} 基准峰值敏感度工程表','', 'S与各c的单位均为剪力降幅百分数/阻尼百分点；按S从小到大排列。所有贡献取同一5%基准控制峰，属于导数分解。','', '|排序|楼层|控制峰时/s|S|主5阶有符号改善项（阶号:c）|其余阶之和|', '|---|---|---|---|---|---|']
    for r in [d for d in main if d['Case']==case]:
        c=next(d for d in control if d['Case']==case and d['Story']==r['Story']);lines.append(f"|{r['slow_improvement_rank']}|{r['Story']}|{r['right_controller_times_s']}|{float(r['S_percent_per_damping_pp']):.6f}|{r['top5_modes_signed_c']}|{float(c['remaining_signed_c_sum']):+.6f}|")
    lines+=['','精确活动峰数和右导数控制峰数在这组数据中均为1。1%近峰容差另列，不将相邻采样点或近峰称为精确并列峰。各候选的改善区间、宽度和判别另见baseline-S-and-existing-candidate-context-120.csv；不能由S单独决定候选是否达标。']
    (O/f'engineering-main-table-{suffix}.md').open('x',encoding='utf-8').write('\n'.join(lines)+'\n')
def get(case,story):return next(d for d in control if d['Case']==case and d['Story']==story)
p5=get('SHW3X_fixed300','Story5');p12=get('SHW3X_fixed300','Story12');u1=get('publicExample5_H-E12140','Story1');u3=get('publicExample5_H-E12140','Story3');ratio=float(p12['S_percent_per_damping_pp'])/float(p5['S_percent_per_damping_pp'])
text=['# 基准峰敏感度解释楼层改善差异','',
'SHW3X第5层的基准峰值敏感度在12层中最小，屋顶最大。第5层局部S=2.132，屋顶S=11.724，后者约为前者的'+f'{ratio:.3f}'+'倍。差异来自同一控制峰处有符号模态导数的合成：第5层13阶抵消2、10阶的促进，屋顶13、10阶则共同强烈促进。该解释只需要5%基准及其一阶阻尼导数。','',
'## 指标与适用范围','',
'在固定保存时间网格上，P0=max|V0|，精确计算活动集合A取|V0|=P0。P′₊=max_{n∈A} sign(V0[n])Vζ[n]，S=−P′₊/P0。阻尼增加b个百分点时，峰值降幅百分数在充分小的正增量下为S·b+o(b)；S不再乘100。S的读数为“剪力降幅百分数/阻尼百分点”。这15层均为单一计算活动峰，未遇精确并列；算法仍保留全部右控制峰，未以容差替代等号。','',
'在每个右控制峰分别求c_r=−sign(V0)B_srω²z_r/(P0·u)，私有模型u=1000、力为kN；公开框架u=1、力为kip。B已包含Γ。c>0促进下降，c<0抵消下降，Σc=S。主5项按|c|排序，剩余全部阶次仍保留有符号和；它不是有限候选阻尼下实际剪力的逐阶分担。','',
'## 第5层为何慢、屋顶为何快','',
'|量|第5层|屋顶|','|---|---|---|',
f"|基准控制峰时/s|{p5['time_s']}|{p12['time_s']}|",
f"|基准绝对峰/kN|{float(p5['P0']):.6f}|{float(p12['P0']):.6f}|",
f"|S|{float(p5['S_percent_per_damping_pp']):.6f}|{float(p12['S_percent_per_damping_pp']):.6f}|",
f"|所有促进项之和|{float(p5['promoting_positive_c_sum']):+.6f}|{float(p12['promoting_positive_c_sum']):+.6f}|",
f"|所有抵消项之和|{float(p5['opposing_negative_c_sum']):+.6f}|{float(p12['opposing_negative_c_sum']):+.6f}|",
f"|主5项|{p5['top5_modes_signed_c']}|{p12['top5_modes_signed_c']}|",
f"|其余295阶之和|{float(p5['remaining_signed_c_sum']):+.6f}|{float(p12['remaining_signed_c_sum']):+.6f}|",'',
'第5层10阶与2阶贡献分别为+1.473275、+1.042284，13阶为−.527229；全部正项+2.727068与负项−.595004相加为2.132064。屋顶13阶与10阶为+7.173442、+5.297377，4阶为−2.041323；全部正项+13.878999与负项−2.155150相加为11.723849。同一阶的促进/抵消作用会随楼层和控制峰时变化，不能把某阶永久称为有利或不利。','',
'比较S是相对于各层基准峰的归一化改善速度，不是绝对剪力减少量比较。第5层峰力变化率为−185.315 kN/阻尼百分点，屋顶为−99.687 kN/阻尼百分点；屋顶的归一化降幅较快并不意味着其绝对剪力变化更大。','',
'## 负敏感度与竞争峰不能删除','',
'公开框架三层S依次为−.012382、.246201、6.064525。Story1二阶的抵消项−.066682大于第一、三阶等促进项总和+.054300，使局部S略负；但已保存6%参照下降.743%，说明足够小增量下的导数符号不能保证增加1个百分点后的符号。这里只报告局部导数与有限参照的区别，不新增更小目标求解。','',
'公开屋面5%控制峰位于10.960s，第二局部峰位于16.520s，基准幅值仅低1.366277%。两峰分支S分别为6.064525与.555914；6%参照实际由16.520s控制，降幅2.654%，局部S×1个百分点的6.065%读数明显偏高。预先固定的1%近峰诊断没有包含这个独立第二峰，因此另存每层前5个局部峰十分必要；不能把“1%内无独立近峰”当作不会换峰。1%内相邻采样点另列，不冒充独立波峰。','',
'## 既有有限增量只作后验排序检查','',
'先于本轮有限参照表读取冻结15层S、主项和1%诊断。随后使用已保存6/7/8/10%参照检查，两组模型的层序在这4个目标上均与基准S层序一致：SHW3X每个目标66对楼层、公开框架每个目标3对，排序倒置均为0，Spearman系数均为1。这只是既有目标的后验结果；没有据此选模态或改容差，也不保证其他输入、候选或连续时间峰的排序。排序保持并不表示降幅数值线性成立，公开框架屋面就是例子。','',
'SHW3X 6%第5层/屋顶真实降幅为2.214%/10.811%，与2.132/11.724的局部读数接近；8%时真实值6.851%/28.320%已不能简单由3S等同。候选是否满足全部楼层10%要求仍按既定整时程区间、宽度及候选策略判断，S只定位重点楼层并解释局部来源。','',
'## 核查与交付','',
f"全部3636条模态贡献、75条主项及15层闭合核对通过；全部模态闭合最大误差{result['max_modal_closure_error']:.3e}，主5项加余项最大误差{result['max_top5_rest_closure_error']:.3e}。改变矩阵乘法次序独立复算S最大差{Sdiff:.3e}，控制峰索引相同；整体翻转力和导数符号后S不变。基准线性分支最大值的极小步长检查误差{result['max_linear_branch_check_error']:.3e}，仅验证有限网格导数规则，未生成任何有限阻尼响应。",'',
'工程主表分别为engineering-main-table-private12.md、engineering-main-table-public3.md；完整排名与有符号来源CSV、近峰表、后验排序表及120行候选区间衔接表均保留。输入、缓存及既有冻结文件散列一致。本轮无新ODE、拟合或参数扫描，计算等号仍属于双精度保存网格，未声称严格浮点或连续峰导数证明。①数学契约及②独立审核与④数值生产分开，④复核不替代独审。']
(O/'one-page-baseline-sensitivity-engineering-result.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 运行与隔离','',
'开始观测2026-11-01T15:23:22UTC（23:23:22+08），8分钟15:31:22UTC，主要10分钟15:33:22UTC，硬12分钟15:35:22UTC。基准S/模态小表实际15:26:49.058855UTC冻结，距开始207.06s。冻结前未读本轮有限目标参照表；这些目标此前已在R002/R005见过，不称盲解释。','',
'实际命令依次为python.exe -X utf8 baseline_peak_sensitivity_and_modal_sources.py与verify_explain_and_freeze.py，工作目录本仓库，脚本只写④R006；实际退出状态见工具。无新状态求解、求解器、拟合、新阈值按结果调整或Git操作。','',
'S的单位换算遵循①契约：定义仍按fractional zeta求导，但数值读数正好为降幅百分数/阻尼百分点，无额外100。私有/1000、公开奖励不/1000；使用B已含Gamma。主项全部按同一基准控制峰的|c|排序，未以候选降幅或原独立幅值排序替代。','',
'近峰阈值1%为预先指定诊断，并不是规范阈值、严格容差或不换峰保证；精确活动峰用计算值==P0。每层前5个局部峰包括阈值外峰，保留公开屋面1.366%差的竞争峰。完整所有近采样点单表，不混称独立近峰。所有模态来源表均为控制峰时的派生标量，不是完整时程缓存。']
(O/'run-isolation-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T15:23:22+00:00')).total_seconds();js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within10min=elapsed<=600,within12min=elapsed<=720,files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.iterdir()) if p.is_file()],new_ODE=0,new_target_reference=0,old_outputs_unchanged=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,verification=verification),ensure_ascii=False,indent=2))
