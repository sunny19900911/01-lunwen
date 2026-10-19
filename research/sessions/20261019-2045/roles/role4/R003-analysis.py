"""New full-height existing-state profiles only. No workbook/solver/fit."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,csv,hashlib,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent
SESSION=O.parents[1];REPO=SESSION.parents[2]
DATA=SESSION/'roles/data';DESIGN=SESSION/'roles/design'
CORE=REPO.parent/'W5-重燃双塔连体/research/maxwell-20261017/experiments/R001/core-cache'
META=CORE.parents[2]/'roles/experiments/metadata/metadata_inventory.json'
START=datetime.fromisoformat('2026-10-19T13:33:53+00:00')
def now():return datetime.now(timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x):
 p=O/('R003-'+name);assert not p.exists(),p;p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=lambda v:v.item())+'\n',encoding='utf-8')
def csvout(name,rows):
 p=O/('R003-'+name);assert not p.exists(),p
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def rcsv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
inputs=[CORE/'manifest.json',CORE/'Story_Forces.npz',CORE/'Story_Drifts.npz',CORE/'Base_Reactions.npz',META,DATA/'R001-existing-cache-index.json',DATA/'R001-link-geometry-88.csv',DATA/'local-cache/new-full-geometry/point_coordinates.csv',DATA/'R002-native-horizontal/device-contributions-384.csv',DATA/'R002-native-horizontal/manifest.json',DESIGN/'R002-three-position-drafts.csv']
bindings=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in inputs]
save('protocol-input-freeze.json',{'utc':now().isoformat(),'start_utc':START.isoformat(),'deadline_utc':(START+timedelta(minutes=12)).isoformat(),'code_sha256':sha(Path(__file__)),'inputs':bindings,'scope':'existing-state full-height Bottom shear and native drift peaks; 3 families separately by X/Y; candidate native motion availability; no new Excel/solver/fit/rigid approximation','peak_definition':'max(abs(native saved output)); original sign/time/source row preserved; drift is a sparse spatial envelope, not fixed-point signal; no missing-value fill','control_definition':'largest observed peak only; no stiffness/capacity/safety ranking; upper four floors separately highlighted','candidate_motion_contract':'need native endpoint displacements/velocities both ends XYZ on same full case grid; donor Link U1 does not supply candidate pair history'})
cm=json.loads((CORE/'manifest.json').read_text(encoding='utf-8'));index=json.loads((DATA/'R001-existing-cache-index.json').read_text(encoding='utf-8'));meta=json.loads(META.read_text(encoding='utf-8'))
assert sha(CORE/'manifest.json')==index['core_manifest_sha256'] and cm['sha256']==index['source_sha256']==meta['sha256']
sf=cm['tables']['Story Forces'];sd=cm['tables']['Story Drifts'];br=cm['tables']['Base Reactions']
assert sf['headers'][sf['headers'].index('VX')]=='VX' and sf['units'][sf['headers'].index('VX')]=='kN'
points=rcsv(DATA/'local-cache/new-full-geometry/point_coordinates.csv');height={}
for p in points:
 if p['story'].startswith('Story'):height[p['story']]=max(height.get(p['story'],-np.inf),float(p['Z_m']))
assert len(points)==3416 and len(height)==12
shears=[];drifts=[];checks=[];sk={};dk={};base={}
def check(n,b):checks.append({'check':n,'pass':bool(b)});assert b,n
def peak(a,t,srow):
 i=int(np.argmax(abs(a)));return {'peak_abs':float(abs(a[i])),'signed_at_peak':float(a[i]),'peak_t_s':float(t[i]),'source_row_at_peak':int(srow[i])}
with np.load(CORE/br['cache'],allow_pickle=False) as bz,np.load(CORE/sf['cache'],allow_pickle=False) as sz,np.load(CORE/sd['cache'],allow_pickle=False) as dz:
 for k,g in br['groups'].items():base[g['keys']['Output Case']]=bz[k][:,br['columns'].index('Time')]
 for k,g in sf['groups'].items():
  keys=g['keys'];story=keys['Story'];case=keys['Output Case'];a=sz[k];t=a[:,sf['columns'].index('Time')]
  check(k+':shear-full-base-grid',np.array_equal(t,base[case]) and np.isfinite(a).all() and np.all(np.diff(t)>0));check(k+':Bottom',keys['Location']=='Bottom')
  for axis in ('X','Y'):
   pk=peak(a[:,sf['columns'].index('V'+axis)],t,a[:,sf['columns'].index('SourceRow')]);r={'Story':story,'height_m':height[story],'Case':case,'wave_family':case[:-1],'input_direction':case[-1],'Axis':axis,'input_main_axis':case[-1]==axis,'Location':'Bottom','QT_peak_kN':pk['peak_abs'],'QT_signed_at_peak_kN':pk['signed_at_peak'],'QT_peak_t_s':pk['peak_t_s'],'source_row_at_peak':pk['source_row_at_peak'],'n_points':len(t),'t0_s':float(t[0]),'t1_s':float(t[-1]),'time_grid_matches_base':True,'scope':'native Story Forces; Link inclusion/sign not yet certified; not isolated main-structure shear'}
   shears.append(r);sk[story,case,axis]=r
 for k,g in sd['groups'].items():
  keys=g['keys'];story=keys['Story'];case=keys['Output Case'];axis=keys['Direction'];a=dz[k];t=a[:,sd['columns'].index('Time')];bt=base[case]
  check(k+':drift-finite-unique-subset',np.isfinite(a).all() and np.all(np.diff(t)>0) and np.all(np.isin(np.round(t,8),np.round(bt,8))))
  pk=peak(a[:,sd['columns'].index('Drift')],t,a[:,sd['columns'].index('SourceRow')]);r={'Story':story,'height_m':height[story],'Case':case,'wave_family':case[:-1],'input_direction':case[-1],'Axis':axis,'input_main_axis':case[-1]==axis,'Drift_peak_ratio':pk['peak_abs'],'Drift_signed_at_peak':pk['signed_at_peak'],'Drift_peak_t_s':pk['peak_t_s'],'source_row_at_peak':pk['source_row_at_peak'],'native_n_points':len(t),'base_n_points':len(bt),'native_grid_coverage_fraction':len(t)/len(bt),'t0_s':float(t[0]),'t1_s':float(t[-1]),'scope':'native recorded Story Drift peak; sparse spatial envelope; no fixed endpoint reconstruction/no missing-value fill'}
  drifts.append(r);dk[story,case,axis]=r
profiles=[]
for s,case,axis in sk:
 if case[-1]!=axis:continue
 a=sk[s,case,axis];b=dk[s,case,axis]
 profiles.append({'Story':s,'height_m':height[s],'Case':case,'wave_family':case[:-1],'Axis':axis,'QT_peak_kN':a['QT_peak_kN'],'QT_peak_t_s':a['QT_peak_t_s'],'QT_source_row':a['source_row_at_peak'],'Drift_peak_ratio':b['Drift_peak_ratio'],'Drift_peak_t_s':b['Drift_peak_t_s'],'Drift_source_row':b['source_row_at_peak'],'drift_native_grid_coverage_fraction':b['native_grid_coverage_fraction']})
profiles.sort(key=lambda r:(r['Case'],int(r['Story'][5:])))
control=[]
for case in sorted(base):
 group=[r for r in profiles if r['Case']==case];q=max(group,key=lambda r:r['QT_peak_kN']);d=max(group,key=lambda r:r['Drift_peak_ratio']);upper=[r for r in group if 8<=int(r['Story'][5:])<=11];uq=max(upper,key=lambda r:r['QT_peak_kN']);ud=max(upper,key=lambda r:r['Drift_peak_ratio'])
 control.append({'Case':case,'wave_family':case[:-1],'Axis':case[-1],'QT_control_Story':q['Story'],'QT_max_kN':q['QT_peak_kN'],'Drift_control_Story':d['Story'],'Drift_max_ratio':d['Drift_peak_ratio'],'upper4_QT_control_Story':uq['Story'],'upper4_QT_max_kN':uq['QT_peak_kN'],'upper4_Drift_control_Story':ud['Story'],'upper4_Drift_max_ratio':ud['Drift_peak_ratio'],'scope':'observed response peak control; no capacity/safety or improved-placement claim'})
env=[]
for s in sorted(height,key=lambda x:int(x[5:])):
 for axis in ('X','Y'):
  group=[r for r in profiles if r['Story']==s and r['Axis']==axis];q=max(group,key=lambda r:r['QT_peak_kN']);d=max(group,key=lambda r:r['Drift_peak_ratio'])
  env.append({'Story':s,'height_m':height[s],'Axis':axis,'QT_envelope_kN':q['QT_peak_kN'],'QT_control_family':q['wave_family'],'Drift_envelope_ratio':d['Drift_peak_ratio'],'Drift_control_family':d['wave_family']})
drafts=rcsv(DESIGN/'R002-three-position-drafts.csv');devices=rcsv(DATA/'R002-native-horizontal/device-contributions-384.csv');geom=rcsv(DATA/'R001-link-geometry-88.csv');knownpairs={(g['I_Point'],g['J_Point']) for g in geom};availability=[];donor=[];layercompare=[]
for c in drafts:
 pair=(c['candidate_I'],c['candidate_J']);available=pair in knownpairs
 check(c['plan']+':candidate-pair-not-existing-link',not available)
 availability.append({'plan':c['plan'],'direction':c['direction'],'donor_story':c['donor_story'],'donor_link':c['donor_link'],'original_I':c['original_I'],'original_J':c['original_J'],'target_story':c['target_story'],'candidate_I':pair[0],'candidate_J':pair[1],'new_endpoint_geometry_exists':all(any(p['point']==pt for p in points) for pt in pair),'native_candidate_displacement_full_cases_available':False,'native_candidate_velocity_full_cases_available':False,'candidate_relative_motion_comparison_possible':False,'donor_original_Link_P_U1_cases':6,'reason':'No native endpoint displacement table in known source inventory; joint absolute velocity table truncated and no certified endpoint histories in handoff caches. Existing other Link motion/CM envelopes cannot substitute.','next_step':'tomorrow native candidate/original I,J XYZ displacement and velocity + same-grid cases or direct model comparison; verify global axes and connectivity'})
 for r in devices:
  if r['Story']==c['donor_story'] and r['Link']==c['donor_link'] and r['Axis']==c['direction']:
   donor.append({'plan':c['plan'],'Story':r['Story'],'Link':r['Link'],'Case':r['Case'],'input_main_axis':r['input_main_axis'],'Axis':r['Axis'],'P_peak_kN':r['P_peak_kN'],'U1_peak_total_mm':r['U1_peak_total_mm'],'horizontal_peak_abs_kN':r['horizontal_peak_abs_kN'],'scope':'existing original Link native response only; not new endpoint motion or moved-device prediction'})
 for family in ['RH4','SHW4','SHW7']:
  case=family+c['direction'];target=dk[c['target_story'],case,c['direction']];old=dk[c['donor_story'],case,c['direction']]
  layercompare.append({'plan':c['plan'],'Case':case,'Axis':c['direction'],'donor_story':c['donor_story'],'target_story':c['target_story'],'donor_StoryDrift_peak_ratio':old['Drift_peak_ratio'],'target_StoryDrift_peak_ratio':target['Drift_peak_ratio'],'target_over_donor_StoryDrift_peak':target['Drift_peak_ratio']/old['Drift_peak_ratio'],'scope':'two native floor spatial-envelope peaks; not candidate endpoint motion/damper effect'})
check('output-coverage',len(shears)==144 and len(drifts)==144 and len(profiles)==72 and len(control)==6 and len(availability)==3 and len(donor)==18)
check('no-joint-displacement-table-in-source-inventory','Joint Displacements' not in meta['sheets']);check('joint-velocity-source-truncated',meta['sheets']['Joint Velocities - Absolute']['reaches_excel_row_limit'])
for n,r in [('story-force-peaks-144.csv',shears),('story-drift-peaks-144.csv',drifts),('main-axis-profiles-72.csv',profiles),('main-axis-control-6.csv',control),('axis-envelopes-24.csv',env),('candidate-motion-availability-3.csv',availability),('original-device-demands-18.csv',donor),('candidate-layer-envelope-comparison-9.csv',layercompare)]:csvout(n,r)
plt.rcParams['font.family']='DejaVu Sans';fig,axs=plt.subplots(2,2,figsize=(10,9),sharey=True)
for col,axis in enumerate(('X','Y')):
 for fam,color in zip(['RH4','SHW4','SHW7'],['#1b6a8f','#c97c26','#9862a7']):
  pp=[r for r in profiles if r['Case']==fam+axis];h=[r['height_m'] for r in pp]
  axs[0,col].plot([r['QT_peak_kN']/1000 for r in pp],h,'o-',label=fam,color=color,ms=4)
  axs[1,col].plot([r['Drift_peak_ratio']*1000 for r in pp],h,'o-',color=color,ms=4)
 for row in (0,1):
  axs[row,col].axhspan(height['Story8'],height['Story11'],color='#bcc9d1',alpha=.2);axs[row,col].grid(alpha=.22);axs[row,col].set_ylim(0,56);axs[row,col].set_ylabel('Story elevation (m)')
 axs[0,col].set_title(f'{axis} input / {axis} response');axs[0,col].set_xlabel('Native Bottom shear absolute peak (MN)');axs[1,col].set_xlabel('Native recorded drift peak x 1000');axs[0,col].legend(frameon=False)
fig.suptitle('Existing controlled model: three wave families\nShaded: Story8-11; peaks occur at different times',fontsize=13)
fig.tight_layout(rect=(0,0,1,.94));fig.savefig(O/'R003-full-height-profiles.png',dpi=180);plt.close(fig)
save('checks.json',checks)
save('run-result.json',{'finished_utc':now().isoformat(),'start_utc':START.isoformat(),'elapsed_seconds':(now()-START).total_seconds(),'checks':len(checks),'passed':sum(r['pass'] for r in checks),'profile_rows':72,'native_force_rows_read':sf['data_rows'],'native_drift_rows_read':sd['data_rows'],'source_workbooks_read':0,'new_ODE_or_solver_runs':0,'candidate_native_motion_comparisons_available':0,'motion_availability_scope':'known source inventory and frozen handoff caches; no global claim that underlying ETABS model lacks these results','new_story_controls':control,'P3_target_over_donor_drift':[r for r in layercompare if r['plan']=='P3'],'code_sha256':sha(Path(__file__)),'dependencies':{'python':sys.version.split()[0],'numpy':np.__version__,'matplotlib':matplotlib.__version__}})
print(json.dumps({'controls':control,'P3_layer_comparison':[r for r in layercompare if r['plan']=='P3'],'checks':len(checks)},ensure_ascii=False))
