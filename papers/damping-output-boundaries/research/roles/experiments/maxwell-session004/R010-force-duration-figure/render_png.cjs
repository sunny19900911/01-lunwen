const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const sharp=require('C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const input=path.join(__dirname,'force_duration_examples.svg');
const output=path.join(__dirname,'force_duration_examples.png');
if(fs.existsSync(output))throw new Error('Refusing existing frozen PNG');
(async()=>{
  await sharp(input,{density:216}).resize({width:2600}).png().toFile(output);
  const meta=await sharp(output).metadata();
  const record={finished_utc:new Date().toISOString(),engine:'sharp',sharp_version:sharp.versions.sharp,command_argv:process.argv,
    input,output,width:meta.width,height:meta.height,sha256:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex'),exit_code:0,visual_QA:'pending actual view_image'};
  fs.writeFileSync(path.join(__dirname,'run_record_png.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify(record));
})().catch(e=>{console.error(e);process.exitCode=1;});
