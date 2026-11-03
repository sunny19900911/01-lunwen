from pathlib import Path
import subprocess,sys,json,datetime,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];C=H/'local-cache';C.mkdir(exist_ok=True)
src=R/'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-v002.md'
out=src.with_name('p06-actual-damper-session025-论文审阅稿-v002.docx')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='f5e12aa1a68cfa5a81473a8f1ef09fc4540cbf1e10207a25ca976834794d0a87'
assert not out.exists() and not (C/'marker-receipt.json').exists()
node=Path('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
marker=Path('C:/Users/mj528/.codex/plugins/cache/openai-primary-runtime/documents/26.1025.11240/skills/documents/container_tools/mark_artifact_operation_started.mjs')
p=subprocess.run([str(node),str(marker),'--operation-kind','edit','--expected-output-count','1','--output-format','docx'],capture_output=True,text=True,cwd=H)
(C/'marker.stdout.txt').write_text(p.stdout,encoding='utf-8');(C/'marker.stderr.txt').write_text(p.stderr,encoding='utf-8')
receipt={'at':datetime.datetime.now().astimezone().isoformat(),'exit_code':p.returncode,'success_count':int(p.returncode==0),'expected_output_count':1,'output_format':'docx','command':[str(node),str(marker),'--operation-kind','edit','--expected-output-count','1','--output-format','docx']}
(C/'marker-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert p.returncode==0,p.stderr
cmd=[sys.executable,'-X','utf8',str(H/'build_word.py'),'--input',str(src),'--output',str(out),'--report',str(C/'build-report.json'),'--author','--marker-receipt',str(C/'marker.stdout.txt')]
p=subprocess.run(cmd,capture_output=True,text=True,cwd=R)
(C/'build.stdout.txt').write_text(p.stdout,encoding='utf-8');(C/'build.stderr.txt').write_text(p.stderr,encoding='utf-8')
assert p.returncode==0,p.stderr
print(json.dumps({'docx':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'marker_success_count':1},ensure_ascii=False))
