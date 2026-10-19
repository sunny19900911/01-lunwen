from pathlib import Path
import sys, json, csv, hashlib, math
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, 'C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts')
from stream_csi import Workbook, file_sha256

OUT=Path(__file__).parent
ROOT=OUT.parents[4]
OLD=ROOT.parent/'W5-重燃双塔连体/research'
SRC=Path('E:/!!!!!!!!TO HOME/20261019/20261019/有控全节点.xlsx')
CACHE=OUT/'local-cache/new-full-geometry'
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def putjson(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

tables={}
with Workbook(SRC) as w:
    for name in w.sheets:
        if name=='Program Control':continue
        rows=list(w.rows(name)); h=dict(rows).get(2,[]); u=dict(rows).get(3,[])
        data=[(n,r) for n,r in rows if n>=4 and any(x is not None for x in r)]
        tables[name]={'header_row':2,'unit_row':3,'columns':h,'units':dict(zip(h,u)),
                      'data_rows':len(data),'first_data_row':data[0][0] if data else None,
                      'last_data_row':data[-1][0] if data else None}
        if len(data)<=1:tables[name]['data']=[{'row':n,'values':dict(zip(h,r))} for n,r in data]
links=readcsv(CACHE/'link_geometry.csv'); points=readcsv(CACHE/'point_coordinates.csv')
stats=defaultdict(lambda:dict(total=0,X=0,Y=0,other=0,links=[],bottom_z_m=[],top_z_m=[],lengths_m=[]))
for r in links:
    nx,ny,nz=(float(r[k]) for k in ('nx','ny','nz'))
    direction='X' if abs(nx)>1e-9 and abs(ny)<1e-9 else 'Y' if abs(ny)>1e-9 and abs(nx)<1e-9 else 'other'
    r['horizontal_direction']=direction
    r['property_assignment_status']='not_exported'
    s=stats[r['Story']];s['total']+=1;s[direction]+=1;s['links'].append(r['Link'])
    s['bottom_z_m'].append(min(float(r['I_Z_m']),float(r['J_Z_m'])))
    s['top_z_m'].append(max(float(r['I_Z_m']),float(r['J_Z_m'])))
    s['lengths_m'].append(float(r['length_m']))
for s in stats.values():
    for k in ('bottom_z_m','top_z_m'):s[k]=sorted(set(s[k]))
    s['length_range_m']=[min(s.pop('lengths_m',[])),max(float(r['length_m']) for r in links if r['Link'] in s['links'])]
    s['links'].sort()
old=readcsv(OLD/'single-floor-20261018-0903/R003-actual-Story4-layout/actual_link_geometry.csv')
new={(r['Story'],r['Link']):r for r in links}; checks=[]
for a in old:
    b=new.get((a['story'],a['link']))
    c={'Story':a['story'],'Link':a['link'],'found':b is not None}
    if b:
        c['same_IJ_ids']=a['I_point']==b['I_Point'] and a['J_point']==b['J_Point']
        c['max_coordinate_difference_m']=max(abs(float(a[f'{end}_{axis}_m'])-float(b[f'{end}_{axis.upper()}_m'])) for end in ('I','J') for axis in 'xyz')
        c['same_direction_within_1e12']=max(abs(float(a[k])-float(b[k])) for k in ('nx','ny','nz'))<1e-12
    checks.append(c)
fields=list(dict.fromkeys(k for r in links for k in r))
with (OUT/'R001-link-geometry-88.csv').open('w',encoding='utf-8-sig',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(links)
pointstats={'count':len(points),'stories':dict(Counter(r['story'] for r in points)),
            'bounds_m':{axis:[min(float(p[axis+'_m']) for p in points),max(float(p[axis+'_m']) for p in points)] for axis in 'XYZ'}}
manifest=json.loads((CACHE/'manifest.json').read_text(encoding='utf-8'))
summary={'read_time_asia_shanghai':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
         'source':str(SRC),'sha256':file_sha256(SRC),'bytes':SRC.stat().st_size,
         'source_stat_stable_during_geometry_read':manifest['source_stat_stable'],
         'sheets':tables,'points':pointstats,'links_count':len(links),
         'all_endpoints_found':all(r['I_coordinate_found']=='True' and r['J_coordinate_found']=='True' for r in links),
         'link_name_unique_global':len(set(r['Link'] for r in links))==len(links),
         'by_story':dict(sorted(stats.items(),key=lambda x:int(x[0].replace('Story','')))),
         'old_Story4_identity_checks':checks,'contains_time_history':False,
         'assignment_table_present':False,'nonlinear_parameter_rows':tables['Link Prop Def - Damper - Exp']['data_rows'],
         'source_changed_since_geometry_extract':file_sha256(SRC)!=manifest['sha256'],
         'full_node_cache_publish':False,'script_sha256':file_sha256(__file__)}
putjson('R001-geometry-summary.json',summary)
core=OLD/'maxwell-20261017/experiments/R001/core-cache/manifest.json'
m=json.loads(core.read_text(encoding='utf-8'))
print('CORE MANIFEST TOP KEYS',list(m))
putjson('R001-source-tables.json',tables)
small=OLD/'maxwell-20261017/roles/experiments/metadata/controlled_small_tables.json'
sm=json.loads(small.read_text(encoding='utf-8'))
assign={(v[1],v[0]):v[2] for rn,v in sm['Link Assigns - Link Properties'] if rn>=4}
assignkeys=set(assign); geomkeys=set(new)
native=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution'
hm=json.loads((native/'local_history_manifest_r006.json').read_text(encoding='utf-8'))
group_counts=Counter((a['Story'],a['Case']) for a in hm['arrays'])
cache_index={'core_cache':str(core.parent),'core_manifest_sha256':file_sha256(core),
  'source_sha256':m['sha256'],'source_bytes':m['bytes'],
  'tables':{k:{'cache':v['cache'],'group_count':len(v['groups']),'data_rows':v['data_rows'],'columns':v['columns'],
              'cases':sorted(set(g['keys'].get('Output Case','') for g in v['groups'].values()))} for k,v in m['tables'].items()},
  'paired_P_U1_npz':str(native/'local_paired_histories_r006.npz'),
  'paired_manifest':str(native/'local_history_manifest_r006.json'),
  'paired_manifest_sha256':file_sha256(native/'local_history_manifest_r006.json'),
  'paired_array_count':len(hm['arrays']),
  'paired_story_case_counts':[{'Story':k[0],'Case':k[1],'devices':v} for k,v in sorted(group_counts.items())],
  'paired_links_have_new_geometry':all((a['Story'],a['Link']) in new for a in hm['arrays']),
  'old_assignment_cache':str(small),'old_assignment_cache_sha256':file_sha256(small),
  'old_assignment_key_count':len(assignkeys),'old_assignment_matches_new_geometry_key_set':assignkeys==geomkeys,
  'old_assignment_property_counts':dict(Counter(assign.values())),
  'old_assignment_scope':'This confirms old-export keys/properties, not new native parameter values or full model equivalence.',
  'new_Excel_contains_responses':False}
putjson('R001-existing-cache-index.json',cache_index)
lines=['# 新全楼几何与既有响应资料清单','',
 '## 实际读取与结论','',
 f'- 新文件：`{SRC}`；{SRC.stat().st_size:,}字节；SHA-256 `{summary["sha256"]}`。本轮实际读取4张表全部数据，未访问同目录其他项目。',
 '- 新文件是几何导出，没有地震波、节点时程、楼层时程或阻尼器力时程。三波反应来自此前有控模型缓存，不在这份新表中。',
 '- 共3416个Point对象、88只Link。Story1—Story11每层8只，均为4只X向和4只Y向；全部I/J端点匹配、正几何长度，无重复Link名。',
 '- Story4原8只Link与前轮冻结几何的I/J编号、坐标和方向完全相同，8/8通过；这证实该层几何一致，不独立证明全模型设置及输入身份未变化。','',
 '## 新表覆盖','',
 '|表名|有效数据行|单位与用途|','|---|---:|---|']
for name,t in tables.items():
    use={'Point Object Connectivity':'XYZ单位m，节点定位','Link Object Connectivity':'I/J对象编号，无力和参数','Link Prop Def - Damper - Exp':'有kN/m与kN*(s/m)^Cexp单位，但无参数数据','Link Prop Def - Summary':'Link1 / Damper - Exponential / U1，不能代替属性赋值表'}[name]
    lines.append(f'|{name}|{t["data_rows"]}|{use}|')
lines+=['','## 各层现有布置','', '|层|下端—上端标高/m|X向|Y向|总数|','|---|---|---:|---:|---:|']
for story,s in summary['by_story'].items():lines.append(f'|{story}|{s["bottom_z_m"][0]:g}—{s["top_z_m"][0]:g}|{s["X"]}|{s["Y"]}|{s["total"]}|')
lines+=['','## 既有响应能够支持什么','',
 '- 原有635,525,054字节有控.xlsx的7表缓存仍在，源散列`9d999dfac02ad758b83b52f908ac5df6925b869b9d0a96c032c24e729bf82c23`；本轮未重读原文件。',
 '- 核已有manifest：RH4、SHW4、SHW7各X/Y共6工况；RH4为0—50s/2501点，SHW4为0—59s/2951点，SHW7为0—53.9s/2696点，间隔0.02s。X/Y不算6个独立地震事件。',
 '- Story Forces为12层×6工况共72组、195552行，Location只有Bottom。可作现状楼层剪力时程及峰值比较，包含阻尼器与否仍须按自由体校准。',
 '- 高层Story8—Story11的32只装置各有6工况完整P/U1，共192组，与新几何的Story+Link全部匹配。因此可先做该4层真实原生P的水平投影，明显强于只用Story4名义本构估力。',
 '- Story4已有48组完整原生U1；该层原生P缺失。不得以高层P替代Story4。其他未导出完整组合不补零。',
 '- 旧元数据小缓存中88条Link属性赋值全为Link1；Story+Link键集合与新几何完全一致。新表仍未给非线性参数行，故κ/c/α实际值只能沿用用户给定名义设置，不能由空参数表认证。',
 '- 原有全楼质量参与/模态或能量结果不能替代新布置复算。拟议移位后的真实结构响应尚不存在，明日须由用户按建议改模后用同输入求解。','',
 '## 命名空间和可安装性','',
 '- `UniquePt1/UniquePt2`只匹配Point Object的`UniqueName`；不把同号梁、柱、单元编号混作节点。方向为真实I→J单位向量，不由截图猜测。',
 '- 全楼点云能定位附近现有节点，不能仅凭坐标认证有梁柱、刚域、支撑承载能力或安装空间。候选节点需在模型中检查连接构件。',
 '- Story4八根与旧几何匹配、88个装置键和旧赋值匹配是正面身份证据；完整结构刚度/质量/阻尼/输入未由新表独立认证。','',
 '## 已交接文件','',
 '- `R001-link-geometry-88.csv`：88根小几何表（端点、所在层、XYZ、长度、方向、源行），可供设计和审核。',
 '- `R001-geometry-summary.json`：节点数量/坐标范围/分层分向统计及旧Story4身份检查。',
 '- `R001-source-tables.json`：所有表头、单位和有效行数。',
 '- `R001-existing-cache-index.json`：已有7表和192组P/U1的路径、散列与覆盖索引。',
 '- `local-cache/new-full-geometry/point_coordinates.csv`：完整3416节点缓存，仅本地，不上传。','',
 '## 失败与未决','',
 '- 预期可能得到新响应，但新表实为纯几何。已改为复用旧缓存，不重提大表。',
 '- 新文件无Link属性赋值、无有效非线性参数行、无梁柱连通、无模型和输入设置。旧缓存补齐属性键而非新参数。',
 '- 未作求解器操作、Git操作或新参数拟合。下一项优先用32只高层原生P配新几何核现状水平传力，并对照Bottom总层剪作明确口径的现状分析。','']
(OUT/'R001-source-inventory.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'sha':summary['sha256'],'point_count':len(points),'by_story':summary['by_story'],'old_identity':checks},ensure_ascii=False,indent=2))
