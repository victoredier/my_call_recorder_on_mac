import os
import unittest
from server import CallRecorderHandler
from tests.test_server_api import MockSocket, DummyServer

class TestIconAssets(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(self.base_dir, "assets")
        self.web_dir = os.path.join(self.base_dir, "web")
        self.app_dir = os.path.join(self.base_dir, "Call Recorder.app")

    def test_asset_files_exist(self):
        expected_assets = [
            "app_icon.svg",
            "app_icon.png",
            "app_icon_1024.png",
            "AppIcon.icns",
            "menu_icon.png",
            "menu_icon@2x.png",
            "menu_icon_recording.png",
            "menu_icon_recording@2x.png",
            "menu_icon_paused.png",
            "menu_icon_paused@2x.png",
        ]
        for asset in expected_assets:
            path = os.path.join(self.assets_dir, asset)
            self.assertTrue(os.path.exists(path), f"Asset missing: {asset}")
            self.assertGreater(os.path.getsize(path), 0, f"Asset empty: {asset}")

    def test_web_icons_exist(self):
        expected_web = [
            "icon.svg",
            "favicon.svg",
            "icon.png",
            "favicon.png",
        ]
        for asset in expected_web:
            path = os.path.join(self.web_dir, asset)
            self.assertTrue(os.path.exists(path), f"Web asset missing: {asset}")
            self.assertGreater(os.path.getsize(path), 0, f"Web asset empty: {asset}")

    def test_index_html_has_icon_and_favicon(self):
        html_path = os.path.join(self.web_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('rel="icon" type="image/svg+xml" href="/favicon.svg"', content)
        self.assertIn('brand-logo-img', content)
        self.assertIn('src="/icon.svg"', content)

    def test_server_routes_icon_assets(self):
        endpoints = [
            ("/icon.svg", "image/svg+xml"),
            ("/favicon.svg", "image/svg+xml"),
            ("/icon.png", "image/png"),
            ("/favicon.png", "image/png"),
        ]
        for ep, expected_content_type in endpoints:
            raw_req = f"GET {ep} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode("utf-8")
            sock = MockSocket(raw_req)
            CallRecorderHandler(sock, ("127.0.0.1", 12345), DummyServer())
            output = sock.wfile.getvalue().decode("latin1", errors="replace")

            self.assertIn("HTTP/1.0 200 OK", output)
            self.assertIn(f"Content-Type: {expected_content_type}", output)

    def test_app_bundle_has_app_icon(self):
        if os.path.exists(self.app_dir):
            icns_path = os.path.join(self.app_dir, "Contents", "Resources", "AppIcon.icns")
            plist_path = os.path.join(self.app_dir, "Contents", "Info.plist")
            self.assertTrue(os.path.exists(icns_path), "AppIcon.icns missing in bundle Resources")
            with open(plist_path, "r", encoding="utf-8") as f:
                plist_content = f.read()
            self.assertIn("<key>CFBundleIconFile</key>", plist_content)
            self.assertIn("<string>AppIcon</string>", plist_content)

if __name__ == "__main__":
    unittest.main()
