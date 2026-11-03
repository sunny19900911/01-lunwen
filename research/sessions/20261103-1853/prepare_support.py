from pathlib import Path
import json,csv,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];prev=R/'research/sessions/20261103-1700'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def mt(head,rows):return '\n'.join(['|'+'|'.join(head)+'|','|'+'|'.join(['---']*len(head))+'|']+['|'+'|'.join(map(str,row))+'|' for row in rows])
eight=read(S/'roles/response/Story8-actual-peak-accounting-6.csv');ten=read(S/'roles/response/R002/Story10-RH4Y-peak-accounting-1.csv')
allr=eight+ten
text='''# 实际控制时段与完整附表

本轮实际5.2只用B/D原生Bottom剪力及实际装置水平合力。旧固定300阶线性机制移至[补充A](补充A-线性机制与实际模态恢复.md)，实际坐标恢复的进展和未闭合步骤也放在该补充内。原六工况72条主分析、24组双控制统计均沿[上轮工程资料](../20261103-1700/工程资料与完整附表.md)。

## 选择比较记录

先完整保留第8层RH4/SHW4/SHW7各X/Y六项，其两模型峰时最大差只有0.22s。因此不能把第8层硬写成跨时段大迁移。根据上轮已冻72表，限定原生P完整的第8—11层24项，以最大|t_D−t_B|选取RH4Y第10层（5.02s），只追加此一项。图并列第8层RH4X（0.06s）与第10层RH4Y，其他五项不删。

## 七条实际记录的两个控制峰

以下量来自同一输入的完整保存时间，未补零/移时/换符号/平滑。S按原基准峰的有符号方向定义，M是自身绝对峰与该同向读数之差；它们是实际峰值核对恒等式，不是因果或模态/相位份额。本文选入图的两个例子，B/D两个控制时刻的剪力均为正。详见原生[18行三时刻表](roles/response/Story8-native-three-times-18.csv)及[新增3行表](roles/response/R002/Story10-RH4Y-three-times-3.csv)。

'''
text+=mt(['层/输入','t_B/s','t_D/s','B(t_B)/kN','D(t_B)/kN','B(t_D)/kN','D(t_D)/kN','r_at/%','r_D/%','d/百分点'],[
 [r['Story']+'/'+r['Case']]+[f"{float(r[k]):.6f}" for k in ['t_B_s','t_D_s','B_signed_at_tB_kN','D_signed_at_tB_kN','B_signed_at_tD_kN','D_signed_at_tD_kN','r_at_percent','r_D_peak_percent','d_pp']] for r in allr])
text+='\n\n## 同刻装置出力\n\nQD=ΣnP为J端结构内力抵抗项，节点外力相反。每层8只装置，实际方向逐只投影，I/J重复P只计一次；QT与QD不物理相减生成主体QS。\n\n'
text+=mt(['层/输入','QD(t_B)/kN','QD(t_D)/kN','QD绝对峰/kN','tQD/s','tB同刻/自身峰/%','tD同刻/自身峰/%'],[
 [r['Story']+'/'+r['Case']]+[f"{float(r[k]):.6f}" for k in ['QD_signed_at_tB_kN','QD_signed_at_tD_kN','P_QD_abs_kN','t_QD_s','QD_abs_at_tB_over_own_peak_percent','QD_abs_at_tD_over_own_peak_percent']] for r in allr])
text+='''

## 两时刻解析关系与复核

取b_i=|V_B(t_i)|，d_i=|V_D(t_i)|，δ_i=b_i−d_i，t1=tB、t2=tD。则d2−d1=(δ1−δ2)−(b1−b2)。此关系比较已经取得的两状态时程，不能表述为输入前的减震预测或装置力直接贡献。

RH4Y第10层原差109.6008322438kN，降低量δ1=1461.7484684581、δ2=771.7559594893kN，差689.9925089688kN，因此D后时刻更高580.3916767251kN。独审见[two-time-identity-audit.json](roles/audit/two-time-identity-audit.json)。

实际同刻数值独审591字段一致，见[actual-sametime-audit.json](roles/audit/actual-sametime-audit.json)。旧q恢复契约与本轮投影算法独审另见roles/audit；所有完整投影数组只保留local-cache。

## 实际模态坐标与剩余数据项

本轮确实读取实际CM时程并尝试第2/13阶恢复。q_obs=N⁻¹AᵀM_obs u_obs是CM平动的质量加权观测投影；缺完整内积及其余模态影响界，不能去掉下标obs而称为实际FNA q。第13阶投影在两控制时刻变化方向不同，不能只选一个时刻来保留旧机制。

原生FNA q或完整质量投影取得后，还需独立目标剪力恢复映射及软件切口/包含关系。动力恢复路径则需完整模态背景、初态、输入与全部非线性广义力；当前32/88完整P及部分CM端点信息不足以替代这些量。这里说明已尝试和下一项具体数据，不启动新的模型求解或要求用户本轮先补表。
'''
p=S/'实际控制时段与完整附表.md';assert not p.exists();p.write_text(text,encoding='utf-8',newline='\n')
W=S/'word';W.mkdir(exist_ok=True)
for name in ['build_word.py','math_omml.py','render_review.py']:
 p=W/name;assert not p.exists();p.write_bytes((prev/'word'/name).read_bytes())
p=W/'build_word.py';s=p.read_text(encoding='utf-8')
s=s.replace('EXPLICIT_INLINE_MATH = {',r'''EXPLICIT_INLINE_MATH = {
 't₁=t_B':r't_1=t_B', 't₂=t_D':r't_2=t_D',
 'b_i=|V_B(t_i)|':r'b_i=|V_B(t_i)|', 'd_i=|V_D(t_i)|':r'd_i=|V_D(t_i)|',
 'δ_i=b_i−d_i':r'\delta_i=b_i-d_i',
 'QD(t_B)':r'Q_D(t_B)', 'QD(t_D)':r'Q_D(t_D)',
''')
s=s.replace("elif header==['量','SHW3X','SHW4X']:widths=[8.0,4.5,4.5]", "elif header[0]=='量' and len(header)==3:widths=[8.4,4.3,4.3]\n  elif header[0]=='楼层/输入' and len(header)==6:widths=[3.1,2.5,2.5,3.0,1.8,4.1]")
p.write_text(s,encoding='utf-8',newline='\n')
gate=(prev/'check_final_word.py').read_text(encoding='utf-8')
gate=gate.replace("assert any('V' in x and 'q' in x and ('φ' in x or 'ϕ' in x) for x in flat),'Modal shear summand lost q or phi'", "assert any('δ' in x and 'b' in x and 'd' in x for x in flat),'Two-time peak relation lost delta/b/d operands'")
gate=gate.replace("'20261103-1700' in x.get('Target','')", "'20261103-1853' in x.get('Target','')")
gate=gate.replace("assert any('engineering-data-and-full-tables' in x.get('Target','') for x in links),'Engineering supplementary hyperlink missing'", "assert any('20261103-1700' in x.get('Target','') for x in links),'Prior complete engineering tables hyperlink missing'")
p=S/'check_final_word.py';assert not p.exists();p.write_text(gate,encoding='utf-8',newline='\n')
print(json.dumps({'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'new_supplement':True,'word_prepared_only':True,'native_gate_updated_for_actual_two_time_relation':True},ensure_ascii=False))
