#!/usr/bin/env python3
"""Suspend only when both the desktop and AI server have been idle 15 minutes."""
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

IDLE_SECONDS = 900
DESKTOP_STATE = Path('/home/vesanieminen/.local/state/ollama/desktop-idle.json')
STAY_AWAKE = Path('/home/vesanieminen/.local/state/omarchy/indicators/stay-awake')


def command(*args):
    return subprocess.check_output(args, text=True, timeout=10)


def desktop_idle():
    if STAY_AWAKE.exists():
        return False
    # Require fresh desktop evidence for graphical sessions. Before login,
    # there is no desktop activity, but the Ollama/startup timer still applies.
    for line in command('loginctl', 'list-sessions', '--no-legend').splitlines():
        fields = line.split()
        if not fields:
            continue
        info = dict(item.split('=', 1) for item in command(
            'loginctl', 'show-session', fields[0], '-p', 'Type', '-p', 'Class',
            '-p', 'User', '-p', 'IdleHint', '-p', 'Remote').splitlines())
        if info.get('Class') != 'user':
            continue
        if info.get('User') != '1000' or info.get('Remote') == 'yes':
            return False
        if info.get('Type') in ('wayland', 'x11'):
            try:
                state = json.loads(DESKTOP_STATE.read_text())
                if state.get('idle') is not True or not 0 <= time.time() - state['at'] <= 60:
                    return False
            except (OSError, ValueError, KeyError, TypeError):
                return False
        elif info.get('IdleHint') != 'yes':
            return False
    return True


def ollama_connected():
    # Conservatively count any established client connection, even if it is
    # idle keep-alive. This protects long streaming and queued requests.
    return bool(command('ss', '-Htn', 'state', 'established',
                        '( sport = :11434 or sport = :5800 or sport = :5801 or sport = :5802 or sport = :5803 or sport = :5804 or sport = :5805 or sport = :5806 or sport = :5807 or sport = :5808 or sport = :5810 or sport = :5811 or sport = :5812 or sport = :5813 )').strip())


def swap_busy():
    state = command('systemctl', 'show', 'llama-swap.service',
                    '--property=ActiveState', '--value').strip()
    if state == 'inactive':
        # Ollama can be selected manually while llama-swap is stopped.
        return False
    if state not in ('active', 'activating', 'deactivating'):
        raise RuntimeError('Unable to verify llama-swap service state')
    # Model discovery and UI/log streams are not inference activity. Read
    # model loading state and the initial snapshot of in-flight API requests.
    with urlopen('http://127.0.0.1:8000/running', timeout=5) as response:
        models = json.load(response)['running']
    if any(model['state'] in ('starting', 'stopping') for model in models):
        return True
    with urlopen('http://127.0.0.1:8000/api/events', timeout=5) as response:
        for _ in range(64):
            line = response.readline(1024 * 1024)
            if not line:
                break
            if not line.startswith(b'data:'):
                continue
            event = json.loads(line[5:])
            if event['type'] == 'inflight':
                snapshot = json.loads(event['data'])
                if snapshot['operation'] == 'snapshot':
                    return bool(snapshot.get('requests'))
    raise RuntimeError('Unable to verify llama-swap in-flight requests')


def recent_swap_request():
    result = subprocess.run(
        ['journalctl', '-u', 'llama-swap.service', '--since', '-16 minutes',
         '--no-pager', '-o', 'json', '--grep',
         r'Request .*"((POST|PUT|DELETE|PATCH) /(v1/|api/models/|api/profiles/)|GET /upstream/[^ ]+/ HTTP)'],
        text=True, capture_output=True, timeout=10)
    if result.returncode == 1 and not result.stdout.strip() and not result.stderr.strip():
        return 0.0
    if result.returncode:
        raise RuntimeError('Unable to check llama-swap request activity')
    return max((int(json.loads(line)['__REALTIME_TIMESTAMP']) / 1_000_000
                for line in result.stdout.splitlines()), default=0.0)


def recent_ollama_request():
    # Count completed API operations, not periodic model/health discovery.
    result = subprocess.run(
        ['journalctl', '-u', 'ollama.service', '--since', '-16 minutes',
         '--no-pager', '-o', 'json', '--grep', r'\[GIN\].* (POST|PUT|DELETE|PATCH) '],
        text=True, capture_output=True, timeout=10)
    # journalctl --grep exits 1 when there are no matching records. That is
    # the expected idle case, not a failed activity check. Preserve actual
    # failures (including permission diagnostics) as errors that block sleep.
    if result.returncode == 1 and not result.stdout.strip() and not result.stderr.strip():
        return 0.0
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, result.args,
                                            result.stdout, result.stderr)
    output = result.stdout
    latest = 0.0
    for line in output.splitlines():
        entry = json.loads(line)
        latest = max(latest, int(entry['__REALTIME_TIMESTAMP']) / 1_000_000)
    return latest


def downloads_active():
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            args = proc.read_bytes().split(b'\0')
            names = [arg.rsplit(b'/', 1)[-1] for arg in args]
            if names and names[0] == b'docker':
                if b'pull' in args[1:3] or (b'compose' in args and b'create' in args):
                    return True
            if b'hf' in names and b'download' in args:
                return True
            if names and names[0] == b'ollama' and b'pull' in args[1:3]:
                return True
        except (OSError, PermissionError):
            continue
    return False


def inspect(last_activity):
    now = time.time()
    connected = ollama_connected() or swap_busy() or downloads_active()
    last_activity = max(last_activity, recent_ollama_request(), recent_swap_request())
    if connected:
        last_activity = now
    desktop = desktop_idle()
    return last_activity, {'desktop_idle': desktop, 'ollama_connected': connected,
                           'ollama_idle_seconds': max(0, int(now - last_activity)),
                           'would_suspend': desktop and not connected and now - last_activity >= IDLE_SECONDS}


def main():
    last_activity = time.time()
    if '--check' in sys.argv:
        # Read-only diagnosis using recent API activity; no suspend is issued.
        _, status = inspect(time.time() - IDLE_SECONDS)
        print(json.dumps(status))
        return
    previous_clock_gap = time.clock_gettime(time.CLOCK_BOOTTIME) - time.monotonic()
    print('Guard started: 15 minutes of desktop and AI server inactivity required', flush=True)
    while True:
        try:
            gap = time.clock_gettime(time.CLOCK_BOOTTIME) - time.monotonic()
            if gap - previous_clock_gap > 1:
                last_activity = time.time()
                print('Resumed: resetting Ollama idle grace period', flush=True)
            previous_clock_gap = gap
            last_activity, status = inspect(last_activity)
            if status['would_suspend']:
                # Repeat the connection check immediately before requesting sleep.
                if not ollama_connected() and not swap_busy() and not downloads_active() and desktop_idle():
                    print('Desktop and AI server idle for 15 minutes; requesting suspend', flush=True)
                    subprocess.run(['systemctl', 'suspend'], check=True, timeout=30)
                last_activity = time.time()
        except Exception as error:
            # Any inability to verify activity prevents sleep.
            last_activity = time.time()
            print(f'Idle check failed; staying awake: {error}', flush=True)
        time.sleep(15)


if __name__ == '__main__':
    main()
