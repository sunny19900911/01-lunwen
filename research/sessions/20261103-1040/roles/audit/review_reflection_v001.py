from pathlib import Path
import re,json,hashlib,datetime,difflib
H=Path(__file__).resolve().parent;R=H.parents[4];O=H/'R002';O.mkdir(exist_ok=True)
assert not (O/'text-checks.json').exists(),'Preserve existing verification'
old=R/'papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-v003.md'
new=R/'papers/damping-output-boundaries/manuscript/p06-design-reflection-session024-v001.md'
draft=H.parent/'writing/R001-工程启示草稿.md'
sha=lambda b:hashlib.sha256(b).hexdigest()
a=old.read_bytes();b=new.read_bytes();d=draft.read_bytes()
assert sha(b)=='b1d4902014d7d9ecbc4f65f801f70a660c7df466d8acd6f4225aa60b824ceedc'
assert sha(a)=='a16f4e6893f4f96b94ed5ef312f4b396682db68c254b104345bbadb22b21a310'
v=b.decode('utf-8');u=a.decode('utf-8');ds=d.decode('utf-8').replace('\r\n','\n')
i=v.index('### 6.1 工程启示与设计反思');j=v.index('## 7 结论',i)
section=v[i:j]
assert section.strip()==ds.strip()
remaining=v[:i]+v[j:]
# Exactly remove the new section; permit the one joining blank line only if required.
if remaining.encode('utf-8')!=a:
    if remaining.replace('\n\n\n## 7 结论','\n\n## 7 结论').encode('utf-8')==a:
        join_adjust='Remove single blank separator belonging to inserted section'
        remaining=remaining.replace('\n\n\n## 7 结论','\n\n## 7 结论')
    else:
        (O/'unexpected-diff.txt').write_text(''.join(difflib.unified_diff(u.splitlines(True),remaining.splitlines(True))),encoding='utf-8')
        raise AssertionError('Non-section changes detected')
else:join_adjust=None
assert remaining.encode('utf-8')==a
tables=lambda t:re.findall(r'(?m)^\|.*(?:\n\|.*)*',t)
assert tables(u)==tables(v) and len(tables(v))==6
formulas=lambda t:re.findall(r'\$\$(.*?)\$\$',t,re.S)
assert formulas(u)==formulas(v) and len(formulas(v))==5
figs=lambda t:re.findall(r'!\[[^\]]*\]\([^)]*\)',t)
assert figs(u)==figs(v) and len(figs(v))==3
assert u.split('## 7 结论')[1]==v.split('## 7 结论')[1]
assert u.split('## 1 引言')[0]==v.split('## 1 引言')[0]
refs=re.findall(r'^\[(\d+)\] ',v,flags=re.M);assert refs==[str(x) for x in range(1,11)]
body=section.split('\n\n',1)[1].strip();cjk=len(re.findall(r'[\u4e00-\u9fff]',body))
assert cjk==312 and 250<=cjk<=400
replacements=[('而不将调频本身作为设计目标','以目标响应的综合改善作为比选依据'),('装置所在层的位移大小或局部曲率不能代替两端运动；统一增加模态阻尼的结果，也不能直接用于判断实体装置布置是否合适。','装置配置宜依据真实端点运动与传力路径，并另核相应本构条件；模态增阻尼比较主要提供目标响应的复核线索。'),('支撑连接及装置需求','稳定、支撑连接及装置力和行程')]
candidate=v
for x,y in replacements:
    assert candidate.count(x)==1
    candidate=candidate.replace(x,y)
ci=candidate.index('### 6.1 工程启示与设计反思');cj=candidate.index('## 7 结论',ci)
cbody=candidate[ci:cj].split('\n\n',1)[1].strip();cc=len(re.findall(r'[\u4e00-\u9fff]',cbody));assert 250<=cc<=400
out={'at':datetime.datetime.now().astimezone().isoformat(),'old_source_sha256':sha(a),'new_source_bytes':len(b),'new_source_sha256':sha(b),'draft_sha256':sha(d),'deleted_section_rest_exact_old_bytes':True,'join_separator_adjustment':join_adjust,'old_tables_exact':6,'old_display_formulas_exact':5,'old_figures_exact':3,'abstracts_exact':True,'conclusions_and_references_exact':True,'references':10,'section_Chinese_characters':cjk,'section_with_punctuation_length':len(body),'root_three_replacements_safe':True,'after_replacements_Chinese_characters':cc,'hypothetical_final_bytes':len(candidate.encode('utf-8')),'hypothetical_final_sha256':sha(candidate.encode('utf-8')),'hypothetical_only_no_author_file_written':True}
(O/'text-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
