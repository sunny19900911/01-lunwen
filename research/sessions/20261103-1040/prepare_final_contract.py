from pathlib import Path
import json,hashlib,datetime,re
S=Path(__file__).resolve().parent;R=S.parents[2]
f=json.loads((S/'roles/audit/R002/freeze.json').read_text(encoding='utf-8'))
for x in f['files']:assert hashlib.sha256((S/'roles/audit/R002'/x['path']).read_bytes()).hexdigest()==x['sha256']
src=R/'papers/damping-output-boundaries/manuscript/p06-design-reflection-session024-v001.md';b=src.read_bytes();assert hashlib.sha256(b).hexdigest()=='b1d4902014d7d9ecbc4f65f801f70a660c7df466d8acd6f4225aa60b824ceedc'
pairs=[['而不将调频本身作为设计目标','以目标响应的综合改善作为比选依据'],['装置所在层的位移大小或局部曲率不能代替两端运动；统一增加模态阻尼的结果，也不能直接用于判断实体装置布置是否合适。','装置配置宜依据真实端点运动与传力路径，并另核相应本构条件；模态增阻尼比较主要提供目标响应的复核线索。'],['支撑连接及装置需求','稳定、支撑连接及装置力和行程']]
t=b.decode('utf-8')
for old,new in pairs:assert t.count(old)==1,old;t=t.replace(old,new,1)
raw=t.encode('utf-8');h=hashlib.sha256(raw).hexdigest();assert len(raw)==28776 and h=='750b1dcc8fa38014d45307cec124c6ef83058a063b32a5bee7ba7c1bd95f1324'
sec=t.split('### 6.1 工程启示与设计反思\n\n',1)[1].split('\n\n## 7 结论',1)[0]
assert len(re.findall('[\u4e00-\u9fff]',sec))==313
out={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source':src.relative_to(R).as_posix(),'target':src.with_name('p06-design-reflection-session024-v002.md').relative_to(R).as_posix(),'replacements':pairs,'expected_bytes':len(raw),'expected_sha256':h,'expected_CJK':313,'must':0,'review':'roles/audit/R002/v001-short-section-final-review.md','no_scientific_or_numeric_change':True,'allow_Word_after_exact_source_match':True}
(S/'final-exact-change-contract.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'final-review-adoption.md').write_text('# 短节终审采用\n\n根已完整读v001新增节与构建/冻结证据、audit六意见收窄和唯一终审、文献正式原页报告及清单。终审must0，采纳三处正面措辞/具体检查对象的小改；精确契约由根独算与审查员内存预测SHA相同。最终313汉字，删除短节可恢复023源，原有全部内容不变。无需再科学计算或旧数字重审，唯一作者匹配后直接进入Word；根最后核精确diff和全部最终页。\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
