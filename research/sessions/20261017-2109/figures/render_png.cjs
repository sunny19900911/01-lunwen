const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const sharp = require(process.argv[2] || 'sharp');
const names = ['01_native_energy_ratio', '02_device_coverage_by_story'];
(async () => {
  const records = [];
  for (const name of names) {
    const target = path.join(__dirname, name + '.png');
    await sharp(path.join(__dirname, name + '.svg'), { density: 144 })
      .resize({ width: 2000 }).png().toFile(target);
    const meta = await sharp(target).metadata();
    records.push({ file: name + '.png', width: meta.width, height: meta.height,
      sha256: crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex') });
  }
  fs.writeFileSync(path.join(__dirname, 'rendering-verification.json'),
    JSON.stringify({ records, rendered: true, visual_review: 'record separately after viewing' }, null, 2) + '\n');
  console.log(JSON.stringify(records));
})().catch(error => { console.error(error); process.exitCode = 1; });
