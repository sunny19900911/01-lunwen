"""R017 root source/repair/finite-statistic checks; no trajectories or author execution."""
from pathlib import Path
from datetime import datetime
import csv, hashlib, importlib.util, json, math
S=Path(__file__).resolve().parent
R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
FOLDERS=[
'ideation/maxwell-session004/R026-forward-BE-contract',
'verification/maxwell-session004/R036-forward-BE-contract-review',
'experiments/maxwell-session004/R022-forward-BE-synthetic',
'literature/maxwell-session004/R022-BE-source-boundary',
'literature/maxwell-session004/R023-forward-BE-implementation-review',
'writing/maxwell-session004/compact-paper-v001',
'writing/maxwell-session004/compact-paper-v002',
'verification/maxwell-session004/R035-compact-math-review',
'novelty/maxwell-session004/R019-compact-source-review',
'novelty/maxwell-session004/R020-compact-v002-repair-review',
]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text('utf-8-sig'))
def verify(obj,parent,checked):
 if isinstance(obj,list):
  for item in obj:verify(item,parent,checked)
 elif isinstance(obj,dict):
  if 'sha256' in obj and any(k in obj for k in ['path','file','name']):
   name=obj.get('path',obj.get('file',obj.get('name')))
   if isinstance(name,str):
    p=Path(name)
    if not p.is_absolute():p=(R if name.startswith(('papers/','research/')) else parent)/p
    p=p.resolve()
    if p.is_relative_to(R) and '/local-cache/' not in p.as_posix() and p.suffix.lower() in {'.md','.json','.py','.csv','.txt','.diff'}:
     assert p.name not in {'5E-07','Program Control'},p
     assert p.stat().st_size<1000000,p
     assert sha(p)==obj['sha256'],p
     if 'bytes' in obj:assert p.stat().st_size==obj['bytes'],p
     checked[p.relative_to(R).as_posix()]=sha(p)
  for item in obj.values():verify(item,parent,checked)
def main():
 checked={}
 for name in FOLDERS:
  directory=B/name
  assert directory.is_dir(),name
  for p in directory.iterdir():
   if p.is_file() and p.suffix=='.json':
    verify(read(p),directory,checked)
 d=B/'experiments/maxwell-session004/R022-forward-BE-synthetic'
 summary=read(d/'summary.json')
 assert summary['fine_u1_u2_maxerror_below_point1']=={'u1':False,'u2':True}
 full=summary['comparison']['fine_vs_reference_on_98305_all_nodes']
 assert full['u1']['max_abs_error']>.1 and full['u2']['max_abs_error']<.1
 assert summary['reference_used_in_prediction'] is False
 assert summary['reference_member_read']=='D_N16384 only'
 for item in summary['predictions']:
  h=item['h'];l1=1/(1+.1*h+h*h);l3=1/(1+.1*math.sqrt(3)*h+3*h*h)
  diag,off=(l1+l3)/2,(l1-l3)/2
  assert abs(item['A_inverse'][0][0]-diag)<5e-16
  assert abs(item['A_inverse'][0][1]-off)<5e-16
  assert abs(item['a']-(.125+h*h*diag))<1e-15
  assert item['root_gate_pass'] and item['root_max_scaled_residual']<=1e-11
  assert item['root_max_iterations']<=60
  assert not item['trajectory_saved_to_disk']
  balance=item['energy_terminal']+sum(item[key] for key in ['physical_background_dissipation','physical_device_dissipation','numerical_dissipation_u','numerical_dissipation_v','numerical_dissipation_F'])-item['work_input']
  assert abs(balance-item['actual_terminal_balance'])<1e-12
 with (d/'prediction_fixed_snapshots.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 assert len(rows)==7
 for row in rows:
  x={key:float(value) for key,value in row.items()}
  E=x['u1']**2+x['u2']**2-x['u1']*x['u2']+.5*(x['v1']**2+x['v2']**2)+x['F']**2/16
  assert abs(E-x['E'])<1e-12
  balance=E+sum(x[key] for key in ['D_background','D_device','D_numerical_u','D_numerical_v','D_numerical_F'])-x['W_input']
  assert abs(balance-x['actual_cumulative_balance'])<1e-12
 events=read(d/'reference_read_order.json')['events']
 labels=[e['event'] for e in events]
 assert labels.index('both_predictions_and_hashes_on_disk_before_reference')<labels.index('reference_hash_access_start')<labels.index('reference_hash_verified_np_load_next')
 assert labels.count('prediction_complete')==2
 olddraft=R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v001.md'
 newdraft=olddraft.with_name('maxwell-paper-compact-v002.md')
 a,b=olddraft.read_text('utf-8').splitlines(),newdraft.read_text('utf-8').splitlines()
 assert len(a)==len(b)
 changed=[i+1 for i,(x,y) in enumerate(zip(a,b)) if x!=y]
 assert changed==[3,43,47,51,53,54,55,56,58],changed
 assert 'sin(t)·1_{[0,20π]}(t)' in b[46] and '[s0(t)+d(t)]' in b[57]
 assert '非零导出末动能与势能之和' in b[42]
 assert '绝对' in b[50] and all('绝对' in b[i-1] for i in [53,54,55,56])
 assert sha(olddraft)=='560d950d3ede543a3ddb78b937803ad750dec1d685a9d16d62ea8a8c90be6d78'
 assert sha(newdraft)=='02ae657ba2d49cf270cacd2a0860fc8d44d041d8dd5b7a643d0efd47caeaa890'
 spec2=importlib.util.spec_from_file_location('publish011',S/'prepare_R011_publish.py')
 diffmod=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(diffmod)
 diffcheck=diffmod.check_diff(B/'writing/maxwell-session004/compact-paper-v002/v001-to-v002.diff',olddraft,newdraft)
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'root_full_content_read':['R026 general BE contract; R036 independent math review','R022 full forward_be.py plus report/summary and R023 complete limited implementation review','R022 primary-source boundary report; root did not view original pages in this checkpoint','compact v001/v002 complete text/diff and R035/R019/R020 review reports'],
 'root_checks':{'two_inverse_eigenformulas':True,'seven_snapshot_energy_balances':True,'read_order_normal_code_path':True,'compact_exact_changed_lines':changed,'diff':diffcheck},
 'BE_fine_fullgrid_errors':full,'BE_fine_gate':summary['fine_u1_u2_maxerror_below_point1'],
 'BE_interpretation':'Fine u1 predeclared maxabs<.1 gate failed. Accepted as reported finite diagnostic with math and static/small-output audit; not independently rerun whole-window max/RMS or certified true continuous error.',
 'rounding_identity_limit':'Implementation outputs two momentum and one constitutive increment residual scalar; remaining identity_defect contains unseparated kinematic rounding work and ordinary evaluation error. Not certified ru/rv/rF whole-step closure.',
 'source_scripts_executed':False,'arrays_or_raw_engineering_data_read':False,'reference_npz_sha_recomputed':False,
 'compact_scope':'R035 mustfix input truncation and two scope clarifications repaired; original failure and original author passed retained. Stage integration only, not reproof of all source theorems.'}
 (S/'R017-root-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'compact_changed_lines':changed,'fine_gate':result['BE_fine_gate']}))
if __name__=='__main__':main()

