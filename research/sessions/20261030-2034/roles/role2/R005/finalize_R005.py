from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261030-2034'
now=lambda:datetime.now(timezone(timedelta(hours=8)))
start=datetime.fromisoformat('2026-10-30T21:30:29+08:00');deadline=start+timedelta(minutes=10)
assert now()<deadline,'deadline; freeze only completed work'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):
    with (O/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
p=S/'roles/role1/R003/manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
for e in m['files']:
    b=Path(e['path']).read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
contract=json.loads((p.parent/'check-contract.json').read_text(encoding='utf-8'))
assert contract['necessary_not_sufficient'] and not contract['physical_output_mapping_verified_here']
cp=R/'research/sessions/20261025-1337/roles/role6/R001/input-config.json'
assert sha(cp)=='c249e22be8f0d41bb5beb59e9c24153bc26eb7948f23f72386c28f78d0a4a1e9'
cfg=json.loads(cp.read_text(encoding='utf-8'))
for c,d in cfg['cases'].items():assert d['cached_ag_unit']=='m/s²' and d['cached_ag_multiplier_for_states']==1.0
hp=Path(cfg['modal_linear_py']);assert sha(hp)=='1c2620542f812e355c4be3ad8877db92db2ba3343cd3a2405e26c731be796827'
save('cross-checks.json',{'completed':now().isoformat(),'role1_R003_manifest_sha256':sha(p),'role1_files_verified':len(m['files']),'theorem_review':'manually cross-checked B=a_s^T M phi Gamma, PSD Cauchy, same-coordinate and elastic-output conditions','ag_units':'frozen config m/s^2, multiplier1; input original function not re-extracted','negative_ag_kernel_sign':'read from existing helper; no integration rerun','config_sha256':sha(cp),'helper_sha256':sha(hp),'mass_matrix_or_native_Bottom_VX_operator_certified':False,'conditional_references_only':True,'cross_role_must_count':0})
result=json.loads((O/'results.json').read_text(encoding='utf-8'));other=json.loads((O/'role6-summary-arithmetic.json').read_text(encoding='utf-8'))
assert result['coefficient_cells']==432 and result['mass_rows']==18 and result['modes']==36
assert other['numeric_checks']==612 and other['must_count']==0
entries=[]
for f in sorted(O.iterdir()):
    if f.is_file() and f.name!='manifest.json':entries.append({'name':f.name,'bytes':f.stat().st_size,'sha256':sha(f)})
t=now();out={'status':'complete physical scale audit; conditional references, no certified native cut-force bound','started_Asia_Shanghai':start.isoformat(),'mass_scale_completed':result['completed'],'frozen_Asia_Shanghai':t.isoformat(),'deadline':deadline.isoformat(),'elapsed_seconds':(t-start).total_seconds(),'within10_minutes':t<=deadline,'mass_source_rows':18,'mode_UX_ratios':36,'coefficient_cells':432,'old_two_stories_exact_comparisons':144,'role6_small_table_arithmetic_checks':612,'role6_arithmetic_must_count':0,'role1_R003_cross_check':'frozen files hash-verified; theorem and caveats agree','no_new_fit_integrator_large_array':True,'scope_limits':['full M and exact Bottom VX elastic cut operator not certified','cached diaphragm mass sum is not automatically the full FE directional modal mass denominator','no unconditional physical bound violation inferred','role6 arithmetic does not independently validate group arrays or causality'],'files':entries}
save('manifest.json',out)
for e in entries:
    f=O/e['name'];assert f.stat().st_size==e['bytes'] and sha(f)==e['sha256']
print(json.dumps({k:v for k,v in out.items() if k!='files'},ensure_ascii=False))
