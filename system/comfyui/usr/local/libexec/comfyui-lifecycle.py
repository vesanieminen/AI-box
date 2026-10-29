#!/usr/bin/env python3
"""Start ComfyUI or drain its queue before stopping its Docker container."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.request import urlopen


CONTAINER = 'qwen-image-comfyui'
RUNTIME = Path('/home/vesanieminen/.local/share/comfyui/runtime')
URL = 'http://127.0.0.1:8188/local-ai/queue-state'


def idle(state):
    return (state['draining'] and not state['history_error']
            and all(state[key] == 0 for key in ('admitting', 'saving', 'running', 'pending')))


def running():
    result = subprocess.run(
        ['/usr/bin/docker', 'inspect', '--format', '{{.State.Running}}', CONTAINER],
        text=True, capture_output=True, check=True, timeout=10)
    return result.stdout.strip() == 'true'


def stop(runtime=RUNTIME, url=URL):
    (runtime / 'draining').touch()
    quiet_since = None
    last_log = 0
    while True:
        try:
            if not running():
                return
            with urlopen(url, timeout=5) as response:
                state = json.load(response)
            if idle(state):
                if quiet_since is None:
                    quiet_since = time.monotonic()
                if time.monotonic() - quiet_since >= 5:
                    subprocess.run(['/usr/bin/docker', 'stop', '--time', '60', CONTAINER],
                                   check=True, timeout=90)
                    return
            else:
                quiet_since = None
            message = json.dumps(state)
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            # A failed queue check must never turn into an unconditional stop.
            quiet_since = None
            message = str(error)
        if time.monotonic() - last_log >= 15:
            print('Waiting for ComfyUI to drain: ' + message, flush=True)
            last_log = time.monotonic()
        time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('start', 'stop'))
    args = parser.parse_args()
    if args.action == 'start':
        RUNTIME.joinpath('draining').unlink(missing_ok=True)
        os.execv('/usr/bin/docker', ['docker', 'start', '--attach', CONTAINER])
    else:
        stop()


if __name__ == '__main__':
    main()
