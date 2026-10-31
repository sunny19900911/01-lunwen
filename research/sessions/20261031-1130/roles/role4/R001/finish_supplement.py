from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[5];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def csvout(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
r=json.loads((O/'results.json').read_text(encoding='utf-8'));basis=read(O/'modal-basis-identity-numeric-comparison-18.csv');basepath=R/'research/sessions/20261021-2157/roles/role4/R004/base-reactions-all300.csv';base=read(basepath);assert len(base)==300
rows=[];gamma=[]
for c in r['selected_projection_checks']:
 m=c['Mode'];ax=c['Axis'];S=c['S_old18_mass_newCM_kg_m'];mr=c['ModalMass_times1000_kg_m2'];mu=c['effective_mass_conditional_ratio_times_oldtotal_kg'];G=S/mr;fr=next(d for d in basis if int(d['Mode'])==m and d['dataset']=='actual_controlled');lam=float(fr['omega_rad_s'])**2;b=next(d for d in base if int(d['Mode'])==m);native=float(b['F'+ax+'_kN']);pred=-lam*S/1000
 rows.append(dict(Mode=m,Axis=ax,omega_actual_rad_s=float(fr['omega_rad_s']),S_oldmass_actualCM_kg_m=S,native_modal_base_reaction_kN=native,reaction_from_negative_omega2_S_kN=pred,difference_native_minus_inertia_kN=native-pred,relative_difference_over_abs_native=abs(native-pred)/max(abs(native),1e-300),base_reaction_SourceRow=b['SourceRow'],normalization='native CM and native modal base reaction from same 881KB export',classification='conditional mass projection versus direct modal base reaction; not fitted sign or scale'))
 gamma.append(dict(Mode=m,Axis=ax,native_PF_raw=c['actual_native_PF'],native_PF_unit='kN-m; not relabeled Gamma',native_ModalMass=c['actual_native_ModalMass'],native_ModalMass_unit='kN-m-s2',mref_kg_m2=mr,S_conditional_kg_m=S,Gamma_conditional_per_m=G,mu_conditional_ratio_times_oldtotal_kg=mu,S_minus_Gamma_mref_kg_m=S-G*mr,Gamma_squared_mref_minus_mu_kg=G*G*mr-mu,identity_relative_error=abs(G*G*mr/mu-1),PF_and_Mass_source_row=c['actual_PF_SourceRow'],scope='Gamma derived from conditional mass projection, not independent native Gamma identification'))
csvout('native-modal-base-reaction-comparison-selected-6.csv',rows);csvout('conditional-Gamma-mass-identities-selected-6.csv',gamma)
force=json.loads((O/'modal-force-existing-manifest-evidence.json').read_text(encoding='utf-8'))
note=['# R001补充：实际q、Γ及已有模态力线索','',
'已读plan-theory-addendum-v002.md。L_sr=r_sᵀMφ_r，Eigen弹性力为ω²Lq；B=ΓL只是单位基底输入归一的系数。实际非经典/FNA耦合、其他广义力或非零初始条件下，Γ=0仍可q≠0，不能据B=0删除实际模态内力。本次未恢复真实FNA q。','',
'实际参与表UX/UY列标kN-m，ModalMass标kN-m-s²；CM平动原生mm已固定转m。因UX/UY字段量纲并非1/m，不未经软件字段定义确认直接称Γ，不由数值吻合拟合任何倍率。补充6行保留原生PF原值/单位，同时按条件质量投影定义Γ_cond=S/m_ref，核S=Γ_cond m_ref及μ_cond=Γ_cond²m_ref；这不是独立原生Γ检验。全300阶X/Y已用实际参与比例/ModalMass核对的600项结果仍有效，旧总质量相同不构成分层质量同源认证。','',
'## 模态力已有小表与跳过行','',
'1. **直接存在**：881KB同次模态导出的Base Reactions已有300行小CSV，Modal/LinModRitz/Mode，源行4—303。无需重提原件，已选mode2/10/13的X/Y六行，与固定负号的−ω²Σoldmφ/1000比较，结果见下表。它是基底模式反力，不是Story5/12模式切口力，也未改名为Γ归一单位响应。','',
'|阶次|方向|同次导出模式反力 / kN|−ω²Σoldmφ / kN|差值 / kN|','|---|---|---:|---:|---:|']
for d in rows:note.append(f"|{d['Mode']}|{d['Axis']}|{d['native_modal_base_reaction_kN']:.9g}|{d['reaction_from_negative_omega2_S_kN']:.9g}|{d['difference_native_minus_inertia_kN']:.9g}|")
note+=['','2. 实际有控core-cache的Story Forces共有195552行，72组之和也是195552，Step Type全为Step By Step；Base Reactions为16296行、全Step By Step。元数据无Modal/Mode组，原目录没有Frame Forces表。此范围没有被Time筛选漏掉Mode行的计数证据，不能宣称原件存在模态层剪力。','3. 旧D +3提取脚本`extract_response_cache.py`第32—34行确实仅缓存Step By Step，Story Forces全462432行，其中缓存462408、跳过24；manifest将被跳过行Step Type记为None，**不是Mode**。CM全693648行中跳过36个None。baseline0的对应计数相同。尚无这些None行的Case/Step Number/源行明细，不能将它们称作模态力。','4. 如以后在既有原件中作最小定点核查，只需要Story Forces的Story、Output Case、Case Type、Step Type、Step Number、Location（A—F）及VX/VY（H—I），针对上述24个非Step By Step行；有可信索引后才取对应原行。当前未为定位而扫描大工作簿。模式切口力最少需同模型mode2/10/13×Story5/12×Bottom的Case/Mode/VX/VY/源行/单位；目前已有缓存未发现这些记录。','',
'原来的R001冻结件保持原字节；本补充及6行表由delivery-manifest-v002.json另行绑定。']
(O/'R001-addendum-actual-q-and-force-evidence.md').write_text('\n'.join(note)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T03:39:13+00:00')).total_seconds();assert elapsed<720
for d in r['source_bindings']:assert sha(Path(d['path']))==d['sha256']
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,actual_q_not_recovered=True,Gamma_zero_does_not_delete_coupled_modal_force=True,native_PF_not_assumed_Gamma=True,no_unit_gain_fit=True,conditional_Gamma_identity_rows=6,max_conditional_Gamma_identity_relative_error=max(x['identity_relative_error'] for x in gamma),direct_modal_base_reaction_existing_rows=300,selected_base_reaction_comparison_rows=6,actual_story_force_all_rows_equal_cached_rows=195552,actual_story_force_Mode_rows_in_existing_metadata=0,old_D_story_force_skipped_None_rows=24,old_D_story_force_skipped_Mode_rows=0,all_source_hashes_unchanged=True,no_large_response_or_new_Excel_read=True,no_Git=True)
(O/'verification-supplement-v002.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest-v002.json']
(O/'delivery-manifest-v002.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,additional_input=dict(path=str(basepath),sha256=sha(basepath))),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(verification=v,base_reaction_comparison=rows),ensure_ascii=False,indent=2))
