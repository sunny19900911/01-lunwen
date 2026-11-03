from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
F=S/'roles/audit/R001';freeze=json.loads((F/'freeze.json').read_text(encoding='utf-8'))
for x in freeze['files']:
 p=F/x['path'];assert p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
assert freeze['must_numeric']==0
algebra=json.loads((S/'roles/audit/R001-algebra-addendum.json').read_text(encoding='utf-8'));assert algebra['must']==0 and algebra['identity_residual']==0
v=R/'papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-v001.md';assert hashlib.sha256(v.read_bytes()).hexdigest()=='75aaecf467284add1a15709eca6c182cdff750d0e13ced05cf95b21ef60bef43'
out={'adopted_at':now,'audit_report':'roles/audit/R001/正确性与数字独审.md','audit_files_verified':len(freeze['files']),'must_numeric':0,'independent_not_blind':True,'C02':'Not supported in conditional fixed300 reference; native causal attribution unresolved.','C03':'Reviewed four-state reference numbers and absolute-output comparisons; retain adjacent18CM/Ritz/restoration/sign conditions.','engineering_algebra':'SH4 baseline17.1021percent higher, reference11.5066percent higher despite larger paired reduction; direct output identity only.','author_v001':'Root read entire original source and exact diff; only2.3 and new auxiliary structure changed; accepted as scaffold.','root_read_path_error':'First read used wrong nested addendum path; no data changed. Actual roles/audit/R001-algebra-addendum.json then fully read.','next':'Unique author R002: write concise reviewed auxiliary table/paragraph and supplement, no Word until content review.'}
(S/'root-R001-adoption.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (S/'claims.md').open('a',encoding='utf-8') as f:f.write('\n- C02 reviewed/not-supported：audit独立实现64字段通过，SH4第10阶更小/第13阶小反向，不支持所检验的10/13同向主导；不认原生全FE归因。\n- C03 reviewed/supported-with-conditions：四状态参照数值、绝对曲线与峰误差独核，符号/完整模型身份保留；不能以低误差认证原生逐阶。\n- C05 reviewed/observed-data：SH4基准峰较SH3高17.1021%，参考峰仍高11.5066%，成对需求—改善区别的直接输出读法。\n')
with (S/'runs.md').open('a',encoding='utf-8') as f:f.write('\n- '+now+' 根完整读audit正式报告/7文件manifest及代数补件，SHA通过；读作者v001精确diff/变更说明。首次根读补件路径少一层目录误报不存在，改实际路径后读成功，无科学副作用。独算非盲核已明。\n')
print(json.dumps(out,ensure_ascii=False))
