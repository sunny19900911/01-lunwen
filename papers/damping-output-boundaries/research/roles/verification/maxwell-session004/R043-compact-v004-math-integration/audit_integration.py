"""Independent text diff, source identity and static integration QA only."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re,difflib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
MANUSCRIPT=ROOT/'papers/damping-output-boundaries/manuscript'
NEW=MANUSCRIPT/'maxwell-paper-compact-v004.md';OLD=MANUSCRIPT/'maxwell-paper-compact-v003.md'
WRITING=ROOT/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/compact-paper-v004'
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'source-freeze.json').exists()
assert rec(NEW)['bytes']==14566 and rec(NEW)['sha256']=='1c68afccee269708ac857adb74b98b94433deccbae6d972da4e239ac4191643b'
assert rec(WRITING/'freeze.json')['sha256']=='77efe1bf7ba048fa6f92477d16d3f3a8e7b008484ddf387f0f7256717d76acb5'
inputs=read(WRITING/'input-freeze.json')
sources=[NEW]+[WRITING/n for n in ['freeze.json','input-freeze.json','diff-from-v003.patch','evidence-map.json','validation.json','report.md']]+[Path(x['path']) for x in inputs['direct_sources']]+[ROLE/'R042-dissipation-modal-bound-independent/validation.json',ROLE/'R042-dissipation-modal-bound-independent/post-freeze-comparison/comparison-freeze.json']
assert len(sources)==20 and len({str(x.resolve()) for x in sources})==20
write('source-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T05:07:16.522594+08:00','deadline':'2026-10-18T05:15:16+08:00','global_deadline':'2026-10-18T07:09:45+08:00','sources':[rec(p) for p in sources],'scope':'Static integration only; no primary download, new proof, ODE, arrays, numeric integration or source execution.'})
assert all(rec(Path(x['path']))==x for x in read(WRITING/'freeze.json')['files'])
for x in inputs['direct_sources']:
    actual=rec(Path(x['path']));assert all(actual[k]==x[k] for k in ['path','bytes','sha256'])
assert all(rec(Path(x['path']))==x for x in inputs['protected_manifests'])
new=NEW.read_text(encoding='utf-8');old=OLD.read_text(encoding='utf-8')
diff=''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile=OLD.name,tofile=NEW.name))
(HERE/'independent-diff.patch').write_text(diff,encoding='utf-8',newline='\n')
assert diff==(WRITING/'diff-from-v003.patch').read_text(encoding='utf-8')
start=new.index('还可将真实耗散预算与目标空间核合并。')
end=new.index('## 5 讨论与结论',start)
restored=new[:start]+new[end:]
start=restored.index('单器件的[已审固定D附录]')
end=restored.index('具体执行见[',start)
restored=restored[:start]+restored[end:]
rlines=restored.splitlines(keepends=True);olines=old.splitlines(keepends=True)
rlines[2]=olines[2];rlines[6]=olines[6]
assert ''.join(rlines).encode('utf-8')==OLD.read_bytes()
oldmath=re.findall(r'\$\$(.*?)\$\$',old,re.S);newmath=re.findall(r'\$\$(.*?)\$\$',new,re.S)
assert len(oldmath)==3 and len(newmath)==4 and newmath[:3]==oldmath
assert re.findall(r'\\tag\{(\d+)\}',new)==list('1234')
def tables(s):
    lines=s.splitlines();out=[]
    for i,line in enumerate(lines):
        if re.fullmatch(r'\|(?:-+\|)+',line):
            block=[lines[i-1],line];j=i+1
            while j<len(lines) and lines[j].startswith('|'):block.append(lines[j]);j+=1
            out.append('\n'.join(block))
    return out
assert tables(new)==tables(old) and len(tables(new))==2
oldimages=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',old)
assert oldimages==re.findall(r'!\[[^\]]*\]\(([^)]+)\)',new) and len(oldimages)==1
links=re.findall(r'\[[^\]]*\]\(([^)]+)\)',new)
local=[x for x in links if not x.startswith(('https://','http://'))]
assert all((NEW.parent/x).resolve().is_file() for x in local)
for p in [NEW,OLD]:
    b=p.read_bytes();assert b'\r' not in b and not b.startswith(b'\xef\xbb\xbf') and b.endswith(b'\n')
    assert all(line==line.rstrip() for line in b.decode('utf-8').splitlines())
prior_path=ROLE/'R042-dissipation-modal-bound-independent/validation.json'
assert rec(prior_path)['sha256']=='e7aa95c6c3980998ab2975e1fcffbe91ffdeee83995a3eb84666005e90d840cd'
prior=read(prior_path)
records=prior['frozen_R001_R041']+[{'run_file':str(prior_path.relative_to(ROLE)).replace('\\','/'),'sha256':rec(prior_path)['sha256'],'outputs_verified':len(prior['outputs'])}]
total=0
for x in records:
    p=ROLE/x['run_file'];assert rec(p)['sha256']==x['sha256'];d=read(p)
    outs=d.get('outputs',[d['report']] if 'report' in d else []);assert len(outs)==x['outputs_verified']
    assert all(rec(Path(y['path']))==y for y in outs);total+=len(outs)
assert len(records)==42 and total==166
extra_records=[prior['additional_R040_postcomparison_freeze'],rec(ROLE/'R042-dissipation-modal-bound-independent/post-freeze-comparison/comparison-freeze.json')]
assert extra_records[1]['sha256']=='f2b6ba8a612c3d42d7cef61843aedf34e9b96917839847313d6e2cba9920f31a'
for x in extra_records:
    assert rec(Path(x['path']))==x
    assert all(rec(Path(y['path']))==y for y in read(Path(x['path']))['outputs'])
write('prior-preservation.json',{'frozen_R001_R042':records,'main_records':42,'main_outputs':166,'additional_comparison_freezes':extra_records,'additional_comparison_outputs':6})
write('checks.json',{'required_changes':0,'scope':'Static mathematical transcription and byte preservation, not a new proof or numeric check','direct_inputs':11,'frozen_sources':20,'author_six_file_records_unchanged':True,'writer_protected_manifests':len(inputs['protected_manifests']),'independent_diff_matches_author_patch':True,'only_four_authorized_changes_reverse_to_v003_bytes':True,'original_three_equations_tags_preserved':True,'new_four_tags_1to4':True,'two_tables_byte_identical':True,'one_figure_reference_preserved':True,'local_links_resolve':len(local),'old_C025_C027_and_machine_conditions_byte_preserved':True,'C039_and_C038_manual_scope_checks_passed':True,'old_42_records_166_outputs_unchanged':True,'six_postcomparison_outputs_unchanged':True,'no_new_proof_numeric_ODE_array_or_primary_access':True})
print(json.dumps({'required_changes':0,'sources':20,'direct_inputs':11,'diff_exact':True,'old_equations':3,'equations':4,'tables':2,'local_links':len(local),'old_records':42,'old_outputs':166,'additional_outputs':6}))
