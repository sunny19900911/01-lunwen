import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
from time import perf_counter
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;S=O.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rules=json.loads((O/'input-method-rules-freeze.json').read_text(encoding='utf-8'));res=json.loads((O/'results.json').read_text(encoding='utf-8'));fr=json.loads((O/'prediction-and-envelope-freeze.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);assert all(sha(Path(d['path']))==d['sha256'] for d in fr['local_arrays'])
with np.load(O/'local-cache/baseline-sensitivities-and-frozen-predictions.npz',allow_pickle=False) as a:
    t=a['t'].copy();ag=a['ag_in_s2'].copy();om=a['omega'].copy();B=a['B'].copy();s=a['s_unit'].copy();v=a['sdot_unit'].copy();Z=a['z_unit'].copy();ZD=a['zdot_unit'].copy();W=a['w_unit'].copy();WD=a['wdot_unit'].copy();PV={(z,o):a[f'z{z:g}_order{o}_shear_kip'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
with np.load(O/'local-cache/frozen-discrete-envelopes.npz',allow_pickle=False) as a:ENV={(z,o):a[f'z{z:g}_order{o}_E_kip'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
P0=np.max(abs((s*om**2)@B.T),axis=0);pred=rd(O/'all3-floor-candidate-peak-predictions-24.csv');rows=rd(O/'discrete-and-coth-prediction-intervals-24.csv');maxpred=maxinterval=0.
for r in rows:
    z=float(r['target_zeta']);o=int(r['Taylor_order']);j=int(r['Story'][5:])-1;VV=PV[z,o][:,j];EE=ENV[z,o][:,j];lo=float(np.max(np.maximum(0,abs(VV)-EE)));up=float(np.max(abs(VV)+EE));maxinterval=max(maxinterval,abs(lo-float(r['P_lower_kip'])),abs(up-float(r['P_upper_kip'])));p=next(d for d in pred if d['target_zeta']==r['target_zeta'] and d['Taylor_order']==r['Taylor_order'] and d['Story']==r['Story']);maxpred=max(maxpred,abs(float(np.max(abs(VV)))-float(p['predicted_peak_kip'])));DL=1-up/P0[j];DU=1-lo/P0[j];assert abs(DL-float(r['D_lower']))<1e-12 and abs(DU-float(r['D_upper']))<1e-12
    decision='meets' if DL>=.1 else ('insufficient' if DU<.1 else 'uncertain');assert decision==r['decision_status'];assert (r['v001_operational_recompute']=='True')==(decision=='uncertain' or DU-DL>.05)
assert maxpred<1e-10 and maxinterval<1e-10
# Independent continuous sensitivity ODE checks at baseline only. No finite candidate state solve.
# x=[s,v,z,zdot,w,wdot], forcing is linearly interpolated ag at each RK4 substep.
idx=np.array([0,1,2]);w=om[idx];kk=w*w;cc=.1*w;dt=.005;ref=np.stack([s[:,idx],v[:,idx],Z[:,idx],ZD[:,idx],W[:,idx],WD[:,idx]],axis=1)
def fun(x,acc):
    d=np.empty_like(x);d[0]=x[1];d[1]=-acc-cc*x[1]-kk*x[0];d[2]=x[3];d[3]=-cc*x[3]-kk*x[2]-2*w*x[1];d[4]=x[5];d[5]=-cc*x[5]-kk*x[4]-4*w*x[3];return d
checks=[];checktime=perf_counter()
for ns in [4,8]:
    h=dt/ns;x=np.zeros((6,3));out=np.zeros_like(ref)
    for n in range(1,len(t)):
        da=(ag[n]-ag[n-1])/ns
        for sub in range(ns):
            aa=ag[n-1]+sub*da;k1=fun(x,aa);k2=fun(x+h/2*k1,aa+da/2);k3=fun(x+h/2*k2,aa+da/2);k4=fun(x+h*k3,aa+da);x=x+h/6*(k1+2*k2+2*k3+k4)
        out[n]=x
    for i,mode in enumerate([1,2,3]):
        for j,name in enumerate(['s','v','z','zdot','w','wdot']):
            error=float(np.linalg.norm(out[:,j,i]-ref[:,j,i])/np.linalg.norm(ref[:,j,i]));checks.append(dict(Mode=mode,State=name,RK4_substeps=ns,relative_L2_error=error,zeta=.05,scope='baseline and analytic derivatives only; no candidate state'))
checktime=perf_counter()-checktime;cs('baseline-only-independent-RK4-checks-36.csv',checks)
ratios=[d['relative_L2_error']/next(e['relative_L2_error'] for e in checks if e['Mode']==d['Mode'] and e['State']==d['State'] and e['RK4_substeps']==8) for d in checks if d['RK4_substeps']==4];err8=max(d['relative_L2_error'] for d in checks if d['RK4_substeps']==8);assert err8<1e-5 and min(ratios)>14
audit=S/'roles/role2/R004';auditstatus='not yet frozen at verification time';auditbindings=[]
for name in ['one-page.md','freeze.json','delivery-manifest.json']:
    p=audit/name
    if p.exists():auditbindings.append(dict(path=str(p),sha256=sha(p)));auditstatus='files available; root/auditor must inspect full conclusion before target stage'
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),prediction_rows_recomputed=24,interval_rows_recomputed=24,max_prediction_peak_difference_kip=maxpred,max_interval_endpoint_difference_kip=maxinterval,baseline_independent_RK4_modes=[1,2,3],RK4_substeps=[4,8],RK4_max_relative_L2_at8=err8,RK4_error_halving_min_ratio=min(ratios),RK4_verification_seconds=checktime,baseline_verification_only=True,candidate_state_solves=0,target_response_reads=0,input_and_array_hashes_unchanged=True,static_audit_status=auditstatus,static_audit_file_bindings=auditbindings,continuous_time_or_rigorous_FP_certificate=False)
js('verification.json',verification)
summary=[]
for z in [.06,.07,.08,.10]:
    for o in [1,2]:
        rr=[d for d in rows if float(d['target_zeta'])==z and int(d['Taylor_order'])==o];cr=next(d for d in res['candidate_actions'] if d['target_zeta']==z and d['Taylor_order']==o);summary.append(dict(target_zeta=z,Taylor_order=o,median_discrete_D_width_pp=100*float(np.median([float(d['D_width']) for d in rr])),median_coth_D_width_pp=100*float(np.median([float(d['coth_D_width']) for d in rr])),**{k:cr[k] for k in ['v002_candidate_action','v001_flagged_floors','v001_building_recompute','v002_building_recompute','meets_floors','insufficient_floors','uncertain_floors']}))
cs('prediction-interval-and-policy-summary-8.csv',summary)
text=['# 公开三层框架：基准、灵敏度和候选预测冻结','',
'已完成全12阶、全7802点的5%零初值基准及一、二阶阻尼灵敏度，并冻结6%、7%、8%、10%的完整楼层剪力预测及离散缺陷区间。本轮没有计算或读取任何候选真值；预测准确度、覆盖和错误决策率均待后续独立评价。','',
'## 模型、输入和单位','',
'采用OpenSees官方Example5的三层三跨ElasticSection参数，由⑥自写线性框架组装；保留16节点、21梁柱、柱脚转动自由。48自由度删8个支承平动约束后为40，将28个无质量自由度静态凝聚，保留12个独立水平质量自由度；没有刚性楼板合并或附加小质量。全12阶质量归一化振型全部使用。此为公开数值教学框架的线性代数重构，不是软件运行结果或实测建筑。','',
'输入为Imperial Valley1979、ElCentro Array#12、140°的H-E12140，原记录PGA=.1433283g。按预先设置ag=rawg×386.4 in/s²、GMfactor=1，全7802点、名义dt=.005s、t=0至39.005s；不重复滤波或截取。所有相对状态及灵敏度初值为零，保留首样本输入。统一5%模态阻尼不同于原例2% Rayleigh设置，未运行OpenSees。','',
'单位核满足s″+2ζωs′+ω²s=−ag；q=Γs，剪力V=ΣBω²s，单位kip。本轮不除1000，不重复乘Γ。另以u=Phi·Γs及Vcut=C·u逐时刻对照。源文件和原始记录只读且不入Git。来源与权限说明复用③R002/public-multistory-benchmark.md。','',
'## 基准和候选点预测','',
'|楼层|5%峰值/kip|基准峰时/s|','|---|---|---|']
for d in rd(O/'baseline-floor-peaks-3.csv'):text.append(f"|{d['Story']}|{float(d['peak_kip']):.6f}|{float(d['peak_time_s']):.3f}|")
text+=['','|ζ|阶次|Story1预测减震率/%|Story2/%|Story3/%|','|---|---|---|---|---|']
for z in [.06,.07,.08,.10]:
    for o in [1,2]:
        pp=[next(d for d in pred if float(d['target_zeta'])==z and int(d['Taylor_order'])==o and d['Story']==f'Story{j}') for j in [1,2,3]];text.append(f"|{z:.2f}|{o}|"+'|'.join(f"{float(d['predicted_decrease_percent']):.3f}" for d in pp)+'|')
text+=['','一阶预测在所有四个候选上均提示Story1可能轻微增大；二阶预测则给出改善，ζ=.10时两阶的差异很大。这些是未验证的预测分歧，不可把负点预测写成真实不利响应。屋面5%控制峰在10.960s，部分候选点预测改由约16.52s峰控制；这说明旧峰时刻评价与完整时程最大值需要分别保留。','',
'## 冻结区间与预定策略','',
'离散缺陷使用已知候选参数、输入及冻结预测构造，不读取候选状态。完整解析矩阵核取绝对值后作双分量因果卷积，并按|B|ω²合成逐时剪力包络。分别记录原coth界，不取两界最小值。包络只是保存时刻上带固定工程浮点保护量的计算区间，不是连续峰或严格浮点证明。','',
'|ζ|阶次|离散区间宽度中位数/百分点|coth中位数/百分点|达到/不足/不确定层数|v001复算层数|v002候选动作|','|---|---|---|---|---|---|---|']
for d in summary:text.append(f"|{d['target_zeta']:.2f}|{d['Taylor_order']}|{d['median_discrete_D_width_pp']:.3f}|{d['median_coth_D_width_pp']:.3f}|{d['meets_floors']}/{d['insufficient_floors']}/{d['uncertain_floors']}|{d['v001_flagged_floors']}/3|{d['v002_candidate_action']}|")
text+=['','Dreq=10%及宽度上限5个百分点是事先冻结的工程演示输入。v001保留任何楼层不确定或宽度超限就完整复算的原规则；v002另允许任一目标楼层的整个区间低于10%时直接拒绝候选，全部楼层达到且宽度合格才通过，其余复算。一次完整分析覆盖全楼。上述动作尚无目标真值核对，不能据此宣称错误率为零或省算已验证。','',
'## 核查和代价','',
f"自身接口核查：质量正交最大误差{res['static_interface_checks']['modal_mass_max_abs']:.3e}，特征方程相对残差{res['static_interface_checks']['eigen_relative']:.3e}，C·Phi与Lω²相对差{res['static_interface_checks']['cut_modal_relative']:.3e}。动态基准两条剪力投影最大绝对差{res['baseline_cut_max_abs_difference_kip']:.3e}kip，8组预测两投影相对L2差不超过{res['predicted_cut_max_relative_L2']:.3e}。",'',
f"不经离散导数公式的独立RK4基准灵敏度核查覆盖1、2、3阶以及s/v/z/zdot/w/wdot，使用每步4与8子步；8子步最大相对L2误差{err8:.3e}，误差比最小{min(ratios):.3f}。该检查仅ζ=.05的基准及导数，不生成有限候选状态。24组预测峰值及24组区间端点、分类、复算标志重新核查通过。24组FFT与固定模态直接正卷积检查均在冻结保护量以内。",'',
f"实测基准状态求解{res['baseline_state_solve_seconds']:.6f}s；一、二阶联合导数递推{res['first_second_derivative_loop_seconds']:.6f}s；8组输出预测及截面对照{res['prediction_and_cut_check_seconds']:.6f}s；8组离散缺陷/核/FFT/投影核心共{res['absolute_bound_core_seconds']:.6f}s。另计直接卷积检查、I/O、散列及本轮独立RK4核查{checktime:.6f}s；这些验证开销不混入核心算法计时。未测候选完整分析，未声称提速。",'',
'②静态独审在本轮开始时尚未冻结；当前生产者检查通过不能替代独审。进入候选真值阶段前须核对②最终结论与接口散列。本轮至此停止，保持所有预测字节冻结。']
(O/'one-page-public-prediction-result.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
note=['# 运行隔离记录','',
'实际运行public_baseline_sensitivity_predictions.py退出0；随后verify_baseline_and_freeze.py实际运行，退出由执行工具记录。只写④R004，无新线程/代理、无Git/求解器/模型API，无候选真值。','',
'实际开始2026-11-01T15:08:59UTC（23:08:59+08），8分钟截止15:16:59UTC，12分钟截止15:20:59UTC。首张24行预测表于15:11:10.936988UTC保存。候选预测及包络冻结见prediction-and-envelope-freeze.json；后续验证没有改写这些文件。','',
'名义步长直接取冻结的.005s，未使用median(diff(t))；计算时间轴np.arange(N)*dt，仅以容差检查终点39.005s。R003旧字节不动。输入原样本首点并非强制改成0。','',
'状态缓存、完整时程和完整记录仅local-cache；Git可选小文本、CSV与自写脚本。新预测独立于公开模型候选真值；后续不能按真值回调两阶预测、界或政策。']
(O/'run-isolation-and-cost-notes.md').open('x',encoding='utf-8').write('\n'.join(note)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T15:08:59+00:00')).total_seconds();files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.iterdir()) if p.is_file()]
js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(__import__('datetime').timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within12min=elapsed<=720,files=files,local_only_arrays=fr['local_arrays'],target_truth_generated=False,target_response_read=False,prediction_and_interval_unchanged=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,verification=verification),ensure_ascii=False,indent=2))
