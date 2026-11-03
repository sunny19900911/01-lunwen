from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
H=Path(__file__).resolve().parent;R=H.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
summary=json.loads((H/'response-summary.json').read_text(encoding='utf-8'))
for item in summary['inputs']:
 p=R/item['relative'];assert sha(p)==item['sha256']
rows=read(H/'three-model-common-six-records-72.csv');assert len(rows)==72
controls=read(H/'common-six-control-records-24.csv');assert len(controls)==24
timing=read(H/'native-device-layer-timing-24.csv');assert len(timing)==24
old384=read(R/'research/sessions/20261019-2045/roles/data/R002-native-horizontal/device-contributions-384.csv')
old48=read(R/'research/sessions/20261020-1844/roles/role4/R005-Story8-device-at-QT-peak-48.csv')
lookup={(r['Story'],r['Case'],r['Axis'],r['Link']):r for r in old384}
maxres=0.0
for r in old48:
 q=lookup[r['Story'],r['Case'],r['Axis'],r['Link']]
 maxres=max(maxres,abs(float(r['qJ_resisting_at_QT_peak_kN'])-float(q['horizontal_at_QT_peak_kN'])))
 assert abs(float(r['qJ_resisting_at_QT_peak_kN'])-float(r['P_at_QT_peak_kN'])*float(r['n_axis']))<1e-10
assert maxres<1e-9
envelope=read(H/'common-six-peak-envelope-24.csv')
for q in envelope:
 for f in ['P_B_kN','P_M_kN','P_D_kN']:
  expected=max(float(r[f])for r in rows if r['Axis']==q['Axis']and r['Story']==q['Story'])
  assert float(q[f])==expected
checks={'baseline_reference_exact_match_to_reviewed168':True,'all_72_unique_keys':True,'24_groups_with_3_inputs':True,
 '24_layer_cases_8_devices_complete':True,'8_device_sum_vs_frozen_QD_max_abs_residual_kN':max(abs(float(r['sum8_device_QD_at_QT_peak_check_residual_kN']))for r in timing),
 'Story8_old48_vs_old384_same_device_QD_max_residual_kN':maxres,'plot24rows_exact_envelope_check':True,
 'figure_actual_viewed_at_original_detail':True,'figure_readability':'two panels; labels and complete axes readable; 1800x1110 pixels',
 'prior_plot_attempt':'First attempt asserted a fixed 12000kN axis limit before producing any output; changed axis to data-dependent 3000kN ceiling, then ran once successfully. No data or calculation changed.',
 'scope':'Arithmetic and frozen-source consistency, not independent solver rerun or cross-model pairing certificate'}
p=H/'response-checks.json';assert not p.exists();p.write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=H/'response-report.md'
with report.open('a',encoding='utf-8',newline='\n')as f:
 f.write('\n## 配图\n\ncommon-six-three-model-peak-envelope.png及SVG为共有六工况三模型沿层绝对峰包络。每个方向均在RH4、SHW4、SHW7三输入中逐层取最大值，保留实际包络控制输入于24行CSV；图示不是同一时刻沿层分布。最终PNG已实际原尺寸查看，坐标、图例及曲线可读。\n')
files=[p for p in sorted(H.iterdir())if p.is_file() and p.name!='delivery-manifest.json']
d={'status':'frozen','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'source_files_unchanged':True,'checks':checks,
 'files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files]}
(H/'delivery-manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'frozen','files':len(files),'source_arrays_read':0,'source_workbooks_read':0,'max_device_reuse_residual_kN':maxres,'finish':d['at']},ensure_ascii=False))
