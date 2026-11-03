from pathlib import Path
import re,json,hashlib,subprocess,sys,collections
H=Path(__file__).resolve().parent;R=H.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-actual-damper-session025-v002.md';dst=src.with_name('p06-actual-damper-session025-v003.md')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='f5e12aa1a68cfa5a81473a8f1ef09fc4540cbf1e10207a25ca976834794d0a87'
assert not dst.exists()
s=src.read_text(encoding='utf-8');before=s
a=s.index('![图1 ');b=s.index('\n\n### 4.2',a)
figure=s[a:b].strip();s=s[:a]+s[b:]
tabs=re.findall(r'(?:^\|.*\n)+',s,re.M);target=tabs[2];pos=s.index(target)+len(target)
s=s[:pos]+'\n'+figure+'\n\n'+s[pos:]
sentence='装置轴线长度为6.440～9.401m，水平倾角为29.20°～48.37°，各层配置见表5。'
assert s.count(sentence)==1;s=s.replace(sentence,'')
pos=s.index('**表5 ');s=s[:pos]+sentence+'\n\n'+s[pos:]
assert re.findall(r'(?:^\|.*\n)+',s,re.M)==re.findall(r'(?:^\|.*\n)+',before,re.M)
assert re.findall(r'!\[.*?\]\(.*?\)',s)==re.findall(r'!\[.*?\]\(.*?\)',before)
assert re.findall(r'\$\$.*?\$\$',s,re.S)==re.findall(r'\$\$.*?\$\$',before,re.S)
assert collections.Counter(re.findall(r'\S',s))==collections.Counter(re.findall(r'\S',before)),'Content characters changed beyond whitespace/reordering'
dst.write_text(s,encoding='utf-8',newline='\n')
out=M/'p06-actual-damper-session025-论文审阅稿-v003.docx';assert not out.exists()
C=H/'word/local-cache';assert json.loads((C/'marker-receipt.json').read_text(encoding='utf-8'))['success_count']==1
report={'previous_source':src.relative_to(R).as_posix(),'final_source':dst.relative_to(R).as_posix(),'final_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'edits':['Unchanged figure1 moved immediately after unchanged table3 within section4.1','One unchanged length/angle sentence moved next to table5 after geometry figure within section4.3.1'],'all_tables_exact':True,'all_display_equations_exact':True,'all_figures_exact':True,'all_non_whitespace_character_counts_exact':True,'new_marker_run':False,'reason':'Avoid excessive whitespace from full-width figure pagination without reducing figure legibility'}
(H/'layout-reflow-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cmd=[sys.executable,'-X','utf8',str(H/'word/build_word.py'),'--input',str(dst),'--output',str(out),'--report',str(C/'build-report-v2.json'),'--author','--marker-receipt',str(C/'marker.stdout.txt')]
p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(C/'reflow-build.stdout.txt').write_text(p.stdout,encoding='utf-8');(C/'reflow-build.stderr.txt').write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
print(json.dumps({'source':dst.name,'source_sha256':report['final_sha256'],'docx':out.name,'docx_bytes':out.stat().st_size,'docx_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'marker_success_count':1},ensure_ascii=False))
