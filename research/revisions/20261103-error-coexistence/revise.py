from pathlib import Path
from decimal import Decimal
import csv,json,hashlib,re,ast
H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'papers/damping-output-boundaries/manuscript/p06-mechanism-classification-v002.md'
dst=src.with_name('p06-mechanism-classification-v003.md')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='74fbdcc680c635cf29655939e8eb2ecc5722b6c3280a857e4d0311e7258bc828'
assert not dst.exists()
rows=list(csv.DictReader((R/'research/sessions/20261103-0845/roles/audit/R001/independent-story5-four-states.csv').open(encoding='utf-8-sig')))
errors=[]
for case in ['SHW3X','SHW4X']:
    row=next(x for x in rows if x['Case']==case and x['zeta']=='0.08')
    a=Decimal(row['reference_at_native_peak_signed_kN']);b=Decimal(row['native_peak_abs_kN'])
    e=100*(abs(a)/b-1)
    assert abs(e-Decimal(row['reference_peak_error_percent']))<Decimal('0.00000000001')
    errors.append({'case':case,'reference_at_native_peak_kN':str(a),'native_peak_abs_kN':str(b),'relative_error_percent':str(e),'table_5_decimal_places':f'{e:.5f}'})
s=src.read_text(encoding='utf-8')
old='针对附加阻尼后各层剪力改善不同、改善较小与绝对需求较大未必由同一输入控制的问题，以双塔连体结构为例，建立逐层多输入剪力复核流程。比较相同输入的基准模型与增加3个百分点模态阻尼的参考模型，形成14个方向工况、12层的168条成对记录。24个楼层—方向组中有19组的两类控制输入不同。'
new='附加阻尼后，同一楼层剪力“减幅最小”和“绝对需求最大”的控制输入可能不同，工程复核需分别保留两类记录。本文以双塔连体结构为例，比较相同输入下基准模型与增加3个百分点模态阻尼的参考模型，整理14个方向工况、12层的168条成对记录，发现24个楼层—方向组中有19组的两类控制输入不同。'
assert s.count(old)==1;s=s.replace(old,new)
old='A story-by-story, multi-input procedure is presented for shear assessment of a coupled twin-tower structure. The baseline model and a reference model with three additional percentage points of modal damping are compared under identical inputs, using 168 paired records from 14 directional cases and 12 stories. The inputs controlling minimum reduction and maximum reference shear differ in 19 of the 24 story-direction groups.'
new='After damping is added, the input producing the smallest story-shear reduction may differ from that producing the largest absolute demand, so both governing records need to be retained in engineering checks. For a coupled twin-tower structure, the baseline model and a reference model with three additional percentage points of modal damping are compared under identical inputs. Among 168 paired records from 14 directional cases and 12 stories, the two governing inputs differ in 19 of the 24 story-direction groups.'
assert s.count(old)==1;s=s.replace(old,new)
old='|参照合成/kN|+8096.35|+9028.47|'
new=old+f'\n|相对误差/%|{errors[0]["table_5_decimal_places"]}|{errors[1]["table_5_decimal_places"]}|'
assert s.count(old)==1;s=s.replace(old,new)
old='|参照第13阶项/kN|+28.36|−1.68|'
new=old+'\n\n相对误差按参照合成绝对值与软件剪力绝对峰之比减1后乘100%计算，采用未舍入数值。两条记录的误差分别为0.00245%和0.00806%，表明控制峰幅值高度接近；下述逐阶项仍按固定线性参照解释。'
assert s.count(old)==1;s=s.replace(old,new)
old='上述分类用于确定“先查哪条记录、哪一阶、哪一类构件或参数”。'
addition='两类作用可能在同一控制输入下并存：较大的低阶项形成较高需求，反向高阶项的抵消若随增阻尼减弱，则又可能抵消部分同向项下降带来的改善。复核时应同时检查主导项幅值和反向项变化，并保留其他模态共同合成，不能只选其中一类解释。\n\n'
assert s.count(old)==1;s=s.replace(old,addition+old)
dst.write_text(s,encoding='utf-8',newline='\n')
assert re.findall(r'\$\$.*?\$\$',s,re.S)==re.findall(r'\$\$.*?\$\$',src.read_text(encoding='utf-8'),re.S)
assert re.findall(r'!\[.*?\]\(.*?\)',s)==re.findall(r'!\[.*?\]\(.*?\)',src.read_text(encoding='utf-8'))
W=H/'word';W.mkdir(exist_ok=True)
old=R/'research/revisions/20261103-1407-mechanism-classification'
for name in ['build_word.py','math_omml.py','render_review.py']:
    b=(old/'word'/name).read_bytes();ast.parse(b.decode('utf-8'));(W/name).write_bytes(b)
(H/'check_final_word.py').write_bytes((old/'check_final_word.py').read_bytes())
(H/'publish_checkpoint.py').write_bytes((old/'publish_checkpoint.py').read_bytes())
author=(old/'word/author_word.py').read_text(encoding='utf-8').replace(src.name,dst.name).replace('论文审阅稿-v002.docx','论文审阅稿-v003.docx').replace(hashlib.sha256(src.read_bytes()).hexdigest(),hashlib.sha256(dst.read_bytes()).hexdigest())
ast.parse(author);(W/'author_word.py').write_text(author,encoding='utf-8',newline='\n')
report={'source':src.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':dst.relative_to(R).as_posix(),'output_bytes':dst.stat().st_size,'output_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'errors_from_unrounded_data':errors,'formulae_and_figures_unchanged':True,'new_table_numeric_cells':2,'no_new_model_or_ODE':True}
(H/'change-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
