"""Independent exact scalar illustration only; no engineering array or response."""
from pathlib import Path
from fractions import Fraction
import json, hashlib
O=Path(__file__).resolve().parent
F=json.loads((O/'input-freeze.json').read_text(encoding='utf-8'))
for s in F['sources']:
    assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
x=F['hypothetical_scalar_example']
p0=x['baseline'];pc=x['candidate']
penv0=max(p0.values());penv=max(pc.values())
de={e:1-Fraction(pc[e],p0[e]) for e in p0}
denv=1-Fraction(penv,penv0)
assert denv>=min(de.values())
assert denv>=Fraction(1,10) and not all(d>=Fraction(1,10) for d in de.values())
r={'identity':'hypothetical scalar illustration, not engineering data',
   'baseline_envelope':penv0,'candidate_envelope':penv,
   'envelope_improvement_fraction':str(denv),'envelope_improvement_percent':float(100*denv),
   'per_input_improvement_fraction':{e:str(d) for e,d in de.items()},
   'per_input_improvement_percent':{e:float(100*d) for e,d in de.items()},
   'envelope_pass_10pct':True,'each_input_pass_10pct':False,
   'baseline_controlling_input':[e for e in p0 if p0[e]==penv0],
   'candidate_controlling_input':[e for e in pc if pc[e]==penv],
   'no_baseline_derivative_inferred_from_endpoints':True}
with (O/'hypothetical-example-results.json').open('x',encoding='utf-8',newline='\n') as h:
    json.dump(r,h,ensure_ascii=False,indent=2);h.write('\n')
print(json.dumps(r,ensure_ascii=False))
