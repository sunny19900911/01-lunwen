"""Bounded two-sheet Link extraction and fixed conditional bookkeeping, no fit."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,math,sys,time
import numpy as np
sys.path.insert(0,'C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts')
from stream_csi import Workbook,TAG,ET,file_sha256
HERE=Path(__file__).resolve().parent
PROTOCOL_SHA='e26d983f153fc9cce3412d4334ff8c8d249360988b34ccfb6650d20190236e89'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def total(x):return math.fsum(float(v) for v in x)
def pack(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def writecsv(name,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def decode(cell,wb):
    if cell is None:return None
    typ=cell.get('t');v=cell.find(TAG('v'))
    if typ=='inlineStr':return ''.join(t.text or '' for t in cell.iter(TAG('t')))
    if v is None:return None
    if typ=='s':return wb.shared[int(v.text)]
    return v.text if typ in ('str','e') else float(v.text)

def extract(wb,force,p,data,meta,started):
    kind='P' if force else 'U';sheet='Element Forces - Links' if force else 'Element Deformations - Links'
    remaining=sum(len(a) for a in data.values())*(2 if force else 1);selected=0;last=0
    links={k[0] for k in data};bound=p['bounded_source_rows'][kind]
    with wb.z.open(wb.sheets[sheet]) as stream:
        for _,el in ET.iterparse(stream,events=('end',),tag=TAG('row')):
            try:
                n=int(el.get('r'));last=n
                assert n<=bound,'Frozen source bound reached before complete targets'
                if n%100000==0:
                    print(pack({'sheet':sheet,'source_row':n,'selected':selected,'elapsed_s':time.perf_counter()-started}),flush=True)
                    assert time.perf_counter()-started<480,'Bounded runtime exhausted'
                cells={Workbook.col_index(c.get('r','')):c for c in el}
                if n==2:
                    headers=[decode(cells.get(i),wb) for i in range(14 if force else 13)]
                    assert headers[:7]==['Story','Unique Name','Link Element','Output Case','Case Type','Step Type','Step Number']
                    assert headers[8 if force else 7]==('P' if force else 'U1');continue
                if n==3:
                    assert decode(cells.get(8 if force else 7),wb)==('kN' if force else 'mm');continue
                if n<4:continue
                ident=str(decode(cells.get(1),wb));element=str(decode(cells.get(2),wb));link=ident if ident in links else element
                if link not in links:continue
                case=str(decode(cells.get(3),wb));key=(link,case)
                if key not in data:continue
                assert decode(cells.get(0),wb)==meta[key]['Story']
                assert decode(cells.get(4),wb)=='NonModHist' and decode(cells.get(5),wb)=='Step By Step'
                t=float(decode(cells.get(6),wb));i=int(round(t/.02));a=data[key]
                assert 0<=i<len(a) and abs(t-i*.02)<1e-10
                if force:
                    loc=decode(cells.get(7),wb);assert loc in ['I-End','J-End']
                    vcol,rcol=(1,5) if loc=='I-End' else (2,6)
                else:vcol,rcol=3,7
                assert np.isnan(a[i,rcol]),'Duplicate target stream time'
                value=decode(cells.get(8 if force else 7),wb);assert value is not None and math.isfinite(float(value))
                if force and loc=='I-End':a[i,0]=t
                else:assert a[i,0]==t,'Three-stream time mismatch'
                a[i,vcol]=float(value);a[i,rcol]=n
                if not force:a[i,4]=float(value)/1000
                selected+=1;remaining-=1
                if remaining==0:break
            finally:
                el.clear()
                while el.getprevious() is not None:del el.getparent()[0]
    assert remaining==0,'Missing group or grid point: no filling allowed'
    return {'sheet':sheet,'sheet_passes':1,'last_source_row':last,'frozen_source_bound':bound,'selected_numeric_rows':selected,'completed_all_targets':True}

def main():
    start=time.perf_counter();assert not (HERE/'summary_r006.json').exists() and not (HERE/'failure_r006.json').exists()
    assert sha(HERE/'protocol.json')==PROTOCOL_SHA
    p=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
    for ref in [p['coverage_ref'],p['training_ref']]+p['crosschecks']:assert sha(ref['path'])==ref['sha256']
    fitted=json.loads(Path(p['training_ref']['path']).read_text(encoding='utf-8'))['best_grid_row']
    alpha=p['fixed_parameters']['alpha'];a=p['fixed_parameters']['a_m_per_kN'];b=p['fixed_parameters']['b']
    assert (alpha,a,b)==(fitted['alpha'],fitted['a_m_per_kN'],fitted['b_m_per_s_kN_power_inverse_alpha'])
    meta={(x['Link'],x['Case']):x for x in p['targets']};data={k:np.full((int(x['expected_n']),8),np.nan) for k,x in meta.items()}
    raw=Path(p['source']);before=raw.stat();assert before.st_size==p['source_bytes'];source_sha=file_sha256(raw);assert source_sha==p['source_sha256']
    try:
        with Workbook(raw) as wb:audits=[extract(wb,True,p,data,meta,start),extract(wb,False,p,data,meta,start)]
    except Exception as e:
        completed={k[0]+'__'+k[1]:v for k,v in data.items() if np.isfinite(v).all()}
        if completed:np.savez_compressed(HERE/'local_partial_histories_r006.npz',**completed)
        (HERE/'failure_r006.json').write_text(json.dumps({'error':str(e),'elapsed_seconds':time.perf_counter()-start,'completed_keys':list(completed),'source_sha256':source_sha},indent=2)+'\n',encoding='utf-8')
        raise
    after=raw.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    rows=[];localmeta=[]
    for key,z in data.items():
        link,case=key;story=meta[key]['Story'];t,F,J,mm,d,ir,jr,ur=z.T
        assert np.isfinite(z).all() and np.array_equal(F,J) and np.array_equal(mm/1000,d)
        assert np.max(abs(np.diff(t)-.02))<1e-10 and t[0]==0
        assert all(np.all(np.diff(v)>0) for v in [ir,jr,ur])
        h=np.sign(F)*abs(F)**(1/alpha);dt=np.diff(t);Fav=(F[1:]+F[:-1])/2
        w=Fav*np.diff(d);us=(a/2)*np.diff(F*F);dp=w-us
        df=b*dt*(F[1:]*h[1:]+F[:-1]*h[:-1])/2
        product=b/4*dt*np.diff(F)*np.diff(h)
        residual=a*(F-F[0])+b*np.r_[0.,np.cumsum(dt*(h[1:]+h[:-1])/2)]-(d-d[0]);rw=Fav*np.diff(residual)
        W=total(w);Us=a*(F[-1]**2-F[0]**2)/2;D=W-Us;Df=total(df);pt=total(product);rwt=total(rw);identity=Df-D-pt-rwt
        tol=1e-12*max(1,abs(W),abs(Df));assert abs(identity)<tol and max(abs(df-dp-product-rw))<tol and min(product)>=0
        fi=np.flatnonzero(abs(F)==max(abs(F)));ui=np.flatnonzero(abs(mm)==max(abs(mm)))
        fctrl=[{'t_s':float(t[i]),'signed_P_kN':float(F[i]),'P_I_cell':'I'+str(int(ir[i])),'P_J_cell':'I'+str(int(jr[i]))} for i in fi]
        uctrl=[{'t_s':float(t[i]),'signed_U1_mm':float(mm[i]),'U1_cell':'H'+str(int(ur[i]))} for i in ui]
        imin=int(np.argmin(dp));name=link+'__'+case
        rows.append({'Link':link,'Story':story,'Case':case,'n_points':len(z),'max_abs_native_P_kN':float(max(abs(F))),
            'force_peak_controllers_json':pack(fctrl),'max_abs_native_U1_mm':float(max(abs(mm))),'U1_peak_controllers_json':pack(uctrl),
            'Wtrap_native_kNm':W,'DeltaUs_conditional_kNm':Us,'Dport_conditional_kNm':D,'Dforce_trap_model_kNm':Df,
            'Dforce_minus_Dport_kNm':Df-D,'discrete_product_kNm':pt,'regression_residual_work_kNm':rwt,
            'identity_residual_kNm':identity,'max_interval_identity_abs_kNm':float(max(abs(df-dp-product-rw))),
            'negative_Dport_increment_count_unclipped':int(sum(dp<0)),'minimum_Dport_increment_kNm':float(dp[imin]),
            'minimum_Dport_interval_start_s':float(t[imin]),'minimum_Dport_interval_end_s':float(t[imin+1]),
            'all_three_streams_complete':True,'I_J_pointwise_equal':True,'local_array_key':name})
        localmeta.append({'key':name,'Link':link,'Story':story,'Case':case,'shape':list(z.shape),'columns':p['paired_columns']})
    cross=[]
    for ref in p['crosschecks']:
        with Path(ref['path']).open(encoding='utf-8',newline='') as f:old=list(csv.DictReader(f))
        z=data[(old[0]['Link'],old[0]['Case'])]
        oldarray=np.array([[float(x[c]) for c in p['paired_columns']] for x in old])
        assert np.array_equal(z,oldarray),'Frozen six-record re-extraction mismatch'
        cross.append({'file':ref['path'],'sha256':ref['sha256'],'n_rows':len(old),'all_eight_columns_exactly_equal':True})
    ranks=[]
    for case in p['cases']:
        for story in p['stories']:
            group=[r for r in rows if r['Case']==case and r['Story']==story];assert len(group)==8
            for metric in ['max_abs_native_P_kN','Dport_conditional_kNm']:
                ordered=sorted(group,key=lambda r:(-r[metric],int(r['Link'][1:])));hi,lo=ordered[1][metric],ordered[-2][metric]
                for side in ['top2','bottom2']:
                    selected=[r for r in ordered if r[metric]>=hi] if side=='top2' else [r for r in ordered if r[metric]<=lo]
                    for r in selected:ranks.append({'Case':case,'Story':story,'metric':metric,'side_with_exact_boundary_ties':side,
                        'rank_desc_competition':1+sum(x[metric]>r[metric] for x in group),'Link':r['Link'],'value':r[metric],
                        'max_abs_native_P_kN':r['max_abs_native_P_kN'],'Wtrap_native_kNm':r['Wtrap_native_kNm'],'Dport_conditional_kNm':r['Dport_conditional_kNm']})
    writecsv('device_record_summary_r006.csv',rows);writecsv('within_story_rank_extremes_r006.csv',ranks)
    print(pack({'stage':'192_group_checks_and_six_CSV_crosschecks_passed','elapsed_s':time.perf_counter()-start}),flush=True)
    np.savez_compressed(HERE/'local_paired_histories_r006.npz',**{k[0]+'__'+k[1]:v for k,v in data.items()})
    (HERE/'local_history_manifest_r006.json').write_text(json.dumps({'local_only_not_upload':True,'arrays':localmeta},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    checks={'192_prespecified_groups':len(rows)==192,'32_common_complete_devices':len({r['Link'] for r in rows})==32,
        'all_three_streams_and_units_verified':True,'P_I_J_equal_counted_once':True,'all_six_frozen_CSVs_exactly_reproduced':len(cross)==6,
        'all_discrete_identity_checks_pass':True,'no_negative_increment_clipping':True,
        'source_SHA_and_stat_stable':True,'frozen_refs_and_protocol_unchanged':sha(HERE/'protocol.json')==PROTOCOL_SHA and all(sha(r['path'])==r['sha256'] for r in [p['coverage_ref'],p['training_ref']]+p['crosschecks']),
        'runtime_below_480_seconds':time.perf_counter()-start<480}
    assert all(checks.values())
    files=['device_record_summary_r006.csv','within_story_rank_extremes_r006.csv','local_paired_histories_r006.npz','local_history_manifest_r006.json']
    out={'evidence_id':p['evidence_id'],'review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
        'protocol_sha256':PROTOCOL_SHA,'code_sha256':sha(__file__),'reader_sha256':sha(Path('C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts/stream_csi.py')),
        'source_sha256':source_sha,'source_before':{'bytes':before.st_size,'mtime_ns':before.st_mtime_ns},'source_after':{'bytes':after.st_size,'mtime_ns':after.st_mtime_ns},
        'sheet_audits':audits,'group_count':len(rows),'total_paired_points_local_only':sum(len(z) for z in data.values()),'rank_rows':len(ranks),
        'six_CSV_crosschecks':cross,'max_abs_total_identity_residual_kNm':max(abs(r['identity_residual_kNm']) for r in rows),
        'negative_increment_groups':sum(r['negative_Dport_increment_count_unclipped']>0 for r in rows),'checks':checks,
        'outputs':[{'file':f,'bytes':(HERE/f).stat().st_size,'sha256':sha(HERE/f),'local_only':f.startswith('local_')} for f in files]}
    (HERE/'summary_r006.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    run={'command_argv':[sys.executable,'-X','utf8',str(Path(__file__).resolve())],'exit_code':0,'elapsed_seconds':out['elapsed_seconds'],'finished_utc':out['finished_utc'],
        'python':sys.version,'numpy':np.__version__,'code_sha256':sha(__file__),'summary_sha256':sha(HERE/'summary_r006.json'),'checks':checks}
    (HERE/'run_record_r006.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','sheet_audits','group_count','total_paired_points_local_only','rank_rows','max_abs_total_identity_residual_kNm','negative_increment_groups','checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
