const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs');
const O=__dirname;
const inputs=[
 ['R004-six-case-reduction-profiles.svg','R007-six-case-reduction-profiles.png'],
 ['R004-all14-directional-envelope.svg','R007-all14-directional-envelope.png'],
 ['../role1/R004-local-modal-terms.svg','R007-local-modal-terms.png'],
 ['R006-Story8-QT-QD-two-cases.svg','R007-Story8-QT-QD-two-cases.png']
];
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const write=(name,obj)=>fs.writeFileSync(path.join(O,name),JSON.stringify(obj,null,2)+'\n',{encoding:'utf8',flag:'wx'});
(async()=>{
 const start=new Date();const records=[];
 write('R007-input-freeze.json',{utc:start.toISOString(),start_observed_utc:'2026-10-20T12:11:31Z',code_sha256:hash(fs.readFileSync(__filename)),scope:'rasterization and visual QA only; no scientific recomputation; frozen SVGs remain unchanged',density:200,width:2200,inputs:inputs.map(([s])=>{const p=path.resolve(O,s);const b=fs.readFileSync(p);return {path:p,bytes:b.length,sha256:hash(b)};})});
 for(const [src,dst] of inputs){
  const input=path.resolve(O,src);const output=path.join(O,dst);if(fs.existsSync(output))throw Error('Refuse overwrite '+output);
  const buffer=fs.readFileSync(input);const info=await sharp(buffer,{density:200}).resize({width:2200}).png({compressionLevel:9}).withMetadata({density:200}).toFile(output);
  const m=await sharp(output).metadata();if(m.width!==2200||m.height<1000||m.density<180||info.size<10000)throw Error('Bad render '+output);
  const r={source_svg:input,source_sha256:hash(buffer),png:output,png_sha256:hash(fs.readFileSync(output)),bytes:info.size,width:m.width,height:m.height,density_ppi:m.density,rendered_utc:new Date().toISOString()};records.push(r);console.log(JSON.stringify(r));
 }
 write('R007-render-map.json',{render_finished_utc:new Date().toISOString(),sharp_version:sharp.versions.sharp,renderer:sharp.versions,records,requires_manual_view_image_QA:true});
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
