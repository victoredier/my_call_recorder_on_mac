import os
import io
import json
import shutil
import tempfile
import unittest
import numpy as np
import soundfile as sf

from server import CallRecorderHandler
from storage_manager import StorageManager

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

class TestServerHandlerDirect(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = StorageManager(base_path=self.test_dir)
        CallRecorderHandler.storage_manager = self.storage

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_dummy_wav(self, path, duration_sec=1.0, sample_rate=16000):
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
        # Instantiate handler without binding actual network port
        try:
            handler = CallRecorderHandler(sock, ("127.0.0.1", 12345), DummyServer())
        except Exception:
            pass

        output = sock.wfile.getvalue()
        # Parse status code and body
        parts = output.split(b"\r\n\r\n", 1)
        header_part = parts[0].decode("utf-8", errors="ignore")
        body_part = parts[1] if len(parts) > 1 else b""
        status_line = header_part.splitlines()[0] if header_part else ""
        return status_line, header_part, body_part

    def test_get_static_index(self):
        status_line, headers, body = self._run_request("GET", "/")
        self.assertIn("200", status_line)
        self.assertIn("Call Recorder", body.decode("utf-8"))

    def test_get_meetings_empty(self):
        status_line, headers, body = self._run_request("GET", "/api/meetings")
        self.assertIn("200", status_line)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(data["meetings"], [])

    def test_meetings_flow(self):
        # 1. Create meeting in storage
        m = self.storage.create_meeting(name="Llamada Test Handler")
        self._create_dummy_wav(m["audio_path"])
        self.storage.finalize_recording(m["meeting_dir"])

        # 2. GET /api/meetings
        status_line, _, body = self._run_request("GET", "/api/meetings")
        self.assertIn("200", status_line)
        data = json.loads(body.decode("utf-8"))
        self.assertEqual(len(data["meetings"]), 1)
        self.assertEqual(data["meetings"][0]["name"], "Llamada Test Handler")

        # 3. GET /api/meetings/<id>
        status_line, _, body = self._run_request("GET", f"/api/meetings/{m['id']}")
        self.assertIn("200", status_line)
        single_data = json.loads(body.decode("utf-8"))
        self.assertEqual(single_data["id"], m["id"])

        # 4. POST /api/meetings/<id>/rename
        rename_body = json.dumps({"name": "Nombre Modificado"}).encode("utf-8")
        status_line, _, body = self._run_request(
            "POST",
            f"/api/meetings/{m['id']}/rename",
            headers={"Content-Type": "application/json"},
            body=rename_body
        )
        self.assertIn("200", status_line)
        renamed = json.loads(body.decode("utf-8"))
        self.assertEqual(renamed["name"], "Nombre Modificado")

        # 5. POST /api/meetings/<id>/transcript
        transcript_body = json.dumps({
            "transcript": {
                "speakers": ["Victor"],
                "speaker_mapping": {"Speaker 1": "Victor"},
                "segments": [
                    {"id": 1, "speaker": "Victor", "text": "Mensaje de prueba", "start_seconds": 0.0, "end_seconds": 1.0}
                ]
            }
        }).encode("utf-8")
        status_line, _, body = self._run_request(
            "POST",
            f"/api/meetings/{m['id']}/transcript",
            headers={"Content-Type": "application/json"},
            body=transcript_body
        )
        self.assertIn("200", status_line)
        res_tr = json.loads(body.decode("utf-8"))
        self.assertTrue(res_tr["success"])

        # 6. Audio Range GET /api/meetings/<id>/audio
        status_line, headers, body = self._run_request(
            "GET",
            f"/api/meetings/{m['id']}/audio",
            headers={"Range": "bytes=0-30"}
        )
        self.assertIn("206", status_line)
        self.assertEqual(len(body), 31)

        # 7. DELETE /api/meetings/<id>
        status_line, _, body = self._run_request("DELETE", f"/api/meetings/{m['id']}")
        self.assertIn("200", status_line)
        del_res = json.loads(body.decode("utf-8"))
        self.assertTrue(del_res["success"])

if __name__ == "__main__":
    unittest.main()
