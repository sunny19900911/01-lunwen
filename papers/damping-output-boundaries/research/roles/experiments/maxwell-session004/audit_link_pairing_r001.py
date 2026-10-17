"""One target-only read of Link P/U1; reuse core time grids, no solver or fitting."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json, math, sys, time
import numpy as np

HERE=Path(__file__).resolve().parent
W5=Path('E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/W5-重燃双塔连体')
BASE=W5/'research/maxwell-20261017'
CACHE=BASE/'experiments/R001/core-cache'
RAW=Path('E:/!!!!!!!!TO HOME/有控.xlsx')
SKILL=Path('C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts')
sys.path.insert(0,str(SKILL))
from stream_csi import Workbook, file_sha256

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writecsv(name,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    started=time.perf_counter();sentinel=HERE/'pairing_audit_r001.json'
    assert not sentinel.exists(),'Refuse to overwrite frozen run'
    before=RAW.stat();manifest=json.loads((CACHE/'manifest.json').read_text(encoding='utf-8-sig'))
    assert before.st_size==manifest['bytes']==635525054
    source_sha=file_sha256(RAW);assert source_sha==manifest['sha256']=='9d999dfac02ad758b83b52f908ac5df6925b869b9d0a96c032c24e729bf82c23'
    small_path=BASE/'roles/experiments/metadata/controlled_small_tables.json'
    small=json.loads(small_path.read_text(encoding='utf-8-sig'))
    devices={str(row[0]):str(row[1]) for n,row in small['Link Assigns - Summary'] if n>=4}
    expected={};grid_arrays={}
    with np.load(CACHE/'Base_Reactions.npz',allow_pickle=False) as z:
        for gid,g in manifest['tables']['Base Reactions']['groups'].items():
            key=(g['keys']['Output Case'],g['keys']['Case Type'],'Step By Step')
            t=z[gid][:,0].copy();grid_arrays[key]=t;expected[key]={int(round(float(v)*100)) for v in t}
    stats={};selected=[];saved={};head_examples={};sheet_counts={};units={};unknown=[]
    def newstat():return {'I':set(),'J':set(),'U':set(),'nI':0,'nJ':0,'nU':0,'dupI':0,'dupJ':0,'dupU':0,'invalid':0,'rowsI':[],'rowsJ':[],'rowsU':[]}
    with Workbook(RAW) as wb:
        for sheet,kind in [('Element Forces - Links','P'),('Element Deformations - Links','U')]:
            count=0
            for n,row in wb.rows(sheet):
                if n==2:cols={v:i for i,v in enumerate(row)};continue
                if n==3:
                    units[kind]=row[cols['P' if kind=='P' else 'U1']]
                    assert units[kind]==('kN' if kind=='P' else 'mm');continue
                if n<4:continue
                count+=1
                if count%100000==0:
                    print(json.dumps({'sheet':sheet,'rows':count,'elapsed_s':time.perf_counter()-started}),flush=True)
                    assert time.perf_counter()-started<480,'Target audit time budget exceeded'
                cell=lambda key:row[cols[key]]
                ident=str(cell('Unique Name'));element=str(cell('Link Element'))
                link=ident if ident in devices else element
                if link not in devices:unknown.append([n,ident,element]);continue
                case=(str(cell('Output Case')),str(cell('Case Type')),str(cell('Step Type')))
                gkey=(link,)+case;g=stats.setdefault(gkey,newstat())
                if kind=='P' and link not in selected and len(selected)<2:selected.append(link)
                loc=('I' if cell('Location')=='I-End' else 'J' if cell('Location')=='J-End' else '?') if kind=='P' else 'U'
                if loc=='?':unknown.append([n,'location',cell('Location')]);continue
                t=float(cell('Step Number'));value=cell('P' if kind=='P' else 'U1')
                g['n'+loc]+=1
                if len(g['rows'+loc])==0:g['rows'+loc]=[n,n]
                else:g['rows'+loc][1]=n
                if value is None or not math.isfinite(float(value)) or abs(round(t*100)-t*100)>1e-6:
                    g['invalid']+=1;continue
                tick=int(round(t*100));g['dup'+loc]+=int(tick in g[loc]);g[loc].add(tick)
                if sheet not in head_examples:head_examples[sheet]={'row':n,'values':row}
                if link in selected:
                    saved.setdefault((gkey,loc),{})[tick]=(float(value),n,t,ident,element)
            sheet_counts[sheet]={'data_rows':count,'last_source_row':n}
            print(json.dumps({'sheet_finished':sheet,'data_rows':count,'elapsed_s':time.perf_counter()-started}),flush=True)
    coverage=[];full_keys=[]
    for link,story in devices.items():
        for case,e in expected.items():
            key=(link,)+case;g=stats.get(key,newstat());common=g['I']&g['J']&g['U']
            complete=all(g[a]==e and g['dup'+a]==0 for a in ['I','J','U']) and g['invalid']==0
            if complete:full_keys.append(key)
            rec={'Link':link,'Story':story,'Case':case[0],'CaseType':case[1],'StepType':case[2],
                 'expected_n':len(e),'expected_t0_s':min(e)/100,'expected_t1_s':max(e)/100,
                 'P_I_n':len(g['I']),'P_J_n':len(g['J']),'U1_n':len(g['U']),'common_n':len(common),
                 'missing_I':len(e-g['I']),'missing_J':len(e-g['J']),'missing_U':len(e-g['U']),
                 'extra_I':len(g['I']-e),'extra_J':len(g['J']-e),'extra_U':len(g['U']-e),
                 'dup_I':g['dupI'],'dup_J':g['dupJ'],'dup_U':g['dupU'],'invalid_rows':g['invalid'],
                 'complete_export_grid':complete,'P_I_source_rows':str(g['rowsI']),'P_J_source_rows':str(g['rowsJ']),'U_source_rows':str(g['rowsU'])}
            coverage.append(rec)
    writecsv('link_case_coverage_r001.csv',coverage)
    complete_devices=[link for link in devices if all((link,)+case in full_keys for case in expected)]
    assert len(selected)==2 and all(link in complete_devices for link in selected)
    paired=[];samples=[];checks=[]
    firstcase=next(iter(expected))
    for link in selected:
        key=(link,)+firstcase;ticks=sorted(expected[firstcase]);rows=[]
        for tick in ticks:
            pi,pj,u=[saved[(key,loc)][tick] for loc in ['I','J','U']]
            assert abs(pi[2]-u[2])<1e-10 and abs(pj[2]-u[2])<1e-10
            rows.append({'Link':link,'Story':devices[link],'Case':firstcase[0],'t_s':u[2],
                'P_I_kN':pi[0],'P_J_kN':pj[0],'U1_mm':u[0],'U1_m':u[0]/1000,
                'force_I_row':pi[1],'force_J_row':pj[1],'deformation_row':u[1],
                'P_I_cell':'I'+str(pi[1]),'P_J_cell':'I'+str(pj[1]),'U1_cell':'H'+str(u[1])})
        name=f'paired_{link}_{firstcase[0]}_r001.csv';writecsv(name,rows);paired.append(name)
        p=np.array([r['P_I_kN'] for r in rows]);pj=np.array([r['P_J_kN'] for r in rows]);u=np.array([r['U1_m'] for r in rows])
        index=sorted({0,1,2,len(rows)//4,len(rows)//2,3*len(rows)//4,len(rows)-2,len(rows)-1,int(np.argmax(abs(p))),int(np.argmax(abs(u)))})
        samples += [rows[i] for i in index]
        checks.append({'Link':link,'Case':firstcase[0],'n':len(rows),'P_I_J_max_abs_difference_kN':float(max(abs(p-pj))),
            'P_I_J_max_abs_sum_kN':float(max(abs(p+pj))),'P_U_same_time':True,'mm_to_m_divisor':1000,
            'P_I_min_kN':float(min(p)),'P_I_max_kN':float(max(p)),'U1_min_m':float(min(u)),'U1_max_m':float(max(u)),
            'raw_signed_trapezoid_PdU_kNm':float(np.sum((p[1:]+p[:-1])/2*np.diff(u))),
            'work_interpretation':'Raw native signed total end-to-end work only; conjugate sign and spring-storage subtraction not yet established; not viscous dissipation.'})
    writecsv('paired_source_samples_r001.csv',samples)
    after=RAW.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    out={'evidence_id':'M-EXP-R001','review_status':'candidate','finished_utc':datetime.now(timezone.utc).isoformat(),
      'elapsed_seconds':time.perf_counter()-started,'source':str(RAW),'source_sha256':source_sha,'source_stable_size_mtime':True,
      'core_manifest_sha256':sha(CACHE/'manifest.json'),'base_cache_sha256':sha(CACHE/'Base_Reactions.npz'),
      'metadata_sha256':sha(small_path),'reader_sha256':sha(SKILL/'stream_csi.py'),'code_sha256':sha(__file__),
      'expected_devices':len(devices),'cases':[list(c) for c in expected],'expected_device_cases':len(coverage),
      'complete_P_I_J_U_device_cases':len(full_keys),'complete_all_case_devices':complete_devices,
      'paired_partial_device_cases':sum(0<r['common_n']<r['expected_n'] for r in coverage),
      'no_common_device_cases':sum(r['common_n']==0 for r in coverage),
      'selected_devices':selected,'selected_case':list(firstcase),'selected_checks':checks,
      'sheet_counts':sheet_counts,'units':units,'first_data_examples':head_examples,'unknown_keys_or_locations':unknown[:20],
      'no_missing_zero_filling':True,'no_full_88_energy_claim':True,'parameter_truth':'C,alpha,K not exported; no candidate screenshot values used',
      'limits':'Complete refers only to six cached exported windows, not unlimited free tail or full 88-device work. I/J must not be added as two dissipations. Sign/conjugacy and Maxwell parameters remain to be independently checked.',
      'outputs':[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f)} for f in [HERE/'link_case_coverage_r001.csv',HERE/'paired_source_samples_r001.csv']+[HERE/n for n in paired]]}
    sentinel.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    record={'command_argv':[sys.executable,str(Path(__file__).resolve())],'exit_code':0,'finished_utc':out['finished_utc'],
            'elapsed_seconds':out['elapsed_seconds'],'python':sys.version,'numpy':np.__version__,'code_sha256':sha(__file__),
            'audit_sha256':sha(sentinel),'target_sheets_only':True,'no_ETABS_no_core_reextraction':True}
    (HERE/'run_record_r001.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['elapsed_seconds','expected_devices','cases','complete_P_I_J_U_device_cases','complete_all_case_devices','paired_partial_device_cases','no_common_device_cases','selected_checks']},ensure_ascii=False,indent=2))
if __name__=='__main__':sys.stdout.reconfigure(encoding='utf-8');main()
