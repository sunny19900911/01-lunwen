"""Pair frozen native P/U1 and Story Forces with newly exported geometry.
No solver, new constitutive inference, time interpolation, or missing-data fill.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,csv,math,sys
import numpy as np

HERE=Path(__file__).parent
ROOT=HERE.parents[4]
OLD=ROOT.parent/'W5-重燃双塔连体/research'
PAIR=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution'
CORE=OLD/'maxwell-20261017/experiments/R001/core-cache'
OUT=HERE/'R002-native-horizontal'
OUT.mkdir(exist_ok=True)
assert not any(OUT.iterdir()), 'Refuse overwriting any completed or partial output'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def jwrite(name,obj):(OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def peak(a,t):
    k=int(np.argmax(np.abs(a)));return k,float(abs(a[k])),float(t[k]),float(a[k])
geom=rcsv(HERE/'R001-link-geometry-88.csv')
G={(r['Story'],r['Link']):r for r in geom}
hm=json.loads((PAIR/'local_history_manifest_r006.json').read_text(encoding='utf-8'))
cm=json.loads((CORE/'manifest.json').read_text(encoding='utf-8'))
oldsum={r['local_array_key']:r for r in rcsv(PAIR/'device_record_summary_r006.csv')}
sf=cm['tables']['Story Forces'];base=cm['tables']['Base Reactions']
storykeys={(g['keys']['Story'],g['keys']['Output Case']):k for k,g in sf['groups'].items()}
basekeys={g['keys']['Output Case']:k for k,g in base['groups'].items()}
groups=defaultdict(list)
for a in hm['arrays']:groups[(a['Story'],a['Case'])].append(a)
assert len(groups)==24 and all(len(a)==8 for a in groups.values())
results=[];devices=[];checks=[];local={}
with np.load(PAIR/'local_paired_histories_r006.npz',allow_pickle=False) as z,np.load(CORE/sf['cache'],allow_pickle=False) as sz,np.load(CORE/base['cache'],allow_pickle=False) as bz:
    for (story,case),records in sorted(groups.items()):
        source=sz[storykeys[(story,case)]];t=source[:,sf['columns'].index('Time')]
        tref=bz[basekeys[case]][:,base['columns'].index('Time')]
        assert np.array_equal(t,tref) and np.all(np.diff(t)>0) and len(t)==len(np.unique(t))
        members=sorted(records,key=lambda r:r['Link']);P=[];U=[];R=[];N=[]
        expected={r['Link'] for r in geom if r['Story']==story}
        assert {r['Link'] for r in members}==expected
        for a in members:
            ar=z[a['key']];cols=a['columns'];g=G[(story,a['Link'])]
            assert np.array_equal(ar[:,cols.index('t_s')],t)
            p=ar[:,cols.index('P_I_kN')];pj=ar[:,cols.index('P_J_kN')];u=ar[:,cols.index('U1_m')]
            assert np.array_equal(p,pj) and np.isfinite(ar).all()
            assert np.allclose(ar[:,cols.index('U1_mm')]*.001,u,rtol=1e-14,atol=1e-16)
            assert float(g['I_Z_m'])<float(g['J_Z_m'])
            P.append(p);U.append(u);R.append(ar);N.append([float(g['nx']),float(g['ny'])])
            frozen=oldsum[a['key']]
            work=float(np.sum((p[1:]+p[:-1])*.5*np.diff(u)))
            assert abs(work-float(frozen['Wtrap_native_kNm']))<1e-10*max(1,abs(work))
            assert max(abs(p))==float(frozen['max_abs_native_P_kN'])
        P=np.array(P);U=np.array(U);N=np.array(N)
        qd=N.T@P
        for ai,axis in enumerate(('X','Y')):
            qt=source[:,sf['columns'].index('V'+axis)]
            d=qd[ai];it,pt,tt,st=peak(qt,t);idd,pd,td,sd=peak(d,t)
            minus=qt-d;plus=qt+d;im,pm,tm,sm=peak(minus,t);ip,pp,tp,sp=peak(plus,t)
            denom=float(np.dot(qt,qt)); cos=float(np.dot(qt,d)/(np.linalg.norm(qt)*np.linalg.norm(d))) if np.linalg.norm(d)>0 else None
            row={'Story':story,'Case':case,'Axis':axis,'input_main_axis':case[-1]==axis,
                 'n_points':len(t),'t0_s':float(t[0]),'t1_s':float(t[-1]),'devices_total':8,'devices_nonzero_projection':int(np.sum(abs(N[:,ai])>1e-12)),
                 'QT_peak_kN':pt,'QT_peak_t_s':tt,'QT_signed_at_peak_kN':st,
                 'QD_peak_abs_kN':pd,'QD_peak_t_s':td,'QD_signed_at_own_peak_kN':sd,
                 'QD_at_QT_peak_kN':float(d[it]),'QD_at_QT_peak_over_QT_signed':float(d[it]/st),
                 'QD_peak_over_QT_peak':pd/pt,'QT_QD_cosine_sample':cos,
                 'QS_minus_peak_kN':pm,'QS_minus_peak_t_s':tm,'QS_minus_signed_at_peak_kN':sm,'QS_minus_peak_over_QT':pm/pt,
                 'QS_plus_peak_kN':pp,'QS_plus_peak_t_s':tp,'QS_plus_signed_at_peak_kN':sp,'QS_plus_peak_over_QT':pp/pt,
                 'QD_at_QS_minus_peak_kN':float(d[im]),'QT_at_QS_minus_peak_kN':float(qt[im]),
                 'QT_source_row_at_QT_peak':int(source[it,sf['columns'].index('SourceRow')]),
                 'QT_source_row_at_QS_minus_peak':int(source[im,sf['columns'].index('SourceRow')]),
                 'force_scope':'native axial P projected with new geometry',
                 'QS_scope':'same-state algebraic remainder under H_cut and chosen sign; not certified main-structure shear'}
            results.append(row)
            key=story+'__'+case+'__'+axis
            local[key]=np.column_stack([t,qt,d,minus,plus,source[:,sf['columns'].index('SourceRow')]])
            for di,a in enumerate(members):
                g=G[(story,a['Link'])];q=N[di,ai]*P[di];jq,pq,tq,sq=peak(q,t);jp,pa,ta,sa=peak(P[di],t);ju,pu,tu,su=peak(U[di],t)
                old=oldsum[a['key']]; rr=R[di];cc=a['columns']
                devices.append({'Story':story,'Case':case,'Axis':axis,'Link':a['Link'],'input_main_axis':case[-1]==axis,
                    'projection_n':float(N[di,ai]),'P_peak_kN':pa,'P_peak_t_s':ta,'P_signed_at_peak_kN':sa,
                    'U1_peak_total_mm':pu*1000,'U1_peak_t_s':tu,'horizontal_peak_abs_kN':pq,'horizontal_peak_t_s':tq,
                    'horizontal_at_QT_peak_kN':float(q[it]),'horizontal_at_QS_minus_peak_kN':float(q[im]),
                    'horizontal_at_QD_peak_kN':float(q[idd]),'P_at_QT_peak_kN':float(P[di,it]),
                    'P_I_source_row_at_QT_peak':int(rr[it,cc.index('force_I_row')]),
                    'P_I_source_row_at_QS_minus_peak':int(rr[im,cc.index('force_I_row')]),
                    'U1_source_row_at_peak':int(rr[ju,cc.index('deformation_row')]),
                    'Wtrap_native_port_kNm':float(old['Wtrap_native_kNm']),
                    'Dport_conditional_previous_kNm':float(old['Dport_conditional_kNm']),
                    'Dport_scope':'old conditional spring-storage correction; not independently certified native damper dissipation',
                    'I_Point':g['I_Point'],'J_Point':g['J_Point'],'geometry_link_source_row':g['link_source_row']})
        checks.append({'Story':story,'Case':case,'8_geometry_matches':True,'all_P_I_equals_P_J':True,'all_time_axes_match_base_and_story_exactly':True,
                       'n_points':len(t),'t0_s':float(t[0]),'t1_s':float(t[-1]),'I_lower_J_upper':True,'no_interpolation_or_zero_fill':True})
write('layer-axis-peaks-48.csv',results);write('device-contributions-384.csv',devices);write('pairing-checks-24.csv',checks)
(HERE/'local-cache/R002-native-horizontal').mkdir(exist_ok=False)
np.savez_compressed(HERE/'local-cache/R002-native-horizontal/paired-layer-histories.npz',**local)
rank=[]
for story in sorted({r['Story'] for r in results},key=lambda x:int(x[5:])):
    for axis in ('X','Y'):
        rows=[r for r in results if r['Story']==story and r['Axis']==axis and r['input_main_axis']]
        worst=max(rows,key=lambda r:r['QT_peak_kN'])
        rank.append({'Story':story,'Axis':axis,'max_QT_peak_kN':worst['QT_peak_kN'],'QT_control_case':worst['Case'],
          'median_QD_peak_over_QT':float(np.median([r['QD_peak_over_QT_peak'] for r in rows])),
          'min_QD_at_QT_peak_fraction':min(r['QD_at_QT_peak_over_QT_signed'] for r in rows),
          'max_QS_minus_over_QT':max(r['QS_minus_peak_over_QT'] for r in rows),
          'max_QS_plus_over_QT':max(r['QS_plus_peak_over_QT'] for r in rows),
          'scope':'existing controlled-state priority only; sign and H_cut conditional'})
rank.sort(key=lambda r:r['max_QT_peak_kN'],reverse=True)
write('target-priority-8.csv',rank)
manifest={'completed_Asia_Shanghai':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'script_sha256':sha(Path(__file__)),
 'inputs':{str(p):sha(p) for p in [HERE/'R001-link-geometry-88.csv',PAIR/'local_history_manifest_r006.json',PAIR/'local_paired_histories_r006.npz',PAIR/'device_record_summary_r006.csv',CORE/'manifest.json',CORE/sf['cache']]},
 'source_response_sha256':cm['sha256'],'source_geometry_sha256':'b75a8979bc902890f025f28e76f69a652796a2304326845e89fc1986500bea04',
 'checks':{'192_complete_native_device_histories':True,'24_complete_8_device_story_cases':True,'48_story_axis_results':True,'P_I_J_equal_count_once':True,'exact_time_match':True,'native_port_work_matches_frozen_summary':True},
 'sign_and_cut':'Geometry I lower/J upper; positive-extension axial P maps to structural internal J resistance +nP. Native Bottom VX/VY cut-side sign and Link inclusion not certified by existing exports; report QT-QD and QT+QD rather than select favorable sign.',
 'new_model_prediction':False,'no_solver':True,'no_original_big_excel_read':True,
 'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in OUT.glob('*.csv')}}
jwrite('manifest.json',manifest)
lines=['# 高层四层原生阻尼力的水平分力与楼层剪力','',
 '本轮把新导出的真实几何，与此前完整的原生轴力及楼层剪力逐点配对。覆盖Story8—11、三波族各X/Y六工况，共32只装置、192条完整轴力时程。以下是现有有控状态后处理，不是改变布置后的预测。','',
 '## 配对与正负号','',
 '- 24个楼层—工况各8只装置全齐；时间与原生Base和Story Forces逐点完全一致，未插值、补零或截短。P在I/J两行完全相同，只计一次。',
 '- I在下层、J在上层，纯轴正拉力的上端结构内力向量可写nP；每层4只X、4只Y。',
 '- Story Forces仅有Bottom输出。其截面侧别、符号以及是否包含Link未在现有资料独立认证，因此并列QT−QD与QT+QD两种符号结果，均先称同轨迹代数余量。不能按有利结果选正负号。','',
 '## 主输入方向结果','',
 '|层|工况|方向|QT峰/kN|QD峰/kN|QT峰时QD/kN|QT−QD峰/QT峰|QT+QD峰/QT峰|','|---|---|---|---:|---:|---:|---:|---:|']
for r in sorted([x for x in results if x['input_main_axis']],key=lambda x:(int(x['Story'][5:]),x['Case'])):
    lines.append(f'|{r["Story"]}|{r["Case"]}|{r["Axis"]}|{r["QT_peak_kN"]:.2f}|{r["QD_peak_abs_kN"]:.2f}|{r["QD_at_QT_peak_kN"]:.2f}|{r["QS_minus_peak_over_QT"]:.6f}|{r["QS_plus_peak_over_QT"]:.6f}|')
lines+=['','## 工程用途与保守排序','',
 '- `target-priority-8.csv`按现有总楼层剪力峰排序，作为优先检查楼层，不代表该层最危险或应直接加装。主体刚度、承载力和层高需共同考虑。',
 '- `device-contributions-384.csv`同时给逐器件轴力、总U1、水平分力，以及QT峰和条件主体峰同一时刻的装置贡献。可据此选择小范围调整对象，再检验移位后的真实运动是否仍有利。',
 '- 水平分力与QT的相位关系会改变峰值位置。只有逐时计算后寻找绝对最大值，才与该假定下的主体剪力定义相符；独立峰值不能直接相减。',
 '- 几何和轴力已无需名义本构估算；但全模型身份、截面包含性、实际安装构件和新方案响应仍有各自的核实环节。','',
 '## 能量与装置需求','',
 '- 逐器件端口功按原生P与总U1增量积分，并与此前冻结结果逐条一致；它是该时段端口功，含弹簧储能变化，不直接等于纯耗散。',
 '- 另列旧有条件弹簧储能扣除后的Dport，保留其条件身份，不把它升级为实际耗能或全楼能量闭合。',
 '- 现有装置P和U1峰是已计算结果；新位置、新参数会改变相对运动和装置力，不能把这份原时程移过去直接认为保持。','',
 '## 结果文件','',
 '- `layer-axis-peaks-48.csv`：48个层—工况—方向的峰值与控制时刻，含双号敏感性。',
 '- `device-contributions-384.csv`：384条方向装置贡献（含零投影方向，不能混作384个独立装置记录）。',
 '- `pairing-checks-24.csv`：实际完整性核查。',
 '- `target-priority-8.csv`：按总剪峰排序的8个楼层—方向检查对象。',
 '- `manifest.json`：所有输入散列及实际执行范围。大时程只在local-cache中。','']
(OUT/'report.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'completed':True,'rank':rank,'main_examples':[r for r in results if r['Case']=='RH4X' and r['Axis']=='X']},ensure_ascii=False,indent=2))
