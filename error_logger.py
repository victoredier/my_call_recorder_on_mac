import os
import sys
import traceback
from datetime import datetime
from typing import Optional, List, Dict, Any

DEFAULT_BASE_PATH = os.path.expanduser("~/Recordings")

def get_base_recordings_path() -> str:
    """Returns the base recordings directory path."""
    return os.environ.get("CALL_RECORDINGS_PATH", DEFAULT_BASE_PATH)

def get_central_log_path() -> str:
    """Returns the path to the central application error log file."""
    base_dir = get_base_recordings_path()
    try:
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "app_errors.log")
    except Exception:
        fallback = os.path.expanduser("~/.call_recorder")
        os.makedirs(fallback, exist_ok=True)
        return os.path.join(fallback, "app_errors.log")

def _write_entry(log_path: str, entry: str):
    """Appends an entry string to the specified log file."""
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception as e:
        print(f"Error escribiendo en log ({log_path}): {e}", file=sys.stderr)

def log_event(
    level: str,
    category: str,
    message: str,
    exc: Optional[BaseException] = None,
    meeting_dir: Optional[str] = None,
    meeting_id: Optional[str] = None
):
    """
    Logs an event (ERROR, WARNING, INFO) to both the central log and
    optionally the specific meeting folder's error.log.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meeting_tag = f" [Meeting: {meeting_id or os.path.basename(meeting_dir)}]" if (meeting_id or meeting_dir) else ""
    header = f"[{now_str}] [{level.upper()}] [{category.upper()}]{meeting_tag} {message}"
    
    body_lines = [header]
    if exc:
        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        body_lines.append("".join(tb_lines).strip())

    entry_text = "\n".join(body_lines)

    # 1. Write to central log
    central_path = get_central_log_path()
    _write_entry(central_path, entry_text)

    # 2. Write to meeting folder if available
    if meeting_dir and os.path.isdir(meeting_dir):
        meeting_log = os.path.join(meeting_dir, "error.log")
        _write_entry(meeting_log, entry_text)

def log_recording_error(message: str, exc: Optional[BaseException] = None, meeting_dir: Optional[str] = None, meeting_id: Optional[str] = None):
    """Helper to log a recording error."""
    log_event("ERROR", "RECORDING", message, exc=exc, meeting_dir=meeting_dir, meeting_id=meeting_id)

def log_recording_warning(message: str, meeting_dir: Optional[str] = None, meeting_id: Optional[str] = None):
    """Helper to log a recording warning."""
    log_event("WARNING", "RECORDING", message, meeting_dir=meeting_dir, meeting_id=meeting_id)

def log_transcription_error(message: str, exc: Optional[BaseException] = None, meeting_dir: Optional[str] = None, meeting_id: Optional[str] = None):
    """Helper to log a transcription error."""
    log_event("ERROR", "TRANSCRIPTION", message, exc=exc, meeting_dir=meeting_dir, meeting_id=meeting_id)

def log_transcription_warning(message: str, meeting_dir: Optional[str] = None, meeting_id: Optional[str] = None):
    """Helper to log a transcription warning."""
    log_event("WARNING", "TRANSCRIPTION", message, meeting_dir=meeting_dir, meeting_id=meeting_id)

def read_logs(meeting_dir: Optional[str] = None, max_lines: int = 200) -> List[Dict[str, Any]]:
    """
    Reads and parses log entries from the specified meeting_dir or the central log.
    Returns list of dicts: [{timestamp, level, category, meeting, message, details}]
    Sorted newest first.
    """
    if meeting_dir and os.path.isdir(meeting_dir):
        log_path = os.path.join(meeting_dir, "error.log")
    else:
        log_path = get_central_log_path()

    if not os.path.exists(log_path):
        return []

    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return []

    # Parse entries: an entry begins with [YYYY-MM-DD HH:MM:SS]
    entries = []
    current_entry = None

    import re
    header_regex = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[([A-Z]+)\] \[([A-Z_]+)\](?: \[Meeting: ([^\]]+)\])? (.*)$")

    for line in lines[-max_lines:]:
        match = header_regex.match(line.strip())
        if match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "timestamp": match.group(1),
                "level": match.group(2),
                "category": match.group(3),
                "meeting": match.group(4) or "",
                "message": match.group(5),
                "details": ""
            }
        elif current_entry is not None:
            if current_entry["details"]:
                current_entry["details"] += "\n" + line.rstrip()
            else:
                current_entry["details"] = line.rstrip()

    if current_entry:
        entries.append(current_entry)

    # Reverse to have newest first
    entries.reverse()
    return entries

def clear_logs(meeting_dir: Optional[str] = None) -> bool:
    """Clears the specified log file."""
    if meeting_dir and os.path.isdir(meeting_dir):
        log_path = os.path.join(meeting_dir, "error.log")
    else:
        log_path = get_central_log_path()

    if os.path.exists(log_path):
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("")
            return True
        except Exception:
            return False
    return True
