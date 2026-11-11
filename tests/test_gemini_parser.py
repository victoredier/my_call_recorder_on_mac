import os
import json
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

    def test_build_prompt_with_and_without_context(self):
        prompt_no_ctx = GeminiTranscriber.build_prompt(GeminiTranscriber.DEFAULT_PROMPT, None)
        self.assertIn("IDENTIFICADORES:", prompt_no_ctx)
        self.assertNotIn("{speakers_context_section}", prompt_no_ctx)

        prompt_with_ctx = GeminiTranscriber.build_prompt(
            GeminiTranscriber.DEFAULT_PROMPT,
            "Víctor (yo) y Carlos (cliente)"
        )
        self.assertIn("CONTEXTO DE PARTICIPANTES EN ESTA LLAMADA:", prompt_with_ctx)
        self.assertIn("Víctor (yo) y Carlos (cliente)", prompt_with_ctx)
        self.assertNotIn("{speakers_context_section}", prompt_with_ctx)

    def test_list_available_models_fallback(self):
        models = GeminiTranscriber.list_available_models(api_key="")
        self.assertIsInstance(models, list)
        self.assertTrue(len(models) >= 3)
        model_ids = [m["id"] for m in models]
        self.assertIn("gemini-2.0-flash-lite", model_ids)
        self.assertIn("gemini-2.0-flash", model_ids)

    def test_list_available_models_mock_api(self):
        from unittest.mock import patch, MagicMock
        import io

        fake_api_response = {
            "models": [
                {
                    "name": "models/gemini-2.0-flash-lite",
                    "displayName": "Gemini 2.0 Flash Lite",
                    "supportedGenerationMethods": ["generateContent", "countTokens"]
                },
                {
                    "name": "models/gemini-embedding-001",
                    "displayName": "Embedding Model",
                    "supportedGenerationMethods": ["embedContent"]
                },
                {
                    "name": "models/gemini-2.0-flash",
                    "displayName": "Gemini 2.0 Flash",
                    "supportedGenerationMethods": ["generateContent"]
                }
            ]
        }

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(fake_api_response).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp):
            models = GeminiTranscriber.list_available_models(api_key="valid-dummy-key")
            model_ids = [m["id"] for m in models]
            self.assertIn("gemini-2.0-flash-lite", model_ids)
            self.assertIn("gemini-2.0-flash", model_ids)
            # Embeddings model should be excluded
            self.assertNotIn("gemini-embedding-001", model_ids)

if __name__ == "__main__":
    unittest.main()
