from pathlib import Path
import hashlib,json,datetime,difflib,re
H=Path(__file__).resolve().parent;R=H.parents[4]
src=R/'papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-v003.md'
target=src.with_name('p06-design-reflection-session024-v001.md')
assert not target.exists()
raw=src.read_bytes();assert hashlib.sha256(raw).hexdigest()=='a16f4e6893f4f96b94ed5ef312f4b396682db68c254b104345bbadb22b21a310'
old=raw.decode('utf-8')
body='''改善幅度与绝对需求应分别作为复核线索。对剪力需求较大的楼层，宜先核对控制输入和目标输出，再结合该层受力构件、振型及响应时程，讨论主体与消能方案的协调；不宜仅凭减幅较小就认定装置不足。若拟调整刚度分布、连接或阻尼参数，应同时比较各层剪力、变形及控制工况的变化，而不将调频本身作为设计目标。

实体装置的复核，应考察目标振型及其响应下，真实两端沿轴线的相对位移和速度，并计入支撑、连接与阻尼单元的整体柔度[2,8,9]。装置所在层的位移大小或局部曲率不能代替两端运动；统一增加模态阻尼的结果，也不能直接用于判断实体装置布置是否合适。

多输入评价中，应分别保留改善较小与绝对需求较大的成对记录，在适用设计条件下检查主体承载力、层间变形、支撑连接及装置需求。任何实际方案调整均需在相应结构模型中重新分析。'''
cjk=len(re.findall(r'[\u4e00-\u9fff]',body));assert 250<=cjk<=400,cjk
section='### 6.1 工程启示与设计反思\n\n'+body+'\n\n'
assert old.count('## 7 结论')==1
new=old.replace('## 7 结论',section+'## 7 结论')
assert new.replace(section,'',1)==old
assert re.findall(r'\$\$[\s\S]*?\$\$',new)==re.findall(r'\$\$[\s\S]*?\$\$',old)
assert re.findall(r'(?:^\|.*\n)+',new,re.M)==re.findall(r'(?:^\|.*\n)+',old,re.M)
assert re.findall(r'!\[[^\]]*\]\([^)]+\)',new)==re.findall(r'!\[[^\]]*\]\([^)]+\)',old)
target.write_bytes(new.encode('utf-8'))
(H/'R001-工程启示草稿.md').write_text(section,encoding='utf-8')
(H/'R001-source-to-v001.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=src.name,tofile=target.name)),encoding='utf-8')
report={'task':'session024/writing/R001','first_clock':'2026-11-03T10:48:30+08:00','frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'stage':'Short discussion draft; pending root evidence adoption/final review','source':str(src),'source_sha256':hashlib.sha256(raw).hexdigest(),'target':str(target),'target_bytes':target.stat().st_size,'target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'new_section_CJK_count_excluding_heading':cjk,'new_section_characters_including_punctuation_and_citations':len(body),'only_exact_insertion':True,'remove_new_section_restores_source_byte_for_byte':new.replace(section,'',1).encode('utf-8')==raw,'existing_title_abstract_conclusions_tables_equations_figures_references_unchanged':True,'new_tables_or_equations':0,'Word_created':False,'marker_run':False,'citations_used_existing_only':[2,8,9]}
(H/'R001-freeze.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
