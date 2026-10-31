from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
O=Path(__file__).resolve().parent;R=O.parents[5];P=R/'research/sessions';W=R.parent/'W5-重燃双塔连体';D=W/'02-数据/增阻尼多目标研究-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
res=json.loads((O/'results.json').read_text(encoding='utf-8'));meta=json.loads((O/'direct-small-table-inspection.json').read_text(encoding='utf-8'))
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def csvout(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cov=[]
for dataset,d in meta.items():
 for table in ['Modal Periods And Frequencies','Modal Participating Mass Ratios','Modal Participation Factors','Centers Of Mass And Rigidity']:
  t=d['tables'].get(table);cov.append(dict(dataset=dataset,path=d['path'],table=table,present=t is not None,data_rows=t['rows'] if t else 0,header_row=2 if t else '',unit_row=3 if t else '',data_source_rows='4..'+str(t['rows']+3) if t else '',fields=';'.join(str(x) for x in t['header'][1]) if t else '',units=json.dumps(dict(zip(t['header'][1],t['units'][1])),ensure_ascii=False) if t else '',model_identity='controlled export same Modal as CM by human confirmation' if dataset=='actual_controlled' else 'old D model; not established same as actual controlled'))
csvout('table-field-coverage-12.csv',cov)
core=W/'research/maxwell-20261017/experiments/R001/core-cache/manifest.json';cmcache=Path(res['source_bindings'][1]['path']);cmeta=json.loads(core.read_text(encoding='utf-8'))
coreinfo=dict(path=str(core),sha256=sha(core),declared_original_path=cmeta['source'],declared_original_sha256=cmeta['sha256'],tables=list(cmeta['tables']),mass_or_modal_summary_table_present=any('Mass' in k or 'Modal Period' in k for k in cmeta['tables']),time_arrays_read=False)
js('core-cache-metadata-only.json',coreinfo)
matrix=[
 dict(dataset='actual CM modal shapes',path=str(cmcache),original='E:/!!!!!!!!TO HOME/20261021/模态的位移角.xlsx',sheet='Diaphragm CM Displacements',rows=5400,source_rows='4..5403',units='UX/UY mm native, m converted; RZ rad',case='Modal / LinModRitz / Mode1..300',identity='human confirmed actual device model; same unchanged Modal as controlled periods',can_join_actual_CM=True),
 dict(dataset='actual period and participation',path=meta['actual_controlled']['path'],original=cmeta['source'],sheet='Modal Periods And Frequencies; Modal Participating Mass Ratios; Modal Participation Factors',rows=300,source_rows='4..303 in each sheet',units='Period sec; omega rad/sec; mass ratios dimensionless; PF kN-m and ModalMass kN-m-s2 retained',case='Modal; Ritz type bound by same-case CM',identity='same unchanged model and Modal per human confirmation; tables share controlled export',can_join_actual_CM=True),
 dict(dataset='actual core response cache',path=str(core),original=cmeta['source'],sheet='7 cached response tables',rows='',source_rows='manifest group records',units='per manifest',case='actual controlled time-history cases',identity='same original SHA as controlled metadata; no mass distribution/modal shape table here',can_join_actual_CM=False),
 dict(dataset='old D mass distribution',path=str(O/'old-D-directional-mass-and-key-coverage-18.csv'),original=meta['old_plus3']['path'],sheet='Centers Of Mass And Rigidity',rows=18,source_rows='4..21',units='Mass X/Y kg; XCM/YCM m',case='mass table has no modal case',identity='old D +3; 18keys agree and 600 conditional projections agree; actual same-source distribution not explicitly certified',can_join_actual_CM=False),
 dict(dataset='old D baseline5 and +3 basis',path=meta['old_baseline5']['path']+';'+meta['old_plus3']['path'],original='old native0/+3 paired exports',sheet='Modal Periods And Frequencies; modal ratios and factors',rows=300,source_rows='4..303',units='period sec, omega rad/sec',case='Modal; mode type not established by these summary columns',identity='old pair common basis retained separately; actual mode300 differs greatly; no by-index transfer',can_join_actual_CM=False)]
csvout('model-identity-matrix-5.csv',matrix)
ex=read(O/'conditional-mass-projection-examples-18.csv');maxscale=maxbase=maxdirect=0.
for d in ex:
 s=float(d['S_all_oldmass_CM_kg_m']);ss=float(d['S_above_oldmass_CM_kg_m']);mu=float(d['conditional_effective_mass_ratio_times_oldtotal_kg']);b=float(d['B_candidate_kg'])
 for c in [-3.,.2]:maxscale=max(maxscale,abs((mu*(c*ss)/(c*s)-b)/max(abs(b),1)))
 if d['cut_story']=='Story1':maxbase=max(maxbase,abs(b-mu))
 ck=next(q for q in res['selected_projection_checks'] if q['Mode']==int(d['Mode']) and q['Axis']==d['Axis']);bdirect=s*ss/ck['ModalMass_times1000_kg_m2'];maxdirect=max(maxdirect,abs(bdirect-b)/max(abs(b),1))
assert maxscale<1e-12 and maxbase<1e-8 and maxdirect<1e-11
lines=['# R001 真实模态质量投影的数据接入与身份核验','',
'**已复用完整5400行CM模态缓存，实际CM与有控300阶周期/参与表可按用户确认的同模型同Modal绑定；实际模型明确为LinModRitz。实际同源质量分布表仍未找到，故不将旧质量拼接结果称为真实有限元弹性楼层剪力。**','',
'## 已确认接口与源行','',
'- CM缓存：`research/sessions/20261022-1856/roles/role4/R001/local-cache/CM-signed-all300-5400.csv`，18个Story/Diaphragm键×300阶，无缺行重复；源为`E:/!!!!!!!!TO HOME/20261021/模态的位移角.xlsx`，881169B，SHA aa593ff6…8f8a。`Diaphragm CM Displacements`原行4—5403，UX/UY原生mm转m、RZ为rad；未重新提取该Excel。','- 实际有控周期、Modal Participating Mass Ratios、Modal Participation Factors：`W5-重燃双塔连体/research/maxwell-20261017/roles/experiments/metadata/controlled_small_tables.json`，三表各300行、原行4—303；源`E:/!!!!!!!!TO HOME/有控.xlsx`既有SHA 9d999dfa…2c23。同模型同Modal确认见`research/sessions/20261023-0726/user-same-modal-basis-confirmation.md`，此次未读取635MB原件。模式2/10/13在各表源行分别5/13/16。','- 同源core-cache只有7类响应表，无质量/周期/参与摘要表；上述摘要实际在metadata小表。当前metadata表名目录及既有原工作簿完整目录均无Centers Of Mass And Rigidity或质量分布表。旧D的baseline0/+3小表各有18行Centers Of Mass And Rigidity，原行4—21，方向质量kg。完整路径、字段和单位见matrix/coverage两CSV。','',
'## 新实数检查与条件示例','',
'旧18行X/Y质量均合计47,440,864.269713 kg，键覆盖全部18组CM。将其与实际300阶CM及同源有控ModalMass、质量参与比例配套，600个方向—阶次检查比较`(Σmφ)²/(1000×native ModalMass)`与`actual ratio×old total mass`，最大相对差为'+f"{res['max_conditional_effective_mass_relative_difference']:.3g}"+'。这把此前高阶统一广义质量假设推进为实际同Modal表的数值核验，但质量分布仍来自旧模型，不能循环地把该一致性当成独立同源证明。原生PF的UX/UY列保留其kN-m表头与原值，不直接称Γ或以1000倍当Σmφ；未核清PF定义前不据该字段反推实际总质量。','',
'条件示例使用`μ=actual UX mass ratio×old X total mass`、`B=μ S_above/S_all`，保留符号。Story底部包含本层及以上全部隔板；Story5为12组、Story12为1组。B单位kg，B/1000乘m/s²得到kN。','',
'|阶次|基底B / kg|Story5 B / kg|Story12 B / kg|','|---|---:|---:|---:|']
for mode in [2,10,13]:
 rr={d['cut_story']:d for d in ex if int(d['Mode'])==mode and d['Axis']=='X'};lines.append('|'+str(mode)+'|'+ '|'.join(f"{float(rr['Story'+str(c)]['B_candidate_kg']):.3f}" for c in [1,5,12])+'|')
lines+=['','这18行X/Y×3阶×3切口是**旧18质量条件下的惯性投影接口**，不是从总剪力拟合；基底B=μ、反号/尺度不变及与S_all S_above/m_ref的独立等式均核对。mode10/13的局部B负值完整保留，不把绝对值或独立峰相加冒充同时刻分担。','',
'## 模态基迁移与自由度条件','',
'实际第300阶周期0.0089312105s，旧D baseline0为0.0000134823960s；第10/13阶也已有非零差异，前三阶频率近似相同不足以按阶号迁移。实际CM明确LinModRitz；旧D周期/参与摘要没有Eigen/Ritz类型字段，现有CM响应缓存无Modal形状组，不能仅凭Eigenvalue列断言Eigen模式。旧0/+3已配对基单独保留，不改用实际CM高阶。','',
'均匀X输入的质量投影是`φᵀ M rX`。若每个隔板的平动质量位于该模型真实质心、凝聚质量平动/转动块解耦，`rX`仅X平动为1，故S_X只需Σm_X UX；Jzz虽影响广义质量，但不单独进入该输入投影，UZ也不进入。不得仅因缺转动惯量就判不可做。若参考点偏离质心或质量有X—θ/X—Z耦合、遗漏非隔板质量、隔板非刚性/分布惯性，则须把相应M rX分量计入；18键吻合并不证明这些条件已满足。','',
'Ritz投影特征方程不自动给出全有限元Kφ=ω²Mφ。因此即使质量身份进一步闭合，当前B仍先定义为质量投影/模态惯性系数；精确弹性切口剪力还需刚度恢复或已导出的模式内力/残差核验。','',
'## 最先可执行的新接口','',
'独审者可直接读取本目录54行模式2/10/13带符号CM、18行旧方向质量、18行条件B示例、600行一致性诊断和实际有控原表行号：先复算S与S_above、单位/符号/基底恒等、共同尺度不变，再决定旧质量是否可在该条件范围采用。无需总剪力拟合、新ODE、求解器或新表。下一主线差距是实际质量分布/约束覆盖的身份认证与Ritz弹性恢复条件，不是重复求周期。','',
'输入散列、精确表字段/源行、原件与缓存身份见`results.json`、`model-identity-matrix-5.csv`、`table-field-coverage-12.csv`；完整5400行原模态缓存仅本地复用，不复制或上传。']
(O/'README-data-interface.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T03:39:13+00:00')).total_seconds();assert elapsed<720
for d in res['source_bindings']:assert sha(Path(d['path']))==d['sha256']
v=dict(frozen_utc=now.isoformat(),started_utc='2026-10-31T03:39:13+00:00',elapsed_seconds=elapsed,full_CM_cache_reused=True,original_small_modal_SHA_checked=True,no_original_Excel_extraction=True,no_large_response_arrays_read=True,model_type_actual='LinModRitz',old_D_mode_type_from_summary='not resolved',actual_mass_distribution_same_source=False,conditional_projection_checks=600,max_conditional_effective_mass_relative_difference=res['max_conditional_effective_mass_relative_difference'],conditional_example_rows=18,selected_actual_CM_rows=54,common_negative_and_positive_scaling_max_relative_error=maxscale,base_B_minus_conditional_mu_max_abs_kg=maxbase,formula_vs_direct_Sproducts_over_native_modal_mass_max_relative_error=maxdirect,no_total_shear_fit=True,no_ODE_or_ETABS_YJK=True,no_Git=True,source_hashes_unchanged=True)
js('verification.json',v)
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json'];js('delivery-manifest.json',dict(frozen_utc=now.isoformat(),outputs=files,inputs=res['source_bindings'],complete_modal_array_upload_allowed=False))
print(json.dumps(v,ensure_ascii=False,indent=2))
