from pathlib import Path
import datetime,hashlib,json,difflib,re
HERE=Path(__file__).resolve().parent
R=HERE.parents[4]
SOURCE=R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-v003.md'
TARGET=SOURCE.with_name('p06-sh3-sh4-session023-v001.md')
assert not TARGET.exists()
original=SOURCE.read_bytes();assert hashlib.sha256(original).hexdigest()=='b546eb7e9afe6dfde8f8bc57f705ee6e283b60141000a408965d39921fffdac3'
old=original.decode('utf-8')
before='工程结构的逐阶剪力分解还需要对应节点振型、响应时程和输出映射。本文利用工程资料比较逐层结果，并在参数完整的三层剪切模型中说明小方向有效质量与局部剪力的关系。'
after='工程结构的逐阶剪力分析需结合振型、响应时程及相应的内力输出关系。本文以软件楼层剪力作为工程需求依据，并用固定300阶线性参照辅助比较SHW3X与SHW4X下第5层的模态项；参数完整的三层剪切模型用于说明方向有效质量与局部剪力对应不同输出。'
assert old.count(before)==1
new=old.replace(before,after)
new=new.replace('### 4.2 原峰时评价的偏差','### 4.3 原峰时评价的偏差').replace('### 4.3 独立装置模型的出力时序','### 4.4 独立装置模型的出力时序')
insert='''### 4.2 SHW3X与SHW4X的第5层辅助对照

表2中SHW4X的第5层参考剪力高于SHW3X，但两者的减幅控制意义不同。进一步的解释应比较目标层在各自剪力峰时的模态项，而不能仅依据总体质量参与率或某一阶自身峰值判断。为此，采用固定300阶线性参照，在两条输入各自的软件剪力峰时，查看第2、10、13阶及全部300阶的有符号合成值；原生软件绝对峰仍单独保留，作为需求比较的依据。

该参照由质心集中质量、Ritz模态数据和相应输出系数建立，用于检查较高阶项同向增强这一候选解释。两输入的峰时不同，比较的是各自峰值的组成；参照项不作为原生软件剪力的唯一逐阶分解。工程复核仍分别保留SHW3X的最小减幅记录和SHW4X的最大参考需求记录。

'''
anchor='### 4.3 原峰时评价的偏差'
assert new.count(anchor)==1
new=new.replace(anchor,insert+anchor)
TARGET.write_text(new,encoding='utf-8',newline='\n')
# First structural draft deliberately excludes new, not-yet-adopted numerical results.
assert all(x in new for x in ['24个楼层—方向组中有19组','6.8513%','9027.7451kN','11.3022%'])
assert re.findall(r'!\[[^\]]*\]\([^)]+\)',new)==re.findall(r'!\[[^\]]*\]\([^)]+\)',old)
assert re.findall(r'\$\$[\s\S]*?\$\$',new)==re.findall(r'\$\$[\s\S]*?\$\$',old)
blocks=lambda s:re.findall(r'(?:^\|.*\n)+',s,re.M)
assert blocks(new)==blocks(old)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==hashlib.sha256(original).hexdigest()
(HERE/'v003-to-v001.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=SOURCE.name,tofile=TARGET.name)),encoding='utf-8')
report={'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'stage':'R001 structural draft; new numerical table and conclusion remain outside body pending root adoption','source':str(SOURCE),'source_sha256':hashlib.sha256(original).hexdigest(),'target':str(TARGET),'bytes':TARGET.stat().st_size,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'old_source_unchanged':True,'tables_equations_figures_unchanged':True,'abstract_and_conclusions_unchanged':True,'new_auxiliary_subsection_only':True,'word_created':False,'marker_run':False}
(HERE/'v001-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
