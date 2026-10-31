from pathlib import Path
import csv,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[5];W=R.parent/'W5-重燃双塔连体';D=W/'02-数据/增阻尼多目标研究-20261016'
sources=[W/'research/maxwell-20261017/experiments/R001/core-cache/manifest.json',D/'response_cache_manifest.json',D/'原生0数据缓存/manifest.json']
out=[]
for p in sources:
 d=json.loads(p.read_text(encoding='utf-8'));rec=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_original=d.get('source',d.get('path')),tables={})
 for name,tab in d.get('tables',{}).items():
  if not any(w in name.lower() for w in ['story force','frame force','base reaction','diaphragm cm']):continue
  info={k:v for k,v in tab.items() if k!='groups' and not isinstance(v,(dict,list))};info['columns']=tab.get('columns',tab.get('value_columns'));info['key_columns']=tab.get('key_columns');info['whole_table_step_types']=tab.get('step_types');info['source_headers']=tab.get('headers');gg=tab.get('groups',{});modal=[];none=[];cases=set();types=set()
  for key,g in gg.items():
   kk=g.get('keys',{});cases.add(str(kk.get('Output Case',kk.get('Case'))));types.add(str(kk.get('Case Type')))
   if any('modal' in str(v).lower() or str(v).lower()=='mode' for v in kk.values()):modal.append(dict(group=key,**g))
   if g.get('step_types',{}).get('None',0) or g.get('step_types',{}).get('Mode',0):none.append(dict(group=key,keys=kk,step_types=g.get('step_types'),first_source_row=g.get('first_source_row'),last_source_row=g.get('last_source_row')))
  info.update(groups=len(gg),cache_group_row_count_fields=sorted({k for g in gg.values() for k in g if 'row' in k.lower() or k in ['n','count']}),cache_group_rows=sum(g.get('n',g.get('rows',g.get('count',0))) for g in gg.values()),cases=sorted(cases),case_types=sorted(types),modal_or_Mode_key_groups=modal,no_time_or_Mode_step_groups=none)
  rec['tables'][name]=info
 out.append(rec)
(O/'modal-force-existing-manifest-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([dict(path=d['path'],tables={k:{x:v.get(x) for x in ['groups','data_rows','all_data_rows','cache_group_row_count_fields','cache_group_rows','skipped_non_step','whole_table_step_types','source_headers']} for k,v in d['tables'].items()}) for d in out],ensure_ascii=False,indent=2))
