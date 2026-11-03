from pathlib import Path
import hashlib,json,datetime
H=Path(__file__).resolve().parent;R=H.parents[4];O=H/'R002'
names=['Story8-RH4X-SHW7X-native-QT-QD-v003.png','Story8-RH4X-SHW7X-native-QT-QD-v003.svg','native-peak-anchors-2-v003.csv','run-record-v003.json','figure-review.md']
paths=[O/n for n in names]+[H/'plot_story8_native_controls.py',Path(__file__)]
for p in paths:assert p.is_file()
report={'status':'frozen','time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'actual_original_detail_PNG_viewed':True,'approved_plot_version':'v003','read_cached_arrays':2,'all_source_peak_checks_passed':True,'no_new_scientific_model_or_ODE':True,
 'files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in paths]}
p=O/'delivery-manifest.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen':True,'files':len(paths),'approved_png_sha256':report['files'][0]['sha256'],'time':report['time']},ensure_ascii=False))
