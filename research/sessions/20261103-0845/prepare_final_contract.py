from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];P=R/'papers/damping-output-boundaries/manuscript'
def sha(b):return hashlib.sha256(b).hexdigest()
f=json.loads((S/'roles/audit/R002/freeze.json').read_text(encoding='utf-8'))
for x in f['files']:assert sha((S/'roles/audit/R002'/x['path']).read_bytes())==x['sha256']
md=P/'p06-sh3-sh4-session023-v002.md';sup=S/'roles/writing/SHW3X-SHW4X-辅助分析资料.md'
assert sha(md.read_bytes())=='8906450fd3ad926e13f3a05de332d692944a6a6e50d43e36a127628b49f9d7c0'
assert sha(sup.read_bytes())=='b41d6563d5daa991d77644531ca14c3038036cd8e65f6979dcb7a5a011c14268'
main_replacements=[['软件峰值取绝对值，参照项按参照方向保留符号。','所列两条软件原始峰值均为负，表中取绝对值；参照项按自身方向保留符号。'],['SHW3X-SHW4X-辅助分析资料.md','SHW3X-SHW4X-辅助分析资料-v002.md']]
supp_replacements=[['相对均方误差','归一化均方根误差'],['两条记录的自身峰差分别为595.4876kN和1150.3464kN，分母及峰时都保留各自输入身份。','SHW3X与SHW4X的基准—参考绝对峰差分别为595.4876kN和1150.3464kN，减幅分母及峰时均按各自输入保留。'],['|输入|阻尼状态/%|','|输入|参照阻尼比/%|']]
out={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'review':'roles/audit/R002/v002-final-correctness-review.md','must':0,'adopted':['S1','S2','O1','O2'],'main':{},'supplement':{},'allow_word_after_exact_source_hash_match':True,'new_science_or_numerics':False}
for key,path,pairs,target in [('main',md,main_replacements,P/'p06-sh3-sh4-session023-v003.md'),('supplement',sup,supp_replacements,S/'roles/writing/SHW3X-SHW4X-辅助分析资料-v002.md')]:
 t=path.read_text(encoding='utf-8')
 for old,new in pairs:assert t.count(old)==1,(key,old);t=t.replace(old,new,1)
 b=t.encode('utf-8');out[key]={'source':path.relative_to(R).as_posix(),'target':target.relative_to(R).as_posix(),'replacements':pairs,'expected_bytes':len(b),'expected_sha256':sha(b)}
(S/'final-exact-change-contract.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'final-review-adoption.md').write_text('# 最终内容审查采用\n\n根已完整读v002与补充、R002正式审稿和清单；must0，新增40数值格及原5表/5公式/3图保持通过。采纳S1误差名称、S2波名峰差对应及O2参照表头；O1以一条事实短句说明两原生峰为负。只按精确契约另存v003和补充v002，不新计算、不改数据。契约预先给出源SHA，匹配即可授权唯一作者继续Word，无需重复科学审稿。最终根核精确diff与Word全部页/数字/公式。\n',encoding='utf-8')
print(json.dumps({k:out[k] for k in ['at','main','supplement']},ensure_ascii=False))
