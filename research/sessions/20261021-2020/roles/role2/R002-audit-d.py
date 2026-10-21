from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal as D, getcontext
import csv, hashlib, json
getcontext().prec=40
B=Path(__file__).resolve().parent;R=B.parent/'role4';START=datetime.fromisoformat('2026-10-21T21:01:03.494008+08:00')
def ident(p):
    b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def rc(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def eq(a,b):assert abs(D(str(a))-D(str(b)))<D('1e-10'),(a,b)
def js(n,x):
    p=B/n;assert not p.exists();p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));json.loads(p.read_text(encoding='utf-8'))
assert not (B/'R002-validation.json').exists()
sources=[ident(R/'R001-delivery-manifest.json')]
for x in json.loads((R/'R001-delivery-manifest.json').read_text(encoding='utf-8'))['files']:
    got=ident(Path(x['path']));assert got['bytes']==x['bytes'] and got['sha256']==x['sha256'];sources.append(got)
definition=json.loads((R/'R001-input-definition.json').read_text(encoding='utf-8'));source=Path(definition['source']);got=ident(source);assert got['sha256']==definition['source_sha256'];sources.append(got)
raw=rc(source);out=rc(R/'R001-d-168.csv');summary=json.loads((R/'R001-d-summary.json').read_text(encoding='utf-8'))
key=lambda r:(r['Case'],r['Story'],r['Axis'],r['Location'])
ri={key(r):(i,r) for i,r in enumerate(raw,2)};assert len(out)==len(ri)==168 and len({key(r) for r in out})==168
computed=[]
for row in out:
    i,r=ri[key(row)];p0,p1,a=D(r['P0_kN']),D(r['P3_kN']),abs(D(r['label3_at_label0_peak_kN']));assert p0>0 and 0<=a<=p1
    rat=D(100)*(1-a/p0);d=D(100)*(p1-a)/p0;rp=D(100)*(1-p1/p0);assert abs(rp-(rat-d))<D('1e-35')
    for k,v in [('P_B_kN',p0),('P_M_kN',p1),('V_M_at_tB_signed_kN',r['label3_at_label0_peak_kN']),('A_abs_V_M_at_tB_kN',a),('r_at_percent',rat),('d_pp',d),('r_peak_percent',rp),('t_B_s',r['t_peak0_s']),('t_M_s',r['t_peak3_s']),('source_CSV_line',i),('source_row_B_peak',r['source_row0']),('source_row_M_peak',r['source_row3'])]:eq(row[k],v)
    assert abs(D(row['identity_residual_pp']))<D('1e-10')
    computed.append({'Case':r['Case'],'Story':r['Story'],'PB':str(p0),'PM':str(p1),'A':str(a),'r_at':str(rat),'d_pp':str(d),'r_peak':str(rp),'tB':r['t_peak0_s'],'tM':r['t_peak3_s'],'source_line':i})
vals=sorted(D(r['d_pp']) for r in computed)
def quantile(p):
    x=D(p)*(len(vals)-1);i=int(x);return vals[i] if i==len(vals)-1 else vals[i]+(x-i)*(vals[i+1]-vals[i])
qq={p:str(quantile(p)) for p in ['0','.25','.5','.75','.9','.95','1']}
for p,v in qq.items():eq(summary['d_pp_quantiles'][str(float(p)).rstrip('0').rstrip('.') if p in ['0','1'] else str(float(p))],v)
maximum=max(computed,key=lambda x:D(x['d_pp']));assert(maximum['Case'],maximum['Story'])==('SHW7Y','Story6')
eq(summary['maximum']['d_pp'],maximum['d_pp']);eq(summary['minimum']['d_pp'],vals[0])
top=sorted(computed,key=lambda x:D(x['d_pp']),reverse=True)[:5]
assert [(x['Case'],x['Story']) for x in top]==[(x['Case'],x['Story']) for x in summary['top_five']]
samples=[x for x in computed if (x['Case'],x['Story']) in [('SHW7Y','Story6'),('RH4X','Story1'),('SHW4Y','Story7'),('R1X','Story12')]]
assert len(samples)==4 and summary['all_tied_peak_times_audited'] is False
for x in sources:assert ident(Path(x['path']))==x
report='''# R002｜168行原峰时偏差d独立数值审核

**通过，可进入新稿。** 用原已审168行CSV，以40位十进制算术独立重算PB、PM、A=|VM(tB)|和三项百分数；全168行键、峰值、同刻有符号值、峰时、源行及r_peak=r_at−d均通过。严格检查A≤PM及PB>0，无负d、未裁零；未运行数据角色脚本或读取数组。

d为“只看基准峰时”减幅相对完整保存记录峰值减幅的高估量，单位为百分点。线性插值分位数独立复核为：最小0、Q25=0、中位0.05578280、Q75=0.50777831、Q90=2.90049937、Q95=4.59062940、最大10.58305117个百分点。偏差分布不均，不能只展示最大值而说所有记录都有显著影响。

最大为SHW7Y／Story6：PB=8091.9866kN、PM=6909.9848kN，参考模型在基准峰时的有符号值−6053.6058kN，A取其绝对值。原峰时减幅25.1901167%，完整记录峰减幅14.6070655%，二者相差10.5830512个百分点；tB=48.88s、tM=38.10s。不是10.5831%的相对误差，也不是相位角或独立装置作用。

最大项、全部前五名与分位数一致，另抽核RH4X／Story1、SHW4Y／Story7、R1X／Story12源字段。结果沿用旧表已选首次峰时，未核全部并列基准峰，因此只能按该锚点规则报告；不能称d对并列峰选择稳定。最小值为0的记录不唯一，摘要示例不应写为唯一最小。

范围仅为已配对基准/模态阻尼参考、同层同轴原生Bottom保存记录，未外推实体装置优劣或连续时间峰，也不减少取得完整PM所需的时程计算。

可直接写稿：“168项记录中，原峰时评价的减幅高估量中位数为0.0558个百分点，但最大达10.5831个百分点。SHW7Y第6层若仅检查基准峰时，会将完整记录的14.6071%峰值减幅报为25.1901%，因此宜同时保留参考模型自身控制峰。”
'''
p=B/'R002-d-number-review.md';assert not p.exists();p.write_bytes(report.encode('utf-8'))
end=datetime.now(START.tzinfo);assert end<=START+timedelta(minutes=5)
js('R002-checks.json',{'source_bindings':sources,'rows_independently_checked':168,'decimal_precision':40,'quantile_rule':'linear at (n-1)p','d_pp_quantiles':qq,'maximum':maximum,'four_source_samples':samples,'all_ties_checked':False,'new_arrays_ODE':0})
js('R002-validation.json',{'status':'pass all168 rows and d quantiles/extrema under existing first-peak rule','actual_start':START.isoformat(),'actual_end':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_5_minutes':True,'only_new_session_role2_written':True})
js('R002-manifest.json',{'frozen_at':end.isoformat(),'files':[ident(B/n) for n in ['R002-audit-d.py','R002-d-number-review.md','R002-checks.json','R002-validation.json']]})
print(json.dumps({'status':'pass','end':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'quantiles':qq,'maximum':maximum},ensure_ascii=False))
