from pathlib import Path
import re,json,hashlib,datetime
R=Path('E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/01-lunwen')
H=Path(__file__).resolve().parent
old=R/'papers/damping-output-boundaries/manuscript/p06-design-reflection-session024-v002.md'
new=R/'papers/damping-output-boundaries/manuscript/p06-mechanism-classification-v001.md'
a=old.read_text(encoding='utf-8');b=new.read_text(encoding='utf-8')
assert hashlib.sha256(new.read_bytes()).hexdigest()=='39cda7f74e8d214ab0cbdc57abf22c98390224b9c2eb912cea919b8ca1f9bcf9'
tables=lambda s:re.findall(r'(?m)^\|.*$',s)
maths=lambda s:re.findall(r'\$\$(.*?)\$\$',s,re.S)
images=lambda s:re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s)
assert tables(a)==tables(b)
assert maths(a)==maths(b) and len(maths(b))==5
assert images(a)==images(b) and len(images(b))==3
assert '没有出现第10、13阶同向叠加主导' not in b
assert '由−42.62kN变为+37.90kN' in b and '增加的80.51kN' in b
assert '由8632.39kN降至7753.76kN' in b
out={'at':datetime.datetime.now().astimezone().isoformat(),'draft':str(new.relative_to(R)),
 'sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'table_rows_equal':True,'display_equations_equal':True,
 'images_equal':True,'table_row_count':len(tables(b)),'display_count':len(maths(b)),'image_count':len(images(b)),
 'manual_targeted_read':['Chinese abstract','English abstract','4.2','6.1','conclusion3'],
 'scientific_must':0,'delivery_dependency':'new mechanism supplement link must exist before delivery; parent notified'}
assert not (H/'targeted-final-review.json').exists()
(H/'targeted-final-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
