#!/usr/bin/env python3
"""Benchmark real uncached Qwen sampling with a fixed set of prompts and seeds."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import threading
import time
from urllib.request import Request, urlopen


def api(base, path, data=None):
    body = None if data is None else json.dumps(data).encode()
    request = Request(base + path, data=body, headers={'Content-Type': 'application/json'})
    with urlopen(request, timeout=600) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workflow', type=Path)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--label', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--warm-runs', type=int, default=3)
    args = parser.parse_args()
    workflow = json.loads(args.workflow.read_text())
    result = {'label': args.label, 'workflow': workflow, 'runs': []}
    # Restart through llama-swap to distinguish model-load time from warm runs.
    api(args.url, '/api/models/unload', {})
    startup = time.monotonic()
    api(args.url, '/comfyui/local-ai/queue-state')
    result['container_start_seconds'] = time.monotonic() - startup
    for index in range(args.warm_runs + 1):
        prompt = json.loads(json.dumps(workflow))
        prompt['7']['inputs']['seed'] = 424200 + index
        prompt['9']['inputs']['filename_prefix'] = 'benchmark/' + args.label
        stopped = threading.Event()
        peaks = {}
        def sample():
            while not stopped.is_set():
                try:
                    output = subprocess.check_output(
                        ['nvidia-smi', '--query-gpu=index,memory.used,utilization.gpu', '--format=csv,noheader,nounits'],
                        text=True, timeout=5)
                    for line in output.splitlines():
                        gpu, memory, utilization = map(int, line.split(','))
                        old = peaks.setdefault(str(gpu), {'memory_mib': 0, 'utilization_percent': 0})
                        old['memory_mib'] = max(old['memory_mib'], memory)
                        old['utilization_percent'] = max(old['utilization_percent'], utilization)
                except (OSError, ValueError, subprocess.SubprocessError):
                    pass
                stopped.wait(.2)
        sampler = threading.Thread(target=sample)
        sampler.start()
        started = time.monotonic()
        try:
            submitted = api(args.url, '/comfyui/prompt', {'prompt': prompt})
            job = submitted['prompt_id']
            deadline = time.monotonic() + 600
            while True:
                history = api(args.url, '/comfyui/history/' + job)
                if job in history:
                    entry = history[job]
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError('Image job took over ten minutes: ' + job)
                time.sleep(.25)
        finally:
            stopped.set()
            sampler.join()
        wall = time.monotonic() - started
        if entry['status']['status_str'] != 'success':
            raise RuntimeError(json.dumps(entry['status']))
        timestamps = {kind: data['timestamp'] for kind, data in entry['status']['messages'] if 'timestamp' in data}
        execution = (timestamps['execution_success'] - timestamps['execution_start']) / 1000
        run = {'kind': 'cold' if index == 0 else 'warm', 'seed': 424200 + index,
               'prompt_id': job, 'execution_seconds': execution, 'wall_seconds': wall,
               'sampled_gpu_peaks': peaks, 'outputs': entry['outputs']}
        result['runs'].append(run)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(run), flush=True)
    warm = [run['execution_seconds'] for run in result['runs'] if run['kind'] == 'warm']
    result['warm_mean_seconds'] = statistics.mean(warm)
    result['warm_median_seconds'] = statistics.median(warm)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('Warm mean:', result['warm_mean_seconds'], 'median:', result['warm_median_seconds'])


if __name__ == '__main__':
    main()
