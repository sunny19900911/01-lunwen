from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,rows):
    p=H/n;assert not p.exists()
    with p.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(n,data):
    p=H/n;assert not p.exists();p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths={
 'three_model':R/'research/sessions/20261020-1844/roles/role4/R003-three-model-peaks-72.csv',
 'paired168':R/'research/sessions/20261102-1917/roles/role4/R001/paired-record-evidence-168.csv',
 'layer48':R/'research/sessions/20261019-2045/roles/data/R002-native-horizontal/layer-axis-peaks-48.csv',
 'coverage24':R/'research/sessions/20261019-2045/roles/data/R002-native-horizontal/pairing-checks-24.csv',
 'device384':R/'research/sessions/20261019-2045/roles/data/R002-native-horizontal/device-contributions-384.csv',
 'story8_48':R/'research/sessions/20261020-1844/roles/role4/R005-Story8-device-at-QT-peak-48.csv'
}
data={k:read(v) for k,v in paths.items()}
native=data['three_model'];assert len(native)==72
keys={(r['Case'],r['Story'],r['Axis']) for r in native};assert len(keys)==72
assert {r['Case'] for r in native}=={'RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y'}
baseline={(r['Case'],r['Story'],r['Axis']):r for r in data['paired168']}
rows=[]
for r in native:
    q=baseline[r['Case'],r['Story'],r['Axis']]
    assert r['Location']==q['Location']=='Bottom' and r['units']==q['force_unit']=='kN'
    for old,new in [('P0_kN','P_B_kN'),('P3_kN','P_M_kN'),('t_peak0_s','t_B_s'),('t_peak3_s','t_M_s')]:
        assert float(r[old])==float(q[new]),(r['Case'],r['Story'],old)
    assert r['physical_own_output_complete']=='True'
    pb,pm,pd=[float(r[k]) for k in ['P0_kN','P3_kN','Pphysical_kN']]
    rows.append({'Case':r['Case'],'Axis':r['Axis'],'Story':r['Story'],'Location':'Bottom','units':'kN',
      'P_B_kN':pb,'P_M_kN':pm,'P_D_kN':pd,'t_B_s':float(r['t_peak0_s']),'t_M_s':float(r['t_peak3_s']),
      't_D_s':float(r['t_peakphysical_s']),'r_M_percent':100*(1-pm/pb),
      'conditional_r_D_percent':100*(1-pd/pb),'P_D_over_P_M':pd/pm,
      'D_vs_M_difference_percent':100*(pd/pm-1),'source_row_D_peak':int(r['source_rowphysical']),
      'physical_input_complete_model_pair_verified_by_old_source':False,
      'scope':'Native model peaks; D/B reductions conditional pending cross-model input and structural pairing; D own maximum demand unconditional within available inputs'})
write('three-model-common-six-records-72.csv',rows)
controls=[]
for axis in ['X','Y']:
  for story in range(1,13):
    group=sorted([r for r in rows if r['Axis']==axis and r['Story']==f'Story{story}'],key=lambda x:x['Case'])
    assert len(group)==3
    low=min(group,key=lambda x:x['conditional_r_D_percent']);high=max(group,key=lambda x:x['P_D_kN'])
    lm=min(group,key=lambda x:x['r_M_percent']);hm=max(group,key=lambda x:x['P_M_kN'])
    controls.append({'Axis':axis,'Story':f'Story{story}','n_input_cases':3,
      'conditional_min_D_reduction_case':low['Case'],'conditional_min_D_reduction_percent':low['conditional_r_D_percent'],
      'P_B_at_conditional_min_D_reduction_kN':low['P_B_kN'],'P_D_at_conditional_min_D_reduction_kN':low['P_D_kN'],
      'actual_max_demand_case':high['Case'],'actual_max_demand_kN':high['P_D_kN'],
      'P_B_at_actual_max_demand_kN':high['P_B_kN'],'conditional_r_D_at_actual_max_demand_percent':high['conditional_r_D_percent'],
      'D_two_controls_differ':low['Case']!=high['Case'],
      'reference_min_reduction_case_common_six':lm['Case'],'reference_min_reduction_percent_common_six':lm['r_M_percent'],
      'reference_max_demand_case_common_six':hm['Case'],'reference_max_demand_kN_common_six':hm['P_M_kN'],
      'reference_two_controls_differ_common_six':lm['Case']!=hm['Case'],
      'max_demand_input_changed_between_M_D':hm['Case']!=high['Case'],
      'conditional_min_D_tied_count':sum(abs(r['conditional_r_D_percent']-low['conditional_r_D_percent'])<1e-12 for r in group),
      'actual_max_D_tied_count':sum(abs(r['P_D_kN']-high['P_D_kN'])<1e-12 for r in group)})
write('common-six-control-records-24.csv',controls)
cover={(r['Story'],r['Case']):r for r in data['coverage24']}
assert len(cover)==24
for r in cover.values():
    for k in ['8_geometry_matches','all_P_I_equals_P_J','all_time_axes_match_base_and_story_exactly','I_lower_J_upper','no_interpolation_or_zero_fill']:assert r[k]=='True'
timing=[]
for r in data['layer48']:
    if r['input_main_axis']!='True':continue
    c=cover[r['Story'],r['Case']];assert int(r['devices_total'])==8 and int(r['devices_nonzero_projection'])==4
    source=next(q for q in rows if q['Case']==r['Case'] and q['Story']==r['Story'] and q['Axis']==r['Axis'])
    assert abs(source['P_D_kN']-float(r['QT_peak_kN']))<1e-9
    ratio=100*abs(float(r['QD_at_QT_peak_kN']))/float(r['QD_peak_abs_kN'])
    devices=[q for q in data['device384'] if q['Story']==r['Story'] and q['Case']==r['Case'] and q['Axis']==r['Axis']]
    assert len(devices)==8 and len({q['Link'] for q in devices})==8
    total=math.fsum(float(q['horizontal_at_QT_peak_kN']) for q in devices)
    assert abs(total-float(r['QD_at_QT_peak_kN']))<1e-9
    timing.append({'Story':r['Story'],'Case':r['Case'],'Axis':r['Axis'],'devices_total':8,'nonzero_projected_devices':4,
       'n_points':int(r['n_points']),'t0_s':float(r['t0_s']),'t1_s':float(r['t1_s']),
       'QT_peak_kN':float(r['QT_peak_kN']),'t_QT_peak_s':float(r['QT_peak_t_s']),
       'QT_signed_at_peak_kN':float(r['QT_signed_at_peak_kN']),
       'QD_abs_peak_kN':float(r['QD_peak_abs_kN']),'t_QD_peak_s':float(r['QD_peak_t_s']),
       'QD_signed_at_QT_peak_kN':float(r['QD_at_QT_peak_kN']),
       'abs_QD_at_QT_peak_over_QD_abs_peak_percent':ratio,
       't_QD_minus_t_QT_s':float(r['QD_peak_t_s'])-float(r['QT_peak_t_s']),
       'sum8_device_QD_at_QT_peak_check_residual_kN':total-float(r['QD_at_QT_peak_kN']),
       'QT_source_row':int(r['QT_source_row_at_QT_peak']),
       'scope':'QD=sum nP J-end internal resisting term; opposite external force; no physical QS subtraction'})
assert len(timing)==24
write('native-device-layer-timing-24.csv',timing)
write('Story8-native-device-timing-6.csv',[r for r in timing if r['Story']=='Story8'])
summary={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'scope':'three native model outputs; conditional cross-model reduction until pairing audit',
 'common_cases':sorted({r['Case']for r in rows}),'rows':len(rows),'groups':len(controls),
 'baseline_reference_72_exact_values_and_times_match_reviewed168':True,
 'actual_peaks_higher_than_reference':sum(r['P_D_kN']>r['P_M_kN'] for r in rows),
 'actual_peaks_lower_than_reference':sum(r['P_D_kN']<r['P_M_kN'] for r in rows),
 'actual_over_reference_ratio_min':min(r['P_D_over_P_M'] for r in rows),'actual_over_reference_ratio_max':max(r['P_D_over_P_M'] for r in rows),
 'conditional_actual_reduction_min_percent':min(r['conditional_r_D_percent']for r in rows),
 'conditional_actual_reduction_max_percent':max(r['conditional_r_D_percent']for r in rows),
 'conditional_actual_control_inputs_differ_groups':sum(r['D_two_controls_differ']for r in controls),
 'reference_control_inputs_differ_groups_common_six':sum(r['reference_two_controls_differ_common_six']for r in controls),
 'max_demand_input_changed_M_to_D_groups':sum(r['max_demand_input_changed_between_M_D']for r in controls),
 'conditional_actual_min_reduction_record':min(rows,key=lambda r:r['conditional_r_D_percent']),
 'actual_max_absolute_record':max(rows,key=lambda r:r['P_D_kN']),
 'Story8_timing':[r for r in timing if r['Story']=='Story8'],
 'no_raw_workbook_or_array_read':True,'inputs':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths.values()]}
js('response-summary.json',summary)
lines=['# 实体阻尼器模型六工况响应核查','','本次直接复用冻结原生Bottom峰值，未读取原Excel或完整数组、未求解或拟合。基准/参考72条与已有168表逐值/峰时完全一致。实体模型与两者的输入和完整主体身份沿旧源为待核，因此下文D/B百分比是条件比较，D自身的绝对峰与控制输入是现有输入范围内的原生模型结果。','',
f"共有72项中，实体峰高于均匀增阻尼参考的{summary['actual_peaks_higher_than_reference']}项、低于的{summary['actual_peaks_lower_than_reference']}项。实体/参考峰比范围{summary['actual_over_reference_ratio_min']:.6f}—{summary['actual_over_reference_ratio_max']:.6f}。若D/B同输入同主体条件成立，实体最小减幅与最大绝对需求控制输入不同的为{summary['conditional_actual_control_inputs_differ_groups']}/24组；同六工况均匀增阻尼参考是{summary['reference_control_inputs_differ_groups_common_six']}/24组，均与原14工况19/24统计分开。两种模型的最大绝对需求控制输入在{summary['max_demand_input_changed_M_to_D_groups']}/24组改变。",'',
 '## 代表层两类控制记录（D/B减幅暂为条件计算）','','|方向/楼层|最小条件减幅输入|条件减幅/%|对应D峰/kN|最大D需求输入|最大D峰/kN|该输入条件减幅/%|','|---|---|---:|---:|---|---:|---:|']
for r in controls:
 if r['Story'] in ['Story1','Story5','Story7','Story8','Story12']:
  lines.append(f"|{r['Axis']}/{r['Story']}|{r['conditional_min_D_reduction_case']}|{r['conditional_min_D_reduction_percent']:.4f}|{r['P_D_at_conditional_min_D_reduction_kN']:.4f}|{r['actual_max_demand_case']}|{r['actual_max_demand_kN']:.4f}|{r['conditional_r_D_at_actual_max_demand_percent']:.4f}|")
lines+=['','## 实际出力与布置相联','','原生P与真实I/J几何已按Story8—11核有24个层—工况，每层8只全齐，4只在该主方向投影非零，时间轴逐点相同，I/J重复P只计一次。用8只装置同刻水平分力之和，24项与冻结层合力的最大残差低于1e-9kN。下表QD=ΣnP为上端J结构内力抵抗项，外力符号相反；不从QT物理扣除生成主体QS。','',
 '|Story8工况|QT绝对峰/kN|tQT/s|QD绝对峰/kN|tQD/s|QT峰时QD/kN|同刻绝对值/自身峰/%|','|---|---:|---:|---:|---:|---:|---:|']
for r in timing:
 if r['Story']=='Story8':lines.append(f"|{r['Case']}|{r['QT_peak_kN']:.4f}|{r['t_QT_peak_s']:.2f}|{r['QD_abs_peak_kN']:.4f}|{r['t_QD_peak_s']:.2f}|{r['QD_signed_at_QT_peak_kN']:.4f}|{r['abs_QD_at_QT_peak_over_QD_abs_peak_percent']:.4f}|")
lines+=['','这里的同刻比例是装置在控制时刻相对于自身峰的出力大小，不是减震贡献率、能量效率或安全度。SHW3X不在实体模型六工况中，不借用其原主例结论。模型输入配对由另一角色独立核，本角色不将待核身份自行升级。']
(H/'response-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:summary[k]for k in ['rows','groups','actual_peaks_higher_than_reference','actual_peaks_lower_than_reference','conditional_actual_control_inputs_differ_groups','reference_control_inputs_differ_groups_common_six','max_demand_input_changed_M_to_D_groups','conditional_actual_reduction_min_percent','conditional_actual_reduction_max_percent']},ensure_ascii=False))
