import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((O/'results.json').read_text(encoding='utf-8'));rule=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));Ns=rule['deduplicated_Ns']
def read(n):return list(csv.DictReader((O/n).open(encoding='utf-8-sig')))
state={N:read(f'N{N}-all12-threewaves-twozeta-convergence-72.csv') for N in Ns};ratio={N:read(f'N{N}-all12-threewaves-peakratio-intervals-36.csv') for N in Ns};murows=read('actual-native-UX-mass-ratio-cumulative-300.csv')
for d in rule['requested_schemes']:
 if d['threshold'] is not None:
  N=d['N'];th=d['threshold'];assert float(murows[N-1]['native_UX_cumulative_no_renormalization'])>=th and (N==1 or float(murows[N-2]['native_UX_cumulative_no_renormalization'])<th)
maxcurve=maxT=maxmetric=maxscale=maxratio=0.;statecount=0;undefined_states=[];undefined_pairs=[]
for record in r['local_only_arrays']:
 p=Path(record['path']);assert sha(p)==record['sha256'];case=p.name.split('-')[1];z=float(p.name.split('-z')[1].split('.')[0]+'.'+p.name.split('-z')[1].split('.')[1]) if False else float(p.stem.split('-z')[1]);orig=Path(next(d['path'] for d in rule['inputs'] if f'-{case}-z{z:g}-' in d['path']))
 with np.load(p,allow_pickle=False) as a,np.load(orig,allow_pickle=False) as b:
  assert list(a['Ns'])==Ns and np.array_equal(a['t'],b['t']);V=a['V_elastic_prefix_kN'];full=V[:,:,Ns.index(300)];s=b['s_unitGamma'];om=b['omega'];B=b['B_direct'];amp=abs(B)*(om**2*np.max(abs(s),axis=0))[None,:]/1000
  for j,N in enumerate(Ns):
   alt=(s[:,:N]*om[:N]**2)@B[:,:N].T/1000;maxcurve=max(maxcurve,float(np.max(abs(alt-V[:,:,j]))))
   for st in range(1,13):
    d=next(d for d in state[N] if d['Case']==case and float(d['zeta'])==z and d['Story']=='Story'+str(st));vn=V[:,st-1,j];v300=full[:,st-1];native=b['shear_native_Story'+str(st)+'_kN'];T=math.fsum(amp[st-1,N:]);maxT=max(maxT,abs(T-float(d['tail_independent_peak_sum_T_kN'])));dd=float(np.max(abs(v300-vn)));assert dd<=T+1e-8
    nrm=float(np.linalg.norm(vn-v300)/np.linalg.norm(v300));nativeNR=float(np.linalg.norm(abs(vn)-abs(native))/np.linalg.norm(native));maxmetric=max(maxmetric,abs(nrm-float(d['signed_NRMSE_vs_full300_reference'])),abs(nativeNR-float(d['peakN_native_absolute_curve_NRMSE'])));PN=float(np.max(abs(vn)));P300=float(np.max(abs(v300)));assert abs(PN-float(d['peakN_kN']))<1e-8
    if PN>T:
     scale=T/(PN-T);maxscale=max(maxscale,abs(scale-float(d['relative_peak_scale_full300_only'])));assert abs(PN-P300)/P300<=scale+1e-12
    else:assert d['relative_peak_scale_status']=='undefined_PN_le_T' and d['relative_peak_scale_full300_only']=='';undefined_states.append(dict(N=N,Case=case,zeta=z,Story=d['Story']))
    statecount+=1
for N in Ns:
 assert len(state[N])==72 and len(ratio[N])==36
 for d in ratio[N]:
  p5=float(d['PN5_kN']);p8=float(d['PN8_kN']);t5=float(d['T5_kN']);t8=float(d['T8_kN']);rf=float(d['full300_peak_ratio_8over5'])
  if p5>t5:
   lo=max(0,p8-t8)/(p5+t5);hi=(p8+t8)/(p5-t5);maxratio=max(maxratio,abs(lo-float(d['ratio_interval_lower_full300_only'])),abs(hi-float(d['ratio_interval_upper_full300_only'])));assert lo-1e-12<=rf<=hi+1e-12
  else:assert d['interval_status']=='undefined_PN5_le_T5' and d['ratio_interval_lower_full300_only']==d['ratio_interval_upper_full300_only']=='';undefined_pairs.append(dict(N=N,Case=d['Case'],Story=d['Story']))
assert statecount==360 and maxcurve<1e-8 and maxT<1e-8 and maxmetric<1e-12 and maxscale<1e-8 and maxratio<1e-12
lines=['# R007：物理模态截断的楼层剪力收敛','',
'**仅用实际μX预先冻结的首次90%/95%/99%规则和固定13/18/300阶，去重后为N=10、13、18、173、300。90%与95%均首次在第10阶达到。质量率95.18%的N10仍可产生64.73%的局部剪力曲线NRMSE；99.14%的N173相对300阶参照最大NRMSE为2.06%。这说明全楼参与质量率不能单独代替关键楼层输出收敛检查。所有方案保留，没有按8%结果择优。**','',
'## 预定义方案与比较对象','',
'μX来自actual有控Modal Participating Mass Ratios，按原Mode顺序累计，未除以300阶累计总量重新归一。90%/95%的首次阶数都是10，99%首次为173；额外固定13/18/300阶。本轮不重解ODE，只用R004冻结的300阶s/ω/B形成`V_N=Σr≤N B_sr ω²s_r/1000`。完整300阶在同一求和次序下生成，和R004既有全阶曲线最大浮点差3.64×10⁻¹¹kN。','',
'V_N与V300在相同参照正向下报告有符号NRMSE、峰幅差和峰时；与软件旧D两状态仅比较绝对曲线/绝对峰，η未知不试±。每个N都包含12层×3波×2ζ的72状态与36对峰比。完整截断曲线生成在新local-cache，未上传。','',
'|N|全楼μX累计 / %|相对300阶最大NRMSE / %|最大峰幅相对差 / %|最大峰降幅差 / 百分点|未定义峰误差尺度/峰比区间数|','|---:|---:|---:|---:|---:|---:|']
for d in r['summary']:lines.append(f"|{d['N']}|{100*d['native_UX_cumulative_mass_ratio']:.6f}|{100*d['max_signed_NRMSE_vs_full300']:.6f}|{100*d['max_abs_peak_relative_difference_vs_full300']:.6f}|{d['max_abs_peak_decrease_difference_vs_full300_pp']:.6f}|{d['undefined_relative_peak_scale_states']} / {d['undefined_peakratio_intervals']}|")
lines+=['','上表峰误差均以已定义的300阶参照为基准，N300为零是同一曲线的自对照；它对软件绝对曲线NRMSE最高仍为0.65822%，不能写成实际FE误差为零。质量率、波形NRMSE、峰幅差和峰降幅差分别报告，不互相替代。','',
'## Story5与Story12','',
'下表对每N、每层取三波两ζ的最大有符号NRMSE与最小U_N/U300；U为独立单阶峰值之和，不是实际合力。','',
'|N|楼层|最大NRMSE对300 / %|最小U_N/U300 / %|最大峰幅相对差 / %|','|---:|---|---:|---:|---:|']
for N in Ns:
 for story in ['Story5','Story12']:
  rr=[d for d in state[N] if d['Story']==story];lines.append(f"|{N}|{story}|{100*max(float(d['signed_NRMSE_vs_full300_reference']) for d in rr):.6f}|{100*min(float(d['U_N_over_U300']) for d in rr):.6f}|{100*max(abs(float(d['peakN_over_peak300_minus1'])) for d in rr):.6f}|")
lines+=['','N10虽有95.18%全楼μX，但全楼最小幅值包络留存率只有60.03%。这来自每层物理投影B对各阶幅值的不同加权，不能从基底质量累计直接移作每层剪力贡献率。截断还会改变有符号抵消，峰差的正负已保留，不能假定缺阶总使峰值变小。','',
'## 尾项尺度：只针对当前300阶参照','',
'对每层、记录与ζ计算`T_N=Σr>N max_t|v_r(t)|`、`U_N/U300`，由三角不等式有`||V300−VN||∞≤T_N`。全360状态均在1e−8kN数值容差内通过，最大未加容差浮点超量为1.71×10⁻¹³kN。若P_N>T_N，给`T_N/(P_N−T_N)`作为相对300阶峰幅差的保守尺度；否则留空undefined，不用无穷或0冒充结论。','',
'两ζ用`[max(0,PN8−T8)/(PN5+T5),(PN8+T8)/(PN5−T5)]`列全300峰比的区间，仅PN5>T5时定义。180对中已定义区间均包含全300峰比；N10的SHW3X/Story12、SHW4X/Story12区间未定义，原行完整保留。N10另有5个状态PN≤T，均为Story12（SHW3两ζ、SHW4两ζ、RH4的8%）。','',
'这些尺度由当前三波、时间窗和300阶线性惯性参照内的实际尾项计算，**不是实际全FE、无限阶、Ritz弹性恢复或新地震的误差界**。宽区间仅表示该尾项尺度保守，不能称局部剪力已达到工程容许误差。','',
'## 可执行的工程使用顺序','',
'先用明确全楼参与质量规则筛出候选阶数，再逐关键楼层检查同向曲线/峰时/峰幅和U留存；以全尾项T审查缺阶对峰及5→8峰比的影响。只有在指定输出、输入范围和工程容差下核过这些项，才对截断是否足够作决定。本轮未预设工程通过阈值，不推荐一个对所有楼层通用的最优N。质量可辨识、参照运动吻合与局部输出收敛是不同检查，Ritz全FE弹性恢复及实际FNA坐标范围保持不变。','',
'## 交付与核验','',
'每N分别72行状态表、36行峰比区间表；重点Story5/12为60行状态和30行峰比表；全部小CSV<1MB。另有5行汇总与6条预定义方案映射，完整数组仅新local-cache。独立以矩阵前向乘法重构全部5个N的曲线、用因子化单阶峰重新核T、重算360个有符号/绝对NRMSE和180个区间；不再积分或拟合。原R004源SHA不变。']
(O/'README-physical-truncation-convergence.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for d in rule['inputs']:assert sha(Path(d['path']))==d['sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:30:33+00:00')).total_seconds();assert elapsed<720
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,Ns=Ns,first_mass_threshold_crossings_verified=True,state_rows=statecount,ratio_rows=180,max_independent_prefix_rebuild_difference_kN=maxcurve,max_tail_recheck_difference_kN=maxT,max_NRMSE_recheck_difference=maxmetric,max_relative_peak_scale_recheck_difference=maxscale,max_peakratio_interval_recheck_difference=maxratio,all_tail_inequalities_pass_1e8_kN=True,undefined_relative_scales=undefined_states,undefined_ratio_intervals=undefined_pairs,all_defined_intervals_contain_full300=True,all_small_CSV_under_1MB=all(p.stat().st_size<1000000 for p in O.glob('*.csv')),sources_unchanged=True,no_new_ODE_fit_or_adaptive_N_choice=True,no_Git=True,scope='tail and relative error scales apply inside defined300 reference only, not actual FE')
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rule['inputs'],local_only_arrays=r['local_only_arrays'],array_upload_allowed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
