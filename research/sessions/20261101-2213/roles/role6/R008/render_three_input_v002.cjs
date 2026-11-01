const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async()=>{
 const stem='figure3-three-input-S-profile-v002',out=path.join(__dirname,stem+'.png');
 if(fs.existsSync(out))throw Error('Refusing overwrite '+out);
 const r=await sharp(path.join(__dirname,stem+'.svg'),{density:144}).resize({width:2800})
   .withMetadata({density:300}).png({compressionLevel:9}).toFile(out);
 const record={actual_utc:new Date().toISOString(),file:path.basename(out),width:r.width,height:r.height,dpi:300,bytes:fs.statSync(out).size};
 fs.writeFileSync(path.join(__dirname,'render-record-v002.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
 process.stdout.write(JSON.stringify(record));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
