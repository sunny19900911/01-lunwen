const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs');
(async()=>{
  const records=[];
  for(const name of ['figure1-native-peak-reduction-profile','figure2-Story12-SHW4X-two-anchors']) {
    const src=path.join(__dirname,name+'.svg'),out=path.join(__dirname,name+'.png');
    const meta=await sharp(src,{density:144}).resize({width:name.startsWith('figure1')?1488:1740}).png({compressionLevel:9,palette:true,quality:100}).toFile(out);
    if(fs.statSync(out).size>500000)throw new Error('PNG exceeds 500KB');
    records.push({file:path.basename(out),bytes:fs.statSync(out).size,width:meta.width,height:meta.height,render:'sharp/libvips SVG rasterization'});
  }
  fs.writeFileSync(path.join(__dirname,'render-record.json'),JSON.stringify({rendered_utc:new Date().toISOString(),records},null,2)+'\n');
  process.stdout.write(JSON.stringify(records,null,2));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
