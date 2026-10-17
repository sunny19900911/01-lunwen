"""Normalize exactly 25 frozen JSON receipts; no Git, network, model or filesystem mtime."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter
import csv, hashlib, json, re

H=Path(__file__).resolve().parent
ROOT=H.parents[6]
S=ROOT/'research/sessions/20261017-2109'
START=datetime.fromisoformat('2026-10-18T06:26:03+08:00')
def fp(path):
    data=Path(path).read_bytes()
    assert len(data)<1000000
    return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def write_json(name,value):
    assert not (H/name).exists()
    (H/name).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha40(value):return isinstance(value,str) and bool(re.fullmatch('[0-9a-f]{40}',value))
def compact(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def minutes_seconds(value):
    minutes=int(value//60);return f'{minutes}分{value-minutes*60:.6f}秒'

def main():
    rows,records,raw_records=[],[],[]
    success_forms,time_fields,attempt_fields,exit_fields,remote_fields=Counter(),Counter(),Counter(),Counter(),Counter()
    verification_fields=['status','verified','push_and_remote_verified','pushed_and_verified']
    for i in range(1,26):
        name=f'R{i:03d}';path=S/(name+'-push.json');data=path.read_bytes()
        assert len(data)<1000000
        records.append({'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        obj=json.loads(data.decode('utf-8-sig'));raw_records.append(obj)
        if obj.get('at'):
            tkey='at';label=obj['at']
        elif obj.get('recorded_at'):
            tkey='recorded_at';label=obj['recorded_at']
        else:
            tkey='unknown';label='unknown'
        time_fields[tkey]+=1
        try:
            dt=datetime.fromisoformat(label)
            if dt.tzinfo is None:dt=None
        except (ValueError,TypeError):dt=None
        if 'push_attempts' in obj:akey='push_attempts'
        elif 'attempts' in obj:akey='attempts'
        else:akey='unknown'
        attempt_fields[akey]+=1
        attempts=obj.get(akey,[]) if akey!='unknown' else []
        exits=[];ec_fields=[]
        for attempt in attempts:
            ekey='exit_code' if 'exit_code' in attempt else ('returncode' if 'returncode' in attempt else 'unknown')
            ec_fields.append(ekey);exit_fields[ekey]+=1;exits.append(attempt.get(ekey,'unknown'))
        present={k:obj[k] for k in verification_fields if k in obj}
        success_key=next((k for k in verification_fields if k in obj),'unknown')
        success_forms[success_key]+=1
        v=present.get(success_key)
        if success_key=='status':normalized_v=True if v=='pushed-and-verified' else 'unknown'
        elif isinstance(v,bool):normalized_v=v
        else:normalized_v='unknown'
        rkey=next((k for k in ['remote_commit','remote_main'] if sha40(obj.get(k))),None)
        query=obj.get('remote_query',{})
        query_match=re.match(r'([0-9a-f]{40})(?:\s|$)',query.get('stdout',''))
        if rkey:rsha=obj[rkey]
        elif query_match:rkey='remote_query.stdout';rsha=query_match.group(1)
        else:rkey='unknown';rsha='unknown'
        remote_fields[rkey]+=1
        commit=obj.get('commit','unknown');assert sha40(commit)
        eq=rsha==commit if rsha!='unknown' else 'unknown'
        if query_match and rsha!='unknown':assert query_match.group(1)==rsha
        query_exit=query.get('returncode',query.get('exit_code','unknown'))
        attempt_remote_exits=[a['remote_check_returncode'] for a in attempts if 'remote_check_returncode' in a]
        all_push_zero=bool(exits) and all(x==0 for x in exits)
        receipt_success=normalized_v is True and eq is True and all_push_zero
        receipt_failed=normalized_v is False and bool(exits) and all(isinstance(x,int) and x!=0 for x in exits)
        outcome='pushed_and_verified_as_recorded' if receipt_success else ('failed_pending_as_recorded' if receipt_failed else 'unknown_or_mixed')
        tls_failure=any('SSL/TLS connection failed' in a.get('stderr','') for a in attempts)
        rows.append({'checkpoint':name,'receipt_completion_or_recorded_at':label,'time_source_field':tkey,'time_parse_status':'timezone_aware' if dt else 'unknown',
                     'commit':commit,'remote_SHA_as_recorded':rsha,'remote_SHA_source_field':rkey,'remote_SHA_equals_commit':eq,
                     'attempts_source_field':akey,'push_attempt_count':len(attempts),'attempt_exit_fields':compact(ec_fields),'attempt_exit_codes':compact(exits),
                     'verification_fields_as_recorded':compact(present),'verification_form':success_key,'verification_normalized':normalized_v,
                     'remote_query_exit_as_recorded':query_exit,'attempt_remote_check_exit_codes':compact(attempt_remote_exits),
                     'receipt_outcome':outcome,'TLS_failure_recorded':tls_failure,'includes_pending_parent_as_recorded':obj.get('includes_pending_parent',''),
                     'interval_from_previous_receipt_seconds':'unknown','interval_from_previous_successful_receipt_seconds':'not_applicable',
                     'source_path':str(path),'source_SHA256':records[-1]['sha256'],'new_remote_verification_performed':False,'_dt':dt,'_success':receipt_success})
    intervals=[];success_intervals=[]
    for i,row in enumerate(rows):
        if i and row['_dt'] is not None and rows[i-1]['_dt'] is not None:
            gap=(row['_dt']-rows[i-1]['_dt']).total_seconds()
            assert gap>=0
            row['interval_from_previous_receipt_seconds']=f'{gap:.6f}'
            intervals.append({'from':rows[i-1]['checkpoint'],'to':row['checkpoint'],'seconds':gap})
    previous=None
    for row in rows:
        if row['_success']:
            if previous is not None and row['_dt'] is not None and previous['_dt'] is not None:
                gap=(row['_dt']-previous['_dt']).total_seconds()
                row['interval_from_previous_successful_receipt_seconds']=f'{gap:.6f}'
                success_intervals.append({'from':previous['checkpoint'],'to':row['checkpoint'],'seconds':gap})
            else:row['interval_from_previous_successful_receipt_seconds']='unknown_no_previous_success'
            previous=row
    r7,r8=raw_records[6],raw_records[7]
    assert rows[2]['attempts_source_field']=='push_attempts' and rows[2]['push_attempt_count']==1
    assert rows[6]['receipt_outcome']=='failed_pending_as_recorded' and json.loads(rows[6]['attempt_exit_codes'])==[128,128]
    assert r7['verified'] is False and rows[6]['TLS_failure_recorded']
    assert r8['includes_pending_parent']==r7['commit'] and rows[7]['_success']
    assert r7['remote_main']==raw_records[5]['commit'] and r7['remote_main']!=r7['commit']
    assert 'normal push' in r8['scope'] and 'no force' in r8['scope']
    assert len(rows)==25
    with (H/'normalized-25-receipts.csv').open('x',encoding='utf-8-sig',newline='') as f:
        out=[{k:v for k,v in row.items() if not k.startswith('_')} for row in rows]
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    min_all=min(intervals,key=lambda x:x['seconds']);max_all=max(intervals,key=lambda x:x['seconds'])
    min_success=min(success_intervals,key=lambda x:x['seconds']);max_success=max(success_intervals,key=lambda x:x['seconds'])
    counts=Counter(row['receipt_outcome'] for row in rows)
    stats={'time_field_forms':dict(time_fields),'success_verification_field_forms':dict(success_forms),'success_verification_distinct_forms':len(success_forms),
           'attempt_container_forms':dict(attempt_fields),'attempt_exit_field_forms_per_attempt':dict(exit_fields),'remote_SHA_field_forms':dict(remote_fields),
           'remote_query_objects':sum('remote_query' in x for x in raw_records),'attempt_remote_check_fields':sum('remote_check_returncode' in a for o in raw_records for a in o.get('attempts',o.get('push_attempts',[]))),
           'outcomes':dict(counts),'total_push_attempts':sum(r['push_attempt_count'] for r in rows),'zero_exit_attempts':sum(x==0 for r in rows for x in json.loads(r['attempt_exit_codes'])),
           'failed_exit_attempts':sum(isinstance(x,int) and x!=0 for r in rows for x in json.loads(r['attempt_exit_codes'])),
           'missing_or_unparseable_times':[r['checkpoint'] for r in rows if r['_dt'] is None],
           'all_receipt_adjacent_intervals_count':len(intervals),'all_receipt_interval_min':min_all,'all_receipt_interval_max':max_all,
           'successful_receipt_intervals_count':len(success_intervals),'successful_receipt_interval_min':min_success,'successful_receipt_interval_max':max_success,
           'all_adjacent_receipt_intervals_greater_than_15_minutes':all(x['seconds']>900 for x in intervals),
           'can_claim_strict_every15minute_sync':False,
           'first_receipt_time':rows[0]['receipt_completion_or_recorded_at'],'last_receipt_time':rows[-1]['receipt_completion_or_recorded_at'],
           'R007_original_failure_preserved':True,'R008_records_normal_push_including_R007_pending_parent':True,
           'Git_or_remote_ancestry_independently_checked':False,'mtime_used':False}
    write_json('audit-stats.json',stats)
    lines=['# R028：会话推送收据小审计','',
           '**不能声称全程严格每15分钟同步。** 仅审R001—R025共25份原小收据：24份记录本轮推送并验证成功，R007保留当次两次TLS失败及待推状态；合计26次尝试，24次exit=0、2次exit=128。本审没有执行Git、访问远端或重新认证任何提交，也不是科研证据或新实验。','',
           f"全部25份均有带时区时间：at {time_fields['at']}份，recorded_at {time_fields['recorded_at']}份；无缺时或无法解析项。时间按收据原字段归一，不取mtime，也不伪造每个网络命令的起止时刻。范围为{stats['first_receipt_time']}至{stats['last_receipt_time']}，不代表已经覆盖整个十小时窗口。",'',
           f"相邻全部收据共24个间隔：最短{min_all['from']}→{min_all['to']}，{minutes_seconds(min_all['seconds'])}；最长{max_all['from']}→{max_all['to']}，{minutes_seconds(max_all['seconds'])}。24个间隔全部超过15分钟。只看记录成功的24份，则有23个成功记录间隔：最短{min_success['from']}→{min_success['to']}，{minutes_seconds(min_success['seconds'])}；最长{max_success['from']}→{max_success['to']}，{minutes_seconds(max_success['seconds'])}，包括R007待推期间。因此最多说按这些实际收据记录了多次同步，不能写严格每15分钟完成。",'',
           f"成功/验证表达有{len(success_forms)}种字段形式："+'；'.join(f'{k}：{v}份' for k,v in success_forms.items())+'。其中verified字段含R007的false，不能把“字段存在”当成功。远端身份字段remote_commit为22份、remote_main为3份；3份另含remote_query，5份尝试内含remote_check_returncode。CSV同时保留原验证字段与归一结论，没有用status代替其他布尔字段。','',
           '推送尝试容器为attempts 24份、push_attempts 1份；后者是R003，已计1次而非0次。尝试退出字段exit_code有18个条目、returncode有8个条目，合计26次；这些字段按实际schema读取，不互相漏算。','',
           f"R007的commit为{r7['commit']}，两次exit=128且均记SSL/TLS握手失败，verified=false；其远端仍记前轮{r7['remote_main']}，与本轮commit不同。R008的commit/所记远端同为{r8['commit']}，本次exit=0、verified=true，并明确includes_pending_parent={r8['includes_pending_parent']}及normal push/no force。故可说“R008收据记载正常推进时包含R007待推父提交”；这是后续恢复记录，不能把原R007收据重标为成功。本审未独立查Git祖先或远端现态。",'',
           '25行CSV逐项保留完成/记录时间与来源键、commit、所记远端SHA及来源、尝试次数/退出码、原验证字段、远端查询支持、相邻间隔和R008父提交声明。缺失字段标unknown或not_applicable，既不当0也不根据文件时间补填。来源与结果SHA见sourcefreeze；本项只读取指定25份收据，未碰模型、原表、缓存、ODE、未知精度项或其他角色文件。冻结后只回主控，本项停笔；研究总硬截止07:09:45保持。']
    assert not (H/'report.md').exists();(H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    assert records==[fp(x['path']) for x in records]
    now=datetime.now(timezone(timedelta(hours=8)));elapsed=(now-START).total_seconds();assert elapsed<=360
    write_json('validation.json',{'task':'R028-session-receipt-audit','started_at':START.isoformat(),'frozen_at':now.isoformat(),'elapsed_seconds':elapsed,
                                  'input_receipts':25,'CSV_rows':25,'schema_normalization_passed':True,'all_source_SHA_unchanged':True,'R003_push_attempts_preserved':True,
                                  'R007_failed_status_not_overwritten':True,'R008_pending_parent_matches_R007_commit':True,'mtime_Git_network_models_or_original_data_used':False,'scientific_evidence_or_new_experiment':False})
    write_json('sourcefreeze.json',{'task':'R028-session-receipt-audit','frozen_at':now.isoformat(),'source_files':records,
                                   'outputs':[fp(p) for p in sorted(H.iterdir()) if p.is_file() and p.name!='sourcefreeze.json']})
    print(json.dumps({'stats':stats,'elapsed_seconds':elapsed,'report':fp(H/'report.md'),'CSV':fp(H/'normalized-25-receipts.csv'),'sourcefreeze':fp(H/'sourcefreeze.json')},ensure_ascii=True))

if __name__=='__main__':main()
