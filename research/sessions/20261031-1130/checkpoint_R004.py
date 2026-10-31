from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2];now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not(S/'git-R004-publication.json').exists()
d=json.loads((S/'status.json').read_text());d.update(last_actual=now,checkpoint='R004-reviewed-forward',checkpoint_open=True,recovery_file='rounds/R004.md')
d['scientific_status'].update(direct_forward='reviewed role2R005 frozen12:25:45;216CM+144shear diagnostics4680numbers checked;6 ownRK4 checks ~7e-10; no fit, CM signed vs shearabsolute scope distinct',modal_terms='root independent audit21600modepeaks/36pairs/288anchors passed<4e-12kN;maxnative/reference peak-reductiondiff.196533pp; linear physical-source reference not fullFE unique q',manuscript='v003 frozen14117B fullrootread+S1; role5R004/v004 integrating reviewed forward and new modal layer mechanism,active')
d['current_tasks'].update(role1='R005 physical-modal truncation/90-95-99mass engineering comparison protocol8min active',role2='R006 commonunit modal amplitude ratios2/10/13/18 and weightedU mechanism10min, noODE, active',role3='R006/R007/R008 frozen source support; v003 fullcitation review0newmust; ownwindow13:11:38; waiting newevidence',role4='R006 δabs∞/288same-timeχ andβ+36peak-ratioerror scale8min active, noODE',role5='R004/v004 layer-mechanism and engineering algorithm integrating reviewed results12min active',role6='R005 Story5/12 realreference topweights/same-time mechanism8min active')
d['next_checkpoint']='Collect role4R006/role2R006 and authorv004, root read; physical modal truncation using frozen arrays only after role4 idle and role1protocol, no repeated state integrations/fits. Finaldeadline15:30:11, writing14:45:11.'
js(S/'status.json',d)
with (S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC020-08 reviewed: role2R004 independently checked72B/24mass/3observability andtheory0must.\nC020-10 supported/numerical reference prediction, reviewed: role2R005216CM+144shear metrics4680numbers agree; six selectedSHW3 independentRK4~7e-10relativeL2. MaxCMsignedNRMSE.35437%,Eabsolute-curve.65822%,peak.23517%. Signedforce mapping unconfirmed, nativeFNAq not recovered.\nC020-11 supported/reference-modal explanation, root independent numerical audit:21600single-mode peaks and36U/P/C+288anchors reconstruct;maxclosure<4e-12kN. SHW3 Story5 .903493*1.030990=.931492 vsroof .846186*.847092=.716798. All36 native-reference peakreduction discrepancies ≤.196533pp observed, not universal error guarantee.\n')
(S/'rounds/R004.md').write_text('# R004｜无拟合预测独审通过，层差机制开始量化\n\n实际记录'+now+'。④R004已冻，根全文读代码/README/results，②R00512:25:45独审正式冻：216CM+144剪力指标4680数及6独立RK4通过0must。CM是signed，剪力仅absolute曲线及峰，符号映射未核；不能将abs误差.65822%写成signed时程误差。\n\n④R005已冻，根新audit_modal_terms_root.py独立重建21600单阶峰、36对U/P/C和288同刻锚点，差<4e-12kN；SHW3 Story5幅值总量下降9.65%但C增加3.10%，最终峰降6.8508%；屋顶U/C均下降，峰降28.3202%。36对参照与native峰降差最大.196533个百分点。不是相位因果份额，也不是实际FNA唯一分力。\n\n⑤v00314117B和S1根全文读，③原文复核0newmust；新v004正在整合审过实数与工程简化流程。下一主线是物理模态保留阶数收敛与全楼质量率规则的比较，不新ODE/拟合：①预定义90/95/99%阈值与N13/18/300，④现补误差尺度/同刻β，②现算公共单位幅比，⑥解释主层实数。\n\n本点Git仅已冻R004/R005生产与审核、旧v003，活动新角色任务文件不收。截止15:30:11不延长，14:45:11起集中成稿。\n',encoding='utf-8')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR004 '+now+': directphysicalforward independentlyvalidated, root term audit actually run1.1s; no new rootODE or rawexport. Submittedrole1truncationprotocol,role2unitamplitudes,role4error/β,role5v004,role6engineeringinterpretation. NewGitfrozenonly.\n')
files=[]
scope={'role1':['R004'],'role2':['R004','R005'],'role3':['R006','R007','R008'],'role4':['R004','R005'],'role5':['R003'],'role6':['R004']}
for role,rounds in scope.items():
 for rr in rounds:
  base=S/'roles'/role/rr
  assert any((base/n).exists()for n in ['manifest.json','freeze.json','delivery-manifest.json','delivery-manifest-v002.json'])
  for p in base.rglob('*'):
   if p.is_file()and 'local-cache'not in p.parts and p.suffix in ['.md','.json','.csv','.py','.svg','.png']and p.stat().st_size<1048576:files.append(p)
files.extend(p for p in(S/'root-R004-term-audit').iterdir()if p.is_file())
for n in ['checkpoint_R004.py','close_checkpoint_R003.py','R003-closed-receipt.json','audit_modal_terms_root.py','status.json','threads.json','claims.md','runs.md','rounds/R004-early.md','rounds/R004.md','git-R003-receipt.json']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-v003.md')
js(S/'git-R004-publication.json',dict(checkpoint='R004',time=now,message='research: validate no-fit modal prediction and explain floor damping differences',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(set(files))]))
print(json.dumps(dict(time=now,files=len(set(files)),bytes=sum(p.stat().st_size for p in set(files))),ensure_ascii=False))
