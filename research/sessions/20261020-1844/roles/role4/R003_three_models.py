from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[4];W=R.parent/'W5-重燃双塔连体';D=W/'02-数据/增阻尼多目标研究-20261016'
START=datetime.fromisoformat('2026-10-20T11:37:41+00:00');DEADLINE=START+timedelta(minutes=10)
def now():return datetime.now(timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rc(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def js(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths=[O/'R001-story-forces-72.csv',O/'R002-common-six-main-axis-72.csv'];bindings=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
js('R003-input-freeze.json',{'utc':now().isoformat(),'code_sha256':sha(Path(__file__)),'start_utc':START.isoformat(),'deadline_utc':DEADLINE.isoformat(),'scope':'three native Bottom model outputs, six common cases; physical input/model pairing remains unverified; modal ranks by directional mass ratio, not mode number or shear contribution','inputs':bindings})
physical={(r['Case'],r['Story']):r for r in rc(paths[0])};paired=rc(paths[1]);out=[]
for r in paired:
 p=physical[r['Case'],r['Story']];a=r['Axis'];field='V'+a;assert p['units']=='kN' and p['Location']==r['Location']=='Bottom'
 out.append({'Case':r['Case'],'wave_family':r['wave_family'],'Axis':a,'Story':r['Story'],'Location':'Bottom','units':'kN','P0_kN':float(r['P0_kN']),'P3_kN':float(r['P3_kN']),'Pphysical_kN':float(p[field+'_peak_abs']),'t_peak0_s':float(r['t_peak0_s']),'t_peak3_s':float(r['t_peak3_s']),'t_peakphysical_s':float(p[field+'_peak_t_s']),'source_row0':r['source_row0'],'source_row3':r['source_row3'],'source_rowphysical':p[field+'_peak_SourceRow'],'physical_over_label3_peak':float(p[field+'_peak_abs'])/float(r['P3_kN']),'label0_label3_input_pair_verified':True,'physical_input_and_complete_model_pair_verified':False,'physical_own_output_complete':p['exact_base_grid']=='True','grid_extent_count_match_only':int(p['n_native'])==int(r['n_points']) and float(p['t0_s'])==float(r['t0_s']) and float(p['t1_s'])==float(r['t1_s']),'scope':'three native QT output peaks; cross-model ratios descriptive, not damping-only causal effect or isolated QS'})
assert len(out)==72 and len({(r['Case'],r['Story']) for r in out})==72
cs('R003-three-model-peaks-72.csv',out);print('FIRST_TABLE_SAVED '+now().isoformat()+' rows=72',flush=True)
sources=[('baseline_label0',D/'native0_small_tables.json'),('modal_added_label3',D/'small_tables.json'),('physical_devices',W/'research/maxwell-20261017/roles/experiments/metadata/controlled_small_tables.json')]
modal=[]
for model,path in sources:
 assert now()<DEADLINE
 bindings.append({'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)})
 small=json.loads(path.read_text(encoding='utf-8'));pp=small['Modal Periods And Frequencies'];mm=small['Modal Participating Mass Ratios'];ph=pp[1][1];mh=mm[1][1];period={int(row[1][ph.index('Mode')]):row[1][ph.index('Period')] for row in pp[3:]}
 assert len(period)==len(mm)-3==300
 for axis in ['X','Y']:
  rank=sorted(mm[3:],key=lambda row:row[1][mh.index('U'+axis)],reverse=True)[:3]
  for j,(srcrow,row) in enumerate(rank,1):
   mode=int(row[mh.index('Mode')]);modal.append({'model':model,'Axis':axis,'rank_by_directional_mass_ratio':j,'global_mode_number':mode,'period_s':period[mode],'directional_mass_ratio':row[mh.index('U'+axis)],'native_mass_table_source_row':srcrow,'scope':'largest directional effective mass ratios among 300 summaries; not first global modes, node shapes, response amplitudes or story shear shares'})
cs('R003-top3-participating-modes-18.csv',modal)
example=next(r for r in out if r['Case']=='RH4X' and r['Story']=='Story1');higher=sum(r['Pphysical_kN']>r['P3_kN'] for r in out);lower=sum(r['Pphysical_kN']<r['P3_kN'] for r in out)
summary={'finished_utc':now().isoformat(),'rows':72,'modal_summary_rows':18,'physical_peak_higher_than_label3_count':higher,'physical_peak_lower_than_label3_count':lower,'example':example,'modal_top3':modal,'inputs':bindings,'source_arrays_read':0,'source_workbooks_read':0,'new_modal_decompositions':0}
js('R003-result.json',summary)
lines=['# R003：三类模型原生Bottom剪力与主要参与模态','','72行共同六工况对照已从本轮冻结小表直接组合，保留kN、峰时和原表源行。0/3已核同输入；实体模型只保留同名工况及各自完整输出身份，输入/完整主体身份尚未全部配对。不能把三列之差解释为仅由阻尼方式导致。','', '|示例|标签0峰/kN|标签3峰/kN|实体装置峰/kN|峰时0/3/实体/s|','|---|---:|---:|---:|---|',f"|RH4X Story1|{example['P0_kN']:.4f}|{example['P3_kN']:.4f}|{example['Pphysical_kN']:.4f}|{example['t_peak0_s']:.2f}/{example['t_peak3_s']:.2f}/{example['t_peakphysical_s']:.2f}|",'',f"共同72行中，实体峰高于标签3为{higher}行，低于为{lower}行；这只是各模型原生QT的数值对照，不是对哪一种阻尼策略更优的公平裁决。示例说明不能把标签3的响应直接代作实际阻尼器响应。",'', '## 各方向前三个主要参与模态','', '按300阶摘要中该方向有效质量参与率从大到小选三阶；序号是原全局模态号。它与按频率顺序取前三阶不同，不等于这三阶的楼层剪力贡献。','', '|模型|方向|主要模态号（质量参与率）|','|---|---|---|']
for model,_ in sources:
 for axis in ['X','Y']:
  rr=[r for r in modal if r['model']==model and r['Axis']==axis];lines.append('|'+model+'|'+axis+'|'+'；'.join(f"{r['global_mode_number']}（{100*r['directional_mass_ratio']:.5f}%）" for r in rr)+'|')
lines+=['','完整周期与质量率见18行CSV。缺节点振型与原生模态坐标，不做精确模态分解或频带拟合。标签0不是零阻尼证明，标签3实际逐阶阻尼值未由本轮确认；原生Bottom也不自动等于剔除Link后的主体QS。','', '下一问题：在统一参考基的简化模型中，检验主要参与阶与更高阶幅值/相位叠加如何改变楼层剪力，再将其作为解释参考对照上述真实峰时，不将质量参与率直接当剪力占比。']
(O/'R003-report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
end=now();js('R003-delivery-manifest.json',{'status':'frozen','start_utc':START.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_10min':end<=DEADLINE,'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R003*')) if p.is_file()]})
print(json.dumps({'example':example,'higher':higher,'lower':lower,'modes':[(r['model'],r['Axis'],r['global_mode_number']) for r in modal],'frozen':end.isoformat()},ensure_ascii=False))
