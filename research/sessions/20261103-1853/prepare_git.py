from pathlib import Path
import datetime,json
S=Path(__file__).resolve().parent;R=S.parents[2];prev=R/'research/sessions/20261103-1700'
for name in ['publish_checkpoint.py','make_checkpoint.py']:
    text=(prev/name).read_text(encoding='utf-8').replace('p06-actual-main-session026-','p06-actual-timing-session027-')
    target=S/name;assert not target.exists();target.write_text(text,encoding='utf-8',newline='\n')
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
text=f'''# R001 实际峰变化与模态恢复诊断

实际汇总时间{now}。本轮初核钟18:52:46，先数据生产、恢复诊断、独审再汇总，未宣称15分钟准点完成。旧会话关闭状态保留。

实际同刻21行和7项峰值关系经独审591字段一致。第8层全六仅0.04—0.22s峰移，未强行当换波包；完整P24项客观最大峰移为第10层RH4Y5.02s。新图含两状态完整QT和原生QD，根原尺寸实际查看通过。

第10层RH4Y原需求差109.600832kN，两个时刻降低量差689.992509kN，实际后时刻比原峰时读数高580.391677kN；两时刻关系独审残差0，只作已有响应的竞争时段解释，不称输入前预测或装置单因果。

实际CM2/13恢复做了有限试算：q_obs质量投影及Gram混叠、旧已知q_ref上的4条误差、实际B/D12行投影峰与8个锚点。不能把投影当实际FNAq，旧参照3—7%误差也不是实际界。旧全88非线性力与完整恢复缺项保持；新投影诊断已独立语义/算法审核，不宣称独立重算全部108CM组。另核已知全节点旧metadata的可用性，不重读358MB。

候选027v001两项终审0must，两类可选措辞已落实至v003及补充A；科学数值、7表、5公式、4图保持。最终科学源v00329311B/SHA61bce79bc063aa05deef28508cdd0189d93341162cca58475d64481402e7fb18。Word已生成554619B/SHA c838307a0af85aab0c102baf07081e3713b88e36e0af08daab19b73a89fb427e，结构gate191数字单元/51原生公式通过；11页视觉QA进行中，未将存在当通过。

当前检查点不收Word。全部最终页实际检查后再最终正常白名单同步，无新科学实验或自动化。
'''
(S/'rounds/R001.md').write_text(text,encoding='utf-8',newline='\n')
with (S/'runs.md').open('a',encoding='utf-8',newline='\n') as f:f.write(f'\n{now}：591字段同刻数与2时点公式独审完成，实际CM投影有限诊断结束，最终措辞已采纳。Word一次marker生成，结构gate通过，实际11页QA在途；首轮同步只收冻结数据/图/MD/代码，不收未完QA的Word。\n')
print(json.dumps({'at':now,'prepared':['publish_checkpoint.py','make_checkpoint.py'],'word_not_in_R001':True},ensure_ascii=False))
