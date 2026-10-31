const fs=require('fs');
const path=require('path');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async()=>{
  const name='figure3-SHW3X-same-time-symmetric-decomposition';
  const out=path.join(__dirname,name+'.png');
  if(fs.existsSync(out))throw new Error('Refuse overwrite '+out);
  const m=await sharp(path.join(__dirname,name+'.svg'),{density:144}).resize({width:2400}).withMetadata({density:300}).png({compressionLevel:9}).toFile(out);
  const record={rendered_utc:new Date().toISOString(),PNG:name+'.png',width:m.width,height:m.height,bytes:fs.statSync(out).size,density:300,font:'Microsoft YaHei'};
  fs.writeFileSync(path.join(__dirname,'render-record.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
  process.stdout.write(JSON.stringify(record));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
