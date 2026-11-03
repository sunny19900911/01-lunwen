from pathlib import Path
import datetime, hashlib, json

S = Path(__file__).resolve().parent
R = S.parents[2]
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
md = 'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-v004.md'
docx = 'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-论文审阅稿-v004.docx'
expected = {md: 'b66b072aeca3019146e41664ce71ae81475d198410bf505e53afaf054d76ffe3', docx: '0a91c78b152baa3472f1f92a00633e914512965d953179abc653bea95e66f88f'}
for p, digest in expected.items():
    assert hashlib.sha256((R / p).read_bytes()).hexdigest() == digest
visual = {
    'passed': True, 'reviewed_at': now, 'reviewer': 'root', 'docx': docx,
    'docx_sha256': expected[docx], 'source': md, 'source_sha256': expected[md],
    'final_render_directory': 'word/local-cache/render-v3',
    'actual_pages_viewed': list(range(1, 15)), 'pages': 14,
    'tables': 8, 'numeric_table_cells_checked': 238, 'native_OMML': 56,
    'display_equations': 5, 'figures': 5,
    'observations': [
        '最终14页均已实际查看。正文、符号、上下标、表格和图中文字可读，未见裁切重叠。',
        '表5跨第7—8页，重复表头且数据行未拆分；第4.3.2标题已缩短为一行。',
        '第11页三层模型矩阵及公式、第12页工程步骤、第13页结论、第14页参考文献均已查看。',
        '旧15页版本的过大留白已通过移动现有图位置修正，未缩小图或字号；旧版本保留。'
    ],
    'structural_check': 'word-identity-final.json',
    'render_method': 'canonical缺少LibreOffice的真实失败留档后，独立hidden Word COM导PDF并以PDFium渲染；仅关闭自建对象。',
    'marker_success_count_this_session': 1,
}
(S / 'final-visual-review.json').write_text(json.dumps(visual, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
summary = f'''# 实际阻尼器方案接入：最终总结

实际关闭时间：{now}。本轮按用户批准的方案完成，不延用任何旧研究窗口，未创建新的定时任务。

## 最终交付

- 科学与排版源：`{md}`，38860字节，SHA256 `{expected[md]}`。
- Word：`{docx}`，690283字节，SHA256 `{expected[docx]}`。
- 14页、8张可编辑表、5张图、5个独立公式；表格238个数值单元格和56个原生公式对象已检查，最终14页均实际查看。
- 完整工程附表与比较条件：`实际方案资料与完整附表.md`。

## 主线结果

保留原14方向工况、168条成对记录及19/24组两类控制输入不同的主框架。在4.2节后新增4.3节，接入88只实际阻尼器的I/J位置、分层配置、六共有方向工况三模型响应和原生装置出力。

88只装置位于第1—11层，每层8只、X/Y各4只。实际方案共有六工况中，24个楼层—方向组有12组的最小减幅和最大需求由不同输入控制；同一六工况范围的模态增阻尼参照为7组。原全14工况19组的结论不与子集混用。

第8层X向：RH4X控制7.7713%的较小减幅，SHW7X控制7132.2925kN的较大需求。两条记录在楼层剪力峰时的装置水平合力绝对值，分别为装置自身峰的58.6736%和63.4488%。这说明实际方案复核应同时保留两类控制记录、楼层剪力峰时出力和装置自身峰。

基准与实际模型六组导出基底输入的16296个保存时刻、六物理分量共97776个数值逐项一致。比较使用现有小表和缓存，未重提原635MB表或运行ETABS求解。

## 验证与真实范围

几何、三模型输出与输入配对分别核查；独立审核通过新增数值，最终稿已修正实施步骤中基准—参考与基准—实际方案的对象限定。旧SHW3X/SHW4X模态解释与新增实际方案分开，不把六共有工况写成含SHW3X。

本文新增的是所提供真实工程模型方案的数值应用核查，不是物理试验。实际模型完整内部求解设置、背景阻尼和初始设置未全部导出；不由输入一致推断所有设置完全一致。原生QT截面包含性尚未认证，因此只列同刻装置出力，不据此扣出主体真实剪力。32只完整装置出力范围为第8—11层，不向88只补零或扩展总量。

## 同步与保留

R001与R002已正常提交并核远端一致。最终白名单同步结果见`git-FINAL-receipt.json`；以其remote_equals_local和pending_push字段为准。仅本轮已冻结文本、小表、代码、图与最终Word进入清单，排除所有local-cache、原件和旧脏文件。无强推、模型求解、付费或投稿。
'''
(S / 'final-summary.md').write_text(summary, encoding='utf-8', newline='\n')
(S / '普通中文研究说明.md').write_text('''# 这次增加了什么

原论文用14个方向工况说明：减幅最小的记录与剪力需求最大的记录经常不同。这部分原样保留。

现在新增了真正对应你提供方案的内容：88只阻尼器放在哪些层、沿哪个方向安装；六个共有工况下，基准、直接增加模态阻尼和实际阻尼器方案各层剪力如何不同；第8层在两条控制记录下，楼层剪力最大时装置究竟出了多大力。

实际方案仍出现两类控制记录不同：24组中有12组。第8层X向，RH4X的减幅只有7.7713%，而SHW7X的需求达到7132.29kN。工程师应分别保留这两条记录，一条查改善不足，一条查较大需求，再回到相应时刻检查装置出力。

所以，这一节不再只有布置图或数据展示，而是把实际布置、整体响应和目标时刻的装置出力连到同一套复核步骤。文章没有把模型计算写成试验，也没有把装置自身峰当成楼层剪力峰时的实际出力。

最终Word为14页，图表和公式已核对，所有页面均已实际查看。完整比较条件和附表另见《实际方案资料与完整附表》。
''', encoding='utf-8', newline='\n')
(S / 'claims.md').write_text('''# 最终主张与范围

- C01 已核：原14方向工况/168成对记录/19组控制输入不同保持；原表2—4、公式及引用保留。
- C02 已核：88只I/J几何完整，第1—11层每层8只，X/Y各4只；真实布置图和配置表已接入。
- C03 已核：六共有工况72层记录可比较，实际方案24组中12组两类控制输入不同，同范围模态参照7组；两组统计范围明确。
- C04 有条件采用：97776项导出基底输入逐值一致，CM方向质量36项相对差最大3.60e-14；允许报告相同导出输入下实际方案相对基准的r_D。不认完整内部设置全部同一或单一参数因果。
- C05 已核有限范围：第8—11层32只装置×六工况原生P完整，可按真实轴向投影列水平合力和同刻值。不扣未认证包含性的QT，不将局部子集冒充全88只贡献。
- C06 完成交付：最终MD v004与14页Word一致；238表格数字、56OMML、5图身份通过，全部最终页已实际查看。

旧SHW3X只用于原14工况和固定300阶线性参照机制，不被移入实际六工况。本文是工程模型数值应用，不称物理试验；不保证刊物录用率或新增首创。
''', encoding='utf-8', newline='\n')
with (S / 'runs.md').open('a', encoding='utf-8', newline='\n') as f:
    f.write(f'\n{now}：已完成几何/响应/配对/独审四项任务及主稿整合，最终v004和14页Word冻结。最终14页实际查看完成，结构身份检查通过；无新ODE或原大表重复提取。R001/R002已正常同步，最终同步结果另见git-FINAL-receipt.json。\n')
(S / 'rounds' / 'FINAL.md').write_text(summary, encoding='utf-8', newline='\n')
status = json.loads((S / 'status.json').read_text(encoding='utf-8'))
status.update({'phase': 'closed-complete', 'closed_at': now, 'checkpoint_open': False,
    'no_new_scientific_dispatch': True, 'no_new_numeric_experiments': True,
    'final_manuscript': md, 'final_word': docx, 'final_word_sha256': expected[docx],
    'visual_QA': 'final-visual-review.json', 'final_git_receipt': 'git-FINAL-receipt.json',
    'remaining_scientific_work': [], 'remaining_scope_limits': ['完整内部模型设置未全部导出', 'QT截面包含性未认证', '完整原生P仅32只范围'],
    'automation_created_this_session': False})
(S / 'status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'closed_at': now, 'final_word': docx, 'QA_passed': True}, ensure_ascii=False))
