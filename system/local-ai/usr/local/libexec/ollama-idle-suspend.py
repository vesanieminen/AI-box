#!/usr/bin/env python3
"""Suspend only when both the desktop and AI server have been idle 15 minutes."""
import json
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time

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
                        '( sport = :11434 or sport = :8000 )').strip())


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


def recent_vllm_request():
    result = subprocess.run(
        ['docker', 'logs', '--since', '16m', '--tail', '10000', '--timestamps', 'qwen38-vllm'],
        text=True, capture_output=True, timeout=10)
    if result.returncode:
        if 'No such container' in result.stderr:
            return 0.0
        raise RuntimeError('Unable to check vLLM request activity')
    latest = 0.0
    for line in (result.stdout + result.stderr).splitlines():
        if any('"' + method + ' /' in line for method in ('POST', 'PUT', 'DELETE', 'PATCH')):
            stamp = line.split(' ', 1)[0]
            latest = max(latest, datetime.fromisoformat(stamp.replace('Z', '+00:00')).timestamp())
    return latest


def downloads_active():
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            args = proc.read_bytes().split(b'\0')
            if any(arg.endswith((b'/download-recipes.py', b'/download-extra-after-queue.py')) for arg in args):
                return True
        except (OSError, PermissionError):
            continue
    return False


def inspect(last_activity):
    now = time.time()
    connected = ollama_connected() or downloads_active()
    last_activity = max(last_activity, recent_ollama_request(), recent_vllm_request())
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
                if not ollama_connected() and not downloads_active() and desktop_idle():
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
