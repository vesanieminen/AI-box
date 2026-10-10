"""Protect inference/loading while allowing idle dashboards to sleep."""
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

path = Path(__file__).resolve().parents[1] / 'system/local-ai/usr/local/libexec/ollama-idle-suspend.py'
spec = importlib.util.spec_from_file_location('idle_guard', path)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def response(payload):
    return io.BytesIO(json.dumps(payload).encode())


def events(requests):
    frames = [{'type': 'modelStatus', 'data': '{}'},
              {'type': 'inflight', 'data': json.dumps({'operation': 'snapshot', 'requests': requests})}]
    return io.BytesIO(b''.join(b'data: ' + json.dumps(frame).encode() + b'\n\n' for frame in frames))


class ActivityTests(unittest.TestCase):
    def setUp(self):
        service = patch.object(guard, 'command', return_value='active\n')
        service.start()
        self.addCleanup(service.stop)

    def test_stopped_swap_allows_manual_ollama_idle_policy(self):
        with patch.object(guard, 'command', return_value='inactive\n'), \
             patch.object(guard, 'urlopen') as urlopen:
            self.assertFalse(guard.swap_busy())
            urlopen.assert_not_called()

    def test_failed_service_blocks_suspend(self):
        with patch.object(guard, 'command', return_value='failed\n'):
            with self.assertRaises(RuntimeError):
                guard.swap_busy()

    def test_loading_and_stopping_block_suspend(self):
        for state in ('starting', 'stopping'):
            with self.subTest(state=state), patch.object(guard, 'urlopen', return_value=response({'running': [{'state': state}]})):
                self.assertTrue(guard.swap_busy())

    def test_loaded_idle_model_does_not_block_suspend(self):
        with patch.object(guard, 'urlopen', side_effect=[response({'running': [{'state': 'ready'}]}), events([])]):
            self.assertFalse(guard.swap_busy())

    def test_queued_or_streaming_inference_blocks_suspend(self):
        with patch.object(guard, 'urlopen', side_effect=[response({'running': []}), events([{'id': '1'}])]):
            self.assertTrue(guard.swap_busy())

    def test_missing_activity_snapshot_is_an_error(self):
        with patch.object(guard, 'urlopen', side_effect=[response({'running': []}), io.BytesIO(b'')]):
            with self.assertRaises(RuntimeError):
                guard.swap_busy()

    def test_unavailable_swap_is_an_error(self):
        with patch.object(guard, 'urlopen', side_effect=OSError('unavailable')):
            with self.assertRaises(OSError):
                guard.swap_busy()

    def test_ui_port_does_not_count_as_inference_connection(self):
        with patch.object(guard, 'command', return_value='') as command:
            self.assertFalse(guard.ollama_connected())
            selector = command.call_args.args[-1]
            self.assertNotIn(':8000', selector)
            self.assertIn(':5800', selector)
            self.assertIn(':5801', selector)
            self.assertIn(':11434', selector)
            self.assertIn(':5806', selector)
            self.assertIn(':5813', selector)

    def test_standard_model_and_runtime_downloads_block_suspend(self):
        for argv in (b'/usr/bin/docker\0pull\0image\0',
                     b'/usr/bin/docker\0compose\0-f\0compose.yaml\0create\0',
                     b'/usr/bin/python3\0/usr/bin/hf\0download\0model\0',
                     b'/usr/bin/ollama\0pull\0model\0'):
            proc = Mock()
            proc.read_bytes.return_value = argv
            with self.subTest(argv=argv), patch.object(guard, 'Path') as path:
                path.return_value.glob.return_value = [proc]
                self.assertTrue(guard.downloads_active())

    def test_read_only_cli_commands_do_not_count_as_downloads(self):
        for argv in (b'/usr/bin/docker\0stats\0',
                     b'/usr/bin/docker\0compose\0config\0',
                     b'/usr/bin/hf\0--help\0'):
            proc = Mock()
            proc.read_bytes.return_value = argv
            with self.subTest(argv=argv), patch.object(guard, 'Path') as path:
                path.return_value.glob.return_value = [proc]
                self.assertFalse(guard.downloads_active())

    def test_idle_desktop_and_idle_models_allow_suspend(self):
        with patch.object(guard.time, 'time', return_value=2000), \
             patch.object(guard, 'ollama_connected', return_value=False), \
             patch.object(guard, 'swap_busy', return_value=False), \
             patch.object(guard, 'downloads_active', return_value=False), \
             patch.object(guard, 'desktop_idle', return_value=True), \
             patch.object(guard, 'recent_ollama_request', return_value=0), \
             patch.object(guard, 'recent_swap_request', return_value=0):
            _, status = guard.inspect(1000)
            self.assertTrue(status['would_suspend'])

    def test_completed_inference_resets_idle_deadline(self):
        with patch.object(guard.time, 'time', return_value=2000), \
             patch.object(guard, 'ollama_connected', return_value=False), \
             patch.object(guard, 'swap_busy', return_value=False), \
             patch.object(guard, 'downloads_active', return_value=False), \
             patch.object(guard, 'desktop_idle', return_value=True), \
             patch.object(guard, 'recent_ollama_request', return_value=0), \
             patch.object(guard, 'recent_swap_request', return_value=1990):
            _, status = guard.inspect(1000)
            self.assertFalse(status['would_suspend'])
            self.assertEqual(status['ollama_idle_seconds'], 10)


if __name__ == '__main__':
    unittest.main()
