"""Bounded target-only Link read and fixed-parameter transfer; no fit or alpha selection."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time
import numpy as np

HERE=Path(__file__).resolve().parent
TOPIC=HERE.parents[4]
CACHE=Path('E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/W5-重燃双塔连体/research/maxwell-20261017/experiments/R001/core-cache')
SKILL=Path('C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts')
sys.path.insert(0,str(SKILL))
from stream_csi import Workbook,TAG,ET,file_sha256
PROTOCOL_SHA='84fe57efb19cf7dbbeb8b8ef5deb0f432eee3dacf41e0f21c29a5cc89d620fae'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writecsv(name,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def decode(cell,wb):
    if cell is None:return None
    typ=cell.get('t');v=cell.find(TAG('v'))
    if typ=='inlineStr':return ''.join(t.text or '' for t in cell.iter(TAG('t')))
    if v is None:return None
    if typ=='s':return wb.shared[int(v.text)]
    if typ in ('str','e'):return v.text
    return float(v.text)
def read_targets(wb,sheet,force,expected,targets,started):
    stores={(link,case,loc):{} for link,case in targets for loc in (['I','J'] if force else ['U'])}
    selected_rows=0;skipped_rows=0;last=0;units=None;duplicates=0
    with wb.z.open(wb.sheets[sheet]) as stream:
        for _,elem in ET.iterparse(stream,events=('end',),tag=TAG('row')):
            try:
                n=int(elem.get('r'));last=n
                assert n<=200000,'Bounded target row limit exceeded'
                assert time.perf_counter()-started<480,'Runtime limit exceeded'
                cells={Workbook.col_index(c.get('r','')):c for c in elem}
                if n==2:
                    headers=[decode(cells.get(i),wb) for i in range(14 if force else 13)]
                    assert headers[3:7]==['Output Case','Case Type','Step Type','Step Number']
                    assert headers[8 if force else 7]==('P' if force else 'U1')
                    continue
                if n==3:
                    units=decode(cells.get(8 if force else 7),wb)
                    assert units==('kN' if force else 'mm');continue
                if n<4:continue
                # Non-target/Y numeric force and deformation cells are never decoded.
                case=str(decode(cells.get(3),wb))
                if case not in expected:skipped_rows+=1;continue
                ident=str(decode(cells.get(1),wb));element=str(decode(cells.get(2),wb))
                link=ident if ident in {'K2','K5'} else element
                if (link,case) not in targets:skipped_rows+=1;continue
                assert decode(cells.get(4),wb)=='NonModHist' and decode(cells.get(5),wb)=='Step By Step'
                t=float(decode(cells.get(6),wb));tick=int(round(t*100));assert abs(t*100-tick)<1e-6 and tick in expected[case]
                loc=('I' if decode(cells.get(7),wb)=='I-End' else 'J' if decode(cells.get(7),wb)=='J-End' else '?') if force else 'U'
                assert loc!='?'
                value=decode(cells.get(8 if force else 7),wb);assert value is not None and math.isfinite(float(value))
                key=(link,case,loc);duplicates+=int(tick in stores[key]);assert tick not in stores[key],'Duplicate target point'
                stores[key][tick]={'t':t,'value':float(value),'row':n,'Story':str(decode(cells.get(0),wb)),
                    'UniqueName':ident,'LinkElement':element}
                selected_rows+=1
                if all(len(records)==len(expected[key[1]]) for key,records in stores.items()):break
            finally:
                elem.clear()
                while elem.getprevious() is not None:del elem.getparent()[0]
    assert all(set(records)==expected[key[1]] for key,records in stores.items()),'Missing target input: no filling allowed'
    return stores,{'sheet':sheet,'last_scanned_source_row':last,'selected_numeric_rows':selected_rows,
        'skipped_non_target_rows':skipped_rows,'duplicates':duplicates,'units':units,
        'stopped_after_targets_complete':True,'global_extra_row_check_inherited_from_same_source_R001':True}
def metrics(y,pred):
    e=pred-y;rmse=float(np.sqrt(np.mean(e*e)));rms=float(np.sqrt(np.mean(y*y)))
    return {'RMSE_m':rmse,'RMSE_mm':1000*rmse,'MAE_m':float(np.mean(abs(e))),
        'max_abs_residual_m':float(max(abs(e))),'mean_residual_m':float(np.mean(e)),
        'end_residual_m':float(e[-1]),'delta_d_RMS_m':rms,'RMSE_over_delta_d_RMS':rmse/rms if rms else None}
def main():
    started=time.perf_counter();prot=HERE/'protocol.json';assert sha(prot)==PROTOCOL_SHA
    p=json.loads(prot.read_text(encoding='utf-8'));output=HERE/'transfer_summary_r003.json';assert not output.exists(),'Frozen output exists'
    summary_path=(HERE/p['training_summary']).resolve();coverage_path=(HERE/p['original_coverage']).resolve()
    assert sha(summary_path)==p['training_summary_sha256'] and sha(coverage_path)==p['original_coverage_sha256']
    source_checks=[(summary_path,p['training_summary_sha256']),(coverage_path,p['original_coverage_sha256']),
        (TOPIC/'research/roles/literature/maxwell-session004/R003-link-force-deformation-port-check.md',p['port_source_sha256']),
        (TOPIC/'research/roles/verification/maxwell-session004/条件积分回归独审-R004.md',p['regression_review_sha256'])]
    assert all(sha(path)==digest for path,digest in source_checks)
    trained=json.loads(summary_path.read_text(encoding='utf-8'))['best_grid_row']
    alpha=float(p['fixed_parameters']['alpha']);a=float(p['fixed_parameters']['a_m_per_kN']);b=float(p['fixed_parameters']['b_m_per_s_kN_power_inverse_alpha'])
    assert (alpha,a,b)==(trained['alpha'],trained['a_m_per_kN'],trained['b_m_per_s_kN_power_inverse_alpha'])
    targets=[tuple(x) for x in p['targets']]
    with coverage_path.open(encoding='utf-8',newline='') as f:coverage=list(csv.DictReader(f))
    for link,case in targets:
        row=next(r for r in coverage if r['Link']==link and r['Case']==case)
        assert row['complete_export_grid']=='True' and all(row[c]=='0' for c in ['dup_I','dup_J','dup_U','invalid_rows'])
    manifest=json.loads((CACHE/'manifest.json').read_text(encoding='utf-8-sig'));expected={};times={}
    with np.load(CACHE/'Base_Reactions.npz',allow_pickle=False) as z:
        for gid,g in manifest['tables']['Base Reactions']['groups'].items():
            case=g['keys']['Output Case']
            if case in {'SHW4X','SHW7X'}:
                times[case]=z[gid][:,0].copy();expected[case]={int(round(float(t)*100)) for t in times[case]}
    raw=Path(p['source']);before=raw.stat();actual_sha=file_sha256(raw);assert actual_sha==p['expected_source_sha256']
    with Workbook(raw) as wb:
        forces,fa=read_targets(wb,'Element Forces - Links',True,expected,targets,started)
        deforms,ua=read_targets(wb,'Element Deformations - Links',False,expected,targets,started)
    after=raw.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    prepared=[];qa=[]
    for link,case in targets:
        ticks=sorted(expected[case]);rows=[]
        for tick in ticks:
            I,J,U=[stores[(link,case,loc)][tick] for stores,loc in [(forces,'I'),(forces,'J'),(deforms,'U')]]
            assert I['t']==J['t']==U['t'];assert I['Story']==J['Story']==U['Story']=='Story11'
            rows.append({'Link':link,'Story':U['Story'],'Case':case,'t_s':U['t'],'P_I_kN':I['value'],'P_J_kN':J['value'],
                'U1_mm':U['value'],'U1_m':U['value']/1000,'force_I_row':I['row'],'force_J_row':J['row'],'deformation_row':U['row'],
                'P_I_cell':'I'+str(I['row']),'P_J_cell':'I'+str(J['row']),'U1_cell':'H'+str(U['row'])})
        F=np.array([r['P_I_kN'] for r in rows]);J=np.array([r['P_J_kN'] for r in rows]);d=np.array([r['U1_m'] for r in rows]);t=np.array([r['t_s'] for r in rows])
        assert np.array_equal(F,J) and np.array_equal(t,times[case]) and np.all(np.diff(t)>0)
        assert all(all(rows[i+1][col]>rows[i][col] for i in range(len(rows)-1)) for col in ['force_I_row','force_J_row','deformation_row'])
        qa.append({'Link':link,'Case':case,'n':len(rows),'t0':float(t[0]),'t1':float(t[-1]),'I_J_identical':True,
            'time_matches_cached_full_grid':True,'source_rows_increasing':True,'P_units':'kN','U_raw_units':'mm','mm_to_m_divisor':1000})
        prepared.append((link,case,rows,t,F,d))
    # Predictions start only after all four target inputs pass the checks above.
    allres=[];worst=[];metrics_rows=[];input_files=[]
    for link,case,rows,t,F,d in prepared:
        name=f'local_input_{link}_{case}_r003.csv';writecsv(name,rows);input_files.append(HERE/name)
        g=np.sign(F)*abs(F)**(1/alpha);integ=np.r_[0.,np.cumsum((g[1:]+g[:-1])/2*np.diff(t))]
        y=d-d[0];pred=a*(F-F[0])+b*integ;e=pred-y
        m={'Link':link,'Case':case,'n':len(rows),'alpha_fixed':alpha,'a_fixed':a,'b_fixed':b,
            'F0_kN_observed':float(F[0]),'d0_m_observed':float(d[0]),'zero_force_points_retained':int(sum(F==0)),
            'max_abs_force_kN':float(max(abs(F))),**metrics(y,pred)};metrics_rows.append(m)
        rr=[]
        for i,r in enumerate(rows):
            rr.append({**r,'observed_delta_d_m':float(y[i]),'fixed_model_predicted_delta_d_m':float(pred[i]),
                'residual_pred_minus_data_m':float(e[i])})
        allres+=rr;worst += [rr[int(i)] for i in np.argsort(abs(e))[-5:][::-1]]
    writecsv('transfer_metrics_r003.csv',metrics_rows);writecsv('local_all_residuals_r003.csv',allres);writecsv('worst_points_r003.csv',worst)
    checks={'four_and_only_four_targets':len(prepared)==4,'all_11294_original_target_points_retained':len(allres)==11294,
        'units_IJ_and_coverage_verified_before_prediction':True,'fixed_RH4X_parameters_no_refit':True,
        'no_Y_numeric_histories_extracted':True,'source_same_version_actually_rehashed':actual_sha==p['expected_source_sha256'],
        'source_size_mtime_stable':True,'all_frozen_source_files_unchanged':all(sha(path)==digest for path,digest in source_checks) and sha(prot)==PROTOCOL_SHA,
        'runtime_below_480_seconds':time.perf_counter()-started<480}
    files=input_files+[HERE/'transfer_metrics_r003.csv',HERE/'local_all_residuals_r003.csv',HERE/'worst_points_r003.csv']
    result={'evidence_id':p['evidence_id'],'review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds':time.perf_counter()-started,'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),
        'fixed_parameters':p['fixed_parameters'],'training_summary_sha256':sha(summary_path),
        'raw_source':str(raw),'raw_source_sha256':actual_sha,'actually_rehashed_this_run':True,
        'source_before':{'bytes':before.st_size,'mtime_ns':before.st_mtime_ns},'source_after':{'bytes':after.st_size,'mtime_ns':after.st_mtime_ns},
        'target_read_audit':[fa,ua],'target_input_QA':qa,'metrics':metrics_rows,'checks':checks,
        'outputs':[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f)} for f in files],
        'source_documents':[{'path':str(path),'sha256':digest} for path,digest in source_checks],
        'core_grid_manifest_sha256':sha(CACHE/'manifest.json'),'core_grid_cache_sha256':sha(CACHE/'Base_Reactions.npz'),
        'interpretation':'Fixed constitutive-integral relation transfer conditional on native force history and P/U1 mapping; not forward prediction from ground motion, independent-event validation, true attribute certification, all88 consistency or energy closure.',
        'local_files_policy':'Four full input CSVs and full residual CSV are local review evidence. Master decides each Git whitelist; no NPZ was made.'}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    record={'evidence_id':p['evidence_id'],'review_status':'candidate','command_argv':[sys.executable,str(Path(__file__).resolve())],
        'finished_utc':result['finished_utc'],'elapsed_seconds':result['elapsed_seconds'],'python':sys.version,'numpy':np.__version__,
        'exit_code_after_checks':0 if all(checks.values()) else 1,'reader_module_sha256':sha(SKILL/'stream_csi.py'),
        'protocol_last_write_utc':datetime.fromtimestamp(prot.stat().st_mtime,timezone.utc).isoformat(),
        'code_sha256':sha(__file__),'summary_sha256':sha(output),'checks':checks}
    (HERE/'run_record_r003.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'metrics':metrics_rows,'read_audit':[fa,ua],'checks':checks,'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())
if __name__=='__main__':sys.stdout.reconfigure(encoding='utf-8');main()
