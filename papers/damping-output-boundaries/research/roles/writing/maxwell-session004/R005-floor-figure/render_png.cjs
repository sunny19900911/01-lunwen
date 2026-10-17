const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const [sharpPath, input, output] = process.argv.slice(2);
if (!sharpPath || !input || !output) throw new Error('Usage: node render_png.cjs SHARP_MODULE INPUT_SVG NEW_PNG');
if (fs.existsSync(output)) throw new Error('Refusing existing PNG output');
const sharp = require(sharpPath);
(async () => {
  await sharp(input, {density:216}).resize({width:2400}).png().toFile(output);
  const meta = await sharp(output).metadata();
  const record={finished_at:new Date().toISOString(),engine:'sharp',sharp_version:sharp.versions.sharp,input:path.resolve(input),output:path.resolve(output),width:meta.width,height:meta.height,sha256:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex'),visual_review:'pending actual view_image'};
  fs.writeFileSync(path.join(path.dirname(output),'run_record_png.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify(record));
})().catch(e=>{console.error(e);process.exitCode=1});
