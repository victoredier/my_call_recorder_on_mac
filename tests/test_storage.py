import os
import shutil
import tempfile
import unittest
import numpy as np
import soundfile as sf

from storage_manager import StorageManager

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manager = StorageManager(base_path=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_dummy_wav(self, path, duration_sec=2.0, sample_rate=16000):
        samples = int(duration_sec * sample_rate)
        data = np.zeros(samples, dtype=np.float32)
        sf.write(path, data, sample_rate)

    def test_create_and_finalize_meeting(self):
        meeting = self.manager.create_meeting(name="Reunión Sprint Planning")
        self.assertIn("meeting_dir", meeting)
        self.assertTrue(os.path.isdir(meeting["meeting_dir"]))
        self.assertTrue(os.path.isfile(meeting["metadata_path"]))

        # Check metadata content
        details = self.manager.get_meeting(meeting["id"])
        self.assertIsNotNone(details)
        self.assertEqual(details["name"], "Reunión Sprint Planning")
        self.assertEqual(details["status"], "recording")

        # Create a dummy audio file and finalize
        self._create_dummy_wav(meeting["audio_path"], duration_sec=3.5)
        finalized = self.manager.finalize_recording(meeting["meeting_dir"], name="Sprint Planning 1")
        self.assertEqual(finalized["status"], "recorded")
        self.assertAlmostEqual(finalized["duration_seconds"], 3.5, places=1)
        self.assertEqual(finalized["name"], "Sprint Planning 1")

    def test_list_meetings(self):
        m1 = self.manager.create_meeting(name="Llamada 1")
        m2 = self.manager.create_meeting(name="Llamada 2")

        meetings = self.manager.list_meetings()
        self.assertEqual(len(meetings), 2)
        names = [m["name"] for m in meetings]
        self.assertIn("Llamada 1", names)
        self.assertIn("Llamada 2", names)

    def test_rename_meeting(self):
        m = self.manager.create_meeting(name="Original Name")
        updated = self.manager.rename_meeting(m["id"], "Nuevo Nombre")
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "Nuevo Nombre")

    def test_save_transcript(self):
        m = self.manager.create_meeting(name="Reunión Transcripción")
        transcript_data = {
            "speakers": ["Víctor", "Carlos"],
            "speaker_mapping": {"Speaker 1": "Víctor", "Speaker 2": "Carlos"},
            "segments": [
                {
                    "id": 1,
                    "speaker": "Víctor",
                    "speaker_raw": "Speaker 1",
                    "start_time": "00:00",
                    "end_time": "00:05",
                    "start_seconds": 0.0,
                    "end_seconds": 5.0,
                    "text": "Hola Carlos."
                }
            ]
        }
        success = self.manager.save_transcript(m["id"], transcript_data)
        self.assertTrue(success)

        details = self.manager.get_meeting(m["id"])
        self.assertEqual(details["status"], "transcribed")
        self.assertIsNotNone(details["transcript"])
        self.assertEqual(len(details["transcript"]["segments"]), 1)
        self.assertEqual(details["transcript"]["segments"][0]["speaker"], "Víctor")

    def test_delete_meeting(self):
        m = self.manager.create_meeting(name="Para Borrar")
        meeting_dir = m["meeting_dir"]
        self.assertTrue(os.path.isdir(meeting_dir))

        deleted = self.manager.delete_meeting(m["id"])
        self.assertTrue(deleted)
        self.assertFalse(os.path.exists(meeting_dir))
        self.assertIsNone(self.manager.get_meeting(m["id"]))

if __name__ == "__main__":
    unittest.main()
