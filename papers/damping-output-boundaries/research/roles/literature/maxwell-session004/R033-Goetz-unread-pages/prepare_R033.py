from pathlib import Path
import hashlib,json,subprocess
from pypdf import PdfReader
base=Path(__file__).resolve().parent
cache=base/'local-cache'
cache.mkdir(exist_ok=True)
source=base.parents[2]/'novelty/maxwell-session004/R027-RL-equivalent-prior-art/local-cache/Goetz2013.pdf'
b=source.read_bytes()
assert hashlib.sha256(b).hexdigest()=='6e7449324392802c8351138e3643fae8e966e89c34352a32cb2824d5b118e63f'
reader=PdfReader(source)
assert len(reader.pages)==12
for n in [3,4,5,6,12]:
    (cache/f'Goetz2013-p{n:02}.txt').write_text(reader.pages[n-1].extract_text(),encoding='utf-8',newline='\n')
poppler='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
subprocess.run([poppler,'-f','3','-l','6','-r','95','-png',str(source),str(cache/'Goetz2013')],check=True)
subprocess.run([poppler,'-f','12','-l','12','-r','95','-png',str(source),str(cache/'Goetz2013')],check=True)
print(json.dumps({'source':str(source),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'pages':len(reader.pages),'extracted_and_rendered':[3,4,5,6,12]},ensure_ascii=False))
