
"""R020 targeted root review: immutable identities, inverse domains, manuscript constants."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime
import ast,hashlib,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
FOLDERS=[
'ideation/maxwell-session004/R029-fixed-dissipation-peak-inverse',
'verification/maxwell-session004/R040-fixed-D-inverse-independent',
'verification/maxwell-session004/R040-fixed-D-inverse-independent/post-freeze-comparison',
'literature/maxwell-session004/R027-nonzero-terminal-dissipation-prior-art',
'novelty/maxwell-session004/R024-finite-observation-appendix-review',
'writing/maxwell-session004/finite-observation-appendix-v001',
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(obj,parent,checked):
 if isinstance(obj,list):
  for item in obj:verify(item,parent,checked)
 elif isinstance(obj,dict):
  name=obj.get('repo_relative',obj.get('path',obj.get('file',obj.get('name'))))
  digest=obj.get('sha256')
  if isinstance(name,str) and isinstance(digest,str) and re.fullmatch('[a-f0-9]{64}',digest):
   p=Path(name)
   if not p.is_absolute():p=(R if name.startswith(('papers/','research/')) else parent)/p
   p=p.resolve()
   if p.is_relative_to(R) and '/local-cache/' not in p.as_posix() and p.suffix in {'.md','.json','.py','.csv','.txt','.diff'}:
    assert p.exists(),p
    assert p.stat().st_size<1000000,p
    assert sha(p)==digest,(p,digest)
    if 'bytes' in obj:assert p.stat().st_size==obj['bytes'],p
    checked[p.relative_to(R).as_posix()]=digest
  for item in obj.values():verify(item,parent,checked)
def main():
 checked={}
 for name in FOLDERS:
  d=B/name
  for p in d.iterdir():
   if p.is_file() and p.suffix=='.json':verify(json.loads(p.read_text('utf-8-sig')),d,checked)
   if p.is_file() and p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'))
 expected={
 B/'ideation/maxwell-session004/R029-fixed-dissipation-peak-inverse/report.md':'c6cc612de443a58642a20d7cdb10a054fb00d051d827a33f2f44b1ac0fcdc910',
 B/'verification/maxwell-session004/R040-fixed-D-inverse-independent/report.md':'3773b2bb6f8556af5f49dd1ec945f6d929a9e938fd692b7417e220a26d8c5294',
 B/'verification/maxwell-session004/非零末力耗散峰力区间独审-R017.md':'5a3596a03e9508861ccfda513ee170addf62c29a35ef97e4ed9e33a3db4c5c6d',
 R/'papers/damping-output-boundaries/manuscript/maxwell-finite-observation-appendix-v001.md':'d55f09c509c2da354eb009567b3516afdb995d7127b03a0a69877a5725720752'}
 for p,digest in expected.items():assert sha(p)==digest;checked[p.relative_to(R).as_posix()]=digest
 # Independent tiny exact algebra; general proof is a separate human/root derivation.
 k,V,g,P,Pp,slack=Q(7,3),Q(5),Q(2),Q(11),Q(13),Q(3,7)
 taup=(1/(V-g)+1/(V+g))/k
 assert taup==2*V/(k*(V*V-g*g))>0
 assert P*taup+Pp*slack-P*taup==Pp*slack>0
 assert P*taup-P*taup==0
 assert Q('8.805443996444')-Q('1.34634002134')==Q('7.459103975104')
 assert Q('7.459103975104')/2==Q('3.729551987552')
 manuscript=(R/'papers/damping-output-boundaries/manuscript/maxwell-finite-observation-appendix-v001.md').read_text('utf-8')
 assert len(re.findall(r'\$\$.*?\$\$',manuscript,re.S))==6
 assert len(re.findall(r'\\tag\{[1-6]\}',manuscript))==6
 lines=manuscript.splitlines();table_start=lines.index('| 观测量i | Li(H) |')
 assert len(lines[table_start:table_start+8])==8
 assert all(line.startswith('|') and line.count('|')==3 for line in lines[table_start:table_start+8])
 assert not lines[table_start+8].startswith('|')
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'root_full_read':['R029 proof/checks.py','R040 independent proof/checks.py','old nonzero-terminal R017 proof','C037 appendix full text and six constants','R027 prior-art report (freeze/independent source grade pending)'],
 'root_independent_math_review':[
 'tau strictly increases to infinity; feasibility and shortest-time branch handled before inversion',
 'Lprime=P*tauprime; Uprime=Pprime*(T-tau), strictly positive on nondegenerate interior despite zero endpoint slope',
 'L image [Dmin,Dmax], U image [U(h),Dmax]; below-U(h) branch must use h or clip inverse argument, domain outside D remains empty',
 'Inequality intersection equivalent to interval; every M has dwell=(D-L)/P and waiting=T-tau-dwell, both nonnegative, so exact attainment inherited',
 'Positive h, fixed terminal sign, terminal delta free; W shift only; no continuous velocity/closed-delta extension',
 'C037 all six Li and explicit metric term match accepted R019; H/scales/eta precede chosen a, common error record needs no new physical system; actual B missing'],
 'tiny_exact_checks':'Algebra cancellation and inherited decimal gap/half-gap; no scientific source executed, no inverse/integrals or arrays',
 'independent_appendix_review':'R024 entire report read; integration only 0must, no source reproof; final adoption is separate',
 'new_claim_candidate':'M-C038 fixed true dissipation exact peak set; classic monotone inversion, exact prior publication unknown'}
 (S/'R020-core-root-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'appendix_equations':6,'appendix_data_rows':6}))
if __name__=='__main__':main()

