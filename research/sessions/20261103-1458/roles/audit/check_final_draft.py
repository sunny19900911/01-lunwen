from pathlib import Path
import hashlib,re,csv,json,datetime
H=Path(__file__).resolve().parent;R=H.parents[4]
src=R/'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-v001.md'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='52f156a71dff7a9973bfe84811a0fed028d4da141ff97d51e3532f0ca4e6cd4f'
md=src.read_text(encoding='utf-8');old=(R/'papers/damping-output-boundaries/manuscript/p06-mechanism-classification-v003.md').read_text(encoding='utf-8')
def tables(s):
 return re.findall(r'(?m)^\|[^\n]+\n(?:\|[^\n]+\n)+',s)
t=tables(md);o=tables(old);assert len(t)==8 and len(o)==6
for ix in [1,2,3]:assert t[ix]==o[ix]
assert re.findall(r'\$\$.*?\$\$',md,re.S)==re.findall(r'\$\$.*?\$\$',old,re.S)
assert md[md.index('## 参考文献'):]==old[old.index('## 参考文献'):]
def rows(block):
 return [[x.strip() for x in row.strip().strip('|').split('|')] for row in block.strip().splitlines()[2:]]
geo={x['Story']:x for x in csv.DictReader((R/'research/sessions/20261103-1458/roles/geometry/layout-by-story-11.csv').open(encoding='utf-8-sig'))}
checked=0
for i,row in enumerate(rows(t[4]),1):
 g=geo[f'Story{i}'];assert row==[f'第{i}层',f"{float(g['lower_z_m']):.1f}→{float(g['upper_z_m']):.1f}",str(g['count_total']),f"{g['X_only']}/{g['Y_only']}",f"{float(g['length_min_m']):.3f}～{float(g['length_max_m']):.3f}",f"{float(g['inclination_min_deg']):.2f}～{float(g['inclination_max_deg']):.2f}"];checked+=len(row)
peaks={(x['Case'],x['Story']):x for x in csv.DictReader((R/'research/sessions/20261020-1844/roles/role4/R003-three-model-peaks-72.csv').open(encoding='utf-8-sig'))}
for row in rows(t[5]):
 axis,st=row[0].split('/');story='Story'+st.removeprefix('第').removesuffix('层');p=peaks[row[2],story]
 assert axis==p['Axis'];assert row[3:]==[f"{float(p['P0_kN']):.2f}",f"{float(p['Pphysical_kN']):.2f}",f"{100*(1-float(p['Pphysical_kN'])/float(p['P0_kN'])):.4f}"];checked+=4
timing={x['Case']:x for x in json.loads((H/'audit.json').read_text(encoding='utf-8'))['Story8_timing']}
for row in rows(t[6]):
 q=timing[row[0]]
 expected=[q['Case'],f"{q['QT_peak_kN']:.4f}（{q['tQT_s']:.2f}）",f"{q['QD_peak_kN']:.4f}（{q['tQD_s']:.2f}）",f"{q['QD_at_QT_kN']:.4f}",f"{q['timing_ratio_percent']:.4f}",f"{q['tQD_s']-q['tQT_s']:.2f}"]
 assert row==expected,(row,expected);checked+=len(row)
links=[]
for target in re.findall(r'\]\(([^)]+)\)',md):
 if '://' in target:continue
 p=(src.parent/target).resolve();assert p.is_file(),target;links.append(target)
assert len(re.findall(r'!\[[^\]]*\]\(',md))==5
result={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_tables2to4_exact':True,'original_display_math_exact':True,'references_exact':True,'new_table_fields_checked':checked,'tables':len(t),'figures':5,'all_relative_links_exist':links,'required_scope_edit_count':1,'required_scope_edit_from':'按最小减幅选择记录时，共同六方向工况对应SHW4Y第7层','required_scope_edit_to':'对模态增阻尼参考按最小减幅选择记录时，共同六方向工况对应SHW4Y第7层','scientific_numeric_must':0,'manuscript_scope_must':1,'no_new_model_or_response_calculation':True}
out=H/'final-review-checks.json';assert not out.exists();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['new_table_fields_checked','scientific_numeric_must','manuscript_scope_must','original_tables2to4_exact']},ensure_ascii=False))
