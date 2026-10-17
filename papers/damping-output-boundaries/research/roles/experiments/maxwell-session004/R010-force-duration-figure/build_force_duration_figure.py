"""All-point scientific LinePlot figure from four frozen Link histories."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time
import numpy as np
import reportlab
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing,String,Rect,Line
from reportlab.graphics import renderSVG
from reportlab.lib import colors
H=Path(__file__).resolve().parent
PROTOCOL_SHA='bf11760e48f122a3ca40314eadaf56611747a7cdb2d3a5632650676b2192324b'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def main():
    start=time.perf_counter();assert not (H/'force_duration_examples.svg').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs']
    assert all(sha(r['path'])==r['sha256'] for r in refs.values())
    audit=json.loads(Path(refs['R008_audit']['path']).read_text(encoding='utf-8'))
    reviewed={(r['Case'],r['Link']):r for ex in audit['examples'] for r in [ex['first'],ex['second']]}
    manifest=json.loads(Path(refs['manifest']['path']).read_text(encoding='utf-8'))
    meta={x['key']:x for x in manifest['arrays']};power=1+1/p['alpha'];series={};summary=[]
    with np.load(refs['NPZ']['path'],allow_pickle=False) as arrays:
        for ex in p['four_records']:
            for link in ex['Links']:
                key=link+'__'+ex['Case'];z=arrays[key];t=z[:,0].tolist();F=z[:,1].tolist();J=z[:,2].tolist()
                assert meta[key]['Story']==ex['Story'] and len(t)==ex['n_points_each']
                assert t[0]==ex['window'][0] and t[-1]==ex['window'][1] and F==J
                assert all(math.isfinite(x) for x in t+F) and all(abs(t[i+1]-t[i]-.02)<1e-10 for i in range(len(t)-1))
                peak=max(abs(x) for x in F);weights=[(abs(x)/peak)**power for x in F];cumulative=[0.];running=0.;correction=0.
                increments=[]
                for i in range(len(t)-1):
                    v=(t[i+1]-t[i])*(weights[i]+weights[i+1])/2;increments.append(v)
                    adjusted=v-correction;new=running+adjusted;correction=(new-running)-adjusted;running=new;cumulative.append(running)
                tau=math.fsum(increments);assert math.isclose(cumulative[-1],tau,abs_tol=1e-12)
                ref=reviewed[(ex['Case'],link)];assert peak==ref['peak'] and math.isclose(tau,ref['tau'],abs_tol=1e-12)
                assert min(cumulative)==0 and all(cumulative[i+1]>=cumulative[i] for i in range(len(t)-1))
                assert max(abs(x) for x in F)<160 and cumulative[-1]<5
                series[key]={'force':list(zip(t,F)),'integral':list(zip(t,cumulative))}
                summary.append({'Case':ex['Case'],'Story':ex['Story'],'Link':link,'n_original_points':len(t),'t0_s':t[0],'T_s':t[-1],
                    'Pmax_native_kN':peak,'tau_direct_integral_s':tau,'I_T_plotted_s':cumulative[-1],'zero_force_points_retained':sum(x==0 for x in F),
                    'R008_tau_difference_s':tau-ref['tau'],'local_array_key':key})
    W,HH=1100,720;drawing=Drawing(W,HH);drawing.add(Rect(0,0,W,HH,fillColor=colors.white,strokeColor=None))
    dark=colors.HexColor('#172C40');muted=colors.HexColor('#4C5C6A');grid=colors.HexColor('#E4E9EE');palette=p['style']['device_colors_in_each_column']
    drawing.add(String(550,693,'Peak force and cumulative force-power duration',fontName='Helvetica-Bold',fontSize=21,fillColor=dark,textAnchor='middle'))
    drawing.add(String(550,671,'Four native full-window histories | Fixed alpha = 0.30 | All original samples plotted',fontName='Helvetica',fontSize=11.5,fillColor=muted,textAnchor='middle'))
    plotted=[]
    for column,ex in enumerate(p['four_records']):
        left=[85,635][column];width=410;case=ex['Case'];links=ex['Links'];end=ex['window'][1]
        drawing.add(String(left,640,f"{case} / {ex['Story']}",fontName='Helvetica-Bold',fontSize=15,fillColor=dark))
        for i,link in enumerate(links):
            row=next(r for r in summary if r['Case']==case and r['Link']==link);ly=616-20*i;col=colors.HexColor(palette[i]);dash=[] if i==0 else [4,2.5]
            drawing.add(Line(left,ly,left+28,ly,strokeColor=col,strokeWidth=1.7,strokeDashArray=dash))
            drawing.add(String(left+37,ly-4,f"{link}   Pmax = {row['Pmax_native_kN']:.3f} kN; tau = {row['tau_direct_integral_s']:.3f} s",fontName='Helvetica',fontSize=11.5,fillColor=dark))
        for metric,bottom,ymin,ymax,ysteps,title in [('force',381,-160,160,[-150,-100,-50,0,50,100,150],'Native signed axial force P (kN)'),
            ('integral',110,0,5,[0,1,2,3,4,5],'Cumulative integral I(t) (s)')]:
            plot=LinePlot();plot.x=left;plot.y=bottom;plot.width=width;plot.height=185
            plot.data=[series[link+'__'+case][metric] for link in links];plot.joinedLines=1
            plot.xValueAxis.valueMin=0;plot.xValueAxis.valueMax=end;plot.xValueAxis.valueSteps=[0,10,20,30,40,50]+([end] if end!=50 else [])
            plot.xValueAxis.labelTextFormat=lambda v:f'{v:g}';plot.xValueAxis.forceZero=False
            plot.yValueAxis.valueMin=ymin;plot.yValueAxis.valueMax=ymax;plot.yValueAxis.valueSteps=ysteps;plot.yValueAxis.labelTextFormat='%g';plot.yValueAxis.forceZero=False
            for axis in [plot.xValueAxis,plot.yValueAxis]:
                axis.labels.fontName='Helvetica';axis.labels.fontSize=10.5;axis.labels.fillColor=muted;axis.strokeColor=colors.HexColor('#8997A4');axis.strokeWidth=.65
                axis.tickStrokeColor=colors.HexColor('#8997A4');axis.visibleGrid=True;axis.gridStrokeColor=grid;axis.gridStrokeWidth=.45
            for i,link in enumerate(links):
                plot.lines[i].strokeColor=colors.HexColor(palette[i]);plot.lines[i].strokeWidth=1.0;plot.lines[i].strokeDashArray=[] if i==0 else [4,2.5];plot.lines[i].symbol=None
                assert len(plot.data[i])==ex['n_points_each'];plotted.append({'Case':case,'Link':link,'metric':metric,'n_points':len(plot.data[i])})
            drawing.add(plot);drawing.add(String(left,bottom+198,title,fontName='Helvetica-Bold',fontSize=11.5,fillColor=dark))
            drawing.add(String(left+width/2,bottom-35,'Original time t (s)',fontName='Helvetica',fontSize=10.7,fillColor=dark,textAnchor='middle'))
    drawing.add(String(550,42,'I_i(t) = integral (abs(P_i) / Pmax_i)^p ds;  p = 4.333333;  I_i(T) = tau_i in seconds.',fontName='Helvetica',fontSize=11,fillColor=dark,textAnchor='middle'))
    drawing.add(String(550,23,'Single-model conditional Lp explanation; classical quantity; no response-reduction or causal claim.',fontName='Helvetica',fontSize=10.5,fillColor=muted,textAnchor='middle'))
    renderSVG.drawToFile(drawing,str(H/'force_duration_examples.svg'))
    with (H/'four_record_endvalues.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    checks={'four_prespecified_full_windows':len(summary)==4,'all10394_original_record_points_retained':sum(r['n_original_points'] for r in summary)==10394,
        'eight_all_point_LinePlot_series':len(plotted)==8 and sum(r['n_points'] for r in plotted)==20788,
        'I_endpoint_matches_direct_tau_and_review':True,'signed_native_force_and_monotone_I_no_clipping':True,
        'no_normalization_by_tau':True,'all_source_SHA_and_protocol_unchanged':all(sha(r['path'])==r['sha256'] for r in refs.values()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below480seconds':time.perf_counter()-start<480};assert all(checks.values())
    qa={'checks':checks,'series_point_counts':plotted,'four_endvalues':summary,'p':power,'force_y_limits':[-160,160],'integral_y_limits':[0,5],
        'curve_engine':'ReportLab LinePlot / renderSVG','source_refs':refs,'no_duplicate_full_array_output':True}
    (H/'numeric_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    caption='图：两组同模型装置的原带符号轴向力与归一化力幂累计积分。左列RH4X/Story8：K10、K92；右列SHW7Y/Story11：K6、K5。上排为原生P-I(kN)，J端仅核重复；下排I_i(t)=∫0^t(|P_i|/Pmax_i)^p ds，alpha=0.30、p=1+1/alpha，末值为tau_i(s)，没有再除以tau。完整0–50s/0–53.9s原窗口、0.02s网格和全部10394原记录点保留，每条分别在两排绘制；不裁峰、平滑、峰时对齐或补尾。同器件上下同色同线型，图例给Pmax与tau。该tau是经典Lp归一化幂积分，不是阈值以上实际持续时长或新指标。本图只作单模型条件幅值—持续量解释，不代替真实属性/端口认证，不是减幅、布置效益、工程因果或高阶模态识别。未用W/Dport冒充直接Dforce；未绘能量量。全部源SHA和R008复核末值见numeric_QA；PNG实际目视记录另附，canonical采纳由主控决定。\n'
    (H/'图注与使用范围.md').write_text(caption,encoding='utf-8')
    record={'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,'command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],
        'exit_code':0,'python':sys.version,'reportlab':reportlab.Version,'numpy':np.__version__,'code_sha256':sha(__file__),'protocol_sha256':PROTOCOL_SHA,
        'outputs':{n:sha(H/n) for n in ['force_duration_examples.svg','four_record_endvalues.csv','numeric_QA.json','图注与使用范围.md']},'checks':checks}
    (H/'run_record_plot.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'elapsed_seconds':record['elapsed_seconds'],'four_record_endvalues':summary,'checks':checks},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
