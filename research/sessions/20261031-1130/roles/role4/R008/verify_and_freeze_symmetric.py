from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
O=Path(__file__).resolve().parent;P=O.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
r=json.loads((O/'results.json').read_text(encoding='utf-8'));rule=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));summary=read(O/'all12-threewaves-two-native-anchors-symmetric-change-72.csv');parts=read(O/'fixed5-and-remaining295-symmetric-components-432.csv');oldanchors=read(P/'R005/all12-four-anchors-both-zeta-signed-reference-288.csv')
groups={};singleerr=hbound=aggregate=partclosure=oldmatch=directionerr=0.;count=0
for rec in r['all_permode_files']:
 path=O/rec['name'];rr=read(path);assert len(rr)==1800
 case=path.name.split('-')[0];label=path.name.split('-')[1]
 for d in rr:
  key=(case,d['Story'],label);groups.setdefault(key,[]).append(d);a5=float(d['A5_kN']);a8=float(d['A8_kN']);v5=float(d['v5_kN']);v8=float(d['v8_kN']);av=float(d['amplitude_change_kN']);hv=float(d['normalized_waveform_change_kN']);un=float(d['unallocated_delta_kN']);singleerr=max(singleerr,abs(v8-v5-av-hv-un))
  if a5>0 and a8>0:
   h5=float(d['h5']);h8=float(d['h8']);hbound=max(hbound,abs(h5)-1,abs(h8)-1);assert abs(h5-v5/a5)<1e-12 and abs(h8-v8/a8)<1e-12
   singleerr=max(singleerr,abs(av-(a8-a5)*(h8+h5)/2),abs(hv-(a8+a5)*(h8-h5)/2));assert un==0
  elif a5==a8==0:assert av==hv==un==v5==v8==0 and d['h5']==d['h8']==''
  else:assert av==hv==0 and un==v8-v5 and d['h5']==d['h8']==''
  count+=1
assert count==21600 and len(groups)==72 and hbound<1e-12
for d in summary:
 key=(d['Case'],d['Story'],d['anchor']);rr=groups[key];assert len(rr)==300 and {int(x['Mode']) for x in rr}==set(range(1,301));assert len({x['time_s'] for x in rr})==1
 vals={name:math.fsum(float(x[field]) for x in rr) for name,field in [('v5','v5_kN'),('v8','v8_kN'),('a','amplitude_change_kN'),('h','normalized_waveform_change_kN'),('u','unallocated_delta_kN')]}
 aggregate=max(aggregate,abs(vals['v5']-float(d['y5_ref_signed_kN'])),abs(vals['v8']-float(d['y8_ref_signed_kN'])),abs(vals['a']-float(d['amplitude_change_sum_kN'])),abs(vals['h']-float(d['normalized_waveform_change_sum_kN'])),abs(vals['v8']-vals['v5']-vals['a']-vals['h']-vals['u']))
 label='native_abspeak_5pct' if d['anchor']=='native5_abspeak' else 'native_abspeak_8pct'
 for z,field in [(.05,'y5_ref_signed_kN'),(.08,'y8_ref_signed_kN')]:
  old=next(x for x in oldanchors if x['Case']==d['Case'] and x['Story']==d['Story'] and x['anchor']==label and float(x['zeta'])==z);oldmatch=max(oldmatch,abs(float(old['reference_sum_signed_kN'])-float(d[field])));assert float(old['time_s'])==float(d['time_s'])
 pp=[x for x in parts if x['Case']==d['Case'] and x['Story']==d['Story'] and x['anchor']==d['anchor']];assert len(pp)==6 and sum(int(x['mode_count']) for x in pp)==300
 for p in pp:
  selected=[x for x in rr if int(x['Mode'])==int(p['Mode'])] if p['component']!='remaining295' else [x for x in rr if x['top5_fixed5']=='False'];assert len(selected)==int(p['mode_count'])
  for field,source in [('v5_signed_ref_kN','v5_kN'),('v8_signed_ref_kN','v8_kN'),('amplitude_change_term_kN','amplitude_change_kN'),('normalized_waveform_change_term_kN','normalized_waveform_change_kN'),('unallocated_zero_amplitude_delta_kN','unallocated_delta_kN')]:partclosure=max(partclosure,abs(math.fsum(float(x[source]) for x in selected)-float(p[field])))
 sig=int(d['sigma5_reference'])
 if sig:
  directionerr=max(directionerr,abs(-sig*float(d['amplitude_change_sum_kN'])-float(d['old_direction_amplitude_weakening_kN'])),abs(-sig*float(d['normalized_waveform_change_sum_kN'])-float(d['old_direction_waveform_weakening_kN'])))
  if d['state_totals_opposite_sign']=='False':directionerr=max(directionerr,abs(float(d['reference_absolute_weakening_kN'])-float(d['old_direction_total_weakening_kN'])))
assert max(singleerr,aggregate,partclosure,oldmatch,directionerr)<1e-8
priority=[d for d in summary if d['Story'] in ['Story5','Story12']]
lines=['# R008：同刻模态幅值变化与归一波形变化的对称记账','',
'**12层×3波×两个软件绝对峰时刻共72个同刻恒等式完成；全部300阶、固定top5与其余295项均保留。幅值项和归一波形项的相反作用没有删去。此为给定物理来源线性参照及峰幅归一化下的确定记账，不是纯相位效应、因果百分比或原生FNA唯一分解。**','',
'## 定义与零幅值规则','',
'在每个选定时刻τ，同一阶的5%/8%参照力为v5、v8，取各自全冻结时间窗的`Aζ=max|vζ|`、`hζ=vζ/Aζ`。A均非零时采用','',
'`Δv=v8−v5=(A8−A5)(h8+h5)/2+(A8+A5)(h8−h5)/2`。','',
'第一项记幅值变化项，第二项记归一波形变化项；后者包含形状、相对时序及符号变化，不改称纯相位。单态A为零时，不给h任意赋值，完整Δv列入未分配项；双态A都零则Δv及两分项为0，h仍留空。本批21600个模式—时刻点没有零幅值，但分母规则已在计算前冻结。','',
'每层每波只在软件5%绝对峰时刻τ5及8%绝对峰时刻τ8分别取两状态；时刻相同时仍保留两个标签，不跨τ5/τ8作差。top5沿用R005的5%单阶包络排名，固定在两状态、两个时刻；其余295项按同一时刻直接有符号合计，不是拟合残差。','',
'## 原5%参照方向与绝对幅值','',
'以全300项合成y5定义`σ5=sign(y5)`，每个变化分项乘`−σ5`得到沿原5%参照方向的削弱量，正数削弱、负数抵消削弱。σ5由合成值定义，不能对每个模式各自选择有利符号。若y5=0则该方向未定义；若新旧合成反号，沿旧方向的投影不称绝对幅值削弱，另列`|y5|−|y8|`。本批72行没有合成反号或零方向。','',
'重点六对、双时刻的结果如下，单位kN。幅值/波形列均已沿原σ5转为削弱量，可直接保留负号；未分配项本批均为0。','',
'|记录|楼层|软件峰时标签 / t|幅值项削弱|归一波形项削弱|同刻净削弱|','|---|---|---|---:|---:|---:|']
for d in priority:
 label='5%' if d['anchor']=='native5_abspeak' else '8%';lines.append('|'+d['Case']+'|'+d['Story']+f"|{label} / {float(d['time_s']):.2f}s|{float(d['old_direction_amplitude_weakening_kN']):.6f}|{float(d['old_direction_waveform_weakening_kN']):.6f}|{float(d['old_direction_total_weakening_kN']):.6f}|")
lines+=['','SHW3X/Story5在22.92s的幅值项削弱739.706906kN，但归一波形项为−132.656071kN，抵消一部分削弱，净值607.050835kN；在22.94s应另行读取742.909383与−158.626182kN。607.050835kN是22.92s同刻差，不是两状态各自全时程峰的差。','',
'SHW4X/Story12在28.34s的两项均促进削弱，为81.297399与108.422581kN，合计189.719980kN；在20.58s分别为66.336892与33.964583kN，合计100.301474kN。这两行是两个独立同刻记账，不相减拼成跨峰时刻“相位份额”。RH4X/Story5的归一波形项同样抵消幅值削弱，负项完整保留。','',
f"全72行中，沿原方向的幅值变化总项为负有{r['amplitude_old_direction_weakening_negative_rows']}行，归一波形变化总项为负有{r['waveform_old_direction_weakening_negative_rows']}行。"+'重复峰时标签仍是记录项，不把这些行数当作独立地震事件数。','',
'## 可复算证据与适用范围','',
'完整72行列出y5/y8、Δy、两分项、未分配项、σ5、沿原方向削弱量、绝对幅值削弱及反号标记；432行展示top5各项和其余295项。21600个原模式—时刻点按case、峰时标签及上下6层拆成12个1800行CSV，每文件不超过0.43MB；重点Story5/12为12行合成和72行组件表。','',
'源为R004冻结的s/ω/B和R005独立峰A及固定top5；没有新ODE、拟合、移时或参数分析。逐项对称恒等、300项/展示组件求和、与R005同刻总量及σ5方向关系均独立核对，最大误差小于1e−8kN（实际300项闭合最大3.95×10⁻¹²kN）。原文件SHA不变，完整数组仍本地。','',
'软件原生Bottom VX的η仍未独立确认；所列有符号分项均是参照正向，软件仅用绝对峰时刻及同刻绝对量提供对照。实际Ritz恢复和实际FNA坐标范围保持不变。本分解不能反向认证原生逐阶唯一，也不将归一波形项升级为因果机制百分比。']
(O/'README-symmetric-same-time-mechanism.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for d in rule['inputs']:assert sha(Path(d['path']))==d['sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:36:53+00:00')).total_seconds();assert elapsed<600
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,mode_point_rows_checked=count,paired_same_time_anchors=72,displayed_components=432,priority_anchor_rows=12,independent_single_mode_identity_max_error_kN=singleerr,independent_all300_aggregate_max_error_kN=aggregate,independent_component_partition_max_error_kN=partclosure,max_difference_vs_R005_native_anchor_reference_totals_kN=oldmatch,max_old_direction_vs_absolute_weakening_identity_error_kN=directionerr,all_normalized_waveforms_within_unit_peak_tolerance=True,no_one_zero_amplitude_observed=True,no_opposite_sign_totals_observed=True,negative_waveform_weakening_rows_retained=r['waveform_old_direction_weakening_negative_rows'],all_CSV_under_1MB=all(p.stat().st_size<1000000 for p in O.glob('*.csv')),all_source_SHA_unchanged=True,no_new_ODE_fit_or_parameter_scan_Git=True,normalized_waveform_not_pure_phase_or_causal_fraction=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rule['inputs'],complete_arrays_local_only=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
