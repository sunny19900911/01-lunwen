const fs=require('fs');
const path=require('path');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async()=>{
  const records=[];
  for(const name of ['figure1-compact-CM-UX-modes2-10-13','figure2-compact-SHW3X-modal-weights']){
    const out=path.join(__dirname,name+'.png');
    if(fs.existsSync(out))throw new Error('Refuse overwrite '+out);
    const r=await sharp(path.join(__dirname,name+'.svg'),{density:144}).resize({width:2400}).withMetadata({density:300}).png({compressionLevel:9}).toFile(out);
    records.push({name:name+'.png',width:r.width,height:r.height,bytes:fs.statSync(out).size,density:300});
  }
  fs.writeFileSync(path.join(__dirname,'render-record.json'),JSON.stringify({rendered_utc:new Date().toISOString(),records},null,2)+'\n',{flag:'wx'});
  process.stdout.write(JSON.stringify(records));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
