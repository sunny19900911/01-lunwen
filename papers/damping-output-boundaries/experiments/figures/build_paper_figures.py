"""Reproducible Matplotlib figures from frozen E001/E003/E004 and V006 evidence.

No solver, response reconstruction, fitting or modification of frozen evidence.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv,hashlib,json,sys,time
import numpy as np

EXTRA=Path.home()/'.codex/tmp/mechanism20261013-pydeps'
if EXTRA.exists():sys.path.append(str(EXTRA))
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

HERE=Path(__file__).resolve().parent
EXP=HERE.parent
TOPIC=EXP.parent
DATA=HERE/'plot-data'
BLUE='#235789';ORANGE='#c75b28';TEAL='#198579';GRAY='#66717d';RED='#b43f46'
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.titlesize':11,
    'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':9,
    'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.7,
    'lines.linewidth':1.5,'grid.color':'#dbe0e5','grid.linewidth':.5,
    'savefig.facecolor':'white','svg.fonttype':'path','mathtext.fontset':'stix'})

INPUTS={}
OUTPUTS=[]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def source(path):
    path=Path(path);INPUTS[str(path.resolve())]={'sha256':sha(path),'bytes':path.stat().st_size}
    return path
def readcsv(path):
    with source(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def readjson(path):return json.loads(source(path).read_text(encoding='utf-8'))
def savecsv(name,rows):
    with (DATA/name).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def finish(fig,name,footer):
    fig.text(.01,.012,footer,fontsize=8,color=GRAY,va='bottom')
    fig.savefig(HERE/(name+'.png'),dpi=300,bbox_inches='tight',pad_inches=.1)
    fig.savefig(HERE/(name+'.svg'),bbox_inches='tight',pad_inches=.1)
    plt.close(fig)
    OUTPUTS.extend([name+'.png',name+'.svg'])

def figure1():
    stories=readcsv(EXP/'round001/story_cut_and_spatial_acceleration.csv')
    nets=readcsv(EXP/'round001/adjacent_cut_net.csv')
    values=[-100*np.array([float(r['cut_reduction']) for r in stories]),
            100*np.array([float(r['increase_ratio']) for r in nets]),
            100*np.array([float(r['spatial_accel_increase_ratio']) for r in stories])]
    labels=['(a) Bottom-cut shear',r'(b) Net difference $N_j=V_j-V_{j+1}$','(c) Spatial acceleration envelope']
    colors=[BLUE,TEAL,ORANGE]
    fig,axes=plt.subplots(1,3,figsize=(10.2,3.8),sharey=True)
    counts=[];plotrows=[]
    for ax,y,label,color in zip(axes,values,labels,colors):
        order=np.argsort(y);yy=y[order];rank=np.arange(1,len(y)+1)
        ax.axhline(0,color=GRAY,ls='--',lw=.8,zorder=1)
        ax.scatter(rank,yy,s=10,color=color,zorder=2,rasterized=False)
        ax.scatter(rank[yy>0],yy[yy>0],s=32,facecolors='white',edgecolors=RED,zorder=3)
        down,equal,up=int(sum(y<0)),int(sum(y==0)),int(sum(y>0))
        ax.set(title=label,xlabel='Group rank (sorted separately)',xlim=(0,174),ylim=(-40,10))
        ax.grid(axis='y');ax.text(.03,.055,f'{down} down / {equal} equal / {up} up',transform=ax.transAxes,fontsize=9)
        if up:
            ax.annotate(f'+{max(y):.2f}%',(168,max(y)),xytext=(105,7.1),
                        arrowprops={'arrowstyle':'-','color':GRAY,'lw':.7},color=RED,fontsize=9)
        counts.append({'output':label,'down':down,'equal':equal,'up':up,'n':len(y)})
        plotrows.extend({'output':label,'sorted_rank':int(i),'change_percent':float(v)} for i,v in zip(rank,yy))
    axes[0].set_ylabel(r'Peak change: $100(P_3/P_0-1)$ (%)')
    fig.suptitle('E001 | Different output definitions give different changes',fontsize=12,y=.98)
    fig.subplots_adjust(left=.075,right=.995,bottom=.21,top=.84,wspace=.15)
    finish(fig,'fig01_native_output_changes','168 groups per output = 7 records x 2 directions x 12 floors; paired exported-window peaks.')
    savecsv('fig01_changes.csv',plotrows)
    return counts

def figure2():
    trace=readcsv(EXP/'round003/T4_response_trace.csv')
    result=readjson(EXP/'round003/truncated_window_result.json')
    table=readcsv(EXP/'round003/window_peak_comparison.csv')
    rows=[r for r in table if float(r['dt_s'])==.0025]
    t=np.array([float(r['t_s']) for r in trace]);y0=np.array([float(r['baseline_y']) for r in trace]);y1=np.array([float(r['new_y']) for r in trace])
    record=next(s for s in result['summaries'] if s['grid']['T_s']==4.)
    fig,axes=plt.subplots(1,2,figsize=(9.7,4.15),gridspec_kw={'width_ratios':[1.25,1]})
    ax=axes[0];ax.axvspan(0,4,color='#e8edf2',label='Frozen input window [0, 4 s]')
    ax.plot(t,y0,color=BLUE,label=r'$\zeta_0=0.05$');ax.plot(t,y1,color=ORANGE,label=r'$\zeta_1=0.08$')
    ax.axvline(4,color=GRAY,ls='--',lw=.8)
    for state,y,color,offset in zip(record['states'],[y0,y1],[BLUE,ORANGE],[(2.3,-.01),(2.3,-.11)]):
        at=state['full_peak_time'];p=state['full_refined_peak']*np.sign(y[np.argmin(abs(t-at))])
        ax.plot(at,p,'o',color=color,ms=4)
        ax.annotate(f'Full peak at {at:.3f} s',(at,p),xytext=(at+offset[0],p+offset[1]),
                    arrowprops={'arrowstyle':'-','color':color,'lw':.7},fontsize=8,color=color)
    ax.set(title='(a) T = 4 s: full peaks occur after shutoff',xlim=(0,12),xlabel='Time (s)',ylabel='Output (synthetic units)')
    ax.legend(loc='upper left',frameon=False,fontsize=8);ax.grid(axis='y')
    ax=axes[1];T=np.array([float(r['T_s']) for r in rows]);short=np.array([float(r['truncated_ratio']) for r in rows]);full=np.array([float(r['full_ratio']) for r in rows])
    ax.semilogy(T,short,'o-',color=RED,ms=4,label='Predefined [0, T] peak ratio')
    ax.semilogy(T,full,'s-',color=BLUE,ms=4,label='Complete response peak ratio')
    ax.axhline(1,color=GRAY,ls=':',lw=.9)
    ax.annotate('113.079',(4,short[T==4][0]),xytext=(4.7,180),fontsize=9,color=RED)
    ax.text(.97,.08,'Full ratio at T=4: 0.933615',ha='right',transform=ax.transAxes,fontsize=9,color=BLUE)
    ax.set(title='(b) The observation window changes the ratio',xlabel='Input duration T (s)',ylabel=r'Peak ratio $P_1/P_0$',xlim=(0,8.5),ylim=(.5,2e7))
    ax.legend(loc='upper left',frameon=False,fontsize=8);ax.grid(axis='y',which='major')
    fig.suptitle('E003 | Frozen-window and complete-tail peaks are different observables',fontsize=12,y=.99)
    fig.subplots_adjust(left=.075,right=.99,bottom=.18,top=.82,wspace=.31)
    finish(fig,'fig02_window_and_complete_peaks','Synthetic fixed output; lines show a display subset. Complete tails were checked to T+600 s with an analytic remainder bound.')
    savecsv('fig02_peak_ratios.csv',[{'T_s':float(r['T_s']),'window_ratio':float(r['truncated_ratio']),'full_ratio':float(r['full_ratio'])} for r in rows])

def figure3():
    result=readjson(EXP/'round004/complete_peak_witness.json')
    trace=readcsv(EXP/'round004/witness_trace_decimated.csv')
    witness=EXP/'round004/finite_input_witness.npz'
    cached=DATA/'fig03_input_plot.csv'
    if witness.exists():
        with np.load(source(witness),allow_pickle=False) as z:t=z['t'];f=z['input']
        whole=np.arange(0,len(t),128);zoom=np.flatnonzero((t>=290)&(t<=310))[::4]
        index=np.unique(np.r_[whole,zoom,np.argmax(abs(f))])
        savecsv(cached.name,[{'t_s':float(t[i]),'input':float(f[i])} for i in index])
    else:
        if not cached.exists():raise FileNotFoundError('Need frozen local witness or cached plot-data/fig03_input_plot.csv')
    plotted=readcsv(cached);t=np.array([float(r['t_s']) for r in plotted]);f=np.array([float(r['input']) for r in plotted])
    tt=np.array([float(r['t_s']) for r in trace]);y0=np.array([float(r['baseline_y']) for r in trace]);y1=np.array([float(r['new_y']) for r in trace])
    row=result['runs'][-1]
    fig,axes=plt.subplots(3,1,figsize=(8.4,6.2),gridspec_kw={'height_ratios':[.75,1,1.4]})
    axes[0].plot(t,f,color=GRAY,lw=.8);axes[0].set(xlim=(0,600),ylim=(-1.15,1.15),ylabel='Input',title='(a) One finite input, common amplitude normalization')
    axes[0].text(.99,.83,r'$\max |f|=1$, support [0, 600 s]',ha='right',transform=axes[0].transAxes,fontsize=9)
    mask=(t>=290)&(t<=310);axes[1].plot(t[mask],f[mask],color=GRAY,lw=1.1)
    axes[1].set(xlim=(290,310),ylabel='Input',title='(b) Input detail around the response peak')
    axes[2].plot(tt,y0,'.-',color=BLUE,ms=2,label=r'$\zeta_0=0.05$');axes[2].plot(tt,y1,'.-',color=ORANGE,ms=2,label=r'$\zeta_1=0.08$')
    axes[2].set(xlim=(290,310),xlabel='Time (s)',ylabel='Output (synthetic units)',title='(c) The same input gives a complete peak ratio above 1.6')
    axes[2].legend(loc='lower left',frameon=False)
    for y,p,at,color in [(y0,row['complete_P0'],row['baseline_peak_time_s'],BLUE),(y1,row['complete_P1'],row['new_peak_time_s'],ORANGE)]:
        signed=p*np.sign(y[np.argmin(abs(tt-at))]);axes[2].plot(at,signed,'o',color=color,ms=4)
    axes[2].text(.98,.08,f'Complete peak ratio = {row["complete_ratio"]:.5f}\nContinuous-peak numerical lower bound > 1.808',
                 transform=axes[2].transAxes,ha='right',fontsize=9,
                 bbox={'facecolor':'white','edgecolor':'#dbe0e5','pad':4})
    for ax in axes:ax.grid(axis='y');ax.tick_params(axis='both',labelsize=8)
    fig.suptitle('E004 | Synthetic two-mode finite-input witness (not engineering shear)',fontsize=12,y=.995)
    fig.subplots_adjust(left=.1,right=.99,bottom=.11,top=.91,hspace=.60)
    finish(fig,'fig03_complete_peak_witness','Lines: saved 0.25 s display samples; peak markers: frozen fine grid. Zero initial state; complete tail checked through 900 s plus a bound.')

def figure4():
    source(TOPIC/'research/roles/verification/round-002.md')
    source(TOPIC/'research/roles/verification/round-006.md')
    source(TOPIC/'research/roles/verification/reply-C006-refinement.md')
    witness=readjson(EXP/'round004/complete_peak_witness.json')['runs'][-1]['complete_ratio']
    k=np.linspace(1,3,401);old=(4*k-3)*(5-4/k)**2;new=(2*k-1)*(3-2/k)**2
    fig,ax=plt.subplots(figsize=(7.7,4.4))
    ax.plot(k,old,color=GRAY,ls='--',label=r'Old coarse peak bound $(4\kappa-3)(5-4/\kappa)^2$')
    ax.plot(k,new,color=BLUE,label=r'New coarse peak bound $(2\kappa-1)(3-2/\kappa)^2$')
    ax.plot(k,k,color=TEAL,ls=':',lw=1.7,label=r'$\kappa$: harmonic / complete $L^2$ bound')
    ax.plot(1.6,witness,'o',color=ORANGE,ms=5,label='E004 synthetic complete peak ratio')
    ax.axvline(1.6,color='#b8bfc7',lw=.7,zorder=0)
    for y,text,xy in [(21.25,'21.25',(1.69,26)),(6.7375,'6.7375',(1.83,11)),(witness,'1.81183 > 1.6',(1.83,2.2))]:
        ax.plot(1.6,y,'o',color=ORANGE if y==witness else BLUE,ms=3)
        ax.annotate(text,(1.6,y),xytext=xy,fontsize=9,arrowprops={'arrowstyle':'-','lw':.7,'color':GRAY})
    ax.set(xlabel=r'Damping ratio multiplier $\kappa=\zeta_1/\zeta_0$',ylabel='Ratio / upper-bound constant',xlim=(1,3),ylim=(.8,120),yscale='log')
    ax.set_title('V002 / V006 | Improved non-sharp complete-response peak bounds',pad=12)
    ax.legend(loc='upper left',frameon=True,facecolor='white',edgecolor='none',framealpha=1,fontsize=8);ax.grid(axis='y',which='major')
    fig.subplots_adjust(left=.1,right=.99,bottom=.19,top=.88)
    finish(fig,'fig04_peak_bound_comparison','Bounds apply to the specified two-mode fixed real output, zero initial state and complete tail. Neither coarse bound is proved sharp.')
    savecsv('fig04_bound_curves.csv',[{'kappa':float(a),'old_coarse_B':float(b),'new_coarse_B':float(c),'harmonic_and_L2_kappa':float(a)} for a,b,c in zip(k,old,new)])

def main():
    start=time.perf_counter();DATA.mkdir(parents=True,exist_ok=True)
    counts=figure1();figure2();figure3();figure4()
    result={'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
            'script_sha256':sha(__file__),'python':sys.version,'numpy':np.__version__,
            'matplotlib':matplotlib.__version__,'matplotlib_local_package_path':str(Path(matplotlib.__file__).resolve()),
            'backend':matplotlib.get_backend(),'font':'Arial; SVG text converted to paths',
            'frozen_sources':INPUTS,'outputs':[{ 'file':name,'sha256':sha(HERE/name),'bytes':(HERE/name).stat().st_size} for name in OUTPUTS],
            'native_group_counts':counts,'local_witness_policy':'NPZ stays local; no Git commands run. Plot input cache is a decimated derivative, not a replacement witness.'}
    (HERE/'figure_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'figures':len(OUTPUTS)//2,'elapsed_seconds':result['elapsed_seconds'],'counts':counts},ensure_ascii=False,indent=2))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
