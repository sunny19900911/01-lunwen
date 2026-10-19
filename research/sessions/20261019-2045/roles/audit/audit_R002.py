from pathlib import Path
import csv, json, hashlib
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
DATA=HERE.parent/'data'
PAIR=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution'
CORE=ROOT.parent/'W5-重燃双塔连体/research/maxwell-20261017/experiments/R001/core-cache'
OUT=HERE/'R002-checks.json'
assert not OUT.exists(), 'Keep prior audit output'
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
geom={(r['Story'],r['Link']):r for r in readcsv(DATA/'R001-link-geometry-88.csv')}
rows=readcsv(DATA/'R002-native-horizontal/layer-axis-peaks-48.csv')
dev=readcsv(DATA/'R002-native-horizontal/device-contributions-384.csv')
hm=json.loads((PAIR/'local_history_manifest_r006.json').read_text(encoding='utf-8'))
cm=json.loads((CORE/'manifest.json').read_text(encoding='utf-8'))
sf=cm['tables']['Story Forces']
lookup={(g['keys']['Story'],g['keys']['Output Case']):k for k,g in sf['groups'].items()}
agroups={}
for a in hm['arrays']:agroups.setdefault((a['Story'],a['Case']),[]).append(a)
metrics=[];matches=0;maxerr=0.;i_equals_j=0
with np.load(PAIR/'local_paired_histories_r006.npz',allow_pickle=False) as z,np.load(CORE/sf['cache'],allow_pickle=False) as s:
    for r in rows:
        key=(r['Story'],r['Case']); axis=r['Axis']; ai=0 if axis=='X' else 1
        ar=s[lookup[key]];t=ar[:,sf['columns'].index('Time')];q=ar[:,sf['columns'].index('V'+axis)]
        d=np.zeros_like(q);branch={}
        for a in agroups[key]:
            h=z[a['key']];cols=a['columns'];g=geom[(r['Story'],a['Link'])]
            assert np.array_equal(h[:,cols.index('t_s')],t)
            p=h[:,cols.index('P_I_kN')]
            assert np.array_equal(p,h[:,cols.index('P_J_kN')]);i_equals_j+=1
            n=(float(g['nx']),float(g['ny']))[ai]
            b=n*p;d+=b;branch[a['Link']]=(b,p,h,cols,n)
        it=int(np.argmax(np.abs(q)));im=int(np.argmax(np.abs(q-d)));ip=int(np.argmax(np.abs(q+d)));idd=int(np.argmax(np.abs(d)))
        vals={'QT_peak_kN':abs(q[it]),'QT_peak_t_s':t[it],'QT_signed_at_peak_kN':q[it],
              'QD_peak_abs_kN':abs(d[idd]),'QD_at_QT_peak_kN':d[it],
              'QS_minus_peak_kN':abs(q[im]-d[im]),'QS_plus_peak_kN':abs(q[ip]+d[ip]),
              'QS_minus_peak_over_QT':max(abs(q-d))/max(abs(q)),
              'QS_plus_peak_over_QT':max(abs(q+d))/max(abs(q))}
        for field,value in vals.items():
            err=abs(float(r[field])-float(value));maxerr=max(maxerr,err)
            assert err<1e-10*max(1,abs(value)),(key,axis,field,err)
            matches+=1
        ds=[a for a in dev if (a['Story'],a['Case'],a['Axis'])==(r['Story'],r['Case'],axis)]
        assert len(ds)==8
        for dr in ds:
            b,p,h,cols,n=branch[dr['Link']]
            for field,value in [('horizontal_at_QT_peak_kN',b[it]),('horizontal_at_QS_minus_peak_kN',b[im]),('projection_n',n),('P_at_QT_peak_kN',p[it])]:
                err=abs(float(dr[field])-float(value));maxerr=max(maxerr,err)
                assert err<1e-10*max(1,abs(value));matches+=1
        assert sum(abs(x[-1])>1e-12 for x in branch.values())==4
        if r['input_main_axis']=='True':metrics.append({'Story':r['Story'],'Case':r['Case'],'Axis':axis,'QT_peak':float(max(abs(q))),'QD_at_QT_peak':float(d[it]),'minus_ratio':float(max(abs(q-d))/max(abs(q))),'plus_ratio':float(max(abs(q+d))/max(abs(q)))})
assert len(rows)==48 and len(metrics)==24 and len(dev)==384
assert {r['Case'] for r in rows}=={'RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y'}
result={'independent_recalculation':True,'layer_axis_rows':48,'main_input_axis_rows':24,'cross_axis_rows':24,'device_axis_rows':384,'unique_device_cases':192,'P_I_J_checks_with_two_axes':i_equals_j,'numeric_checks_passed':matches,'max_absolute_roundoff_difference':maxerr,'main_input_metrics':metrics,'physical_cut_sign_resolved':False,'source_geometry_sha256':hashlib.sha256((DATA/'R001-link-geometry-88.csv').read_bytes()).hexdigest()}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='main_input_metrics'},ensure_ascii=False,indent=2))
