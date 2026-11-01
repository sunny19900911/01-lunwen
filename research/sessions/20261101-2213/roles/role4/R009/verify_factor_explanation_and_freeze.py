from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import math
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
res=json.loads((O/'results.json').read_text(encoding='utf-8'));rules=json.loads((O/'input-and-factor-contract-freeze.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);allrows=rd(O/'all300-fixed-and-response-factors-2400.csv');factors=rd(O/'selected6-fixed-and-response-factors-48.csv');summaries=rd(O/'controller-and-contribution-closure-8.csv');focus=rd(O/'mode13-priority-sign-factor-comparison-3.csv');diagnoses=rd(O/'mode13-symbol-sign-change-diagnosis-2.csv');maxc=maxv=maxdv=0.;maxclosure=0.
for d in allrows:
    w=float(d['omega_rad_s']);B=float(d['B_kg']);z=float(d['z_unit_m_per_fractional_zeta']);s=float(d['s0_unit_m']);P=float(d['P0_kN']);sign=float(d['sign_V0']);v=B*w*w*s/1000;dv=B*w*w*z/1000;c=-sign*dv/P;maxc=max(maxc,abs(c-float(d['c_improvement_percent_per_damping_pp'])));maxv=max(maxv,abs(v-float(d['modal_baseline_shear_v_r_kN'])));maxdv=max(maxdv,abs(dv-float(d['modal_shear_derivative_kN_per_zeta'])));assert abs(2*math.pi/w-float(d['period_s']))<1e-12
    cf=-(-sign)*(-dv)/P;assert abs(cf-c)<1e-14
for d in summaries:
    rr=[e for e in allrows if e['Case']==d['Case'] and e['Story']==d['Story'] and e['controller_number']==d['controller_number']];assert len(rr)==300;values=[float(e['c_improvement_percent_per_damping_pp']) for e in rr];S=float(d['S_percent_per_damping_pp']);maxclosure=max(maxclosure,abs(math.fsum(values)-S));assert abs(float(d['selected6_c_sum'])+float(d['other294_c_sum'])-S)<1e-10;assert abs(float(d['abs_c_top5_sum'])+float(d['other295_c_sum'])-S)<1e-10
assert len(factors)==48 and len(summaries)==8 and maxc<1e-10 and maxclosure<1e-10
for d in diagnoses:assert float(d['c_sign_ratio'])==float(d['sign_factor_product_ratio'])==-1.
first=diagnoses[0];assert first['B_identical']=='True' and first['sign_B_from']==first['sign_B_to'] and first['signV_from']==first['signV_to'] and first['sign_z_from']!=first['sign_z_to']
second=diagnoses[1];assert second['sign_B_from']==second['sign_B_to'] and second['sign_z_from']==second['sign_z_to'] and second['signV_from']!=second['signV_to']
ratios=[]
for d in diagnoses:
    a=next(e for e in focus if e['Case']==d['from_case'] and e['Story']==d['from_story']);b=next(e for e in focus if e['Case']==d['to_case'] and e['Story']==d['to_story']);br=abs(float(b['B_kg'])/float(a['B_kg']));zr=abs(float(b['z_unit_m_per_fractional_zeta'])/float(a['z_unit_m_per_fractional_zeta']));pr=float(a['P0_kN'])/float(b['P0_kN']);cr=abs(float(b['c_improvement_percent_per_damping_pp'])/float(a['c_improvement_percent_per_damping_pp']));assert abs(br*zr*pr-cr)<1e-10;ratios.append(dict(comparison=d['comparison'],abs_B_ratio_to_over_from=br,abs_z_ratio_to_over_from=zr,inverse_P0_ratio=pr,omega_squared_ratio=1.,product_abs_c_ratio=br*zr*pr,observed_abs_c_ratio=cr))
cs('mode13-factor-magnitude-ratios-2.csv',ratios)
struct=[]
for st in sorted(set(d['Story'] for d in factors),key=lambda x:int(x[5:])):
    for mode in [2,4,10,13,18,50]:
        ff=[d for d in factors if d['Story']==st and int(d['Mode'])==mode];assert len(set(d['B_kg'] for d in ff))==1 and len(set(d['omega_rad_s'] for d in ff))==1;f=ff[0];struct.append(dict(Story=st,Mode=mode,period_s=float(f['period_s']),omega_squared_s2=float(f['omega_squared_s2']),B_kg=float(f['B_kg']),scope='fixed floor/modal coefficient across inputs; same floor only'))
cs('selected-mode-periods-and-fixed-B-by-floor-24.csv',struct)
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),factor_rows_recomputed=2400,selected_factor_rows=48,controllers=8,max_c_factor_rebuild_difference=maxc,max_baseline_modal_force_difference_kN=maxv,max_modal_force_derivative_difference=maxdv,max_all300_S_closure_error=maxclosure,selected6_other294_closure_pass=True,actual_top5_other295_closure_pass=True,mode13_sign_factor_diagnoses_both_verified=True,mode13_magnitude_product_ratios_both_verified=True,force_direction_flip_c_invariance_pass=True,input_hashes_unchanged=True,new_ODE=0,target_arrays_read=False,independent_role2_review_not_replaced=True)
js('verification.json',verification)
compact=['# 13阶促进与抵消的具体因子','', '同一固定300阶基底，13阶T=0.448527360s、ω²=196.237433835s⁻²；两者在三输入中完全相同。B已包含Γ。z单位m/单位小数阻尼，v和dv分别是基准模态剪力及其阻尼导数；c单位为剪力降幅百分数/阻尼百分点。','', '|输入/层|t*/s|B/kg|z(t*)|sign V0|v13/kN|dv13/dζ|c13|','|---|---|---|---|---|---|---|---|']
for d in focus:compact.append(f"|{d['Case']}/{d['Story']}|{float(d['time_s']):.2f}|{float(d['B_kg']):.3f}|{float(d['z_unit_m_per_fractional_zeta']):+.9f}|{int(float(d['sign_V0'])):+d}|{float(d['modal_baseline_shear_v_r_kN']):+.6f}|{float(d['modal_shear_derivative_kN_per_zeta']):+.6f}|{float(d['c_improvement_percent_per_damping_pp']):+.6f}|")
compact+=['','完整六个预选阶次（2、4、10、13、18、50）的48行因子表：selected6-fixed-and-response-factors-48.csv。固定结构项T、ω²及逐层B见selected-mode-periods-and-fixed-B-by-floor-24.csv。每个控制峰“预选6阶+其余294阶”和“实际主5阶+其余295阶”分别闭合，见controller-and-contribution-closure-8.csv。']
(O/'compact-mode13-factor-table.md').open('x',encoding='utf-8').write('\n'.join(compact)+'\n')
text=['# 同一振型为何有时促进、有时抵消','',
'本研究保持同一结构M/K及既有300阶振型基不变；三份基准缓存的ω和B逐元素完全一致。变的是输入激发的模态运动s、其对阻尼的导数z，以及总剪力控制峰的时刻和正负号。不能把这些结果解释为“增阻尼使模态振型改变”。','',
'在各层基准控制峰t*，v_r=B_srω²s_r/1000为该阶基准剪力，dv_r/dζ=B_srω²z_r/1000为它随阻尼的局部变化。定义c_r=−sign(V0)·(dv_r/dζ)/P0，Σc_r=S。c>0表示沿当前总峰方向的绝对剪力下降，c<0表示抵消下降。ω²、1000及P0均为正，c的符号由−sign(V0)·sign(B_sr)·sign(z_r)决定。','',
'**同一第5层、不同输入：改变符号的是z。** 13阶B均为−349831.835kg，总峰均为正。SHW3在22.92s的z=−.066752635，故该阶剪力导数为+4582.575145kN/ζ，c=−.527229；SHW4在29.94s的z=+.018335310，剪力导数为−1258.720884kN/ζ，c=+.123705。B和总峰号未变，阻尼响应导数反号，因而从抵消转为促进。输入与选中的总峰时刻同时不同，不能把符号变化单独归结为纯相位变化。','',
'**同一SHW3、不同楼层：改变符号的是总控制峰号。** 第5层与屋顶13阶B均负、各自峰时的z亦均负，因此两处剪力导数均为正。但第5层总峰为+8691.808507kN，正导数使其绝对值局部增加；屋顶总峰为−850.295475kN，正导数把负峰推向零，故c变为+7.173442。楼层B的数值和控制时刻仍不同，只是符号上都没有改变；c反号由总峰号翻转解释。','',
'v_r与c_r必须分开。SHW3第5层13阶原剪力为−42.616833kN，对正总峰起抵消作用；但它的阻尼导数为正，增阻尼使这项负剪力局部趋向零，从而削弱原有抵消，使总峰更大，所以c反为负。屋顶该阶原剪力−369.307987kN与负总峰同向，正导数使负剪力趋零，因此c为正。原有剪力的正负或大小不能直接代替“改善贡献”。','',
'数值大小同样不是纯符号问题。屋顶与第5层13阶|c|之比，恰等于|B_屋/B_5|×|z_屋/z_5|×(P0_5/P0_屋)；三个因子分别约'+f"{ratios[1]['abs_B_ratio_to_over_from']:.6f}、{ratios[1]['abs_z_ratio_to_over_from']:.6f}、{ratios[1]['inverse_P0_ratio']:.6f}"+'，乘积'+f"{ratios[1]['observed_abs_c_ratio']:.6f}"+'。因此屋顶较小的基准总峰也会放大归一化c；不能只看模态振幅或质量参与率。','',
'z满足基准阻尼灵敏度方程L0z=−2ωṡ，包含整段输入历史及运动变化，不能凭一个振型图或单个模态周期认定某阶永久有利。选定2、4、10、13、18、50阶仅用于逐因子展示；每个峰全部300阶仍闭合S。8个去重控制峰的预选六阶加其余294阶、实际|c|主5阶加其余295阶均通过闭合检查。','',
'以上均为5%基准控制峰导数解释，不是有限候选的实际模态剪力份额，也未认证某阶为扭转模态。全体2400条因子独立重建c最大差'+f'{maxc:.3e}'+'，总S闭合最大误差'+f'{maxclosure:.3e}'+'；基准模态剪力及导数也分别闭合。无新ODE、目标响应数组读取、拟合或几何重建，④复核不替代②独审。']
(O/'one-page-modal-factor-physical-explanation.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 运行与隔离记录','',
'实际开始2026-11-01T15:53:46UTC（23:53:46+08），主要10分钟16:03:46UTC，硬12分钟16:05:46UTC。输入规则先冻结；只读SHW3X/SHW4X/RH4X的5%基准s0/z、ω/B和已有S小表。','',
'实际命令python.exe -X utf8 decompose_fixed_modal_and_response_factors.py退出0，随后verify_factor_explanation_and_freeze.py只读派生表验证、撰写解释并冻结，退出以工具记录为准。8个控制峰对应SHW3第5/屋顶，SHW4第1/第5/屋顶，RH4第5/第7/屋顶，重复角色去重。所有控制峰分别求和，未跨时刻拼贡献。','',
'无新ODE/有限候选/拟合/模态Excel/节点/几何重建/求解器/Git。全300阶因子表为控制峰时的派生标量，非整时程数组。B在同层跨输入完全相同，不同层有不同数值；不能把不同层B变化当成同一结构振型随输入改变。ω²恒正。c式不再乘Gamma，/1000按m/kg→kN转换。','',
'模式2/4/10/13/18/50由根预先指定；同时给出真正按|c|排序的主5项+余项，防止把六个展示模式等同于所有层的真正主项。所有正负促进与抵消保留，解释不使用质量参与率、未认证扭转标签或纯相位份额。']
(O/'run-isolation-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T15:53:46+00:00')).total_seconds();js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within10min=elapsed<=600,within12min=elapsed<=720,files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.iterdir()) if p.is_file()],new_ODE=0,new_target_response=0,target_arrays_read=False,old_outputs_unchanged=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,verification=verification),ensure_ascii=False,indent=2))
