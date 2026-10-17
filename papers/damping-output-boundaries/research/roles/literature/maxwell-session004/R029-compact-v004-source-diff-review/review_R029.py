from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re,difflib
H=Path(__file__).resolve().parent;P=H.parents[4];ROOT=P.parents[1];R=ROOT/'research/sessions/20261017-2109';W=P/'research/roles/writing/maxwell-session004/compact-paper-v004'
def obj(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def rec(p):
    p=Path(p);assert p.suffix.lower() not in ['.png','.svg','.pdf','.npz','.xlsx']
    d=p.read_bytes();return {'path':str(p),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
def write(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
author=obj(W/'input-freeze.json');checks=[]
def ck(n,x,d=None):checks.append({'name':n,'pass':bool(x),'detail':d})
paths=[P/'manuscript/maxwell-paper-compact-v003.md',P/'manuscript/maxwell-paper-compact-v004.md']+[W/n for n in ['freeze.json','input-freeze.json','evidence-map.json','report.md','validation.json','diff-from-v003.patch']]
paths += [Path(e['path']) for e in author['direct_sources']+author['protected_manifests']]
paths += [R/n for n in ['R021-adoption.json','R021-provenance-addendum.json','R021-root-review.json','R021-C039-root-review.json','R021-illustration-adoption.json']]
paths += [P/'research/roles/literature/maxwell-session004/R028-convolution-holder-source/source-manifest-R028.json',P/'research/roles/ideation/maxwell-session004/R030-dissipation-modal-output-bound/report.md',P/'research/roles/verification/maxwell-session004/R042-dissipation-modal-bound-independent/post-freeze-comparison/report.md',P/'manuscript/maxwell-fixed-dissipation-peak-appendix-v001.md',P/'research/roles/experiments/maxwell-session004/R025-fixed-D-two-peak-example/report.md',P/'research/roles/novelty/maxwell-session004/R025-fixed-D-example-review/report.md']
paths=list(dict.fromkeys(paths));inputs=[rec(p) for p in paths]
write('input-rules-R029.json',{'started_at':'2026-10-18T05:07:17+08:00','deadline':'2026-10-18T05:15:17+08:00','snapshot_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'inputs':inputs,'scope':'text/source delta integration only, math separate role2; no search,original PDF/images/arrays,author scientific execution or shared/Git edits'})
a=(P/'manuscript/maxwell-paper-compact-v003.md').read_bytes();b=(P/'manuscript/maxwell-paper-compact-v004.md').read_bytes();aa=a.decode();bb=b.decode();al=aa.splitlines(keepends=True);bl=bb.splitlines(keepends=True)
ck('v004_expected_SHA_and_bytes',len(b)==14566 and hashlib.sha256(b).hexdigest()=='1c68afccee269708ac857adb74b98b94433deccbae6d972da4e239ac4191643b')
ck('writer_freeze_expected_SHA',rec(W/'freeze.json')['sha256']=='77efe1bf7ba048fa6f92477d16d3f3a8e7b008484ddf387f0f7256717d76acb5')
ops=[x for x in difflib.SequenceMatcher(None,al,bl,autojunk=False).get_opcodes() if x[0]!='equal']
ck('only_four_allowed_changes',[x[0] for x in ops]==['replace','replace','insert','insert'] and ops[0][1:3]==(2,3) and ops[1][1:3]==(6,7))
back=bl.copy()
for _,i,j,k,l in reversed(ops):back[k:l]=al[i:j]
ck('reverse_v003_bytes_exact',''.join(back).encode()==a)
generated=''.join(difflib.unified_diff(al,bl,fromfile='maxwell-paper-compact-v003.md',tofile='maxwell-paper-compact-v004.md'))
ck('actual_unified_patch_exact',generated==(W/'diff-from-v003.patch').read_text(encoding='utf-8'))
ck('headings_exact',re.findall(r'^## .*$',aa,re.M)==re.findall(r'^## .*$',bb,re.M))
ck('sections1to3_exact',aa.split('## 1 问题')[1].split('## 4 ')[0]==bb.split('## 1 问题')[1].split('## 4 ')[0])
tables=lambda x:re.findall(r'(?m)(?:^\|.*\|\n)+',x)
forms=lambda x:re.findall(r'(?ms)^\$\$\n.*?^\$\$',x)
ck('two_original_tables_all_bytes',len(tables(aa))==len(tables(bb))==2 and tables(aa)==tables(bb))
af,bf=forms(aa),forms(bb);ck('original_tag1_2_3_exact_and_only_new_tag4',len(af)==3 and len(bf)==4 and af==bf[:3] and '\\tag{4}' in bf[3])
ck('tag4_outside_aligned','\\end{aligned}\\tag{4}' in bf[3])
for prefix in ['第一类为近单位主体','![C025','图1','C026令外力','C025/C027及其推论依赖','C031仅检验','Correia的作者扩展论文','具体执行见']:
    ck('protected_paragraph:'+prefix,next(x for x in aa.splitlines() if x.startswith(prefix))==next(x for x in bb.splitlines() if x.startswith(prefix)))
for t in tables(bb):ck('table_3columns4datarows',len(t.strip().splitlines())==6 and all(len(x.split('|'))-2==3 for x in t.strip().splitlines()))
links=[]
for label,target in re.findall(r'!?\[([^\]\n]+)\]\(([^)\n]+)\)',bb):
    if target.startswith('https://'):links.append({'label':label,'target':target,'external_not_opened':True})
    else:
        q=(P/'manuscript'/target.split('#')[0]).resolve();ok=q.is_file();links.append({'label':label,'target':target,'exists':ok});ck('link:'+label,ok)
ck('only_recorded_external',[e['target'] for e in links if 'external_not_opened' in e]==['https://fenix.tecnico.ulisboa.pt/downloadFile/3378094857519319/Extend_Paper_Dissipadores_Energia.pdf','https://math.mit.edu/~lguth/Math156/notes/25.pdf#page=3'])
ck('no_early_illustration_as_draft_authority','R021-illustration-adoption' not in bb and 'R021-adoption.json' in bb)
current=obj(R/'R021-root-review.json');early=obj(R/'R021-illustration-adoption.json');add=obj(R/'R021-provenance-addendum.json');adopt=obj(R/'R021-adoption.json')
ck('formal_adoption_expected_SHA',rec(R/'R021-adoption.json')['sha256']=='4372ebec3613c4e5f7f9640c36633965c348ecbe50f27d4a33b883c6b769f530')
ck('affected_early_identity',rec(R/'R021-illustration-adoption.json')['sha256']==add['affected_adoption_sha256'])
ck('old_review_link_only_historical',early['review_record']['sha256']==add['superseded_link']['sha256'] and add['superseded_link']['sha256']!=rec(R/'R021-root-review.json')['sha256'])
ck('current_root_review_addendum_binding',rec(R/'R021-root-review.json')['sha256']==add['current_root_review']['sha256'])
oldanchors=early['checked_identities'];newanchors=current['checked_small_file_identities']
ck('54_scientific_anchors_subset_of_current62',len(oldanchors)==54 and len(newanchors)==62 and all(newanchors.get(k)==v for k,v in oldanchors.items()))
for e in adopt['review_records']:ck('formal_review_record_binding:'+e['path'],rec(R/e['path'])['sha256']==e['sha256'])
for e in author['direct_sources']+author['protected_manifests']:
    actual=rec(e['path']);ck('writer_input_binding:'+str(e['path']),actual['sha256']==e['sha256'] and actual['bytes']==e['bytes'])
for e in obj(W/'freeze.json')['files']:
    actual=rec(e['path']);ck('writer_delivery_binding:'+Path(e['path']).name,actual['sha256']==e['sha256'] and actual['bytes']==e['bytes'])
ck('UTF8_LF_noBOM_no_trailing',not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and all(x==x.rstrip() for x in bb.splitlines()))
for e in inputs:ck('end_unchanged:'+e['path'],rec(e['path'])==e)
assert all(x['pass'] for x in checks),[x for x in checks if not x['pass']]
write('checks-R029.json',{'checks':checks,'check_count':len(checks),'failed':[],'delta_opcodes':ops,'reverse_recovered_v003_SHA':hashlib.sha256(a).hexdigest(),'links':links,'old_manifests_count':len(author['protected_manifests']),'old133_underlying_entries_not_rehashed':True,'PNG_pixels_or_binary_identity_not_reverified':True,'old_QA_bytes_not_recovered':True,'math_not_reproved':True})
print(json.dumps({'passed':len(checks),'failed':0,'inputs':len(inputs),'delta':ops,'links':len(links)},ensure_ascii=False))
