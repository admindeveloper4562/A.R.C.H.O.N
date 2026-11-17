import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from http.server import ThreadingHTTPServer

from apps.web.server import ROUTES, WEB_ROOT, handler_for


class RuntimeDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(WEB_ROOT))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        headers = {key.lower(): value for key, value in response.getheaders()}
        connection.close()
        return response.status, headers, body

    def test_all_dashboard_routes_open_and_reload(self):
        for route in ROUTES:
            status, headers, body = self.get(route)
            self.assertEqual(status, 200, route)
            self.assertEqual(headers["content-type"].split(";", 1)[0], "text/html", route)
            self.assertIn(b"data-page-title", body, route)
            self.assertIn(b"/settings", body, route)

    def test_assets_and_unknown_routes_are_bounded(self):
        for asset in ("/dashboard.css", "/dashboard.js"):
            status, _headers, body = self.get(asset)
            self.assertEqual(status, 200)
            self.assertTrue(body)
        status, _headers, _body = self.get("/not-a-dashboard-route")
        self.assertEqual(status, 404)

    def test_responses_include_browser_hardening_headers(self):
        status, headers, _body = self.get("/")
        self.assertEqual(status, 200)
        self.assertEqual(headers["x-frame-options"], "DENY")
        self.assertIn("frame-ancestors 'none'", headers["content-security-policy"])
        self.assertEqual(headers["cache-control"], "no-store")

    def test_world_overview_is_source_backed_and_date_explicit(self):
        status, _headers, body = self.get("/world")
        self.assertEqual(status, 200)
        self.assertIn(b"data-world-overview", body)
        script = (WEB_ROOT / "dashboard.js").read_text(encoding="utf-8")
        for label in ("Source/published date", "Fetched date", "Event date", "Correction"):
            self.assertIn(label, script)
        self.assertIn("No verified source-backed stories are available.", body.decode())


if __name__ == "__main__":
    unittest.main()
