import os
import json
import re
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
import soundfile as sf

class StorageManager:
    """
    Manages call recordings storage.
    Each meeting/call is stored in its own subfolder inside the base recordings directory:
      ~/Recordings/
        └── 2026-09-21_10-50-00_Mi_Reunion/
              ├── audio.wav
              ├── metadata.json
              └── transcript.json
    """

    def __init__(self, base_path: Optional[str] = None):
        if not base_path:
            default_path = os.path.expanduser("~/Recordings")
            base_path = os.environ.get("CALL_RECORDINGS_PATH", default_path)
        self.base_path = os.path.abspath(base_path)
        self._ensure_base_dir()

    def _ensure_base_dir(self):
        """Ensures the base directory exists."""
        os.makedirs(self.base_path, exist_ok=True)

    @staticmethod
    def slugify(text: str) -> str:
        """Converts text into a safe folder/file name slug."""
        text = text.strip().replace(" ", "_")
        return re.sub(r'[^a-zA-Z0-9_\-]', '', text)

    def create_meeting(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new meeting subfolder and initializes its metadata.json.
        Returns the meeting metadata dictionary including paths.
        """
        self._ensure_base_dir()
        now = datetime.now()
        timestamp_str = now.strftime('%Y-%m-%d_%H-%M-%S')
        meeting_id = now.strftime('%Y%m%d_%H%M%S')
        
        default_name = name if name and name.strip() else f"Llamada {now.strftime('%d/%m/%Y %H:%M')}"
        slug = self.slugify(default_name)
        folder_name = f"{timestamp_str}_{slug}" if slug else timestamp_str
        
        meeting_dir = os.path.join(self.base_path, folder_name)
        # Avoid collision if folder already exists
        counter = 1
        base_dir_candidate = meeting_dir
        while os.path.exists(meeting_dir):
            meeting_dir = f"{base_dir_candidate}_{counter}"
            folder_name = os.path.basename(meeting_dir)
            counter += 1
            
        os.makedirs(meeting_dir, exist_ok=True)
        
        audio_filename = "audio.wav"
        audio_path = os.path.join(meeting_dir, audio_filename)
        
        metadata = {
            "id": meeting_id,
            "folder_name": folder_name,
            "name": default_name,
            "created_at": now.isoformat(),
            "duration_seconds": 0.0,
            "audio_filename": audio_filename,
            "status": "recording",  # recording, recorded, transcribing, transcribed, error
            "speakers": [],
            "speaker_mapping": {},
            "error_message": None
        }
        
        self._save_metadata(meeting_dir, metadata)
        
        return {
            **metadata,
            "meeting_dir": meeting_dir,
            "audio_path": audio_path,
            "metadata_path": os.path.join(meeting_dir, "metadata.json"),
            "transcript_path": os.path.join(meeting_dir, "transcript.json")
        }

    def _save_metadata(self, meeting_dir: str, metadata: Dict[str, Any]):
        """Helper to write metadata.json atomically."""
        meta_path = os.path.join(meeting_dir, "metadata.json")
        tmp_path = meta_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, meta_path)

    def find_meeting_dir_by_id(self, meeting_id: str) -> Optional[str]:
        """Finds the directory of a meeting by its ID or folder name."""
        if not os.path.exists(self.base_path):
            return None
            
        for entry in os.listdir(self.base_path):
            entry_path = os.path.join(self.base_path, entry)
            if not os.path.isdir(entry_path):
                continue
            meta_path = os.path.join(entry_path, "metadata.json")
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if str(data.get("id")) == str(meeting_id) or entry == meeting_id:
                        return entry_path
                except Exception:
                    continue
            elif entry == meeting_id:
                return entry_path
        return None

    def finalize_recording(self, meeting_dir: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Finalizes a recording: calculates duration from audio.wav and updates metadata.
        Optionally renames the meeting and folder.
        """
        meta_path = os.path.join(meeting_dir, "metadata.json")
        metadata = {}
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception:
                pass

        audio_path = os.path.join(meeting_dir, metadata.get("audio_filename", "audio.wav"))
        duration = 0.0
        if os.path.exists(audio_path):
            try:
                info = sf.info(audio_path)
                duration = round(info.duration, 2)
            except Exception as e:
                print(f"Error getting audio duration: {e}")

        metadata["duration_seconds"] = duration
        metadata["status"] = "recorded"
        if name and name.strip():
            metadata["name"] = name.strip()

        self._save_metadata(meeting_dir, metadata)
        return metadata

    def list_meetings(self) -> List[Dict[str, Any]]:
        """
        Lists all meetings from subfolders in base_path, sorted by creation date (newest first).
        """
        if not os.path.exists(self.base_path):
            return []

        meetings = []
        for entry in os.listdir(self.base_path):
            entry_path = os.path.join(self.base_path, entry)
            if not os.path.isdir(entry_path):
                continue

            meta_path = os.path.join(entry_path, "metadata.json")
            audio_path = os.path.join(entry_path, "audio.wav")
            transcript_path = os.path.join(entry_path, "transcript.json")

            metadata = {}
            if os.path.isfile(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                except Exception:
                    pass

            if not metadata:
                # Infer metadata if missing
                mtime = os.path.getmtime(entry_path)
                created_iso = datetime.fromtimestamp(mtime).isoformat()
                metadata = {
                    "id": entry,
                    "folder_name": entry,
                    "name": entry,
                    "created_at": created_iso,
                    "duration_seconds": 0.0,
                    "audio_filename": "audio.wav",
                    "status": "recorded" if os.path.exists(audio_path) else "empty",
                    "speakers": [],
                    "speaker_mapping": {}
                }

            has_transcript = os.path.isfile(transcript_path)
            has_audio = os.path.isfile(os.path.join(entry_path, metadata.get("audio_filename", "audio.wav")))
            
            meetings.append({
                **metadata,
                "has_audio": has_audio,
                "has_transcript": has_transcript,
                "folder_name": entry
            })

        # Sort descending by created_at
        meetings.sort(key=lambda m: m.get("created_at", ""), reverse=True)
        return meetings

    def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Gets complete details of a meeting including transcript if available."""
        meeting_dir = self.find_meeting_dir_by_id(meeting_id)
        if not meeting_dir:
            return None

        meta_path = os.path.join(meeting_dir, "metadata.json")
        metadata = {}
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception:
                pass

        transcript_path = os.path.join(meeting_dir, "transcript.json")
        transcript = None
        if os.path.isfile(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    transcript = json.load(f)
            except Exception as e:
                print(f"Error loading transcript: {e}")

        audio_path = os.path.join(meeting_dir, metadata.get("audio_filename", "audio.wav"))
        
        return {
            **metadata,
            "folder_name": os.path.basename(meeting_dir),
            "meeting_dir": meeting_dir,
            "has_audio": os.path.isfile(audio_path),
            "audio_path": audio_path,
            "transcript": transcript
        }

    def rename_meeting(self, meeting_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        """Renames a meeting in metadata (and updates transcript meeting_name)."""
        meeting_dir = self.find_meeting_dir_by_id(meeting_id)
        if not meeting_dir:
            return None

        meta_path = os.path.join(meeting_dir, "metadata.json")
        metadata = {}
        if os.path.isfile(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

        metadata["name"] = new_name.strip()
        self._save_metadata(meeting_dir, metadata)

        # Also update transcript if present
        transcript_path = os.path.join(meeting_dir, "transcript.json")
        if os.path.isfile(transcript_path):
            try:
                with open(transcript_path, "r", encoding="utf-8") as f:
                    tr = json.load(f)
                tr["meeting_name"] = new_name.strip()
                with open(transcript_path, "w", encoding="utf-8") as f:
                    json.dump(tr, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        return self.get_meeting(meeting_id)

    def save_transcript(self, meeting_id: str, transcript_data: Dict[str, Any]) -> bool:
        """
        Saves updated transcript and updates metadata speakers & status.
        """
        meeting_dir = self.find_meeting_dir_by_id(meeting_id)
        if not meeting_dir:
            return False

        transcript_path = os.path.join(meeting_dir, "transcript.json")
        tmp_path = transcript_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, transcript_path)

        # Update metadata status and speakers
        meta_path = os.path.join(meeting_dir, "metadata.json")
        metadata = {}
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception:
                pass

        metadata["status"] = "transcribed"
        if "speakers" in transcript_data:
            metadata["speakers"] = transcript_data["speakers"]
        if "speaker_mapping" in transcript_data:
            metadata["speaker_mapping"] = transcript_data["speaker_mapping"]

        self._save_metadata(meeting_dir, metadata)
        return True

    def update_status(self, meeting_id: str, status: str, error_message: Optional[str] = None):
        """Updates meeting status (e.g. transcribing, error)."""
        meeting_dir = self.find_meeting_dir_by_id(meeting_id)
        if not meeting_dir:
            return

        meta_path = os.path.join(meeting_dir, "metadata.json")
        metadata = {}
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
            except Exception:
                pass

        metadata["status"] = status
        metadata["error_message"] = error_message
        self._save_metadata(meeting_dir, metadata)

    def delete_meeting(self, meeting_id: str) -> bool:
        """Permanently deletes a meeting subfolder."""
        meeting_dir = self.find_meeting_dir_by_id(meeting_id)
        if not meeting_dir or not os.path.isdir(meeting_dir):
            return False

        try:
            shutil.rmtree(meeting_dir)
            return True
        except Exception as e:
            print(f"Error deleting meeting directory {meeting_dir}: {e}")
            return False
