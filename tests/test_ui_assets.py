import os
import unittest

class TestUIAssets(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.web_dir = os.path.join(self.base_dir, "web")

    def test_index_html_contains_floating_player_elements(self):
        html_path = os.path.join(self.web_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('id="audioCardSentinel"', content)
        self.assertIn('id="audioCard"', content)
        self.assertIn('id="audioFloatingHeader"', content)
        self.assertIn('id="audioStatusBadge"', content)
        self.assertIn('id="audioFloatingTitle"', content)
        self.assertIn('id="btnScrollToTop"', content)
        self.assertIn('id="audioPlayer"', content)
        self.assertIn('class="playback-controls"', content)

    def test_style_css_contains_floating_and_sticky_rules(self):
        css_path = os.path.join(self.web_dir, "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn(".audio-card", content)
        self.assertIn("position: sticky;", content)
        self.assertIn("top: 0;", content)
        self.assertIn(".audio-card.is-floating", content)
        self.assertIn(".audio-floating-header", content)
        self.assertIn(".audio-floating-indicator", content)
        self.assertIn(".btn-scroll-top", content)
        self.assertIn(".audio-controls-row", content)
        self.assertIn(".segment-item.active-playing", content)

    def test_app_js_contains_floating_logic_and_shortcuts(self):
        js_path = os.path.join(self.web_dir, "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("setupFloatingPlayer", content)
        self.assertIn("audioCard", content)
        self.assertIn("audioCardSentinel", content)
        self.assertIn("is-floating", content)
        self.assertIn("highlightActiveSegment", content)
        self.assertIn("btnScrollToTop", content)
        # Check keyboard shortcut handling
        self.assertIn("altKey", content)
        self.assertIn("ctrlKey", content)

if __name__ == "__main__":
    unittest.main()
