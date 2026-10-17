"""Predefined seven-event LOEO diagnostic using two frozen 168-row CSVs only."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,csv,hashlib,json,platform,re,sys,time
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'round007_grouped_diagnostic'
SOURCES=[HERE/'round001/story_cut_and_spatial_acceleration.csv',HERE/'round001/adjacent_cut_net.csv']
EVENTS=['R1','RH4','SHW3','SHW4','SHW5','SHW6','SHW7']
TARGETS=['net_difference_change_pct','spatial_acceleration_change_pct']
MODELS=['cut_proxy','training_target_mean','ols_intercept_cut_floor']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()
def readcsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writejson(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def writecsv(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def freeze():
    OUT.mkdir(exist_ok=True)
    path=OUT/'frozen_protocol.json'
    if path.exists():raise FileExistsError('Protocol already frozen; do not silently replace it')
    protocol={'evidence_id':'E-EXP-007','frozen_utc':utc(),
              'sources':[{'path':str(p),'sha256':sha(p)} for p in SOURCES],
              'expected_events':EVENTS,'join_keys':['record_event','direction','floor'],
              'event_direction_floor_contract':[7,2,12],
              'feature_cut_change':'100*(cut_peak3/cut_peak0-1), percentage points',
              'feature_floor':'z=(floor-1)/11, fixed range [0,1]',
              'targets':TARGETS,'models':MODELS,
              'cut_proxy':'No parameters: predict target change equal to same-group Bottom cut change',
              'training_target_mean':'Per target: mean target of training events only',
              'ols_intercept_cut_floor':'Per target: OLS [1,cut_change_pct,z]; np.linalg.lstsq rcond=None; no interactions, tuning or selection',
              'split':'7-fold leave-one-event-out; both directions and all 12 floors held out together',
              'classification':'actual>0 and predicted>0; fixed threshold zero; exact zero is non-increase',
              'metrics':['MAE_pp','RMSE_pp','TP','FP','FN','TN'],
              'scope':'Previously explored 7-event dataset. Descriptive/group-transfer diagnostic, not external independent confirmation, mechanism, modal identification or engineering prediction guarantee.',
              'seed':None,'randomness':'none','code_sha256_at_freeze':sha(__file__)}
    writejson(path.name,protocol)
    print(json.dumps({'frozen_protocol':str(path),'sources':protocol['sources'],'models':MODELS},ensure_ascii=False,indent=2))

def rowkey(row,net=False):
    case=row['case'];direction=case[-1];event=case[:-1]
    if direction not in ['X','Y'] or event not in EVENTS:raise ValueError(f'Unexpected case {case}')
    pattern=r'^Story(\d+)/Bottom$' if net else r'^Story(\d+)$'
    field=row['lower_cut'] if net else row['story'];match=re.fullmatch(pattern,field)
    if not match:raise ValueError(f'Unrecognised floor/Bottom field {field}')
    floor=int(match.group(1))
    if floor not in range(1,13):raise ValueError(f'Unexpected floor {floor}')
    return event,direction,floor

def metrics(actual,pred):
    residual=pred-actual;truth=actual>0;positive=pred>0
    tp=int(sum(truth&positive));fp=int(sum(~truth&positive));fn=int(sum(truth&~positive));tn=int(sum(~truth&~positive))
    return {'n':len(actual),'MAE_pp':float(np.mean(abs(residual))),'RMSE_pp':float(np.sqrt(np.mean(residual*residual))),
            'TP':tp,'FP':fp,'FN':fn,'TN':tn,'actual_increases':int(sum(truth)),
            'predicted_increases':int(sum(positive)),
            'recall':tp/(tp+fn) if tp+fn else None,'precision':tp/(tp+fp) if tp+fp else None}

def run():
    started=time.perf_counter();OUT.mkdir(exist_ok=True)
    protocol_path=OUT/'frozen_protocol.json'
    protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
    assert protocol['code_sha256_at_freeze']==sha(__file__),'Code changed after protocol freeze'
    assert protocol['models']==MODELS and protocol['targets']==TARGETS
    for p,m in zip(SOURCES,protocol['sources']):assert sha(p)==m['sha256'],'Frozen source changed'
    left,right=readcsv(SOURCES[0]),readcsv(SOURCES[1])
    joined=[];maps=[];duplicates=[]
    for rows,isnet in [(left,False),(right,True)]:
        mapping={}
        for row in rows:
            key=rowkey(row,isnet)
            if key in mapping:duplicates.append(list(key))
            mapping[key]=row
        maps.append(mapping)
    expected={(event,direction,floor) for event in EVENTS for direction in ['X','Y'] for floor in range(1,13)}
    audit={'left_rows':len(left),'right_rows':len(right),'duplicates':duplicates,
           'left_missing':sorted(expected-set(maps[0])),'right_missing':sorted(expected-set(maps[1])),
           'left_only':sorted(set(maps[0])-set(maps[1])),'right_only':sorted(set(maps[1])-set(maps[0])),
           'denominator':'7 events x 2 directions x 12 floors = 168 response groups; 7 independent event groups, not 168 independent events',
           'units':'Both targets and cut feature are percentage-point changes; floor feature dimensionless. Native shear peaks kN; spatial acceleration peaks mm/s^2.'}
    writejson('join_audit.json',audit)
    assert len(left)==len(right)==168 and not duplicates
    assert set(maps[0])==set(maps[1])==expected,'No inner join allowed to hide missing groups'
    ratio_error=0.
    for key in sorted(expected):
        a,b=maps[0][key],maps[1][key];event,direction,floor=key
        assert a['case']==b['case']
        expected_upper=f'Story{floor+1}/Bottom' if floor<12 else 'declared_zero_top'
        assert b['upper_cut']==expected_upper
        p0,p3=float(a['cut_peak0_kN']),float(a['cut_peak3_kN'])
        n0,n3=float(b['peak0_kN']),float(b['peak3_kN'])
        g0,g3=float(a['spatial_accel_peak0_mm_s2']),float(a['spatial_accel_peak3_mm_s2'])
        assert min(p0,n0,g0)>0
        cut=100*(p3/p0-1);net=100*(n3/n0-1);acc=100*(g3/g0-1)
        ratio_error=max(ratio_error,abs(cut+100*float(a['cut_reduction'])),
                        abs(net-100*float(b['increase_ratio'])),abs(acc-100*float(a['spatial_accel_increase_ratio'])))
        joined.append({'record_event':event,'direction':direction,'floor':floor,'case':a['case'],
                       'cut_change_pct':cut,'floor_fraction':(floor-1)/11,
                       'net_difference_change_pct':net,'spatial_acceleration_change_pct':acc})
    assert ratio_error<1e-10
    writecsv('strict_joined_dataset.csv',joined)
    X=np.array([[1.,row['cut_change_pct'],row['floor_fraction']] for row in joined])
    assert np.isfinite(X).all()
    event_array=np.array([row['record_event'] for row in joined])
    oof=[];folds=[];diagnostics=[];failures=[]
    for target in TARGETS:
        y=np.array([row[target] for row in joined]);assert np.isfinite(y).all()
        for event in EVENTS:
            test=event_array==event;train=~test
            train_events=sorted(set(event_array[train]));test_events=sorted(set(event_array[test]))
            assert not set(train_events)&set(test_events)
            assert int(sum(test))==24 and int(sum(train))==144
            beta,_,rank,singular=np.linalg.lstsq(X[train],y[train],rcond=None)
            diagnostic={'target':target,'held_event':event,'training_events':train_events,'n_train':144,'n_test':24,
                        'rank':int(rank),'n_columns':3,'singular_values':singular.tolist(),
                        'condition_number':float(singular[0]/singular[-1]),'ols_coefficients':beta.tolist(),
                        'training_actual_increases':int(sum(y[train]>0)),
                        'held_actual_increases':int(sum(y[test]>0))}
            diagnostics.append(diagnostic)
            if rank<3:failures.append({'target':target,'held_event':event,'issue':'OLS rank deficient; minimum-norm fit retained and labelled'})
            predictions={'cut_proxy':X[test,1],'training_target_mean':np.full(sum(test),np.mean(y[train])),
                         'ols_intercept_cut_floor':X[test]@beta}
            for model,pred in predictions.items():
                fold={'target':target,'model':model,'held_event':event,**metrics(y[test],pred)}
                folds.append(fold)
                for i,p in zip(np.flatnonzero(test),pred):
                    row=joined[i];actual=float(y[i]);prediction=float(p)
                    oof.append({'target':target,'model':model,'held_event':event,**row,
                                'actual_change_pct':actual,'predicted_change_pct':prediction,
                                'residual_prediction_minus_actual_pp':prediction-actual,
                                'absolute_error_pp':abs(prediction-actual),
                                'actual_increase':bool(actual>0),'predicted_increase':bool(prediction>0)})
    summary=[]
    for target in TARGETS:
        for model in MODELS:
            selected=[row for row in oof if row['target']==target and row['model']==model]
            yy=np.array([row['actual_change_pct'] for row in selected]);pp=np.array([row['predicted_change_pct'] for row in selected])
            f=[row for row in folds if row['target']==target and row['model']==model]
            summary.append({'target':target,'model':model,**metrics(yy,pp),
                            'mean_fold_MAE_pp':float(np.mean([row['MAE_pp'] for row in f])),
                            'mean_fold_RMSE_pp':float(np.mean([row['RMSE_pp'] for row in f])),
                            'worst_fold_MAE_pp':max(row['MAE_pp'] for row in f),
                            'worst_fold_event':max(f,key=lambda row:row['MAE_pp'])['held_event']})
    writecsv('oof_predictions.csv',oof);writecsv('fold_metrics.csv',folds);writecsv('summary_metrics.csv',summary)
    positive_cases=[{'target':row['target'],'model':row['model'],'case':row['case'],'floor':row['floor'],
                     'actual_change_pct':row['actual_change_pct'],'predicted_change_pct':row['predicted_change_pct'],
                     'detected':row['predicted_increase']} for row in oof if row['actual_increase']]
    checks={'strict_168_group_bijection':not any(audit[k] for k in ['duplicates','left_missing','right_missing','left_only','right_only']),
            'ratio_fields_match_raw_peak_ratios':ratio_error<1e-10,
            'seven_disjoint_event_folds':len(folds)==42,
            'every_model_target_has_168_oof_predictions':all(row['n']==168 for row in summary),
            'all_ols_designs_full_rank':all(row['rank']==3 for row in diagnostics),
            'three_acceleration_increases_and_one_net_increase':sum(row['spatial_acceleration_change_pct']>0 for row in joined)==3 and sum(row['net_difference_change_pct']>0 for row in joined)==1,
            'all_frozen_source_hashes_unchanged':all(sha(p)==m['sha256'] for p,m in zip(SOURCES,protocol['sources'])),
            'runtime_below_600s':time.perf_counter()-started<600}
    result={'evidence_id':'E-EXP-007','finished_utc':utc(),'elapsed_seconds':time.perf_counter()-started,
            'code_sha256':sha(__file__),'protocol_sha256':sha(protocol_path),'protocol':protocol,
            'python':platform.python_version(),'numpy':np.__version__,'checks':{k:bool(v) for k,v in checks.items()},
            'join_audit':audit,'max_ratio_reconstruction_error_pp':ratio_error,
            'target_counts':{target:{'negative':sum(row[target]<0 for row in joined),'zero':sum(row[target]==0 for row in joined),'positive':sum(row[target]>0 for row in joined)} for target in TARGETS},
            'fold_metrics':folds,'summary_metrics':summary,'ols_diagnostics':diagnostics,
            'failed_rank_or_fit_paths':failures,'actual_increase_predictions':positive_cases,
            'boundary':protocol['scope']}
    writejson('grouped_diagnostic_result.json',result)
    print(json.dumps({'summary':summary,'checks':result['checks'],'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(result['checks'].values())

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--freeze-only',action='store_true');mode.add_argument('--run',action='store_true')
    args=parser.parse_args()
    if args.freeze_only:freeze()
    else:run()
