"""Read frozen primary traces only; no refit/ODE and no arrays written."""
from pathlib import Path
import json,csv,hashlib,datetime
import numpy as np
O=Path(__file__).resolve().parent;F=json.loads((O/'input-freeze.json').read_text(encoding='utf-8'))
for src in F['sources']:assert hashlib.sha256(Path(src['path']).read_bytes()).hexdigest()==src['sha256']
def rc(i):
    with Path(F['sources'][i]['path']).open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
models=json.loads(Path(F['sources'][2]['path']).read_text(encoding='utf-8'))
coef12=np.array(models['N12_elastic_rc1e-10']['raw_output_coef'])[:,0]
coef6=np.array(models['N6_elastic_rc1e-10']['raw_output_coef'])[:,0]
assert np.all(coef12[:6]!=0)
assert np.array_equal(coef12,np.array(models['N12_elastic_rc1e-08']['raw_output_coef'])[:,0])
metrics=rc(5);table=[];results=[];max_identity=0.;max_reconstruction=0.
def chi(v):
    den=abs(v).sum(1);out=np.full(len(v),np.nan);np.divide(abs(v.sum(1)),den,out=out,where=den>0);return 1-out
with np.load(F['sources'][1]['path'],allow_pickle=False) as z:
 for case in F['cases']:
    load=lambda zet,key:z[f'{case}__Story5__z{zet:g}__{key}']
    t=load(.05,'t');assert np.array_equal(t,load(.08,'t'))
    v0,v1=load(.05,'terms'),load(.08,'terms');y0,y1=load(.05,'prediction'),load(.08,'prediction')
    n0,n1=load(.05,'native'),load(.08,'native')
    g0=np.column_stack([v0[:,i:i+3].sum(1) for i in range(0,12,3)])
    g1=np.column_stack([v1[:,i:i+3].sum(1) for i in range(0,12,3)])
    max_reconstruction=max(max_reconstruction,float(np.max(abs(g0.sum(1)-y0))),float(np.max(abs(g1.sum(1)-y1))))
    A0,A1=np.max(abs(g0),0),np.max(abs(g1),0);assert np.all(A0>0) and np.all(A1>0)
    h0,h1=g0/A0,g1/A1
    da=(A1-A0)*(h1+h0)/2;dw=(A1+A0)*(h1-h0)/2
    max_identity=max(max_identity,float(np.max(abs(da+dw-(g1-g0)))))
    c0,c1=chi(g0),chi(g1);ct0,ct1=chi(v0),chi(v1)
    i0,i1=int(np.argmax(abs(y0))),int(np.argmax(abs(y1)))
    anchor=[]
    for label,i in [('predicted5_peak',i0),('predicted8_peak',i1)]:
        anchor.append({'anchor':label,'time_s':float(t[i]),'groups5_kN':g0[i].tolist(),'groups8_kN':g1[i].tolist(),'sum5_kN':float(y0[i]),'sum8_kN':float(y1[i]),'native5_kN':float(n0[i]),'native8_kN':float(n1[i]),'chi_groups5':float(c0[i]),'chi_groups8':float(c1[i]),'chi_terms5':float(ct0[i]),'chi_terms8':float(ct1[i]),'amplitude_delta_sum_kN':float(da[i].sum()),'waveform_delta_sum_kN':float(dw[i].sum())})
    for j in range(4):
        table.append({'Case':case,'frequency_order_group':f'{3*j+1}-{3*j+3}','same_time_anchor':'primary8_own_peak','t_s':float(t[i1]),'group_own_peak5_kN':float(A0[j]),'group_own_peak8_kN':float(A1[j]),'group_peak_change_percent':float(100*(A1[j]/A0[j]-1)),'same_time_group5_kN':float(g0[i1,j]),'same_time_group8_kN':float(g1[i1,j]),'symmetric_amplitude_component_kN':float(da[i1,j]),'symmetric_normalized_waveform_component_kN':float(dw[i1,j]),'identity':'fixed fitted-output reference group; not uniquely identified native modes'})
    sensitivity=[]
    for zet,v,native in [(.05,v0,n0),(.08,v1,n1)]:
        terms6=v[:,:6]*(coef6/coef12[:6]);pred6=terms6.sum(1)
        expected=next(x for x in metrics if x['variant']=='N6_elastic_rc1e-10' and x['Story']=='Story5' and x['Case']==case and float(x['zeta'])==zet)
        error=float(np.linalg.norm(pred6-native)/np.linalg.norm(native));assert abs(error-float(expected['NRMSE']))<1e-10
        groups6=np.column_stack([terms6[:,:3].sum(1),terms6[:,3:6].sum(1)])
        gp=g0 if zet==.05 else g1
        sensitivity.append({'zeta':zet,'N6_prediction_NRMSE_reproduced':error,'g1_N6_vs_N12_relative_L2':float(np.linalg.norm(groups6[:,0]-gp[:,0])/np.linalg.norm(gp[:,0])),'g2_N6_vs_N12_relative_L2':float(np.linalg.norm(groups6[:,1]-gp[:,1])/np.linalg.norm(gp[:,1]))})
    p0,p1=np.max(abs(y0)),np.max(abs(y1));pn0,pn1=np.max(abs(n0)),np.max(abs(n1))
    results.append({'Case':case,'predicted_peak5_kN':float(p0),'predicted_peak8_kN':float(p1),'predicted_reduction_percent':float(100*(1-p1/p0)),'native_peak5_kN':float(pn0),'native_peak8_kN':float(pn1),'native_reduction_percent':float(100*(1-pn1/pn0)),'pred_peak_times':[float(t[i0]),float(t[i1])],'group_peak_ratios8_over5':(A1/A0).tolist(),'individual_terms_peak_decrease_count':int(np.sum(np.max(abs(v1),0)<np.max(abs(v0),0))),'group1_signed_fraction_at8peak':float(g1[i1,0]/y1[i1]),'group4_signed_fraction_at8peak':float(g1[i1,3]/y1[i1]),'anchors':anchor,'first6_sensitivity':sensitivity})
assert len(table)==12 and max_identity<1e-9 and max_reconstruction<1e-8
with (O/'key-group-table-12.csv').open('x',encoding='utf-8',newline='') as h:
    w=csv.DictWriter(h,fieldnames=list(table[0]),lineterminator='\n');w.writeheader();w.writerows(table)
out={'completed_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'identity':'Story5 primary fitted reference, not native unique modal contributions','primary':'N12_elastic_rc1e-10','cases':results,'split_identity_max_abs_error_kN':max_identity,'groups_sum_prediction_max_abs_error_kN':max_reconstruction,'rcond_coefficient_change_zero':True,'new_ODE_or_fit':False,'arrays_output':False,'Story12_not_interpreted':True,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_freeze_sha256':hashlib.sha256((O/'input-freeze.json').read_bytes()).hexdigest()}
with (O/'results.json').open('x',encoding='utf-8',newline='\n') as h:json.dump(out,h,ensure_ascii=False,indent=2);h.write('\n')
print(json.dumps(out,ensure_ascii=False))
