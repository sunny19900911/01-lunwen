"""Close completed deliverables before the hard deadline; no further research."""
from pathlib import Path
import json,datetime,tomllib,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
tool=json.loads((S/'final-tool-receipts.json').read_text('utf-8'))
configs={}
for name in ['automation-5','git','automation-3','automation-4']:
 d=tomllib.loads((Path('C:/Users/mj528/.codex/automations')/name/'automation.toml').read_text('utf-8'));assert d['status']=='PAUSED';configs[name]={k:d.get(k) for k in ['id','status','rrule','target_thread_id']}
(S/'final-automation-readback.json').write_text(json.dumps({'at':now,'configs':configs,'official_tool_receipts':'final-tool-receipts.json'},ensure_ascii=False,indent=2)+'\n','utf-8')
v=json.loads((S/'status.json').read_text('utf-8'));by={p['role']:p for p in tool['final_actual_role_snapshot']}
for role in v['roles']:
 p=by[role['role']];assert p['turn']['status']=='completed';role.update(cursor=p['cursor'],actual_status=p['status'],turn_status='completed',task='completed_no_new_dispatch')
word=R/v['canonical_word'];assert hashlib.sha256(word.read_bytes()).hexdigest()=='2844e66450e65ec489e33f3e1c1db82f9abab5800aa52c363549bb20cfd0f998'
v.update(phase='closed-complete',closed_at=now,closed_before_deadline=True,close_reason='All authorized revised-paper, practical-method, independent-review and editable-Word deliverables complete; no forced idle research.',checkpoint_open=False,scientific_dispatch_allowed=False,no_new_scientific_dispatch=True,no_new_experiments=True,automation_actual_config=configs,final_summary='final-summary.md',final_git_status='pending_final_checkpoint')
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');(S/'threads.json').write_text(json.dumps({'session':v['session'],'roles':v['roles'],'last_checked_at':now},ensure_ascii=False,indent=2)+'\n','utf-8')
summary=(S/'final-summary-prepared.md').read_text('utf-8')
summary+='\n## 最终文件与实际完成\n\n最终科学源011-v004 SHA c30cbbccecc21be395ad9cf55de3f842f806cfea8372b72d180d240a3e532b7a；最终Word为'+v['canonical_word']+'，651982字节，SHA 2844e66450e65ec489e33f3e1c1db82f9abab5800aa52c363549bb20cfd0f998。其余无后缀/v003/v004/r2为预览，不交付也不最终stage。\n\n最终9页，7可编辑表、3图、5原生数学结构（含K矩阵）、30处原生下标。作者与主控均实际逐张查看pages-subscript第1—9页；正文/表头变量下标正确，图表公式无裁切重叠，参考文献不拆条且末页双栏平衡。根独立核最终Word与上轮仅下标归一后全文等价、所有数字串不变、3嵌图字节一致，见root-final-Word-content-check.json。\n\n机制节约占正文9.01%，正文含表图注4338汉字；中摘要331纯汉字，5中/5英关键词，7条实际支持的引用。按已核期刊要求准备了单栏题摘/双栏正文/通栏表图，但未下载官方完整模板，不把本稿认作投稿模板完全认证；作者信息仍待本人填写。\n\n实际于'+now+'完成收束，早于21:50:14硬截止，因所有必需成果与独审/QA已完成而提前交付，不宣称用满90分钟，也不将原早间三小时未执行的间隔算科研。六角色最后回合均completed/idle，不再新派研究。automation-5正式暂停、view及只读实配回读确认，旧git/automation-3/4仍PAUSED。\n\n最后正常Git结果以git-FINAL-receipt.json为准；本总结先于该检查点写入，不预先声称推送成功。行政回执与最后status可能晚于Git提交，留本地核对，原未知改动和5E-07未动。\n'
(S/'final-summary.md').write_text(summary,'utf-8')
with (S/'runs.md').open('a',encoding='utf-8') as f:f.write('\n'+now+'成果完成提前收束：最终Word全页QA和内容等价检查通过，六角色完成，automation正式暂停/实配核对。不是延长科研或用满预算；最终Git回执单列。\n')
with (S/'claims.md').open('a',encoding='utf-8') as f:f.write('\nC006 Final reviewed：工程主导稿、4步方法、168d、24/14/108及图表均有已列独审；最终Word9页根与作者全页实际查看。其余未认证模型范围不升级。\n')
(S/'rounds/R003-final.md').write_text('# 最终交付\n\n'+now+'。全部成果完成，原始3h执行失败保留，追加90分钟原人类授权已核，本次提前完成而不凑时长。最终源v004与变量排版Word固定，无新研究。暂停工具/实配、QA、真实未决与最终Git见本会话记录。\n','utf-8')
print(json.dumps({'closed_at':now,'phase':v['phase'],'word_sha256':v['canonical_word_sha256'],'all_automations_paused':True},ensure_ascii=False))
