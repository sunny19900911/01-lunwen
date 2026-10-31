import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
r=json.loads((O/'results.json').read_text(encoding='utf-8'));rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));cm=read(O/'CM-direct-forward-errors-216.csv');ff=read(O/'shear-two-operator-absolute-diagnostics-144.csv');tc=read(O/'native-time-group-pairing-180.csv')
assert len(cm)==216 and len(ff)==144 and len(tc)==180 and all(d['exact_time_match']=='True' for d in tc)
assert len({(d['Case'],d['zeta'],d['Story'],d['Diaphragm'],d['Axis']) for d in cm})==216
assert len({(d['Case'],d['zeta'],d['Story'],d['operator']) for d in ff})==144
allmax=dict(CM_output_reconstruction_abs_m=0.,force_output_reconstruction_abs_kN=0.,NRMSE_recheck_difference=0.,peak_relative_error_recheck_difference=0.,peak_time_recheck_difference_s=0.,Gamma_relative_recheck=0.)
cmcount=forcecount=0
for d in r['arrays_local_only']:
 p=Path(d['path']);assert sha(p)==d['sha256'];case=p.name.split('-')[1];z=float(p.name.split('-z')[1].split('-')[0])
 with np.load(p,allow_pickle=False) as a:
  t=a['t'];s=a['s_unitGamma'];v=a['sdot_unitGamma'];om=a['omega'];G=a['Gamma_X'];px=a['phi_X'];py=a['phi_Y'];B=a['B_direct'];assert s.shape==v.shape==(len(t),300) and np.all(s[0]==0) and np.all(v[0]==0) and np.isfinite(s).all() and np.isfinite(v).all()
  xx=s@(px*G).T;yy=s@(py*G).T;allmax['CM_output_reconstruction_abs_m']=max(allmax['CM_output_reconstruction_abs_m'],float(np.max(abs(xx-a['CM_predicted_UX_m']))),float(np.max(abs(yy-a['CM_predicted_UY_m']))))
  ef=(s*om**2)@B.T/1000;qf=(s*om**2+v*(2*z*om))@B.T/1000
  allmax['force_output_reconstruction_abs_kN']=max(allmax['force_output_reconstruction_abs_kN'],float(np.max(abs(ef-a['shear_elastic_inertia_predicted_kN']))),float(np.max(abs(qf-a['shear_classical_balance_predicted_kN']))))
  def check(y,pred,d,abscurve):
   val=float(np.linalg.norm(abs(pred)-abs(y) if abscurve else pred-y)/np.linalg.norm(y));col='absolute_curve_NRMSE' if abscurve else 'NRMSE';allmax['NRMSE_recheck_difference']=max(allmax['NRMSE_recheck_difference'],abs(val-float(d[col])))
   i=int(np.argmax(abs(y)));j=int(np.argmax(abs(pred)));pe=float(abs(pred[j])/abs(y[i])-1);allmax['peak_relative_error_recheck_difference']=max(allmax['peak_relative_error_recheck_difference'],abs(pe-float(d['peak_relative_error'])));allmax['peak_time_recheck_difference_s']=max(allmax['peak_time_recheck_difference_s'],abs(float(t[i])-float(d['native_peak_time_s'])),abs(float(t[j])-float(d['predicted_peak_time_s'])))
  keys=sorted({(d['Story'],d['Diaphragm']) for d in cm},key=lambda k:(int(k[0][5:]),k[1]))
  for d in cm:
   if d['Case']!=case or float(d['zeta'])!=z:continue
   j=keys.index((d['Story'],d['Diaphragm']));ia=0 if d['Axis']=='UX' else 1;y=a[f"CM_native_{d['Story']}_{d['Diaphragm']}_UX_UY_m"][:,ia];pred=xx[:,j] if ia==0 else yy[:,j];check(y,pred,d,False);cmcount+=1
  for d in ff:
   if d['Case']!=case or float(d['zeta'])!=z:continue
   j=int(d['Story'][5:])-1;pred=ef[:,j] if d['operator']=='elastic_inertia' else qf[:,j];y=a['shear_native_'+d['Story']+'_kN'];check(y,pred,d,True);forcecount+=1
assert cmcount==216 and forcecount==144 and max(allmax.values())<1e-10
for b in rules['sources']:assert sha(Path(b['path']))==b['sha256']
globalstats={}
for label,rr,nrm in [('CM',cm,'NRMSE'),('elastic_inertia',[d for d in ff if d['operator']=='elastic_inertia'],'absolute_curve_NRMSE'),('classical_balance',[d for d in ff if d['operator']=='classical_balance'],'absolute_curve_NRMSE')]:
 globalstats[label]=dict(count=len(rr),min_NRMSE=min(float(d[nrm]) for d in rr),median_NRMSE=float(np.median([float(d[nrm]) for d in rr])),max_NRMSE=max(float(d[nrm]) for d in rr),max_absolute_peak_relative_error=max(abs(float(d['peak_relative_error'])) for d in rr),worst_NRMSE_row=max(rr,key=lambda d:float(d[nrm])),worst_absolute_peak_error_row=max(rr,key=lambda d:abs(float(d['peak_relative_error']))))
(O/'global-statistics.json').write_text(json.dumps(globalstats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# R004：实际300阶Ritz基的无输出拟合前向检验','',
'**全部18个CM、三波、5%/8%均完成。216条CM运动对照最大NRMSE为0.35437%、最大绝对峰误差0.06564%；弹性惯性投影剪力参照的72条绝对曲线诊断最大NRMSE为0.65822%、最大绝对峰误差0.23517%。经典阻尼平衡项参照的误差明显较大，两算子全部保留。剪力符号映射仍未由独立定义闭合，未宣布有符号剪力通过。**','',
'## 冻结输入与前向模型','',
'采用actual有控300阶CM形状、周期及ModalMass，质量直接复用R002识别结果；m_r=1000×native ModalMass（kg·m²），S_X=Σm_Xφ_X（kg·m），Γ=S_X/m_r（m⁻¹）。φ平动原生mm固定转m。每阶只求解零初始`sdotdot+2ζωsdot+ω²s=−ag`，由q_ref=Γs、u_ref=Σφq_ref预测X输入下各CM的UX/UY。全部物理系数固定，无训练、无输出回归、无原生PF倍率标定。','',
'三波严格为SHW3X、SHW4X、RH4X，使用既有load_inputs.py的ag（m/s²）、dt=0.02s与有效长度，包括冻结的SHW4末端输入延续约定。该loader读取的旧omega仅是其返回项，本轮计算未使用；所有六次积分均使用actual同源300阶omega。源SHA与代码均登记。','',
'以B_sr=S_sr Γ_r直接计算（不以S为分母），分别生成E=ΣBω²s/1000、Q=ΣB(ω²s+2ζωsdot)/1000，单位kN。B与Γ只来自质量/形状，不从旧019任何拟合系数迁移。','',
'## 全位置对照结果','',
'原生CM的UX/UY单位为mm，固定乘0.001；剪力为Bottom VX、kN。180组原生时间向量均与输入逐项完全相同，无缺组、缺时刻补零、移时或交集截断。CM的NRMSE为||u_ref−u_native||₂/||u_native||₂；峰误差为max|ref|/max|native|−1。剪力仅给|| |V_ref|−|V_native| ||₂/||V_native||₂及绝对峰诊断；原始有符号峰时和同刻值均留在CSV，但η未确认。下表各误差均为该波/状态的所有位置最大值（%）。','',
'|记录|ζ|CM NRMSE|CM峰误差|E绝对曲线NRMSE|E峰误差|Q绝对曲线NRMSE|Q峰误差|','|---|---:|---:|---:|---:|---:|---:|---:|']
for case in ['SHW3X','SHW4X','RH4X']:
 for z in [.05,.08]:
  cc=[d for d in cm if d['Case']==case and float(d['zeta'])==z];ee=[d for d in ff if d['Case']==case and float(d['zeta'])==z and d['operator']=='elastic_inertia'];qq=[d for d in ff if d['Case']==case and float(d['zeta'])==z and d['operator']=='classical_balance']
  vals=[max(float(d['NRMSE']) for d in cc),max(abs(float(d['peak_relative_error'])) for d in cc),max(float(d['absolute_curve_NRMSE']) for d in ee),max(abs(float(d['peak_relative_error'])) for d in ee),max(float(d['absolute_curve_NRMSE']) for d in qq),max(abs(float(d['peak_relative_error'])) for d in qq)]
  lines.append('|'+case+f'|{z:.0%}|'+ '|'.join(f'{100*v:.5f}' for v in vals)+'|')
lines+=['','CM最不利NRMSE为RH4X、5%、Story1/D1的UY（0.35437%）；最大CM峰误差在同位置RH4X、8%、UY（0.06564%）。没有择点、择波或删除小响应方向。E在RH4X、5%达到最大绝对曲线NRMSE0.65822%；Q的全部72条记录保留，不能因其较差就省略。','',
'## 有符号剪力与物理身份','',
'E正向定义按r_cutᵀKu冻结，原生Bottom VX保留软件表符号。独立η仍记未核，没有试选±以降低误差。例如SHW4X、5%、Story12的原生峰时28.34s，原生VX=+596.984511kN，E_ref=−596.200681kN；该反号观察不用于反推或批准η，必须另用软件切面定义/独立自由体核验。绝对曲线拟合良好不等于有符号身份已通过。','',
'实际Ritz基与旧D基准/直接8%的完整M/K身份仍有混杂。此次CM与E幅值在这些记录/窗口中吻合，支持把这一固定质量—模态前向链作为可复算工程参照；不反向认证全FE刚度恢复、Ritz切口残差为零或实际Maxwell/FNA逐阶唯一。Q比E误差较大，也不单凭此认证软件剪力一定只含弹性项。q_ref=Γs是新增线性解耦参照坐标，不是取得实际FNA原生q。Γ=0时本参照为零，不据此删除实际耦合模态。','',
'## 可复核存储与核验','',
'小表含216行CM误差、144行两算子绝对诊断、180组时间配对和300阶固定物理参数；每波/状态36条CM结果先行落盘。六份完整数组仅在local-cache：保存逐阶单位s、sdot、Γ、φ、B及原生/合成输出，以因子化形式完整保留逐阶项，避免复制巨大的Story×Mode×Time张量；按`B_sr[ω²s]`或`B_sr[ω²s+2ζωsdot]`可逐项复原。文件不上传。','',
'独立从保存数组重构全部CM及E/Q合成量，并重算216+144条NRMSE、峰误差和峰时；最大差均为0。180组时间逐项一致，源与代码SHA不变，零初始、300阶和两阻尼状态均核对。未安装依赖、调用求解器、新提Excel、输出拟合、调符号/增益/时移或操作Git。完整结果是事后独立输出检验，不称盲测。']
(O/'README-direct-forward-validation.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:11:33+00:00')).total_seconds();assert elapsed<900
v=dict(frozen_utc=now.isoformat(),started_utc='2026-10-31T04:11:33+00:00',elapsed_seconds=elapsed,within_primary12_minutes=elapsed<720,CM_rows_recomputed=cmcount,shear_rows_recomputed=forcecount,all_180_native_times_exact=True,native_pair_failures=0,rechecks=allmax,sources_unchanged=True,no_output_fit_or_old_fitted_coefficients=True,six_actual300_state_integrations_only=True,all_sign_gain_time_choices_frozen=True,shear_eta_independently_confirmed=False,actual_FNA_q_recovered=False,all_complete_arrays_local_only=True,no_Git=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rules['sources'],local_only_arrays=r['arrays_local_only'],array_upload_allowed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(verification=v,globalstats={k:{a:b for a,b in d.items() if not a.startswith('worst')} for k,d in globalstats.items()}),ensure_ascii=False,indent=2))
