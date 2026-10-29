"""Protect accepted image jobs and their results during GPU handover."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1] / 'system/comfyui'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = load('queue_guard', ROOT / 'queue_guard/guard.py')
lifecycle = load('lifecycle', ROOT / 'usr/local/libexec/comfyui-lifecycle.py')


class Queue:
    def __init__(self):
        self.mutex = threading.RLock()
        self.history = {}
        self.running = []
        self.pending = []

    def task_done(self, job):
        self.running.clear()
        self.history[job] = {'outputs': {'image': job + '.png'}}

    def get_current_queue(self):
        return self.running[:], self.pending[:]

    def get_history(self, max_items):
        return dict(list(self.history.items())[-max_items:])


class QueueGuardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.queue = Queue()
        self.guard = guard.QueueGuard(self.queue, self.directory.name)

    def test_draining_rejects_new_jobs_but_tracks_already_admitted_post(self):
        self.assertTrue(self.guard.admit())
        self.guard.draining.touch()
        self.assertFalse(self.guard.admit())
        self.assertFalse(lifecycle.idle(self.guard.snapshot()))
        self.guard.submitted()
        self.assertTrue(lifecycle.idle(self.guard.snapshot()))

    def test_pending_and_running_jobs_prevent_stop(self):
        self.guard.draining.touch()
        for field in ('running', 'pending'):
            with self.subTest(field=field):
                getattr(self.queue, field).append('job')
                self.assertFalse(lifecycle.idle(self.guard.snapshot()))
                getattr(self.queue, field).clear()
        self.assertTrue(lifecycle.idle(self.guard.snapshot()))

    def test_latest_twenty_results_survive_restart(self):
        for number in range(25):
            self.queue.task_done(str(number))
        restored = Queue()
        guard.QueueGuard(restored, self.directory.name)
        self.assertEqual(list(restored.history), [str(n) for n in range(5, 25)])
        self.assertEqual(restored.history['24']['outputs']['image'], '24.png')

    def test_finishing_job_cannot_stop_during_history_write(self):
        self.guard.draining.touch()
        original = self.queue.get_history
        def history(max_items):
            self.assertFalse(lifecycle.idle(self.guard.snapshot()))
            return original(max_items)
        self.queue.get_history = history
        self.queue.task_done('completed')
        self.assertTrue(lifecycle.idle(self.guard.snapshot()))

    def test_history_failure_keeps_worker_alive_and_prevents_stop(self):
        self.guard.draining.touch()
        with patch.object(Path, 'write_text', side_effect=OSError('disk full')), self.assertLogs(level='ERROR'):
            self.queue.task_done('first')
        self.assertFalse(lifecycle.idle(self.guard.snapshot()))
        self.queue.task_done('second')
        self.assertTrue(lifecycle.idle(self.guard.snapshot()))
        self.assertIn('first', json.loads(self.guard.history_path.read_text()))


class LifecycleTests(unittest.TestCase):
    def test_failed_checks_and_active_jobs_never_stop_container(self):
        state = dict(draining=True, history_error=None, admitting=0, saving=0, running=1, pending=0)
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(lifecycle, 'running', side_effect=[True, True, True, False]), \
             patch.object(lifecycle, 'urlopen', side_effect=[OSError('unreachable'), io.BytesIO(b'{}'), io.BytesIO(json.dumps(state).encode())]), \
             patch.object(lifecycle.time, 'sleep'), \
             patch.object(lifecycle.subprocess, 'run') as docker:
            lifecycle.stop(Path(directory))
            docker.assert_not_called()

    def test_docker_inspect_failure_does_not_release_gpu_group(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(lifecycle, 'running', side_effect=[subprocess.CalledProcessError(1, 'docker'), False]), \
             patch.object(lifecycle.time, 'sleep'), \
             patch.object(lifecycle.subprocess, 'run') as docker:
            lifecycle.stop(Path(directory))
            docker.assert_not_called()

    def test_stop_requires_idle_grace_after_last_active_job(self):
        busy = dict(draining=True, history_error=None, admitting=0, saving=0, running=1, pending=0)
        idle = dict(busy, running=0)
        now = [0]
        states = iter([idle, busy, idle, idle, idle, idle, idle, idle])
        def response(*args, **kwargs):
            return io.BytesIO(json.dumps(next(states)).encode())
        def advance(seconds):
            now[0] += 1
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(lifecycle, 'running', return_value=True), \
             patch.object(lifecycle, 'urlopen', side_effect=response), \
             patch.object(lifecycle.time, 'monotonic', side_effect=lambda: now[0]), \
             patch.object(lifecycle.time, 'sleep', side_effect=advance), \
             patch.object(lifecycle.subprocess, 'run') as docker:
            lifecycle.stop(Path(directory))
            self.assertEqual(now[0], 7)
            docker.assert_called_once_with(['/usr/bin/docker', 'stop', '--time', '60', lifecycle.CONTAINER], check=True, timeout=90)


if __name__ == '__main__':
    unittest.main()
