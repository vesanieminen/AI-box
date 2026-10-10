#!/usr/bin/env python3
"""Expose the local model to the home LAN, adding gateway auth internally."""
import http.client
import ipaddress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LAN = ipaddress.ip_network('192.168.0.0/24')
KEY = Path.home() / '.local/state/omarchy/local-ai/gateway.key'
HOP = {'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
       'te', 'trailer', 'transfer-encoding', 'upgrade'}


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def verify_request(self, request, client_address):
        return ipaddress.ip_address(client_address[0]) in LAN


class Proxy(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, format, *args):
        pass

    def forward(self):
        self.close_connection = True
        if not self.path.startswith('/'):
            self.send_error(400, 'Expected a relative API path')
            return
        if self.headers.get('Transfer-Encoding'):
            self.send_error(411, 'Use Content-Length for request bodies')
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 0:
                raise ValueError
        except ValueError:
            self.send_error(400, 'Invalid Content-Length')
            return
        upstream = http.client.HTTPConnection('127.0.0.1', 12434, timeout=600)
        started = False
        try:
            key = KEY.read_text().strip()
            upstream.putrequest(self.command, self.path, skip_accept_encoding=True)
            excluded = HOP | {'host', 'authorization', 'x-api-key', 'content-length'}
            excluded.update(v.strip().lower() for v in self.headers.get('Connection', '').split(','))
            for name, value in self.headers.items():
                if name.lower() not in excluded:
                    upstream.putheader(name, value)
            upstream.putheader('Authorization', 'Bearer ' + key)
            upstream.putheader('x-api-key', key)
            upstream.putheader('Content-Length', str(length))
            upstream.putheader('Connection', 'close')
            upstream.endheaders()
            remaining = length
            while remaining:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    raise ConnectionError('Incomplete request body')
                upstream.send(chunk)
                remaining -= len(chunk)
            response = upstream.getresponse()
            self.send_response(response.status, response.reason)
            excluded = HOP.copy()
            excluded.update(v.strip().lower() for v in (response.getheader('Connection') or '').split(','))
            for name, value in response.getheaders():
                if name.lower() not in excluded:
                    self.send_header(name, value)
            self.send_header('Connection', 'close')
            self.end_headers()
            started = True
            if self.command != 'HEAD':
                while chunk := response.read1(65536):
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except (OSError, http.client.HTTPException):
            if not started:
                self.send_error(502, 'Local model gateway is unavailable')
        finally:
            upstream.close()

    do_GET = forward
    do_HEAD = forward
    do_POST = forward
    do_OPTIONS = forward
    do_PUT = forward
    do_PATCH = forward
    do_DELETE = forward


if __name__ == '__main__':
    Server(('192.168.0.189', 12450), Proxy).serve_forever()
