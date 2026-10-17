"""One two-panel figure from frozen E007 OOF values; no fitting or new thresholds."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,sys,time
import numpy as np

EXTRA=Path.home()/'.codex/tmp/mechanism20261013-pydeps'
if EXTRA.exists():sys.path.append(str(EXTRA))
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'round007_grouped_diagnostic'
BLUE='#235789';RED='#b43f46';GRAY='#66717d'
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.titlesize':11,'axes.labelsize':10,
 'xtick.labelsize':9,'ytick.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,
 'axes.linewidth':.7,'grid.color':'#dbe0e5','grid.linewidth':.5,'svg.fonttype':'path'})

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def readcsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def main():
    started=time.perf_counter()
    sources=[SRC/'oof_predictions.csv',SRC/'summary_metrics.csv',SRC/'frozen_protocol.json']
    before={str(p):sha(p) for p in sources}
    oof=readcsv(sources[0]);metrics=readcsv(sources[1])
    labels=[('net_difference_change_pct','(a) Simultaneous adjacent-cut net difference'),
            ('spatial_acceleration_change_pct','(b) Spatial acceleration envelope')]
    fig,axes=plt.subplots(1,2,figsize=(10.4,5.9),sharex=True,sharey=True)
    highlighted=[];data=[]
    positions={'net_difference_change_pct':{'SHW6X':(-1.,-4.)},
               'spatial_acceleration_change_pct':{'SHW3Y':(-15.,-2.),'SHW6X':(-2.,-6.),'SHW7X':(-6.,-20.)}}
    for ax,(target,title) in zip(axes,labels):
        rows=[r for r in oof if r['target']==target and r['model']=='ols_intercept_cut_floor']
        assert len(rows)==168
        actual=np.array([float(r['actual_change_pct']) for r in rows]);pred=np.array([float(r['predicted_change_pct']) for r in rows])
        ax.fill_between([0,12],[-40,-40],[0,0],facecolor='#faecec',zorder=0)
        ax.plot([-40,12],[-40,12],ls='--',color=GRAY,lw=1,zorder=1)
        ax.axhline(0,color=GRAY,lw=.8);ax.axvline(0,color=GRAY,lw=.8)
        ax.scatter(actual,pred,s=18,color=BLUE,alpha=.65,edgecolors='none',zorder=2)
        for r,x,y in zip(rows,actual,pred):
            data.append({'target':target,'record':r['record_event'],'direction':r['direction'],'floor':int(r['floor']),
                         'actual_change_pct':x,'ols_oof_prediction_pct':y})
            if x>0:
                label=f'{r["record_event"]}-{r["direction"]}-F{r["floor"]}'
                ax.scatter([x],[y],marker='^',s=58,color=RED,edgecolors='white',linewidths=.6,zorder=4)
                ax.annotate(label,(x,y),xytext=positions[target][r['case']],fontsize=8.5,color=RED,
                            bbox={'facecolor':'white','edgecolor':'none','pad':1},
                            arrowprops={'arrowstyle':'-','color':RED,'lw':.8,'connectionstyle':'arc3,rad=-.05'},zorder=5)
                highlighted.append({'target':target,'label':label,'actual_change_pct':float(x),'prediction_pct':float(y)})
        ols=next(r for r in metrics if r['target']==target and r['model']=='ols_intercept_cut_floor')
        mean=next(r for r in metrics if r['target']==target and r['model']=='training_target_mean')
        text=('OOF MAE / RMSE (pp)\n'
              f'OLS: {float(ols["MAE_pp"]):.2f} / {float(ols["RMSE_pp"]):.2f}\n'
              f'Train mean: {float(mean["MAE_pp"]):.2f} / {float(mean["RMSE_pp"]):.2f}')
        ax.text(.035,.965,text,transform=ax.transAxes,va='top',fontsize=9,
                bbox={'facecolor':'white','edgecolor':'#dbe0e5','pad':4},zorder=6)
        ax.text(.035,.04,f'TP={ols["TP"]}, FP={ols["FP"]}, FN={ols["FN"]}; 168 groups',
                transform=ax.transAxes,fontsize=9,color=RED)
        ax.set(title=title,xlabel='Observed peak change (%)',xlim=(-40,12),ylim=(-40,12))
        ax.set_aspect('equal',adjustable='box');ax.xaxis.set_major_locator(MultipleLocator(10));ax.yaxis.set_major_locator(MultipleLocator(10));ax.grid()
    axes[0].set_ylabel('OLS out-of-fold prediction (%)')
    fig.suptitle('E007 | Lower average error still misses every observed increase',fontsize=13,y=.97)
    handles=[Line2D([0],[0],marker='o',linestyle='none',markerfacecolor=BLUE,markeredgecolor='none',markersize=5,label='OLS OOF groups'),
             Line2D([0],[0],marker='^',linestyle='none',markerfacecolor=RED,markeredgecolor='white',markersize=7,label='Observed increases (all false negatives)'),
             Line2D([0],[0],color=GRAY,ls='--',lw=1,label='y = x')]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.52,.925),ncol=3,frameon=False,fontsize=9)
    fig.text(.025,.07,'7 record-ID groups (geological independence unverified); held-out Bottom-change features are already known.',fontsize=8.5,color=GRAY)
    fig.text(.025,.035,'Same record is held out in both directions and all 12 floors. Increase threshold is fixed at zero.',fontsize=8.5,color=GRAY)
    fig.subplots_adjust(left=.075,right=.99,bottom=.22,top=.84,wspace=.12)
    base='fig07_ols_oof_local_changes'
    fig.savefig(HERE/(base+'.png'),dpi=300,bbox_inches='tight',pad_inches=.12)
    fig.savefig(HERE/(base+'.svg'),bbox_inches='tight',pad_inches=.12)
    plt.close(fig)
    with (HERE/'plot_values.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    assert len(highlighted)==4
    assert all(sha(p)==before[str(p)] for p in sources)
    outputs=[HERE/(base+'.png'),HERE/(base+'.svg')]
    manifest={'evidence':'E-EXP-007 frozen results only','finished_utc':datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds':time.perf_counter()-started,'script_sha256':sha(__file__),
              'sources':[{'file':str(p),'sha256':before[str(p)],'bytes':p.stat().st_size} for p in sources],
              'outputs':[{'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size} for p in outputs],
              'highlighted_false_negatives':highlighted,'numpy':np.__version__,'matplotlib':matplotlib.__version__,
              'backend':matplotlib.get_backend(),'font':'Arial, SVG text as paths','no_refit':True,'source_hashes_unchanged':True,
              'notes':'Plot uses original OOF and summary CSV numbers; no threshold changes or majority-class accuracy. SVG generator bytes retained including any trailing whitespace.'}
    (HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'figure':base,'elapsed_seconds':manifest['elapsed_seconds'],'highlighted':highlighted},ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
