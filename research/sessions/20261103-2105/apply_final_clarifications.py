from pathlib import Path
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-control-check-session028-v003.md';out=M/'p06-control-check-session028-v004.md';assert not out.exists()
t=src.read_text(encoding='utf-8');changes=[
('# 黏滞阻尼器作用下楼层剪力控制输入与控制时刻的识别','# 阻尼器作用下楼层剪力的控制输入与控制时刻'),
('对基准原峰时刻t₁和任一候选时刻t₂，按第5.2节的绝对值定义比较原需求差与两时刻降低量之差：','对基准原峰时刻t₁和任一候选时刻t₂，记b_i=|V_B(t_i)|、d_i=|V_D(t_i)|、δ_i=b_i−d_i。比较原需求差与两时刻降低量之差：'),
('以原非线性黏滞运动为参照，按耗能等效确定黏滞系数。','以原非线性黏滞单元的速度历程为参照，用其耗能与速度平方积分之比确定等效黏滞系数。'),
('0—15s定参方案在15—50s的装置合力相对RMS差为46.00%；','相对RMS差以相同评价时段的原生装置水平合力RMS为分母。0—15s定参方案在15—50s的装置合力相对RMS差为46.00%；'),
('https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Cuts.htm.','[官方页面](https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Cuts.htm)。')]
for old,new in changes:
 assert t.count(old)==1,(old,t.count(old));t=t.replace(old,new)
out.write_text(t,encoding='utf-8',newline='\n')
(S/'final-clarification-adoption.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'final_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changes':[{'before':a,'after':b}for a,b in changes],'scientific_numeric_values_changed':False,'new_experiments':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(out)
