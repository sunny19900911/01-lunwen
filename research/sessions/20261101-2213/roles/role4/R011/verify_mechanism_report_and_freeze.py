from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent;Sroot=O.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
rules=json.loads((O/'input-mechanism-rules-freeze.json').read_text(encoding='utf-8'));result=json.loads((O/'results.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);main=rd(O/'baseline-U-C-local-sensitivity-main-39.csv');selected=rd(O/'selected-mode-own-peak-vs-total-peak-57.csv');old=rd(O/'same-source-old-5pct-U-P-C-check-2.csv')
with np.load(rules['inputs'][0]['path'],allow_pickle=False) as a:t3=a['t'].copy();s3=a['s_unitGamma'].copy();w3=a['omega'].copy();B3=a['B_direct'].copy()
with np.load(rules['inputs'][1]['path'],allow_pickle=False) as a:Z3=a['z_unit'].copy()
with np.load(rules['inputs'][2]['path'],allow_pickle=False) as a:t4=a['t'].copy();s4=a['s0'].copy();w4=a['omega'].copy();B4=a['B'].copy();Z4=a['Z'].copy()
with np.load(rules['inputs'][3]['path'],allow_pickle=False) as a:tR=a['t'].copy();sR=a['s0'].copy();wR=a['omega'].copy();BR=a['B'].copy();ZR=a['Z'].copy()
with np.load(rules['inputs'][4]['path'],allow_pickle=False) as a:tu=a['t'].copy();su=a['s_unit'].copy();wu=a['omega'].copy();Bu=a['B'].copy();Zu=a['z_unit'].copy()
datasets=[('SHW3X',t3,s3,Z3,w3,B3,1000.),('SHW4X',t4,s4,Z4,w4,B4,1000.),('RH4X',tR,sR,ZR,wR,BR,1000.),('publicExample5',tu,su,Zu,wu,Bu,1.)];maxU=maxUp=maxP=maxPp=maxC=maxCp=maxSU=maxSC=0.;owncount=0
for case,t,s,Z,w,B,div in datasets:
    # Independent factorization: modal own peak times are shared across floors for
    # nonzero constant coefficients; use unit-kernel peaks then abs(coefficient).
    peakunit=np.max(abs(s),axis=0);primeunit=[]
    for m in range(len(w)):
        A=np.flatnonzero(abs(s[:,m])==peakunit[m]);primeunit.append(float(np.max(np.sign(s[A,m])*Z[A,m])) if peakunit[m]>0 else float(np.max(abs(Z[:,m]))))
    coef=B*w*w/div;U=np.abs(coef)@peakunit;Up=np.abs(coef)@np.array(primeunit);V=s@coef.T;VZ=Z@coef.T
    for j in range(B.shape[0]):
        story=f'Story{j+1}';r=next(d for d in main if d['Case']==case and d['Story']==story);PP=float(np.max(abs(V[:,j])));A=np.flatnonzero(abs(V[:,j])==PP);Pp=float(np.max(np.sign(V[A,j])*VZ[A,j]));CC=PP/U[j];Cp=(Pp-CC*Up[j])/U[j];Su=-Up[j]/U[j];Sc=-Cp/CC
        for val,key,which in [(U[j],'U_sum_modal_own_peaks','U'),(Up[j],'Uprime_right_force_per_zeta','Up'),(PP,'P_total_peak','P'),(Pp,'Pprime_right_force_per_zeta','Pp'),(CC,'C_PoverU','C'),(Cp,'Cprime_right_per_zeta','Cp'),(Su,'SU_percent_per_damping_pp','SU'),(Sc,'SC_percent_per_damping_pp','SC')]:
            diff=abs(float(val)-float(r[key]))
            if which=='U':maxU=max(maxU,diff)
            elif which=='Up':maxUp=max(maxUp,diff)
            elif which=='P':maxP=max(maxP,diff)
            elif which=='Pp':maxPp=max(maxPp,diff)
            elif which=='C':maxC=max(maxC,diff)
            elif which=='Cp':maxCp=max(maxCp,diff)
            elif which=='SU':maxSU=max(maxSU,diff)
            else:maxSC=max(maxSC,diff)
        assert U[j]+1e-9>=PP and 0<CC<=1+1e-12 and abs(Su+Sc-float(r['S_percent_per_damping_pp']))<1e-10
    for r in [d for d in selected if d['Case']==case]:
        j=int(r['Story'][5:])-1;m=int(r['Mode'])-1;coeff=abs(coef[j,m]);assert abs(float(r['p_mode_own_peak'])-coeff*peakunit[m])<1e-8;assert abs(float(r['pprime_mode_own_peak_force_per_zeta'])-coeff*primeunit[m])<1e-7;owncount+=1
assert maxSU<1e-10 and maxSC<1e-10 and maxU<1e-8 and maxUp<1e-6
# Same total-peak c as the earlier factor packet, not own-peak pprime/U.
earlier=rd(P/'R009/selected6-fixed-and-response-factors-48.csv');maxc=0.
for r in selected:
    if r['Case']=='publicExample5':continue
    e=next(d for d in earlier if d['Case']==r['Case'] and d['Story']==r['Story'] and d['Mode']==r['Mode']);maxc=max(maxc,abs(float(e['c_improvement_percent_per_damping_pp'])-float(r['c_at_total_peak_percent_per_damping_pp'])))
assert maxc<1e-10
mathpath=Sroot/'roles/role1/R007/baseline-S-and-UPC-one-page.md';mathbinding=dict(path=str(mathpath),sha256=sha(mathpath)) if mathpath.exists() else None
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),main_layers_verified=39,selected_modal_rows_verified=owncount,independent_unit_peak_factorization=True,max_U_difference_force=maxU,max_Uprime_difference_force_per_zeta=maxUp,max_P_difference_force=maxP,max_Pprime_difference_force_per_zeta=maxPp,max_C_difference=maxC,max_Cprime_difference=maxCp,max_SU_difference=maxSU,max_SC_difference=maxSC,max_prior_total_peak_c_difference=maxc,max_SU_SC_S_closure=result['max_SU_SC_closure'],all_triangle_inequalities_and_C_range_pass=True,old_5pct_same_source_checks_pass=all(abs(float(d['U_difference']))<1e-8 and abs(float(d['P_difference']))<1e-8 and abs(float(d['C_difference']))<1e-12 for d in old),exact_modal_active_max_count=result['max_modal_exact_active_count'],source_hashes_unchanged=True,role1_formula_read_binding=mathbinding,new_ODE=0,target_arrays_read=False,independent_role2_review_pending=True)
js('verification.json',verification)
priority=[r for r in main if (r['Case']=='SHW3X' and r['Story'] in ['Story5','Story12']) or r['Case']=='publicExample5'];table=['# 基准U/C敏感度关键两层与公开例','', '每增加1个阻尼百分点，SU、SC、S分别表示U、C、P的局部相对降幅百分数；不再乘100。SU+SC=S仅为基准对数导数关系，非有限增量百分数相加。','', '|输入/层|U5|C5|SU|SC|S|','|---|---|---|---|---|---|']
for r in priority:table.append(f"|{r['Case']}/{r['Story']}|{float(r['U_sum_modal_own_peaks']):.6f} {r['force_unit']}|{float(r['C_PoverU']):.9f}|{float(r['SU_percent_per_damping_pp']):+.6f}|{float(r['SC_percent_per_damping_pp']):+.6f}|{float(r['S_percent_per_damping_pp']):+.6f}|")
table+=['','完整39层：baseline-U-C-local-sensitivity-main-39.csv。57条选定模态自己的峰时/幅值导数与总峰c对照：selected-mode-own-peak-vs-total-peak-57.csv。旧基准两层同源核查：same-source-old-5pct-U-P-C-check-2.csv。']
(O/'priority-U-C-SU-SC-table.md').open('x',encoding='utf-8').write('\n'.join(table)+'\n')
text=['# 从基准U/C局部导数解释剪力改善','',
'基准5%下，第5层各阶独立峰幅总和U虽随阻尼增加而下降，合成比例C却上升，抵消了部分改善；屋顶U与C同时下降。这个结论现在由5%基准及其导数得到，不依赖5%与8%两个完整响应作差，也不把旧两态比值除以阻尼增量冒充导数。','',
'定义p_r=max|v_r|、U=Σp_r、P=max|Σv_r|、C=P/U。各p′_r在本模态真正活动峰中取sign(v_r)v′_r的最大值，U′=Σp′_r；P′则在总剪力真正活动峰中取导数。由商法则C′=(P′U−PU′)/U²，得到SU=−U′/U、SC=−C′/C及S=SU+SC。当前39层P、U均正，各自活动峰均唯一；零峰退化分支按契约保留，不用sign(0)代替max|v′|。','',
'SHW3X第5层SU=4.642959，SC=−2.510894，合计S=2.132064；即幅总改善被合成比例上升抵消。屋顶SU=6.373211，SC=5.350638，合计S=11.723849，幅总和合成比例的局部变化共同促使峰值下降。39层SU本次均为正，但SC有20层为正、19层为负；这是本批数据结果，不是预设SU或SC的符号。','',
'公开框架Story1提供了更清楚的抵消例子：SU=.560312，SC=−.572694，净S=−.012382。尽管各阶峰幅总量局部下降，合成比例的局部上升更大，总剪力峰对充分小的正增量反而略增。公开Story3为1.887498+4.177027=6.064525。这里不对有限6%/7%响应作新的推断。','',
'两种模态分项不能混用。SHW3X第5层13阶的自身峰在20.48s，p′_13=−3762.884167kN/ζ，对SU的贡献为+.339632；总剪力峰在22.92s，同阶c^P_13=−.527229。前者在模态自身峰求导、除以U；后者在总峰求导、投影总峰号、除以P。二者一个促进U下降、一个抵消P下降，并不矛盾。全部57条选定模态均保留两类时间与分母，不跨峰拼项。','',
'C描述合成峰占独立峰幅总和的比例，包含模态权重、有符号抵消、异时达峰、波形和控制峰选择，不能叫纯相位份额或独立因果百分比。SU与SC是相应量的局部相对变化率，只有在基准导数层面可相加为S；不能将有限U、C的百分变化直接相加，也不能把SU+SC当作有限候选精确预测。','',
'同源核查确认第5层U5=11079.289845kN、C5=.784509533；屋顶U5=1880.177172kN、C5=.452242207，与旧020/R005基准小表一致：U最大差'+f"{result['old_baseline_U_max_difference']:.3e}"+'kN，C最大差'+f"{result['old_baseline_C_max_difference']:.3e}"+'。旧5%→8%U/C只作为已有机制对照保留，没有读取候选状态拟合本轮导数。','',
'39层主表和57条选定模态由不同算法因式分解核查：先求单位核自身峰及导数，再乘|固定输出系数|，重建U与U′；总峰另用完整投影。SU+SC−S最大误差'+f"{result['max_SU_SC_closure']:.3e}"+'，全部三角不等式及0<C≤1检查通过。无新ODE、目标状态、输入或参数，未生成完整时程派生数组。①公式已全文核对，②独立审查仍待完成。']
(O/'one-page-baseline-U-C-sensitivity-mechanism.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 运行和边界','',
'开始观测2026-11-01T16:23:16UTC（2026-11-02 00:23:16+08），8分钟16:31:16UTC，12分钟硬限16:35:16UTC。关键39层/57条模态/旧两层核查于16:25:47UTC前实际保存。只写④R011。','',
'实际python.exe -X utf8 baseline_UC_derivative_mechanism.py退出0，verify_mechanism_report_and_freeze.py做既有缓存与标量小表验证和报告，退出由工具记录。没有新ODE、ζ扫描、输入/目标状态读取或拟合。旧优先表仅读U5/P5/C5字段用于同源核查，没有使用8%数值选公式或拟合导数。','',
'私有3×12层均用固定300阶Bω²s/1000，公开3层用12阶Bω²s，不重复Gamma。每一模态独立峰及其真正活动集在本模态时程定义；总峰活动集单独定义，两个峰不混用。零p分支取max|v′|，P/U归一退化留null；本批数据未发生零p/P/U，不宣称工程数据已验证所有退化情形。','',
'工程表只保留39层主表与57条预定模态小表，以及必要验证/同源比较，未写10836条全部模态峰表或全时程新大数组。selected priorities为三个私有输入Story5/Story12/自身最慢层去重，模式2/4/10/13/18/50；公开全3层模式1/2/3。没有用目标结果选择主项。','',
'本研究为既有有限网格固定输出参照的方向导数恒等机制，不是新基本定理、纯相位分担、有限阻尼精确预测或实际FNA逐阶唯一分解。旧R010独审通过消息已收到，本任务没有改其数据或主张。']
(O/'run-isolation-and-definition-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T16:23:16+00:00')).total_seconds();js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within12min=elapsed<=720,files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.iterdir()) if p.is_file()],new_ODE=0,target_state_arrays_read=False,main_rows=39,selected_modal_rows=57,old_outputs_unchanged=True,independent_role2_review_pending=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,verification=verification),ensure_ascii=False,indent=2))
