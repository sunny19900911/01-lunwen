"""Static manuscript fidelity/identity review only; no scientific recalculation."""
import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def tables(text):
    result=[];current=[]
    for line in text.splitlines()+['']:
        if line.startswith('|'):current.append([s.strip() for s in line.strip('|').split('|')])
        elif current:result.append(current);current=[]
    return result


def rounding_matches(text,value):
    quantum=float(Decimal(1).scaleb(Decimal(text).as_tuple().exponent))
    assert abs(float(text)-value)<=quantum*.50001+abs(value)*2e-15,(text,value,quantum)


def run(root,out):
    paper=root/'papers/damping-output-boundaries';writer=paper/'research/roles/writing/maxwell-session004'
    review=paper/'research/roles/verification/maxwell-session004';experiment=paper/'research/roles/experiments/maxwell-session004'
    draft=paper/'manuscript/maxwell-engineering-draft-v003.md'
    assert sha(draft)=='b38d81a6f8b3caf469fe30c6fb8f05bace2f78b15cd0a553178ca2e5788b96b6'
    expected={'v001':'8f3d3fd831beae77a1e5de7fa66b5eff5e54613590da49c45bee6434f3035bde',
              'v002':'921d68bb57e4c9c4a6a6960e2dc31a93727375901fa4118d5b9cd26fb5c71a12',
              'v003':'f16c2264b49a316fd3402a8f401bf767b318b27458b04d1abc5ba1ce4a00b367'}
    files=[];freeze_counts={}
    for version,checksum in expected.items():
        f=writer/f'frozen-draft-{version}.json';assert sha(f)==checksum;files.append(f)
        frozen=json.loads(f.read_text(encoding='utf-8'));freeze_counts[version]=len(frozen['files'])
        for item in frozen['files']:
            p=Path(item['path']);assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes'];files.append(p)
    evidence=json.loads((writer/'draft-v003-evidence-map.json').read_text(encoding='utf-8'))
    for item in evidence['sources']+[evidence['predecessor'],evidence['predecessor_freeze'],evidence['snapshot']]:
        p=Path(item['path']);assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes'];files.append(p)
    frozen=json.loads((writer/'frozen-draft-v003.json').read_text(encoding='utf-8'))
    accepted=frozen['accepted_R007'];assert sha(Path(accepted['path']))==accepted['sha256']=='c1cf505cf1c9fe7f8c40a2e5b658a91b05471f16dfb5d37901f9bb5596504494'
    mutable=[];snapshots=[]
    v1map=json.loads((writer/'draft-v001-evidence-map.json').read_text(encoding='utf-8'))
    for name,item in v1map['sources'].items():
        actual=sha(Path(item['path']));is_mutable=name in {'plan','claims','handoff'}
        if not is_mutable:assert actual==item['sha256'],name
        mutable.append({'name':name,'mutable_session_document':is_mutable,'original_read_sha256':item['sha256'],
                        'current_sha256':actual,'current_matches_original_read':actual==item['sha256']})
    v1snapshot=json.loads((writer/'draft-v001-session-snapshot.json').read_text(encoding='utf-8'))
    for name,item in v1snapshot['sources'].items():
        body=item['text_utf8'].encode('utf-8');assert hashlib.sha256(body).hexdigest()==item['source_identity']['sha256']
        assert len(body)==item['source_identity']['bytes'];snapshots.append({'version':'v001','name':name,'raw_text_hash_valid':True})
    v2snapshot=json.loads((writer/'draft-v002-session-snapshot.json').read_text(encoding='utf-8'))
    for item in v2snapshot['sources']:
        raw=item['content'].encode('utf-8');crlf=item['content'].replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
        mode='raw' if hashlib.sha256(raw).hexdigest()==item['sha256'] else 'LF text reconstructs original CRLF bytes'
        candidate=raw if mode=='raw' else crlf
        if hashlib.sha256(candidate).hexdigest()!=item['sha256']:
            # Historical claims appended LF lines to a CRLF document. JSON text
            # was newline-normalized; verify the original byte identity too.
            chunks=item['content'].split('\n');count=len(chunks)-1
            crlf_count=item['bytes']-len(raw);assert 0<=crlf_count<=count
            candidate=(''.join(chunks[i]+('\r\n' if i<crlf_count else '\n') for i in range(count))+chunks[-1]).encode('utf-8')
            mode=f'LF text reconstructs original mixed endings: first {crlf_count} CRLF, remaining {count-crlf_count} LF'
        assert hashlib.sha256(candidate).hexdigest()==item['sha256'] and len(candidate)==item['bytes']
        snapshots.append({'version':'v002','name':Path(item['path']).name,'content_identity_mode':mode,
                          'current_source_matches_snapshot':sha(Path(item['path']))==item['sha256']})
    text=draft.read_text(encoding='utf-8');v2=(paper/'manuscript/maxwell-engineering-draft-v002.md').read_text(encoding='utf-8')
    tab=tables(text);old=tables(v2);assert len(tab)==5 and tab[:4]==old
    energy=readcsv(review/'R001-review-data/energy_review_summary.csv');bycase={x['case']:x for x in energy}
    cells=0
    for index,table in enumerate([tab[1],tab[2]]):
        assert len(table[2:])==6
        for row in table[2:]:
            x=bycase[row[0]]
            if index==0:
                expected_row=[x['case'],str(int(x['n'])),f"{float(x['T_s']):.1f}",f"{float(x['Eglobal_delta_kNm']):.6f}",
                    f"{float(x['Elink_delta_kNm']):.6f}",f"{float(x['Elink_over_Eglobal']):.9f}",f"{float(x['conditional_added_damping_percent']):.6f}"]
            else:
                expected_row=[x['case'],f"{float(x['max_abs_balance_over_peak_input']):.6e}",f"{float(x['max_balance_minus_EnergyError_kNm']):.6e}",
                    str(int(x['negative_Link_increment_count'])),f"{float(x['end_kinetic_plus_potential_kNm']):.6f}"]
            assert row==expected_row;cells+=len(row)-1
    assert sum(int(x['n']) for x in energy)==16296 and sum(int(x['negative_Link_increment_count']) for x in energy)==206
    fit=json.loads((experiment/'R002-integral-regression/fit_summary_r002.json').read_text(encoding='utf-8'))['best_grid_row']
    independent=json.loads((review/'R004-integral-review/review_record.json').read_text(encoding='utf-8'))['best_grid_row']
    fields=['n','y_RMS_m','RMSE_m','MAE_m','max_abs_residual_m','RMSE_over_y_RMS']
    assert len(tab[3][2:])==6
    for row,field in zip(tab[3][2:],fields):
        for label,value in [('K2',row[1]),('K5_transfer',row[2])]:
            expected_value=2501 if field=='n' else fit[label+'_'+field]*(100 if field=='RMSE_over_y_RMS' else 1)
            rounding_matches(value,expected_value)
            independent_value=2501 if field=='n' else independent[label+'_'+field]*(100 if field=='RMSE_over_y_RMS' else 1)
            rounding_matches(value,independent_value);cells+=1
    transfer=json.loads((review/'R007-transfer-review/review_summary.json').read_text(encoding='utf-8'))
    metricrefs={(x['Link'],x['Case']):x for x in readcsv(experiment/'R003-cross-case-transfer/transfer_metrics_r003.csv')}
    assert transfer['all_point_residuals_checked']==11294 and transfer['worst_points_checked']==20
    assert len(tab[4][2:])==4
    selected=[]
    for row in tab[4][2:]:
        link,case=row[0].split('/');x=next(g['metrics'] for g in transfer['groups'] if (g['metrics']['Link'],g['metrics']['Case'])==(link,case))
        fields=['n','RMSE_m','MAE_m','max_abs_residual_m','mean_residual_m','RMSE_over_delta_d_RMS']
        for displayed,field in zip(row[1:],fields):
            value=x[field]*(100 if field=='RMSE_over_delta_d_RMS' else 1);rounding_matches(displayed,value)
            source_value=float(metricrefs[(link,case)][field])*(100 if field=='RMSE_over_delta_d_RMS' else 1)
            assert math.isclose(value,source_value,abs_tol=2e-18,rel_tol=2e-12),(link,case,field)
            cells+=1
        selected.append({'Link':link,'Case':case,'mean_residual_m':x['mean_residual_m'],'relative_RMSE_percent':100*x['RMSE_over_delta_d_RMS']})
    assert sum(int(row[1]) for row in tab[4][2:])==11294
    assert all(x['mean_residual_m']<0 for x in selected if x['Link']=='K5')
    assert transfer['fixed_parameters']=={'alpha':fit['alpha'],'a':fit['a_m_per_kN'],'b':fit['b_m_per_s_kN_power_inverse_alpha']}
    protocol=json.loads((experiment/'R003-cross-case-transfer/protocol.json').read_text(encoding='utf-8'))
    assert float(protocol['fixed_parameters']['alpha'])==fit['alpha']
    assert float(protocol['fixed_parameters']['a_m_per_kN'])==fit['a_m_per_kN']
    assert float(protocol['fixed_parameters']['b_m_per_s_kN_power_inverse_alpha'])==fit['b_m_per_s_kN_power_inverse_alpha']
    for token,value in [('499848.982420',fit['k_kN_per_m']),('476.930816',fit['c_kN_s_per_m_power_alpha'])]:
        assert token in text;rounding_matches(token,value)
    for key,precision in [('K2_raw_condition',6),('K5_design_raw_condition',6),('K2_scaled_condition',9),('K5_design_scaled_condition',9)]:
        assert format(fit[key],f'.{precision}f') in text
    response=json.loads((review/'R002-review-data/response_review.json').read_text(encoding='utf-8'))
    for table in tab[0][2:]:
        r=response['table_coverage'][table[0]];assert f"{r['groups']}组" in table[1] and format(r['data_rows'],',') in table[1]
    assert '161,802' in text and response['table_coverage']['Story Drifts']['missing_times_total']==161802
    formulas=re.findall(r'\$\$(.*?)\$\$',text,re.S);oldformulas=re.findall(r'\$\$(.*?)\$\$',v2,re.S)
    assert formulas==oldformulas and len(formulas)==6 and re.findall(r'\\tag\{([^}]+)\}',text)==list('123456')
    references=re.findall(r'^\[([1-5])\].*$',text,re.M);assert references==list('12345')
    assert re.findall(r'^\[[1-5]\].*$',text,re.M)==re.findall(r'^\[[1-5]\].*$',v2,re.M)
    figures=[];image_links=re.findall(r'!\[[^]]*\]\(([^)]+)\)',text);assert len(image_links)==2
    for link in image_links:
        path=(draft.parent/link).resolve();relative=path.relative_to(root).as_posix()
        entry=next(x for x in evidence['figure_portability'] if x['link']==link)
        assert relative==entry['repo_relative'] and sha(path)==entry['identity']['sha256']
        git=subprocess.run(['git','ls-files','--error-unmatch','--',relative],cwd=root,text=True,capture_output=True)
        assert git.returncode==0,(relative,git.stderr)
        assert path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
        figures.append({'relative_link':link,'repo_relative':relative,'tracked':True,'sha256':sha(path),'bytes':path.stat().st_size})
    links=[]
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('http://','https://')):continue
        path=(draft.parent/target).resolve();assert path.exists();links.append(str(path))
    assert not re.search(r'(?<![A-Za-z])[A-Za-z]:[\\/]',text) and not re.search(r'[a-f0-9]{64}',text)
    assert all(x==x.rstrip() for x in text.splitlines()) and b'\r' not in draft.read_bytes() and not draft.read_bytes().startswith(b'\xef\xbb\xbf')
    assert all(token in text for token in ['K2训练','同RH4X','不构成从地震动出发的前向响应预测','独立地震外验','没有去均值或末点校准','未预设工程验收阈值'])
    assert not any(token in text for token in ['R008','R009','Dforce_trap','326个窗口','楼层Top3','峰力条件界'])
    assert not any('R004-energy-ledger' in x['path'] or 'R005-floor-results' in x['path'] for x in evidence['sources'])
    extras=[review/'R004-integral-review/review_record.json',review/'R002-review-data/response_review.json']
    unique={str(f.resolve()):f.resolve() for f in files+extras};inputs=[{'path':key,'bytes':f.stat().st_size,'sha256':sha(f)} for key,f in unique.items()]
    record={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,'script_sha256':sha(Path(__file__)),
        'scope':'Static integration/transcription fidelity only; no scientific experiment, original Excel, external search or remote rendering test.',
        'frozen_author_file_counts':freeze_counts,'prior_four_tables_identical':True,'energy_numeric_cells':60,'training_numeric_cells':12,
        'transfer_numeric_cells':24,'numeric_cells_checked':cells,'six_formula_blocks_identical_to_v002':True,
        'five_references_identical_to_v002':True,'coverage_table_rows_checked':4,'transfer_summary':selected,'figures':figures,
        'remote_GitHub_rendering_tested':False,'local_links':links,'original_map_source_states':mutable,'snapshot_content_checks':snapshots,
        'v003_immutable_map_sources_checked':len(evidence['sources']),'later_R008_R009_results_excluded':True,'inputs':inputs,
        'limits':['Stage manuscript reviewable only, not submission/novelty/physical parameters/fair reduction certification.',
                  'Frozen sources may retain candidate labels; acceptance traced to reviewed report and master snapshot.',
                  'Current master ledgers differ from historical frozen read versions; historical snapshots preserved.',
                  'Tracked local PNG paths and hashes verified; GitHub remote rendering not visited or certified.']}
    assert cells==96
    out.mkdir(parents=True,exist_ok=True);target=out/'review_summary.json';assert not target.exists()
    target.write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'checks_passed':True,'recorded_at':record['recorded_at'],'numeric_cells':cells,
        'source_files':len(inputs),'map_sources':len(evidence['sources']),'frozen_author_file_counts':freeze_counts,
        'mutable_current_mismatches':[x['name'] for x in mutable if x['mutable_session_document'] and not x['current_matches_original_read']],
        'figures':figures},ensure_ascii=True,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();run(args.root.resolve(),args.out)
