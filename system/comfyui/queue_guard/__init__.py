"""The only enabled custom extension: queue-safe llama-swap lifecycle."""
import os

from aiohttp import web
from server import PromptServer

from .guard import QueueGuard


server = PromptServer.instance
guard = QueueGuard(server.prompt_queue,
                   os.environ.get('COMFYUI_LIFECYCLE_DIR', '/data/runtime'))


@web.middleware
async def admission(request, handler):
    if request.method != 'POST' or request.path not in ('/prompt', '/api/prompt'):
        return await handler(request)
    if not guard.admit():
        return web.json_response(
            {'error': 'ComfyUI is switching to another GPU backend; retry later.'},
            status=503, headers={'Retry-After': '5'})
    try:
        return await handler(request)
    finally:
        guard.submitted()


server.app.middlewares.append(admission)


@server.routes.get('/local-ai/queue-state')
async def queue_state(request):
    return web.json_response(guard.snapshot())


NODE_CLASS_MAPPINGS = {}
