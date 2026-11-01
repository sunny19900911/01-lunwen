from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
source=O.parent/'R007/shw4_baseline_prediction_then_two_targets.py'
text=source.read_text(encoding='utf-8')
changes=[('SHW4X','RH4X'),('61c7165f08156aaef3af39dab94832b89772c60517d5a4444d74add79cb936d8','2354441c71c1bf4e714c26d43af7b103c443419be8578bf775c47466a604cae5'),('2951','2501'),('t[-1]==59','t[-1]==50'),('15:34:56','15:43:56'),('15:42:56','15:51:56'),('15:46:56','15:55:56'),('15:49:56','15:58:56'),("near1pct_local_peak_count=sum(amp[n]>=P0[j]*(1-near_tol) and n not in active for n in local)","near1pct_local_peak_count=int(sum(amp[n]>=P0[j]*(1-near_tol) and n not in active for n in local))")]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
target=O/'rh4_baseline_prediction_then_two_targets.py'
with target.open('x',encoding='utf-8') as f:f.write(text)
def bind(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
with (O/'algorithm-reuse-provenance.json').open('x',encoding='utf-8') as f:json.dump(dict(source=bind(source),target=bind(target),changes='case/source hash/N/span/start/deadlines only; NumPy near-count explicitly cast to int fixes prior final-console print error; numerical algorithm and thresholds unchanged'),f,ensure_ascii=False,indent=2);f.write('\n')
