import unittest
from gemini_transcriber import GeminiTranscriber

class TestGeminiParser(unittest.TestCase):
    def test_parse_clean_json(self):
        raw = """
        {
          "speakers": ["Speaker 1", "Speaker 2"],
          "segments": [
            {
              "speaker": "Speaker 1",
              "start_time": "00:00:02",
              "end_time": "00:00:07",
              "start_seconds": 2.0,
              "end_seconds": 7.0,
              "text": "Hola, ¿cómo estás?"
            },
            {
              "speaker": "Speaker 2",
              "start_time": "00:00:08",
              "end_time": "00:00:12",
              "start_seconds": 8.0,
              "end_seconds": 12.0,
              "text": "Muy bien, gracias por preguntar."
            }
          ]
        }
        """
        result = GeminiTranscriber.parse_and_validate_transcript(raw)
        self.assertEqual(len(result["speakers"]), 2)
        self.assertIn("Speaker 1", result["speakers"])
        self.assertIn("Speaker 2", result["speakers"])
        self.assertEqual(len(result["segments"]), 2)
        self.assertEqual(result["segments"][0]["text"], "Hola, ¿cómo estás?")
        self.assertEqual(result["segments"][1]["start_seconds"], 8.0)

    def test_parse_markdown_fences(self):
        raw = """```json
        {
          "speakers": ["Speaker 1"],
          "segments": [
            {
              "speaker": "Speaker 1",
              "start_seconds": 1.5,
              "end_seconds": 4.0,
              "text": "Prueba de fenced block"
            }
          ]
        }
        ```"""
        result = GeminiTranscriber.parse_and_validate_transcript(raw)
        self.assertEqual(len(result["segments"]), 1)
        self.assertEqual(result["segments"][0]["start_time"], "00:01")
        self.assertEqual(result["segments"][0]["text"], "Prueba de fenced block")

    def test_time_conversions(self):
        self.assertEqual(GeminiTranscriber.format_seconds(125), "02:05")
        self.assertEqual(GeminiTranscriber.format_seconds(3665), "01:01:05")
        self.assertEqual(GeminiTranscriber.parse_time_to_seconds("02:05"), 125.0)
        self.assertEqual(GeminiTranscriber.parse_time_to_seconds("01:01:05"), 3665.0)

if __name__ == "__main__":
    unittest.main()
