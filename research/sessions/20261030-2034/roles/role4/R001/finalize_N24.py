from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;S=O.parents[2];ROOT=S/'root-R001-low-order';R=O.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def js(n,d):
 with (O/n).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));metrics=read(O/'prediction-errors-N24-24.csv');coefchange=read(O/'prefix-coefficient-change-vs-N12-8.csv');models=json.loads((O/'models-small-N24.json').read_text(encoding='utf-8'))
cfg=json.loads((R/'research/sessions/20261025-1337/roles/role6/R001/input-config.json').read_text(encoding='utf-8'));source_rows={}
for q in cfg['output_groups']:
 with np.load(q['npz'],allow_pickle=False) as z:source_rows[q['group_keys']['Output Case'],q['group_keys']['Story'],q['state']]=z[q['group_id']][:,-1]
for q in metrics:
 q['native_peak_SourceRow']=int(source_rows[q['Case'],q['Story'],'0' if float(q['zeta'])==.05 else '3'][round(float(q['native_peak_time_s'])/.02)])
with (O/'prediction-errors-N24-24.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
maxerr=0.
with np.load(O/'local-cache/N24-two-operator-traces.npz',allow_pickle=False) as z:
 for q in metrics:
  key=f"{q['operator']}__{q['Case']}__{q['Story']}__z{float(q['zeta']):g}";y=z[key+'__native'];pred=z[key+'__prediction'];terms=z[key+'__terms'];err=float(np.linalg.norm(pred-y)/np.linalg.norm(y));maxerr=max(maxerr,abs(err-float(q['NRMSE'])))
  assert abs(err-float(q['NRMSE']))<1e-12 and np.max(abs(terms.sum(1)-pred))<1e-6
  assert math.isclose(float(np.max(abs(pred)))/float(np.max(abs(y)))-1,float(q['peak_relative_error']),rel_tol=1e-10,abs_tol=1e-12)
assert len(metrics)==24 and len(models)==2
lines=['# 唯一N24扩阶：输出误差显著改善，系数分配仍需限定','',
'完全沿用主控冻结的原生SHW3X+SHW4X、5%两波训练，RH4X整波留出；8%三波使用同一训练系数、尺度和active列，没有再拟合。只新增N24、rcond=1e-10，elastic与balance预先并列保留。没有重复N6/N12拟合或扩至36/300。ag沿用loader的m/s²，不再乘倍率。','',
'下表NRMSE以相应原生完整曲线L2为分母，峰差为(预测绝对峰/原生绝对峰−1)，峰均从各自完整曲线取得。','',
'| 口径 | 层 | 5%留出RH4 NRMSE | 8%三波NRMSE范围 | 8%峰差范围 | rank |','|---|---|---|---|---|']
for op in ['elastic','balance']:
 for story in ['Story5','Story12']:
  hh=next(q for q in metrics if q['operator']==op and q['Story']==story and q['evaluation']=='heldout5');tt=[q for q in metrics if q['operator']==op and q['Story']==story and q['evaluation']=='fixed_map8'];n=[float(q['NRMSE'])*100 for q in tt];pe=[float(q['peak_relative_error'])*100 for q in tt]
  lines.append(f"| {op} | {story} | {100*float(hh['NRMSE']):.3f}% | {min(n):.3f}%—{max(n):.3f}% | {min(pe):+.3f}%—{max(pe):+.3f}% | {hh['rank']} |")
lines+=['',
'elastic的Story12固定8%误差由冻结N12的45.279%—60.185%降至2.576%—5.033%；RH4X的5%整波留出由45.335%降至4.384%。同样扩阶下，balance的Story12固定8%误差仍为9.838%—12.137%，Story5为11.699%—13.095%。两种口径均保留，不能按8%表现重新选输出定义。','',
'## 前6/12阶系数变化','',
'相对变化为新增N24的共同前缀系数与冻结N12的差，除以冻结N12该前缀系数L2；不是新识别真实模态系数。','',
'| 口径 | 层 | 前6系数相对L2变化 | 前12系数相对L2变化 |','|---|---|---:|---:|']
for op in ['elastic','balance']:
 for story in ['Story5','Story12']:
  r6=next(q for q in coefchange if q['operator']==op and q['Story']==story and q['common_prefix_modes']=='6');r12=next(q for q in coefchange if q['operator']==op and q['Story']==story and q['common_prefix_modes']=='12')
  lines.append(f"| {op} | {story} | {100*float(r6['relative_L2_change_vs_frozen_N12']):.3f}% | {100*float(r12['relative_L2_change_vs_frozen_N12']):.3f}% |")
lines+=['',
'Story12的前12系数重新分配较强，elastic为52.073%、balance为54.825%；前6变化分别4.133%、5.153%。训练按列RMS缩放后的条件数约3.88×10⁵与3.90×10⁵，虽在该rcond下秩均24，仍不能据低输出误差宣布真实逐阶可辨识。符号变化逐系数保留，没有抹去很小系数的变化。','',
'组层面另给144行同口径对照，不把N12遗漏阶当物理零。例如elastic、Story12、RH4X、8%：前1—6组曲线相对L2变化1.983%，前1—12组为11.999%；7—9阶组虽变化96.825%，其RMS仅从1.316降至0.0849 kN。说明需要同时看绝对量，不能只用相对变化渲染主导作用。','',
'## 可采用的结论','',
'在既定共同基和训练/留出规则下，扩至N24显著减少Story12输出参照的截断相关误差，并改善固定映射的8%预测。这仍是fitted-model检验；系数与部分组分配随截断改变，不能提前称真实单阶贡献。后续幅值、波形与抵消解释应同时保留拟合残差、截断和输出口径，尤其不能把N12的高误差项当作已准确复原的工程单阶。','',
'主小表prediction-errors-N24-24.csv保留所有训练/留出/固定8%记录、峰差及原生峰源行；prefix-coefficient-change-vs-N12-8.csv和common-prefix-group-curve-change-144.csv给系数/组变化。models-small-N24.json及96个系数为可审小产物。完整预测与24项时程仅在local-cache/N24-two-operator-traces.npz，禁止上传。','',
'实际命令：python -X utf8 run_N24_extension.py，随后python -X utf8 finalize_N24.py。输入SHA与根冻结一致，旧文件保持；没有原件大提取、ETABS/API或Git操作。待独立数值与可辨识性审核。']
(O/'README-N24.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for b in rules['source']:assert sha(Path(b['path']))==b['sha256']
for b in rules['additional_frozen_inputs']:assert sha(Path(b['path']))==b['sha256']
assert sha(O/'run_N24_extension.py')==rules['code_sha256']
now=datetime.now(timezone.utc);start=datetime.fromisoformat(rules['start_observed_utc']);assert now<=datetime.fromisoformat(rules['deadline_utc'])
js('verification.json',{'verified_utc':now.isoformat(),'new_N_only':24,'operators':['elastic','balance'],'rcond':1e-10,'prediction_rows':24,'new_models':2,'rank_both':24,'training_only_native5_SHW3_SHW4':True,'fixed_validation_native5_RH4':True,'native8_all_cases_no_refit':True,'N6_N12_not_refitted':True,'metrics_independently_recomputed_from_saved_prediction_arrays':True,'max_NRMSE_recheck_difference':maxerr,'coefficient_and_group_changes_against_frozen_N12':True,'full_arrays_local_only':True,'all_root_sources_and_code_hashes_unchanged':True,'classified_as':'fitted-model, not true modal decomposition'})
files=[{'name':p.name,'bytes':p.stat().st_size,'last_modified_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
js('delivery-manifest.json',{'status':'complete N24-only extension; independent review pending','frozen_utc':now.isoformat(),'frozen_Asia_Shanghai':now.astimezone(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within10_minutes':True,'files':files,'local_only_array':{'path':'local-cache/N24-two-operator-traces.npz','bytes':(O/'local-cache/N24-two-operator-traces.npz').stat().st_size,'sha256':sha(O/'local-cache/N24-two-operator-traces.npz'),'upload_allowed':False},'main_errors':'prediction-errors-N24-24.csv','report':'README-N24.md'})
print(json.dumps({'frozen_Asia_Shanghai':now.astimezone(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':(now-start).total_seconds(),'files':len(files),'within10_minutes':True,'N24_error_rows':24}))
