"""Loopback-only static dashboard server with route fallback."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from jarvis_v2.runtime.security import SECURITY_HEADERS


ROUTES = frozenset({
    "/", "/calendar", "/email", "/actions", "/files", "/system",
    "/projects", "/voice", "/activity", "/settings", "/world", "/world/timeline",
})
ASSETS = frozenset({"/dashboard.css", "/dashboard.js", "/index.html"})
WEB_ROOT = Path(__file__).resolve().parent


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serve only the static shell and its known assets."""

    def _rewrite_route(self) -> bool:
        path = urlsplit(self.path).path
        if path in ROUTES:
            self.path = "/index.html"
            return True
        if path in ASSETS:
            return True
        self.send_error(404)
        return False

    def do_GET(self) -> None:
        if self._rewrite_route():
            super().do_GET()

    def do_HEAD(self) -> None:
        if self._rewrite_route():
            super().do_HEAD()

    def end_headers(self) -> None:
        for key, value in SECURITY_HEADERS.items():
            self.send_header(key, value)
        super().end_headers()

    def log_message(self, format: str, *_args: object) -> None:
        return


def handler_for(directory: Path = WEB_ROOT):
    return partial(DashboardHandler, directory=str(directory))


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("dashboard binds to loopback only")
    with ThreadingHTTPServer((host, port), handler_for()) as server:
        server.serve_forever()


if __name__ == "__main__":
    serve()
