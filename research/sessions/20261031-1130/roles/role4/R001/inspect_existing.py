from pathlib import Path
import json,csv,hashlib
O=Path(__file__).resolve().parent;R=O.parents[5];D=R.parent/'W5-重燃双塔连体'
paths={'actual_controlled':D/'research/maxwell-20261017/roles/experiments/metadata/controlled_small_tables.json','old_plus3':D/'02-数据/增阻尼多目标研究-20261016/small_tables.json','old_baseline5':D/'02-数据/增阻尼多目标研究-20261016/native0_small_tables.json'}
safe=['Modal Periods And Frequencies','Modal Participating Mass Ratios','Modal Participation Factors','Centers Of Mass And Rigidity','Mass Summary','Mass Summary by Story','Mass Summary by Group','Modal Direction Factors','Modal Load Participation Ratios']
out={}
for label,p in paths.items():
 d=json.loads(p.read_text(encoding='utf-8-sig'));entry={'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'table_names':[k for k in d if k!='Program Control'],'tables':{}}
 for k in safe:
  if k in d:
   a=d[k];entry['tables'][k]={'rows':len(a)-3,'header':a[1],'units':a[2],'selected_rows':[x for x in a[3:] if (k=='Centers Of Mass And Rigidity' or (len(x[1])>1 and x[1][1] in [1,2,3,10,13,300]))][:20]}
 out[label]=entry
(O/'direct-small-table-inspection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
