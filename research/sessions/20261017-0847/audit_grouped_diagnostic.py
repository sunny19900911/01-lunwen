"""Independent standard-library audit of frozen E007 grouping and OOF fits."""
from pathlib import Path
import csv, json, math, hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'papers/damping-output-boundaries/experiments'
OUT=Path(__file__).with_name('grouped-diagnostic-independent-audit.json')
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def solve(a,b):
    a=[list(row)+[rhs] for row,rhs in zip(a,b)]
    for k in range(3):
        j=max(range(k,3),key=lambda i:abs(a[i][k]));a[k],a[j]=a[j],a[k]
        assert abs(a[k][k])>1e-10
        scale=a[k][k];a[k]=[v/scale for v in a[k]]
        for i in range(3):
            if i!=k:
                scale=a[i][k];a[i]=[x-scale*y for x,y in zip(a[i],a[k])]
    return [row[-1] for row in a]
left=read(BASE/'round001/story_cut_and_spatial_acceleration.csv')
right=read(BASE/'round001/adjacent_cut_net.csv')
net={(x['case'],int(x['lower_cut'].split('/')[0][5:])):x for x in right}
assert len(net)==len(right)==len(left)==168
joined={}
for row in left:
    case=row['case'];floor=int(row['story'][5:]);other=net[(case,floor)]
    f=lambda a,b:100*(float(a)/float(b)-1)
    key=(case,floor);assert key not in joined
    joined[key]={'event':case[:-1],'x':[1.,f(row['cut_peak3_kN'],row['cut_peak0_kN']),(floor-1)/11],
        'net_difference_change_pct':f(other['peak3_kN'],other['peak0_kN']),
        'spatial_acceleration_change_pct':f(row['spatial_accel_peak3_mm_s2'],row['spatial_accel_peak0_mm_s2'])}
events=sorted({r['event'] for r in joined.values()});assert len(events)==7
frozen=read(BASE/'round007_grouped_diagnostic/oof_predictions.csv')
lookup={(r['target'],r['model'],r['case'],int(r['floor'])):r for r in frozen}
assert len(lookup)==len(frozen)==1008
summary=[];max_difference=0.
for target in ['net_difference_change_pct','spatial_acceleration_change_pct']:
    predictions={name:[] for name in ['cut_proxy','training_target_mean','ols_intercept_cut_floor']}
    for event in events:
        train=[r for r in joined.values() if r['event']!=event]
        test=[(key,r) for key,r in joined.items() if r['event']==event]
        assert len(train)==144 and len(test)==24
        a=[[math.fsum(r['x'][i]*r['x'][j] for r in train) for j in range(3)] for i in range(3)]
        b=[math.fsum(r['x'][i]*r[target] for r in train) for i in range(3)]
        beta=solve(a,b);mean=math.fsum(r[target] for r in train)/len(train)
        for (case,floor),row in test:
            pred={'cut_proxy':row['x'][1],'training_target_mean':mean,
                'ols_intercept_cut_floor':math.fsum(v*w for v,w in zip(beta,row['x']))}
            for model,value in pred.items():
                old=lookup[(target,model,case,floor)]
                assert old['held_event']==row['event']==old['record_event']
                assert abs(float(old['actual_change_pct'])-row[target])<1e-12
                difference=abs(value-float(old['predicted_change_pct']))
                max_difference=max(max_difference,difference);assert difference<1e-8
                predictions[model].append((row[target],value))
    for model,pairs in predictions.items():
        assert len(pairs)==168
        err=[b-a for a,b in pairs]
        rec={'target':target,'model':model,'n':len(pairs),
             'MAE_pp':math.fsum(abs(x) for x in err)/168,
             'RMSE_pp':math.sqrt(math.fsum(x*x for x in err)/168),
             'TP':sum(a>0 and b>0 for a,b in pairs),
             'FP':sum(a<=0 and b>0 for a,b in pairs),
             'FN':sum(a>0 and b<=0 for a,b in pairs)}
        summary.append(rec)
result={'method':'Original two CSVs independently joined; pure Python pivoted 3x3 normal equations, not numpy least squares; train-only 7-record-group LOEO.',
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'max_abs_prediction_difference':max_difference,'rows_verified':1008,'summary':summary,
        'limits':['Previously explored data, not fresh external confirmation.',
                  'Group prefixes not verified seismologically independent events.',
                  'Frozen join_audit denominator calls groups independent; this audit does not certify that word.',
                  'Test-event Bottom response already known; descriptive proxy diagnostic, not prior engineering forecast.']}
OUT.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps({'verified_oof_rows':1008,'max_prediction_difference':max_difference,'TP':[x['TP'] for x in summary],'FN':[x['FN'] for x in summary]}))
