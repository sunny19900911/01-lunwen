from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
p=Path(__file__).resolve().parent
def rec(f):
 b=f.read_bytes();return {'file':f.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
now=datetime.now(timezone(timedelta(hours=8)))
m={'task':'role3 R001','access_date':'2026-10-21','official_guidelines_url':'https://jcjg.build.com.cn/EditorDN/PromptPageInfo.aspx?c=1&t=v','official_guidelines_sections':['II submission/templates','IV.1 editorial scope','V.1 abstract300–500/keywords5–8','V.2 figures/symbols/numbering','V.3 formatting and references'],'guideline_revision_date_not_displayed':True,'official_home_link':'https://jcjg.publish.founderss.cn/info/9184?lang=zh','official_home_access':'not accessible via tool once, no retry','old_official_record_only':'https://jcjg.build.com.cn/WKD/WebPublication/wkTextContent.aspx?contentID=f177d75c-ec49-40a3-9374-0705d790befb&mid=jcjg','old_8000word_8page_rule_not_certified_current':True,'domestic_work_adopted':{'authors':['柳博哲','汪梦甫'],'title':'梁端铰接钢管混凝土框架-核心筒结构的减震研究','journal':'世界地震工程','year':2024,'volume':'40','issue':'3','pages':'142–153','doi':'10.19994/j.cnki.WEE.2024.0053','new_access':'official indexed PDF record; no redownload','original_reading_reused':'engineering-session006/H001/source-scope.json and H005 bibliography audit'},'domestic_works_adopted':1,'new_full_text_downloads':0,'hard_vs_advisory_separated':True,'acceptance_probability_claim':False,'new_ODE_or_raw_data_reads':0}
(p/'R001-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v={'first_clock':'2026-10-21T07:42:32+08:00','last_clock':'2026-10-21T07:52:56+08:00','finished_at':now.isoformat(),'delivery_boundary':'2026-10-21T07:53:00+08:00','within_delivery_boundary':now<datetime.fromisoformat('2026-10-21T07:53:00+08:00'),'stopped_new_retrieval_at_boundary':True,'status':'bounded_official_requirements_and_reused_neighbour_closeout','new_search_queries':5,'new_downloads':0,'failed_home_opens':1,'retries':0,'manuscript_or_shared_writes':False,'Git_or_ETABS':False,'new_agents_or_chats':False}
(p/'R001-validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
z={'task':'role3 R001','frozen_at':now.isoformat(),'immutable':True,'files':[rec(p/n) for n in ['R001-report.md','R001-manifest.json','R001-validation.json','R001-close.py']],'ignored_raw_receipts':[rec(f) for f in (p/'R001-local-cache').glob('*.json')]}
(p/'R001-freeze.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for n in ['R001-report.md','R001-freeze.json']:print(json.dumps(rec(p/n),ensure_ascii=False))
print(json.dumps(v,ensure_ascii=False))
