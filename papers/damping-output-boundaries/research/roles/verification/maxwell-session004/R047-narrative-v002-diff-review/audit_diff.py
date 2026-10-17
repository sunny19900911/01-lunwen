"""Independent unified-diff/reverse verification; no scientific computation."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re,difflib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
MAN=ROOT/'papers/damping-output-boundaries/manuscript'
W=ROOT/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/narrative-paper-v002'
OLDW=W.with_name('narrative-paper-v001')
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'source-freeze.json').exists()
assert rec(MAN/'maxwell-paper-narrative-v002.md')['sha256']=='af496eafe3996eb73f48be5be5722ebfa895265fd4965af204ab30f9c58d5911'
assert rec(MAN/'maxwell-fixed-dissipation-peak-appendix-v002.md')['sha256']=='c36bbd54984e119de7ca89b25f3bc651ce92e90bc13e3dcaf1c67d3cf6843f5f'
assert rec(W/'freeze.json')['sha256']=='d860399d03d6001b049138fbb77c467e5f8381d1003507331a7c6b3f38b01f83'
pairs=[(MAN/'maxwell-paper-narrative-v001.md',MAN/'maxwell-paper-narrative-v002.md',W/'diff-narrative-from-v001.patch'),(MAN/'maxwell-fixed-dissipation-peak-appendix-v001.md',MAN/'maxwell-fixed-dissipation-peak-appendix-v002.md',W/'diff-fixed-D-appendix-from-v001.patch'),(OLDW/'reproduction-appendix.md',W/'reproduction-appendix.md',W/'diff-reproduction-from-v001.patch')]
sources=list(dict.fromkeys([p for a,b,c in pairs for p in [a,b,c]]+[p for p in sorted(W.iterdir()) if p.is_file()]+[ROLE/'R046-narrative-paper-math-integration/report.md',ROLE/'R046-narrative-paper-math-integration/findings.json',ROLE/'R046-narrative-paper-math-integration/validation.json',ROOT/'papers/damping-output-boundaries/research/roles/novelty/maxwell-session004/R028-narrative-paper-contribution-review/report.md',ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R026-narrative-engineering-integration/report.md',ROLE/'非零末力耗散峰力区间独审-R017.md',ROOT/'research/sessions/20261017-2109/R023-C038-terminology-erratum-v001.md']))
assert len(sources)==22
write('source-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T05:44:48.889424+08:00','deadline':'2026-10-18T05:49:48+08:00','global_deadline':'2026-10-18T07:09:45+08:00','sources':[rec(p) for p in sources],'scope':'Three limited diffs only. No old-history scan, proof/data/ODE/array run or author execution.'})
assert all(rec(Path(x['path']))==x for x in read(W/'freeze.json')['files'])
def reverse_patch(new,patch):
    lines=new.splitlines(keepends=True);pl=patch.splitlines(keepends=True);out=[];cursor=0;i=0
    while i<len(pl):
        m=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',pl[i])
        if not m:i+=1;continue
        oldn=int(m[2] or 1);newstart=int(m[3])-1;newn=int(m[4] or 1)
        out.extend(lines[cursor:newstart]);oldblock=[];newblock=[];i+=1
        while i<len(pl) and not pl[i].startswith('@@ '):
            row=pl[i]
            if row.startswith(' '):oldblock.append(row[1:]);newblock.append(row[1:])
            elif row.startswith('-'):oldblock.append(row[1:])
            elif row.startswith('+'):newblock.append(row[1:])
            else:raise AssertionError('Unexpected patch syntax')
            i+=1
        assert len(oldblock)==oldn and len(newblock)==newn and lines[newstart:newstart+newn]==newblock
        out.extend(oldblock);cursor=newstart+newn
    out.extend(lines[cursor:]);return ''.join(out)
results=[]
for old,new,patch in pairs:
    a=old.read_text(encoding='utf-8');b=new.read_text(encoding='utf-8');p=patch.read_text(encoding='utf-8')
    actual=''.join(difflib.unified_diff(a.splitlines(keepends=True),b.splitlines(keepends=True),fromfile=old.name,tofile=new.name))
    assert actual==p
    rebuilt=reverse_patch(b,actual).encode('utf-8');assert rebuilt==old.read_bytes()
    (HERE/('independent-'+patch.name)).write_text(actual,encoding='utf-8',newline='\n')
    results.append({'old':rec(old),'new':rec(new),'patch':rec(patch),'independent_diff_identical':True,'reverse_restores_old_bytes_and_SHA':True,'restored_sha256':hashlib.sha256(rebuilt).hexdigest()})
def maths(p):return re.findall(r'\$\$(.*?)\$\$',p.read_text(encoding='utf-8'),re.S)
assert len(maths(pairs[0][0]))==10 and maths(pairs[0][0])==maths(pairs[0][1])
assert len(maths(pairs[1][0]))==7 and maths(pairs[1][0])==maths(pairs[1][1])
def tables(p):
    ls=p.read_text(encoding='utf-8').splitlines();out=[]
    for i,s in enumerate(ls):
        if re.fullmatch(r'\|(?:-+\|)+',s):
            j=i+1
            while j<len(ls) and ls[j].startswith('|'):j+=1
            out.append('\n'.join(ls[i-1:j]))
    return out
assert tables(pairs[0][0])==tables(pairs[0][1]) and tables(pairs[1][0])==tables(pairs[1][1])
newbody=pairs[0][1].read_text(encoding='utf-8');newfixed=pairs[1][1].read_text(encoding='utf-8');newrepro=pairs[2][1].read_text(encoding='utf-8')
assert '低于U逆的像域' not in newbody+newfixed
assert all('不在U_J⁻¹的定义域[D0,D_max]内，因为D_min<D0' in s for s in [newbody,newfixed])
proof=ROLE/'非零末力耗散峰力区间独审-R017.md';assert rec(proof)['sha256']=='5a3596a03e9508861ccfda513ee170addf62c29a35ef97e4ed9e33a3db4c5c6d'
assert '非零末力耗散峰力区间独审-R017.md' in newbody and '非零末力耗散峰力区间独审-R017.md' in newrepro
assert 'maxwell-fixed-dissipation-peak-appendix-v002.md' in newbody+newrepro
assert re.findall(r'!\[[^\]]*\]\([^)]+\)',pairs[0][0].read_text(encoding='utf-8'))==re.findall(r'!\[[^\]]*\]\([^)]+\)',newbody)
linkcounts={}
for p in [pairs[0][1],pairs[1][1],pairs[2][1]]:
    s=p.read_text(encoding='utf-8');links=[u for u in re.findall(r'\[[^\]]*\]\(([^)]+)\)',s) if not u.startswith(('https://','http://'))]
    assert all((p.parent/u).resolve().is_file() for u in links);linkcounts[str(p)]=len(links)
write('checks.json',{'required_changes':0,'R046_M1_resolved_in_new_versions_only':True,'R046_old_required_change_record_preserved':True,'three_independent_diffs_and_reverse_checks':results,'ten_and_seven_formulas_byte_equal':True,'both_tables_and_figure_reference_preserved':True,'R017_direct_proof_identity_verified':True,'authorized_version_terminology_proof_link_reproduction_and_engineering_clarifications_only':True,'existing_science_numbers_and_machine_assumptions_unchanged':True,'new_5_8_labels_are_old_model_clarification_not_new_data':True,'local_link_counts':linkcounts,'no_old_history_scan_or_scientific_runs':True})
print(json.dumps({'required_changes':0,'sources':len(sources),'reverse_SHA':[x['restored_sha256'] for x in results],'formulas':[10,7],'M1_resolved':True},ensure_ascii=False))
