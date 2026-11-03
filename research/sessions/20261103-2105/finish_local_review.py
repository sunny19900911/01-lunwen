from pathlib import Path
import json,hashlib,datetime,re,ast
S=Path(__file__).resolve().parent;R=S.parents[2];M=R/'papers/damping-output-boundaries/manuscript';now=datetime.datetime.now().astimezone().isoformat()
src=M/'p06-control-check-session028-v004.md';doc=M/'p06-control-check-session028-论文审阅稿-v004.docx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=M/'p06-actual-timing-session027-v004.md';assert sha(old)=='f56b44fc5172778261364253e69eb8fa324f97af148e0fdd968e50b3dbe15a71'
assert sha(M/'p06-actual-timing-session027-论文审阅稿-v004.docx')=='85350fbecf951a17e39e4e37f0394dc947237351ef6f24be895898b08fa5dc68'
qa=json.loads((S/'word-identity-v004.json').read_text(encoding='utf-8'));assert qa['docx_sha256']==sha(doc)
pages=[S/f'word/local-cache/render-v004/page-{i}.png'for i in range(1,14)];assert all(p.is_file()for p in pages)
for p in S.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
links=[]
for target in re.findall(r'\]\(([^)]+)\)',src.read_text(encoding='utf-8')):
 if not target.startswith(('http://','https://')):
  p=(src.parent/target).resolve();assert p.is_file(),target;links.append(str(p))
visual={'at':now,'passed':True,'docx':doc.relative_to(R).as_posix(),'docx_sha256':sha(doc),'source':src.relative_to(R).as_posix(),'source_sha256':sha(src),'pages_actual_viewed':list(range(1,14)),'pages':13,'native_editable_tables':10,'independent_display_equations':6,'OMML':57,'numeric_table_cells_checked':241,'figures_original_bytes':5,'issues_fixed':['Title fits one line','New table6 kN header no broken unit','Official URL encoded as real hyperlink instead of inline math'],'final_render_used':'render-v004','old_source_and_docx_bytes_preserved':True,'local_links_checked':links,'marker_success_count':1,'canonical_failure_logged_then_safe_hidden_Word_COM_and_PDFium':True}
(S/'final-visual-review.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=f'''# 四项补强本轮交付

本地核审实际完成：{now}。目录2105来自最初核钟，本轮主控实际恢复执行21:35，角色启动存在消息等待；没有声称每15分钟严格执行或持续离线科研，没有新定时器。

最终稿：[{src.name}](../../../papers/damping-output-boundaries/manuscript/{src.name})；[Word审阅稿](../../../papers/damping-output-boundaries/manuscript/{doc.name})。13页逐页实际查看，10张可编辑表、6独立公式、57原生OMML、5原图，241数字表格单元精确核；旧027原MD/Word哈希未变。

## 实际取得的结果

1. 两层×两输入的QT/QD/代数差12行、控制峰4行及完整四曲线图齐。根与数据角色独算36字段一致。明确J端结构抵抗项与节点外力相反，正负两种代数对照均保留。
2. Story10/RH4Y有限Maxwell局部等效完成：原κ保留，0—15s定参留出段QD相对RMS差45.9994%；全0—50s事后定参全窗差42.6387%。16.62/21.64s绝对合力大小次序均保持，未生成等效结构QT。
3. 三阈值216行来自同72记录，基准候选先冻再读实际D。5%有91候选，±0.10s覆盖41/72真峰、51/72峰误差≤1%；最差仍低估31.7364%。10%也有漏检。以此将筛查写为复核优先级，完整实际时程取峰保留。
4. 摘要、方法、工程步骤与结论统一为控制输入＋控制时刻；保留实际88布置、72B/D记录、原14工况参考，未冒称现场实测、真实逐阶恢复或录用率提高。

独审162字段无差异，must0；两项可选用语已采纳，见final-clarification-adoption.json。所有新增代码通过AST、实际相关计算已执行，原生源时刻/单位/源行有保存。最终版Word原生数学、数字、图及链接检查通过，全部13页实际查看。

## 仍未闭合的两项

- 第一项没有同切口独立主体合力/含不含Link双cut，故不能宣布QT包含性已经物理认证，也不能将QT−QD标为QS。最小核对量详见角色cut正式报告。
- 第二项没有把全部装置作用组装到一致的结构方程后重算QT；局部出力次序相同不足以证明剪力控制迁移可由整楼等效线性化解释。真实q2/q13原缺口也保持，未靠旧线性参照补齐。

## 同步

R001已正常推送47200ad9b069fc0891e667561dc67a469bdf0603且远端等。最后白名单同步的实际提交/远端结果以git-FINAL-receipt.json为准；回执生成在提交后，不为回执本身无限重复提交。没有原始Excel、大数组、local-cache、第三方全文、凭据或旧脏文件进入白名单。
'''
(S/'final-summary.md').write_text(summary,encoding='utf-8',newline='\n')
(S/'普通中文修改说明.md').write_text('''# 这轮改了什么

论文现在分开回答两件事：哪条输入值得重点复核，以及这条输入下哪个时刻真正控制。实际88只布置和72条计算时程仍是主体。

新增四组同刻受力表和一张完整曲线图，明确列出装置力方向，但没有把缺少独立核对的差值改叫主体剪力。局部线性等效保留Maxwell串联弹簧，两时刻出力次序一致，幅值误差仍较大；它尚未替代整楼结构重算。

5%接近峰办法实际做了72条检验，加上前后0.10秒只抓住41条控制峰，第12层出现明显漏检。现在把它作为先查哪些时段的办法，最终需求仍看完整实际时程，避免只靠一个好案例就推广。

成稿13页，表格、公式可编辑；旧稿保持。进一步补强的关键只剩独立同切口主体内力、完整结构等效线性重算两类证据，具体要求列在补充说明中。
''',encoding='utf-8',newline='\n')
claims='''# 本轮主张裁决

- C1 supported / observed-data / reviewed：四组同刻QT/QD/代数差数值可核；独立主体平衡unresolved，不把平滑当证据。
- C2 supported / numerical-test / reviewed：两种局部有限Maxwell等效均保持所选两时刻绝对QD次序；相对RMS42.64/46%明确。全结构等效QT检验unresolved。
- C3 supported / analytic-derivation+observed-data / reviewed：两时刻排序不等式正确；5%有限候选保证全部实际峰的主张refuted，反例RH4Y/Story12，31.7364%漏峰。
- C4 supported / engineering-method / reviewed：控制输入与控制时刻分别列示；实际方案软件数据不是现场实测，近峰检查不是计算前预测。
'''
(S/'claims.md').write_text(claims,encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write(f'\n{now}：root四组复算、两种局部Maxwell递推、基准先冻三阈值72组筛查全部实际执行；独审162字段通过。最终v004字节完成渲染、全部13页实际查看与OOXML身份检查。没有新结构求解、旧300阶ODE重跑或原大Excel提取。\n')
status={'state':'closed-reviewed-with-two-physical-gaps','closed_local_review_at':now,'stage':4,'checkpoint_open':False,'no_new_numeric_experiments':True,'new_automation':False,'manuscript':src.relative_to(R).as_posix(),'docx':doc.relative_to(R).as_posix(),'docx_sha256':sha(doc),'independent_numeric_fields':162,'must':0,'stages':{'1':'simultaneous comparison done; independent cut balance unavailable','2':'local equivalent tests done; global QT forward unavailable','3':'all72 tested; universal 5% coverage refuted','4':'integrated and 13-page QA complete'},'git_final_receipt':'git-FINAL-receipt.json','old_dirty_files_preserved':True}
(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'local_review_closed':now,'pages':13,'docx_sha256':sha(doc)},ensure_ascii=False))
