from pathlib import Path
import datetime, hashlib, json, subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
source=R/'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-v004.md'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='b66b072aeca3019146e41664ce71ae81475d198410bf505e53afaf054d76ffe3'
(S/'local-cache').mkdir(exist_ok=True)
(S/'local-cache'/'initial-git-status.txt').write_text(subprocess.check_output(['git','status','--short'],cwd=R).decode('utf-8',errors='replace'),encoding='utf-8')
plan='''# 实际方案为主的工程论文改写

用户最新授权：把实际阻尼器方案提升为工程主体；继续推进主线。沿用必要多角色、正常白名单Git与最终Word交付的授权，不启动旧计时研究或新后台任务。

## 本轮范围与结束条件

完成一轮有实质数据增量的改写：实际六方向工况72条为主，原14方向工况168条为扩展对照，固定300阶线性参照与三层模型压缩为辅助机制解释。交已独审MD和渲染逐页检查Word后结束，不索新数据、不求解、不扩ODE或装置布置优化。

## 责任

主控唯一作者/共享账本/Git；response只写roles/response，派生实际D/B逐层范围及可用的原峰时偏差；audit只写roles/audit，独核实际主线和最终稿；pairing只写roles/method，检查非线性比较及机制范围。旧1458会话与所有旧稿保持原字节。

## 工作契约

实际输入只有RH4/SHW4/SHW7各X/Y，共6方向而非6独立事件；不冒充14实际工况/168条实际记录。D/B是所提供工程方案相对基准的软件响应比较，不称实测，不认完整内部设置全部同一。QT不扣未认证包含性的QD。局部原生P范围32只不补全88。

实际原峰时偏差若新算，必须直接来自B/D完整保存网格；不得把原M偏差搬给D。实际逐阶解释仍需真实非线性q及力恢复关系，旧线性300阶只说明可能机制。

## 交付与同步

新唯一稿名前缀p06-actual-main-session026-。正常Git仅当前会话冻结小文本/代码/CSV/PNG/SVG及本轮稿/最终Word；不收任何local-cache、原Excel/EDB、第三方全文、旧脏文件，不整目录stage。命令级代理、逐blob校验、普通push及lsremote核；不force/reset/登录或凭据访问。检查点按真实时间记录，不为凑周期重复实验。
'''
(S/'plan.md').write_text(plan,encoding='utf-8',newline='\n')
(S/'status.json').write_text(json.dumps({'phase':'actual-mainline-analysis','started_at':now,'checkpoint_open':False,'source':source.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'no_solver_or_new_ODE':True,'author':'root','agents':['p06_actual_response','p06_actual_audit','p06_actual_pairing'],'automation_created':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'claims.md').write_text('''# 本轮主张

- C01 supported：实际方案六工况72条、24层—方向组两类控制不同12组；旧168/19组独立作扩展参照。
- C02 testing：实际方案逐层min/median/max及底层/平均漏查，待本轮独算。
- C03 testing：D/B原峰时偏差，依完整缓存可用性派生并独核，不借M。
- C04 supported有限：旧线性模态及三层说明叠加机制，不自动解释实际D逐阶。
- C05 supported：88几何和32只完整出力沿用1458正式已核结果。
''',encoding='utf-8',newline='\n')
(S/'runs.md').write_text(f'# 运行记录\n\n{now}：源稿v004/旧会话已关闭。本轮三项followup正式派发，角色只写新目录；原始数据只读，先复用现有缓存。根为唯一作者。\n',encoding='utf-8',newline='\n')
print(json.dumps({'started_at':now,'source_bytes':source.stat().st_size},ensure_ascii=False))
