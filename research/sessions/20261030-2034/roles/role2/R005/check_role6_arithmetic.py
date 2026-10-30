from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
O=Path(__file__).parent;S=O.parents[5]/'research/sessions/20261030-2034'; D=S/'roles/role6/R004'
now=lambda:datetime.now(timezone(timedelta(hours=8)))
assert now()<datetime.fromisoformat('2026-10-30T21:40:29+08:00')
m=json.loads((D/'freeze.json').read_text(encoding='utf-8'))
for name,e in m['files'].items():
    b=(D/name).read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
rr=rows(D/'all12-three-input-summary-36.csv')
src={(x['Story'],x['Case'],float(x['zeta'])):x for x in rows(S/'roles/role4/R003/all12-prediction-errors-144.csv') if x['N']=='36'}
count=0;maxerr={};counts={'low_abs_larger':0,'chi_zero':0,'chi_nonzero':0,'low_ratio_above1':0,'high_reverse':0,'wave_opposes_amplitude':0,'low_amplitude_decreased':0,'high_amplitude_decreased':0}
def ck(name,a,b):
    global count
    e=abs(a-b);maxerr[name]=max(maxerr.get(name,0.),e);assert e<1e-8*max(1.,abs(b)),(name,a,b);count+=1
for row in rr:
    peak=[]
    for z in (5,8):
        low=float(row[f'low{z}_at_native_peak_kN']);high=float(row[f'high{z}_at_native_peak_kN']);p=float(row[f'prediction{z}_at_native_peak_kN']);res=float(row[f'residual{z}_at_native_peak_kN']);v=float(row[f'native{z}_signed_peak_kN']);peak.append(abs(v))
        ck('group_prediction',low+high,p);ck('prediction_residual',p+res,v)
        ck('chi',1-abs(low+high)/(abs(low)+abs(high)),float(row[f'chi{z}_at_native_peak']))
        for label,value in [('low',low),('high',high),('residual',res)]:ck('ratio_'+label,value/v,float(row[f'{label}{z}_signed_over_native']))
        ck('N36_NRMSE',float(row[f'N36_NRMSE{z}']),float(src[row['Story'],row['Case'],z/100]['NRMSE']))
        counts['low_abs_larger']+=abs(low)>abs(high);counts['chi_zero']+=abs(float(row[f'chi{z}_at_native_peak']))<1e-12;counts['chi_nonzero']+=abs(float(row[f'chi{z}_at_native_peak']))>=1e-12
        counts['low_ratio_above1']+=low/v>1;counts['high_reverse']+=high/v<0
        a=float(row[f'native{z}_peak_symmetric_amplitude_sum_kN']);b=float(row[f'native{z}_peak_normalized_waveform_sum_kN']);opposed=a*b<0
        assert opposed==(row[f'native{z}_peak_wave_opposes_amplitude']=='True');counts['wave_opposes_amplitude']+=opposed
    ck('native_peak_reduction',100*(1-peak[1]/peak[0]),float(row['native_peak_reduction_percent']))
    for group in ('low','high'):
        a5=float(row[f'{group}_A5_kN']);a8=float(row[f'{group}_A8_kN'])
        ck(group+'_amplitude_reduction',100*(1-a8/a5),float(row[f'{group}_group_amplitude_reduction_percent']))
        counts[group+'_amplitude_decreased']+=a8<a5
result={'completed':now().isoformat(),'scope':'small frozen summary arithmetic only, not independent group arrays or modal identification','rows':len(rr),'numeric_checks':count,'must_count':0,'max_abs_difference':maxerr,'counts':counts,'source_freeze_sha256':hashlib.sha256((D/'freeze.json').read_bytes()).hexdigest()}
with (O/'role6-summary-arithmetic.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
