from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R001';Q=O.parent/'R002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
method=json.loads((O/'method-and-inputs-freeze.json').read_text(encoding='utf-8'));result=json.loads((O/'results.json').read_text(encoding='utf-8'));freeze=json.loads((O/'envelopes-frozen-before-target-open.json').read_text(encoding='utf-8'))
bindings=method['inputs'];assert all(sha(Path(d['path']))==d['sha256'] for d in bindings)
assert sha(O/'baseline-only-discrete-envelope-intervals-96.csv')==freeze['interval_csv_sha256']
assert sha(O/'local-cache/baseline-only-discrete-envelopes.npz')==freeze['array_sha256']
with np.load(bindings[0]['path'],allow_pickle=False) as a:
    t=a['t'].copy();om=a['omega'].copy();B=a['B_direct'].copy();s0=a['s_unitGamma'].copy()
with np.load(bindings[1]['path'],allow_pickle=False) as a:Vhat={(z,o):a[f'z{z:g}_order{o}_shear_inertia_kN'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
with np.load(O/'local-cache/baseline-only-discrete-envelopes.npz',allow_pickle=False) as a:E={(z,o):a[f'z{z:g}_order{o}_story_E_kN'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
P0=np.max(abs((s0*om**2)@B.T/1000),axis=0);rows=rd(O/'discrete-envelope-coverage-width-decisions-96.csv');maxL=maxU=maxD=0.;strict_curve_uncovered=0;peak_miss=0
truthidx=json.loads((Q/'reference-truth-array-index.json').read_text(encoding='utf-8'))
for b in truthidx:
    z=b['zeta']
    with np.load(b['path'],allow_pickle=False) as a:T=a['shear_elastic_inertia_predicted_kN' if z==.08 else 'shear_elastic_inertia_kN'].copy()
    for o in [1,2]:
        lo=np.max(np.maximum(0,abs(Vhat[z,o])-E[z,o]),axis=0);up=np.max(abs(Vhat[z,o])+E[z,o],axis=0);Pt=np.max(abs(T),axis=0)
        strict_curve_uncovered+=int(np.count_nonzero(abs(Vhat[z,o]-T)>E[z,o]))
        for j in range(12):
            r=next(d for d in rows if float(d['target_zeta'])==z and int(d['Taylor_order'])==o and d['Story']=='Story'+str(j+1));DL=1-up[j]/P0[j];DU=1-lo[j]/P0[j]
            maxL=max(maxL,abs(lo[j]-float(r['P_lower_kN'])));maxU=max(maxU,abs(up[j]-float(r['P_upper_kN'])));maxD=max(maxD,abs(DL-float(r['D_lower'])),abs(DU-float(r['D_upper'])))
            decision='meets' if DL>=.1 else ('insufficient' if DU<.1 else 'uncertain');assert r['interval_decision']==decision
            assert (r['operational_full_recompute']=='True')==(decision=='uncertain' or DU-DL>.05)
            peak_miss+=int(not(lo[j]<=Pt[j]<=up[j]))
assert maxL<1e-8 and maxU<1e-8 and maxD<1e-12 and peak_miss==0
# Matrix powers verify analytic displacement kernels without using candidate response arrays.
kernelmax=0.;powerchecks=0;dt=float(np.median(np.diff(t)))
for z in [.06,.07,.08,.10]:
    for m in [0,1,9,12,49,99,199,299]:
        w=om[m];wd=w*np.sqrt(1-z*z);a=z*w;h=np.exp(-a*dt);s=np.sin(wd*dt)/wd;c=np.cos(wd*dt);A=h*np.array([[c+a*s,s],[-w*w*s,c-a*s]])
        for step in [0,1,17,199,2690]:
            tau=step*dt;dec=np.exp(-a*tau);si=np.sin(wd*tau)/wd;co=np.cos(wd*tau);expected=dec*np.array([co+a*si,si]);power=np.linalg.matrix_power(A,step)[0]
            scaled=float(np.max(abs(power-expected)/np.array([1.,1/w])));kernelmax=max(kernelmax,scaled);powerchecks+=1
assert kernelmax<1e-10
fftchecks=rd(O/'FFT-vs-direct-positive-convolution-checks-64.csv');assert len(fftchecks)==64 and all(d['difference_within_guard']=='True' for d in fftchecks)
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),all_bound_rows_recomputed=96,source_hashes_unchanged=True,peak_lower_max_difference_kN=maxL,peak_upper_max_difference_kN=maxU,D_endpoints_max_difference=maxD,strict_curve_uncovered_samples=strict_curve_uncovered,strict_peak_uncovered_rows=peak_miss,analytic_kernel_vs_matrix_power_checks=powerchecks,max_scaled_kernel_difference=kernelmax,positive_FFT_vs_direct_checks=64,max_FFT_direct_difference_m=result['FFT_direct_max_difference_m'],all_FFT_direct_differences_within_guard=True,new_target_state_solves=0,continuous_time_certificate=False,rigorous_floating_point_certificate=False)
js('verification.json',verification)
old={ (float(d['target_zeta']),int(d['Taylor_order'])):d for d in rd(Q/'prediction-and-coth-bound-summary-8.csv') }
summary=result['summary'];priority=rd(O/'Story5-Story12-discrete-envelope-priority-16.csv');cost=rd(O/'measured-envelope-cost-8.csv')
text=['# 逐时离散缺陷包络的结果','',
'保留误差随时间的变化后，SHW3X小阻尼增量的判别区间明显收紧。在ζ=.06的二阶预测中，12层均可按既定10%减震目标和5个百分点宽度要求作出判断，无需按此策略复算；ζ=.07二阶只剩1层触发复算。ζ=.08及.10仍有大量楼层需要复算。原一、二阶预测未改变。','',
'## 方法和计算对象','',
'对每阶模态使用冻结的一、二阶位移及速度预测。候选阻尼的精确离散步进矩阵A和分段线性地震输入项b只由已知ω、ζ、dt及输入确定。定义d[n]=A xhat[n]+b[n]−xhat[n+1]，则误差满足e[n+1]=A e[n]+d[n]，且初值为零。将位移、速度缺陷分别与|E11(kdt)|、|E12(kdt)|作有限离散卷积，再按Σ|B|ω²/1000投影至各层。所有卷积输入及核均取绝对值，没有通过带符号缺陷重构真值。','',
'峰值下限为max_n max(0,|Vhat[n]|−E[n])，上限为max_n(|Vhat[n]|+E[n])。该写法保留逐时包络，比先取全时段最大误差再加减峰值更能利用时程信息。仍采用原先冻结的Dreq=.10、宽度上限.05；数学三分类、宽度及是否复算分别记录。潜在控制峰区段数量单列，不将区段重叠自动判为全时程峰值失效。','',
'对象为固定300阶线性参照、SHW3X、2691个保存时刻和dt≈.02s。全部目标在R002已知，本轮不称盲验证。界针对保存时刻的离散递推；未覆盖相邻采样时刻间的连续极值。','',
'## 96组完整结果','',
'|ζ|阶次|coth宽度中位数/百分点|离散包络宽度中位数/百分点|达到/不足/不确定|coth复算层数|离散包络复算层数|','|---|---|---|---|---|---|---|']
for d in summary:
    oo=old[d['target_zeta'],d['Taylor_order']];text.append(f"|{d['target_zeta']:.2f}|{d['Taylor_order']}|{100*float(oo['median_D_interval_width']):.3f}|{d['median_D_width_pp']:.3f}|{d['meets']}/{d['insufficient']}/{d['uncertain']}|{round(12*float(oo['full_recompute_fraction']))}/12|{d['operational_recompute_count']}/12|")
text+=['','96组峰值区间和96组整条保存曲线均覆盖对应线性参照；逐样本严格比较未覆盖数为'+str(strict_curve_uncovered)+'。96组中没有比原coth界更宽的区间；全部组合、失败和不确定结果均保留。真实减震率小于零的样本数为0，故不利响应漏判率分母不适用。低改善误放行和错误判为改善不足均为0。该结果只能说明当前已知案例的包络有效，不能将无不利样本解释为不利分支安全。','',
'## Story5和Story12','',
'|ζ|阶次|楼层|减震率下限/%|减震率上限/%|数学判断|宽度|复算|','|---|---|---|---|---|---|---|---|']
cn={'meets':'达到','insufficient':'不足','uncertain':'不确定','acceptable':'合格','too_wide':'超限'}
for d in priority:text.append(f"|{float(d['target_zeta']):.2f}|{d['Taylor_order']}|{d['Story']}|{100*float(d['D_lower']):.3f}|{100*float(d['D_upper']):.3f}|{cn[d['interval_decision']]}|{cn[d['width_status']]}|{'是' if d['operational_full_recompute']=='True' else '否'}|")
text+=['','ζ=.08二阶Story5区间5.374%—9.668%，可以判断达不到10%；同一候选的屋面区间虽位于10%以上，宽度仍超过5个百分点，故按已定规则复算。ζ=.10的两层均不能完成有效判断，保留为收紧方法仍失败的分支。','',
'## 代价和数值核查','',
f"8个目标/阶次包络的核心构造、FFT和投影合计{result['core_envelope_seconds']:.6f}s；FFT长度8192。核与核FFT按目标共享，只计一次。每个目标/阶次仍要遍历807000个模态状态缺陷，并做完整绝对卷积；本轮新增目标状态求解为0。R002中每次完整300阶参照求解加投影约.060—.063s，当前包络实现的计算量明显更大，不能据此声称提速。另需计入R001两套导数状态及8套输出预测，其独立CPU计时未记录，不能编造端到端加速比。",'',
'全楼复算以一次状态求解覆盖全部楼层；1层被标记仍触发1次全楼复算，绝不将层数当成求解次数。如果工程动作只要求拒绝某个未达到目标的方案，数学上的“不足”也可直接拒绝，需与追求精确响应的复算规则区分。本轮未选择该替代策略以改善统计。','',
f"64组固定模态的FFT结果与直接正卷积核对，最大绝对差{result['FFT_direct_max_difference_m']:.3e}m，均小于预置FFT保护量。160组解析核与矩阵幂核对的最大无量纲尺度差{kernelmax:.3e}。96组峰值端点、判断和复算标志独立重算通过。局部缺陷采用64ε量级保护，核采用128ε保护，FFT另加固定1e−12乘核L1与输入L1的保护；这些是工程浮点保护，不是有向舍入区间算术，未给libm超越函数误差作形式证明。",'',
'原R001预测、R002真值及工程阈值文件的散列未改变。逐时包络在本轮读取任何目标数组前保存并绑定散列；由于目标结果此前已见，不将该时序称为新的盲测。完整时程包络仅保存在local-cache，不入Git。未读取或计算新公开框架地震响应。','',
'详细表：discrete-envelope-coverage-width-decisions-96.csv；discrete-vs-coth-summary-8.csv；candidate-level-building-accounting-8.csv。复核：verification.json；输入和方法：method-and-inputs-freeze.json；包络冻结：envelopes-frozen-before-target-open.json。']
(O/'one-page-discrete-envelope-result.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 运行与隔离记录','',
'实际命令：python.exe -X utf8 research/sessions/20261101-2213/roles/role4/R003/discrete_absolute_defect_envelopes.py，退出0。随后运行verify_report_and_freeze.py，退出状态由执行工具记录。只写R003，不覆盖旧文件。无求解器、模型API、新输入或目标状态求解。','',
f"开始观测2026-11-01T14:56:29+00:00；方法冻结见method-and-inputs-freeze.json；包络冻结{freeze['frozen_utc']}；Story5/12表于2026-11-01T14:58:50.044601+00:00保存，距开始约141s。8分钟截止15:04:29UTC；硬截止15:11:29UTC。",'',
'内核计时不含源读取/散列、直接卷积检查和数组保存。all_envelope_stage_seconds包括包络阶段的检查、保存等开销；total_script_seconds另含输入、真值读取和评价。不把仅无states调用视为低工作量。R001导数成本仍不可忽略。','',
'冻结前只读基准、灵敏度、原预测、coth界及政策；冻结后仅读R002已保存真值数组，没有重算其状态。method_frozen_utc与envelope冻结时间可查。已知案例条件如实保留。','',
'核以解析E(kdt)构造，避免直接对连续|Gc|以dt取样而漏掉dt内振荡。它与采样时刻的精确离散递推一致；没有延伸为连续时程极值界。浮点保护参数在读本轮目标数组前冻结，未按覆盖或宽度回调。']
(O/'run-isolation-and-cost-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-11-01T14:56:29+00:00')).total_seconds()
files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file()]
js('delivery-manifest.json',dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within15min=elapsed<=900,files=files,local_only_arrays=[dict(path=str(O/'local-cache/baseline-only-discrete-envelopes.npz'),sha256=sha(O/'local-cache/baseline-only-discrete-envelopes.npz'),bytes=(O/'local-cache/baseline-only-discrete-envelopes.npz').stat().st_size)],no_old_outputs_modified=True,new_target_solves=0))
print(json.dumps(dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,verification=verification,report=str(O/'one-page-discrete-envelope-result.md')),ensure_ascii=False,indent=2))
