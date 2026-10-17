"""Only frozen small result comparison after R038 BOM failure; no trajectory access."""
from pathlib import Path
from datetime import datetime
import csv,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3]
V=R/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004/R038-midpoint-independent-fine-replay'
A=R/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R023-forward-midpoint-synthetic'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main():
 assert not (H/'result.json').exists()
 inputs=[V/name for name in ['reference_metrics.json','prediction_four_snapshots.csv','report.md','validation.json','closure_checks.json','failure.json','independent_modal_newton.py']]
 inputs += [A/'summary.json',A/'prediction_fixed_snapshots.csv',H/'protocol.md',Path(__file__),H.parent/'independent-midpoint-fine-replay-protocol-v001.md']
 frozen=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs]
 (H/'input-freeze.json').write_text(json.dumps({'at':datetime.now().astimezone().isoformat(),'files':frozen},ensure_ascii=False,indent=2)+'\n','utf-8')
 assert sha(V/'report.md')=='8ccdc262dacb08a4f1e70964f5ee2653c4a0e517246742b786d4ef11c299afd8'
 assert 'KeyError' in read(V/'failure.json')['error']
 own=read(V/'reference_metrics.json');author=read(A/'summary.json')
 assert own['N']==16384 and own['nodes']==98305
 assert own['u1_u2_maxerror_below_point1']=={'u1':True,'u2':True}
 stat=[]
 for name in ['u1','u2','F']:
  for field in ['max_abs_error','RMS_error']:
   x=own['metrics'][name][field];y=author['comparison']['fine_vs_reference_on_98305_all_nodes'][name][field]
   stat.append({'output':name,'metric':field,'independent':x,'author':y,'absolute_difference':abs(x-y),'passed':abs(x-y)<1e-6})
 with (V/'prediction_four_snapshots.csv').open(encoding='utf-8-sig',newline='') as f:ownrows=list(csv.DictReader(f))
 with (A/'prediction_fixed_snapshots.csv').open(encoding='utf-8-sig',newline='') as f:authorrows=list(csv.DictReader(f))
 assert len(ownrows)==4 and len(authorrows)==7
 assert [int(row['node']) for row in ownrows]==[0,16384,16529,98304]
 points=[]
 for row in ownrows:
  assert int(row['N'])==16384
  match=[item for item in authorrows if int(item['N'])==16384 and int(item['node'])==int(row['node'])]
  assert len(match)==1
  assert row['time']==match[0]['time']
  for field in ['u1','u2','v1','v2','F']:
   x,y=float(row[field]),float(match[0][field])
   points.append({'node':int(row['node']),'state':field,'independent':x,'author':y,'absolute_difference':abs(x-y),'passed':abs(x-y)<1e-6})
 assert len(stat)==6 and len(points)==20
 for item in frozen:
  p=R/item['path'];assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes'],p
 result={'at':datetime.now().astimezone().isoformat(),'six_statistic_checks':stat,'twenty_snapshot_checks':points,
 'all_six_pass':all(item['passed'] for item in stat),'all_twenty_pass':all(item['passed'] for item in points),
 'maximum_statistic_difference':max(item['absolute_difference'] for item in stat),
 'maximum_snapshot_difference':max(item['absolute_difference'] for item in points),
 'original_gate':1e-6,'all_original_inputs_unchanged':True,'old_R038_exit1_and_failure_preserved':True,
 'scientific_solver_rerun':False,'reference_arrays_opened':False,
 'scope':'Small-output recovery completes originally missing checks only. Independent all-node reference metrics come from R038 earlier completed stage;no complete author-vs-independent predicted-trajectory pointwise comparison.'}
 (H/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 outcome='全部通过' if result['all_six_pass'] and result['all_twenty_pass'] else '存在失败'
 report=f"# R038 BOM后的小结果独立验收\n\n{result['at']}，原六统计和二十固定状态值在原1e-6门下{outcome}。六统计最大差{result['maximum_statistic_difference']:.17g}，二十值最大差{result['maximum_snapshot_difference']:.17g}。\n\n仅新程序用utf-8-sig解析已冻结CSV，不重跑求解器、不读/hash/stat NPZ或原Excel，全部旧输入SHA保持。原R038仍为exit1/STOPPED_INCOMPLETE，failure与冻结报告不回写。此阶段补齐被BOM阻断的小结果比较，与R038先前完成的独立98305节点对同RK4参考统计分开登记。\n\n未比较两条完整预测轨迹，不认证真连续误差、收敛阶、盲测、FNA或实际工程效果。详细6+20项数和源身份见result.json/input-freeze.json。\n"
 (H/'report.md').write_text(report,'utf-8')
 files=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(H.iterdir()) if p.is_file()]
 (H/'freeze.json').write_text(json.dumps({'at':datetime.now().astimezone().isoformat(),'files':files},ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:result[key] for key in ['all_six_pass','all_twenty_pass','maximum_statistic_difference','maximum_snapshot_difference']}))
if __name__=='__main__':main()

