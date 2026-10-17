"""Fixed R002 integral reconstruction on frozen R006 histories; no fitting."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time
import numpy as np
H=Path(__file__).resolve().parent
PROTOCOL_SHA='8dd93c139aff83e515b8d7bc837cc33ca7bce4630452d52ecfa3cefff9d3e952'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def pack(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def readcsv(f):
    with Path(f).open(encoding='utf-8',newline='') as stream:return list(csv.DictReader(stream))
def writecsv(name,rows):
    with (H/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    started=time.perf_counter();assert not (H/'summary_r007.json').exists(),'Frozen output exists'
    assert sha(H/'protocol.json')==PROTOCOL_SHA
    p=json.loads((H/'protocol.json').read_text(encoding='utf-8'))
    refs=list(p['inputs'].values())+p['six_CSV_crosschecks']
    assert all(sha(x['path'] if 'path' in x else x['file'])==x['sha256'] for x in refs)
    paths={k:Path(v['path']) for k,v in p['inputs'].items()}
    m=json.loads(paths['array_manifest'].read_text(encoding='utf-8'))
    training=json.loads(paths['R002_training'].read_text(encoding='utf-8'))['best_grid_row']
    alpha=p['fixed_parameters']['alpha'];a=p['fixed_parameters']['a_m_per_kN'];b=p['fixed_parameters']['b']
    assert (alpha,a,b)==(training['alpha'],training['a_m_per_kN'],training['b_m_per_s_kN_power_inverse_alpha'])
    before=paths['paired_npz'].stat();rows=[];csvchecks=[]
    with np.load(paths['paired_npz'],allow_pickle=False) as arrays:
        assert set(arrays.files)=={x['key'] for x in m['arrays']} and len(arrays.files)==192
        for meta in m['arrays']:
            z=arrays[meta['key']];t,F,J,mm,d,ir,jr,ur=z.T;delta=d-d[0]
            assert np.isfinite(z).all() and np.array_equal(F,J) and np.array_equal(mm/1000,d)
            assert np.all(np.diff(t)>0) and np.max(abs(np.diff(t)-.02))<1e-10
            h=np.sign(F)*abs(F)**(1/alpha)
            integral=np.r_[0.,np.cumsum(np.diff(t)*(h[1:]+h[:-1])/2)]
            pred=a*(F-F[0])+b*integral;r=pred-delta
            rms=float(np.sqrt(np.mean(delta*delta)));rmse=float(np.sqrt(np.mean(r*r)))
            ratio=rmse/rms if rms!=0 else None;maxabs=float(max(abs(r)));ii=np.flatnonzero(abs(r)==maxabs)
            controls=[{'t_s':float(t[i]),'signed_residual_m':float(r[i]),'observed_delta_d_m':float(delta[i]),'predicted_delta_d_m':float(pred[i]),
                'P_I_kN':float(F[i]),'U1_m':float(d[i]),'P_I_cell':'I'+str(int(ir[i])),'P_J_cell':'I'+str(int(jr[i])),'U1_cell':'H'+str(int(ur[i]))} for i in ii]
            row={'Link':meta['Link'],'Story':meta['Story'],'Case':meta['Case'],
                'record_role':'sole_training_record' if [meta['Link'],meta['Case']]==p['only_training_record'] else 'same_model_conditional_check',
                'n_points':len(z),'t0_s':float(t[0]),'t1_s':float(t[-1]),'zero_force_points_retained':int(sum(F==0)),
                'F0_kN_observed':float(F[0]),'d0_m_observed':float(d[0]),'delta_d_RMS_m':rms,'RMSE_m':rmse,'MAE_m':float(np.mean(abs(r))),
                'max_abs_residual_m':maxabs,'max_residual_controllers_json':pack(controls),'mean_residual_m':float(np.mean(r)),
                'end_residual_m':float(r[-1]),'relative_RMSE':ratio,'relative_RMSE_percent':100*ratio if ratio is not None else None,
                'relative_RMSE_status':'defined' if ratio is not None else 'undefined_zero_denominator','local_array_key':meta['key']}
            rows.append(row)
        for ref in p['six_CSV_crosschecks']:
            old=readcsv(ref['file']);columns=['t_s','P_I_kN','P_J_kN','U1_mm','U1_m','force_I_row','force_J_row','deformation_row']
            x=np.array([[float(r[c]) for c in columns] for r in old]);key=old[0]['Link']+'__'+old[0]['Case']
            assert np.array_equal(x,arrays[key]);csvchecks.append({'key':key,'n_rows':len(old),'all_eight_columns_exact_equal':True})
    lookup={(r['Link'],r['Case']):r for r in rows};numeric_cross=[]
    def compare(label,key,expected):
        actual=lookup[key];diff={}
        for name,old in expected.items():
            value=actual[name];tol=2e-12 if name=='relative_RMSE' else 2e-14
            assert math.isclose(value,float(old),rel_tol=1e-9,abs_tol=tol),(label,key,name,value,old)
            diff[name]=value-float(old)
        numeric_cross.append({'reference':label,'Link':key[0],'Case':key[1],'numeric_differences':diff})
    def old_pair(best,link):
        prefix='K2_' if link=='K2' else 'K5_transfer_'
        return {k:best[prefix+k] for k in ['RMSE_m','MAE_m','max_abs_residual_m','mean_residual_m','end_residual_m']}|{
            'delta_d_RMS_m':best[prefix+'y_RMS_m'],'relative_RMSE':best[prefix+'RMSE_over_y_RMS']}
    review4=json.loads(paths['R004_review_numbers'].read_text(encoding='utf-8'))['best_grid_row']
    for link in ['K2','K5']:
        compare('R002_frozen_fit', (link,'RH4X'),old_pair(training,link))
        compare('R004_independent_review', (link,'RH4X'),old_pair(review4,link))
    oldmetrics=readcsv(paths['R003_metrics'])
    review7=json.loads(paths['R007_review_numbers'].read_text(encoding='utf-8'))['groups']
    for label,records in [('R003_frozen_transfer',oldmetrics),('R007_independent_review',[x['metrics'] for x in review7])]:
        for old in records:
            expected={k:old[k] for k in ['RMSE_m','MAE_m','max_abs_residual_m','mean_residual_m','end_residual_m','delta_d_RMS_m']}
            expected['relative_RMSE']=old['RMSE_over_delta_d_RMS'];compare(label,(old['Link'],old['Case']),expected)
    worst=[];case_summaries=[]
    for case in p['cases']:
        group=[r for r in rows if r['Case']==case];assert len(group)==32
        ordered=sorted([r for r in group if r['relative_RMSE'] is not None],key=lambda r:(-r['relative_RMSE'],int(r['Link'][1:])))
        cutoff=ordered[min(1,len(ordered)-1)]['relative_RMSE'] if ordered else None
        selected=[r for r in ordered if r['relative_RMSE']>=cutoff] if ordered else []
        for r in selected:worst.append({'case_relative_error_rank':1+sum(x['relative_RMSE']>r['relative_RMSE'] for x in ordered),**r})
        case_summaries.append({'Case':case,'n_groups':len(group),'undefined_ratio_count':len(group)-len(ordered),
            'relative_RMSE_min':min((r['relative_RMSE'] for r in ordered),default=None),
            'relative_RMSE_max':max((r['relative_RMSE'] for r in ordered),default=None),
            'RMSE_m_min':min(r['RMSE_m'] for r in group),'RMSE_m_max':max(r['RMSE_m'] for r in group),
            'worst2_with_exact_ties':[r['Link'] for r in selected]})
    after=paths['paired_npz'].stat()
    checks={'192_all_groups_retained':len(rows)==192,'521472_all_original_points':sum(r['n_points'] for r in rows)==521472,
        'sole_K2_RH4X_training_191_checks':sum(r['record_role']=='sole_training_record' for r in rows)==1,
        'all_units_time_and_I_J_checks_passed':True,'all_six_CSVs_reproduce_frozen_arrays':len(csvchecks)==6,
        'R002_R003_R004_R007_metric_crosschecks':len(numeric_cross)==12,'zero_denominators_explicit_not_filled':all(r['relative_RMSE_status']=='undefined_zero_denominator' for r in rows if r['relative_RMSE'] is None),
        'all_frozen_SHA_unchanged':all(sha(x['path'] if 'path' in x else x['file'])==x['sha256'] for x in refs) and sha(H/'protocol.json')==PROTOCOL_SHA,
        'NPZ_size_mtime_stable':(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'runtime_below_480_seconds':time.perf_counter()-started<480}
    assert all(checks.values()),checks
    writecsv('all_device_integral_metrics_r007.csv',rows);writecsv('worst2_by_case_r007.csv',worst)
    lines=['# M-EXP-R007：192组固定参数积分重建误差','', '状态：candidate，待独立复核。K2/RH4X为唯一训练记录，其余191组为同模型跨器件/跨工况条件检查。', '',
        '本项不拟合或选参。固定R002 alpha=0.30、a=2.0006042528243313e−6 m/kN、b=1.1798190016520894e−9；保留全部521472个原始点、零点与小值，P-I仅计一次，U1由mm换为m。', '',
        '```', 'd_pred−d0 = a(F−F0) + b trapezoid_integral(sign(F)|F|^(1/alpha))', 'r = (d_pred−d0) − (d_obs−d0)', 'relative RMSE = RMSE(r)/RMS(d_obs−d0)', '```', '',
        '各组RMSE、MAE、最大绝对残差、平均/末残差都基于完整原始时间网格。最大残差保留全部精确同值控制点的符号、时刻、P-I/J与U1源格。若原Δd RMS为零，相对RMSE明确不可定义，输出空/JSON null，保留该组但不参与相对误差排名。没有任何偏置拟合、裁剪、去均值、末点修正或工程合格阈值。', '',
        '## 各工况描述性范围', '', '| 工况 | 组数 | 相对RMSE最小–最大/% | RMSE最小–最大/m | 不可定义组数 | 最差前2含并列 |', '|---|---:|---:|---:|---:|---|']
    for c in case_summaries:
        rr='不可定义' if c['relative_RMSE_min'] is None else f"{100*c['relative_RMSE_min']:.6g}–{100*c['relative_RMSE_max']:.6g}"
        lines.append(f"| {c['Case']} | {c['n_groups']} | {rr} | {c['RMSE_m_min']:.6g}–{c['RMSE_m_max']:.6g} | {c['undefined_ratio_count']} | {'、'.join(c['worst2_with_exact_ties'])} |")
    lines+=['', '## 预定相对RMSE最差前2记录定位', '',
        '按每工况32组相对RMSE降序取第二名的值为阈值，包含全部精确边界并列。此处仅为描述，不将不同波形/工况当独立事件，也不把时刻当独立样本。', '',
        '| 工况 | Link/层 | 原Δd RMS/m | RMSE/m | 相对RMSE/% | 最大绝对残差/m | 最差点时刻/s及有符号残差/m | 源格P-I/U1 |', '|---|---|---:|---:|---:|---:|---|---|']
    for r in worst:
        cs=json.loads(r['max_residual_controllers_json'])
        lines.append(f"| {r['Case']} | {r['Link']}/{r['Story']} | {r['delta_d_RMS_m']:.6g} | {r['RMSE_m']:.6g} | {r['relative_RMSE_percent']:.6g} | {r['max_abs_residual_m']:.6g} | "+'; '.join(f"{c['t_s']:.8g} / {c['signed_residual_m']:+.6g}" for c in cs)+' | '+'; '.join(c['P_I_cell']+'/'+c['U1_cell'] for c in cs)+' |')
    lines+=['', '## 来源与核验', '',
        '只读取R006冻结本地NPZ及元数据和六条既有CSV，未读取原始Excel。NPZ SHA256为 `'+p['inputs']['paired_npz']['sha256']+'`，所有来源SHA前后相同，NPZ大小/mtime保持。R011已审192组三流覆盖和源定位，本项继承其限制；六旧CSV八列逐点完全一致，以及R002/R003原指标与R004/R007独审数字的12组交叉核对均通过。这些是同源证据/算术的一致性检查，不构成新的独立原表读取器。', '',
        '输入F本身是已观测到的结构响应，重建Δd不是从地震输入前向预测结构响应。191个检查记录不等于191个独立地震事件，也不表示未经使用的事件外验。真实参数、当前版本端口/质量映射及基收敛等未知项继续保留；低误差不能认证全88只同参、物理真实性或因果减幅。', '',
        f"数值脚本完成全部192行指标和{len(worst)}条预定最差记录，10项检查全部通过，exit 0。没有另存完整残差数组；原NPZ可复算。192行总表保留所有组，最差前2不会替代或删去其他组。实际时间、命令、版本和SHA见summary/run_record。"]
    (H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (H/'next-task.md').write_text('独立只读冻结R006 NPZ与R007协议，用不同累计/指标实现复核全部192组原Δd RMS、RMSE/MAE/最大残差符号时刻源格、均值末值及相对RMSE；核唯一训练记录K2/RH4X、191同模型条件检查和每case最差前2含精确并列。核六旧CSV及R004/R007数字交叉一致、无零分母补0和完整残差新数组。不拟合、不读Excel、不设合格阈值或外推全88。冻结后本角色停止。\n',encoding='utf-8')
    out={'evidence_id':p['evidence_id'],'review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-started,
        'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'n_group_rows':len(rows),'n_worst_rows':len(worst),'n_training':1,'n_conditional_check':191,
        'case_summaries':case_summaries,'six_CSV_input_crosschecks':csvchecks,'old_and_review_metric_crosschecks':numeric_cross,'checks':checks,
        'source_refs':p['inputs'],'outputs':{n:sha(H/n) for n in ['all_device_integral_metrics_r007.csv','worst2_by_case_r007.csv','report.md','next-task.md']}}
    (H/'summary_r007.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'run_record_r007.json').write_text(json.dumps({'command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,'finished_utc':out['finished_utc'],
        'elapsed_seconds':out['elapsed_seconds'],'python':sys.version,'numpy':np.__version__,'code_sha256':sha(__file__),'summary_sha256':sha(H/'summary_r007.json'),'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','n_group_rows','n_worst_rows','case_summaries','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
