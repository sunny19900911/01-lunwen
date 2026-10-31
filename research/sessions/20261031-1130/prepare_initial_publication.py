from pathlib import Path
import json,hashlib,datetime,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
st.update(last_actual=now,checkpoint='R001-initial',checkpoint_open=True,next_checkpoint='Collect six R001 actual frozen outputs; data identity before engineering modal coefficients; route root known3floor physical reconstruction to role2 after idle; no repeated fits')
st['git']['publication']='initial candidate-science checkpoint pending; only reviewed code/invariants in known model, no actual engineering coefficients claimed'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nRoot R001 actual executed and frozen, synthetic known3floor only; directB vsK residual4.44e-16, time output residual2e-15. First six tasks actualallactive11:39:55. Formal heartbeatgit-2 ACTIVE confirmed; fixed15:30:11 deadline. Initial ordinary Git publication pending receipt.\n')
paths=[S/n for n in ['plan.md','plan-theory-addendum-v001.md','claims.md','runs.md','threads.json','status.json','initial-actual-snapshot.json','actual-R001-dispatched.json','rounds/R001-start.md','rounds/R001-root-increment.md','automation-initial-receipt.json','root_three_floor_physical.py','root-R001-model-definition.json','publish_checkpoint.py','prepare_initial_publication.py']]
paths.extend(p for p in (S/'root-R001-physical-three-floor').iterdir()if p.is_file()and p.suffix in ['.md','.json','.csv'])
files=[]
for p in sorted(set(paths),key=str):
 assert p.is_file() and 'local-cache'not in p.parts and p.stat().st_size<1048576
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with (S/'git-R001-publication.json').open('x',encoding='utf-8')as f:json.dump({'checkpoint':'R001','time':now,'message':'research: start physical modal shear study with direct reconstruction check','files':files},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(files)},ensure_ascii=False))
