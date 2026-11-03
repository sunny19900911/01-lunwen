from pathlib import Path
import re,json,hashlib,ast
H=Path(__file__).resolve().parent;R=H.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-actual-damper-session025-v001.md';dst=src.with_name('p06-actual-damper-session025-v002.md')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='52f156a71dff7a9973bfe84811a0fed028d4da141ff97d51e3532f0ca4e6cd4f'
assert not dst.exists()
s=src.read_text(encoding='utf-8');changes=[
('实体模型18个质心方向质量与基准、参考表的逐组数值对应','实体模型18个质心的X、Y方向质量与基准、参考表的逐组数值对应'),
('几何相同数量并不意味着水平合力相同','装置数量相同并不意味着水平合力相同'),
('24个楼层—工况的8只装置时程均与楼层输出时间逐点一致','第8—11层合计24个楼层—工况组中，每组8只装置的时程均与楼层输出时间逐点一致'),
('本文不由QT与QD相减另造主体剪力','若需分离主体剪力，应先明确软件截面的受力范围及装置作用的包含方式'),
('明确比较的是基准与附加模态阻尼参考模型','明确比较对象为基准—模态增阻尼参考，或基准—实体阻尼器方案'),
('分别求两模型完整保存时程的绝对峰与峰时，计算r_peak、r_at和d。全部量来自同一记录','分别求所比较模型完整保存时程的绝对峰与峰时。基准—模态参考计算r_peak、r_at和d；实体方案相对基准另列r_D并保留各自峰时。全部量来自同一记录'),
('按最小减幅选择记录时，共同六方向工况对应SHW4Y第7层','对模态增阻尼参考按最小减幅选择记录时，共同六方向工况对应SHW4Y第7层'),
('在目标层及相邻层的完整时程中标出t_B和t_M，并结合d查看原峰时读数与该输入下参考剪力峰的差别。','对基准—模态增阻尼参考，在目标层及相邻层的完整时程中标出t_B和t_M，并结合d查看原峰时读数与该输入下参考剪力峰的差别。实体方案同样保留基准与自身峰时，回到对应时段检查响应。')]
for old,new in changes:
    assert s.count(old)==1,old;s=s.replace(old,new)
dst.write_text(s,encoding='utf-8',newline='\n')
newsha=hashlib.sha256(dst.read_bytes()).hexdigest()
old=R/'research/revisions/20261103-error-coexistence'
W=H/'word';W.mkdir(exist_ok=True)
for n in ['math_omml.py','render_review.py']:
    assert not (W/n).exists();(W/n).write_bytes((old/'word'/n).read_bytes())
build=(old/'word/build_word.py').read_text(encoding='utf-8')
build=build.replace("EXPLICIT_INLINE_MATH = {", "EXPLICIT_INLINE_MATH = {\n 'P_D':r'P_D', 'r_D':r'r_D',\n 'κ=500000kN/m':r'\\kappa=500000\\mathrm{kN}/\\mathrm{m}',\n 'c=477kN(s/m)^0.3':r'c=477\\mathrm{kN}(\\mathrm{s}/\\mathrm{m})^{0.3}',\n 'α=0.3':r'\\alpha=0.3',")
build=build.replace("if header[0]=='方向/楼层':", "if header[0]=='上端所在层':widths=[2.1,3.0,1.2,2.5,4.1,4.1]\n  elif header[0]=='方向/楼层':")
ast.parse(build);(W/'build_word.py').write_text(build,encoding='utf-8',newline='\n')
author=(old/'word/author_word.py').read_text(encoding='utf-8')
author=author.replace('p06-mechanism-classification-v003.md',dst.name).replace('p06-mechanism-classification-论文审阅稿-v003.docx','p06-actual-damper-session025-论文审阅稿-v002.docx').replace('afa9ccbef57335084d7bb57a8ed443644b7fd53c57623cf59ea02788212708df',newsha)
ast.parse(author);(W/'author_word.py').write_text(author,encoding='utf-8',newline='\n')
(H/'check_final_word.py').write_bytes((old/'check_final_word.py').read_bytes())
tabs=lambda x:re.findall(r'(?:^\|.*\n)+',x,re.M)
assert tabs(s)==tabs(src.read_text(encoding='utf-8'))
assert re.findall(r'\$\$.*?\$\$',s,re.S)==re.findall(r'\$\$.*?\$\$',src.read_text(encoding='utf-8'),re.S)
report={'reviewed_v001_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'final_md':dst.relative_to(R).as_posix(),'final_bytes':dst.stat().st_size,'final_sha256':newsha,'exact_clarifications':[{'from':a,'to':b}for a,b in changes],'all_tables_unchanged_from_review':True,'display_math_unchanged':True,'marker_not_yet_run':True,'native_math_formatting_added':'P_D/r_D and actual parameter units; no scientific value changes'}
(H/'final-text-adoption.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['final_md','final_bytes','final_sha256','all_tables_unchanged_from_review']},ensure_ascii=False))
