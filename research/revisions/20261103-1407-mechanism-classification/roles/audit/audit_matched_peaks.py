from pathlib import Path
import csv, json, math, hashlib, datetime

R=Path('E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/01-lunwen')
H=Path(__file__).resolve().parent
src=R/'research/sessions/20261031-1130/roles/role4/R008/Story5-Story12-top5-other-symmetric-components-72.csv'
states=R/'research/sessions/20261103-0845/roles/audit/R001/independent-story5-four-states.csv'
assert not (H/'matched-time-audit.json').exists()
rows=list(csv.DictReader(src.open(encoding='utf-8-sig',newline='')))
st=list(csv.DictReader(states.open(encoding='utf-8-sig',newline='')))
selected=[r for r in rows if r['Case']=='SHW3X' and r['Story']=='Story5']
assert len(selected)==12
anchors={}
for anchor in ('native5_abspeak','native8_abspeak'):
 a=[r for r in selected if r['anchor']==anchor]
 assert len(a)==6 and sum(int(r['mode_count']) for r in a)==300
 v5=math.fsum(float(r['v5_signed_ref_kN']) for r in a)
 v8=math.fsum(float(r['v8_signed_ref_kN']) for r in a)
 d=v8-v5
 assert abs(d-math.fsum(float(r['delta_v_signed_ref_kN']) for r in a))<1e-9
 mode13=next(r for r in a if r['Mode']=='13')
 others=math.fsum(float(r['delta_v_signed_ref_kN']) for r in a if r['Mode']!='13')
 assert abs(others+float(mode13['delta_v_signed_ref_kN'])-d)<1e-9
 anchors[anchor]={'time_s':float(a[0]['time_s']),'all300_v5':v5,'all300_v8':v8,
  'all300_delta_v8_minus_v5':d,'mode13_v5':float(mode13['v5_signed_ref_kN']),
  'mode13_v8':float(mode13['v8_signed_ref_kN']),
  'mode13_delta':float(mode13['delta_v_signed_ref_kN']),
  'other299_delta':others}
old=anchors['native5_abspeak'];new=anchors['native8_abspeak']
P5=old['all300_v5'];P8=new['all300_v8'];oldtime_reduction=P5-old['all300_v8']
peak_migration=P8-old['all300_v8']
assert abs((P5-P8)-(oldtime_reduction-peak_migration))<1e-9
def state(case,zeta):return next(r for r in st if r['Case']==case and float(r['zeta'])==zeta)
s3a=state('SHW3X',.05);s3b=state('SHW3X',.08)
s4a=state('SHW4X',.05);s4b=state('SHW4X',.08)
comparison={'mode2_SHW4_minus_SHW3_at_own8_peaks':float(s4b['reference_mode2_kN'])-float(s3b['reference_mode2_kN']),
 'mode2_SHW4_own8_minus_own5':float(s4b['reference_mode2_kN'])-float(s4a['reference_mode2_kN']),
 'SHW4_reference_total_own8_minus_own5':float(s4b['reference_at_native_peak_signed_kN'])-float(s4a['reference_at_native_peak_signed_kN'])}
out={'at':datetime.datetime.now().astimezone().isoformat(),'sources':[
 {'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (src,states)],
 'method':'stdlib CSV and math.fsum of five fixed baseline-ranked modes plus remaining295; no ODE, array reading or regression',
 'matched_time_anchors':anchors,'SHW3_reference_peak_identity':{'P5':P5,'P8':P8,
 'old_time_reduction':oldtime_reduction,'peak_migration':peak_migration,'peak_reduction':P5-P8,
 'check_residual':(P5-P8)-(oldtime_reduction-peak_migration)},'comparison':comparison,
 'must':0,'scope':'fixed classical-damping linear reference, not unique native FNA story-force decomposition'}
(H/'matched-time-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (H/'matched-time-anchors.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['anchor',*old.keys()]);w.writeheader()
 for k,v in anchors.items():w.writerow({'anchor':k,**v})
print(json.dumps(out,ensure_ascii=False,indent=2))
