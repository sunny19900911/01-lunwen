from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[5];D=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['SHW3X','SHW3Y','SHW4X','SHW4Y','RH4X','RH4Y'];out=[]
for state,p in [('native5',D/'native0_small_tables.json'),('native8',D/'small_tables.json')]:
 d=json.loads(p.read_text(encoding='utf-8-sig'));n='Load Cases - TH - Nonlin Modal';tab=d[n];head=tab[1][1];units=tab[2][1];rr=[]
 for rn,v in tab[3:]:
  if v and v[0] in names:rr.append(dict(SourceRow=rn,**{h:v[i] if i<len(v) else None for i,h in enumerate(head) if h not in ['GUID','Notes']}))
 out.append(dict(state=state,path=str(p),sha256=sha(p),table=n,header_row=2,unit_row=3,headers=[h for h in head if h not in ['GUID','Notes']],units={h:units[i] if i<len(units) else None for i,h in enumerate(head) if h not in ['GUID','Notes']},selected_rows=rr))
(O/'loadcase-YX-raw-metadata-safe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
