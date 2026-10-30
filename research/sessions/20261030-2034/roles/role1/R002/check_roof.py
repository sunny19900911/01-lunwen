"""Independent N36 postprocess + exact native peak accounting. No solver."""
from pathlib import Path
import csv,json,hashlib,datetime
import numpy as np
O=Path(__file__).resolve().parent;F=json.loads((O/'input-freeze.json').read_text(encoding='utf-8'))
for x in F['sources']:assert hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256']
def rc(i):
    with Path(F['sources'][i]['path']).open(encoding='utf-8-sig',newline='') as h:return list(csv.DictReader(h))
oldanchors={(x['Case'],x['anchor']):x for x in rc(2) if x['variant']=='N36_rc1e-10'}
oldsplit={(x['Case'],x['anchor'],x['group']):x for x in rc(3) if x['variant']=='N36_rc1e-10'}
ledger=[];anchors=[];splitrows=[];errors=[]
def cancellation(v):
    d=float(np.sum(abs(v)));return None if d==0 else 1-abs(float(np.sum(v)))/d
with np.load(F['sources'][1]['path'],allow_pickle=False) as a:
 for case in F['cases']:
    get=lambda z,n:a[f'N36_elastic_rc1e-10__{case}__Story12__z{z:g}__{n}']
    t=get(.05,'t');assert np.array_equal(t,get(.08,'t'))
    y0,y1=get(.05,'native'),get(.08,'native');v0,v1=get(.05,'terms'),get(.08,'terms')
    g0=np.column_stack([v0[:,:12].sum(1),v0[:,12:].sum(1)])
    g1=np.column_stack([v1[:,:12].sum(1),v1[:,12:].sum(1)])
    A0,A1=np.max(abs(g0),0),np.max(abs(g1),0);assert np.all(A0>0) and np.all(A1>0)
    h0,h1=g0/A0,g1/A1;da=(A1-A0)*(h1+h0)/2;dw=(A1+A0)*(h1-h0)/2
    errors.append(float(np.max(abs(g1-g0-da-dw))))
    i0,i1=int(np.argmax(abs(y0))),int(np.argmax(abs(y1)));P0,P1=float(abs(y0[i0])),float(abs(y1[i1]));assert P0>0
    sign=float(np.sign(y0[i0]));same=float(sign*y1[i0]);D=float(sign*(y0[i0]-y1[i0]));M=P1-same;diff=P0-P1
    assert M>=0
    identity=diff-(D-M);assert abs(identity)<1e-10
    ledger.append({'Case':case,'Story':'Story12','t0_native5_peak_s':float(t[i0]),'t1_native8_peak_s':float(t[i1]),'s0':sign,'P5_native_kN':P0,'P8_native_kN':P1,'s0_V8_at_t0_kN':same,'D_old_peak_suppression_kN':D,'M_controlling_peak_transfer_gap_kN':M,'P5_minus_P8_kN':diff,'D_minus_M_kN':D-M,'identity_error_kN':identity,'native_peak_reduction_percent':100*diff/P0,'D_over_P5_percent':100*D/P0,'M_over_P5_percent':100*M/P0,'identity':'exact native peak ledger; M is not energy or independent causal contribution'})
    for label,i in [('native5_peak',i0),('native8_peak',i1)]:
        cg0,cg1=cancellation(g0[i]),cancellation(g1[i]);ref=oldanchors[case,label]
        row={'Case':case,'anchor':label,'time_s':float(t[i]),'low5_kN':float(g0[i,0]),'high5_kN':float(g0[i,1]),'low8_kN':float(g1[i,0]),'high8_kN':float(g1[i,1]),'chi_two_groups5':cg0,'chi_two_groups8':cg1,'chi_inside_low5':cancellation(v0[i,:12]),'chi_inside_high5':cancellation(v0[i,12:]),'chi_inside_low8':cancellation(v1[i,:12]),'chi_inside_high8':cancellation(v1[i,12:]),'native5_kN':float(y0[i]),'native8_kN':float(y1[i]),'prediction5_kN':float(g0[i].sum()),'prediction8_kN':float(g1[i].sum()),'amplitude_term_sum_kN':float(da[i].sum()),'waveform_term_sum_kN':float(dw[i].sum())}
        for field,val in [('time_s',t[i]),('low5_same_t_kN',g0[i,0]),('high5_same_t_kN',g0[i,1]),('low8_same_t_kN',g1[i,0]),('high8_same_t_kN',g1[i,1]),('chi5_same_t',cg0),('chi8_same_t',cg1),('sum_symmetric_amplitude_terms_kN',da[i].sum()),('sum_normalized_waveform_terms_kN',dw[i].sum())]:errors.append(abs(float(ref[field])-float(val)))
        assert g0[i,0]*g0[i,1]>0 and g1[i,0]*g1[i,1]>0
        anchors.append(row)
        for j,group in enumerate(['low1to12','high13plus']):
            ref=oldsplit[case,label,group]
            out={'Case':case,'anchor':label,'time_s':float(t[i]),'group':group,'A5_kN':float(A0[j]),'A8_kN':float(A1[j]),'v5_kN':float(g0[i,j]),'v8_kN':float(g1[i,j]),'amplitude_component_kN':float(da[i,j]),'normalized_waveform_component_kN':float(dw[i,j]),'delta_kN':float(g1[i,j]-g0[i,j])}
            for field,val in [('A5_kN',A0[j]),('A8_kN',A1[j]),('v5_same_t_kN',g0[i,j]),('v8_same_t_kN',g1[i,j]),('symmetric_amplitude_term_kN',da[i,j]),('normalized_waveform_term_kN',dw[i,j])]:errors.append(abs(float(ref[field])-float(val)))
            splitrows.append(out)
assert len(ledger)==3 and len(anchors)==6 and len(splitrows)==12 and max(errors)<1e-8
for name,rows in [('native-peak-ledger-3.csv',ledger),('independent-roof-anchors-6.csv',anchors),('independent-symmetric-split-12.csv',splitrows)]:
    with (O/name).open('x',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
out={'completed_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'all_checks_passed':True,'ledger':ledger,'anchors':anchors,'maximum_role6_or_identity_check_error_kN':max(errors),'M_nonnegative_all_three':True,'two_groups_same_sign_all6_anchors_both_states':True,'group_internal_cancellation_separately_reported':True,'roles6_recomputed_from_role4_arrays_not_executed_script':True,'no_refit_ODE_or_scan':True,'no_full_array_output':True,'scope':'native D/M exact sampled peak bookkeeping; groups are N36 fitted references, not physical unique modal decomposition','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_freeze_sha256':hashlib.sha256((O/'input-freeze.json').read_bytes()).hexdigest()}
with (O/'results.json').open('x',encoding='utf-8',newline='\n') as h:json.dump(out,h,ensure_ascii=False,indent=2);h.write('\n')
print(json.dumps({'completed_at':out['completed_at'],'ledger':ledger,'max_error':max(errors),'within_group_chi':[(r['Case'],r['anchor'],r['chi_inside_low5'],r['chi_inside_high5'],r['chi_inside_low8'],r['chi_inside_high8']) for r in anchors]},ensure_ascii=False))
