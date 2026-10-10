#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
base=Path(__file__).parent
config=json.loads((base/'server-config.json').read_text())
image=config.get('image_digest',config['image_tag'])
command=['docker','run','-d','--name',config['container_name'],'--restart','no','--user','1000:1000','--init','--network','host','--device','nvidia.com/gpu=all','--shm-size','8g','--security-opt','no-new-privileges','--cap-drop','ALL']
for key,value in config['env'].items():command+=['--env',f'{key}={value}']
model_dir=config.get('model_dir','qwen3.8-27b-int8')
if '/' in model_dir or model_dir in ('','.','..'):raise ValueError('Invalid model directory')
for source,target,readonly in [('models/'+model_dir,'/models/'+model_dir,True),('cache/vllm','/cache/vllm',False),('cache/triton','/cache/triton',False),('cache/huggingface','/cache/huggingface',False)]:
    command+=['--mount',f'type=bind,src={base/source},dst={target}'+(',readonly' if readonly else '')]
command+=[image]+config['args']
subprocess.run(command,check=True)
