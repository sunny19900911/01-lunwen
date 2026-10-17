from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,difflib,re
H=Path(__file__).resolve().parent;P=H.parents[4];ROOT=P.parents[1]
W=P/'research/roles/writing/maxwell-session004/compact-paper-v003'
def read(p):return Path(p).read_text(encoding='utf-8')
def obj(p):return json.loads(read(p))
def rec(p):
    p=Path(p);assert p.suffix.lower() not in ['.png','.svg','.pdf','.npz','.xlsx']
    x=p.read_bytes();return {'path':str(p),'bytes':len(x),'sha256':hashlib.sha256(x).hexdigest()}
def dump(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
def ck(n,x,d=None):checks.append({'name':n,'pass':bool(x),'detail':d})
author=obj(W/'input-freeze.json');paths=[P/'manuscript/maxwell-paper-compact-v002.md',P/'manuscript/maxwell-paper-compact-v003.md']+[W/n for n in ['input-freeze.json','freeze.json','evidence-map.json','validation.json','report.md','v002-to-v003.diff']]
paths += [Path(x['path']) for x in author['sources'] if Path(x['path']).suffix.lower() not in ['.png','.svg','.pdf','.npz','.xlsx']]
paths += [Path(x['manifest']['path']) for x in author['protected_prior_packages']]
paths += [P/'research/roles/novelty/maxwell-session004/R022-Correia-Maxwell-prior-art-review/report.md',P/'research/roles/experiments/maxwell-session004/R024-C025-figure-review/report.md',P/'research/roles/novelty/maxwell-session004/R021-engineering-validation-plan-review/report.md']
paths=list(dict.fromkeys(paths));inputs=[rec(p) for p in paths]
dump('input-rules-R026.json',{'started_at':'2026-10-18T04:15:41+08:00','deadline':'2026-10-18T04:22:41+08:00','snapshot_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'inputs':inputs,'scope':'text delta/source integration only; no PDF/images/arrays read or hashed, no scientific calculation/render/solver/search; PNG identity inherited from root/current review'})
a=(P/'manuscript/maxwell-paper-compact-v002.md').read_bytes();b=(P/'manuscript/maxwell-paper-compact-v003.md').read_bytes()
ck('v003_expected_SHA',hashlib.sha256(b).hexdigest()=='8c92fc07944df70491931733530902b7bd4e2d577b508fe5004741dcade06095')
al,bl=a.decode().splitlines(keepends=True),b.decode().splitlines(keepends=True)
ops=[x for x in difflib.SequenceMatcher(None,al,bl,autojunk=False).get_opcodes() if x[0]!='equal']
ck('only_version_replace_three_insertions',[x[0] for x in ops]==['replace','insert','insert','insert'] and ops[0][1:3]==(2,3))
back=bl.copy()
for _,i,j,k,l in reversed(ops):back[k:l]=al[i:j]
ck('reverse_bytes_exact',''.join(back).encode()==a,hashlib.sha256(''.join(back).encode()).hexdigest())
aa,bb=a.decode(),b.decode()
ck('abstract_exact',aa.split('## 摘要\n\n')[1].split('## 1 ')[0]==bb.split('## 摘要\n\n')[1].split('## 1 ')[0])
ck('headings_exact',re.findall(r'^## .*$',aa,re.M)==re.findall(r'^## .*$',bb,re.M))
tables=lambda t:re.findall(r'(?m)(?:^\|.*\|\n)+',t)
forms=lambda t:re.findall(r'(?ms)^\$\$\n.*?^\$\$',t)
ck('two_tables_all_bytes',len(tables(aa))==len(tables(bb))==2 and tables(aa)==tables(bb))
ck('three_display_formulas_all_bytes',len(forms(aa))==len(forms(bb))==3 and forms(aa)==forms(bb))
for prefix in ['第一类为近单位主体','C026令外力','C025/C027及其推论依赖','C031仅检验']:
    ck('protected_paragraph:'+prefix,next(x for x in aa.splitlines() if x.startswith(prefix))==next(x for x in bb.splitlines() if x.startswith(prefix)))
ck('no_C036_R028_in_draft','C036' not in bb and 'R028' not in bb)
table_shapes=[]
for block in tables(bb):
    rows=block.strip().splitlines();widths=[len(x.split('|'))-2 for x in rows]
    ck('table_width',len(rows)==6 and widths==[3]*6);table_shapes.append({'columns':3,'data_rows':4})
links=[]
for label,target in re.findall(r'!?\[([^\]\n]+)\]\(([^)\n]+)\)',bb):
    if target.startswith('https://'):links.append({'label':label,'target':target,'external_not_opened':True})
    else:
        q=(P/'manuscript'/target).resolve();links.append({'label':label,'target':target,'exists':q.is_file()});ck('local_link:'+label,q.is_file())
ck('only_institution_external',[x['target'] for x in links if 'external_not_opened' in x]==['https://fenix.tecnico.ulisboa.pt/downloadFile/3378094857519319/Extend_Paper_Dissipadores_Energia.pdf'])
ck('UTF8_LF_noBOM',not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b)
ck('no_trailing_whitespace',all(x==x.rstrip() for x in bb.splitlines()))
deferred=[]
for e in author['sources']:
    p=Path(e['path'])
    if p.suffix.lower() in ['.png','.svg','.pdf','.npz','.xlsx']:deferred.append({'path':str(p),'declared_sha256':e['sha256'],'not_read_or_hashed_here':True});continue
    r=rec(p);ck('author_source_binding:'+p.name,r['sha256']==e['sha256'] and r['bytes']==e['bytes'])
for e in author['protected_prior_packages']:
    old=e['manifest'];r=rec(old['path']);ck('protected_manifest:'+str(old['path']),r['sha256']==old['sha256'] and r['bytes']==old['bytes'])
for e in obj(W/'freeze.json')['files']:
    r=rec(e['path']);ck('writer_freeze:'+Path(e['path']).name,r['sha256']==e['sha256'] and r['bytes']==e['bytes'])
root=obj(ROOT/'research/sessions/20261017-2109/R019-core-adoption.json')
ck('current_root_figure_admission',root['accepted']['C025_figure']['must_retain_full_caption_and_R011_contract'])
ck('current_root_Correia_boundary',root['accepted']['Correia_source_boundary']['broad_displacement_related_increase_not_unique'] and root['accepted']['Correia_source_boundary']['strict_samecondition_C025_C027_prior_publication']=='unresolved')
for e in deferred:
    key='PNG_SHA' if Path(e['path']).suffix.lower()=='.png' else 'SVG_SHA'
    ck('inherited_media_declared_binding:'+key,e['declared_sha256']==root['accepted']['C025_figure'][key])
for e in inputs:ck('end_unchanged:'+e['path'],rec(e['path'])==e)
assert all(x['pass'] for x in checks),[x for x in checks if not x['pass']]
dump('checks-R026.json',{'checks':checks,'check_count':len(checks),'failed':[],'delta_opcodes':ops,'reverse_recovered_SHA':hashlib.sha256(a).hexdigest(),'table_shapes':table_shapes,'links':links,'deferred_binary_identity':deferred,'protected_manifest_count':len(author['protected_prior_packages']),'underlying_117_entries_not_rehashed':True,'source_scope':'text/JSON/diff identity and semantics only; no media/source PDF/arrays read/hash; source claims inherited from independent reviews/current root'})
print(json.dumps({'checks':len(checks),'failed':0,'inputs':len(inputs),'opcodes':ops,'deferred_media':len(deferred),'links':len(links)},ensure_ascii=False))
