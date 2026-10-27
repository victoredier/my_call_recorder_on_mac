import os
import tempfile
import unittest
import numpy as np
import soundfile as sf
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

    def test_truncated_json_recovery_user_case(self):
        # Exact pattern reported by the user where JSON cuts off abruptly
        truncated_raw = '{ "speakers": [ "Speaker 1", "Speaker 2" ], "segments": [ { "id": 1, "speaker": "Speaker 1", "start_time": "00:00:00", "end_time": "00:00:01", "start_seconds": 0.0, "end_seconds": 1.0, "text": "es quads." }, { "id": 2, '
        result = GeminiTranscriber.parse_and_validate_transcript(truncated_raw)
        self.assertEqual(len(result["segments"]), 1)
        self.assertEqual(result["segments"][0]["text"], "es quads.")
        self.assertEqual(result["segments"][0]["speaker"], "Speaker 1")
        self.assertTrue(result.get("is_partial"))

    def test_truncated_json_inside_string(self):
        truncated_raw = """
        {
          "speakers": ["Speaker 1"],
          "segments": [
            {
              "speaker": "Speaker 1",
              "start_time": "00:00:00",
              "end_time": "00:00:10",
              "text": "Segmento completo 1"
            },
            {
              "speaker": "Speaker 1",
              "start_time": "00:00:11",
              "end_time": "00:00:20",
              "text": "Este texto fue cortado a la mi
        """
        result = GeminiTranscriber.parse_and_validate_transcript(truncated_raw)
        self.assertEqual(len(result["segments"]), 1)
        self.assertEqual(result["segments"][0]["text"], "Segmento completo 1")
        self.assertTrue(result.get("is_partial"))

    def test_compact_format_parsing(self):
        # New compact prompt format without redundant id and start_seconds
        compact_raw = """
        {
          "speakers": ["Speaker 1", "Speaker 2"],
          "segments": [
            {
              "speaker": "Speaker 1",
              "start_time": "00:00:00",
              "end_time": "00:00:25",
              "text": "Primer párrafo de intervención larga."
            },
            {
              "speaker": "Speaker 2",
              "start_time": "00:00:26",
              "end_time": "00:01:10",
              "text": "Respuesta completa del segundo orador."
            }
          ]
        }
        """
        result = GeminiTranscriber.parse_and_validate_transcript(compact_raw)
        self.assertEqual(len(result["segments"]), 2)
        # Verify auto-computed fields
        self.assertEqual(result["segments"][0]["id"], 1)
        self.assertEqual(result["segments"][0]["start_seconds"], 0.0)
        self.assertEqual(result["segments"][0]["end_seconds"], 25.0)
        self.assertEqual(result["segments"][1]["id"], 2)
        self.assertEqual(result["segments"][1]["start_seconds"], 26.0)
        self.assertEqual(result["segments"][1]["end_seconds"], 70.0)

    def test_audio_optimization(self):
        # Create a stereo 48kHz WAV audio file
        sr = 48000
        duration = 2.0  # 2 seconds
        samples = int(sr * duration)
        stereo_data = np.zeros((samples, 2), dtype=np.float32)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_wav = f.name
        
        try:
            sf.write(temp_wav, stereo_data, sr, subtype="PCM_24")
            transcriber = GeminiTranscriber(api_key="test_key")
            opt_path, mime_type, is_temp, dur = transcriber._prepare_optimized_audio(temp_wav)

            self.assertAlmostEqual(dur, 2.0, places=1)
            self.assertTrue(is_temp)
            self.assertIn(mime_type, ["audio/mp3", "audio/wav"])
            self.assertTrue(os.path.exists(opt_path))

            # Verify optimized audio has 1 channel (mono) and <= 16000 sr
            opt_info = sf.info(opt_path)
            self.assertEqual(opt_info.channels, 1)
            self.assertLessEqual(opt_info.samplerate, 16000)

            # Cleanup
            if is_temp and os.path.exists(opt_path):
                os.remove(opt_path)
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)

if __name__ == "__main__":
    unittest.main()
