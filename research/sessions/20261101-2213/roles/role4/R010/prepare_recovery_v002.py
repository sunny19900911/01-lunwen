from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent;src=O/'extend_two_inputs_then_form_input_envelope.py';text=src.read_text(encoding='utf-8')
text=text.replace("L=O/'local-cache';L.mkdir(exist_ok=False)","L=O/'local-cache'/'v002';L.mkdir(parents=True,exist_ok=False)")
text=text.replace("input-method-envelope-rules-freeze.json","input-method-envelope-rules-freeze-v002.json")
old="k=data['omega']**2)";new="k=data['omega']**2,V0=(data['s0']*data['omega']**2)@data['B'].T/1000,VZ=(data['Z']*data['omega']**2)@data['B'].T/1000,P0=np.max(abs((data['s0']*data['omega']**2)@data['B'].T/1000),axis=0))";assert text.count(old)==1;text=text.replace(old,new)
out=O/'extend_two_inputs_then_form_input_envelope_v002.py'
with out.open('x',encoding='utf-8') as f:f.write(text)
with (O/'early-failure-and-recovery-v002.json').open('x',encoding='utf-8') as f:json.dump(dict(first_exit=1,stage='first reused prediction block missing V0 namespace; no prediction or target result had been saved',new_target_solves_at_failure=0,old8_arrays_opened_at_failure=False,original_code_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),recovery_code_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),change='provide known baseline V0/VZ/P0 to frozen arithmetic block; use new cache subdirectory and new input freeze filename; no numerical method/threshold change',no_original_bytes_overwritten=True),f,ensure_ascii=False,indent=2);f.write('\n')
