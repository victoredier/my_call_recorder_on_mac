import os
import sys
import json
import mimetypes
import re
import subprocess
import threading
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

from storage_manager import StorageManager
from gemini_transcriber import GeminiTranscriber, get_saved_config, save_config

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # Ignore broken pipe and connection reset errors (standard during audio streaming)
        ex_type, _, _ = sys.exc_info()
        if ex_type in (BrokenPipeError, ConnectionResetError):
            return
        super().handle_error(request, client_address)

class CallRecorderHandler(BaseHTTPRequestHandler):
    storage_manager = StorageManager()

    def finish(self):
        try:
            super().finish()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204, "text/plain")

    def _read_json_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        body = self.rfile.read(content_len).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {}

    def _send_json(self, data, status=200):
        try:
            self._set_headers(status, "application/json; charset=utf-8")
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status=status)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # Static assets routing
        if path == "/" or path == "/index.html":
            self._serve_static_file("index.html", "text/html")
            return
        elif path == "/style.css":
            self._serve_static_file("style.css", "text/css")
            return
        elif path == "/app.js":
            self._serve_static_file("app.js", "application/javascript")
            return

        # API: List all meetings
        if path == "/api/meetings":
            meetings = self.storage_manager.list_meetings()
            self._send_json({"meetings": meetings})
            return

        # API: Get config
        if path == "/api/config":
            cfg = get_saved_config()
            # Mask API key for safety in UI
            raw_key = cfg.get("gemini_api_key", "")
            masked = f"{raw_key[:4]}...{raw_key[-4:]}" if len(raw_key) > 8 else ("***" if raw_key else "")
            self._send_json({
                "has_api_key": bool(raw_key),
                "masked_api_key": masked,
                "gemini_model": cfg.get("gemini_model", "gemini-2.5-flash"),
                "recordings_path": self.storage_manager.base_path
            })
            return

        # API: Single meeting details /api/meetings/<id>
        match_meeting = re.match(r"^/api/meetings/([^/]+)$", path)
        if match_meeting:
            meeting_id = match_meeting.group(1)
            meeting = self.storage_manager.get_meeting(meeting_id)
            if not meeting:
                self._send_error("Reunión no encontrada", 404)
                return
            self._send_json(meeting)
            return

        # API: Stream audio /api/meetings/<id>/audio
        match_audio = re.match(r"^/api/meetings/([^/]+)/audio$", path)
        if match_audio:
            meeting_id = match_audio.group(1)
            meeting = self.storage_manager.get_meeting(meeting_id)
            if not meeting or not meeting.get("has_audio"):
                self._send_error("Archivo de audio no encontrado", 404)
                return
            self._stream_audio_file(meeting["audio_path"])
            return

        self._send_error("Ruta no encontrada", 404)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # API: Save config
        if path == "/api/config":
            body = self._read_json_body()
            updates = {}
            if "gemini_api_key" in body:
                updates["gemini_api_key"] = body["gemini_api_key"].strip()
            if "gemini_model" in body:
                updates["gemini_model"] = body["gemini_model"].strip()
            save_config(updates)
            self._send_json({"success": True, "message": "Configuración guardada correctamente."})
            return

        # API: Open folder in macOS Finder
        if path == "/api/open-folder":
            body = self._read_json_body()
            meeting_id = body.get("meeting_id")
            folder_to_open = self.storage_manager.base_path
            if meeting_id:
                meeting = self.storage_manager.get_meeting(meeting_id)
                if meeting and meeting.get("meeting_dir"):
                    folder_to_open = meeting["meeting_dir"]
            try:
                subprocess.Popen(["open", folder_to_open])
                self._send_json({"success": True})
            except Exception as e:
                self._send_error(f"Error abriendo carpeta en Finder: {e}", 500)
            return

        # API: Rename meeting /api/meetings/<id>/rename
        match_rename = re.match(r"^/api/meetings/([^/]+)/rename$", path)
        if match_rename:
            meeting_id = match_rename.group(1)
            body = self._read_json_body()
            new_name = body.get("name", "").strip()
            if not new_name:
                self._send_error("El nombre no puede estar vacío", 400)
                return
            updated = self.storage_manager.rename_meeting(meeting_id, new_name)
            if not updated:
                self._send_error("No se pudo actualizar el nombre", 404)
                return
            self._send_json(updated)
            return

        # API: Save edited transcript /api/meetings/<id>/transcript
        match_transcript = re.match(r"^/api/meetings/([^/]+)/transcript$", path)
        if match_transcript:
            meeting_id = match_transcript.group(1)
            body = self._read_json_body()
            transcript_data = body.get("transcript")
            if not transcript_data:
                self._send_error("Datos de transcripción no proporcionados", 400)
                return
            success = self.storage_manager.save_transcript(meeting_id, transcript_data)
            if not success:
                self._send_error("Error al guardar la transcripción", 500)
                return
            updated_meeting = self.storage_manager.get_meeting(meeting_id)
            self._send_json({"success": True, "meeting": updated_meeting})
            return

        # API: Transcribe with Gemini /api/meetings/<id>/transcribe
        match_transcribe = re.match(r"^/api/meetings/([^/]+)/transcribe$", path)
        if match_transcribe:
            meeting_id = match_transcribe.group(1)
            body = self._read_json_body()
            meeting = self.storage_manager.get_meeting(meeting_id)
            if not meeting:
                self._send_error("Reunión no encontrada", 404)
                return
            if not meeting.get("has_audio"):
                self._send_error("No se encontró el archivo de audio para transcribir", 400)
                return

            custom_api_key = body.get("gemini_api_key")
            custom_model = body.get("gemini_model")
            
            # Update status to transcribing
            self.storage_manager.update_status(meeting_id, "transcribing")

            try:
                transcriber = GeminiTranscriber(api_key=custom_api_key, model=custom_model)
                audio_path = meeting["audio_path"]
                transcript_result = transcriber.transcribe_audio(audio_path)
                
                # Attach meeting metadata into transcript
                transcript_result["meeting_id"] = meeting.get("id")
                transcript_result["meeting_name"] = meeting.get("name")
                transcript_result["created_at"] = meeting.get("created_at")

                self.storage_manager.save_transcript(meeting_id, transcript_result)
                updated_meeting = self.storage_manager.get_meeting(meeting_id)
                self._send_json({"success": True, "meeting": updated_meeting})
            except Exception as e:
                err_str = str(e)
                self.storage_manager.update_status(meeting_id, "error", error_message=err_str)
                self._send_error(f"Error al transcribir: {err_str}", 500)
            return

        self._send_error("Ruta POST no encontrada", 404)

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # API: Delete meeting /api/meetings/<id>
        match_delete = re.match(r"^/api/meetings/([^/]+)$", path)
        if match_delete:
            meeting_id = match_delete.group(1)
            success = self.storage_manager.delete_meeting(meeting_id)
            if not success:
                self._send_error("No se pudo eliminar la reunión", 404)
                return
            self._send_json({"success": True, "deleted_id": meeting_id})
            return

        self._send_error("Ruta DELETE no encontrada", 404)

    def _serve_static_file(self, filename: str, content_type: str):
        web_dir = os.path.join(os.path.dirname(__file__), "web")
        file_path = os.path.join(web_dir, filename)
        if not os.path.isfile(file_path):
            self._send_error(f"Archivo no encontrado: {filename}", 404)
            return

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            self._send_error(f"Error sirviendo archivo: {e}", 500)

    def _stream_audio_file(self, audio_path: str):
        """
        Streams audio file supporting HTTP Range requests for instant seeking in audio player.
        """
        if not os.path.isfile(audio_path):
            self._send_error("Audio file not found", 404)
            return

        file_size = os.path.getsize(audio_path)
        range_header = self.headers.get("Range")

        try:
            if range_header:
                # Parse Range: bytes=start-end
                range_match = re.match(r"^bytes=(\d+)-(\d*)$", range_header.strip())
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                    end = min(end, file_size - 1)

                    if start >= file_size or start > end:
                        self.send_response(416)  # Range Not Satisfiable
                        self.send_header("Content-Range", f"bytes */{file_size}")
                        self.end_headers()
                        return

                    chunk_size = (end - start) + 1
                    self.send_response(206)
                    self.send_header("Content-Type", "audio/wav")
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(chunk_size))
                    self.end_headers()

                    with open(audio_path, "rb") as f:
                        f.seek(start)
                        bytes_left = chunk_size
                        while bytes_left > 0:
                            read_len = min(bytes_left, 64 * 1024)
                            chunk = f.read(read_len)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            bytes_left -= len(chunk)
                    return

            # Full file response
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()

            with open(audio_path, "rb") as f:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            # Normal browser behavior when aborting stream or scrubbing
            pass
        except Exception as e:
            print(f"Error streaming audio: {e}")

    def log_message(self, format, *args):
        # Silence default terminal request spam
        pass

def start_server(host="127.0.0.1", port=5050) -> ThreadedHTTPServer:
    """Starts the local HTTP server in a background thread."""
    server = None
    for p in range(port, port + 10):
        try:
            server = ThreadedHTTPServer((host, p), CallRecorderHandler)
            actual_port = p
            break
        except OSError:
            continue

    if not server:
        raise RuntimeError("Could not find an available port for CallRecorder local server.")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Call Recorder Dashboard running at http://{host}:{actual_port}")
    return server

if __name__ == "__main__":
    srv = start_server(port=5050)
    print("Server running. Press Ctrl+C to stop.")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        srv.shutdown()
