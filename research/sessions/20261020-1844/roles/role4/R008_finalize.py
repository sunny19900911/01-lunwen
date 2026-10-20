from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image
import json,hashlib,re,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((O/'R008-render-map.json').read_text(encoding='utf-8'));rows=[]
for r in m['records']:
 src=Path(r['source_svg']);svg=Path(r['revised_svg']);png=Path(r['approved_png_pending_visual_QA']);assert sha(src)==r['source_sha256']
 old=src.read_text(encoding='utf-8');new=svg.read_text(encoding='utf-8');geom=lambda s:re.findall(r'<(?:polyline|circle|line|path|polygon)\b[^>]*>',s)
 assert geom(old)==geom(new) and r['numeric_tick_text_and_positions_identical'];ET.parse(svg)
 if 'Story8-QT' in svg.name:assert geom(new)==geom((O/'R006-Story8-QT-QD-two-cases.svg').read_text(encoding='utf-8'))
 with Image.open(png) as im:
  assert im.width==2200 and min(im.info['dpi'])>=180 and im.convert('L').getextrema()[0]<100
  rows.append({'source_svg':str(src),'source_sha256':sha(src),'new_svg':str(svg),'new_svg_sha256':sha(svg),'approved_png':str(png),'png_sha256':sha(png),'width':im.width,'height':im.height,'density_ppi':200,'all_geometry_strings_and_numeric_ticks_unchanged':True,'actual_view_image_QA_pass':True,'XML_valid':True})
(O/'R008-QA.md').write_text('''# R008 图中文字与最终PNG映射

三幅主图及14工况包络图均已另存R008 SVG/PNG，未覆盖原冻结图。四幅PNG均2200像素宽、200ppi，已逐张实际view_image查看，中文、图例、坐标轴、公式和边界完整，无缺字、遮挡或裁切。

六工况及包络图改为基准模型/增加3个百分点模态阻尼模型称谓，楼层中文化；横轴和P_M/P_B公式改为工程论文表达。局部图改用第2层弹性剪力V2、第1/2/3阶与三阶合计，并说明无量纲与20.090/20.215虚线，删除ODE及投影过程记录。真实时序图保留必要QD方向定义与不同纵轴尺度，删除重复防御句。

全部polyline/circle/line/path/polygon原始坐标字符串逐项相同，纯数值刻度及其位置相同；时序图与原R006的上述几何亦相同。原SVG SHA全部保持。没有读取新数据或进行科学重算。

请作者下一版采用映射清单的4个approved_png；不要求延长其当前任务。插入Word后，仍按实际页面另行逐页渲染核字号、图宽与分页。
''',encoding='utf-8')
end=datetime.now(timezone.utc);start=datetime.fromisoformat('2026-10-20T12:21:48+00:00');p=O/'R008-QA-and-mapping-manifest.json';assert not p.exists()
p.write_text(json.dumps({'status':'frozen','start_utc':start.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-start).total_seconds(),'within_10min':end<=start+timedelta(minutes=10),'mapping':rows,'original_sources_unchanged':True,'new_scientific_calculations':0,'files':[{'path':str(z),'bytes':z.stat().st_size,'sha256':sha(z)} for z in sorted(O.glob('R008*')) if z.is_file()]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen_utc':end.isoformat(),'elapsed_seconds':(end-start).total_seconds(),'approved_PNGs':4,'visual_QA_pass':True},ensure_ascii=False))
