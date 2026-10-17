"""Exact exported endpoint-domain check; no tolerance/window search or fitting."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,sys,time
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='13fc67b4ca09d87cbeafd2e6074524c42a9137eee9f9353e3b20489d9a3482ff'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def main():
    start=time.perf_counter();assert not (H/'summary_r009.json').exists()
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'));refs=p['refs']
    assert all(sha(r['path'])==r['sha256'] for r in refs.values())
    manifest=json.loads(Path(refs['array_manifest']['path']).read_text(encoding='utf-8'))
    before=Path(refs['paired_npz']['path']).stat();rows=[]
    with np.load(refs['paired_npz']['path'],allow_pickle=False) as arrays:
        assert len(arrays.files)==len(manifest['arrays'])==192
        for meta in manifest['arrays']:
            assert meta['columns']==['t_s','P_I_kN','P_J_kN','U1_mm','U1_m','force_I_row','force_J_row','deformation_row']
            z=arrays[meta['key']];t,F,J,mm,d,Irow,Jrow,Urow=z.T
            assert np.isfinite(z).all() and np.array_equal(F,J) and np.array_equal(mm/1000,d)
            assert np.all(np.diff(t)>0) and list(z.shape)==meta['shape']
            peak=float(max(abs(F)));net=float(d[-1]-d[0]);netmm=float(mm[-1]-mm[0]);scale=float(max(abs(d-d[0])));scalemm=float(max(abs(mm-mm[0])))
            row={'Link':meta['Link'],'Story':meta['Story'],'Case':meta['Case'],'n_points':len(z),'t0_s':float(t[0]),'tT_s':float(t[-1]),
                'F0_I_kN':float(F[0]),'F0_J_kN':float(J[0]),'FT_I_kN':float(F[-1]),'FT_J_kN':float(J[-1]),'Pmax_kN':peak,
                'd0_native_mm':float(mm[0]),'dT_native_mm':float(mm[-1]),'d0_m':float(d[0]),'dT_m':float(d[-1]),
                'net_delta_native_mm':netmm,'net_delta_m':net,'record_max_abs_delta_from_d0_mm':scalemm,'record_max_abs_delta_from_d0_m':scale,
                'FT_over_Pmax':float(F[-1])/peak if peak else None,'abs_FT_over_Pmax':abs(float(F[-1]))/peak if peak else None,
                'force_ratio_status':'defined' if peak else 'undefined_zero_Pmax','net_delta_over_record_scale':net/scale if scale else None,
                'abs_net_delta_over_record_scale':abs(net)/scale if scale else None,'net_ratio_status':'defined' if scale else 'undefined_zero_record_scale',
                'F0_exact_zero':bool(F[0]==0),'FT_exact_zero':bool(F[-1]==0),'both_force_endpoints_exact_zero':bool(F[0]==0 and F[-1]==0),
                'net_delta_exact_zero':bool(net==0),'net_delta_mm_exact_zero':bool(netmm==0),
                'F0_I_cell':'I'+str(int(Irow[0])),'F0_J_cell':'I'+str(int(Jrow[0])),'FT_I_cell':'I'+str(int(Irow[-1])),'FT_J_cell':'I'+str(int(Jrow[-1])),
                'd0_U1_cell':'H'+str(int(Urow[0])),'dT_U1_cell':'H'+str(int(Urow[-1])),'local_array_key':meta['key']}
            rows.append(row)
    flagkeys=['F0_exact_zero','FT_exact_zero','both_force_endpoints_exact_zero','net_delta_exact_zero']
    counts={k:sum(r[k] for r in rows) for k in flagkeys};case=[]
    for name in ['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']:
        g=[r for r in rows if r['Case']==name];assert len(g)==32
        force=[r['abs_FT_over_Pmax'] for r in g if r['abs_FT_over_Pmax'] is not None]
        net=[r['abs_net_delta_over_record_scale'] for r in g if r['abs_net_delta_over_record_scale'] is not None]
        case.append({'Case':name,'n':len(g),**{k:sum(r[k] for r in g) for k in flagkeys},
            'abs_FT_over_Pmax_range':[min(force),max(force)] if force else None,
            'abs_net_delta_over_record_scale_range':[min(net),max(net)] if net else None,
            'undefined_force_ratio_count':sum(r['force_ratio_status']!='defined' for r in g),
            'undefined_net_ratio_count':sum(r['net_ratio_status']!='defined' for r in g)})
    after=Path(refs['paired_npz']['path']).stat()
    checks={'192_original_complete_record_endpoints':len(rows)==192,'all_I_J_and_mm_to_m_checks_pass':True,
        'm_and_native_mm_net_zero_flags_agree':all(r['net_delta_exact_zero']==r['net_delta_mm_exact_zero'] for r in rows),
        'zero_denominators_explicit_undefined':all((r['force_ratio_status']=='undefined_zero_Pmax')==(r['FT_over_Pmax'] is None) and (r['net_ratio_status']=='undefined_zero_record_scale')==(r['net_delta_over_record_scale'] is None) for r in rows),
        'frozen_input_SHA_and_protocol_unchanged':all(sha(r['path'])==r['sha256'] for r in refs.values()) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'NPZ_size_mtime_stable':(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'runtime_below_240_seconds':time.perf_counter()-start<240}
    assert all(checks.values())
    with (H/'endpoint_summary_192_r009.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# M-EXP-R009：有限原导出窗口的端点前提适用域','',
        '状态：candidate，待主控/角色2复核。检查只针对原导出窗口端点，不搜索新窗口、不补自由尾，不添加容差。', '',
        f"192组中：F0精确等于0有{counts['F0_exact_zero']}组，FT精确等于0有{counts['FT_exact_zero']}组，两力端同时精确为0有{counts['both_force_endpoints_exact_zero']}组；净总变形dT−d0精确为0有{counts['net_delta_exact_zero']}组。",
        '', '因此，现有原导出窗口'+('没有任何一组能按精确导出端点直接满足F0=FT=0前提。' if counts['both_force_endpoints_exact_zero']==0 else '有上列数量的组在采样端点上满足两力端精确为零，但仍不认证连续物理端口前提。'),
        '候选命题不要求总变形回零，所以净总变形是否为零只作适用域描述，不作为额外合格条件。FT的精确非零也不能被解释为工程上显著；本项未设置工程容差或检验近似前提。', '',
        '## 固定定义与逐工况结果', '',
        '原生P-I为kN，P-J仅逐点核重复；U1保留原mm和换算m。净变形=dT−d0。预先固定变化尺度s=max|d(t)−d0|；报告带符号及绝对净变形/s。另报告带符号及绝对FT/Pmax，Pmax=max|P-I|。任一分母0时对应比值明确undefined，不填0。两个比值的分母来自同一完整原导出窗口。', '',
        '| 工况 | 组数 | F0=0 | FT=0 | 两力端零 | 净总变形=0 | abs(FT)/Pmax范围 | abs(净变形)/s范围 |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for c in case:
        show=lambda key:'undefined' if c[key] is None else '–'.join(f'{v:.8g}' for v in c[key])
        lines.append(f"| {c['Case']} | {c['n']} | {c['F0_exact_zero']} | {c['FT_exact_zero']} | {c['both_force_endpoints_exact_zero']} | {c['net_delta_exact_zero']} | {show('abs_FT_over_Pmax_range')} | {show('abs_net_delta_over_record_scale_range')} |")
    lines+=['', f"本次力比值分母不可定义组数为{sum(c['undefined_force_ratio_count'] for c in case)}，净变形比值分母不可定义组数为{sum(c['undefined_net_ratio_count'] for c in case)}。192行CSV保留全部原带符号端点、峰力、净总变形、变化尺度、比值、精确相等标志，以及两端P-I/P-J和U1源格；没有另存点数组。", '',
        '## 来源与可认证范围', '',
        '只读冻结R006本地NPZ与manifest。NPZ SHA256为 `'+refs['paired_npz']['sha256']+'`；读取前后来源SHA及文件大小/mtime一致。RH4X/Y、SHW4X/Y、SHW7X/Y保留各自原0–50/59/53.9s窗口；未读原始Excel、拟合或运行求解器。', '',
        '本项只认证导出采样端点是否满足精确数值前提，不能从采样差分认证连续速度V，也不把Dport当真实D。真实参数、当前版本P/U1端口、质量映射等既有限制继续保留。对有限窗候选的连续证明仍由角色2审查，数据未满足前提不反驳条件命题本身。', '',
        '实际运行及7项检查结果见summary/run_record；本目录外证据不改、无Git操作。完成后冻结停止，由主控决定是否用于候选适用域说明。']
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    out={'evidence_id':p['evidence_id'],'review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
        'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'counts_exact_exported_endpoints':counts,'case_summaries':case,'checks':checks,
        'source_refs':refs,'outputs':{n:sha(H/n) for n in ['endpoint_summary_192_r009.csv','report.md']}}
    (H/'summary_r009.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    run={'command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],
        'python':sys.version,'numpy':np.__version__,'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r009.json'),'checks':checks}
    (H/'run_record_r009.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','counts_exact_exported_endpoints','case_summaries','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
