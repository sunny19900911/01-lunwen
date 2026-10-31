const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async()=>{
  const names=['figure1-actual-CM-UX-modes2-10-13','figure2-SHW3X-Story5-Story12-envelope-weights'];
  const records=[];
  for(const name of names){
    const src=path.join(__dirname,name+'.svg'),out=path.join(__dirname,name+'.png');
    if(fs.existsSync(out))throw new Error('Refuse overwrite: '+out);
    const meta=await sharp(src,{density:144}).resize({width:2400}).withMetadata({density:300}).png({compressionLevel:9}).toFile(out);
    records.push({file:name+'.png',bytes:fs.statSync(out).size,width:meta.width,height:meta.height,density:300});
  }
  const out=path.join(__dirname,'render-record.json');
  fs.writeFileSync(out,JSON.stringify({rendered_utc:new Date().toISOString(),sharp:sharp.versions.sharp,rsvg:sharp.versions.rsvg,font:'Microsoft YaHei',records},null,2)+'\n',{flag:'wx'});
  process.stdout.write(JSON.stringify(records));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
