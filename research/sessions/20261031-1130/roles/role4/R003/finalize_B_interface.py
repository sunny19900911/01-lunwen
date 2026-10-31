from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
O=Path(__file__).resolve().parent;R=O.parents[5];W=R.parent/'W5-重燃双塔连体';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return list(csv.DictReader((O/n).open(encoding='utf-8-sig')))
r=json.loads((O/'results.json').read_text(encoding='utf-8'));rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'))
for d in rules['inputs']:assert sha(Path(d['path']))==d['sha256']
full=read('all12-300-XY-signed-B-inertia-not-elastic-7200.csv');sums=read('finite300-signed-sumB-versus-mass-above-24.csv');base=read('mode-direction-normalization-checks-600.csv');main=read('modes2-10-13-all12-XY-B-inertia-not-elastic-72.csv')
assert len(full)==7200 and len({(d['cut_story'],d['Axis'],int(d['Mode'])) for d in full})==7200
maxsum=0.;maxbase=0.
for row in sums:
 pp=[d for d in full if d['cut_story']==row['cut_story'] and d['Axis']==row['Axis']];assert len(pp)==300
 val=math.fsum(float(d['B_inertia_projection_kg_not_fullFE_elastic']) for d in pp);maxsum=max(maxsum,abs(val-float(row['sum_signed_300_B_inertia_projection_kg_not_fullFE_elastic'])))
for row in base:
 d=next(d for d in full if d['cut_story']=='Story1' and d['Axis']==row['Axis'] and d['Mode']==row['Mode']);maxbase=max(maxbase,abs(float(d['B_inertia_projection_kg_not_fullFE_elastic'])-float(row['m_eff_actual_ratio_times_identified_M_kg'])))
assert maxsum<1e-6 and maxbase<1e-6
assert all(float(d['Cauchy_B2_over_meff_Mabove'])<=1+1e-10 and float(d['Cauchy_Sabove2_over_Mabove_Gabove'])<=1+1e-10 for d in full)
corepath=W/'research/maxwell-20261017/experiments/R001/core-cache/manifest.json';metapath=W/'research/maxwell-20261017/roles/experiments/metadata/metadata_inventory.json';core=json.loads(corepath.read_text(encoding='utf-8'));md=json.loads(metapath.read_text(encoding='utf-8'));assert core['sha256']==md['sha256'];groups=core['tables']['Diaphragm CM Displacements']['groups']
cases=sorted({g['keys']['Output Case'] for g in groups.values()});cmcounts={c:sum(g['keys']['Output Case']==c for g in groups.values()) for c in cases};assert set(cmcounts.values())=={18}
identity=dict(checked_utc=datetime.now(timezone.utc).isoformat(),cache_manifest_path=str(corepath),cache_manifest_sha256=sha(corepath),controlled_metadata_inventory_path=str(metapath),metadata_inventory_sha256=sha(metapath),same_original_XLSX_SHA=core['sha256'],same_original_XLSX=core['source'],CM_time_cases=cases,CM_groups_per_case=cmcounts,total_CM_groups=len(groups),actual_modal_shape_binding='external 881KB CM modal export bound to same unchanged model and Modal by human confirmation 20261023-0726/user-same-modal-basis-confirmation.md',current_status='existing actual-controlled CM time cache identity supported by shared original and human Modal binding; time arrays not opened',old_D_baseline5_plus3='not transferred into actual basis; distinct high-mode periods already recorded',actual_q_recovered=False)
(O/'existing-CM-time-cache-identity-metadata-only.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# R003：全楼逐阶惯性投影与CM坐标可辨识性','',
'**已形成12层×300阶×XY共7200行带符号B，质量沿用R002冻结结果，没有重新识别质量。基底恒等和Cauchy检查通过；有限300阶的有符号ΣB与切口以上质量最大偏差0.0136626%。36×300质量加权CM平动观测矩阵rank36，仍有264维零空间，第2/10/13阶坐标均不可由瞬时平动观察量唯一恢复。**','',
'## B的物理对象与切口','',
'本表B为单位基底输入归一的**质量惯性投影系数，非全FE精确弹性剪力系数**。对每一方向，S_r=Σ全部18组mφ，S_sr=Σ切口以上mφ，m_eff,r=实际有控参与质量比例×R002已识别方向总质量，B_sr=m_eff,r S_sr/S_r，单位kg。这里实际Modal为LinModRitz，不能偷设全空间Kφ=ω²Mφ；实际弹性剪力仍需恢复算子及实际q。','',
'Storys底部包含Story≥s的全部隔板，不按单塔删减；Story1为18组，Story5为12组，Story12为1组。负B逐项保留。完整7200行的B字段名直接注明inertia_projection/not_fullFE_elastic；模式2/10/13的72行主表另存S、m_eff和覆盖质量。','',
'|阶次|方向|Story5 B / kg|Story12 B / kg|','|---|---|---:|---:|']
for mode in [2,10,13]:
 for ax in ['X','Y']:
  rr={d['cut_story']:d for d in main if int(d['Mode'])==mode and d['Axis']==ax};lines.append(f"|{mode}|{ax}|{float(rr['Story5']['B_inertia_projection_kg_not_fullFE_elastic']):.6f}|{float(rr['Story12']['B_inertia_projection_kg_not_fullFE_elastic']):.6f}|")
lines+=['','## 质量恒等与Cauchy检查','',
'基底B与m_eff的最大绝对差为'+f"{r['base_B_minus_meff_max_abs_kg']:.4g}"+' kg。检查局部Cauchy `S_sr²≤M_above Σabove(mφ²)`（7200项最大比例1.0000000000000004，属舍入）及模态质量界`B_sr²≤m_eff,r M_above`（最大比例'+f"{r['max_global_Cauchy_ratio']:.9f}"+'），全部在1e−10容差内。600项S²/m_r与m_eff相对差最大'+f"{r['max_mode_normalization_relative_error']:.4g}"+'，保留了R002留出模式的浮点散布，没有重新调质量。','',
'全300阶有符号求和ΣB与已识别切口以上质量逐层比较，最大绝对相对偏差为Story11/X的0.0136626%（少617.353 kg）；基底X/Y分别少0.0097026%、0.0121048%。24项完整保留，局部也有正偏差；未将有限Ritz基的求和强制设成完整质量恒等。Σ|B|另列，它不是有符号恒等，也不是实际地震贡献率。','',
'## 36×300观测矩阵与实际q','',
'定义`C=[diag(√mX)ΦX; diag(√mY)ΦY]`，每组18个CM平动，共36行、300列；列对应实际模态坐标q，未作列缩放。C最大/最小非零奇异值为'+f"{r['C_singular_max']:.9g}/{r['C_singular_min']:.9g}"+'；按机器精度阈值及相对1e−10阈值均rank36。满行秩表示36个观测方向独立，并不等于300个q可辨识。','',
'令P为C的行空间正交投影，若e_r不在行空间，则q_r不能由瞬时CM平动唯一决定。计算n=(I−P)e_r，有Cn≈0但n_r≠0，形成不改变这些观察量却改变该阶坐标的明确方向：','',
'|阶次|dist(e_r,row(C))|n_r|\|Cn\|/(\|C\|\|n\|)|','|---|---:|---:|---:|']
for d in r['selected_coordinate_checks']:lines.append(f"|{d['Mode']}|{d['distance_e_to_rowspace']:.10f}|{d['nullspace_vector_mode_component']:.10f}|{d['relative_observation_null_residual']:.4g}|")
lines+=['','三项均非零，故**仅靠这36个瞬时平动量、且不追加动力学/截断约束时，第2/10/13阶实际q均不唯一**。高投影杠杆率也不能改称唯一恢复。本轮没有拟合或恢复q，也没有用时程平滑来掩盖零空间。结论不排除未来在已知完整动力学和初始条件下研究时间域可观测性。','',
'## 已有CM时间缓存的身份','',
'实际有控core-cache中的CM时间量有6工况（RH4X/Y、SHW4X/Y、SHW7X/Y），每工况18组；其原件SHA与实际有控参与/周期metadata来源相同，且用户已经确认881KB CM模态与有控周期同一未改模型同一Modal，因此身份链有支持。此次只核manifest与既有人为确认，未打开时间数组。旧D的baseline5/+3时间缓存不据此迁入实际模态基。即便时间缓存身份成立，以上瞬时坐标零空间仍在。','',
'输出：完整7200行B；72行重点模式；600行归一检查；24行ΣB质量对照；36个观测奇异值；300个坐标行空间距离；3项重点坐标核查。无新表/大原件读取、无质量重识别、无ODE、无q或剪力拟合、无求解器/Git操作。']
(O/'README-B-inertia-and-observability.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:01:49+00:00')).total_seconds();assert elapsed<720
for d in rules['inputs']:assert sha(Path(d['path']))==d['sha256']
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,B_rows=7200,mode_focus_rows=72,signed_sum_mass_comparisons=24,base_B_meff_recheck_max_abs_kg=maxbase,independent_math_fsum_vs_stored_sum_max_abs_kg=maxsum,all_Cauchy_checks_pass_1e10=True,C_shape=[36,300],C_rank=36,C_nullspace_dimension=264,modes2_10_13_unique_from_instantaneous_CM=False,identity_time_cache_checked_metadata_only=True,no_actual_time_arrays_read=True,no_mass_reidentification_or_ODE_q_shear_fit=True,source_hashes_unchanged=True,no_Git=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rules['inputs'],additional_metadata=[dict(path=str(corepath),sha256=sha(corepath)),dict(path=str(metapath),sha256=sha(metapath))],complete_arrays_local_only=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
