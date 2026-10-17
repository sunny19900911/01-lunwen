"""Independent scalar Lp-duration audit; NumPy only decodes frozen NPZ."""
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
import csv,hashlib,itertools,json,math,sys,time
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='ade73742a5a12eaaa29096e09b4ab574b578913c43273e08083b0435ce52fe22'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def read(f):
    with Path(f).open(encoding='utf-8-sig',newline='') as x:return list(csv.DictReader(x))
def write(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def trap(t,v):return math.fsum((t[i+1]-t[i])*(v[i]+v[i+1])/2 for i in range(len(t)-1))
def duration(t,f,p,b):
    peak=max(abs(x) for x in f)
    energy=b*trap(t,[abs(x)**p for x in f])
    if peak==0:return peak,None,energy,'undefined_zero_peak'
    tau=trap(t,[(abs(x)/peak)**p for x in f])
    return peak,tau,energy,'defined'
def inversions(peak1,peak2,e1,e2):return peak1>peak2 and e1<e2
def logterms(x,y,p):
    vals=[x[k] for k in ['peak','tau','Dport','Dforce']]+[y[k] for k in ['peak','tau','Dport','Dforce']]
    if any(v is None or v<=0 for v in vals):return None
    A=p*math.log(x['peak']/y['peak']);T=math.log(x['tau']/y['tau'])
    Q=math.log((x['Dport']/x['Dforce'])/(y['Dport']/y['Dforce']))
    L=math.log(x['Dport']/y['Dport']);return A,T,Q,L,L-A-T-Q
def main():
    start=time.perf_counter();assert not (H/'audit_summary_r008.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs'];paths={k:Path(v['path']) for k,v in refs.items()}
    assert all(sha(paths[k])==v['sha256'] for k,v in refs.items())
    alpha=p['alpha'];b=p['b'];a=p['a'];power=1+1/alpha
    trained=json.loads(paths['R002_fit'].read_text(encoding='utf-8'))['best_grid_row']
    assert (alpha,a,b)==(trained['alpha'],trained['a_m_per_kN'],trained['b_m_per_s_kN_power_inverse_alpha'])
    meta=json.loads(paths['array_manifest'].read_text(encoding='utf-8'))['arrays']
    old={r['local_array_key']:r for r in read(paths['R006_summary_CSV'])}
    source={r['Link']+'__'+r['Case']:r for r in read(paths['W5_devices'])}
    rows=[];by={};differences=defaultdict(float)
    def close(label,x,y,log=False):
        err=abs(x-y);differences[label]=max(differences[label],err)
        assert err<=1e-11 if log else math.isclose(x,y,abs_tol=1e-12,rel_tol=1e-10),(label,x,y)
    with np.load(paths['NPZ'],allow_pickle=False) as z:
        assert len(z.files)==len(meta)==len(old)==len(source)==192
        for info in meta:
            key=info['key'];data=z[key].tolist();t=[x[0] for x in data];f=[x[1] for x in data];d=[x[4] for x in data]
            assert all(math.isfinite(v) for line in data for v in line) and all(t[i+1]>t[i] for i in range(len(t)-1))
            assert all(x[1]==x[2] and x[3]/1000==x[4] for x in data)
            peak,tau,df,status=duration(t,f,power,b);assert status=='defined' and 0<tau<=t[-1]-t[0]+1e-10
            W=math.fsum((f[i]+f[i+1])/2*(d[i+1]-d[i]) for i in range(len(t)-1))
            Us=a/2*(f[-1]**2-f[0]**2);dp=W-Us;assert dp>0 and df>0
            reconstructed=b*peak**power*tau;close('own_Dforce_identity',reconstructed,df)
            controls=[{'t_s':t[i],'signed_P_kN':f[i],'P_I_cell':'I'+str(int(data[i][5])),'P_J_cell':'I'+str(int(data[i][6]))} for i in range(len(f)) if abs(f[i])==peak]
            src=source[key];assert peak==float(src['peak_kN']) and controls==json.loads(src['force_peak_controllers_json'])
            assert controls==json.loads(old[key]['force_peak_controllers_json'])
            for label,x,y in [('tau',tau,float(src['tau_p_grid_s'])),('Dforce',df,float(src['Dforce_model_kNm'])),
                ('Dport',dp,float(src['Dport_conditional_kNm'])),('q',dp/df,float(src['Dport_over_Dforce'])),('W_native',W,float(old[key]['Wtrap_native_kNm']))]:close('source_'+label,x,y)
            r={'Link':info['Link'],'Case':info['Case'],'Story':info['Story'],'peak':peak,'tau':tau,'T':t[-1]-t[0],
                'tau_over_T':tau/(t[-1]-t[0]),'W_native':W,'DeltaUs_conditional':Us,'Dport':dp,'Dforce':df,'Dforce_peak_duration':reconstructed,
                'q_conditional':dp/df,'peak_controllers_json':json.dumps(controls,separators=(',',':'))}
            rows.append(r);by[key]=r
    groups=defaultdict(list)
    for r in rows:groups[(r['Case'],r['Story'])].append(r)
    assert len(groups)==24 and all(len(g)==8 for g in groups.values())
    pairs=[]
    for (case,story),group in groups.items():
        for x,y in itertools.combinations(sorted(group,key=lambda r:int(r['Link'][1:])),2):
            if x['peak']<y['peak']:x,y=y,x
            A,T,Q,L,res=logterms(x,y,power);assert abs(res)<1e-11
            pairs.append({'Case':case,'Story':story,'higher_or_tied_peak_Link':x['Link'],'lower_or_tied_peak_Link':y['Link'],
                'peak_tie':x['peak']==y['peak'],'Dport_tie':x['Dport']==y['Dport'],'Dforce_tie':x['Dforce']==y['Dforce'],
                'port_inverse':inversions(x['peak'],y['peak'],x['Dport'],y['Dport']),
                'force_inverse':inversions(x['peak'],y['peak'],x['Dforce'],y['Dforce']),
                'log_amplitude':A,'log_duration':T,'log_q_conditional':Q,'log_Dport_ratio':L,'log_identity_residual':res})
    keypair=lambda r:(r['Case'],r['Story'],r['higher_or_tied_peak_Link'],r['lower_or_tied_peak_Link'])
    sourcepairs={keypair(r):r for r in read(paths['W5_pairs'])};assert len(pairs)==len(sourcepairs)==672
    for r in pairs:
        src=sourcepairs[keypair(r)]
        for own,oldname in [('peak_tie','peak_tie'),('port_inverse','conditional_port_rank_inversion'),('force_inverse','model_force_rank_inversion')]:assert r[own]==(src[oldname]=='True')
        for own,oldname in [('log_amplitude','log_peak_amplitude_term'),('log_duration','log_duration_term'),('log_q_conditional','log_conditional_reconstruction_term'),('log_Dport_ratio','log_Dport_ratio')]:close('pair_'+own,r[own],float(src[oldname]),True)
    portset={keypair(r) for r in pairs if r['port_inverse']};forceset={keypair(r) for r in pairs if r['force_inverse']}
    assert portset==forceset=={keypair(r) for r in read(paths['W5_inversions'])} and len(portset)==38
    inversegroups={(x[0],x[1]) for x in portset};assert len(inversegroups)==17
    synthetics={}
    P,tau,D,status=duration([0.,1.,2.],[0.,0.,0.],power,b)
    synthetics['all_zero_peak']=P==0 and tau is None and D==0 and status=='undefined_zero_peak'
    P,tau,D,status=duration([0.,1.,2.],[2.,2.,2.],power,b);synthetics['constant_force_tau_equals_T']=tau==2
    synthetics['peak_tie_not_strict_inverse']=not inversions(2.,2.,1.,2.)
    tied={'peak':2.,'tau':1.,'Dport':3.,'Dforce':4.}
    synthetics['all_quantities_tied_zero_logs']=all(x==0 for x in logterms(tied,tied,power)) and not inversions(2,2,3,3)
    synthetics['energy_tie_not_inverse']=not inversions(2.,1.,3.,3.)
    synthetics['nonpositive_Dport_log_undefined']=all(logterms(dict(tied,Dport=value),tied,power) is None for value in [0.,-1.])
    assert all(synthetics.values())
    examples=[]
    for case,story,li,lj in p['examples']:
        x,y=by[li+'__'+case],by[lj+'__'+case];assert x['Story']==y['Story']==story
        examples.append({'Case':case,'Story':story,'first':x,'second':y,'log_terms':logterms(x,y,power)})
    leak=[]
    for (case,story),g in groups.items():
        ordered=sorted(g,key=lambda r:-r['Dport']);cutoff=ordered[1]['Dport'];selected=[r for r in g if r['Dport']>=cutoff]
        maximum=max(r['peak'] for r in g);leak.append(1-max(r['peak'] for r in selected)/maximum)
    checks={'192_direct_force_duration_recomputed':len(rows)==192,'24_groups_672_all_pairs':len(groups)==24 and len(pairs)==672,
        '38_same_inverse_pairs_in_17_groups':len(portset)==38 and portset==forceset and len(inversegroups)==17,
        'all_source_pair_values_flags_and_peak_locators_match':True,'six_degenerate_semantics_cases_pass':all(synthetics.values()),
        'log_three_terms_and_force_identity_pass':True,'all_input_SHA_unchanged':all(sha(paths[k])==v['sha256'] for k,v in refs.items()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'runtime_below_360_seconds':time.perf_counter()-start<360}
    assert all(checks.values())
    write('independent_devices_192_r008.csv',rows);write('independent_pairs_672_r008.csv',pairs)
    out={'evidence_id':p['evidence_id'],'review_outcome':'0 required corrections within stated domain','finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
        'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'source_report_sha256':refs['W5_report']['sha256'],'records':192,'groups':24,'pairs':672,
        'port_inversions':38,'force_inversions':38,'inverse_groups':17,'same_inverse_pair_sets':True,'actual_peak_ties':sum(r['peak_tie'] for r in pairs),
        'actual_Dport_ties':sum(r['Dport_tie'] for r in pairs),'actual_Dforce_ties':sum(r['Dforce_tie'] for r in pairs),
        'tau_range_s':[min(r['tau'] for r in rows),max(r['tau'] for r in rows)],'max_abs_log_identity_residual':max(abs(r['log_identity_residual']) for r in pairs),
        'max_abs_force_identity_residual_kNm':differences['own_Dforce_identity'],'source_max_abs_numeric_differences':dict(differences),
        'synthetic_algorithm_semantics':synthetics,'examples':examples,'max_same_group_top2_Dport_peak_omission_fraction':max(leak),
        'checks':checks,'source_refs':refs}
    lines=['# M-EXP-R008：峰力—条件能量持续量分解独立审计','',
        '结论：在冻结192条正峰值、正模型能量及正条件端口量的适用域内，0项必须修改问题。192记录、24组全部672对、38对反序及17个反序组均独立复核；能量两种定义产生相同38对。正文采纳及共享准入由主控决定。', '',
        '先读取W5报告、脚本定义及validation来源SHA，再冻结审核协议。未导入或执行W5脚本，未读原始Excel或拟合。NumPy只解码NPZ到普通列表；本审核用标量有符号/绝对幂与math.fsum直接累计梯形积分，独立重算原生W、端点条件储能和Dport。', '',
        '```', 'P=max|F|, p=1+1/alpha, alpha=.30', 'tau=Σ Δt avg((|F|/P)^p)  [P>0]', 'Dforce=b Σ Δt avg(|F|^p)=b P^p tau',
        'Dport=Wtrap−a(Fend²−F0²)/2, q=Dport/Dforce', 'log(Dport_i/Dport_j)=p log(P_i/P_j)+log(tau_i/tau_j)+log(q_i/q_j)', '```', '',
        'tau由力采样直接积分；Dforce另用未归一化力幂积分计算，未用Dforce反解tau。tau单位秒，是归一化幂权重积分，不能解释为阈值以上持续秒数。P峰值及全部符号/时刻/I-J源格与原摘要精确一致。672对逐一核对W5标志与log各项，而非只核计数。', '',
        f"独立tau范围{out['tau_range_s'][0]:.12g}–{out['tau_range_s'][1]:.12g}s；Dforce幅值—持续量恒等式最大绝对残差{out['max_abs_force_identity_residual_kNm']:.6g}kN·m，log三项分解最大绝对残差{out['max_abs_log_identity_residual']:.6g}。均为浮点算术检查，不是连续采样误差界或独立物理验证。", '',
        f"实际672对中峰值并列{out['actual_peak_ties']}对，Dport并列{out['actual_Dport_ties']}对，Dforce并列{out['actual_Dforce_ties']}对。严格反序要求峰值较大且能量较小，任一精确并列不计反序；没有自适应容差。", '',
        '## 两例及来源定位', '', '| 工况/层 | 装置 | P/kN | tau/s | 原生W/kN·m | 条件Dport/kN·m | 峰力时刻/s、I端源格 |', '|---|---|---:|---:|---:|---:|---|']
    for ex in examples:
        for r in [ex['first'],ex['second']]:
            cs=json.loads(r['peak_controllers_json']);loc='; '.join(f"{c['t_s']:.8g}, {c['P_I_cell']}" for c in cs)
            lines.append(f"| {ex['Case']}/{ex['Story']} | {r['Link']} | {r['peak']:.9g} | {r['tau']:.9g} | {r['W_native']:.9g} | {r['Dport']:.9g} | {loc} |")
    for ex in examples:
        A,T,Q,L,res=ex['log_terms'];lines+=['',f"{ex['Case']}/{ex['Story']} {ex['first']['Link']}/{ex['second']['Link']}：log幅值项{A:+.10g}、持续量项{T:+.10g}、条件差额项{Q:+.10g}，总log比{L:+.10g}。峰力较高者的力幂积分已较低，反序无需依靠条件端口差额项制造；不据此归因为高阶模态或特定传力路径。"]
    lines+=['', '## 零峰、并列和退化语义', '',
        '实际192条全为P>0、Dforce>0、Dport>0，W5脚本用断言限定该域。另以6项合成算法边界用例检查：全零力P=0时tau不可定义、Dforce=0；常力tau=T；峰值并列而能量不等不算严格反序；全部并列时log项为0；峰值不等但能量并列不反序；Dport非正时log分解不可定义。全部通过。合成用例不加入192条工程记录，也不声称W5脚本已支持零峰域。', '',
        f"源文‘最大漏峰约0.036%’另按同组Dport前2含并列复算为{100*max(leak):.9g}%，仅核其描述数值，不设置工程意义阈值。", '',
        '原生W、固定拟合储能扣除的Dport、力本构模型量Dforce始终分列。q项含既有离散乘积/回归残差功影响，不是独立实测损失。本项是经典Lp幅值—持续量恒等解释，无新指标/新理论、工程因果、高阶模态识别、方向投影、全88能量或物理真实性认证。', '',
        f"实际运行{out['elapsed_seconds']:.6f}s，exit0，8项检查通过。来源SHA前后不变。只新增本R008目录，192行/672对小诊断及元数据；无重复全时程、原始提取、拟合或Git操作。W5源报告SHA为 `{refs['W5_report']['sha256']}`，脚本只读，最终正文使用由主控决定。"]
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out['outputs']={f:sha(H/f) for f in ['independent_devices_192_r008.csv','independent_pairs_672_r008.csv','report.md']}
    (H/'audit_summary_r008.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'run_record_r008.json').write_text(json.dumps({'command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,'python':sys.version,'numpy_decoder':np.__version__,
        'elapsed_seconds':out['elapsed_seconds'],'code_sha256':sha(__file__),'summary_sha256':sha(H/'audit_summary_r008.json'),'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','review_outcome','records','pairs','port_inversions','inverse_groups','actual_peak_ties','max_abs_log_identity_residual','max_abs_force_identity_residual_kNm','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
