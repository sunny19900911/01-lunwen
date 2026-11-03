from pathlib import Path
import csv,json,math,hashlib,datetime,collections
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(rel):
 p=R/rel
 return list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b,tol=1e-9):
 assert abs(float(a)-float(b))<=tol,(a,b)
def nstory(s):return int(s.removeprefix('Story'))
sources=[
 'research/sessions/20261020-1844/roles/role4/R003-three-model-peaks-72.csv',
 'research/sessions/20261019-2045/roles/data/R001-link-geometry-88.csv',
 'research/sessions/20261019-2045/roles/data/R002-native-horizontal/layer-axis-peaks-48.csv',
 'research/sessions/20261019-2045/roles/data/R002-native-horizontal/device-contributions-384.csv',
 'research/sessions/20261102-1917/roles/role4/R001/paired-record-evidence-168.csv']
before={s:sha(R/s) for s in sources}
peaks,geo,layer,device,paired=[read(p) for p in sources]
assert len(peaks)==72 and len(geo)==88 and len(layer)==48 and len(device)==384 and len(paired)==168
assert len({g['Link'] for g in geo})==88
geomax={k:0. for k in ['length','nx','ny','nz','inclination']};gby={}
for g in geo:
 xyz=[[float(g[f'{end}_{axis}_m']) for axis in ['X','Y','Z']] for end in ['I','J']]
 vec=[v-u for u,v in zip(*xyz)];L=math.sqrt(math.fsum(x*x for x in vec));nn=[x/L for x in vec]
 inc=math.degrees(math.asin(abs(nn[2])))
 assert g['I_coordinate_found']==g['J_coordinate_found']=='True' and L>0 and xyz[1][2]>xyz[0][2]
 st=nstory(g['Story']);assert g['J_Story']==g['Story'] and g['I_Story']==('Base' if st==1 else f'Story{st-1}')
 typ='X' if abs(nn[0])>1e-12 and abs(nn[1])<=1e-12 else 'Y' if abs(nn[1])>1e-12 and abs(nn[0])<=1e-12 else 'other'
 assert typ!='other'
 z=gby.setdefault(g['Story'],{'n':0,'X':0,'Y':0,'zlow':xyz[0][2],'zhigh':xyz[1][2],'lengths':[],'angles':[]})
 close(z['zlow'],xyz[0][2]);close(z['zhigh'],xyz[1][2]);z['n']+=1;z[typ]+=1;z['lengths'].append(L);z['angles'].append(inc)
 for name,new,old in [('length',L,g['length_m']),('nx',nn[0],g['nx']),('ny',nn[1],g['ny']),('nz',nn[2],g['nz']),('inclination',inc,g['elevation_from_horizontal_deg'])]:geomax[name]=max(geomax[name],abs(new-float(old)))
assert set(gby)=={f'Story{i}' for i in range(1,12)}
assert all((z['n'],z['X'],z['Y'])==(8,4,4) for z in gby.values())
assert max(geomax.values())<1e-10

pkey={(p['Case'],p['Story']):p for p in paired};groups=collections.defaultdict(list)
required={f'{w}{a}' for w in ['RH4','SHW4','SHW7'] for a in ['X','Y']}
assert {x['Case'] for x in peaks}==required
assert len({(x['Case'],x['Story']) for x in peaks})==72
for p in peaks:
 assert p['Location']=='Bottom' and p['units']=='kN' and p['Axis']==p['Case'][-1]
 assert p['label0_label3_input_pair_verified']=='True' and p['physical_own_output_complete']=='True'
 assert p['physical_input_and_complete_model_pair_verified']=='False'
 q=pkey[p['Case'],p['Story']]
 for a,b in [('P0_kN','P_B_kN'),('P3_kN','P_M_kN'),('t_peak0_s','t_B_s'),('t_peak3_s','t_M_s')]:close(p[a],q[b],1e-12)
 p=dict(p);p['rD']=100*(1-float(p['Pphysical_kN'])/float(p['P0_kN']));p['rM']=100*(1-float(p['P3_kN'])/float(p['P0_kN']))
 groups[p['Axis'],p['Story']].append(p)
assert len(groups)==24 and all(len(v)==3 for v in groups.values())
controls=[]
for (axis,story),records in sorted(groups.items(),key=lambda z:(z[0][0],nstory(z[0][1]))):
 rD=min(records,key=lambda x:x['rD']);vD=max(records,key=lambda x:float(x['Pphysical_kN']))
 rM=min(records,key=lambda x:x['rM']);vM=max(records,key=lambda x:float(x['P3_kN']))
 rd=sorted(x['rD'] for x in records);gap=rd[1]-rd[0]
 controls.append({'Axis':axis,'Story':story,'D_min_reduction_case':rD['Case'],'D_min_reduction_percent':rD['rD'],'D_peak_at_min_reduction_kN':float(rD['Pphysical_kN']),'D_max_demand_case':vD['Case'],'D_max_demand_kN':float(vD['Pphysical_kN']),'D_reduction_at_max_demand_percent':vD['rD'],'D_controls_differ':rD['Case']!=vD['Case'],'M_min_reduction_case':rM['Case'],'M_min_reduction_percent':rM['rM'],'M_max_demand_case':vM['Case'],'M_max_demand_kN':float(vM['P3_kN']),'M_controls_differ':rM['Case']!=vM['Case'],'M_D_max_controls_differ':vM['Case']!=vD['Case'],'D_min_vs_second_gap_pp':gap})

geo_by_link={g['Link']:g for g in geo};timing=[];maxsumerr=0.;maxprojerr=0.
for row in layer:
 if row['input_main_axis']!='True':continue
 key=row['Story'],row['Case'],row['Axis'];dd=[d for d in device if (d['Story'],d['Case'],d['Axis'])==key]
 assert len(dd)==8 and len({d['Link'] for d in dd})==8
 assert int(row['devices_total'])==8 and int(row['devices_nonzero_projection'])==4
 for d in dd:
  g=geo_by_link[d['Link']];assert g['Story']==row['Story'];assert (d['I_Point'],d['J_Point'])==(g['I_Point'],g['J_Point'])
  n=float(g['n'+row['Axis'].lower()]);maxprojerr=max(maxprojerr,abs(n*float(d['P_at_QT_peak_kN'])-float(d['horizontal_at_QT_peak_kN'])))
  close(d['projection_n'],n)
 total=math.fsum(float(d['horizontal_at_QT_peak_kN']) for d in dd)
 err=abs(total-float(row['QD_at_QT_peak_kN']));maxsumerr=max(err,maxsumerr)
 ratio=100*abs(total)/float(row['QD_peak_abs_kN'])
 timing.append({'Story':row['Story'],'Case':row['Case'],'Axis':row['Axis'],'QT_peak_kN':float(row['QT_peak_kN']),'tQT_s':float(row['QT_peak_t_s']),'QD_peak_kN':float(row['QD_peak_abs_kN']),'tQD_s':float(row['QD_peak_t_s']),'QD_at_QT_kN':total,'timing_ratio_percent':ratio,'sum_check_residual_kN':err})
assert len(timing)==24 and maxsumerr<1e-9 and maxprojerr<1e-9

# Only now compare the frozen producers' small output tables, never their algorithm.
P=R/'research/sessions/20261103-1458/roles/response';G=R/'research/sessions/20261103-1458/roles/geometry'
freeze=json.loads((P/'delivery-manifest.json').read_text(encoding='utf-8'));assert freeze['status']=='frozen'
prod_ctrl={(x['Axis'],x['Story']):x for x in read(str((P/'common-six-control-records-24.csv').relative_to(R)))}
checked=0
for q in controls:
 p=prod_ctrl[q['Axis'],q['Story']]
 for a,b in [('D_min_reduction_case','conditional_min_D_reduction_case'),('D_max_demand_case','actual_max_demand_case'),('M_min_reduction_case','reference_min_reduction_case_common_six'),('M_max_demand_case','reference_max_demand_case_common_six')]:assert q[a]==p[b];checked+=1
 for a,b in [('D_min_reduction_percent','conditional_min_D_reduction_percent'),('D_peak_at_min_reduction_kN','P_D_at_conditional_min_D_reduction_kN'),('D_max_demand_kN','actual_max_demand_kN'),('D_reduction_at_max_demand_percent','conditional_r_D_at_actual_max_demand_percent'),('M_min_reduction_percent','reference_min_reduction_percent_common_six'),('M_max_demand_kN','reference_max_demand_kN_common_six')]:close(q[a],p[b]);checked+=1
 for a,b in [('D_controls_differ','D_two_controls_differ'),('M_controls_differ','reference_two_controls_differ_common_six'),('M_D_max_controls_differ','max_demand_input_changed_between_M_D')]:assert q[a]==(p[b]=='True');checked+=1
prod_t={(x['Story'],x['Case'],x['Axis']):x for x in read(str((P/'native-device-layer-timing-24.csv').relative_to(R)))}
for q in timing:
 p=prod_t[q['Story'],q['Case'],q['Axis']]
 for a,b in [('QT_peak_kN','QT_peak_kN'),('tQT_s','t_QT_peak_s'),('QD_peak_kN','QD_abs_peak_kN'),('tQD_s','t_QD_peak_s'),('QD_at_QT_kN','QD_signed_at_QT_peak_kN'),('timing_ratio_percent','abs_QD_at_QT_peak_over_QD_abs_peak_percent')]:close(q[a],p[b]);checked+=1
prod_geo={x['Story']:x for x in read(str((G/'layout-by-story-11.csv').relative_to(R)))}
for story,z in gby.items():
 p=prod_geo[story]
 for a,b in [('n','count_total'),('X','X_only'),('Y','Y_only')]:assert z[a]==int(p[b]);checked+=1
 for a,b in [(z['zlow'],'lower_z_m'),(z['zhigh'],'upper_z_m'),(min(z['lengths']),'length_min_m'),(max(z['lengths']),'length_max_m'),(min(z['angles']),'inclination_min_deg'),(max(z['angles']),'inclination_max_deg')]:close(a,p[b]);checked+=1
assert before=={s:sha(R/s) for s in sources}
result={'audited_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'method':'Independent stdlib CSV + math implementation; production algorithms unread; old frozen inputs read first; production small tables compared only after frozen status confirmed.','source_hashes':before,'geometry_count':88,'stories_with8_X4_Y4':11,'geometry_max_abs_differences':geomax,'paired72_matches_reviewed168':True,'D_min_and_max_controls_differ_conditional':sum(x['D_controls_differ'] for x in controls),'M_min_and_max_controls_differ_common_six':sum(x['M_controls_differ'] for x in controls),'M_D_max_demand_control_changes':sum(x['M_D_max_controls_differ'] for x in controls),'physical_above_M_count':sum(float(x['Pphysical_kN'])>float(x['P3_kN']) for x in peaks),'physical_below_M_count':sum(float(x['Pphysical_kN'])<float(x['P3_kN']) for x in peaks),'D_B_conditional_reduction_range_percent':[min(100*(1-float(x['Pphysical_kN'])/float(x['P0_kN'])) for x in peaks),max(100*(1-float(x['Pphysical_kN'])/float(x['P0_kN'])) for x in peaks)],'controls':controls,'Story8_timing':[x for x in timing if x['Story']=='Story8'],'nP_max_abs_residual_kN':maxprojerr,'sum8_max_abs_residual_kN':maxsumerr,'producer_table_fields_compared':checked,'must':0,'limitations':['D/B reduction is conditional until the pairing role resolves input and model comparability; actual absolute demand is native own-model output.','Three labelled inputs with X/Y orientations are not six independent earthquakes.','QD=sum nP is upper J structural internal resisting term, opposite to external force; unknown native cut inclusion means no physical QS subtraction.','Story5 X two smallest conditional reductions are only about0.018pp apart; do not overclaim rank robustness.','Current small-table audit is not a new blind test, new ODE or physical experiment.']}
(H/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (H/'independent-controls-24.csv').open('x',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(controls[0]));w.writeheader();w.writerows(controls)
print(json.dumps({k:result[k] for k in ['geometry_count','D_min_and_max_controls_differ_conditional','M_min_and_max_controls_differ_common_six','M_D_max_demand_control_changes','producer_table_fields_compared','nP_max_abs_residual_kN','sum8_max_abs_residual_kN','must']},ensure_ascii=False))
