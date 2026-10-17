"""ReportLab LinePlot floor profiles from two frozen, reviewed source files.
Usage requires a new --out directory. No package install, source mutation or raw arrays.
"""
import argparse,csv,datetime,hashlib,json,math,platform,sys,time
from pathlib import Path
import reportlab
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing,String,Rect,Line
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics import renderSVG
from reportlab.lib import colors

def identity(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();started=time.perf_counter()
 if args.out.exists():raise SystemExit('Refusing existing --out directory')
 repo=args.repo.resolve();out=args.out.resolve()
 src=repo/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R005-floor-results/floor_three_metric_table_r005.csv'
 review=repo/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004/楼层输出与控制位置独审-R009.md'
 expected=['fc4ea0e6291be246e2c3c167176d09d2c06728cb51c34ccfd8a04c3ebee6cb2c','eb8b86079c8fc0ff05d466c2889db08f3456f29313540ec14ac7c50ac441af1e']
 sources=[identity(p) for p in [src,review]]
 assert [s['sha256'] for s in sources]==expected,'Source SHA mismatch'
 cases=['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']
 raw=list(csv.DictReader(src.open(encoding='utf-8-sig',newline='')));assert len(raw)==72
 indexed={}
 for row in raw:
  case=row['Case'];story=int(row['Story'].removeprefix('Story'));key=(case,story);assert key not in indexed and case in cases and 1<=story<=12
  assert row['shear_and_CM_complete']=='True'
  shear=float(row['Bottom_shear_abs_record_peak_kN']);cm=float(row['CM_abs_record_peak_mm']);assert math.isfinite(shear) and math.isfinite(cm) and shear>0 and cm>0
  indexed[key]=(shear,cm)
 assert set(indexed)=={(c,s) for c in cases for s in range(1,13)}
 norms={};plotrows=[];top3={}
 for case in cases:
  denom=[max(indexed[(case,s)][j] for s in range(1,13)) for j in [0,1]]
  assert all(x>0 for x in denom)
  for story in range(1,13):
   values=indexed[(case,story)];normalized=[values[j]/denom[j] for j in [0,1]];assert all(0<=x<=1 for x in normalized)
   norms[(case,story)]=normalized;plotrows.append({'Case':case,'Story':story,'Bottom_shear_abs_record_peak_kN':values[0],'CM_abs_record_peak_mm':values[1],'case_shear_max_12stories_kN':denom[0],'case_CM_max_12stories_mm':denom[1],'Bottom_shear_normalized':normalized[0],'CM_normalized':normalized[1]})
  for j,metric in enumerate(['Bottom_shear','CM']):
   assert max(norms[(case,s)][j] for s in range(1,13))==1.0
   top3[case+'_'+metric]=sorted(range(1,13),key=lambda s:(-indexed[(case,s)][j],s))[:3]
   assert top3[case+'_'+metric]==([1,2,3] if j==0 else [12,11,10])
 out.mkdir(parents=True,exist_ok=False)
 with (out/'plot_floor_profiles_72rows.csv').open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(plotrows[0]),lineterminator='\n');writer.writeheader();writer.writerows(plotrows)
 # Every data curve is drawn by the standard ReportLab LinePlot chart.
 W,H=900,560;drawing=Drawing(W,H);drawing.add(Rect(0,0,W,H,fillColor=colors.white,strokeColor=None))
 dark=colors.HexColor('#172C40');muted=colors.HexColor('#4C5C6A');grid=colors.HexColor('#E4E9EE')
 drawing.add(String(450,533,'Floor profiles of absolute record peaks',fontName='Helvetica-Bold',fontSize=19,fillColor=dark,textAnchor='middle'))
 drawing.add(String(450,512,'Single controlled model | Each case and metric normalized separately',fontName='Helvetica',fontSize=11.5,fillColor=muted,textAnchor='middle'))
 palette=['#0072B2','#56B4E9','#D55E00','#E69F00','#009E73','#CC79A7'];styles=[]
 for i,case in enumerate(cases):
  color=colors.HexColor(palette[i]);dash=[] if case.endswith('X') else [5,3];styles.append({'case':case,'color':palette[i],'dash':dash})
  lx=112+i*126;drawing.add(Line(lx,486,lx+27,486,strokeColor=color,strokeWidth=2,strokeDashArray=dash));drawing.add(String(lx+34,482,case,fontName='Helvetica',fontSize=10.5,fillColor=dark))
 panel_specs=[(80,0,'(a) Bottom shear'),(510,1,'(b) CM displacement')]
 for left,j,title in panel_specs:
  plot=LinePlot();plot.x=left;plot.y=96;plot.width=310;plot.height=348;plot.data=[[(norms[(case,s)][j],s) for s in range(1,13)] for case in cases]
  plot.xValueAxis.valueMin=0;plot.xValueAxis.valueMax=1;plot.xValueAxis.valueSteps=[0,.2,.4,.6,.8,1];plot.xValueAxis.labelTextFormat='%.1f';plot.xValueAxis.forceZero=False
  plot.yValueAxis.valueMin=1;plot.yValueAxis.valueMax=12;plot.yValueAxis.valueSteps=list(range(1,13));plot.yValueAxis.labelTextFormat='%d';plot.yValueAxis.forceZero=False
  for axis in [plot.xValueAxis,plot.yValueAxis]:
   axis.labels.fontName='Helvetica';axis.labels.fontSize=10.5;axis.labels.fillColor=muted;axis.strokeColor=colors.HexColor('#8997A4');axis.strokeWidth=.7;axis.tickStrokeColor=colors.HexColor('#8997A4');axis.visibleGrid=True;axis.gridStrokeColor=grid;axis.gridStrokeWidth=.5
  for i,case in enumerate(cases):
   plot.lines[i].strokeColor=colors.HexColor(palette[i]);plot.lines[i].strokeWidth=1.65;plot.lines[i].strokeDashArray=styles[i]['dash']
   marker=makeMarker('Circle' if case.endswith('X') else 'Square');marker.size=3.3;marker.strokeColor=colors.HexColor(palette[i]);marker.fillColor=colors.white;marker.strokeWidth=.8;plot.lines[i].symbol=marker
  drawing.add(plot);drawing.add(String(left,459,title,fontName='Helvetica-Bold',fontSize=13,fillColor=dark));drawing.add(String(left-37,449,'Story',fontName='Helvetica',fontSize=10.5,fillColor=muted));drawing.add(String(left+155,62,'Peak / maximum across 12 stories',fontName='Helvetica',fontSize=10.7,fillColor=dark,textAnchor='middle'))
 drawing.add(String(450,31,'Each floor may peak at a different time; these are not simultaneous profiles.',fontName='Helvetica',fontSize=10,fillColor=muted,textAnchor='middle'))
 drawing.add(String(450,14,'Bottom section shear and CM displacement only; no response-reduction inference.',fontName='Helvetica',fontSize=10,fillColor=muted,textAnchor='middle'))
 svg=out/'floor_record_peak_profiles.svg';renderSVG.drawToFile(drawing,str(svg))
 checks={'72_unique_case_story_rows':True,'six_cases_12_stories_each':True,'complete_Bottom_and_CM_only':True,'all_raw_values_positive_finite':True,'per_case_per_metric_denominators':True,'all_normalized_values_in_0_1':True,'all_12_series_maxima_exactly_1':True,'raw_kN_mm_values_retained':True,'Top3_matches_reviewed_positions':True,'all_data_curves_use_ReportLab_LinePlot':True,'no_Drift_curve':True,'sources_unchanged':sources==[identity(p) for p in [src,review]]}
 assert all(checks.values())
 qa={'checks':checks,'source_identity':sources,'plot_rows':72,'series':12,'points_per_series':12,'normalization':'For each case and each metric separately divide its 12 floor absolute record peaks by their own maximum. Units never divided against one another.','top3':top3,'styles_consistent_across_panels':styles,'not_simultaneous':True,'no_model_comparison_or_reduction_rate':True}
 (out/'numeric_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 record={'finished_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'elapsed_seconds':time.perf_counter()-started,'python':sys.version,'reportlab':reportlab.Version,'plot_engine':'reportlab.graphics.charts.lineplots.LinePlot','svg_engine':'reportlab.graphics.renderSVG','script':identity(Path(__file__)),'arguments':sys.argv[1:],'source_identity':sources,'outputs':[identity(out/n) for n in ['plot_floor_profiles_72rows.csv','floor_record_peak_profiles.svg','numeric_QA.json']],'exit_code':0,'PNG_render_and_visual_QA':'separate after SVG generation'}
 (out/'run_record_plot.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(record,ensure_ascii=False))
if __name__=='__main__':main()
