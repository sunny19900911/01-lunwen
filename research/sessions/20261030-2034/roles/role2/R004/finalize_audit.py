from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
O=Path(__file__).parent;R=O.parents[5];SRC=R/'research/sessions/20261030-2034/roles/role4/R003'
now=lambda:datetime.now(timezone(timedelta(hours=8)))
deadline=datetime.fromisoformat('2026-10-30T21:20:59+08:00')
assert now()<deadline,'deadline; do not start further arithmetic'
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(name,obj):
    with (O/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
allrows=rows(SRC/'all12-prediction-errors-144.csv');summary=rows(SRC/'all12-validation-summary-24.csv')
count=0
for s in summary:
    rr=[x for x in allrows if x['N']==s['N'] and x['Story']==s['Story']]
    held=next(float(x['NRMSE']) for x in rr if x['Case']=='RH4X' and float(x['zeta'])==.05)
    r8=[x for x in rr if float(x['zeta'])==.08]
    expected={'heldout5_NRMSE':held,'fixed8_NRMSE_min':min(float(x['NRMSE']) for x in r8),'fixed8_NRMSE_max':max(float(x['NRMSE']) for x in r8),'fixed8_peak_error_min':min(float(x['peak_relative_error']) for x in r8),'fixed8_peak_error_max':max(float(x['peak_relative_error']) for x in r8)}
    for k,v in expected.items():assert abs(float(s[k])-v)<1e-14;count+=1
save('summary-arithmetic-checks.json',{'completed':now().isoformat(),'N':[24,36],'summary_rows':len(summary),'numeric_checks':count,'must_count':0,'scope':'summary against delivered per-case metrics only; no independent N24 regression'})
ind=rows(O/'independent-validation-48.csv');checks=json.loads((O/'checks.json').read_text(encoding='utf-8'));fit=json.loads((O/'independent-fit-small.json').read_text(encoding='utf-8'))
worst=json.loads((O/'worst-first.json').read_text(encoding='utf-8'))
stories=['Story'+str(i) for i in range(1,13)]
lines=['# R004｜N36全12层独立数值审核','',
'结论：独立复算48条验证记录、288个数值，与④R003冻结交付一致，数值核验0 must。72个原生缓存组的键、单位、完整网格与SourceRow定位通过。Story11误差最大，且一条8%记录存在显著峰时偏差；输出拟合一致不等于峰时准确或真实逐阶分解唯一。','',
'## 独立结果小表','',
'下表为独立计算的NRMSE百分数。5%仅列整波留出的RH4X，8%三波均使用同一5%训练映射。','',
'| 层 | 5% RH4X留出/% | 8% SHW3X/% | 8% SHW4X/% | 8% RH4X/% |',
'|---|---:|---:|---:|---:|']
for story in stories:
    rr=[x for x in ind if x['Story']==story]
    vals=[next(float(x['NRMSE'])*100 for x in rr if x['Case']==c and float(x['zeta'])==z) for c,z in [('RH4X',.05),('SHW3X',.08),('SHW4X',.08),('RH4X',.08)]]
    lines.append('| '+story+' | '+' | '.join(f'{v:.6f}' for v in vals)+' |')
lines+=['','## 指定关键层的峰值与峰时','',
'峰为各曲线独立寻得的绝对最大值；峰差=(预测峰−原生峰)/原生峰。以下12条关键记录及其余36条完整精度均在independent-validation-48.csv。','',
'| 层 | 波 | ζ | 原生峰/kN | 预测峰/kN | 峰差/% | 原生峰时/s | 预测峰时/s |',
'|---|---|---:|---:|---:|---:|---:|---:|']
for story in ('Story1','Story7','Story11'):
    for x in (x for x in ind if x['Story']==story):
        lines.append(f"| {story} | {x['Case']} | {float(x['zeta'])*100:.0f}% | {float(x['native_peak_kN']):.6f} | {float(x['predicted_peak_kN']):.6f} | {float(x['peak_relative_error'])*100:+.6f} | {float(x['native_peak_time_s']):.2f} | {float(x['predicted_peak_time_s']):.2f} |")
lines+=['','## 验证范围与数值尺度','',
'④清单冻结于21:07:18+08；16个文件的字节数与SHA256在科学计算前全部核验。本轮预检曾先查看清单、README与CSV表头，guard如实记录。输入规则列出的15个源哈希均通过。原始大Excel未打开。','',
'原生两个缓存manifest按Story、Location=Bottom、Output Case精确选组；5%另限制Case Type=NonModHist。72组VX单位为kN，Time与冻结ag网格逐值相同，SourceRow为唯一整数并保留峰行定位；48个原生峰SourceRow与交付逐项一致。未回读原Excel验证源行内容，此处认证缓存定位一致。','',
'仅读取批准旧loader的同一ag/ω[:36]并复用states积分核；拟合与指标均独立实现，不import④脚本，不从④逐阶项恢复基。仅将两波5%原生输出拼成12输出矩阵，一次lstsq；RH4X整波留出。8%不重拟合，48条使用同一系数指纹。独立审核包含旧Story5/12的重算，但未改写旧冻结成果；④生产结果仍按约定复用旧两层。','',
f"288项中的最大NRMSE差为{checks['max_abs_difference']['NRMSE']:.3e}，预测峰差为{checks['max_abs_difference']['predicted_peak_kN']:.3e} kN，峰差比例差为{checks['max_abs_difference']['peak_relative_error']:.3e}；原生峰、两类峰时差均为0。采用逐量容差1e-8×max(1,|交付值|)，通过不等于预测等于原生。",'',
f"独立L2列缩放矩阵秩{fit['rank']}、条件数{fit['condition']:.7g}，最小/最大奇异值比{fit['sigma_min_over_max']:.7g}。R003已核两个rcond均未实际截断最弱方向；本轮不重复双阈值回归。高条件数及扩阶后误差改善不认证高阶物理分量唯一。",'',
'N24/N36汇总表24行×5字段共120项算术核验通过，仅由冻结逐波指标重新取留出值、8%极值；没有重跑N24回归。低/高组曲线、同刻抵消与残差表不在本轮独立审核范围。','',
'## 必须保留的适用限制','',
'Story11/RH4X：5%留出NRMSE=5.716602%，峰时21.68→21.70 s；8%NRMSE=4.552383%，峰差=-1.084287%，峰时16.64→21.70 s，相差5.06 s。两层先前表现不能代表全楼同等精度；曲线NRMSE较小和峰幅误差较小不能推出峰时可靠。该偏差是参照模型的已知限制，不是本次复算不一致。','',
'RH4X为记录独立的回顾性留出；N36在已见较低N误差后选择，不能称为完全未参与模型选择的新盲测。只支持固定M/K和同输入下此输出参照的误差陈述，不上升为逐模态真实唯一识别。','',
f"实际起点21:10:59+08，数值核验完成{checks['completed']}；清单另记最终封存时间，截止21:20:59。到此停止，不新增N、8%重拟合或物理求解。",'']
with (O/'review.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines))
files=[]
for p in sorted(O.iterdir()):
    if p.is_file() and p.name!='manifest.json':
        b=p.read_bytes();files.append({'name':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
t=now();m={'status':'complete scoped N36 all12 numerical audit','frozen_Asia_Shanghai':t.isoformat(),'started_Asia_Shanghai':'2026-10-30T21:10:59+08:00','deadline':deadline.isoformat(),'within10_minutes':t<=deadline,'elapsed_seconds':(t-datetime.fromisoformat('2026-10-30T21:10:59+08:00')).total_seconds(),'independent_validation_rows':48,'independent_numeric_checks':288,'numeric_must_count':0,'summary_arithmetic_checks':120,'native_groups_checked':72,'target_refits':0,'scope_limit':'no N24 regression; no low/high decomposition audit; shared approved states integrator','source_manifest_sha256':hashlib.sha256((SRC/'delivery-manifest.json').read_bytes()).hexdigest(),'files':files}
save('manifest.json',m)
for e in m['files']:
    b=(O/e['name']).read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
print(json.dumps({k:v for k,v in m.items() if k!='files'},ensure_ascii=False))
