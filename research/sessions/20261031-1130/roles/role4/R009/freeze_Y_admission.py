from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
import json,csv,hashlib
O=Path(__file__).resolve().parent;R=O.parents[5];D=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
rawpath=O/'loadcase-YX-raw-metadata-safe.json';raw=json.loads(rawpath.read_text(encoding='utf-8'));cfgpath=R/'research/sessions/20261025-1337/roles/role6/R001/input-config.json';cfg=json.loads(cfgpath.read_text(encoding='utf-8'));pairedpath=D/'native_paired_validation.json';paired=json.loads(pairedpath.read_text(encoding='utf-8'));paths={.05:D/'原生0数据缓存/manifest.json',.08:D/'response_cache_manifest.json'};man={z:json.loads(p.read_text(encoding='utf-8')) for z,p in paths.items()};data={.05:raw[0],.08:raw[1]};by={z:{d['Name']:d for d in rr['selected_rows']} for z,rr in data.items()}
bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in [cfgpath,pairedpath,*paths.values(),Path(raw[0]['path']),Path(raw[1]['path'])]]
npzpath=Path(cfg['derived_npz']);entries=set(ZipFile(npzpath).namelist());sources=[];settings=[];gridrows=[];grouprows=[]
for base in ['SHW3','SHW4','RH4']:
 x=base+'X';y=base+'Y';xcfg=cfg['cases'][x];assert xcfg['ag_key']+'.npy' in entries and xcfg['t_key']+'.npy' in entries
 for z in [.05,.08]:
  xx=by[z][x];yy=by[z][y];diff=[k for k in xx if k not in ['SourceRow','Name','Load Name'] and xx[k]!=yy[k]];assert not diff
  assert xx['Load Name']=='U1' and yy['Load Name']=='U2' and yy['Load Type']=='Accel' and yy['Angle']==0 and yy['Initial Condition']=='Unstressed' and yy['Modal Case']=='Modal'
  assert yy['Function']==xcfg['function'] and yy['Trans Accel SF']==xcfg['SF_mm_s2'] and yy['Time Factor']==xcfg['time_factor'] and yy['Arrival Time']==xcfg['arrival_time']
  settings.append(dict(state_zeta=z,X_case=x,Y_case=y,X_LoadCase_SourceRow=xx['SourceRow'],Y_LoadCase_SourceRow=yy['SourceRow'],Function=yy['Function'],X_load_direction=xx['Load Name'],Y_load_direction=yy['Load Name'],Angle_deg=yy['Angle'],TransAccelSF_native_mm_s2=yy['Trans Accel SF'],TimeFactor=yy['Time Factor'],ArrivalTime_s=yy['Arrival Time'],InitialCondition=yy['Initial Condition'],ModalCase=yy['Modal Case'],MassSource=yy['Mass Source'],NumberSteps=yy['Number Steps'],StepSize_s=yy['Step Size'],non_direction_setting_differences=json.dumps(diff),source_path=data[z]['path']))
  for tabname in ['Diaphragm CM Displacements','Story Forces']:
   tab=man[z]['tables'][tabname];cols=tab.get('columns',tab.get('value_columns'));units=dict(zip(tab['headers'],tab['units']));assert ('UX' in cols and 'UY' in cols and units['UX']==units['UY']=='mm') if tabname.startswith('Diaphragm') else ('VY' in cols and units['VY']=='kN')
   gg=tab['groups'];yd={};xd={}
   for gid,g in gg.items():
    kk=g['keys'];case=kk.get('Output Case');key=(kk['Story'],kk.get('Diaphragm',kk.get('Location')))
    if case==y:yd[key]=(gid,g)
    if case==x:xd[key]=(gid,g)
   assert set(yd)==set(xd) and len(yd)==(18 if tabname.startswith('Diaphragm') else 12)
   sigkeys=['n','t0','t1','n_unique','strictly_increasing','dt_min','dt_max'];diffkeys=[]
   for key,(gid,g) in yd.items():
    xg=xd[key][1];diffkeys.extend(k for k in sigkeys if g.get(k)!=xg.get(k));assert g['n']==xcfg['n'] and abs(g['t0']-xcfg['t0'])<1e-9 and abs(g['t1']-xcfg['t1'])<1e-9
    grouprows.append(dict(zeta=z,Case=y,table=tabname,Story=key[0],Diaphragm_or_Location=key[1],group_id=gid,n=g['n'],t0=g['t0'],t1=g['t1'],dt_min=g.get('dt_min'),dt_max=g.get('dt_max'),Xmatching_group_id=xd[key][0],grid_summary_equal_all_fields=not any(g.get(k)!=xg.get(k) for k in sigkeys),cache_path=str(paths[z].parent/tab['cache']),columns=';'.join(cols),units='UX/UY mm; RZ rad' if tabname.startswith('Diaphragm') else 'VY kN',manifest_path=str(paths[z])))
   assert not diffkeys
   gridrows.append(dict(zeta=z,Y_case=y,table=tabname,groups=len(yd),X_Y_position_keys_equal=True,X_Y_grid_metadata_equal=True,n_per_group=xcfg['n'],t0_s=xcfg['t0'],t1_s=xcfg['t1'],step_s=xcfg['dt'],unit='mm for UX/UY' if tabname.startswith('Diaphragm') else 'kN for VY',response_array_values_read=False))
 xy5=by[.05][y];xy8=by[.08][y];crossdiff=[k for k in xy5 if k!='SourceRow' and xy5[k]!=xy8[k]];assert not crossdiff
 paired_y=next(d for d in paired['matched_grids_and_inputs'] if d['case']==y);assert paired_y['same_input_all_samples'] and paired_y['group_counts']['CM']==18 and paired_y['group_counts']['Forces']==12
 sources.append(dict(Y_case=y,reuse_scalar_X_input_from=x,exact_same_Function_object=xy5['Function'],native5_X_Y_SourceRows=f"{by[.05][x]['SourceRow']}/{xy5['SourceRow']}",native8_X_Y_SourceRows=f"{by[.08][x]['SourceRow']}/{xy8['SourceRow']}",TransAccelSF_mm_s2=xy5['Trans Accel SF'],input_scale_factor_change=1.0,TimeFactor=xy5['Time Factor'],ArrivalTime_s=xy5['Arrival Time'],Angle_deg=xy5['Angle'],Y_direction='Accel U2 at Angle0; scalar input unchanged from U1',InitialCondition=xy5['Initial Condition'],reused_t_key=xcfg['t_key'],reused_ag_key=xcfg['ag_key'],cached_ag_unit='m/s2 already scaled; no extra SF or g',existing_X_PGA_m_s2=xcfg['PGA_m_s2'],n=xcfg['n'],t0=xcfg['t0'],t1=xcfg['t1'],function_SourceRows=';'.join(map(str,xcfg['function_source_rows'])),function_endpoint_policy=xcfg['function_endpoint_handling'],native5_native8_same_case_settings=True,prior5_8_input_all_samples_equal=paired_y['same_input_all_samples'],admission='metadata_input_admitted; native time vectors require exact check when later read',independent_new_earthquake_record=False))
cs('Y-input-admission-and-X-reuse-evidence-3.csv',sources);cs('native5-8-XY-loadcase-setting-comparisons-6.csv',settings);cs('Y-response-cache-grid-unit-summary-12.csv',gridrows);cs('Y-exact-response-group-metadata-180.csv',grouprows)
lines=['# R009：Y方向输入与原生缓存资料准入（仅元信息）','',
'**三组Y方向在元信息层面可以复用各自既有X向标量ag，不需要猜测或另乘倍率。证据是同一LoadCase表内引用同一个函数对象、完全相同SF/时间缩放/到达时间/初始状态，输入仅由Accel U1改为U2、Angle均0；不是由工况名相近推断。此次没有Y向积分、响应数组读取或预测。**','',
'## 精确源行与输入对应','',
'两个状态分别来自旧D `native0_small_tables.json`和`small_tables.json`的Load Cases - TH - Nonlin Modal，表头/单位行2/3。单位Trans Accel SF=mm/sec²、Time Factor=sec、Arrival Time=sec、Angle=deg。表中所有相关设置（除Name和Load Name方向字段）逐格比较一致；5%/8%同名Y工况除GUID/Notes外设置也逐格一致。','',
'|Y工况|X/Y源行（两状态相同）|共同函数|SF / mm·s⁻²|输入方向|有效n / 终时刻|','|---|---|---|---:|---|---|']
for d in sources:lines.append('|'+d['Y_case']+'|'+d['native5_X_Y_SourceRows']+'|'+d['exact_same_Function_object']+f"|{d['TransAccelSF_mm_s2']}|U2，Angle=0|{d['n']} / {d['t1']:.2f}s|")
lines+=['','全部工况Initial Condition=Unstressed、Mass Source=Previous (MsSrc1)、Modal Case=Modal、Motion Type=Transient、Step Size=.02s；对应X/Y的Number Steps及其余非方向设置相同。SHW3与SHW4的SF为0.35，RH4为3.5，**不得因既有缓存PGA同为0.35m/s²而把三个SF改成相同**。其函数数值本身归一不同，已有X输入配置已完成源函数×SF/1000的m/s²核验。','',
'可复用字段为既有X输入配置中的SHW3X_t/ag、SHW4X_t/ag、RH4X_t/ag；cached ag已经以m/s²缩放，不再乘SF或g，也不将非零ag[0]强置零。这里“复用X ag”只指相同标量加速度函数，现在施加于U2；不能把X方向的Γ、B或剪力响应直接改名为Y。后续若派工，方向投影应使用同实际模态的ΣmYφY和相应切口投影。','',
'函数源行沿用已核X配置：SHW3、SHW4、RH4的具体范围均写入3行准入表。SHW4函数结束58.98s、原生输出至59.00s的既有端点续值规则同样继承，不新增外推方法、不补零。LoadCase对象同函数且同参数，以及原5/8配对验证的same_input_all_samples=True，支持这一元信息准入；没有在本轮重新读取函数序列或输入数组。','',
'## 缓存覆盖与5%/8%配对','',
'两个manifest均存在SHW3Y、SHW4Y、RH4Y：每工况18个CM位置、12个Story Bottom切口，UX/UY为mm、VY为kN。X/Y的全部位置键及n、t0、t1、唯一时刻数、严格递增性和dt_min/max摘要逐组一致。180组精确key/group_id/路径已冻结；尚未读取时间向量，后续读取时仍须像X检验一样逐项核对时间，不以摘要相同代替运行时检查。','',
'既有native_paired_validation.json已经对每个Y工况核5%/8%输入全部采样相同及18CM/12Forces覆盖，质量表全单元相同，LoadCase参数除GUID/Notes一致；周期/参与小表保留既有浮点差。5%/8%的ζ数值沿用已批准研究口径与X配置，本次LoadCase摘要不另含模态阻尼数值字段，不能把本轮读表称为独立再认证ζ。actual300受控Ritz基与旧D两状态的完整M/K身份混杂保持不变。','',
'## 准入边界与停止位置','',
'本轮结论为**标量输入及原生缓存的元信息准入通过**，是否执行Y输出检验由根另行派工；没有先执行六套Y积分。若使用同一actualω、ζ、零初始和标量ag，已有单位参与s核从方程上可代数复用，仍须单独使用Y投影并检验原生Y输出，不把这句话当作本轮已运行。','',
'三组X/Y是同三个地震函数在不同方向的输入，不增加为六条独立地震事件。这里Y目标是旧D的5%/8%原生响应，不将实际装置缓存里的SHW7Y改名成SHW3Y，不恢复布局或扩展求解器。无原始Excel、NPZ数组值或大响应读取，无ODE、拟合、Git或新数据。']
(O/'README-Y-metadata-admission.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
assert paired['metadata']['load_case_settings_equal_excluding_GUID_notes'] is True
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:43:28+00:00')).total_seconds();assert elapsed<480
for d in bindings:assert sha(Path(d['path']))==d['sha256']
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,admitted_Y_cases=[d['Y_case'] for d in sources],loadcase_same_function_and_scaling=True,only_Name_LoadName_direction_differences=True,Unstressed_initial_conditions_explicit=True,Y5_Y8_same_settings=True,priorY5_Y8_all_input_samples_equal=True,Y_response_group_metadata_rows=180,Y_response_summary_rows=12,unit_headers_confirmed=True,cached_X_ag_keys_exist_ZIP_directory_only=True,response_and_input_arrays_values_read=False,exact_native_vectors_not_rechecked_here=True,no_Y_ODE_or_prediction=True,no_new_Excel_or_fitted_scaling_Git=True,source_SHA_unchanged=True,decision='metadata input admitted; await root dispatch, exact vector checks on later read')
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=bindings,existing_X_input_config_path=str(cfgpath),no_array_values_read=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(v,ensure_ascii=False,indent=2))
