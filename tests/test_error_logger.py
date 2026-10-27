import os
import shutil
import tempfile
import unittest
from error_logger import (
    log_recording_error,
    log_recording_warning,
    log_transcription_error,
    log_transcription_warning,
    read_logs,
    clear_logs
)

class TestErrorLogger(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_env = os.environ.get("CALL_RECORDINGS_PATH")
        os.environ["CALL_RECORDINGS_PATH"] = self.test_dir

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["CALL_RECORDINGS_PATH"] = self.orig_env
        else:
            os.environ.pop("CALL_RECORDINGS_PATH", None)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_log_and_read_central_logs(self):
        log_recording_warning("Advertencia de prueba en audio")
        try:
            raise ValueError("Error simulado de grabación")
        except Exception as e:
            log_recording_error("Fallo de prueba en grabación", exc=e, meeting_id="TestMeeting_1")

        log_transcription_warning("Advertencia en transcripción")

        logs = read_logs()
        self.assertGreaterEqual(len(logs), 3)

        # Most recent first
        self.assertEqual(logs[0]["category"], "TRANSCRIPTION")
        self.assertEqual(logs[0]["level"], "WARNING")
        self.assertIn("Advertencia en transcripción", logs[0]["message"])

        # Second entry should be the error with exception details
        self.assertEqual(logs[1]["category"], "RECORDING")
        self.assertEqual(logs[1]["level"], "ERROR")
        self.assertEqual(logs[1]["meeting"], "TestMeeting_1")
        self.assertIn("ValueError: Error simulado de grabación", logs[1]["details"])

    def test_meeting_specific_log(self):
        meeting_dir = os.path.join(self.test_dir, "meeting_abc")
        os.makedirs(meeting_dir, exist_ok=True)

        log_transcription_error("Fallo específico de esta llamada", meeting_dir=meeting_dir, meeting_id="meeting_abc")

        meeting_logs = read_logs(meeting_dir=meeting_dir)
        self.assertEqual(len(meeting_logs), 1)
        self.assertEqual(meeting_logs[0]["category"], "TRANSCRIPTION")
        self.assertEqual(meeting_logs[0]["level"], "ERROR")
        self.assertIn("Fallo específico de esta llamada", meeting_logs[0]["message"])

        # Clear meeting logs
        clear_logs(meeting_dir=meeting_dir)
        self.assertEqual(len(read_logs(meeting_dir=meeting_dir)), 0)

    def test_clear_central_logs(self):
        log_recording_warning("Mensaje para borrar")
        self.assertGreaterEqual(len(read_logs()), 1)

        clear_logs()
        self.assertEqual(len(read_logs()), 0)

if __name__ == "__main__":
    unittest.main()
