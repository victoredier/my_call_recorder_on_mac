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

    def test_segment_transcription_ui_assets(self):
        html_path = os.path.join(self.web_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="btnOpenSegmentModal"', html)
        self.assertIn('id="btnAudioCardSegment"', html)
        self.assertIn('id="btnTranscriptHeaderSegment"', html)
        self.assertIn('id="segmentModal"', html)
        self.assertIn('id="inputSegmentStart"', html)
        self.assertIn('id="inputSegmentEnd"', html)
        self.assertIn('id="btnExecuteSegmentTranscribe"', html)
        self.assertIn('id="btnPreviewSegmentAudio"', html)

        css_path = os.path.join(self.web_dir, "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".btn-segment", css)
        self.assertIn(".btn-audio-segment", css)
        self.assertIn(".segment-range-picker", css)
        self.assertIn(".segment-preview-box", css)
        self.assertIn(".input-time", css)

        js_path = os.path.join(self.web_dir, "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("openSegmentModal", js)
        self.assertIn("closeSegmentModal", js)
        self.assertIn("executeSegmentTranscription", js)
        self.assertIn("parseTimeString", js)
        self.assertIn("updateSegmentDurationCalc", js)
        self.assertIn("/api/meetings/${selectedMeeting.id}/transcribe-segment", js)

    def test_search_replace_and_replacements_ui_assets(self):
        html_path = os.path.join(self.web_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # HTML elements check
        self.assertIn('id="btnReplacementsModal"', html)
        self.assertIn('id="btnToggleSearchReplace"', html)
        self.assertIn('id="searchReplaceBar"', html)
        self.assertIn('id="srSearchInput"', html)
        self.assertIn('id="srReplaceInput"', html)
        self.assertIn('id="srMatchCounter"', html)
        self.assertIn('id="btnSrPrev"', html)
        self.assertIn('id="btnSrNext"', html)
        self.assertIn('id="btnSrReplaceOne"', html)
        self.assertIn('id="btnSrReplaceAll"', html)
        self.assertIn('id="btnSrSaveToCentral"', html)
        self.assertIn('id="replacementsAlertBanner"', html)
        self.assertIn('id="btnApplyAllDetectedRep"', html)
        self.assertIn('id="replacementsModal"', html)
        self.assertIn('id="inputNewRepFind"', html)
        self.assertIn('id="inputNewRepReplace"', html)
        self.assertIn('id="btnAddNewReplacement"', html)

        # CSS checks
        css_path = os.path.join(self.web_dir, "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".search-replace-bar", css)
        self.assertIn(".sr-badge-counter", css)
        self.assertIn(".replacements-alert-banner", css)
        self.assertIn(".rep-chip", css)
        self.assertIn(".rep-form-card", css)
        self.assertIn(".segment-item.sr-has-match", css)
        self.assertIn(".segment-item.sr-active-match", css)

        # JS checks
        js_path = os.path.join(self.web_dir, "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("buildSearchRegex", js)
        self.assertIn("toggleSearchReplace", js)
        self.assertIn("performSearch", js)
        self.assertIn("replaceOneMatch", js)
        self.assertIn("replaceAllMatches", js)
        self.assertIn("saveCurrentSearchToCentral", js)
        self.assertIn("checkDetectedReplacements", js)
        self.assertIn("applyAllDetectedReplacements", js)
        self.assertIn("openReplacementsModal", js)
        self.assertIn("closeReplacementsModal", js)
        self.assertIn("/api/replacements", js)

    def test_models_and_participants_ui_assets(self):
        html_path = os.path.join(self.web_dir, "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn('id="inputParticipantsContext"', html)
        self.assertIn('id="btnRefreshModels"', html)
        self.assertIn('id="btnConfigRefreshModels"', html)
        self.assertIn('id="segmentParticipantsContext"', html)
        self.assertIn('gemini-2.0-flash-lite', html)

        css_path = os.path.join(self.web_dir, "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn(".context-toolbar-row", css)
        self.assertIn(".context-input-wrapper", css)
        self.assertIn(".input-context", css)

        js_path = os.path.join(self.web_dir, "app.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("fetchAvailableModels", js)
        self.assertIn("updateModelSelectOptions", js)
        self.assertIn("speakers_context", js)
        self.assertIn("/api/gemini/models", js)

if __name__ == "__main__":
    unittest.main()
