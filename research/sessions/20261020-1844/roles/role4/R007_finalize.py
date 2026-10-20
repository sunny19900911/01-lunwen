from pathlib import Path
from datetime import datetime,timezone,timedelta
from PIL import Image,ImageStat
import json,hashlib
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((O/'R007-render-map.json').read_text(encoding='utf-8'));fix=json.loads((O/'R007-layout-repair.json').read_text(encoding='utf-8'));rows=[]
notes=['六条实虚线、图例、Story1—12及百分号完整；中文与底部公式正常，无切图。','X/Y双面板、最小—最大阴影和中位线、两侧Story轴及脚注完整。','四类模态/总量图例、正负小数、20.090/20.215虚线标注与无量纲脚注完整，无缺字。','四子图轴/kN、时间/s、QT/QD峰点和竖线完整；已复看修正版，峰值标签不再与竖线/点重叠。']
for i,r in enumerate(m['records']):
 src=Path(r['source_svg']);assert sha(src)==r['source_sha256'];png=Path(fix['png'] if i==3 else r['png'])
 with Image.open(png) as im:
  assert im.width==2200 and im.height>=1000;dpi=im.info.get('dpi');assert dpi and min(dpi)>=180
  gray=im.convert('L');lo,hi=gray.getextrema();assert lo<100 and hi>240
  assert png.stat().st_size>10000
  rows.append({'source_svg':str(src),'source_svg_sha256':sha(src),'approved_png':str(png),'png_sha256':sha(png),'width':im.width,'height':im.height,'dpi':list(dpi),'bytes':png.stat().st_size,'visually_viewed_via_view_image':True,'QA_pass':True,'notes':notes[i],'corrected_svg_copy':fix['corrected_svg'] if i==3 else None})
report='''# R007 四幅插图PNG交付与实际目视QA

四幅最终PNG均为2200像素宽、200ppi，已逐张调用view_image实际查看；中文、英文、负号、百分号、Σ及箭头显示正常，坐标轴/图例/脚注完整，没有边界裁切。Pillow另核尺寸、DPI和非空像素。正式采用路径见R007-QA-and-mapping-manifest.json的approved_png。

QT/QD初次渲染有峰值标签与峰时竖线轻微重叠。已另存R007-Story8-QT-QD-two-cases-qa.svg和PNG，只将4个峰标签上移到图区上方，未改变任何曲线、峰点、竖线几何或标签数值；修正后再次实际查看通过。请采用带-qa后缀PNG，初次PNG仅作为QA过程保留。

四个冻结原SVG的SHA全部保持。只作渲染与排版修正，没有新科学计算。本轮目视验收针对PNG本身；作者将图插入Word后仍须按实际版面逐页渲染，核图宽、文字可读性与分页。
'''
(O/'R007-QA.md').write_text(report,encoding='utf-8')
end=datetime.now(timezone.utc);start=datetime.fromisoformat('2026-10-20T12:11:31+00:00');out=O/'R007-QA-and-mapping-manifest.json';assert not out.exists()
out.write_text(json.dumps({'status':'frozen; four approved PNGs visually inspected','start_observed_utc':start.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-start).total_seconds(),'within_10min':end<=start+timedelta(minutes=10),'original_four_SVGs_unchanged':True,'mapping':rows,'final_Word_page_render_QA_still_required':True,'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R007*')) if p.is_file()]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen':end.isoformat(),'seconds':(end-start).total_seconds(),'approved_PNGs':len(rows),'all_visual_QA_pass':True},ensure_ascii=False))
