from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R004';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
r=json.loads((O/'results.json').read_text(encoding='utf-8'));rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));pairs=read(O/'all12-threewaves-UPC-paired-36.csv');anc=read(O/'all12-four-anchors-both-zeta-signed-reference-288.csv');assert len(pairs)==36 and len(anc)==288
modecsv={(case,z):read(O/f'mode-envelopes-{case}-z{z:g}-3600.csv') for case in ['SHW3X','SHW4X','RH4X'] for z in [.05,.08]}
idx={(c,z,d['Story'],int(d['Mode'])):d for (c,z),rr in modecsv.items() for d in rr};assert len(idx)==21600
maxU=maxweight=maxratio=maxanchor=maxnative=maxenv=0.;modecount=anchorcount=0
for d in pairs:
 case=d['Case'];story=d['Story'];r5=[idx[case,.05,story,i] for i in range(1,301)];top=sorted(range(1,301),key=lambda i:(-float(idx[case,.05,story,i]['reference_mode_abs_peak_kN']),i))[:5];assert d['top5_modes_fixed5']==';'.join(map(str,top))
 for z in [.05,.08]:
  rr=[idx[case,z,story,i] for i in range(1,301)];U=math.fsum(float(q['reference_mode_abs_peak_kN']) for q in rr);suffix='5' if z==.05 else '8';maxU=max(maxU,abs(U-float(d['U'+suffix+'_sum_single_mode_peaks_kN'])));maxweight=max(maxweight,abs(math.fsum(float(q['weight_this_zeta']) for q in rr)-1));assert all(int(idx[case,z,story,i]['fixed_5pct_rank'])==int(idx[case,.05,story,i]['fixed_5pct_rank']) for i in range(1,301))
  cc=float(d['P'+suffix+'_reference_peak_kN'])/U;maxratio=max(maxratio,abs(cc-float(d['C'+suffix+'_PoverU'])))
 assert abs(float(d['P8_over_P5'])-float(d['U8_over_U5'])*float(d['C8_over_C5']))<1e-12
for source in rules['inputs']:
 p=Path(source['path']);assert sha(p)==source['sha256']
 if p.suffix!='.npz':continue
 case=p.name.split('-')[1];z=float(p.name.split('-z')[1].split('-')[0])
 with np.load(p,allow_pickle=False) as a:
  t=a['t'];s=a['s_unitGamma'];w=a['omega'];B=a['B_direct'];smax=np.max(abs(s),axis=0)
  for st in range(1,13):
   story='Story'+str(st);expected=abs(B[st-1])*w*w*smax/1000
   for ir in range(300):
    saved=float(idx[case,z,story,ir+1]['reference_mode_abs_peak_kN']);maxenv=max(maxenv,abs(float(expected[ir])-saved)/max(abs(saved),1e-300));modecount+=1
  for d in anc:
   if d['Case']!=case or float(d['zeta'])!=z:continue
   story=d['Story'];st=int(story[5:])-1;ii=np.flatnonzero(np.isclose(t,float(d['time_s']),rtol=0,atol=1e-9));assert len(ii)==1;it=int(ii[0]);vv=B[st]*w*w*s[it]/1000;top=[int(d[f'fixed5_rank{k}_Mode'])-1 for k in range(1,6)];rest=[i for i in range(300) if i not in top]
   maxanchor=max(maxanchor,abs(float(math.fsum(vv))-float(d['reference_sum_signed_kN'])),abs(float(math.fsum(vv[rest]))-float(d['remaining295_signed_sum_kN'])))
   for k,ir in enumerate(top,1):maxanchor=max(maxanchor,abs(float(vv[ir])-float(d[f'fixed5_rank{k}_signed_ref_kN'])))
   for name,start,end in [('mode1to3',0,3),('mode4to9',3,9),('mode10to13',9,13),('mode14to300',13,300)]:maxanchor=max(maxanchor,abs(float(math.fsum(vv[start:end]))-float(d[name+'_signed_ref_sum_kN'])))
   maxnative=max(maxnative,abs(float(a['shear_native_'+story+'_kN'][it])-float(d['native_signed_value_kN'])));anchorcount+=1
assert modecount==21600 and anchorcount==288 and maxenv<1e-12 and maxanchor<1e-8 and maxU<1e-8
priority=[d for d in pairs if d['Story'] in ['Story5','Story12']];worst=max(pairs,key=lambda d:abs(float(d['reference_minus_native_decrease_percentage_points'])));c_up=sum(float(d['C8_over_C5'])>1 for d in pairs)
lines=['# R005：物理来源弹性惯性参照的幅值包络与同刻叠加','',
'**36对楼层—记录的U/P/C均已完成，P8/P5=(U8/U5)(C8/C5)的最大闭合误差2.22×10⁻¹⁶。单阶项来自R004固定质量、实际300阶CM形状/频率与单位核，没有任何输出拟合；仍是弹性惯性投影线性参照，不是原生FNA的唯一逐阶分解。**','',
'## 量的定义与冻结的选择','',
'每阶参照项为`v_srζ(t)=B_sr ω_r² s_rζ(t)/1000`（kN），`a_rζ=max_t|v_srζ(t)|`。定义独立单阶峰值之和`Uζ=Σa_rζ`、同刻合成峰`Pζ=max_t|Σv_srζ(t)|`、峰叠加系数`Cζ=Pζ/Uζ`。因此0<C≤1且P=UC；U是包络上界，不是实际合力，C综合了波形、符号、叠加及控制峰时刻选择，不能单独解释为纯相位量或因果份额。','',
'所有300阶独立峰与权重均保留。top5只用5%的`a_r5/U5`降序确定，平局按模式号升序，随后两状态及全部时刻固定这五阶；该权重是单阶包络权重，不称同刻力贡献率。各case/ζ分别3600行CSV，文件约0.33MB。辅助阶次组在计算前固定为1—3、4—9、10—13、14—300，不根据结果更改。','',
'每对在5%参照控制峰、8%参照控制峰、5%软件绝对峰、8%软件绝对峰四个时刻，分别取两ζ的全部300项。即便时刻重复也保留不同标签，共288行；每行列出固定top5的逐项有符号值、其余295项**同刻有符号合成**以及四个固定组的同刻合成。两种划分分别闭合，不把单阶独立峰相加当作控制时刻合力，也不把top5之外的项补零。','',
'## Story5与Story12的六对重点结果','',
'|记录|楼层|U8/U5|C8/C5|P8/P5|参照峰降幅 / %|软件峰降幅 / %|','|---|---|---:|---:|---:|---:|---:|']
for d in priority:lines.append('|'+d['Case']+'|'+d['Story']+'|'+ '|'.join(f"{float(d[k]):.6f}" for k in ['U8_over_U5','C8_over_C5','P8_over_P5','reference_peak_decrease_percent','native_peak_decrease_percent'])+'|')
lines+=['','SHW3X的Story5有`0.903493×1.030990=0.931492`：单阶包络之和下降，但C增加，最终参照峰降幅仅6.8508%；Story12则为`0.846186×0.847092=0.716798`，U与C同时下降，合成峰降幅28.3202%。这说明同样增ζ在不同楼层可因物理系数带来的模态组合不同，产生不同的合成峰变化；它是乘法记账，不是把幅值与“相位”划成可相加的因果百分比。','',
'在5%单阶包络权重排序中，Story5的五阶为SHW3X的2/10/3/13/1、SHW4X和RH4X的2/10/3/1/13；Story12分别为13/10/4/2/18、10/13/2/4/18、10/13/4/2/18。排序只用于选择展示项，不能替代实际同刻符号和剩余295项核算。','',
'SHW4X、Story12的四个同刻总量示例（参照正向）：','',
'|时刻 / s|ζ|固定top5合成 / kN|其余295项合成 / kN|全部300项 / kN|','|---|---:|---:|---:|---:|']
for d in anc:
 if d['Case']=='SHW4X' and d['Story']=='Story12' and d['anchor'].startswith('predicted'):
  lines.append(f"|{float(d['time_s']):.2f}|{float(d['zeta']):.0%}|{float(d['top5_signed_sum_kN']):.6f}|{float(d['remaining295_signed_sum_kN']):.6f}|{float(d['reference_sum_signed_kN']):.6f}|")
lines+=['','完整48行重点层同刻表同时保留每个主项和四个组，不能只拿上表top5合成替代全部300项。','',
'## 全楼对照与范围','',
f'36对中C8/C5>1有{c_up}对，其余{36-c_up}对≤1，均保留。参照与软件绝对峰降幅的最大差为'+worst['Case']+'/'+worst['Story']+f"的{abs(float(worst['reference_minus_native_decrease_percentage_points'])):.6f}个百分点。"+'该小误差支持在既定三波及时间窗中采用固定物理来源参照解释楼层差异，不能升级为完整FE刚度切口恢复或实际FNA坐标已取得。','',
'所有有符号项都按R004预测正向r_cutᵀKu；软件Bottom VX的η仍未由独立定义确认，因此软件仅比较绝对峰及降幅。共同全局反号不改变U/P/C。软件峰时刻只是取参照项的查询时刻，不能把未知符号映射的参照项称为软件原生同刻分力。实际Ritz与旧D两状态的模型身份混杂及弹性恢复条件沿用R004。','',
'## 复核与文件','',
'独立以`|B|ω²max|s|/1000`核21600个单阶峰，用因子化数组的查询行核288行主项、剩余项与分组；以CSV单阶峰重新求和U并验证权重和为1、5%排名在两ζ固定。全部来源SHA不变，没有新ODE、拟合、新数组输出或CM指标复算。','',
'主表：`all12-threewaves-UPC-paired-36.csv`；重点：`Story5-Story12-UPC-priority-6.csv`和`Story5-Story12-signed-reference-priority-48.csv`；全楼同刻：`all12-four-anchors-both-zeta-signed-reference-288.csv`；六份`mode-envelopes-*-3600.csv`保留全部单阶独立峰/权重。每个小CSV均小于1MB，完整数组继续只留R004/local-cache。']
(O/'README-UPC-and-same-time-modal-reference.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:17:58+00:00')).total_seconds();assert elapsed<720
v=dict(frozen_utc=now.isoformat(),started_utc='2026-10-31T04:17:58+00:00',elapsed_seconds=elapsed,pairs=36,single_mode_peak_checks=modecount,same_time_anchor_checks=anchorcount,per_case_zeta_file_rows=3600,max_sum_U_recheck_abs_kN=maxU,max_envelope_weight_sum_error=maxweight,max_C_recheck_error=maxratio,max_factorized_single_peak_relative_error=maxenv,max_same_time_term_recheck_abs_kN=maxanchor,max_native_same_time_value_recheck_abs_kN=maxnative,ratio_identity_max_error=r['max_UPC_identity_error'],max_top5_plus_295_closure_kN=r['max_top5_plus_remaining_closure_kN'],max_fixed_groups_closure_kN=r['max_fixed_groups_closure_kN'],fixed5_rank_verified=True,all_CSV_under_1MB=all(p.stat().st_size<1000000 for p in O.glob('*.csv')),sources_unchanged=True,no_new_ODE_fit_CM_metric_or_Git=True,complete_arrays_remain_local_only=True,native_FNA_unique_decomposition_claimed=False)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rules['inputs'],complete_array_upload_allowed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
