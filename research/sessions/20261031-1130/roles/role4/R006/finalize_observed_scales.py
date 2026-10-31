from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return list(csv.DictReader((O/n).open(encoding='utf-8-sig')))
r=json.loads((O/'results.json').read_text(encoding='utf-8'));rule=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));states=read('observed-amplitude-delta-and-native-anchor-deviations-72.csv');pairs=read('peak-decrease-discrepancy-and-observed-scales-36.csv');anc=read('same-time-chi-beta-and-observed-amplitude-288.csv')
assert len(states)==72 and len({(d['Case'],d['Story'],d['zeta']) for d in states})==72
assert len(pairs)==36 and len({(d['Case'],d['Story']) for d in pairs})==36
assert len(anc)==288 and len({(d['Case'],d['Story'],d['zeta'],d['anchor']) for d in anc})==288
maxchi=maxbeta=maxscale=0.
for d in states:
 delta=float(d['delta_abs_inf_observed_amplitude_kN']);assert float(d['absolute_peak_amplitude_difference_kN'])<=delta+1e-8
 for tag in ['native5_peak','native8_peak']:assert float(d[tag+'_absolute_observed_amplitude_deviation_kN'])<=delta+1e-8
for d in anc:
 E=float(d['reference_E_denominator_kN']);S=float(d['sum_abs_all300_signed_reference_terms_kN']);assert S>=abs(E)-1e-8
 if S:val=1-abs(E)/S;maxchi=max(maxchi,abs(val-float(d['chi_same_time_all300'])));assert -1e-12<=val<=1+1e-12
 assert d['signed_native_force_residual_unaligned']==''
 if E:
  vals=[]
  for k in range(1,6):val=float(d[f'fixed5_rank{k}_signed_ref_kN'])/E;maxbeta=max(maxbeta,abs(val-float(d[f'fixed5_rank{k}_beta'])));vals.append(float(d[f'fixed5_rank{k}_beta']))
  val=float(d['remaining295_signed_sum_kN'])/E;maxbeta=max(maxbeta,abs(val-float(d['remaining295_sum_beta'])),abs(math.fsum(vals)+float(d['remaining295_sum_beta'])-1))
 else:assert d['beta_status']=='undefined_E_zero' and all(d[f'fixed5_rank{k}_beta']=='' for k in range(1,6))
for d in pairs:
 assert float(d['absolute_peak_ratio_discrepancy'])<=float(d['observed_amplitude_ratio_mismatch_scale'])+1e-12
 diff=abs(float(d['reference_peak_decrease_percent'])-float(d['native_peak_decrease_percent']));maxscale=max(maxscale,abs(diff-float(d['absolute_decrease_discrepancy_percentage_points'])))
assert maxchi<1e-12 and maxbeta<1e-12 and maxscale<1e-10
priority=[d for d in pairs if d['Story'] in ['Story5','Story12']];cvals=[float(d['chi_same_time_all300']) for d in anc if d['chi_same_time_all300']!='']
lines=['# R006：观测幅值偏差尺度与同刻抵消/分担量','',
'**新增72状态的δ_abs∞及两个软件峰时刻的幅值偏差、36对峰降幅差与同量纲尺度、288行全300项Σ|v|/χ及固定top5+其余295项β。未改R005，没有新ODE、拟合或CM指标复算。**','',
'## 观测幅值偏差','',
'记E(t)为R004弹性惯性参照、N(t)为旧D两阻尼状态的软件Bottom VX。计算`d_abs(t)=|E(t)|−|N(t)|`与`δ_abs∞=max|d_abs(t)|`（kN），并列两个软件绝对峰时刻的d_abs及其绝对值。这里d_abs的正负仅表示幅值偏大或偏小，**不是未知η下的有符号剪力残差**。δ_abs∞是已保存两条曲线的观测幅值偏差，不认证全FE误差界、Ritz恢复误差或完整模型不确定性。','',
'72状态最大δ_abs∞为RH4X、Story2、5%的55.105732kN（t=5.38s）；其自身软件峰幅为10157.975374kN。最大归一化δ为RH4X、Story9、5%的0.878394%，对应49.588889kN。全部72状态满足峰幅差不超过该状态δ_abs∞，两个软件峰时刻的幅值差亦逐项保留。','',
'对每对5%/8%，同时列参照与软件峰降幅、其差的绝对值，以及归一化δ5/Pnative5和δ8/Pnative8。为避免把kN直接拿来比较比值，另列已观测幅值偏差导出的比值尺度：','',
'`scale_obs=(δ8 + R_native δ5)/P_ref5`，其中`R_native=P_native8/P_native5`。由当前曲线的峰幅偏差满足`|R_ref−R_native|≤scale_obs`；该式是**事后观测偏差的代数尺度**，不称对新地震或全FE的误差保证。乘100后单位为峰降幅的百分点。','',
'|记录|楼层|δ5 / kN|δ8 / kN|峰降幅差绝对值 / 百分点|观测偏差尺度 / 百分点|','|---|---|---:|---:|---:|---:|']
for d in priority:lines.append('|'+d['Case']+'|'+d['Story']+'|'+ '|'.join(f"{float(d[k]):.6f}" for k in ['delta5_abs_inf_observed_amplitude_kN','delta8_abs_inf_observed_amplitude_kN','absolute_decrease_discrepancy_percentage_points','observed_amplitude_decrease_mismatch_scale_percentage_points'])+'|')
lines+=['','全36对峰降幅差最大为RH4X/Story11的0.196533个百分点，对应观测比值偏差尺度0.572682个百分点。该尺度来自已观测曲线，不把它分派给某个模式或当作其余295项的物理来源。','',
'## 同刻全300项与β','',
'沿用R005的全部288个标签时刻及冻结top5，不重新排名。每态均按同刻全部300项求`Sabs=Σ|v_r|`、`χ=1−|Σv_r|/Sabs`。χ只描述该时刻有符号抵消，不等于峰叠加系数C=P/U；后者还涉及异时达峰与整个时间窗。此批χ范围为'+f"{min(cvals):.6f}—{max(cvals):.6f}"+'。','',
'对E=Σv≠0定义`β_i=v_i/E`，固定top5分别列β，其余295项先有符号合成后除E；分项和为1。E=0则β留空并标undefined，Sabs=0则χ留空，不填0、不截剪、不重归一。共同全局反号同时改变v与E，β不变；不以软件有符号VX作β分母。','',
'本批E零分母为0行；1440个top5 β中157个为负，范围−0.0587973892至0.9260648860，未出现>1的top5 β，但代码与字段均允许并保留这种情况。top5与其余295项β和的最大误差4.44×10⁻¹⁶，共同反号检查差为0。负β是参照内部的同刻抵消，不能改称负的原生FNA实测分担。','',
'## 核验与交付','',
'观测δ来自R004已保存E/软件数组；同刻300项只从冻结s、ω、B因子查询重构，无新积分。E重构与R004/005总量最大浮点差1.27×10⁻¹¹kN；新增χ、β、峰幅不等式及36对比值尺度均由小CSV独立复核。原R005文件SHA不变，所有新CSV小于1MB，完整数组仍只在R004/local-cache。','',
'文件：`observed-amplitude-delta-and-native-anchor-deviations-72.csv`；`peak-decrease-discrepancy-and-observed-scales-36.csv`；重点`Story5-Story12-decrease-and-observed-scales-6.csv`；`same-time-chi-beta-and-observed-amplitude-288.csv`及重点48行；`verification.json`和`delivery-manifest.json`。']
(O/'README-observed-amplitude-and-beta.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for d in rule['inputs']:assert sha(Path(d['path']))==d['sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:24:53+00:00')).total_seconds();assert elapsed<480
v=dict(frozen_utc=now.isoformat(),started_utc='2026-10-31T04:24:53+00:00',elapsed_seconds=elapsed,state_delta_rows=72,paired_decrease_rows=36,same_time_chi_beta_rows=288,max_chi_formula_recheck_error=maxchi,max_beta_formula_partition_recheck_error=maxbeta,max_decrease_discrepancy_recheck_error_percentage_points=maxscale,all_peak_deviations_le_observed_delta=True,all_ratio_discrepancies_le_observed_scale=True,beta_undefined_zero_E_rows=r['undefined_E_zero_rows'],negative_top5_beta_values=r['negative_top5_beta_values'],top5_beta_greater_one_values=r['top5_beta_over_one_values'],signed_native_force_residuals_all_blank=True,all_CSV_under_1MB=all(p.stat().st_size<1000000 for p in O.glob('*.csv')),source_SHA_unchanged=True,R005_unchanged=True,no_new_ODE_fit_or_CM_metric_Git=True,delta_claim='observed amplitude deviation only; not signed force residual or fullFE error bound')
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rule['inputs'],complete_arrays_local_only=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
