const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs');
const O=__dirname,hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const write=(n,x)=>fs.writeFileSync(path.join(O,n),JSON.stringify(x,null,2)+'\n',{encoding:'utf8',flag:'wx'});
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const common={
 '相对标签0的原生剪力峰值降幅 / %':'相对基准模型的剪力峰值降幅/%',
 '相对标签0的峰值降幅 / %':'相对基准模型的剪力峰值降幅/%',
 '降幅 = 100 × (1 − P3/P0)；各层峰分别取自各自完整时程':'降幅 = 100×(1−P_M/P_B)；P_B、P_M分别为两模型各自完整时程的剪力绝对峰'
};
const jobs=[
 {src:'R004-six-case-reduction-profiles.svg',stem:'R008-six-case-reduction-profiles',map:{
  '共同六工况：各层原生剪力峰值降幅':'各楼层水平剪力峰值的降幅',
  '标签0基准 → 标签3模型；Bottom输出；三波族各X/Y':'基准模型与增加3个百分点模态阻尼模型比较；三组输入分别沿X、Y向作用'}},
 {src:'../role1/R004-local-modal-terms.svg',stem:'R008-local-modal-terms',map:{
  'H2 / QS2: signed modal terms on the same saved time axis':'第2层弹性剪力的振型叠加（H2输入）',
  'Mode 1':'第1阶','Mode 2':'第2阶','Mode 3':'第3阶','Total QS2':'三阶合计 V2',
  'No added device (C = .02 K)':'无阻尼器（C = 0.02K）',
  'Device at story 1 (same bare basis)':'第1层设置阻尼器（同参考振型）',
  'Time and QS2 are nondimensional; local window only':'时间与第2层弹性剪力 V2 均为无量纲量；图示为局部时窗',
  'Dashed lines: common anchors 20.090 and 20.215. No new ODE; same-state projection.':'虚线对应20.090和20.215两个时刻。'}},
 {src:'R007-Story8-QT-QD-two-cases-qa.svg',stem:'R008-Story8-QT-QD-two-cases',map:{
  '现有实体装置模型：Story8剪力与装置水平合力时序':'第8层楼层剪力与阻尼器水平合力时程',
  '局部时窗5—25秒；保留0.02秒原生采样，未平滑；上下纵轴范围不同':'RH4X、RH4Y输入；局部时窗5—25秒，上下纵轴尺度不同',
  'QD = Σ n_axis P：上端J的结构内力抵抗项；装置对J的外力为−QD。图中没有计算主体QT−QD。':'QD = Σ n_axis P，n由下端I指向上端J；QD取J端内力抵抗方向，装置对J的作用力为−QD。'}},
 {src:'R004-all14-directional-envelope.svg',stem:'R008-all14-directional-envelope',map:{
  '14工况：各方向逐层剪力降幅分布':'各方向楼层剪力峰值降幅的分布',
  '标签0基准 → 标签3模型；每方向7工况；阴影为最小—最大，实线为中位数':'基准模型与增加3个百分点模态阻尼模型比较；每方向7组输入',
  '统计单位为工况；X/Y分量不视为独立地震事件。原生QT不自动等于剔除装置后的主体QS。':'阴影表示最小—最大范围，实线表示中位数；X、Y向结果分别统计。'}}
];
const geometry=s=>(s.match(/<(?:polyline|circle|line|path|polygon)\b[^>]*>/g)||[]).join('\n');
const numbers=s=>(s.match(/<text\b[^>]*>[+-]?[\d.]+<\/text>/g)||[]).join('\n');
(async()=>{
 write('R008-input-freeze.json',{utc:new Date().toISOString(),start_observed_utc:'2026-10-20T12:21:48Z',code_sha256:hash(fs.readFileSync(__filename)),scope:'requested publication wording only; all geometry and numeric tick coordinates unchanged; no science',inputs:jobs.map(j=>{const p=path.resolve(O,j.src);return {path:p,sha256:hash(fs.readFileSync(p))};})});
 const records=[];
 for(const j of jobs){
  const src=path.resolve(O,j.src),old=fs.readFileSync(src,'utf8'),map={...common,...j.map};let count=0;
  let edited=old.replace(/(<text\b[^>]*>)([^<]*)(<\/text>)/g,(all,open,body,close)=>{let txt=map[body];if(/^Story\d+$/.test(body))txt='第'+body.slice(5)+'层';if(txt!==undefined){count++;return open+esc(txt)+close;}return all;});
  edited=edited.replace(/<title>[^<]*<\/title>/g,'<title>'+esc(j.stem==='R008-local-modal-terms'?'第2层弹性剪力的振型叠加':'楼层剪力研究图')+'</title>').replace(/<desc>[^<]*<\/desc>/g,'<desc>楼层剪力研究图。模型与物理量定义见图中文字及正文。</desc>');
  if(geometry(edited)!==geometry(old)||numbers(edited)!==numbers(old))throw Error('Geometry or numeric positions changed '+j.stem);
  if(/标签0|标签3|No new ODE|same-state projection|QS2/.test(edited))throw Error('Unconverted text '+j.stem);
  const svg=path.join(O,j.stem+'.svg'),png=path.join(O,j.stem+'.png');fs.writeFileSync(svg,edited,{encoding:'utf8',flag:'wx'});
  const info=await sharp(Buffer.from(edited),{density:200}).resize({width:2200}).png({compressionLevel:9}).withMetadata({density:200}).toFile(png);const meta=await sharp(png).metadata();
  const r={source_svg:src,source_sha256:hash(old),revised_svg:svg,revised_svg_sha256:hash(edited),approved_png_pending_visual_QA:png,png_sha256:hash(fs.readFileSync(png)),width:meta.width,height:meta.height,density_ppi:meta.density,bytes:info.size,text_replacements:count,all_geometry_strings_identical:true,numeric_tick_text_and_positions_identical:true,original_source_unchanged:hash(fs.readFileSync(src))===hash(old)};records.push(r);console.log(JSON.stringify(r));
 }
 write('R008-render-map.json',{utc:new Date().toISOString(),records,requires_actual_view_image_QA:true});
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
