from pathlib import Path
import json,hashlib,re,datetime
H=Path(__file__).resolve().parent;R=H.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-mechanism-classification-v003.md';doc=M/'p06-mechanism-classification-论文审阅稿-v003.docx'
s=src.read_text(encoding='utf-8')
links=[]
for target in re.findall(r'\]\(([^)]+)\)',s):
    if '://' in target:continue
    assert (src.parent/target).resolve().is_file(),target;links.append(target)
identity=json.loads((H/'word-identity.json').read_text(encoding='utf-8'))
assert identity['docx_sha256']==hashlib.sha256(doc.read_bytes()).hexdigest()
report={'reviewed_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'docx_sha256':identity['docx_sha256'],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'actual_pages_viewed_original_detail':list(range(1,11)),'passed':True,'page1':'Rewritten Chinese and English abstract readable and consistent; 168 records remain paired.','page6':'Table4 relative errors 0.00245/0.00806 and unrounded-data definition complete, no clipping.','page9':'Combined action paragraph in section6.1 complete and readable.','all_pages':'Original editable tables, formulas, figures and references readable; no overlap, clipped text or missing operands observed.','source_links_exist':links,'numeric_table_cells_checked':identity['numeric_table_cells_checked'],'native_math_count':identity['native_OMML_count'],'marker_success_count':1}
(H/'final-visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(H/'final-summary.md').write_text('''# 三项修订交付

- 表4增加相对误差行，按未舍入数据算得SHW3X为0.00245%、SHW4X为0.00806%，说明这两条记录控制峰的幅值一致性；未据此扩大为唯一原生逐阶剪力证明。
- 第6.1节补充两类作用可在同一输入下并存，要求共同检查主导项幅值与反向项变化。
- 重写中英文摘要开头，直接说明两类控制输入不同带来的工程复核问题；保留168条成对记录和19/24组的实际口径。

新版为p06-mechanism-classification-v003.md及p06-mechanism-classification-论文审阅稿-v003.docx。旧版本不改。最终Word10页已全部实际查看，117个数值表格单元和43处原生公式通过校验。本次未新建模型、求解、拟合或读取原始大表。Git同步结果见git-FINAL-receipt.json。
''',encoding='utf-8',newline='\n')
paths=[p for p in sorted(H.rglob('*')) if p.is_file() and 'local-cache' not in p.parts and '__pycache__' not in p.parts and p.suffix in ['.md','.json','.py']]
paths.extend([src,doc]);manifest=H/'git-FINAL-manifest.json';assert not manifest.exists()
cfg={'checkpoint':'FINAL','message':'Add peak-error comparison and combined modal-mechanism guidance','files':[{'relative':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
manifest.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen_files':len(paths),'pages_actually_viewed':10,'docx_sha256':identity['docx_sha256']},ensure_ascii=False))
