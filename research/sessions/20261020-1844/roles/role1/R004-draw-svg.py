"""Standard-library SVG from frozen local QS2 contribution CSV only."""
from pathlib import Path
import csv,html,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
with (P/'R004-local-curves.csv').open(encoding='utf-8') as f:rows=[{k:float(v) for k,v in r.items()} for r in csv.DictReader(f)]
x0,x1=19.7,20.5;y0,y1=-.075,.010;left,right=100,1040
for r in rows:
 assert x0-1e-12<=r['time_nondimensional']<=x1+1e-12
 assert all(y0<v<y1 for k,v in r.items() if k!='time_nondimensional')
def X(t):return left+(t-x0)/(x1-x0)*(right-left)
def Y(v,top):return top+200*(y1-v)/(y1-y0)
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="760" viewBox="0 0 1120 760">','<rect width="1120" height="760" fill="white"/>','<style>text{font-family:Segoe UI,Microsoft YaHei,sans-serif;font-size:14px;fill:#1f2937}.small{font-size:12px}</style>']
def text(x,y,t,extra=''):s.append(f'<text x="{x}" y="{y}" {extra}>{html.escape(t)}</text>')
text(560,28,'H2 / QS2: signed modal terms on the same saved time axis','text-anchor="middle" font-weight="bold"')
colors=['#2563eb','#16a34a','#ea580c','#111827'];labels=['Mode 1','Mode 2','Mode 3','Total QS2']
for j,(c,l) in enumerate(zip(colors,labels)):
 x=120+230*j;s.append(f'<path d="M{x},52h30" stroke="{c}" stroke-width="2.4"/>');text(x+40,57,l)
for name,label,top in [('none','No added device (C = .02 K)',115),('story1','Device at story 1 (same bare basis)',455)]:
 text(left,top-31,label,'font-weight="bold"')
 for v in [-.075,-.05,-.025,0]:
  y=Y(v,top);s.append(f'<path d="M{left},{y:.3f}H{right}" stroke="#e5e7eb"/>');text(left-12,y+5,f'{v:.3f}','text-anchor="end"')
 for t in [19.7,19.9,20.1,20.3,20.5]:
  x=X(t);s.append(f'<path d="M{x:.3f},{top}V{top+200}" stroke="#f0f1f4"/>');text(x,top+222,f'{t:.1f}','text-anchor="middle"')
 for t in [20.09,20.215]:
  x=X(t);s.append(f'<path d="M{x:.3f},{top}V{top+200}" stroke="#6b7280" stroke-dasharray="4 4"/>');text(x,top-9,f'{t:.3f}','text-anchor="middle" class="small"')
 s.append(f'<rect x="{left}" y="{top}" width="{right-left}" height="200" fill="none" stroke="#9ca3af"/>')
 for k,c in zip(['mode1','mode2','mode3','total'],colors):
  pts=' '.join(f"{X(r['time_nondimensional']):.2f},{Y(r[name+'_'+k],top):.2f}" for r in rows)
  s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{2.5 if k=="total" else 1.8}"/>')
 peak=20.215 if name=='none' else 20.09;r=min(rows,key=lambda r:abs(r['time_nondimensional']-peak));s.append(f'<circle cx="{X(peak):.2f}" cy="{Y(r[name+"_total"],top):.2f}" r="3.2" fill="#111827"/>')
text(560,716,'Time and QS2 are nondimensional; local window only','text-anchor="middle"')
text(560,739,'Dashed lines: common anchors 20.090 and 20.215. No new ODE; same-state projection.','text-anchor="middle" class="small"')
s.append('</svg>');p=P/'R004-local-modal-terms.svg';assert not p.exists();p.write_text('\n'.join(s)+'\n',encoding='utf-8',newline='\n');ET.parse(p)
print(str(p))
