"""测试辅助：本地 fixture HTTP 服务（不联网）。"""
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

FIXTURES = os.path.join(HERE, "fixtures")


def fixture_bytes(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def serve(routes):
    """routes: {path: (status, headers, body) | callable(headers) -> tuple}。

    返回 (base_url, stop)。未知路径返回 404。
    """

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            route = routes.get(self.path.split("?")[0])
            if route is None:
                status, headers, body = 404, {"Content-Type": "text/plain"}, b"not found"
            elif callable(route):
                status, headers, body = route(self.headers)
            else:
                status, headers, body = route
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # 客户端截断读取后提前关闭

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def stop():
        server.shutdown()
        server.server_close()

    return "http://127.0.0.1:%d" % server.server_address[1], stop
