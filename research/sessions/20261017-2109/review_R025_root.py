"""R025: bind reviewed endpoint appendix and bounded plain-language repairs."""
from pathlib import Path
from datetime import datetime
import hashlib,importlib.util,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles';OUT=S/'R025-root-review-v001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists()
 spec=importlib.util.spec_from_file_location('id020',S/'review_R020_integrations.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 checked={}
 adopt=json.loads((S/'C042-adoption-v001.json').read_text('utf-8'))
 for n,d in adopt['checked_identities'].items():assert sha(R/n)==d,n;checked[n]=d
 folders=['ideation/maxwell-session004/R034-continuous-velocity-endpoints','verification/maxwell-session004/R048-continuous-velocity-independent','verification/maxwell-session004/R048-continuous-velocity-independent/post-freeze-comparison','writing/maxwell-session004/continuous-velocity-endpoints-v001','verification/maxwell-session004/R049-continuous-velocity-appendix-integration','literature/maxwell-session004/R032-public-candidate-original','experiments/maxwell-session004/R027-plain-summary-engineering-review','novelty/maxwell-session004/R029-plain-summary-contribution-review','novelty/maxwell-session004/R030-handoff-plain-and-priorart-review']
 for name in folders:
  d=B/name
  for p in d.iterdir():
   if p.is_file():
    assert p.stat().st_size<1000000
    if p.suffix=='.json':m.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
    checked[p.relative_to(R).as_posix()]=sha(p)
 expected={
  B/folders[4]/'report.md':'ac1a7f080880de0a1b04f1d40f972d6e8b40df008e9927a6cad48bd75f1a2888',
  B/folders[5]/'report.md':'28156e10e013fd1d890595161c8169dd8fd4df940655f42739a12c72ebaa88a3',
  B/folders[6]/'report.md':'12cd8fa05f8d7db6836a0a3e2ebef93a4c5b5cf9249f95f16a0a0d5a15dcd841',
  B/folders[7]/'report.md':'9a0b968050c128140f11d6d5ae59970a66f9db963a973218e6059f7572bcba10',
  B/folders[8]/'report.md':'ad5c912c264eec947145213e5acb0aaf135ed0421d1bb1e9a56c0ed9fc501654'}
 for p,h in expected.items():assert sha(p)==h,p
 paper=R/'papers/damping-output-boundaries/manuscript/maxwell-continuous-velocity-endpoints-v001.md'
 assert sha(paper)=='3de22587466e7546385db5c8109e1ab855fc8124c053e183c50f90e5925cf47f'
 text=paper.read_text('utf-8');assert len(re.findall(r'\$\$.*?\$\$',text,re.S))==6
 assert len(re.findall(r'^## [1-4] ',text,re.M))==4
 assert re.findall(r'\\tag\{([1-6])\}',text)==list('123456')
 old=S/'阶段结论-白话-v001.md';new=S/'阶段结论-白话-v002.md';diff=S/'阶段结论-白话-v002.diff'
 assert sha(old)=='63cce9c7daed2031fb6d67ea6a61a6e617a8539b23baee6d9e6aaf505df9e7fd'
 assert sha(new)=='235f2a3ca00e36706f2cab97f14bcd6b943de6f400835af21c68d5fd40c7c521'
 spec=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py');dm=importlib.util.module_from_spec(spec);spec.loader.exec_module(dm)
 dm.check_diff(diff,old,new)
 for p in [paper,old,new,diff,S/'同条件排重-结论表-v001.md',S/'C042-adoption-v001.json']:
  checked[p.relative_to(R).as_posix()]=sha(p)
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'patch_pairs':{diff.relative_to(R).as_posix():[old.relative_to(R).as_posix(),new.relative_to(R).as_posix()]},
 'root_entire_text_read':['C042 author/independent/post proofs in previous round','new endpoint appendix, six formulas/four sections','R049 full integration report','old plain-summary engineering and contribution reports, new summary real diff','prior-art table and R032403 report','R030 final bounded review'],
 'endpoint_appendix_review':'Faithful C042 integration: signed-Psi lower rigidity, upper time-equality rigidity, bounded continuous ramps with exact terminalh by comparison/IVT, L1/cost convergence, T=tmin exception;0<alpha<=1 and no endpointvelocity/acceleration/terminaldelta closure/building feedback. No full openD/fixedDpeakset/priority extension.',
 'plain_summary_review':'Original v001 contribution must=1 preserved; v002 explicitalpha/endpoint/time domain plus88x6 addresses finding/P3. Other original full engineering/contribution scope retained. R030 separately reviews new text and prior-art table; master independently reads entire changed prose.',
 'prior_art_review':'Known classical tools and generalized Maxwell displacement increase separated from still-unresolved exact publication. R032 one403 toolfetch,0body/metadata; no source-specific relevance/coverage exclusion or novelty upgrade.',
 'original_science_or_arrays_executed':False,'immutable_output':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'equations':6,'plain_diff':1}))
if __name__=='__main__':main()
