"""Independent limited audit: no solver or raw workbook, writes only this role."""
from pathlib import Path
import csv,json,datetime,hashlib
import numpy as np
O=Path(__file__).resolve().parent; S=O.parents[1]; R=S.parents[2]
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def readjson(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def normdiff(x,y):return float(np.linalg.norm(x-y)/np.linalg.norm(y))
errors=[];fields=0
def check(label,x,y,atol=1e-9):
    global fields
    fields+=1
    if not np.isclose(x,y,rtol=1e-11,atol=atol):errors.append({'label':label,'audit':float(x),'source':float(y)})

# Original element records, not the production force cache.
P=R/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution'
meta=readjson(P/'local_history_manifest_r006.json')
geom={(x['Story'],x['Link']):x for x in readcsv(R/'research/sessions/20261019-2045/roles/data/R001-link-geometry-88.csv')}
prod={x['Link']:x for x in readcsv(S/'roles/equivalent/equivalent-device-8.csv')}
whole={x['Link']:x for x in readcsv(S/'roles/equivalent/R002/whole-response-device-8.csv')}
results={};branch=[]
with np.load(P/'local_paired_histories_r006.npz',allow_pickle=False) as z:
    for fit in ['train','whole']:
        qq=[];qnative=[]
        for a in sorted([x for x in meta['arrays'] if x['Story']=='Story10' and x['Case']=='RH4Y'],key=lambda x:x['Link']):
            ar=z[a['key']]; col={k:i for i,k in enumerate(a['columns'])}
            t=ar[:,col['t_s']]; p=ar[:,col['P_I_kN']]; u=ar[:,col['U1_m']]
            vel=np.copysign(np.power(np.abs(p)/477.,10./3.),p)
            ix=t<=15 if fit=='train' else np.ones(len(t),dtype=bool)
            # Work is dashpot work, not integral(P du_total), which includes spring storage.
            ce=float(np.trapezoid(p[ix]*vel[ix],t[ix])/np.trapezoid(vel[ix]**2,t[ix]))
            check(f'{fit}-{a["Link"]}-ce',ce,float((prod if fit=='train' else whole)[a['Link']]['c_eq_kN_s_per_m' if fit=='train' else 'c_eq_whole_response_kN_s_per_m']),1e-6)
            force=np.zeros(len(t));force[0]=p[0]
            for j in range(1,len(t)):
                dt=t[j]-t[j-1];h=500000.*dt/ce
                force[j]=np.exp(-h)*force[j-1]+ce*(-np.expm1(-h))*(u[j]-u[j-1])/dt
            ny=float(geom[('Story10',a['Link'])]['ny']);qq.append(ny*force);qnative.append(ny*p)
            if fit=='train':check(a['Link']+'-holdRMS',normdiff(force[t>15],p[t>15]),float(prod[a['Link']]['holdout_relative_RMS']))
            else:check(a['Link']+'-wholeRMS',normdiff(force,p),float(whole[a['Link']]['whole_relative_RMS']))
        q=np.sum(qq,axis=0);qn=np.sum(qnative,axis=0)
        out={'QD_relative_RMS':normdiff(q[t>15],qn[t>15]) if fit=='train' else normdiff(q,qn),'anchors':[]}
        src=readjson(S/('roles/equivalent/equivalent-results.json' if fit=='train' else 'roles/equivalent/R002/whole-response-results.json'))
        check(fit+'-aggregateRMS',out['QD_relative_RMS'],src['local_prescribed_u_QD_holdout_relative_RMS' if fit=='train' else 'whole_QD_relative_RMS'])
        for tt,pr in zip([16.62,21.64],src['anchors']):
            j=int(np.where(np.isclose(t,tt,atol=1e-10))[0][0]);out['anchors'].append({'time':tt,'native':float(qn[j]),'linear':float(q[j])})
            check(fit+str(tt)+'native',qn[j],pr['native_QD_kN']);check(fit+str(tt)+'linear',q[j],pr['linear_prescribed_u_QD_kN' if fit=='train' else 'linear_whole_response_QD_kN'])
        results[fit]=out

# Independently aggregate all three published screening policies.
rows=readcsv(S/'roles/screen/screening-216.csv'); summaries=readcsv(S/'roles/screen/screening-summary-3.csv')
summ=[]
for sr in summaries:
    eps=float(sr['epsilon_percent']);rr=[x for x in rows if float(x['epsilon_percent'])==eps]
    r={'epsilon':eps,'n':len(rr),'candidates':sum(int(x['n_candidates']) for x in rr),'single_1pct':sum(float(x['missed_actual_peak_percent'])<=1+1e-10 for x in rr),'near_exact':sum(float(x['neighborhood_missed_peak_percent'])<=1e-8 for x in rr),'near_1pct':sum(float(x['neighborhood_missed_peak_percent'])<=1+1e-10 for x in rr),'max_near_miss':max(float(x['neighborhood_missed_peak_percent']) for x in rr)}
    for a,b in [('n','records'),('candidates','candidate_count_total'),('single_1pct','peak_error_le_1_percent'),('near_exact','neighborhood_exact_capture'),('near_1pct','neighborhood_error_le_1_percent'),('max_near_miss','maximum_neighborhood_peak_miss_percent')]:check(str(eps)+a,r[a],float(sr[b]))
    summ.append(r)

# Independently select baseline maxima using simple neighbor tests; no production selector import.
W=R.parent/'W5-重燃双塔连体';B=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';D=W/'research/maxwell-20261017/experiments/R001/core-cache'
tb=readjson(B/'manifest.json')['tables']['Story Forces'];td=readjson(D/'manifest.json')['tables']['Story Forces']
def getkey(tb,story):
    return next(k for k,v in tb['groups'].items() if v['keys']['Story']==f'Story{story}' and v['keys']['Location']=='Bottom' and v['keys']['Output Case']=='RH4Y')
casechecks=[]
with np.load(B/tb['cache'],allow_pickle=False) as zb,np.load(D/td['cache'],allow_pickle=False) as zd:
    for st in [10,12]:
        bc=tb.get('columns',tb.get('value_columns'));dc=td.get('columns',td.get('value_columns'));ba=zb[getkey(tb,st)];da=zd[getkey(td,st)]
        t=ba[:,bc.index('Time')]; b=ba[:,bc.index('VY')];d=da[:,dc.index('VY')];assert np.array_equal(t,da[:,dc.index('Time')])
        ab=np.abs(b);ad=np.abs(d);ib=int(np.argmax(ab));ip=int(np.argmax(ad));pb=ab[ib];pd=ad[ip]
        # These two records have no equal adjacent levels; simpler selector is independent and exact here.
        assert np.all(np.diff(ab)!=0)
        peaks=[i for i in range(len(t)) if (i==0 or ab[i]>=ab[i-1]) and (i==len(t)-1 or ab[i]>=ab[i+1])]
        for eps in [.02,.05,.10]:
            cand=[i for i in peaks if ab[i]>=(1-eps)*pb]
            mask=np.array([min(abs(tt-t[cand]))<=.1+1e-9 for tt in t])
            cp=max(ad[cand]);npk=max(ad[mask]);row=next(x for x in rows if x['Case']=='RH4Y' and int(x['Story'])==st and float(x['epsilon_percent'])==100*eps)
            vals={'n_candidates':len(cand),'t_B_s':t[ib],'t_D_s':t[ip],'P_B_kN':pb,'P_D_kN':pd,'baseline_gap_at_actual_peak_percent':100*(pb-ab[ip])/pb,'candidate_actual_peak_kN':cp,'missed_actual_peak_percent':100*(pd-cp)/pd,'neighborhood_actual_peak_kN':npk,'neighborhood_missed_peak_percent':100*(pd-npk)/pd,'D_SourceRow_at_own_peak':da[ip,dc.index('SourceRow')]}
            for key,value in vals.items():check(f'Story{st}-{eps}-{key}',value,float(row[key]))
            casechecks.append({'story':st,'epsilon':eps,'candidate_times':[float(t[i]) for i in cand],**{k:float(v) for k,v in vals.items()}})

four=[]
with np.load(R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz',allow_pickle=False) as z:
    for rr in readcsv(S/'root-four-records.csv'):
        st=int(rr['Story']);case=rr['Case'];a=z[f'Story{st}__{case}__{case[-1]}'];j=int(np.argmax(np.abs(a[:,1])))
        vals={'time_QT_peak_s':a[j,0],'QT_kN':a[j,1],'QD_J_resisting_kN':a[j,2],'QT_minus_QD_kN':a[j,1]-a[j,2],'QT_plus_QD_kN':a[j,1]+a[j,2],'SourceRow':a[j,5],'peak_abs_QT_kN':max(abs(a[:,1])),'peak_abs_QT_minus_QD_kN':max(abs(a[:,1]-a[:,2])),'peak_abs_QT_plus_QD_kN':max(abs(a[:,1]+a[:,2]))}
        for key,value in vals.items():check(f'{st}-{case}-{key}',value,float(rr[key]))
        four.append({'Story':st,'Case':case,**{k:float(v) for k,v in vals.items()}})
out={'at':datetime.datetime.now().astimezone().isoformat(),'fields':fields,'must':len(errors),'errors':errors,'equivalent':results,'screening_summary':summ,'independent_cached_groups':casechecks,'four_same_time_records':four,'scope':'prescribed-U local Maxwell only; screening on existing two response groups; four old force-cache groups; no structural solve','code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(O/'independent-new-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
