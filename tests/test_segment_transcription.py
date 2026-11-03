import os
import io
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import soundfile as sf

from gemini_transcriber import GeminiTranscriber
from storage_manager import StorageManager
from server import CallRecorderHandler

class MockSocket:
    def __init__(self, data=b""):
        self.rfile = io.BytesIO(data)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "b" in mode:
            if "r" in mode:
                return self.rfile
            elif "w" in mode:
                return self.wfile
        return self.rfile

    def sendall(self, data):
        self.wfile.write(data)

class DummyServer:
    pass

class TestSegmentTranscription(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = StorageManager(base_path=self.test_dir)
        CallRecorderHandler.storage_manager = self.storage

        # Create dummy wav (10 seconds long)
        self.dummy_wav_path = os.path.join(self.test_dir, "test_audio.wav")
        self._create_dummy_wav(self.dummy_wav_path, duration_sec=10.0, sample_rate=16000)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_dummy_wav(self, path, duration_sec=10.0, sample_rate=16000):
        samples = int(duration_sec * sample_rate)
        data = np.zeros(samples, dtype=np.float32)
        sf.write(path, data, sample_rate)

    def _run_request(self, method, path, headers=None, body=b""):
        if headers is None:
            headers = {}
        headers_lines = [f"{k}: {v}" for k, v in headers.items()]
        if body and "Content-Length" not in headers:
            headers_lines.append(f"Content-Length: {len(body)}")

        raw_req = f"{method} {path} HTTP/1.1\r\n" + "\r\n".join(headers_lines) + "\r\n\r\n"
        req_bytes = raw_req.encode("utf-8") + body

        sock = MockSocket(req_bytes)
        try:
            CallRecorderHandler(sock, ("127.0.0.1", 12345), DummyServer())
        except Exception:
            pass

        output = sock.wfile.getvalue()
        parts = output.split(b"\r\n\r\n", 1)
        header_part = parts[0].decode("utf-8", errors="ignore")
        body_part = parts[1] if len(parts) > 1 else b""
        status_line = header_part.splitlines()[0] if header_part else ""
        return status_line, header_part, body_part

    # --- 1. GeminiTranscriber.transcribe_segment Tests ---

    def test_transcribe_segment_validation_errors(self):
        transcriber = GeminiTranscriber(api_key="fake-test-key")

        # Start time >= total duration (audio is 10s)
        with self.assertRaises(ValueError) as ctx:
            transcriber.transcribe_segment(self.dummy_wav_path, start_seconds=15.0, end_seconds=18.0)
        self.assertIn("no puede ser mayor o igual a la duración total", str(ctx.exception))

        # End time <= start time
        with self.assertRaises(ValueError) as ctx:
            transcriber.transcribe_segment(self.dummy_wav_path, start_seconds=5.0, end_seconds=3.0)
        self.assertIn("debe ser posterior al tiempo de inicio", str(ctx.exception))

        # Slice too short (< 0.5s)
        with self.assertRaises(ValueError) as ctx:
            transcriber.transcribe_segment(self.dummy_wav_path, start_seconds=2.0, end_seconds=2.2)
        self.assertIn("debe durar al menos 1 segundo", str(ctx.exception))

    @patch.object(GeminiTranscriber, "transcribe_audio")
    def test_transcribe_segment_timestamp_offsetting(self, mock_transcribe_audio):
        # Mock Gemini returning segments relative to the 3-second slice
        mock_transcribe_audio.return_value = {
            "speakers": ["Speaker 1", "Speaker 2"],
            "speaker_mapping": {"Speaker 1": "Speaker 1", "Speaker 2": "Speaker 2"},
            "segments": [
                {
                    "id": 1,
                    "speaker": "Speaker 1",
                    "start_time": "00:00",
                    "end_time": "00:02",
                    "start_seconds": 0.0,
                    "end_seconds": 2.0,
                    "text": "Hola mundo en segmento"
                },
                {
                    "id": 2,
                    "speaker": "Speaker 2",
                    "start_time": "00:02",
                    "end_time": "00:03",
                    "start_seconds": 2.0,
                    "end_seconds": 3.0,
                    "text": "Respuesta en segmento"
                }
            ]
        }

        transcriber = GeminiTranscriber(api_key="fake-test-key")
        # Transcribe from second 4.0 to second 7.0
        result = transcriber.transcribe_segment(self.dummy_wav_path, start_seconds=4.0, end_seconds=7.0)

        self.assertTrue(result["is_segment"])
        self.assertEqual(result["segment_bounds"]["start_seconds"], 4.0)
        self.assertEqual(result["segment_bounds"]["end_seconds"], 7.0)

        # Check that segment timestamps were offset by 4.0 seconds
        segments = result["segments"]
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]["start_seconds"], 4.0)
        self.assertEqual(segments[0]["end_seconds"], 6.0)
        self.assertEqual(segments[0]["start_time"], "00:04")
        self.assertEqual(segments[0]["end_time"], "00:06")

        self.assertEqual(segments[1]["start_seconds"], 6.0)
        self.assertEqual(segments[1]["end_seconds"], 7.0)
        self.assertEqual(segments[1]["start_time"], "00:06")
        self.assertEqual(segments[1]["end_time"], "00:07")

    @patch.object(GeminiTranscriber, "transcribe_audio")
    def test_transcribe_segment_empty_speech_warning(self, mock_transcribe_audio):
        mock_transcribe_audio.return_value = {
            "speakers": [],
            "speaker_mapping": {},
            "segments": []
        }

        transcriber = GeminiTranscriber(api_key="fake-test-key")
        result = transcriber.transcribe_segment(self.dummy_wav_path, start_seconds=1.0, end_seconds=3.0)

        self.assertTrue(result["is_segment"])
        self.assertEqual(len(result["segments"]), 0)
        self.assertIn("No se detectó diálogo", result.get("warning", ""))

    # --- 2. StorageManager.merge_transcript_segment Tests ---

    def test_merge_segment_into_empty_meeting(self):
        m = self.storage.create_meeting(name="Llamada Segmento Inicial")
        self._create_dummy_wav(m["audio_path"], duration_sec=10.0)
        self.storage.finalize_recording(m["meeting_dir"])

        segment_tr = {
            "speakers": ["Speaker 1"],
            "speaker_mapping": {"Speaker 1": "Víctor"},
            "segments": [
                {
                    "id": 1,
                    "speaker": "Víctor",
                    "start_time": "00:02",
                    "end_time": "00:05",
                    "start_seconds": 2.0,
                    "end_seconds": 5.0,
                    "text": "Frase en segmento"
                }
            ]
        }

        updated = self.storage.merge_transcript_segment(
            meeting_id=m["id"],
            segment_transcript=segment_tr,
            start_seconds=2.0,
            end_seconds=5.0,
            mode="merge"
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated["status"], "transcribed")
        self.assertEqual(len(updated["transcript"]["segments"]), 1)
        self.assertEqual(updated["transcript"]["segments"][0]["text"], "Frase en segmento")
        self.assertEqual(updated["transcript"]["segments"][0]["start_seconds"], 2.0)

    def test_merge_segment_preserving_non_overlapping_segments(self):
        m = self.storage.create_meeting(name="Llamada con Transcripción Previa")
        self._create_dummy_wav(m["audio_path"], duration_sec=10.0)
        self.storage.finalize_recording(m["meeting_dir"])

        # Initial full transcript with 3 segments: [0-2s], [2-6s], [6-10s]
        initial_tr = {
            "speakers": ["Speaker 1", "Speaker 2"],
            "speaker_mapping": {"Speaker 1": "Alice", "Speaker 2": "Bob"},
            "segments": [
                {
                    "id": 1,
                    "speaker": "Alice",
                    "start_time": "00:00",
                    "end_time": "00:02",
                    "start_seconds": 0.0,
                    "end_seconds": 2.0,
                    "text": "Segmento antes"
                },
                {
                    "id": 2,
                    "speaker": "Bob",
                    "start_time": "00:02",
                    "end_time": "00:06",
                    "start_seconds": 2.0,
                    "end_seconds": 6.0,
                    "text": "Segmento viejo a reemplazar"
                },
                {
                    "id": 3,
                    "speaker": "Alice",
                    "start_time": "00:06",
                    "end_time": "00:10",
                    "start_seconds": 6.0,
                    "end_seconds": 10.0,
                    "text": "Segmento después"
                }
            ]
        }
        self.storage.save_transcript(m["id"], initial_tr)

        # Transcribe replacement segment from 2.0 to 6.0
        replacement_tr = {
            "speakers": ["Speaker 3"],
            "speaker_mapping": {"Speaker 3": "Charlie"},
            "segments": [
                {
                    "id": 1,
                    "speaker": "Charlie",
                    "start_time": "00:02",
                    "end_time": "00:04",
                    "start_seconds": 2.0,
                    "end_seconds": 4.0,
                    "text": "Nuevo segmento parte 1"
                },
                {
                    "id": 2,
                    "speaker": "Charlie",
                    "start_time": "00:04",
                    "end_time": "00:06",
                    "start_seconds": 4.0,
                    "end_seconds": 6.0,
                    "text": "Nuevo segmento parte 2"
                }
            ]
        }

        updated = self.storage.merge_transcript_segment(
            meeting_id=m["id"],
            segment_transcript=replacement_tr,
            start_seconds=2.0,
            end_seconds=6.0,
            mode="merge"
        )

        segments = updated["transcript"]["segments"]
        self.assertEqual(len(segments), 4)

        # Segment 1 (original before)
        self.assertEqual(segments[0]["id"], 1)
        self.assertEqual(segments[0]["text"], "Segmento antes")

        # Segment 2 (new replacement 1)
        self.assertEqual(segments[1]["id"], 2)
        self.assertEqual(segments[1]["text"], "Nuevo segmento parte 1")
        self.assertEqual(segments[1]["speaker"], "Charlie")

        # Segment 3 (new replacement 2)
        self.assertEqual(segments[2]["id"], 3)
        self.assertEqual(segments[2]["text"], "Nuevo segmento parte 2")

        # Segment 4 (original after)
        self.assertEqual(segments[3]["id"], 4)
        self.assertEqual(segments[3]["text"], "Segmento después")

        # Verify speakers merged
        self.assertIn("Charlie", updated["transcript"]["speakers"])
        self.assertIn("Alice", updated["transcript"]["speakers"])

    def test_merge_segment_replace_mode(self):
        m = self.storage.create_meeting(name="Llamada Reemplazar Todo")
        self._create_dummy_wav(m["audio_path"], duration_sec=10.0)
        self.storage.finalize_recording(m["meeting_dir"])

        initial_tr = {
            "speakers": ["Speaker 1"],
            "segments": [
                {"id": 1, "speaker": "Speaker 1", "start_seconds": 0.0, "end_seconds": 5.0, "text": "Viejo 1"},
                {"id": 2, "speaker": "Speaker 1", "start_seconds": 5.0, "end_seconds": 10.0, "text": "Viejo 2"}
            ]
        }
        self.storage.save_transcript(m["id"], initial_tr)

        new_tr = {
            "speakers": ["Speaker 2"],
            "segments": [
                {"id": 1, "speaker": "Speaker 2", "start_seconds": 3.0, "end_seconds": 6.0, "text": "Solo este tramo"}
            ]
        }

        updated = self.storage.merge_transcript_segment(
            meeting_id=m["id"],
            segment_transcript=new_tr,
            start_seconds=3.0,
            end_seconds=6.0,
            mode="replace"
        )

        segments = updated["transcript"]["segments"]
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]["text"], "Solo este tramo")

    # --- 3. Server API endpoint Tests ---

    @patch.object(GeminiTranscriber, "transcribe_segment")
    def test_api_transcribe_segment_endpoint(self, mock_transcribe_seg):
        m = self.storage.create_meeting(name="Reunión API Segmento")
        self._create_dummy_wav(m["audio_path"], duration_sec=10.0)
        self.storage.finalize_recording(m["meeting_dir"])

        mock_transcribe_seg.return_value = {
            "speakers": ["Speaker 1"],
            "speaker_mapping": {"Speaker 1": "Speaker 1"},
            "segments": [
                {
                    "id": 1,
                    "speaker": "Speaker 1",
                    "start_time": "00:01",
                    "end_time": "00:03",
                    "start_seconds": 1.0,
                    "end_seconds": 3.0,
                    "text": "Transcripción vía API"
                }
            ],
            "is_segment": True,
            "segment_bounds": {
                "start_seconds": 1.0,
                "end_seconds": 3.0,
                "start_time": "00:01",
                "end_time": "00:03",
                "duration_seconds": 2.0
            }
        }

        body = json.dumps({
            "start_seconds": "00:01",
            "end_seconds": "00:03",
            "gemini_model": "gemini-2.5-flash",
            "merge_mode": "merge"
        }).encode("utf-8")

        status_line, headers, resp_body = self._run_request(
            "POST",
            f"/api/meetings/{m['id']}/transcribe-segment",
            headers={"Content-Type": "application/json"},
            body=body
        )

        self.assertIn("200", status_line)
        res_data = json.loads(resp_body.decode("utf-8"))
        self.assertTrue(res_data["success"])
        self.assertEqual(res_data["segment"]["start_seconds"], 1.0)
        self.assertEqual(res_data["segment"]["end_seconds"], 3.0)
        self.assertEqual(len(res_data["meeting"]["transcript"]["segments"]), 1)
        self.assertEqual(res_data["meeting"]["transcript"]["segments"][0]["text"], "Transcripción vía API")

    @patch.object(GeminiTranscriber, "transcribe_segment")
    def test_api_transcribe_endpoint_with_segment_params(self, mock_transcribe_seg):
        m = self.storage.create_meeting(name="Reunión API Transcribe con Rango")
        self._create_dummy_wav(m["audio_path"], duration_sec=10.0)
        self.storage.finalize_recording(m["meeting_dir"])

        mock_transcribe_seg.return_value = {
            "speakers": ["Speaker 1"],
            "speaker_mapping": {"Speaker 1": "Speaker 1"},
            "segments": [
                {
                    "id": 1,
                    "speaker": "Speaker 1",
                    "start_time": "00:02",
                    "end_time": "00:04",
                    "start_seconds": 2.0,
                    "end_seconds": 4.0,
                    "text": "Vía transcribe con parámetros"
                }
            ],
            "is_segment": True,
            "segment_bounds": {
                "start_seconds": 2.0,
                "end_seconds": 4.0,
                "start_time": "00:02",
                "end_time": "00:04",
                "duration_seconds": 2.0
            }
        }

        body = json.dumps({
            "start_seconds": 2.0,
            "end_seconds": 4.0,
            "merge_mode": "merge"
        }).encode("utf-8")

        status_line, _, resp_body = self._run_request(
            "POST",
            f"/api/meetings/{m['id']}/transcribe",
            headers={"Content-Type": "application/json"},
            body=body
        )

        self.assertIn("200", status_line)
        res_data = json.loads(resp_body.decode("utf-8"))
        self.assertTrue(res_data["success"])
        self.assertEqual(res_data["meeting"]["transcript"]["segments"][0]["text"], "Vía transcribe con parámetros")

    def test_api_transcribe_segment_not_found(self):
        status_line, _, resp_body = self._run_request(
            "POST",
            "/api/meetings/non-existent-id/transcribe-segment",
            headers={"Content-Type": "application/json"},
            body=b"{}"
        )
        self.assertIn("404", status_line)

if __name__ == "__main__":
    unittest.main()
