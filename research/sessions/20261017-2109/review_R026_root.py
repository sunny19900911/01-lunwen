"""R026 root integration review: explicit small files and finite metadata, no rerun."""
from pathlib import Path
from datetime import datetime
import ast,csv,difflib,hashlib,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
PACKAGES=[
'ideation/maxwell-session004/R035-continuous-cost-image',
'verification/maxwell-session004/R050-continuous-cost-image-independent',
'verification/maxwell-session004/R051-continuous-cost-image-integration',
'experiments/maxwell-session004/R028-session-receipt-audit',
'novelty/maxwell-session004/R031-final-handoff-scope',
'novelty/maxwell-session004/R032-final-handoff-v002',
'writing/maxwell-session004/continuous-cost-image-v001']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=S/'R026-root-review-v001.json';assert not out.exists()
 ids=dict(json.loads((S/'C043-adoption-v001.json').read_text('utf-8'))['checked_identities'])
 def add(p):
  p=p.resolve();name=p.relative_to(R).as_posix();raw=p.read_bytes()
  assert p.suffix in {'.md','.json','.csv','.diff','.py'} and len(raw)<1000000 and 'local-cache' not in name
  t=raw.decode('utf-8-sig')
  if p.suffix=='.json':json.loads(t)
  if p.suffix=='.py':ast.parse(t)
  if p.suffix=='.csv':
   rows=list(csv.reader(t.splitlines()));assert rows and all(len(x)==len(rows[0]) for x in rows)
  ids[name]=hashlib.sha256(raw).hexdigest()
 def records(obj,parent):
  if isinstance(obj,dict):
   name=obj.get('path',obj.get('file'))
   if isinstance(name,str) and isinstance(obj.get('sha256'),str):
    p=Path(name)
    if not p.is_absolute():p=R/name if (R/name).exists() else parent/name
    add(p);assert sha(p)==obj['sha256'],name
    if 'bytes' in obj:assert p.stat().st_size==obj['bytes'],name
   for value in obj.values():records(value,parent)
  elif isinstance(obj,list):
   for value in obj:records(value,parent)
 for pkg in PACKAGES:
  for p in (B/pkg).iterdir():
   if p.is_file():add(p)
 post=B/PACKAGES[1]/'post-freeze-comparison'
 for p in post.iterdir():
  if p.is_file():add(p)
 # Only finite input/output metadata; no full history or protected-manifest recursion.
 for rolepkg,filename,keys in [
 (PACKAGES[3],'sourcefreeze.json',['source_files','outputs']),
 (PACKAGES[4],'input-freeze.json',['inputs']),
 (PACKAGES[4],'validation.json',['files']),
 (PACKAGES[5],'input-freeze.json',['inputs']),
 (PACKAGES[5],'validation.json',['files']),
 (PACKAGES[6],'freeze.json',['files']),
 (PACKAGES[6],'input-freeze.json',['direct_sources']),
 (PACKAGES[6],'evidence-map.json',['sources']),
 ]:
  p=B/rolepkg/filename;j=json.loads(p.read_text('utf-8'))
  for key in keys:records(j[key],p.parent)
 v=B/PACKAGES[2]
 for n in ['source-freeze.json','validation.json']:
  p=v/n;records(json.loads(p.read_text('utf-8')),p.parent)
 draft=R/'papers/damping-output-boundaries/manuscript/maxwell-continuous-cost-image-v001.md'
 add(draft);assert sha(draft)=='23acaade3bf7b6916f526a9182e7c669368e8888fec966d951ea601cd5173734'
 t=draft.read_text('utf-8')
 assert re.findall(r'\\tag\{(\d+)\}',t)==['1','2','3','4','5']
 assert len(re.findall(r'^## ',t,re.M))==4
 for n in ['C043-adoption-v001.json','C043-root-review-v001.json','continuous-velocity-cost-image-protocol-v001.md',
 'continuous-cost-image-root-candidate-v001.md','continuous-cost-image-root-core-v001.json',
 'R026-receipt-root-audit-v001.json','R026-receipt-csv-comparison-v001.json','R026-handoff-v002-repair.json',
 '最终交付说明-候选-v001.md','最终交付说明-候选-v002.md','最终交付说明-候选-v002.diff',
 'R026-frozen-table-display-addendum.md','R026-R025-preflight-completion-addendum.json','R026-scheduler-preclose-audit.json']:
  add(S/n)
 old=(S/'最终交付说明-候选-v001.md').read_text('utf-8')
 new=(S/'最终交付说明-候选-v002.md').read_text('utf-8')
 diff=(S/'最终交付说明-候选-v002.diff').read_text('utf-8')
 assert diff==''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='最终交付说明-候选-v001.md',tofile='最终交付说明-候选-v002.md'))
 assert '给定实测力后的条件一致性检查' in old and '给定实测力后的条件一致性检查' not in new
 assert '给定ETABS导出力后的条件一致性检查' in new
 repair=json.loads((S/'R026-handoff-v002-repair.json').read_text('utf-8'))
 assert repair['old_sha256']==sha(S/'最终交付说明-候选-v001.md') and repair['new_sha256']==sha(S/'最终交付说明-候选-v002.md')
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 assert sha(R/'papers/damping-output-boundaries/manuscript/maxwell-paper-narrative-v002.md')=='af496eafe3996eb73f48be5be5722ebfa895265fd4965af204ab30f9c58d5911'
 result={'at':datetime.now().astimezone().isoformat(),'checked_identities':ids,'finite_identity_count':len(ids),
 'manual_full_read':['R035/R050 full proofs and separate postcomparison with independent root note','C043 supplement all four sections/five equations','R051 limited integration report','Original handoff plus current exact repair diff; R031 one required wording fix and R032 zero-must limited follow-up','R028 receipt report/statistics; own all25 normalization and local ancestry, exact224 CSV comparisons'],
 'mathematical_integration':'Root read equations, quantifiers, proof route, T branches and no-extension clauses; static formula/link/hash checks ancillary only',
 'original_handoff_v001':'Historical one required evidence-level wording fix preserved, not accepted unchanged',
 'handoff_v002':'ETABS export wording fixed; C043 only reviewed scope; new supplement still labeled pending at handoff freeze; actual receipt scope not full cutoff state',
 'no_proof_or_machine_certification_upgrade':True,'no_new_ODE_arrays_reextract_or_search':True,
 'old_161_writer_and_98_novelty_history_entries':'Not re-recursively reviewed; only explicitly listed current sources and outputs',
 'publication_and_engineering':'Exact publication coverage unknown; actual layout/model-matched target validation unresolved',
 'checkpoint_not_final_close':True}
 out.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
 print(json.dumps({'pass':True,'identities':len(ids),'equations':5,'sections':4}))
if __name__=='__main__':main()
