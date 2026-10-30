from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,re
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261030-2034'
START=datetime.fromisoformat('2026-10-30T22:02:53+08:00');DEADLINE=START+timedelta(minutes=5)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
assert now()<DEADLINE
def save(n,obj):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[]
for p,key in [(S/'roles/role5/R004/manifest.json','artifacts'),(S/'roles/role1/R004/manifest.json','files'),(S/'roles/role3/R003/freeze.json','files')]:
    m=json.loads(p.read_text(encoding='utf-8'))
    for e in m[key]:
        f=Path(e['path']);b=f.read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
    sources.append({'path':str(p),'sha256':sha(p),'verified_files':len(m[key])})
p=R/'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v004.md'
assert sha(p)=='731cf15941ea9ded8f2343a59a7159a8ef60bd20174287e94d60a95d6e3880fe'
text=p.read_text(encoding='utf-8')
with (S/'roles/role1/R004/independent-kernel-check-36.csv').open(encoding='utf-8-sig',newline='') as f:rs=list(csv.DictReader(f))
assert len(rs)==36 and all(x['all_comparisons_pass']=='True' for x in rs)
lookup={(x['Case'],int(x['Mode'])):x for x in rs}
block=text.split('**表1 ',1)[1].split('同样把',1)[0];out=[]
for line in block.splitlines():
    match=re.fullmatch(r'\|([1-3])\|([^|]+)\|([^|]+)\|([^|]+)\|',line)
    if not match:continue
    mode=int(match[1])
    for case,cell in zip(('SHW3X','SHW4X','RH4X'),match.groups()[1:]):
        reduction,eps=[x.strip() for x in cell.split('/')]
        row=lookup[case,mode];er=f"{100*(1-float(row['N12_A8_over_A5'])):.3f}";ee=f"{float(row['N12_normalized_waveform_relative_L2']):.5f}"
        assert reduction==er and eps==ee,(mode,case,reduction,er,eps,ee)
        out.append({'Case':case,'Mode':mode,'draft_reduction_percent':reduction,'reference_reduction_percent_rounded':er,'draft_epsilon':eps,'reference_epsilon_rounded':ee,'pass':True})
assert len(out)==9
with (O/'table1-nine-checks.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
pk=json.loads((S/'roles/role3/R003/scalar-checks.json').read_text(encoding='utf-8'))
assert pk['rows_checked']==36 and pk['counts']['time_unchanged']==16 and pk['counts']['positive_M']==20 and pk['counts']['sign_changed']==3
examples=next(v for v in pk.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'D_percent' in v[0])
for case,story,label in [('RH4X','Story1','RH4X / 第1层'),('RH4X','Story2','RH4X / 第2层'),('SHW4X','Story12','SHW4X / 第12层')]:
    x=next(x for x in examples if x['Case']==case and x['Story']==story)
    line=next(line for line in text.splitlines() if line.startswith('|'+label+'|'))
    for field in ('D_percent','M_percent','net_percent'):assert f"{x[field]:.4f}" in line
# The 108-row statement is checked against a frozen small scalar CSV only, not new arrays.
frozen=json.loads((S/'roles/role1/R004/input-freeze.json').read_text(encoding='utf-8'))
entry=next(e for e in frozen['sources'] if e['path'].endswith('modal-unit-kernel-change-108.csv'))
source=Path(entry['path']);assert source.stat().st_size==entry['bytes'] and sha(source)==entry['sha256']
save('adoption-checks.json',{'completed':now().isoformat(),'draft_sha256':sha(p),'source_manifests':sources,'first12_reference_rows':36,'table1_cells':9,'table1_scalar_checks':18,'peak_ledger_rows_from_role3':36,'time_changes_adopted':20,'sign_changes_adopted':3,'selected_D_M_rows_display_checks':9,'must_change_count':0,'unit_108_source_hash_verified':sha(source),'independently_reaudited_kernel_modes':'1-12 via role1 frozen scalar results only','no_array_ODE_or_fit':True,'manual_checks':['common nonzero multiplier invariance and zero Gamma exception','epsilon not called a phase angle','M keeps old sign and is not a causal phase share','summary and conclusions preserve unit-response versus physical-share distinction']})
print('9 cells / 18 values and 3 D-M rows pass; source manifests pass')
