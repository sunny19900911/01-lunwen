"""R018 root midpoint/engineering-plan frozen-byte and small-data review."""
from pathlib import Path
from datetime import datetime
import csv,hashlib,importlib.util,json,math
from fractions import Fraction
S=Path(__file__).resolve().parent
R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
FOLDERS=[
'ideation/maxwell-session004/R027-forward-midpoint-contract',
'verification/maxwell-session004/R037-forward-midpoint-contract-review',
'experiments/maxwell-session004/R023-forward-midpoint-synthetic',
'literature/maxwell-session004/R024-forward-midpoint-implementation-review',
'writing/maxwell-session004/engineering-paired-validation-v001',
'novelty/maxwell-session004/R021-engineering-validation-plan-review',
'verification/maxwell-session004/R038-midpoint-independent-fine-replay',
'literature/maxwell-session004/R025-nonlinear-displacement-prior-art',
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main():
 spec=importlib.util.spec_from_file_location('review017',S/'review_R017_integrations.py')
 old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
 checked={}
 for name in FOLDERS:
  directory=B/name
  assert directory.is_dir(),name
  for p in directory.iterdir():
   if p.is_file() and p.suffix=='.json':old.verify(read(p),directory,checked)
 post=S/'R018-independent-replay-postprocess'
 for p in post.iterdir():
  if p.is_file() and p.suffix=='.json':old.verify(read(p),post,checked)
 recovered=read(post/'result.json')
 assert recovered['all_six_pass'] and recovered['all_twenty_pass']
 assert recovered['maximum_snapshot_difference']<1e-6
 independent=B/'verification/maxwell-session004/R038-midpoint-independent-fine-replay'
 assert sha(independent/'independent_modal_newton.py')=='4b96a5b06df6e4f70ddf61a03cf111af6e742985317ae6b2c27b2d552fe0c78a'
 assert sha(independent/'report.md')=='8ccdc262dacb08a4f1e70964f5ee2653c4a0e517246742b786d4ef11c299afd8'
 assert 'KeyError' in read(independent/'failure.json')['error']
 independent_metrics=read(independent/'reference_metrics.json')
 assert independent_metrics['nodes']==98305
 assert independent_metrics['u1_u2_maxerror_below_point1']=={'u1':True,'u2':True}
 paper_ratios={
 'first_story_0C_value_from_Table13':str(Fraction('.038182')/Fraction('5.7')),
 'crossregion_0C_value_from_Table13':str((Fraction('.044036')-Fraction('.038182'))/24),
 'Table8_increase':str(Fraction('.00697439')-Fraction('.0066986')),
 'upper_Table9_increase':str(Fraction('.00028529')-Fraction('.00024392'))}
 assert Fraction(paper_ratios['Table8_increase'])>0 and Fraction(paper_ratios['upper_Table9_increase'])>0
 d=B/'experiments/maxwell-session004/R023-forward-midpoint-synthetic'
 data=read(d/'summary.json')
 assert data['fine_u1_u2_maxerror_below_point1']=={'u1':True,'u2':True}
 assert not data['BE_trajectory_pointwise_comparison_performed']
 assert data['no_large_arrays_saved'] and data['model_input_only_predictions']
 befile=B/'experiments/maxwell-session004/R022-forward-BE-synthetic/summary.json'
 be=read(befile);assert sha(befile)==data['BE_source_sha256']
 assert be['fine_u1_u2_maxerror_below_point1']=={'u1':False,'u2':True}
 comparisons=0
 for group,outputs in data['BE_small_summary_comparison_only'].items():
  for name,metrics in outputs.items():
   for metric,record in metrics.items():
    assert record['midpoint']==data['comparison'][group][name][metric]
    assert record['BE']==be['comparison'][group][name][metric]
    assert record['midpoint_less_than_BE']==(record['midpoint']<record['BE'])
    comparisons+=1
 assert comparisons==24
 for item in data['predictions']:
  a=item['h']/2
  l1=1/(1+.1*a+a*a);l3=1/(1+.1*math.sqrt(3)*a+3*a*a)
  diag,off=(l1+l3)/2,(l1-l3)/2
  assert abs(item['A_inverse'][0][0]-diag)<5e-16
  assert abs(item['A_inverse'][0][1]-off)<5e-16
  assert abs(item['a_F']-(.125+a*a*diag))<1e-15
  assert item['root_gate_pass'] and item['root_max_scaled_residual']<=1e-11
  assert item['root_max_iterations']<=60
  assert not item['BE_numerical_dissipation_formula_used']
  assert item['dissipation_midpoints']=='actual endpoint averages'
  balance=item['energy_terminal']+item['physical_background_dissipation']+item['physical_device_dissipation']-item['input_work']
  assert abs(balance-item['actual_terminal_balance'])<1e-12
  assert abs(balance-sum(item['signed_residual_work_sums'])-item['terminal_balance_minus_summed_residual_work'])<1e-12
 with (d/'prediction_fixed_snapshots.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
 assert len(rows)==7
 for row in rows:
  x={key:float(value) for key,value in row.items()}
  E=x['u1']**2+x['u2']**2-x['u1']*x['u2']+.5*(x['v1']**2+x['v2']**2)+x['F']**2/16
  assert abs(E-x['E'])<1e-12
  balance=E+x['physical_background_dissipation']+x['physical_device_dissipation']-x['input_work']
  assert abs(balance-x['actual_cumulative_balance'])<1e-12
 events=read(d/'reference_read_order.json')['events'];labels=[e['event'] for e in events]
 assert labels.index('both_prediction_summaries_snapshots_and_hashes_persisted')<labels.index('reference_hash_access_start')<labels.index('reference_hash_verified_np_load_next')
 assert labels.count('prediction_complete')==2
 plan=R/'papers/damping-output-boundaries/manuscript/maxwell-engineering-validation-plan-v001.md'
 assert sha(plan)=='688c5e5bb5f25a88d8845933bd10ace0091a51fbede0d19318931977430b3281'
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'root_full_content_read':['R027 exact-step midpoint contract, complete R037 math report','R023 full 18965B code/report/summary, full R024 limited implementation audit','Engineeringvalidationplan whole6541B and R021 independent integration report'],
 'root_finite_checks':{'two_halfstep_inverse_eigenformulas':True,'seven_snapshot_energy_balances':True,'BE_error_summary_comparisons':comparisons,'normal_code_read_order':True},
 'midpoint_reported_fine_errors':data['comparison']['fine_vs_reference_on_98305_all_nodes'],
 'root_trajectory_or_npz_read':False,'root_author_solver_executed':False,
 'scope':'Classical exact midpoint step;finite same-model numerical diagnostic with separately completed independent full-grid reference statistics and recovered small-result checks. Engineering plan integration only;new nonlinear Maxwell prior-art neighbor,exact-condition priority unresolved.',
 'R038_independent_metrics':independent_metrics['metrics'],
 'R038_original_status':'STOPPED_INCOMPLETE/exit1 retained;BOM small-result recovery is a distinct root phase,not a rewrite or scientific rerun',
 'postprocess_gates':{key:recovered[key] for key in ['all_six_pass','all_twenty_pass','maximum_statistic_difference','maximum_snapshot_difference']},
 'comparison_scope':'Independent program actually computed all98305 nodes and compared each with same RK4 reference;consistency with author only six statistics and20 values,not two complete predicted trajectories pointwise.',
 'new_prior_art':{'root_actual_visual_pages':[7,8,9],'source':'Correia IST author extended paper as identified in R025','exact_decimal_checks':paper_ratios,'scope':'Author-reported displacement-related indicator increases with nonlinear Maxwell alpha.15;units/normalization,synchronous peak definition,singlebranch,actual C/IC/serialk group unresolved;role6 R022 independent source review pending. Not first or complete same-condition duplicate.'},
 'BE_failure_retained':True,'no_true_continuous_accuracy_order_or_FNA_or_engineering_claim':True}
 (S/'R018-root-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'small_BE_comparisons':comparisons}))
if __name__=='__main__':main()

