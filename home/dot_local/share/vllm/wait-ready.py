#!/usr/bin/env python3
"""Wait for the configured local vLLM model without issuing inference."""
import json,time,urllib.request
started=time.monotonic()
while time.monotonic()-started<540:
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/v1/models',timeout=5) as response:
            data=json.load(response)
        if any(model['id']=='qwen3.8-27b-int8' for model in data.get('data',[])):
            print('Qwen3.8 INT8 vLLM API is ready',flush=True)
            break
    except (OSError,ValueError):
        pass
    time.sleep(5)
else:
    raise SystemExit('vLLM API did not become ready within nine minutes')
