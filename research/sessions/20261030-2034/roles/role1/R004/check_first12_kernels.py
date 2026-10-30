"""Independent N12 cache check against role4's N36-derived scalar table; no ODE/fit."""
from pathlib import Path
import csv, json, hashlib, datetime
import numpy as np

O=Path(__file__).resolve().parent
S=O.parents[2]
P=S/'root-R001-low-order'
R=S/'roles/role4/R006'
START='2026-10-30T21:41:26+08:00'
def ident(p):
    b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def put(name,obj):
    with (O/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
sources=[P/'local-cache/primary-reference-traces.npz',P/'models-small.json',R/'modal-unit-kernel-change-108.csv',R/'README-unit-modal-kernels.md',R/'verification.json',P/'input-rules-freeze.json']
frozen=[ident(p) for p in sources]
put('input-freeze.json',dict(started_at=START,sources=frozen,primary='N12_elastic_rc1e-10',comparison='role4 R006 N36-derived scalar CSV, modes1-12 only',scope='no import of role4 code; no ODE, fitting, new N, complete trace output, or Git',peak_tolerance='abs(abs(g)-A) <= 1e-14 + 1e-12*A; reference time match <= 1e-9 s'))
model=json.loads(sources[1].read_text(encoding='utf-8'))['N12_elastic_rc1e-10']
coef=np.asarray(model['raw_output_coef'],float)
assert coef.shape==(12,2) and np.isfinite(coef).all() and np.all(coef!=0)
with sources[2].open(encoding='utf-8-sig',newline='') as f:
    refs={(r['Case'],int(r['Mode'])):r for r in csv.DictReader(f) if int(r['Mode'])<=12}
assert len(refs)==36
rows=[];twostory=0.;directdiff=0.
with np.load(sources[0],allow_pickle=False) as z:
    for case in ['SHW3X','SHW4X','RH4X']:
        t=z[f'{case}__Story5__z0.05__t']
        load=lambda story,ze:z[f'{case}__{story}__z{ze:g}__terms']
        for story in ['Story5','Story12']:
            for ze in [.05,.08]:
                assert np.array_equal(t,z[f'{case}__{story}__z{ze:g}__t'])
        terms=[[load(story,ze) for ze in [.05,.08]] for story in ['Story5','Story12']]
        assert all(a.shape==(len(t),12) for pair in terms for a in pair)
        for j in range(12):
            c=int(np.argmax(abs(coef[j])))
            gs=[terms[c][k][:,j]/coef[j,c] for k in range(2)]
            other=[terms[1-c][k][:,j]/coef[j,1-c] for k in range(2)]
            cross=max(float(np.max(abs(gs[k]-other[k]))) for k in range(2))
            twostory=max(twostory,cross)
            A=np.array([np.max(abs(g)) for g in gs]);assert np.all(A>0)
            ratio=float(A[1]/A[0])
            h0,h1=gs[0]/A[0],gs[1]/A[1]
            eps=float(np.linalg.norm(h1-h0)/np.linalg.norm(h0))
            v0,v1=terms[c][0][:,j],terms[c][1][:,j]
            a0,a1=np.max(abs(v0)),np.max(abs(v1))
            direct_ratio=float(a1/a0)
            direct_eps=float(np.linalg.norm(v1/a1-v0/a0)/np.linalg.norm(v0/a0))
            directdiff=max(directdiff,abs(direct_ratio-ratio),abs(direct_eps-eps))
            ref=refs[case,j+1]
            rr=float(ref['A8_over_A5']);er=float(ref['normalized_waveform_relative_L2'])
            row=dict(Case=case,Mode=j+1,recovery_story=['Story5','Story12'][c],N12_A5_unit_kernel=float(A[0]),N12_A8_unit_kernel=float(A[1]),N12_A8_over_A5=ratio,R006_A8_over_A5=rr,ratio_abs_error=abs(ratio-rr),N12_normalized_waveform_relative_L2=eps,R006_normalized_waveform_relative_L2=er,waveform_metric_abs_error=abs(eps-er),two_story_kernel_max_abs_error=cross,samples=len(t))
            assert len(t)==int(ref['samples'])
            for k,ze in enumerate([5,8]):
                imax=int(np.argmax(abs(gs[k])))
                tied=np.flatnonzero(A[k]-abs(gs[k])<=1e-14+1e-12*A[k])
                tr=float(ref[f'peak{ze}_time_s'])
                exact=float(t[imax])
                ok=bool(np.any(abs(t[tied]-tr)<=1e-9))
                row.update({f'peak{ze}_N12_exact_argmax_time_s':exact,f'peak{ze}_R006_time_s':tr,f'peak{ze}_strict_time_abs_error_s':abs(exact-tr),f'peak{ze}_tie_count':len(tied),f'peak{ze}_tie_first_time_s':float(t[tied[0]]),f'peak{ze}_tie_last_time_s':float(t[tied[-1]]),f'peak{ze}_reference_in_tolerance_tie_set':ok,f'A{ze}_abs_error_vs_R006':abs(float(A[k])-float(ref[f'A{ze}_g_m_s2']))})
            row['all_comparisons_pass']=bool(row['ratio_abs_error']<1e-12 and row['waveform_metric_abs_error']<1e-12 and row['peak5_reference_in_tolerance_tie_set'] and row['peak8_reference_in_tolerance_tie_set'] and row['A5_abs_error_vs_R006']<1e-12 and row['A8_abs_error_vs_R006']<1e-12)
            rows.append(row)
assert len(rows)==36 and all(r['all_comparisons_pass'] for r in rows)
with (O/'independent-kernel-check-36.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
summary=dict(rows=36,all_pass=True,max_ratio_abs_error=max(r['ratio_abs_error'] for r in rows),max_normalized_waveform_metric_abs_error=max(r['waveform_metric_abs_error'] for r in rows),max_A_abs_error=max(r[f'A{k}_abs_error_vs_R006'] for r in rows for k in [5,8]),max_strict_peak_time_error_s=max(r[f'peak{k}_strict_time_abs_error_s'] for r in rows for k in [5,8]),peak_anchor_count=72,multiple_tie_anchor_count=sum(r[f'peak{k}_tie_count']>1 for r in rows for k in [5,8]),max_two_story_kernel_abs_error=twostory,max_direct_terms_vs_recovered_kernel_metric_error=directdiff,ratio_min=min(r['N12_A8_over_A5'] for r in rows),ratio_max=max(r['N12_A8_over_A5'] for r in rows),epsilon_min=min(r['N12_normalized_waveform_relative_L2'] for r in rows),epsilon_max=max(r['N12_normalized_waveform_relative_L2'] for r in rows),counterincrease_count=sum(r['N12_A8_over_A5']>1 for r in rows),by_wave={case:dict(ratio_min=min(r['N12_A8_over_A5'] for r in rows if r['Case']==case),ratio_max=max(r['N12_A8_over_A5'] for r in rows if r['Case']==case)) for case in ['SHW3X','SHW4X','RH4X']})
put('results.json',summary)
def lookup(case,j):return next(r for r in rows if r['Case']==case and r['Mode']==j)
lines=['# R004｜N12旧缓存独立核验前12阶单位核变化','',f"**前12阶×3波共36行全部与④R006的N36来源小表吻合：幅比最大误差{summary['max_ratio_abs_error']:.3g}，归一波形差最大误差{summary['max_normalized_waveform_metric_abs_error']:.3g}；72个峰时锚点均通过。**",'', '方法：只读取根目录原有 N12 elastic 分项与固定 raw coefficient，按系数绝对值较大的楼层恢复单位核，并以另一层交叉检查；另直接在原分项计算指标，确认非零常数抵消。不导入④脚本、不重新求解 ODE、不拟合，不输出完整时程。', '',r'定义 $A_\zeta=\max_t|g_\zeta(t)|$、$\rho=A_8/A_5$、$\varepsilon=\|g_8/A_8-g_5/A_5\|_2/\|g_5/A_5\|_2$。在相同原始网格直接计算，不移动或对齐峰值，$\varepsilon$ 表示归一波形变化，不能称为纯相位差。','', '|波形|阶次|ρ=A8/A5|峰幅减小|ε|5%峰时/s|8%峰时/s|','|---|---:|---:|---:|---:|---:|---:|']
for case,j in [('SHW3X',3),('SHW3X',9),('SHW4X',1),('SHW4X',9),('RH4X',3),('RH4X',9)]:
    r=lookup(case,j);rho=r['N12_A8_over_A5']
    lines.append(f"|{case}|{j}|{rho:.6f}|{100*(1-rho):.4f}%|{r['N12_normalized_waveform_relative_L2']:.6f}|{r['peak5_N12_exact_argmax_time_s']:.2f}|{r['peak8_N12_exact_argmax_time_s']:.2f}|")
lines+=['',f"36行的ρ为{summary['ratio_min']:.6f}—{summary['ratio_max']:.6f}，此次均小于1；ε为{summary['epsilon_min']:.6f}—{summary['epsilon_max']:.6f}。同一SHW3X输入下，第3阶与第9阶的峰幅减小分别为{100*(1-lookup('SHW3X',3)['N12_A8_over_A5']):.4f}%和{100*(1-lookup('SHW3X',9)['N12_A8_over_A5']):.4f}%，可直接支撑“相同阻尼增量在不同阶产生不同响应变化”；这不是任意地震输入下的单调性定理。",'',f"**峰时并列检查：** 每条时程先保留精确 `argmax`，再以单位核幅值容差 `1e-14+1e-12*A` 建立并列集合，以时间容差1e-9 s检查④的峰时是否在集合中。多候选锚点{summary['multiple_tie_anchor_count']}个；严格峰时最大差{summary['max_strict_peak_time_error_s']:.3g} s。表中同时保留精确峰时、容差集合首末时刻和候选数，不把舍入或并列差异解释为机制变化。",'',f"两楼层恢复核最大绝对差{twostory:.3g}；直接分项与恢复核的ρ/ε最大差{directdiff:.3g}。逐行结果见 `independent-kernel-check-36.csv`。",'', '**可供⑤正文使用：** “在固定频率、共同输入及零初始条件下，将各阶阻尼比统一由5%提高至8%，各阶单位参与核的峰幅比与归一波形变化并不相同，说明相同阻尼增量具有模态和输入相关的响应效应。”', '', '**解释边界：** 对共同非零常数c，ρ与ε均不随c改变，故固定输出系数和非零Γ在这些比值中抵消；Γ=0时实际模态不受激，实际幅比为0/0，不使用本表认定其有实际贡献。本表描述Γ=1单位核，不是原生楼层贡献，不能据此识别主导楼层剪力的真实模态，也不赋予病态拟合系数物理意义。N12/N36一致性在此验证的是核及指标，而非截断输出的准确性。']
with (O/'one-page.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
assert [ident(p) for p in sources]==frozen
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
elapsed=(now-datetime.datetime.fromisoformat(START)).total_seconds()
put('validation.json',dict(completed_at=now.isoformat(),elapsed_seconds=elapsed,budget_seconds=360,within_budget=elapsed<=360,source_hashes_unchanged=True,all_36_rows_pass=True,independent_N12_vs_N36=True,imports_role4_script=False,new_ODE_or_fit=False,arrays_written=False,git_used=False,code=ident(Path(__file__))))
put('manifest.json',dict(task='session019-role1-R004',files=[ident(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='manifest.json']))
print(json.dumps(summary,ensure_ascii=False));print('elapsed_seconds',elapsed)
