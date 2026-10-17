"""Two fixed scalar examples only: exact affine-log identities plus ordinary log display."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime, timezone
import hashlib, json, math, sys

H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fp(p):return {'path':str(p),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def save(name,data):
    assert not (H/name).exists()
    (H/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def form(c=0,u=0,d=0):return (Q(c),Q(u),Q(d))
def add(*xs):return tuple(sum((x[j] for x in xs),Q(0)) for j in range(3))
def scale(a,x):return tuple(Q(a)*v for v in x)
def neg(x):return scale(-1,x)
def val(x,u,d):return float(x[0])+float(x[1])*u+float(x[2])*d
def encoded(x):return dict(zip(['constant','log_up','log_down'],map(str,x)))

def main():
    frozen=json.loads((H/'input-freeze.json').read_text(encoding='utf-8'))
    for f in frozen['sources']:assert fp(f['path'])==f
    assert frozen['parameters']=={'kappa':1,'c':1,'V':1,'alpha':1,'F0':0,'h':'1/2','T':4,'D':'1/4','M':['1/2','3/5'],'terminal_total_delta':'free'}
    h,T,D=Q(1,2),Q(4),Q(1,4); up,down=form(u=1),form(d=1)
    results=[]
    for M in [Q(1,2),Q(3,5)]:
        up_arg=1/(1-M);down_arg=(1+M)/(1+h)
        down=form() if down_arg==1 else form(d=1)  # exact log(1)=0 in the M=h degenerate segment
        tau=add(up,down)
        L=add(tau,form(-2*M+h-h*h/2));ell=scale(1/(M*M),add(form(D),neg(L)))
        wait=add(form(T),neg(tau),neg(ell));delta=add(up,scale(M,ell),neg(down))
        Phi_up=add(up,form(-M-M*M/2));Phi_down=add(down,form(-M+M*M/2+h-h*h/2))
        D_total=add(Phi_up,Phi_down,scale(M*M,ell))
        W_up=add(up,form(-M));W_down=add(down,form(h-M));W_total=add(W_up,W_down,scale(M*M,ell))
        dashpot_integral=add(up,neg(down),form(-h),scale(M,ell))
        assert add(Phi_up,Phi_down)==L
        assert add(wait,up,ell,down)==form(T)
        assert D_total==form(D) and W_total==form(Q(3,8))
        assert add(form(h),dashpot_integral)==delta
        assert 1-1/up_arg==M and (1+M)/down_arg-1==h
        assert h<=M<1 and abs(M)<=1
        if M==h:
            assert down_arg==1 and tau==up
            # 2/3 < log(2) < 3/4 gives L>1/24 and D-L>1/8.
            exact_bounds={'tau_lower':'2/3','tau_upper':'3/4','L_lower':'1/24','D_minus_L_lower':'1/8','ell_lower':'1/2','wait_lower':'5/2','down_duration':'0'}
            assert Q(2,3)-Q(5,8)==Q(1,24)
            assert Q(7,8)-Q(3,4)==Q(1,8)
        else:
            # 10/11 < log(8/3) < 1 gives L>37/440 and D-L>3/40.
            exact_bounds={'tau_lower':'10/11','tau_upper':'1','L_lower':'37/440','D_minus_L_lower':'3/40','ell_lower':'5/24','wait_lower':'73/72','down_duration':'log(16/15)>0'}
            assert up_arg*down_arg==Q(8,3) and up_arg/down_arg==Q(75,32)
            assert Q(10,11)-Q(33,40)==Q(37,440)
            assert Q(43,40)-1==Q(3,40) and Q(25,9)*Q(3,40)==Q(5,24)
        u,d=math.log(float(up_arg)),math.log(float(down_arg))
        display={'up':u,'dwell':val(ell,u,d),'down':d,'wait':val(wait,u,d),'tau':val(tau,u,d),'L':val(L,u,d),'delta_T_relative_to_delta0_zero':val(delta,u,d)}
        assert all(display[k]>=0 for k in ['up','dwell','down','wait','L'])
        results.append({'M':str(M),'up_log_argument':str(up_arg),'down_log_argument':str(down_arg),'exact_affine_log_basis':['1','log(up_argument)','log(down_argument)'],
                        'tau':encoded(tau),'L':encoded(L),'ell':encoded(ell),'wait':encoded(wait),'delta_T':encoded(delta),
                        'D_exact':str(D),'W_exact':'3/8','E_terminal_spring_exact':'1/8','time_sum_exact':'4','F0_exact':'0','FT_exact':'1/2',
                        'peak_exact':str(M),'control_wait_up_dwell_down':['0','1',str(M),'-1'],
                        'nonnegative_duration_bounds_from_report':exact_bounds,'ordinary_float_log_display_not_certificate':display})
    assert results[0]['M']=='1/2' and results[1]['M']=='3/5'
    save('checks.json',{'status':'candidate_readable_example_waiting_independent_static_review','method':'exact Fraction affine-log coefficient identities; two scalar math.log displays only','exact_checks_passed':True,'cases':results,'no_ODE_arrays_timehistory_parameter_scan':True,'float_displays_are_not_continuous_certification':True})
    lines=[r'# R025：相同真实耗散，可以对应两个不同峰力','',
           r'这是已准入C038的无量纲说明例，状态candidate，待角色2小范围静态独核。预先固定 κ=c=V=α=1、F(0)=0、F(4)=h=1/2、真实黏滞耗散D=1/4；仅比较提前指定的峰M=1/2和3/5，不求整个峰区间。末总变形自由，以δ(0)=0选取位移原点。','',
           r'本构为 F′=v−F，δ′=v，|v|≤1 a.e.，F和δ绝对连续。允许开关速度跳变。按“零力等待w、v=1最快升力、v=M驻留ℓ、v=−1最快降力”排列。若以各段起点为s=0，力依次是0、1−e^(−s)、M、(1+M)e^(−s)−1；不是数值积分。M=h时降力段长度为0。','',
           r'已审α=1闭式直接给 τ↑=−log(1−M)、τ降=log[(1+M)/(1+h)]、τh=τ↑+τ降，L=τh−2M+h−h²/2。取ℓ=(D−L)/M²、w=4−τh−ℓ，则总时长恰4、峰恰M、末力恰h，且D=L+M²ℓ恰为1/4。','',
           '| 项 | M=1/2 | M=3/5 |','|---|---|---|',
           '| 升力时长 | log2 | log(5/2) |',
           '| 驻留时长ℓ | 7/2−4log2 | 215/72−(25/9)log(8/3) |',
           '| 降力至h时长 | 0 | log(16/15) |',
           '| 零力等待w | 1/2+3log2 | 73/72+(16/9)log(8/3) |',
           '| τh | log2 | log(8/3) |',
           '| 过渡耗散L | log2−5/8 | log(8/3)−33/40 |',
           '| 末总δ | 7/4−log2 | 43/24+log(75/32)−(5/3)log(8/3) |','',
           '逐项非负的精确理由：对x>1，有log x>2(x−1)/(x+1)，由导数或正项级数可证；对log2用1/x在[1,2]的严格凸梯形上界得log2<3/4。所以2/3<log2<3/4，第一例L>1/24、D−L>1/8、ℓ>1/2、w>5/2，下降时长恰0。第二例10/11<log(8/3)<1；上界由e>1+1+1/2+1/6=8/3得出。因此L>37/440、D−L>3/40、ℓ>5/24、w>73/72；升降log参数都大于1，各段为正。等待非负亦证明ℓ≤4−τh，且τh<4。','',
           r'两者速度只取0、1、M、−1，均满足同一个V=1；升力单调至M、驻留在M、降力单调至h，故连续力的真实绝对峰就是指定M，不是采样峰。用分段闭式和原R017的积分恒等式，真实耗散精确为1/4，端部净功 W=D+h²/(2κ)=1/4+1/8=3/8。W与D不能混用；其中1/8是非零末力保留的串联弹簧储能。','',
           '下面仅是普通标量log显示，精确形式和上述证明才是依据；没有把浮点显示当连续误差认证。','',
           '| 峰M | 等待 | 升 | 驻留 | 降 | 末总δ |','|---:|---:|---:|---:|---:|---:|']
    for r in results:
        x=r['ordinary_float_log_display_not_certificate'];lines.append(f"| {r['M']} | {x['wait']:.12g} | {x['up']:.12g} | {x['dwell']:.12g} | {x['down']:.12g} | {x['delta_T_relative_to_delta0_zero']:.12g} |")
    lines+=['',r'末δ由∫v=τ↑+Mℓ−τ降得到，亦满足δ(4)=h+∫Fdt，均非零。它们确实不同：固定D的上述表达δ(M)=τ↑−τ降+(D−L)/M有δ′(M)=−(D−L)/M²；在[1/2,3/5]上L严格增且L(3/5)<D，故δ严格降。此处只是解释两个已固定实例，没有扫描参数。若要求末δ相同或回零，就加了本例没有满足/证明的条件，不能沿用这两个构造。','',
            '因此在完全相同的κ/c/α/V/T、初末力和真实耗散下，峰力可以为1/2或3/5；端部功也相同。这只帮助理解“同耗散不唯一确定同峰力”，不说明真实结构可产生这些速度，不给楼层反应、真实477/500000装置、FNA实现或安全保证。它是旧已审闭式与取满构造的经典特例，不称新研究或首创。','',
            '精确系数检查见checks.py/checks.json；普通log小数不替代解析证明。根协议、旧verification非零末力R017及C038/R029/R040来源见input-freeze/sourcefreeze；未访问数组、原表、底层缓存或运行ODE/拟合/图，未改旧件、作者当前输入、共享文件或Git。冻结后停止待独审。']
    assert not (H/'report.md').exists();(H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    for f in frozen['sources']:assert fp(f['path'])==f
    deadline=datetime.fromisoformat(frozen['deadline']);now=datetime.now(timezone.utc);assert now<=deadline
    save('validation.json',{'started_at':frozen['started_at'],'finished_utc':now.isoformat(),'status':'candidate_waiting_independent_static_review','two_preselected_cases_only':True,'both_feasible':True,'exact_duration_D_W_endpoint_and_delta_identities':True,'nonnegative_durations_proved_analytically':True,'terminal_delta_free_and_values_explicit':True,'initial_delta_zero_is_coordinate_origin':True,'bounds_measurable_velocity_AC_force_delta':True,'sources_unchanged':True,'no_ODE_numpy_arrays_Excel_fitting_or_figures':True,'python':sys.version,'code_sha256':sha(__file__)})
    save('sourcefreeze.json',{'frozen_utc':now.isoformat(),'sources':frozen['sources'],'outputs':[fp(x) for x in sorted(H.iterdir()) if x.is_file() and x.name!='sourcefreeze.json']})
    print(json.dumps({'status':'candidate','both_feasible':True,'D_exact':'1/4','W_exact':'3/8','scalar_displays':[r['ordinary_float_log_display_not_certificate'] for r in results],'report':fp(H/'report.md'),'checks':fp(H/'checks.json'),'sourcefreeze':fp(H/'sourcefreeze.json')},ensure_ascii=True))

if __name__=='__main__':main()
