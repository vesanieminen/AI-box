"""Drain accepted prompts and retain completed jobs across GPU switches."""
import json
import logging
from pathlib import Path
import threading


class QueueGuard:
    def __init__(self, queue, runtime):
        self.queue = queue
        self.runtime = Path(runtime)
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.draining = self.runtime / 'draining'
        self.history_path = self.runtime / 'history.json'
        self.lock = threading.RLock()
        self.admitting = 0
        self.saving = 0
        self.history_error = None
        if self.history_path.exists():
            history = json.loads(self.history_path.read_text())
            if not isinstance(history, dict):
                raise ValueError('Invalid persisted ComfyUI history')
            with queue.mutex:
                queue.history.update(history)
        self.original_task_done = queue.task_done
        queue.task_done = self.task_done

    def admit(self):
        with self.lock:
            if self.draining.exists():
                return False
            self.admitting += 1
            return True

    def submitted(self):
        with self.lock:
            self.admitting -= 1

    def snapshot(self):
        with self.lock:
            running, pending = self.queue.get_current_queue()
            return {'draining': self.draining.exists(),
                    'admitting': self.admitting, 'saving': self.saving,
                    'running': len(running), 'pending': len(pending),
                    'history_error': self.history_error}

    def task_done(self, *args, **kwargs):
        with self.lock:
            self.saving += 1
        try:
            result = self.original_task_done(*args, **kwargs)
            try:
                history = self.queue.get_history(max_items=20)
                temporary = self.history_path.with_suffix('.tmp')
                temporary.write_text(json.dumps(history))
                temporary.replace(self.history_path)
                with self.lock:
                    self.history_error = None
            except Exception as error:
                # Keep the worker alive, but prevent a stop that loses results.
                with self.lock:
                    self.history_error = str(error)
                logging.exception('Cannot persist ComfyUI job history')
            return result
        finally:
            with self.lock:
                self.saving -= 1
