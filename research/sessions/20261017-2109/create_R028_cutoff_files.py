"""Manually invoked after real cutoff only. Never operates Git or scheduler."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
S=Path(__file__).resolve().parent;R=S.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put_same_or_new(p,text):
 raw=text.encode('utf-8')
 if p.exists():assert p.read_bytes()==raw,('Preserve differing pre-existing output',str(p))
 else:p.write_bytes(raw)
def main():
 j=json.loads((S/'status.json').read_text('utf-8'));now=datetime.now().astimezone();deadline=datetime.fromisoformat(j['deadline'])
 assert now>=deadline,'Do not generate cutoff records before real deadline'
 assert j['checkpoint_open'] and j['current_round']=='R028'
 snapshot=json.loads((S/'R028-cutoff-snapshot.json').read_text('utf-8'))
 observed=datetime.strptime(snapshot['at_utc'],'%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
 assert observed>=deadline
 assert len(snapshot['roles'])==6
 assert all(p['thread']['status']['type']!='active' for p in snapshot['roles'].values()),'Collect in-flight role work first, no new dispatch'
 adoption=json.loads((S/'R028-adoption.json').read_text('utf-8'))
 for name,digest in adoption['checked_identities'].items():assert sha(R/name)==digest,name
 source=(S/'final-summary-science-candidate-v001.md').read_text('utf-8');body=source.split('\n\n',2)[2]
 assert hashlib.sha256(body.encode()).hexdigest()==adoption['science_body_sha256']
 when=j.get('closure_started_at',now.isoformat());j['closure_started_at']=when
 j['phase']='closing-budget';j['final_summary']='final-summary.md'
 j['remaining_window_mode']='Hard cutoff reached; no new study or role tasks. Complete final reviewed publication then formally pause both schedulers and verify actual configs.'
 (S/'status.json').write_bytes((json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode())
 header='# Maxwell十小时研究总结\n\n授权窗口为2026-10-17 21:09:45至2026-10-18 07:09:45（北京时间），现已结束。记录生成于'+when+'。同步与定时器的实际关闭状态由主控操作后回执和最终回复记录。\n\n'
 footer='\n文献与证据分层见[排重结论表](同条件排重-结论表-v001.md)，后续目标与资料见[需确定的事项](待用户决定-本轮收束-v001.md)。\n'
 put_same_or_new(S/'final-summary.md',header+body+footer)
 card='# T-M001 v023：预算截止交付\n\n时间：'+when+'\n\n用户已选A理论方向保持，最终题目/主要贡献未由团队代定。当前主稿narrative-v003已审并发布；固定D峰集合、连续端点和完整连续D域均按各自许可条件保留，连续类固定D峰集合仍未解决。主稿原10公式、实际一张4行表及图/数字/机器输入合同在v003仅最小衔接中保持。\n\n新增原文阅读页与书目指针不提升具体发表优先权，核心同条件覆盖仍未知。广义反升有先例，能量分账/Green与Hölder/比较与连通工具均经典。真实建筑减幅/最优布局未验证；193完整组合及共同192只是导出子集，给定ETABS力的条件检查不当实测或前向。\n\n最小下一步是一个目标/方向/指标、实际属性及背景/输入身份、端点与相关模态、完整力和合格无装置参考。最多176端点仅在88个两端单元假设下的集合计数，不认证现状几何或截断收敛。\n\n科研正文候选经R034/R029及根核后按原字节接入最终总结。已到07:09:45，不再派新研究；最后Git与两自动化正式暂停状态须由随后真实工具回执证明。窗口结束不表示论文所有问题已解决。需要新的研究预算由用户另行安排。\n'
 put_same_or_new(S/'topic-cards/T-M001-v023.md',card)
 line=when+' R028到期收束：已核真实时间/六角色快照，停止新研究；最终总结科研正文逐字取已审候选body，未新造证据，T-M001 v023保留A/未决。最终Git与正式暂停仍待实际工具，不预写成功。'
 for name in ['runs.md','rounds/R028.md','topic-cards/events.md']:
  p=S/name;t=p.read_text('utf-8')
  if line not in t:p.write_bytes((t+'\n'+line+'\n').encode())
 d=R/'docs/Maxwell六角色协作-20261017.md';t=d.read_text('utf-8');marker='## 当前阅读入口\n\n'
 entry=when+' [十小时最终说明](../research/sessions/20261017-2109/final-summary.md)已按实际截止生成，主稿为[叙述v003](../papers/damping-output-boundaries/manuscript/maxwell-paper-narrative-v003.md)。具体发表排重与实际工程布置验证仍未完成；同步和定时器关闭以主控后置回执/最终回复为准。\n\n'
 if entry not in t:
  assert t.count(marker)==1;t=t.replace(marker,marker+entry,1);d.write_bytes(t.encode())
 for role,poll in snapshot['roles'].items():
  entry=j['roles'][role];entry.update(cursor=poll['cursor'],actual_status=poll['thread']['status'],actual_status_at_snapshot=poll['thread']['status'],turn_status=poll['latestTurn']['status'],observed_at_utc=snapshot['at_utc'],snapshot_note='Actual hard-cutoff snapshot; no new dispatch',dispatch='Budget ended; all prior artifacts collected, no new research')
 j['latest_topic_card']='topic-cards/T-M001-v023.md';j['final_summary_sha256']=sha(S/'final-summary.md')
 j['cutoff_science_body_sha256']=adoption['science_body_sha256']
 (S/'status.json').write_bytes((json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode())
 print(json.dumps({'generated_at':when,'final_summary_sha256':j['final_summary_sha256'],'science_body_copied_exact':True,'scheduler_pause_not_yet_claimed':True}))
if __name__=='__main__':main()
