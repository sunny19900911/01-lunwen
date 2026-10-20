from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,csv,hashlib,html,xml.etree.ElementTree as ET
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[4];P=R/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution';C=R.parent/'W5-重燃双塔连体/research/maxwell-20261017/experiments/R001/core-cache';G=R/'research/sessions/20261019-2045/roles/data/R001-link-geometry-88.csv'
START=datetime.fromisoformat('2026-10-20T12:02:40+00:00')
def now():return datetime.now(timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rc(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def js(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths=[P/'local_history_manifest_r006.json',P/'local_paired_histories_r006.npz',C/'manifest.json',C/'Story_Forces.npz',G,O/'R005-first-two-layer-summary.csv'];bindings=[{'path':str(p),'sha256':sha(p)} for p in paths]
js('R006-input-freeze.json',{'utc':now().isoformat(),'code_sha256':sha(Path(__file__)),'inputs':bindings,'scope':'replot two frozen Story8 examples only; retain all native points in 5-25s; QD=upper J internal resisting sum nP, no QT-QD'})
hm=json.loads(paths[0].read_text(encoding='utf-8'));cm=json.loads(paths[2].read_text(encoding='utf-8'));sf=cm['tables']['Story Forces'];gg={(r['Story'],r['Link']):r for r in rc(G)};old={r['Case']:r for r in rc(paths[5])};data=[];peaks=[];checks=[]
with np.load(paths[1],allow_pickle=False) as zz,np.load(C/sf['cache'],allow_pickle=False) as sz:
 for case in ['RH4X','RH4Y']:
  sk=next(k for k,g in sf['groups'].items() if g['keys']['Story']=='Story8' and g['keys']['Output Case']==case);a=sz[sk];t=a[:,sf['columns'].index('Time')];qt=a[:,sf['columns'].index('V'+case[-1])];members=sorted([r for r in hm['arrays'] if r['Story']=='Story8' and r['Case']==case],key=lambda r:r['Link']);assert len(members)==8
  parts=[];sr=[]
  for r in members:
   ar=zz[r['key']];cc=r['columns'];assert np.array_equal(t,ar[:,cc.index('t_s')]);assert np.array_equal(ar[:,cc.index('P_I_kN')],ar[:,cc.index('P_J_kN')]);parts.append(float(gg['Story8',r['Link']]['n'+case[-1].lower()])*ar[:,cc.index('P_I_kN')]);sr.append(ar[:,cc.index('force_I_row')])
  qd=np.sum(parts,axis=0);it=int(np.argmax(abs(qt)));id=int(np.argmax(abs(qd)));o=old[case]
  values={'QT_peak_abs_kN':float(abs(qt[it])),'QT_signed_at_peak_kN':float(qt[it]),'t_QT_peak_s':float(t[it]),'QD_J_resisting_peak_abs_kN':float(abs(qd[id])),'QD_J_resisting_signed_at_own_peak_kN':float(qd[id]),'t_QD_abs_peak_s':float(t[id]),'QD_J_resisting_at_QT_peak_kN':float(qd[it]),'QT_signed_at_QD_abs_peak_kN':float(qt[id])}
  for k,v in values.items():assert v==float(o[k]);checks.append({'Case':case,'field':k,'exact_float_match_R005':True})
  mask=(t>=5)&(t<=25);assert int(mask.sum())==1001 and mask[it] and mask[id] and np.allclose(np.diff(t),.02,rtol=0,atol=1e-12)
  for signal,i,y,other in [('QT',it,qt,qd),('QD_J_resisting',id,qd,qt)]:peaks.append({'Case':case,'Story':'Story8','signal':signal,'peak_t_s':float(t[i]),'signed_value_kN':float(y[i]),'absolute_peak_kN':float(abs(y[i])),'other_signal_signed_at_this_time_kN':float(other[i]),'QT_source_row_at_this_time':int(a[i,sf['columns'].index('SourceRow')]),'P_I_SourceRows_at_this_time':';'.join(str(int(s[i])) for s in sr),'scope':'full-record peak, also inside plotted 5-25s; source R005 matched exactly'})
  data.append((case,t[mask],qt[mask],qd[mask],float(t[it]),float(t[id]),qt[it],qd[id]))
with (O/'R006-peak-points-4.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(peaks[0]));w.writeheader();w.writerows(peaks)
def text(x,y,s,size=13,anchor='start',extra=''):return f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" {extra}>{html.escape(str(s))}</text>'
def line(x1,y1,x2,y2,color='#d7dee3',width=1,extra=''):return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}" {extra}/>'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="760" viewBox="0 0 1180 760" role="img"><title>Story8：原生剪力与装置水平合力时序</title><desc>Two cases RH4X and RH4Y; native unsmoothed points 5 to 25 seconds; QT and QD on separate kN axes. QD is upper J internal resisting term, not QT minus QD.</desc><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei,Segoe UI,Arial,sans-serif" fill="#243642">',text(590,35,'现有实体装置模型：Story8剪力与装置水平合力时序',21,'middle'),text(590,63,'局部时窗5—25秒；保留0.02秒原生采样，未平滑；上下纵轴范围不同',14,'middle'),line(370,92,405,92,'#68737d',1.5,'stroke-dasharray="6 4"'),text(415,97,'QT绝对峰时',13),line(660,92,695,92,'#bd7928',1.5,'stroke-dasharray="3 3"'),text(705,97,'QD绝对峰时',13)]
for col,(case,t,qt,qd,tqt,tqd,pqt,pqd) in enumerate(data):
 left=95+col*580;width=430;xx=lambda v:left+(v-5)/20*width
 svg.append(text(left+width/2,130,case,18,'middle'))
 for row,(name,y,lim,ticks,color) in enumerate([('QT',qt,6500,[-6000,-4000,-2000,0,2000,4000,6000],'#216d9d'),('QD',qd,500,[-400,-200,0,200,400],'#16836b')]):
  top=165+row*285;height=210;yy=lambda v:top+height/2-v/(2*lim)*height
  for tick in ticks:svg.extend([line(left,yy(tick),left+width,yy(tick),'#dfe5e9' if tick else '#a2afb8'),text(left-10,yy(tick)+4,tick,11,'end')])
  for tick in [5,10,15,20,25]:svg.extend([line(xx(tick),top,xx(tick),top+height),text(xx(tick),top+height+21,tick,12,'middle')])
  svg.extend([line(left,top,left,top+height,'#5c6b75',1.2),line(left,top+height,left+width,top+height,'#5c6b75',1.2),text(left-58,top+height/2,name+' / kN',13,'middle',f'transform="rotate(-90 {left-58} {top+height/2})"')])
  svg.append('<polyline points="'+' '.join(f'{xx(float(a)):.5f},{yy(float(b)):.5f}' for a,b in zip(t,y))+f'" fill="none" stroke="{color}" stroke-width="1.35" stroke-linejoin="round"/>')
  for tp,cc,dash in [(tqt,'#68737d','6 4'),(tqd,'#bd7928','3 3')]:svg.append(line(xx(tp),top,xx(tp),top+height,cc,1.5,f'stroke-dasharray="{dash}"'))
  tp,peak=(tqt,pqt) if row==0 else (tqd,pqd);svg.append(f'<circle cx="{xx(tp):.5f}" cy="{yy(peak):.5f}" r="4" fill="{color}" stroke="white" stroke-width="1"/>');svg.append(text(left+7,top+16,f'{name}峰：{abs(peak):.2f} kN @ {tp:.2f} s',12))
  if row==1:svg.append(text(left+width/2,top+height+49,'时间 / s',14,'middle'))
svg.extend([text(590,728,'QD = Σ n_axis P：上端J的结构内力抵抗项；装置对J的外力为−QD。图中没有计算主体QT−QD。',12,'middle'),'</g></svg>'])
path=O/'R006-Story8-QT-QD-two-cases.svg';assert not path.exists();path.write_text('\n'.join(svg),encoding='utf-8');root=ET.parse(path).getroot();assert len(root.findall('.//{http://www.w3.org/2000/svg}polyline'))==4
caption='图：现有实体装置模型Story8在RH4X、RH4Y下的原生Bottom剪力QT与8只装置主输入方向水平合力QD。每例上下子图时间轴一致，分别采用kN纵轴；曲线仅显示5—25秒局部范围，保留该范围全部1001个原生时刻，未平滑或移动峰点。灰色虚线为QT全记录绝对峰时，棕色点线为QD全记录绝对峰时，二者均落在显示区间内。QD=ΣnP采用上端J的结构内力抵抗项，装置对J的外力为其反号；没有以QT−QD构造主体剪力。两个峰时不同不等于相位角或减震因果。'
(O/'R006-caption.md').write_text(caption+'\n',encoding='utf-8')
assert all(sha(Path(b['path']))==b['sha256'] for b in bindings)
js('R006-checks.json',{'R005_scalar_matches':checks,'matched_scalars':len(checks),'XML_valid':True,'polyline_count':4,'native_points_per_curve':1001,'peak_point_rows':4,'native_interval_s':.02,'display_window_s':[5,25],'smoothing':False,'full_time_arrays_written':False,'new_model_calculations':0})
end=now();js('R006-delivery-manifest.json',{'status':'frozen','start_utc':START.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_8min':end<=START+timedelta(minutes=8),'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R006*')) if p.is_file()]});print(json.dumps({'frozen':end.isoformat(),'seconds':(end-START).total_seconds(),'matched_scalars':len(checks),'SVG_bytes':path.stat().st_size},ensure_ascii=False))
