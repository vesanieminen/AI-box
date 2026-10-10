#!/usr/bin/env python3
"""Wait for Ollama and preload the tuned model during service startup."""
import json
import time
import urllib.error
import urllib.request

base = 'http://127.0.0.1:11434'
for attempt in range(60):
    try:
        with urllib.request.urlopen(base + '/api/tags', timeout=2):
            break
    except (OSError, urllib.error.URLError):
        time.sleep(1)
else:
    raise SystemExit('Ollama API did not become available')

payload = json.dumps({'model': 'qwen3.8:3090', 'stream': False, 'keep_alive': -1}).encode()
request = urllib.request.Request(base + '/api/generate', data=payload,
                                 headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(request, timeout=480) as response:
    result = json.load(response)
if result.get('error') or not result.get('done'):
    raise SystemExit('Model preload failed: ' + str(result))
print('qwen3.8:3090 preloaded and kept in memory', flush=True)
