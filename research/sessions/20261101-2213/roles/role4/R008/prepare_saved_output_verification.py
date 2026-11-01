from pathlib import Path
O=Path(__file__).resolve().parent
source=O.parent/'R007/verify_saved_outputs_report_and_freeze.py'
text=source.read_text(encoding='utf-8').split("table=['# SHW4X",1)[0]
assert 'verification.json' in text and 'delivery-manifest.json' not in text
text=text.replace('posterior-rank-inversion-pairs-3.csv','posterior-rank-inversion-pairs-4.csv').replace('point-insufficient-miss-cases-2.csv','point-insufficient-miss-cases-1.csv').replace('original_producer_exit=1','original_producer_exit=0').replace("original_failure_stage='only final console json.dumps of NumPy int64 after every numeric output and results.json had been saved'","original_failure_stage=None")
text+="\nprint(json.dumps(verification,ensure_ascii=False,indent=2))\n"
with (O/'verify_rh4_saved_outputs.py').open('x',encoding='utf-8') as f:f.write(text)
