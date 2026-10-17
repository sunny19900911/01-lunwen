"""R019 root exact input identity, inherited-bound and minimal manuscript checks."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime
import difflib,hashlib,importlib.util,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
FOLDERS=[
'ideation/maxwell-session004/R028-finite-observation-neighbor',
'verification/maxwell-session004/R039-finite-observation-neighbor-review',
'novelty/maxwell-session004/R023-contribution-grading',
'writing/maxwell-session004/compact-paper-v003',
'literature/maxwell-session004/R026-compact-v003-integration-review',
]
OLD_CLAIMS='8140c0690e9195809cb3b1e2d718e48149bff92e5a0d824d66a99063517c3a30'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def verify(obj,parent,checked,mapped):
 if isinstance(obj,list):
  for item in obj:verify(item,parent,checked,mapped)
 elif isinstance(obj,dict):
  if 'sha256' in obj and any(k in obj for k in ['path','file','name']):
   name=obj.get('path',obj.get('file',obj.get('name')))
   if isinstance(name,str):
    p=Path(name)
    if not p.is_absolute():p=(R if name.startswith(('papers/','research/')) else parent)/p
    p=p.resolve()
    if p==S/'claims.md' and obj['sha256']==OLD_CLAIMS:
     mapped.append({'original':p.relative_to(R).as_posix(),'recorded_sha256':OLD_CLAIMS,'resolved_to':'research/sessions/20261017-2109/R019-source-snapshots/claims-read-before-R019.md'})
     p=S/'R019-source-snapshots/claims-read-before-R019.md'
    if p.is_relative_to(R) and '/local-cache/' not in p.as_posix() and p.suffix.lower() in {'.md','.json','.py','.csv','.txt','.diff'}:
     assert p.stat().st_size<1000000
     assert sha(p)==obj['sha256'],(p,obj['sha256'])
     if 'bytes' in obj:assert p.stat().st_size==obj['bytes'],p
     checked[p.relative_to(R).as_posix()]=sha(p)
  for item in obj.values():verify(item,parent,checked,mapped)
def main():
 checked={};mapped=[]
 for name in FOLDERS:
  d=B/name;assert d.is_dir(),d
  for p in d.iterdir():
   if p.is_file() and p.suffix=='.json':verify(read(p),d,checked,mapped)
 old=R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v002.md'
 new=old.with_name('maxwell-paper-compact-v003.md')
 assert sha(old)=='02ae657ba2d49cf270cacd2a0860fc8d44d041d8dd5b7a643d0efd47caeaa890'
 assert sha(new)=='8c92fc07944df70491931733530902b7bd4e2d577b508fe5004741dcade06095'
 a,b=old.read_text('utf-8').splitlines(keepends=True),new.read_text('utf-8').splitlines(keepends=True)
 ops=difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes()
 changed=[op for op in ops if op[0]!='equal']
 assert sum(op[0]=='replace' for op in changed)==1 and sum(op[0]=='insert' for op in changed)==3 and not any(op[0]=='delete' for op in changed)
 replace=next(op for op in changed if op[0]=='replace');assert replace[1:]==(2,3,2,3)
 rebuilt=[]
 for tag,i,j,k,l in ops:
  if tag=='equal':rebuilt+=b[k:l]
  elif tag=='replace':rebuilt+=a[i:j]
  else:assert tag=='insert'
 assert ''.join(rebuilt).encode('utf-8')==old.read_bytes()
 ta,tb=''.join(a),''.join(b)
 formulas=lambda text:re.findall(r'\$\$.*?\$\$',text,re.S)
 assert len(formulas(ta))==3 and formulas(ta)==formulas(tb)
 def tables(text):
  result=[];current=[]
  for line in text.splitlines():
   if line.startswith('|'):current.append(line)
   elif current:result.append('\n'.join(current));current=[]
  if current:result.append('\n'.join(current))
  return result
 assert len(tables(ta))==2 and tables(ta)==tables(tb)
 spec=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 diff=mod.check_diff(B/'writing/maxwell-session004/compact-paper-v003/v002-to-v003.diff',old,new)
 upper=Q('1.34634002134');lower=Q('8.805443996444');gap=lower-upper
 assert gap==Q('7.459103975104') and gap>Q('7.45') and gap/2==Q('3.729551987552')
 assert sha(S/'R019-source-snapshots/claims-read-before-R019.md')==OLD_CLAIMS
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,'historical_mutable_input_mappings':mapped,
 'historical_source_reason':'R023 honestly records live claims changed;exact original read SHA recovered from existing b80475bc HEAD commit,not modify role freeze/current ledger. Fifteen actual proof/source anchors unchanged.',
 'root_full_content_read':['R028 entire proof/checks plusR039 proof/checks','R023 entire contributiongrading andvalidation,only recommendation notfinaltopic','compact-v003 fulltext anddiff plusR026 finalintegration report'],
 'root_proof_review':'Each L_i rederived using fullstate radius and explicit metric change;bounded power derivative and cumulative integrals;quantifier/min/measurementerror set assumptions separately checked. Classical tools/no priority.',
 'finite_window_inherited_gap':str(gap),'finite_window_half_gap':str(gap/2),
 'manuscript_checks':{'one_version_replace_three_insertions':True,'exact_reverse_recovery_v002':True,'three_formulas_unchanged':True,'two_tables_unchanged':True,'diff':diff},
 'scope':'Conditional finite observation error-set information boundary;reviewed v003 minimalintegration;contributiongrading recommendation only. Not physicalquantization,knownB impossibility orengineeringnovelty.',
 'source_programs_executed':False,'arrays_or_originals_read':False}
 (S/'R019-root-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'historical_claim_mappings':len(mapped),'gap':str(gap)}))
if __name__=='__main__':main()

