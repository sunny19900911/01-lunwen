const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs');
(async()=>{
 const out=[];
 for(const name of ['figure-modal-amplitude-reduction','figure-floor-peak-reduction-calculated']){
  const src=path.join(__dirname,name+'.svg'),dst=path.join(__dirname,name+'.png');
  const m=await sharp(src,{density:144}).resize({width:1584}).png({compressionLevel:9,palette:true,quality:100}).toFile(dst);
  const bytes=fs.statSync(dst).size;if(bytes>=500000)throw Error('figure exceeds 500KB');
  out.push({file:path.basename(dst),bytes,width:m.width,height:m.height});
 }
 fs.writeFileSync(path.join(__dirname,'render-QA.json'),JSON.stringify({rendered_utc:new Date().toISOString(),renderer:'existing sharp/libvips',out},null,2)+'\n');process.stdout.write(JSON.stringify(out,null,2));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
