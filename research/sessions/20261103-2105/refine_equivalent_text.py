from pathlib import Path
import json,csv,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-control-check-session028-v001.md';out=M/'p06-control-check-session028-v002.md';assert not out.exists()
t=src.read_text(encoding='utf-8')
old='由原生轴力和α=0.3本构求黏滞单元速度，在0—15s内按耗能相同确定等效黏滞系数，再用原生装置总变形驱动线性Maxwell模型；15s后的响应用于检验。两处待检查的16.62s和21.64s均不参与系数确定。'
new='由原生轴力和α=0.3本构求黏滞单元速度，以原非线性黏滞运动为参照，按耗能等效确定黏滞系数。分别采用0—15s定参、15s后检验，以及0—50s整个响应水平定参两种方案，两者均用原生装置总变形驱动线性Maxwell模型。前者的16.62s、21.64s未参与定参；后者使用整段实际记录，属于事后等效对照。'
assert t.count(old)==1;t=t.replace(old,new)
start=t.index('|时刻/s|实际QD/kN|规定运动下线性等效QD/kN|');end=t.index('\n\n两种装置计算均保留',start)
with (S/'roles/equivalent/equivalent-QD-two-times.csv').open(encoding='utf-8-sig',newline='')as f:a=list(csv.DictReader(f))
with (S/'roles/equivalent/R002/whole-response-QD-two-times.csv').open(encoding='utf-8-sig',newline='')as f:b=list(csv.DictReader(f))
table='|时刻/s|实际QD/kN|0—15s定参等效QD/kN|全程定参等效QD/kN|\n|---|---:|---:|---:|\n'
for x,y in zip(a,b):table+=f"|{float(x['time_s']):.2f}|{float(x['native_QD_kN']):.2f}|{float(x['linear_prescribed_u_QD_kN']):.2f}|{float(y['linear_whole_response_QD_kN']):.2f}|\n"
t=t[:start]+table.rstrip()+t[end:]
t=t.replace('两种装置计算均保留21.64s出力绝对值大于16.62s的次序，但15—50s装置合力的相对RMS差为46.00%。这一差异说明，用一个固定等效黏滞系数概括整段非线性装置响应仍有较大偏差。','两种等效方案与实际装置计算均保留21.64s出力绝对值大于16.62s的次序。0—15s定参方案在15—50s的装置合力相对RMS差为46.00%；全程定参方案在0—50s的相对RMS差为42.64%。这两种固定系数等效在各自评价范围内均有较大偏差；全程定参使用了全部实际响应，不能当作独立验证。')
out.write_text(t,encoding='utf-8',newline='\n')
(S/'equivalent-text-refinement.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'only_section_5_3_changed':t.split('### 5.3')[0]==src.read_text(encoding='utf-8').split('### 5.3')[0] and t.split('### 5.4')[1]==src.read_text(encoding='utf-8').split('### 5.4')[1]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)
