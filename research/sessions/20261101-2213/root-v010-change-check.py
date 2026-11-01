from pathlib import Path
import re,json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
a=(M/'damping-prediction-session021-v009.md').read_text(encoding='utf8');p=M/'damping-prediction-session021-v010.md';b=p.read_text(encoding='utf8')
assert re.findall(r'(?m)^\|.*\|$',a)==re.findall(r'(?m)^\|.*\|$',b)
assert re.findall(r'\$\$(.*?)\$\$',a,re.S)==re.findall(r'\$\$(.*?)\$\$',b,re.S)
assert len(re.findall(r'\$\$(.*?)\$\$',b,re.S))==10
assert '以指定三输入的楼层剪力最大峰包络及10%降幅为目标' in b
assert '并列控制时仅在并列输入中取最小S' in b
assert '对逐输入全部达标目标，8%二阶则可舍弃' in b
assert '完整分析按一条输入一次全模型求解计量' in b
assert 'PEER STRONG MOTION DATABASE' in b and 'Pacific Engineering' in b
newS1=(S/'roles/role5/R012/supplement-S1.md').read_text(encoding='utf8')
assert '后补入' not in newS1 and '独立评价留给其他输入' not in newS1
figs=re.findall(r'!\[[^]]*\]\(([^)]+)\)',b)
assert figs==re.findall(r'!\[[^]]*\]\(([^)]+)\)',a) and len(figs)==3
result={'actual':datetime.datetime.now().astimezone().isoformat(),'v010_bytes':p.stat().st_size,'v010_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'table_rows_exact':True,'all_10_display_formulas_exact':True,'three_figure_paths_exact':True,'target_workflow_and_citations_checked':True,'S1_stale_text_removed':True,'root_read':'Full v009-to-v010 and S1-R010-to-R012 diffs plus QA and manifest read; changes implement already adopted final review. No new whole scientific review.','failed_first_probe':'Previous inline PowerShell command expanded dollar-parenthesis regex, printed shell errors while Python still exited0. Its formula check result is invalid; this standalone script replaces it using unexpanded literal source.'}
(S/'root-v010-change-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
