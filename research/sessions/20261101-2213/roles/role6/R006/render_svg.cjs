const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async () => {
  const records = [];
  for (const stem of ['figure1-S-along-height-v001', 'figure2-signed-modal-improvement-v001']) {
    const png = path.join(__dirname, stem + '.png');
    if (fs.existsSync(png)) throw new Error('Refusing overwrite: ' + png);
    const r = await sharp(path.join(__dirname, stem + '.svg'), {density:144})
      .resize({width:2800}).withMetadata({density:300})
      .png({compressionLevel:9}).toFile(png);
    records.push({file:path.basename(png),width:r.width,height:r.height,bytes:fs.statSync(png).size,dpi:300});
  }
  fs.writeFileSync(path.join(__dirname,'render-record.json'),
    JSON.stringify({actual_utc:new Date().toISOString(),backend:'SVG + Sharp',records},null,2)+'\n',{flag:'wx'});
  process.stdout.write(JSON.stringify(records));
})().catch(e=>{process.stderr.write(String(e));process.exitCode=1;});
