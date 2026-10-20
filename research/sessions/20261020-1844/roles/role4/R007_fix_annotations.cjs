const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs');
const O=__dirname,src=path.join(O,'R006-Story8-QT-QD-two-cases.svg');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const original=fs.readFileSync(src,'utf8');let moved=0;
 const edited=original.replace(/<text\b([^>]*)>(QT峰[^<]*|QD峰[^<]*)<\/text>/g,(whole,attrs,label)=>{moved++;return '<text'+attrs.replace(/y="([\d.]+)"/,(_,v)=>'y="'+(Number(v)-26).toFixed(3)+'"')+'>'+label+'</text>';});
 if(moved!==4)throw Error('Expected four annotation labels');
 const geom=s=>s.match(/<(?:polyline|line|circle|path|polygon)\b[^>]*>/g).join('\n');
 if(geom(edited)!==geom(original))throw Error('Geometry changed');
 const svg=path.join(O,'R007-Story8-QT-QD-two-cases-qa.svg'),png=path.join(O,'R007-Story8-QT-QD-two-cases-qa.png');
 fs.writeFileSync(svg,edited,{encoding:'utf8',flag:'wx'});
 const info=await sharp(Buffer.from(edited),{density:200}).resize({width:2200}).png({compressionLevel:9}).withMetadata({density:200}).toFile(png);
 const meta=await sharp(png).metadata();const out={utc:new Date().toISOString(),original_svg:src,original_sha256:hash(original),corrected_svg:svg,corrected_svg_sha256:hash(edited),png,png_sha256:hash(fs.readFileSync(png)),width:meta.width,height:meta.height,density_ppi:meta.density,bytes:info.size,labels_moved:4,change:'Only peak annotation label y positions moved upward 26 SVG units to clear vertical guides; all curve/line/circle geometry identical; all text numbers unchanged',geometry_unchanged:true,requires_manual_view:true};
 fs.writeFileSync(path.join(O,'R007-layout-repair.json'),JSON.stringify(out,null,2)+'\n',{encoding:'utf8',flag:'wx'});console.log(JSON.stringify(out));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
