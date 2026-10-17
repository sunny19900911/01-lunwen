from pathlib import Path
from datetime import datetime
import ast, hashlib, json, re

ROOT=Path(__file__).resolve().parents[6]
P=ROOT/'papers/damping-output-boundaries'
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
draft=P/'manuscript/theory-draft-v001.md'
text=draft.read_text(encoding='utf-8')
assert sha(P/'manuscript/working-draft-v009.md')=='76dc25e88faae9c95ea411cee58d56371d526eee9f00b59e7d7ef3f0ff3ba028'
assert '\r' not in text and not re.search(r'[ \t]+$',text,re.M)
assert len(re.findall(r'^## [1-5] ',text,re.M))==5
assert len(re.findall(r'^!\[',text,re.M))==2
assert len(re.findall(r'^\[[1-7]\] ',text,re.M))==7
tags=re.findall(r'\\tag\{([^}]+)\}',text)
assert len(tags)==len(set(tags))==31
assert not re.search(r'（[EF][0-9]+）|附录[EF]',text)
for n in range(1,10): assert str(n) in tags
assert '式（6）—（7）' in text and '式（8）—（9）' in text
assert '其Result3式（11）' in text
assert '印刷页521—522、式（9）' in text
assert '第3—4页式（4）—（6）' in text
local=[]
for target in re.findall(r'\]\(([^\n]+?)\)',text):
    target=target.strip('<>')
    if target.startswith(('https://','http://','#')): continue
    path=Path(target) if re.match(r'^[A-Za-z]:',target) else draft.parent/target
    assert path.is_file(),str(path)
    local.append(target)
old=json.loads((P/'manuscript/figure-map-v009.json').read_text(encoding='utf-8'))
selected=old['selected_figures'][:2]
for fig in selected:
    for asset in fig['sources']:
        p=ROOT/asset['path']
        assert sha(p)==asset['sha256'] and p.stat().st_size==asset['bytes']
evidence={
 'C006-v2':('§2 / 附录A','research/roles/verification/reply-C006-refinement.md'),
 'C011':('§2 广义输出短段 / 图1','research/roles/verification/EEXP004-bound-audit.json'),
 'C016-v2':('§3.1、3.3 / §4.2、表1、图2','research/roles/verification/addendum-V011-general-topcut.md'),
 'C017':('§3.2 / 附录B','research/roles/verification/appendix-V011-low-damping-IVT.md'),
 'C018':('§4.1 / 附录C','research/roles/verification/detuning-boundary-review.md'),
 'C019':('§5.2 / 附录D','research/roles/verification/network-realizability-proof.md'),
 'E010':('§4.2、表1、图2','experiments/round010_unit_topcut_envelopes/six_envelope_sampled_peaks.csv'),
 'prior-art':('§1、5.1 / 参考文献','research/roles/literature/manuscript-citation-review-v009.md')}
# Discover the existing V006 refinement report rather than inventing a filename.
if not (P/evidence['C006-v2'][1]).exists():
    matches=list((P/'research/roles/verification').glob('*006*'))
    raise AssertionError('update C006 report path from actual source: '+str(matches))
claims=[]
for claim,(section,path) in evidence.items():
    file=P/path
    assert file.is_file(),str(file)
    claims.append({'claim':claim,'location':section,'source':info(file),'status':'previously-reviewed; no new research promoted'})
mapping={'draft':info(draft),'base':info(P/'manuscript/working-draft-v009.md'),'selected_figures':selected,'evidence_map':claims,'author_pngs_actually_viewed':True,'excluded_from_theory_main':['native ETABS engineering observations C004','grouped proxy diagnostic C015','old high-frequency/input-rescaling/compactness branches','free generalized-output slow-envelope branch','new unreviewed detuning quantitative claims','E012 approximate root values'],'new_evidence_claimed':False}
mp=P/'manuscript/theory-figure-evidence-map-v001.json'
mp.write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
ast.parse((HERE/'build_theory_draft.py').read_text(encoding='utf-8'))
ast.parse(Path(__file__).read_text(encoding='utf-8'))
checks={'checked_at':datetime.now().astimezone().isoformat(),'main_sections':5,'figures':2,'references':7,'formula_tags':tags,'local_links_checked':local,'figure_asset_hashes_checked':4,'source_v009_unchanged':True,'scripts_ast_passed':True,'no_experiment_rerun':True,'no_new_proof_claimed':True}
(HERE/'validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'draft':info(draft),'map':info(mp),'checks':{'sections':5,'figures':2,'references':7,'tags':len(tags),'links':len(local)}},ensure_ascii=False))
