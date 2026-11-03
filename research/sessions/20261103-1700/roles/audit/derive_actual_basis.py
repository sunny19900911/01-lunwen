from pathlib import Path
import csv,json,math,statistics,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
new=R/'research/sessions/20261103-1458/roles/response/three-model-common-six-records-72.csv'
old=R/'research/sessions/20261020-1844/roles/role4/R003-three-model-peaks-72.csv'
rr=read(new);oo=read(old);assert len(rr)==len(oo)==72
oldkey={(x['Case'],x['Story']):x for x in oo};records=[]
for x in rr:
 y=oldkey[x['Case'],x['Story']]
 for a,b in [('P_B_kN','P0_kN'),('P_M_kN','P3_kN'),('P_D_kN','Pphysical_kN'),('t_B_s','t_peak0_s'),('t_M_s','t_peak3_s'),('t_D_s','t_peakphysical_s')]:assert float(x[a])==float(y[b])
 x=dict(x);x['rD']=100*(1-float(x['P_D_kN'])/float(x['P_B_kN']))
 records.append(x)
case=[]
for c in sorted({x['Case'] for x in records}):
 a=sorted([x for x in records if x['Case']==c],key=lambda x:int(x['Story'][5:]));assert len(a)==12
 q=min(a,key=lambda x:x['rD']);bottom=a[0];mean=statistics.mean(x['rD'] for x in a)
 case.append({'Case':c,'minimum_story':q['Story'],'minimum_reduction_percent':q['rD'],'P_B_at_min_kN':float(q['P_B_kN']),'P_D_at_min_kN':float(q['P_D_kN']),'minimum_t_B_s':float(q['t_B_s']),'minimum_t_D_s':float(q['t_D_s']),'bottom_reduction_percent':bottom['rD'],'arithmetic_mean12_percent':mean,'bottom_minus_min_pp':bottom['rD']-q['rD'],'mean_minus_min_pp':mean-q['rD'],'bottom_is_minimum':q['Story']=='Story1'})
ranges=[]
for axis in ['X','Y']:
 for k in range(1,13):
  a=[x for x in records if x['Axis']==axis and x['Story']==f'Story{k}'];assert len(a)==3
  q=min(a,key=lambda x:x['rD']);vals=sorted(x['rD'] for x in a)
  ranges.append({'Axis':axis,'Story':f'Story{k}','minimum_percent':vals[0],'median_percent':vals[1],'maximum_percent':vals[2],'minimum_case':q['Case'],'P_B_at_min_kN':float(q['P_B_kN']),'P_D_at_min_kN':float(q['P_D_kN'])})
legacy=json.loads((R/'research/sessions/20261103-1458/roles/audit/audit.json').read_text(encoding='utf-8'))
assert legacy['source_hashes'][old.relative_to(R).as_posix()]==hashlib.sha256(old.read_bytes()).hexdigest()
for name,rows in [('independent-actual-case-minima-6.csv',case),('independent-actual-story-range-24.csv',ranges)]:
 p=H/name;assert not p.exists()
 with p.open('w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
d={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source_sha256':{p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [new,old]},'new72_exact_old72':True,'all72_rD_positive':all(x['rD']>0 for x in records),'rD_range_percent':[min(x['rD'] for x in records),max(x['rD'] for x in records)],'bottom_minimum_count_out_of6':sum(x['bottom_is_minimum'] for x in case),'case_minima':case,'actual24_two_controls_differ':legacy['D_min_and_max_controls_differ_conditional'],'same6_reference_two_controls_differ':legacy['M_min_and_max_controls_differ_common_six'],'most_mean_masking_example':max(case,key=lambda x:x['mean_minus_min_pp']),'most_bottom_masking_example':max(case,key=lambda x:x['bottom_minus_min_pp']),'old19of24_scope':'reference M vs B, fourteen directional cases; auxiliary only in actual-mainline paper','SHW3X_scope':'not present in actual six cases; fixed linear reference mechanism illustration only, cannot explain actual Story8 as observed modal decomposition','r_at_d_status':'pending independently derived response production and audit; old M-based d statistics not transferable to D'}
(H/'actual-mainline-basis.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
