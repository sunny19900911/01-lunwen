"""Focused small-text identity/structure audit; no prior-history scan."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
MAN=ROOT/'papers/damping-output-boundaries/manuscript';ROLE=HERE.parent
DRAFT=MAN/'maxwell-paper-narrative-v001.md';W=ROOT/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/narrative-paper-v001'
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'source-freeze.json').exists()
assert rec(DRAFT)['sha256']=='98de2905d9871dffa5a39b9ec61d5d9d84edc6607a7ea25c609dd6c61611b320'
assert rec(W/'freeze.json')['sha256']=='c03122c23effd0ccc62d519b6ceeebcff04e707af55f01d4c1bc768f7c56ddf8'
sources=[DRAFT]+[W/n for n in ['freeze.json','reproduction-appendix.md','evidence-map.json','validation.json','input-freeze.json','report.md']]+[
 MAN/'maxwell-fixed-dissipation-peak-appendix-v001.md',
 ROOT/'research/sessions/20261017-2109/R021-adoption.json',
 ROLE/'R042-dissipation-modal-bound-independent/report.md',
 ROLE/'R042-dissipation-modal-bound-independent/post-freeze-comparison/report.md',
 ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R030-dissipation-modal-output-bound/report.md',
 ROOT/'research/sessions/20261017-2109/layout-nonlinear03-protocol-v001.json',
 ROOT/'research/sessions/20261017-2109/R011-certificate-adoption.md',
 ROOT/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/C025-layout-explanation-figure-v001/caption.md']
assert len(sources)==15
write('source-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T05:34:14.620466+08:00','deadline':'2026-10-18T05:41:14+08:00','global_deadline':'2026-10-18T07:09:45+08:00','sources':[rec(p) for p in sources],'scope':'Specified small texts only. No engineering-table judgment, contribution adjudication, primary download, old-history scan or author execution.'})
assert all(rec(Path(x['path']))==x for x in read(W/'freeze.json')['files'])
text=DRAFT.read_text(encoding='utf-8');appendix=(W/'reproduction-appendix.md').read_text(encoding='utf-8')
assert re.findall(r'\\tag\{(\d+)\}',text)==[str(x) for x in range(1,11)] and text.count('$$')==20
line=next(i for i,s in enumerate(text.splitlines(),1) if 'D_min虽合法，却低于U逆的像域' in s)
assert line==93
finding={'id':'R046-M1','priority':2,'required':True,'category':'mathematical terminology / dimensions','file':str(DRAFT.resolve()),'line':line,'excerpt':'D_min虽合法，却低于U逆的像域','issue':'U_J^{-1} has dissipation domain [D0,Dmax] and force image J. D_min is energy and cannot be compared to that force image. Formula5 and formula6 are correct.','proposed_sentence':'D_min虽在总耗散域内，却不在U_J^{-1}的定义域[D0,D_max]内，因为D_min<D0。','source_phrase_also_present_in_old_appendix':True,'old_sources_not_modified':True}
assert '低于U逆的像域' in (MAN/'maxwell-fixed-dissipation-peak-appendix-v001.md').read_text(encoding='utf-8')
links={}
for p,s in [(DRAFT,text),(W/'reproduction-appendix.md',appendix)]:
    local=[u for u in re.findall(r'\[[^\]]*\]\(([^)]+)\)',s) if not u.startswith(('https://','http://'))]
    assert all((p.parent/u).resolve().is_file() for u in local)
    links[p.name]=len(local)
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n') and not b.startswith(b'\xef\xbb\xbf')
    assert all(x==x.rstrip() for x in s.splitlines())
write('findings.json',{'required_changes':1,'formula_changes_required':0,'findings':[finding]})
write('checks.json',{'required_changes':1,'formula_changes_required':0,'math_integration_status':'One terminology correction required; conditional formulas otherwise pass.','ten_equations_and_symbol_mapping_reviewed':True,'device_class_domain_empty_singleton_inverse_and_attainment_reviewed':True,'C039_physical_kernel_exponents_units_and_finite_window_scope_reviewed':True,'C025_model_and_machine_tail_contract_reviewed':True,'static_tags_1to10':True,'source_files_match_author_freeze':True,'local_links':links,'UTF8_LF_noBOM_whitespace':True,'static_pass_does_not_override_mathematical_finding':True,'old_180_packages_scanned':False,'new_proof_ODE_array_data_or_author_execution':False,'engineering_table_and_contribution_review_deferred':True})
print(json.dumps({'required_changes':1,'formula_changes_required':0,'finding_line':line,'sources':len(sources),'local_links':links},ensure_ascii=False))
