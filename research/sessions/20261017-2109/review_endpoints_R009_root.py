"""Independent endpoint checks on frozen local evidence; no Excel or fitting."""
import csv, hashlib, json, datetime, math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SESSION = Path(__file__).resolve().parent
EXP = ROOT / 'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    out = SESSION / 'R006-endpoints-root-review.json'
    if out.exists():
        raise FileExistsError(out)
    source = EXP/'R006-device-distribution/local_paired_histories_r006.npz'
    before = sha(source)
    assert before == '65be34f8125e5e7f2aee90ebe5a4b2612cfe717d84abf0886789a1bc75709340'
    report = EXP/'R009-endpoint-domain/report.md'
    assert sha(report) == '8874ce9483acc88814c0b36378a80efe22cd9783df7c9b2ef3d8c26641242a31'
    table = EXP/'R009-endpoint-domain/endpoint_summary_192_r009.csv'
    assert sha(table) == '45fedbb8bfd95246d98ea981a434e2702e57bf6f6672b6899eed4dd14d694d39'
    with table.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    manifest=json.loads((EXP/'R006-device-distribution/local_history_manifest_r006.json').read_text('utf-8'))
    meta={x['key']:x for x in manifest['arrays']}
    counts=dict(F0_zero=0,FT_zero=0,both_zero=0,net_delta_zero=0)
    checked=0
    with np.load(source,allow_pickle=False) as arrays:
        assert len(rows)==len(arrays.files)==192
        for row in rows:
            a=arrays[row['local_array_key']]
            cols=meta[row['local_array_key']]['columns']
            t,fi,fj,mm,m,ir,jr,dr = [a[:,cols.index(name)].tolist() for name in ['t_s','P_I_kN','P_J_kN','U1_mm','U1_m','force_I_row','force_J_row','deformation_row']]
            force=max(abs(x) for x in fi)
            scale=max(abs(x-m[0]) for x in m)
            net=m[-1]-m[0]
            expected={'F0_I_kN':fi[0],'F0_J_kN':fj[0],'FT_I_kN':fi[-1],'FT_J_kN':fj[-1],'Pmax_kN':force,'d0_native_mm':mm[0],'dT_native_mm':mm[-1],'d0_m':m[0],'dT_m':m[-1],'net_delta_native_mm':mm[-1]-mm[0],'net_delta_m':net,'record_max_abs_delta_from_d0_mm':max(abs(x-mm[0]) for x in mm),'record_max_abs_delta_from_d0_m':scale,'FT_over_Pmax':fi[-1]/force,'abs_FT_over_Pmax':abs(fi[-1])/force,'net_delta_over_record_scale':net/scale,'abs_net_delta_over_record_scale':abs(net)/scale,'t0_s':t[0],'tT_s':t[-1]}
            for key,value in expected.items():
                assert float(row[key])==value,(row['Link'],row['Case'],key)
                checked+=1
            for key,number in [('F0_I_cell',ir[0]),('F0_J_cell',jr[0]),('FT_I_cell',ir[-1]),('FT_J_cell',jr[-1]),('d0_U1_cell',dr[0]),('dT_U1_cell',dr[-1])]:
                assert row[key]==('H' if 'U1' in key else 'I')+str(int(number)),key
            flags={'F0_exact_zero':fi[0]==0,'FT_exact_zero':fi[-1]==0,'both_force_endpoints_exact_zero':fi[0]==0 and fi[-1]==0,'net_delta_exact_zero':net==0}
            for key,value in flags.items():
                assert (row[key].lower()=='true')==value,key
            counts['F0_zero']+=fi[0]==0
            counts['FT_zero']+=fi[-1]==0
            counts['both_zero']+=fi[0]==0 and fi[-1]==0
            counts['net_delta_zero']+=net==0
    assert counts==dict(F0_zero=192,FT_zero=0,both_zero=0,net_delta_zero=0)
    assert sha(source)==before
    result={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'passed':True,'counts':counts,'numeric_fields_checked':checked,'source_locations_checked':192*6,'source_sha256':before,'report_sha256':sha(report),'table_sha256':sha(table),'scope':'Independent scalar endpoint/scale/ratio and location audit on frozen local arrays. No source Excel or fit; exported exact nonzero is not an engineering significance threshold or a refutation of conditional theorem.'}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(result))

if __name__=='__main__':
    main()
