import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
r=json.loads((O/'results.json').read_text(encoding='utf-8'));rule=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));cm=read(O/'Y-CM-direct-forward-errors-216.csv');ff=read(O/'Y-VY-two-operator-absolute-diagnostics-144.csv');pairs=read(O/'Y-all12-threewaves-native-E-Q-peak-decrease-36.csv');upc=read(O/'Y-all12-threewaves-E-UPC-36.csv');time=read(O/'Y-native-exact-time-pairing-180.csv')
assert [len(cm),len(ff),len(pairs),len(upc),len(time)]==[216,144,36,36,180] and all(d['time_vectors_exact']=='True' for d in time)
masspath=Path(next(d['path'] for d in rule['sources'] if d['path'].endswith('identified-masses-before-old-comparison-36.csv')));mass=read(masspath);keys=sorted({(d['Story'],d['Diaphragm']) for d in mass},key=lambda k:(int(k[0][5:]),k[1]));my=np.array([float(next(d['identified_mass_kg'] for d in mass if d['Axis']=='Y' and (d['Story'],d['Diaphragm'])==k)) for k in keys]);actual=Path(next(d['path'] for d in rule['sources'] if d['path'].endswith('controlled_small_tables.json')));mdata=json.loads(actual.read_text(encoding='utf-8'));pf={int(v[1][1]):dict(zip(mdata['Modal Participation Factors'][1][1],v[1])) for v in mdata['Modal Participation Factors'][3:] if v[1][0]=='Modal'};mr=np.array([1000*float(pf[i]['ModalMass']) for i in range(1,301)])
maxG=maxB=maxout=maxmetric=maxpeak=maxclock=maxupc=0.;cmcount=forcecount=0
for info in r['unit_kernel_sources']:
 case=info['Y_case'];z=info['zeta'];source=Path(info['unit_kernel_path']);assert sha(source)==info['unit_kernel_sha256']
 with np.load(source,allow_pickle=False) as a,np.load(info['new_Y_output_path'],allow_pickle=False) as b:
  assert not any(k in b.files for k in ['s_unitGamma','sdot_unitGamma','omega']);assert np.array_equal(a['t'],b['t']);t=b['t'];s=a['s_unitGamma'];v=a['sdot_unitGamma'];om=a['omega'];px=a['phi_X'];py=a['phi_Y'];G=b['Gamma_Y'];B=b['B_Y'];Galt=np.array([math.fsum(float(my[j])*float(py[j,i]) for j in range(18))/mr[i] for i in range(300)]);maxG=max(maxG,float(np.max(abs(Galt-G)/np.maximum(abs(G),1e-300))))
  Balt=np.array([[math.fsum(float(my[j])*float(py[j,i]) for j,k in enumerate(keys) if int(k[0][5:])>=cut)*Galt[i] for i in range(300)] for cut in range(1,13)]);maxB=max(maxB,float(np.max(abs(Balt-B))));ux=s@(px*G).T;uy=s@(py*G).T;E=s*om**2;Q=E+v*(2*z*om);ee=E@B.T/1000;qq=Q@B.T/1000
  maxout=max(maxout,float(np.max(abs(ux-b['CM_predicted_UX_m']))),float(np.max(abs(uy-b['CM_predicted_UY_m']))),float(np.max(abs(ee-b['shear_elastic_inertia_predicted_kN']))),float(np.max(abs(qq-b['shear_classical_balance_predicted_kN']))))
  def check(y,p,d,absolute):
   global maxmetric,maxpeak,maxclock
   nr=float(np.linalg.norm(abs(p)-abs(y) if absolute else p-y)/np.linalg.norm(y));maxmetric=max(maxmetric,abs(nr-float(d['absolute_curve_NRMSE' if absolute else 'NRMSE'])));i=int(np.argmax(abs(y)));j=int(np.argmax(abs(p)));pe=float(abs(p[j])/abs(y[i])-1);maxpeak=max(maxpeak,abs(pe-float(d['peak_relative_error'])));maxclock=max(maxclock,abs(float(t[i])-float(d['native_peak_time_s'])),abs(float(t[j])-float(d['predicted_peak_time_s'])))
  for d in cm:
   if d['Case']!=case or float(d['zeta'])!=z:continue
   j=keys.index((d['Story'],d['Diaphragm']));ia=0 if d['Axis']=='UX' else 1;y=b[f"CM_native_{d['Story']}_{d['Diaphragm']}_UX_UY_m"][:,ia];p=ux[:,j] if ia==0 else uy[:,j];check(y,p,d,False);cmcount+=1
  amps=abs(B)*(om**2*np.max(abs(s),axis=0))[None,:]/1000
  for d in ff:
   if d['Case']!=case or float(d['zeta'])!=z:continue
   j=int(d['Story'][5:])-1;y=b['shear_native_'+d['Story']+'_VY_kN'];p=ee[:,j] if d['operator']=='elastic_inertia' else qq[:,j];check(y,p,d,True);forcecount+=1
   if d['operator']=='elastic_inertia':
    u=next(q for q in upc if q['Case']==case and q['Story']==d['Story']);suffix='5' if z==.05 else '8';U=float(amps[j].sum());maxupc=max(maxupc,abs(U-float(u['U'+suffix+'_kN'])),abs(float(np.max(abs(p)))/U-float(u['C'+suffix])))
assert cmcount==216 and forcecount==144 and maxout<1e-10 and maxmetric<1e-12 and maxpeak<1e-12 and maxclock==0 and maxG<1e-8 and maxB<1e-6 and maxupc<1e-8
maxratio=max(abs(float(d['ratio_identity_error'])) for d in upc);assert maxratio<1e-12
for d in pairs:
 native=100*(1-float(d['native_peak8_VY_kN'])/float(d['native_peak5_VY_kN']));Edec=100*(1-float(d['E_peak8_kN'])/float(d['E_peak5_kN']));Qdec=100*(1-float(d['Q_peak8_kN'])/float(d['Q_peak5_kN']));assert abs(native-float(d['native_peak_decrease_percent']))<1e-10 and abs(Edec-float(d['E_reference_peak_decrease_percent']))<1e-10 and abs(Qdec-float(d['Q_reference_peak_decrease_percent']))<1e-10
stats={}
for label,rr,nr in [('CM',cm,'NRMSE'),('E',[d for d in ff if d['operator']=='elastic_inertia'],'absolute_curve_NRMSE'),('Q',[d for d in ff if d['operator']=='classical_balance'],'absolute_curve_NRMSE')]:stats[label]=dict(count=len(rr),min_NRMSE=min(float(d[nr]) for d in rr),max_NRMSE=max(float(d[nr]) for d in rr),max_abs_peak_relative_error=max(abs(float(d['peak_relative_error'])) for d in rr),worst_NRMSE_row=max(rr,key=lambda d:float(d[nr])))
worstpair=max(pairs,key=lambda d:abs(float(d['E_minus_native_decrease_pp'])));newbytes=sum(d['bytes'] for d in r['local_only_Y_outputs']);sourcebytes=sum(next(x['bytes'] for x in rule['sources'] if x['path']==d['unit_kernel_path']) for d in r['unit_kernel_sources'])
(O/'global-statistics.json').write_text(json.dumps(dict(stats=stats,max_abs_E_native_peak_decrease_discrepancy_pp=abs(float(worstpair['E_minus_native_decrease_pp'])),worst_E_peak_decrease_pair=worstpair,new_Y_array_bytes=newbytes,reused_source_unit_array_bytes=sourcebytes),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# R010候选：复用冻结单位核的Y向无拟合输出检验','',
'**候选数字待②独审：216条CM对照最大NRMSE0.44310%、最大绝对峰误差0.07217%；E惯性投影VY参照的72条绝对曲线诊断最大NRMSE0.66915%、最大峰误差0.19921%。全部180组Y原生时间向量与冻结t逐项完全相同，无缺组或填补。Q两算子结果保留。没有新增ODE或复制单位s/sdot数组。**','',
'## 方向、核与物理系数','',
'R009已逐格确认SHW3Y/SHW4Y/RH4Y和对应X工况引用同一函数对象，SF/时间缩放/到达时间/Unstressed初始状态一致，仅Accel U1→U2、Angle=0。本轮直接引用R004相应case/ζ的同actual300 s、sdot、ω路径与SHA。三组原有SF不同，输入已缩放；本轮未再读ag乘SF或g，未重新积分。','',
'只更换方向投影：`S_Y=ΣmY φY`、`ΓY=S_Y/m_r`、`B_Y,s=ΓY Σabove mY φY`。mY用R002识别质量，φY用同actual300模态，m_r=1000×native ModalMass（kg·m²）。预测CM的UX/ UY分别用φX/φY乘ΓY s，不把X投影或X响应改名为Y。软件CM原生mm转m，剪力只取Bottom VY/kN。','',
'E=ΣB_Y ω²s/1000；Q=ΣB_Y(ω²s+2ζωsdot)/1000。两者都按固定参照方向，原生η未独立确认，故只比较VY绝对曲线和峰，不试±、增益或移时。未知Ritz恢复项及actual基与旧D两状态完整M/K身份混杂仍保留。q_ref,Y=ΓY s仍是线性参照坐标，不是取得实际Maxwell/FNA原生q。','',
'## 全位置结果','',
'下表是每波/ζ所有CM和12层的最大误差，均为%；VY的NRMSE使用绝对曲线。','',
'|记录|ζ|CM NRMSE|CM峰误差|E绝对NRMSE|E峰误差|Q绝对NRMSE|Q峰误差|','|---|---:|---:|---:|---:|---:|---:|---:|']
for case in ['SHW3Y','SHW4Y','RH4Y']:
 for z in [.05,.08]:
  cc=[d for d in cm if d['Case']==case and float(d['zeta'])==z];ee=[d for d in ff if d['Case']==case and float(d['zeta'])==z and d['operator']=='elastic_inertia'];qq=[d for d in ff if d['Case']==case and float(d['zeta'])==z and d['operator']=='classical_balance'];vals=[max(float(d['NRMSE']) for d in cc),max(abs(float(d['peak_relative_error'])) for d in cc),max(float(d['absolute_curve_NRMSE']) for d in ee),max(abs(float(d['peak_relative_error'])) for d in ee),max(float(d['absolute_curve_NRMSE']) for d in qq),max(abs(float(d['peak_relative_error'])) for d in qq)];lines.append('|'+case+f'|{z:.0%}|'+ '|'.join(f'{100*v:.5f}' for v in vals)+'|')
lines+=['','CM最不利NRMSE位于RH4Y、8%的UX；Y输入的主向UY和交叉UX均完整保留，不择位置。Q绝对曲线NRMSE的全记录范围为'+f"{100*stats['Q']['min_NRMSE']:.4f}%—{100*stats['Q']['max_NRMSE']:.4f}%"+'，不能因其较差而省略或直接据E较优认证软件剪力算子。','',
'## Story5/12峰降幅与U/P/C','',
'|记录|楼层|软件VY峰降幅 / %|E参照 / %|Q参照 / %|E−软件 / 百分点|','|---|---|---:|---:|---:|---:|']
for d in pairs:
 if d['Story'] in ['Story5','Story12']:lines.append('|'+d['Case']+'|'+d['Story']+'|'+ '|'.join(f'{float(d[k]):.6f}' for k in ['native_peak_decrease_percent','E_reference_peak_decrease_percent','Q_reference_peak_decrease_percent','E_minus_native_decrease_pp'])+'|')
lines+=['','全36对中E与软件峰降幅差的最大绝对值为'+worstpair['Case']+'/'+worstpair['Story']+f"的{abs(float(worstpair['E_minus_native_decrease_pp'])):.6f}个百分点。"+'原生与参照各自的峰时均保留，未按软件峰时强制参照峰相同。另交36行E的U/P/C：U为全部300阶独立峰之和、C=P/U、P8/P5=(U8/U5)(C8/C5)，恒等最大误差'+f'{maxratio:.3g}'+'；这是参照记账，不称原生FNA单阶唯一分担。','',
'## 核复用、完整数组与核验','',
'每波/ζ的新Y数组只保存新ΓY、BY、预测/原生输出及t，单份约2.1—2.5MB，合计'+f'{newbytes/1e6:.3f}'+'MB；不含s、sdot或ω，六份单位核只通过路径/SHA引用，避免复制约'+f'{sourcebytes/1e6:.3f}'+'MB的原X因子数组。按引用源s/ω与新BY可完整复原Y逐阶项。所有完整数组仅local-cache，不上传。','',
'独立从引用源和新Y数组重构216个CM及144个VY指标、峰误差/峰时与36对峰降幅，结果一致；用math.fsum从Y质量/φY/m_r重核ΓY和BY，没有拟合倍率。所有输入与单位核SHA不变，代码无ODE调用。180组原生时间向量在本轮实际读出后逐项核验，弥补R009仅摘要准入的边界。','',
'SHW3Y/SHW4Y/RH4Y与先前3X是同三个标量地震函数的两种输入方向，不能称六条独立地震事件；这是同一无拟合物理算法的事后方向输出检验，不是新盲测。未将SHW7Y或实际装置时程移入本数据组。小表候选交②独审后再用于正文裁决。','',
'主要文件：`Y-CM-direct-forward-errors-216.csv`、`Y-VY-two-operator-absolute-diagnostics-144.csv`、`Y-all12-threewaves-native-E-Q-peak-decrease-36.csv`、`Y-all12-threewaves-E-UPC-36.csv`、`Y-native-exact-time-pairing-180.csv`、`unit-kernel-reuse-6.json`及核验清单。']
(O/'README-Y-direction-output-validation.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for d in rule['sources']:assert sha(Path(d['path']))==d['sha256']
assert sha(O/'forward_Y_reusing_unit_kernels.py')==rule['code_sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:48:53+00:00')).total_seconds();assert elapsed<720
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,candidate_pending_role2_review=True,CM_rows_recomputed=cmcount,VY_rows_recomputed=forcecount,peak_decrease_pairs_rechecked=36,UPC_pairs=36,all_180_native_times_exact=True,missing_native_pairings=0,max_output_reconstruction_difference=maxout,max_NRMSE_recheck_difference=maxmetric,max_peak_error_recheck_difference=maxpeak,max_peak_time_recheck_difference_s=maxclock,independent_Y_Gamma_source_recheck_max_relative_difference=maxG,independent_Y_B_source_recheck_max_abs_difference_kg=maxB,max_UPC_recheck_difference=maxupc,max_UPC_identity_error=maxratio,no_new_ODE=True,source_unit_s_sdot_omega_not_duplicated=True,no_sign_gain_time_tuning=True,native_eta_not_confirmed=True,source_and_code_SHA_unchanged=True,no_Git=True,same3_functions_not6_independent_events=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rule['sources'],source_unit_kernel_references=r['unit_kernel_sources'],new_local_only_arrays=r['local_only_Y_outputs'],array_upload_allowed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(verification=v,global_stats={k:{a:b for a,b in d.items() if a!='worst_NRMSE_row'} for k,d in stats.items()},max_E_native_decrease_discrepancy_pp=abs(float(worstpair['E_minus_native_decrease_pp']))),ensure_ascii=False,indent=2))
