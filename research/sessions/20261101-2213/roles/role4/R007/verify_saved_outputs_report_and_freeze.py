from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rules=json.loads((O/'input-method-freeze.json').read_text(encoding='utf-8'));freeze=json.loads((O/'prediction-S-envelope-freeze.json').read_text(encoding='utf-8'));res=json.loads((O/'results.json').read_text(encoding='utf-8'));idx=json.loads((O/'target-array-index.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);assert all(sha(Path(d['path']))==d['sha256'] for d in freeze['files']);assert sha(Path(freeze['local_array']['path']))==freeze['local_array']['sha256'];assert all(sha(Path(d['path']))==d['sha256'] for d in idx)
with np.load(freeze['local_array']['path'],allow_pickle=False) as a:
    t=a['t'].copy();ag=a['ag'].copy();om=a['omega'].copy();B=a['B'].copy();s0=a['s0'].copy();Z=a['Z'].copy();V0=a['V0'].copy();VZ=a['VZ'].copy();PV={(z,o):a[f'z{z:g}_order{o}_V'].copy() for z in [.06,.07] for o in [1,2]};EE={(z,o):a[f'z{z:g}_order{o}_E'].copy() for z in [.06,.07] for o in [1,2]}
sr=rd(O/'baseline-S-ranked-floors-12.csv');mm=rd(O/'all-mode-signed-S-sources-3600.csv');ref=rd(O/'exact-reference-floor-peaks-24.csv');comp=rd(O/'prediction-vs-reference-48.csv');interval=rd(O/'interval-coverage-and-decision-validation-48.csv');candidates=rd(O/'candidate-decision-validation-4.csv');ranks=rd(O/'posterior-S-vs-reference-ranks-24.csv');maxclosure=maxS=maxpeak=maxmetric=0.;strictmiss=0
P0=np.max(abs(V0),axis=0)
for j in range(12):
    story=f'Story{j+1}';r=next(d for d in sr if d['Story']==story);amp=abs(V0[:,j]);act=np.flatnonzero(amp==P0[j]);g=np.sign(V0[:,j])*VZ[:,j];p=float(np.max(g[act]));ctrl=act[g[act]==p];Sc=-p/P0[j];maxS=max(maxS,abs(Sc-float(r['S_percent_per_damping_pp'])));assert ';'.join(str(int(n)) for n in ctrl)==r['controller_indices']
    for ci,n in enumerate(ctrl):
        c=-np.sign(V0[n,j])*(B[j]*om**2/1000)*Z[n]/P0[j];mr=[d for d in mm if d['Story']==story and int(d['controller_number'])==ci+1];assert len(mr)==300;maxclosure=max(maxclosure,abs(c.sum()-Sc));assert max(abs(c[int(d['Mode'])-1]-float(d['c_improvement_percent_per_damping_pp'])) for d in mr)<1e-12
assert maxS<1e-12 and maxclosure<1e-11
for entry in idx:
    z=entry['target_zeta']
    with np.load(entry['path'],allow_pickle=False) as a:
        assert np.array_equal(t,a['t']) and np.array_equal(ag,a['ag']) and np.array_equal(om,a['omega']) and np.array_equal(B,a['B']);q=a['s'].copy();V=a['V'].copy()
    assert np.max(abs(V-(q*om**2)@B.T/1000))<1e-10
    for j in range(12):
        story=f'Story{j+1}';ip=int(np.argmax(abs(V[:,j])));Pk=float(abs(V[ip,j]));D=1-Pk/P0[j];rr=next(d for d in ref if float(d['target_zeta'])==z and d['Story']==story);maxpeak=max(maxpeak,abs(Pk-float(rr['reference_peak_kN'])));assert abs(D-float(rr['reference_D']))<1e-12 and float(rr['reference_signed_peak_kN'])==float(V[ip,j]);assert float(rr['reference_peak_time_s'])==float(t[ip])
        for o in [1,2]:
            ir=next(d for d in interval if float(d['target_zeta'])==z and int(d['Taylor_order'])==o and d['Story']==story);pr=next(d for d in comp if float(d['target_zeta'])==z and int(d['Taylor_order'])==o and d['Story']==story);ph=float(np.max(abs(PV[z,o][:,j])));lo=float(np.max(np.maximum(0,abs(PV[z,o][:,j])-EE[z,o][:,j])));up=float(np.max(abs(PV[z,o][:,j])+EE[z,o][:,j]));maxmetric=max(maxmetric,abs(ph/Pk-1-float(pr['peak_relative_error'])),abs(lo-float(ir['P_lower_kN'])),abs(up-float(ir['P_upper_kN'])));strictmiss+=int(np.count_nonzero(abs(PV[z,o][:,j]-V[:,j])>EE[z,o][:,j]));DL=1-up/P0[j];DU=1-lo/P0[j];decision='meets' if DL>=.1 else ('insufficient' if DU<.1 else 'uncertain');assert decision==ir['decision_status'];assert (ir['v001_recompute']=='True')==(decision=='uncertain' or DU-DL>.05)
assert maxpeak==0 and maxmetric<1e-10
for r in candidates:
    z=float(r['target_zeta']);o=int(r['Taylor_order']);ir=[d for d in interval if float(d['target_zeta'])==z and int(d['Taylor_order'])==o];action='reject' if any(d['decision_status']=='insufficient' for d in ir) else ('pass' if all(d['decision_status']=='meets' and d['width_status']=='acceptable' for d in ir) else 'recompute');assert action==r['v002_action']
inversionrows=[]
for z in [.06,.07]:
    for i,a in enumerate(sr):
        for b in sr[i+1:]:
            da=next(d for d in ranks if float(d['target_zeta'])==z and d['Story']==a['Story']);db=next(d for d in ranks if float(d['target_zeta'])==z and d['Story']==b['Story'])
            if (float(a['S_percent_per_damping_pp'])-float(b['S_percent_per_damping_pp']))*(float(da['reference_D'])-float(db['reference_D']))<0:inversionrows.append(dict(target_zeta=z,baseline_slower_floor=a['Story'],baseline_faster_floor=b['Story'],S_slower=float(a['S_percent_per_damping_pp']),S_faster=float(b['S_percent_per_damping_pp']),reference_D_of_baseline_slower=float(da['reference_D']),reference_D_of_baseline_faster=float(db['reference_D'])))
cs('posterior-rank-inversion-pairs-3.csv',inversionrows);miss=[d for d in comp if d['point_miss_insufficient']=='True'];cs('point-insufficient-miss-cases-2.csv',miss)
fft=rd(O/'positive-FFT-direct-checks-16.csv');assert len(fft)==16 and all(d['within_guard']=='True' for d in fft)
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),baseline_S_rows_verified=12,modal_source_rows_verified=3600,max_modal_closure_error=maxclosure,reference_peak_rows_verified=24,prediction_interval_rows_verified=48,candidate_actions_verified=4,max_peak_difference_kN=maxpeak,max_predicted_metric_difference=maxmetric,strict_uncovered_samples=strictmiss,rank_inversion_pairs_verified=len(inversionrows),FFT_direct_checks=16,source_and_frozen_prediction_hashes_unchanged=True,reference_array_hashes_unchanged=True,extra_target_state_solves=0,old8_response_read=False,original_producer_exit=1,original_failure_stage='only final console json.dumps of NumPy int64 after every numeric output and results.json had been saved',this_script_reads_saved_results_without_recomputing_targets=True,independent_role2_review_pending=True)
js('verification.json',verification)
table=['# SHW4X基准峰值敏感度工程主表','', 'S及c单位：剪力降幅百分数/阻尼百分点。只代表5%基准控制峰导数，全部300阶参与。','', '|排序|楼层|峰时/s|S|主5阶有符号改善项|其余295阶之和|','|---|---|---|---|---|---|']
for r in sr:table.append(f"|{r['slow_improvement_rank']}|{r['Story']}|{r['controller_times_s']}|{float(r['S_percent_per_damping_pp']):.6f}|{r['top5_signed_c']}|{float(r['remaining_signed_c_sum']):+.6f}|")
(O/'engineering-main-table-SHW4X12.md').open('x',encoding='utf-8').write('\n'.join(table)+'\n')
story5=next(d for d in sr if d['Story']=='Story5');story1=next(d for d in sr if d['Story']=='Story1');story6=next(d for d in sr if d['Story']=='Story6');story12=next(d for d in sr if d['Story']=='Story12');truthad=sum(float(d['reference_D'])<0 for d in ref);passes=sum(d['v002_action']=='pass' for d in candidates)
text=['# SHW4X另一输入：基准解释、冻结预测与两目标验证','',
'SHW4X不支持“第5层总是改善最慢”：基准S最小为Story1，第5层只排第4；6%完整参照最慢变为Story6。6%和7%分别出现2对、1对楼层排序倒置。预先冻结的一、二阶离散区间仍覆盖全部48组峰值及完整采样曲线，但7%一阶点预测出现两次改善不足漏判。','',
'## 输入和前后顺序','',
'只读取旧020/R004保存的actual300-SHW4X-z0.05-factorized-reference.npz，SHA256为61c7165f08156aaef3af39dab94832b89772c60517d5a4444d74add79cb936d8，与旧清单一致。全2951点、0—59s、名义dt=.02s；缓存ag已为m/s²且PGA=.35，不再乘SF或g。全部300阶ω/B与已核SHW3X完全相同，复用缓存零初值5%状态；不重新生成Ritz或读取旧8%。力按Bω²s/1000为kN，Γ不重复。','',
'基准灵敏度、S、主模态、6%/7%整时程预测、离散缺陷区间及v002动作于'+freeze['frozen_utc']+'先冻结；随后只生成两个新完整线性参照。SHW4历史响应此前见过，本轮是另一输入的预定前瞻计算顺序，不称未见地震盲测或新独立建筑。固定1%近峰诊断与前5个独立局部峰未按目标结果修改。','',
'## 第5层不再最慢，模态来源也改变','',
'|楼层|基准S|慢改善排名|主5项：阶号:c|','|---|---|---|---|']
for r in [story1,story6,story5,story12]:text.append(f"|{r['Story']}|{float(r['S_percent_per_damping_pp']):.6f}|{r['slow_improvement_rank']}|{r['top5_signed_c']}|")
text+=['','SHW4X第5层S=4.676272，2阶、10阶为+3.483561、+.596233，13阶亦为+.123705。SHW3X第5层13阶原为−.527229；同一固定结构和振型系下，输入及控制峰变化可改变有符号导数项的促进/抵消关系。这里的c仍只是基准峰导数分解，不是候选真实剪力分担。','',
'|目标ζ|基准最慢层|参照最慢层|第5层参照排名|倒置对数/66|Spearman|','|---|---|---|---|---|---|']
for d in res['rank_validation']:text.append(f"|{d['target_zeta']:.2f}|{d['baseline_slowest']}|{d['reference_slowest']}|{d['Story5_reference_rank']}|{d['strict_inversions']}|{d['Spearman_no_ties_rho']:.6f}|")
text+=['','基准Story1与Story6的S仅相差约.024，次序在6%时翻转；其余倒置逐对保存在posterior-rank-inversion-pairs-3.csv。S排序在相邻楼层导数接近时不能保证有限增量排序不变。两目标所有参照降幅均为正，真实不利分支样本数为0，漏判率分母N/A。','',
'## 冻结预测与区间结果','',
'|ζ|阶次|最大峰值相对误差/%|最大降幅误差/百分点|区间宽度中位数/百分点|原v001复算层数|v002动作|','|---|---|---|---|---|---|---|']
for d in res['summary']:text.append(f"|{d['target_zeta']:.2f}|{d['Taylor_order']}|{100*d['max_abs_peak_relative_error']:.3f}|{d['max_abs_D_error_pp']:.3f}|{d['median_D_width_pp']:.3f}|{d['v001_recompute_floors']}/12|{d['v002_action']}|")
text+=['','48/48峰值和48/48整条保存曲线严格覆盖；全部样本误差≤对应计算包络。目标仍为10%、宽度上限5个百分点；连续时刻峰及严格浮点误差未获证明，工程保护量沿用冻结值。候选层面v002两阶均拒绝6%，7%一阶要求复算、二阶拒绝；完整参照显示两个候选都未实现全12层10%目标，因此没有错误拒绝或错误放行。没有通过候选，条件误放行率N/A，零计数不等于有分母的零错误率。','',
'7%一阶点预测改善不足漏判如下；区间并未把这些层误放行：','', '|楼层|点预测降幅/%|完整参照降幅/%|','|---|---|---|']
for d in miss:text.append(f"|{d['Story']}|{100*float(d['predicted_D']):.6f}|{100*float(d['reference_D']):.6f}|")
text+=['','## 有限核查与代价','',
f"12层S、3600条有符号模态来源闭合，最大误差{maxclosure:.3e}；24组真值峰、48组误差与区间、4组候选动作及3对倒置由已保存数组/小表复核，未新增目标求解。16条固定模态正卷积与FFT对照均在预定保护量以内。缓存基准步进残差最大位移{freeze['baseline_q_step_residual_m']:.3e}m、速度{freeze['baseline_v_step_residual_m_s']:.3e}m/s。",'',
f"两阶基准灵敏度联合递推{res['baseline_sensitivity_seconds']:.6f}s；4组候选预测/核/缺陷/FFT/投影核心{res['prediction_bound_core_seconds']:.6f}s；2组完整参照状态及剪力寻峰核心{res['new_target_complete_core_seconds']:.6f}s。计时不包含全部归档、读取和验证开销，且并列评估两个阶次，不据此构造端到端加速比；包络本身的较高成本仍保留，未声称减少求解次数就能提速。",'',
'主生产脚本末尾仅向控制台打印摘要时，NumPy int64未转换导致退出1；此前所有CSV、完整数组、target-array-index.json与results.json均已保存。原失败脚本和预测冻结字节保留；后续校验脚本仅读取保存结果，实际成功，未重跑两套参照。该失败不隐去，也不将退出1写成成功运行。②后续独审仍待进行。']
(O/'one-page-SHW4X-prediction-and-rank-validation.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 运行与隔离记录','',
'实际开始2026-11-01T15:34:56UTC（23:34:56+08）；8分钟15:42:56UTC，主要12分钟15:46:56UTC，硬15分钟15:49:56UTC。预测/S/区间15:37:06.995117UTC冻结，约130.995s；随后两目标参照和results.json于15:37:08.108944UTC保存。','',
'实际主命令python.exe -X utf8 shw4_baseline_prediction_then_two_targets.py，退出1，错误仅末尾print(json.dumps(...Story5...))包含NumPy int64。所有数值和JSON结果此前已经成功写盘，未覆盖或重跑。随后python.exe -X utf8 verify_saved_outputs_report_and_freeze.py检查保存数组/表、源散列、预测冻结散列，退出状态由工具记录。','',
'只写④R007；无新结构/布局、CM修补、旧8%读取、Excel重新提取或ETABS/YJK调用。基准从缓存读取，解析一/二阶灵敏度按旧R001纯函数复用（AST只导入mul/coefficients，不运行其顶层）。新完整目标状态恰2套(.06/.07)，校验阶段0套。完整数组全部local-cache不入Git。','',
'S单位为降幅百分数/阻尼百分点，不再×100；有符号促进/抵消与候选真实模态分担区分；精确活动峰采用计算等号，1%近峰只是诊断。所有楼层和全部300阶保留，排序翻转/漏判/宽区间均保留。']
(O/'run-isolation-and-failure-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T15:34:56+00:00')).total_seconds();js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within12min=elapsed<=720,within15min=elapsed<=900,files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.iterdir()) if p.is_file()],local_only_arrays=[freeze['local_array']]+idx,new_target_reference_solves=2,verification_extra_target_solves=0,producer_exit=1,producer_exit_reason='final console print only, data/results previously saved',old8_response_read=False,old_outputs_unchanged=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,verification=verification),ensure_ascii=False,indent=2))
