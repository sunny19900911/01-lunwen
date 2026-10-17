"""Freeze read-only inputs, then replay a byte-identical certificate in this round."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
SRC=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R017-addition-witness-certificate'
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
p=json.loads((SRC/'protocol.json').read_text(encoding='utf-8'))
files=list(SRC.iterdir())+[Path(x['path']) for x in p['refs'].values()]
files += [ROOT/'research/sessions/20261017-2109/addition-baseline-analytic-candidate-v001.md']
author=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R020-addition-baseline-proof'
files+=list(author.iterdir())
records=[record(x) for x in files if x.is_file()]
assert next(x['sha256'] for x in records if x['path'].endswith('enclose_addition_witness.py'))=='7d696a7e9f95f007a1bb2ac4cea40b00c464bf100b4ba3ef7ed0783d83f6a9aa'
assert next(x['sha256'] for x in records if x['path'].endswith('summary_r017.json'))=='1b0454f443d1c27466e00bd40ece92deb6e259edf7ea82da38cd25e1708e4d7c'
assert hashlib.sha256((author/'report.md').read_bytes()).hexdigest()=='5be93e50da1b8ea2612916819527984e8b81c7486c114b400b4e0c72eeaac633'
(HERE/'source-before.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
dst=HERE/'isolated-run';dst.mkdir(exist_ok=False)
for name in ['enclose_addition_witness.py','protocol.json']:shutil.copyfile(SRC/name,dst/name)
argv=[sys.executable,'-B','-X','utf8',str(dst/'enclose_addition_witness.py')]
r=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
(HERE/'replay-stdout.txt').write_text(r.stdout,encoding='utf-8',newline='\n')
(HERE/'replay-stderr.txt').write_text(r.stderr,encoding='utf-8',newline='\n')
(HERE/'replay-invocation.json').write_text(json.dumps({'argv':argv,'cwd':str(ROOT),'exit_code':r.returncode},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert r.returncode==0,r.stderr
assert all(record(Path(x['path']))==x for x in records)
print(json.dumps({'replay_exit':r.returncode,'inputs_frozen':len(records),'sources_unchanged':True}))
