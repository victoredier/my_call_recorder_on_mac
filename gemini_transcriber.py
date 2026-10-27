import os
import json
import base64
import time
import re
import socket
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple
import soundfile as sf
import numpy as np
from error_logger import log_transcription_error, log_transcription_warning

CONFIG_PATH = os.path.expanduser("~/.call_recorder_config.json")

def get_saved_config() -> Dict[str, Any]:
    """Reads configuration from ~/.call_recorder_config.json or .env."""
    config = {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
        "gemini_model": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("gemini_api_key"):
                    config["gemini_api_key"] = saved["gemini_api_key"]
                if saved.get("gemini_model"):
                    config["gemini_model"] = saved["gemini_model"]
        except Exception:
            pass

    # Also check local .env if present
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if key and not config["gemini_api_key"]:
                            config["gemini_api_key"] = key
        except Exception:
            pass

    return config

def save_config(config_updates: Dict[str, Any]):
    """Saves configuration updates to ~/.call_recorder_config.json."""
    current = get_saved_config()
    current.update(config_updates)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

class GeminiTranscriber:
    """
    Handles transcription and speaker diarization via Google Gemini API.
    Outputs structured JSON with timestamps and speaker identifiers.
    """

    DEFAULT_PROMPT = """Eres un transcriptor profesional de reuniones y llamadas de alta precisión.
Transcribe el audio completo en su idioma original (ej. español) con diarización de interlocutores (ej. "Speaker 1", "Speaker 2", etc.).

REGLAS CRÍTICAS DE SEGMENTACIÓN Y CONCISIÓN:
1. NO dividas el audio en micro-segmentos de 1 o 2 segundos ni por palabras sueltas.
2. Agrupa las frases continuas de un mismo interlocutor en turnos de habla naturales y completos (típicamente de 10 a 45 segundos, o párrafos enteros de conversación). Solo cambia de segmento cuando hable otra persona o haya un cambio de tema con silencio prolongado.
3. Para mantener la respuesta ágil y completa en audios largos, NO incluyas campos redundantes de segundos o IDs; solo especifica speaker, start_time (HH:MM:SS), end_time (HH:MM:SS) y text.

Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura exacta:
{
  "speakers": ["Speaker 1", "Speaker 2"],
  "segments": [
    {
      "speaker": "Speaker 1",
      "start_time": "00:00:00",
      "end_time": "00:00:28",
      "text": "Párrafo completo con las oraciones que dijo este participante durante su intervención..."
    },
    {
      "speaker": "Speaker 2",
      "start_time": "00:00:29",
      "end_time": "00:01:05",
      "text": "Respuesta completa del segundo participante..."
    }
  ]
}
No incluyas texto explicativo antes ni después del JSON.
"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        config = get_saved_config()
        self.api_key = api_key or config.get("gemini_api_key", "")
        self.model = model or config.get("gemini_model", "gemini-2.5-flash")

    def _prepare_optimized_audio(self, audio_path: str) -> Tuple[str, str, bool, float]:
        """
        Optimizes audio for Gemini API:
        - Downmixes multi-channel audio to mono.
        - Resamples to 16kHz if higher.
        - Compresses to MP3 (or 16-bit mono WAV if MP3 not available) to drastically reduce size and upload time.
        Returns (path_to_audio, mime_type, is_temporary, duration_seconds).
        """
        duration_sec = 0.0
        try:
            info = sf.info(audio_path)
            duration_sec = float(info.duration)
        except Exception:
            pass

        try:
            data, sr = sf.read(audio_path, dtype='float32')

            if duration_sec <= 0 and sr > 0:
                duration_sec = float(len(data) / sr)

            # Downmix to mono if multi-channel
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = data.mean(axis=1)

            # Resample to 16kHz if rate is high
            target_sr = 16000
            if sr > 24000:
                if sr % target_sr == 0:
                    step = sr // target_sr
                    data = data[::step]
                else:
                    step = sr / target_sr
                    indices = np.round(np.arange(0, len(data), step)).astype(np.int64)
                    indices = indices[indices < len(data)]
                    data = data[indices]
                sr = target_sr

            # Try saving as MP3 first for dramatic size reduction (e.g., 299MB -> ~8MB)
            temp_path_mp3 = audio_path + ".optimized.mp3"
            try:
                sf.write(temp_path_mp3, data, sr, format='MP3')
                return temp_path_mp3, "audio/mp3", True, duration_sec
            except Exception as mp3_err:
                log_transcription_warning(f"MP3 encoding fallback: {mp3_err}. Guardando en WAV mono.", meeting_dir=os.path.dirname(audio_path) if audio_path else None)
                print(f"MP3 encoding fallback: {mp3_err}. Saving as 16-bit mono WAV.")

            # Fallback to 16-bit mono WAV
            temp_path_wav = audio_path + ".optimized.wav"
            sf.write(temp_path_wav, data, sr, subtype='PCM_16')
            return temp_path_wav, "audio/wav", True, duration_sec

        except Exception as e:
            log_transcription_warning(f"Audio optimization warning: {e}. Usando audio original.", meeting_dir=os.path.dirname(audio_path) if audio_path else None)
            print(f"Audio optimization warning: {e}. Using original audio.")
            mime_type = "audio/wav"
            if audio_path.lower().endswith(".mp3"):
                mime_type = "audio/mp3"
            elif audio_path.lower().endswith(".ogg"):
                mime_type = "audio/ogg"
            elif audio_path.lower().endswith(".flac"):
                mime_type = "audio/flac"
            return audio_path, mime_type, False, duration_sec

    def _upload_file_gemini(self, file_path: str, mime_type: str = "audio/wav") -> Tuple[str, str]:
        """
        Uploads audio to Gemini using the Files API (supports up to 2GB).
        Returns (file_uri, file_resource_name).
        """
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        display_name = os.path.basename(file_path)

        # Step 1: Initialize resumable upload
        init_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={self.api_key}"
        init_headers = {
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(file_size),
            "X-Goog-Upload-Header-Content-Type": mime_type,
            "Content-Type": "application/json"
        }
        init_body = json.dumps({"file": {"display_name": display_name}}).encode("utf-8")

        req = urllib.request.Request(init_url, data=init_body, headers=init_headers, method="POST")
        meeting_dir = os.path.dirname(file_path) if file_path else None
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                upload_url = resp.headers.get("x-goog-upload-url") or resp.headers.get("X-Goog-Upload-URL")
        except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
            err_msg = f"Tiempo de espera agotado al conectar con el servidor de subida de Gemini: {e}"
            log_transcription_error(err_msg, exc=e, meeting_dir=meeting_dir)
            raise TimeoutError(err_msg)

        if not upload_url:
            err_msg = "Gemini upload failed: missing upload URL in response."
            log_transcription_error(err_msg, meeting_dir=meeting_dir)
            raise ValueError(err_msg)

        # Step 2: Upload file bytes with generous timeout
        upload_timeout = max(180, int(file_size_mb * 5))
        with open(file_path, "rb") as f:
            audio_bytes = f.read()

        upload_headers = {
            "Content-Length": str(file_size),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize"
        }
        upload_req = urllib.request.Request(upload_url, data=audio_bytes, headers=upload_headers, method="POST")
        try:
            with urllib.request.urlopen(upload_req, timeout=upload_timeout) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
            err_msg = (
                f"Tiempo de espera agotado al subir el archivo de audio ({file_size_mb:.1f} MB). "
                "Verifica tu conexión a internet o intenta nuevamente."
            )
            log_transcription_error(err_msg, exc=e, meeting_dir=meeting_dir)
            raise TimeoutError(err_msg)

        file_obj = res_data.get("file", {})
        file_uri = file_obj.get("uri")
        file_name = file_obj.get("name")  # e.g. "files/xyz123"

        if not file_uri:
            err_msg = f"Gemini upload returned invalid file object: {res_data}"
            log_transcription_error(err_msg, meeting_dir=meeting_dir)
            raise ValueError(err_msg)

        # Check state: wait briefly if PROCESSING
        state = file_obj.get("state")
        retries = 0
        while state == "PROCESSING" and retries < 30:
            time.sleep(2)
            check_url = f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={self.api_key}"
            check_req = urllib.request.Request(check_url, method="GET")
            try:
                with urllib.request.urlopen(check_req, timeout=30) as check_resp:
                    check_data = json.loads(check_resp.read().decode("utf-8"))
                    state = check_data.get("state")
            except Exception:
                pass
            retries += 1

        if state == "FAILED":
            err_msg = "El procesamiento del archivo de audio falló en los servidores de Gemini."
            log_transcription_error(err_msg, meeting_dir=meeting_dir)
            raise ValueError(err_msg)

        return file_uri, file_name

    def _delete_file_gemini(self, file_name: str):
        """Cleans up the file from Gemini storage."""
        if not file_name:
            return
        try:
            del_url = f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={self.api_key}"
            del_req = urllib.request.Request(del_url, method="DELETE")
            with urllib.request.urlopen(del_req, timeout=15) as _:
                pass
        except Exception:
            pass

    def transcribe_audio(self, audio_path: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribes the given audio file using Gemini API.
        Returns the parsed JSON response with speakers and segments.
        """
        if not self.api_key:
            raise ValueError("No se ha configurado la clave API de Gemini (GEMINI_API_KEY). Configúrala en los ajustes.")

        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")

        prompt_text = custom_prompt or self.DEFAULT_PROMPT

        # Optimize audio if needed and calculate duration
        upload_path, mime_type, is_temp, duration_sec = self._prepare_optimized_audio(audio_path)
        file_size_mb = os.path.getsize(upload_path) / (1024 * 1024)

        # Dynamic timeout: scale with duration (e.g., 34 mins audio = ~2040s -> ~1020s timeout)
        # Minimum 300s (5 minutes), Maximum 1200s (20 minutes)
        if duration_sec > 0:
            generation_timeout = int(max(300, min(1200, duration_sec * 0.5)))
        else:
            generation_timeout = 600

        file_name_to_cleanup = None
        try:
            # If file is very small (< 15MB), we can use inline data for maximum speed
            if file_size_mb < 15.0:
                with open(upload_path, "rb") as f:
                    encoded_audio = base64.b64encode(f.read()).decode("utf-8")
                
                parts = [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": encoded_audio
                        }
                    },
                    {
                        "text": prompt_text
                    }
                ]
            else:
                # Upload using Files API
                file_uri, file_name = self._upload_file_gemini(upload_path, mime_type=mime_type)
                file_name_to_cleanup = file_name
                parts = [
                    {
                        "file_data": {
                            "file_uri": file_uri,
                            "mime_type": mime_type
                        }
                    },
                    {
                        "text": prompt_text
                    }
                ]

            # Determine maxOutputTokens according to model capabilities
            model_name = (self.model or "").lower()
            if "2.5" in model_name or "2.0" in model_name:
                max_tokens = 65536
            elif "1.5" in model_name:
                max_tokens = 8192
            else:
                max_tokens = 32768

            # Request generation with JSON schema configuration
            gen_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": parts
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.2,
                    "maxOutputTokens": max_tokens
                }
            }

            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                gen_url,
                data=json_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            meeting_dir = os.path.dirname(audio_path) if audio_path else None
            try:
                with urllib.request.urlopen(req, timeout=generation_timeout) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                err_msg = f"Error de Gemini API ({e.code}): {err_body}"
                log_transcription_error(err_msg, exc=e, meeting_dir=meeting_dir)
                raise ValueError(err_msg)
            except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
                err_str = str(e)
                if "timed out" in err_str.lower() or isinstance(getattr(e, "reason", None), (TimeoutError, socket.timeout)):
                    duration_info = f" (duración: {int(duration_sec // 60)}m)" if duration_sec > 0 else ""
                    err_msg = (
                        f"El tiempo de espera para transcribir el audio se agotó tras {generation_timeout} segundos{duration_info}. "
                        "Para llamadas muy largas, asegúrate de utilizar el modelo rápido 'gemini-2.5-flash' o vuelve a intentarlo."
                    )
                    log_transcription_error(err_msg, exc=e, meeting_dir=meeting_dir)
                    raise TimeoutError(err_msg)
                err_msg = f"Error de conexión con Gemini API: {getattr(e, 'reason', e)}"
                log_transcription_error(err_msg, exc=e, meeting_dir=meeting_dir)
                raise ValueError(err_msg)

            # Extract generated content
            candidates = resp_data.get("candidates", [])
            if not candidates:
                err_msg = "Gemini no devolvió ninguna transcripción."
                log_transcription_error(err_msg, meeting_dir=meeting_dir)
                raise ValueError(err_msg)

            candidate = candidates[0]
            finish_reason = candidate.get("finishReason")
            parts_resp = candidate.get("content", {}).get("parts", [])
            raw_text = "".join(p.get("text", "") for p in parts_resp)

            parsed_json = self.parse_and_validate_transcript(raw_text)
            if finish_reason == "MAX_TOKENS" and not parsed_json.get("warning"):
                parsed_json["is_partial"] = True
                parsed_json["warning"] = "La transcripción alcanzó el límite máximo de tokens y se preservó hasta el último segmento completo."
            
            if parsed_json.get("warning"):
                log_transcription_warning(parsed_json["warning"], meeting_dir=meeting_dir)

            return parsed_json

        finally:
            if is_temp and os.path.exists(upload_path):
                try:
                    os.remove(upload_path)
                except Exception:
                    pass
            if file_name_to_cleanup:
                self._delete_file_gemini(file_name_to_cleanup)

    @classmethod
    def repair_truncated_json(cls, text: str) -> Dict[str, Any]:
        """
        Attempts to repair a JSON string that was truncated by max output token limits.
        Salvages all complete segments so transcription data is not lost.
        """
        clean = text.strip()
        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean).strip()

        try:
            return json.loads(clean)
        except Exception:
            pass

        # Strategy 1: Find the last complete segment closing brace "}"
        last_brace_idx = clean.rfind("}")
        while last_brace_idx > 0:
            candidate = clean[:last_brace_idx + 1].strip()
            if candidate.endswith(","):
                candidate = candidate[:-1].strip()
            if not candidate.endswith("]"):
                candidate += "\n  ]"
            if not candidate.endswith("}"):
                candidate += "\n}"
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict) and "segments" in parsed and isinstance(parsed["segments"], list):
                    return parsed
            except Exception:
                pass
            last_brace_idx = clean.rfind("}", 0, last_brace_idx)

        # Strategy 2: Regex extraction of individual valid segments
        segment_pattern = re.compile(r"\{[^{}]*\"(?:speaker|text)\"[^{}]*\}", re.DOTALL)
        recovered_segments = []
        for match in segment_pattern.finditer(clean):
            try:
                seg = json.loads(match.group(0))
                if isinstance(seg, dict) and ("speaker" in seg or "text" in seg):
                    recovered_segments.append(seg)
            except Exception:
                continue

        if recovered_segments:
            speakers = []
            spk_match = re.search(r"\"speakers\"\s*:\s*\[(.*?)\]", clean, re.DOTALL)
            if spk_match:
                try:
                    speakers = json.loads(f"[{spk_match.group(1)}]")
                except Exception:
                    pass
            return {"speakers": speakers, "segments": recovered_segments}

        raise ValueError(
            f"La respuesta de Gemini fue interrumpida y no contiene JSON válido ni segmentos recuperables.\n"
            f"Muestra recibida: {clean[:200]}"
        )

    @classmethod
    def parse_and_validate_transcript(cls, raw_text: str) -> Dict[str, Any]:
        """
        Parses JSON text (handling potential markdown fences and truncated outputs) and validates the structure.
        """
        clean_text = raw_text.strip()
        # Remove ```json ... ``` fences if present
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
            clean_text = re.sub(r"\s*```$", "", clean_text)
        clean_text = clean_text.strip()

        is_repaired = False
        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError:
            data = cls.repair_truncated_json(clean_text)
            is_repaired = True

        # Ensure segments is a list
        segments = data.get("segments", [])
        if not isinstance(segments, list):
            segments = []

        # Normalize and fill missing segment fields
        normalized_segments = []
        speakers_set = set()

        for idx, seg in enumerate(segments, 1):
            if not isinstance(seg, dict):
                continue
            speaker = seg.get("speaker") or f"Speaker {idx}"
            speakers_set.add(speaker)

            start_s = seg.get("start_seconds")
            end_s = seg.get("end_seconds")
            start_t = seg.get("start_time")
            end_t = seg.get("end_time")

            # Fallback formatting for time strings
            if start_s is not None and not start_t:
                start_t = cls.format_seconds(float(start_s))
            elif start_t and start_s is None:
                start_s = cls.parse_time_to_seconds(start_t)

            if end_s is not None and not end_t:
                end_t = cls.format_seconds(float(end_s))
            elif end_t and end_s is None:
                end_s = cls.parse_time_to_seconds(end_t)

            start_s = float(start_s or 0.0)
            end_s = float(end_s or (start_s + 2.0))

            normalized_segments.append({
                "id": seg.get("id") or idx,
                "speaker": speaker,
                "speaker_raw": seg.get("speaker_raw") or speaker,
                "start_time": start_t or cls.format_seconds(start_s),
                "end_time": end_t or cls.format_seconds(end_s),
                "start_seconds": round(start_s, 2),
                "end_seconds": round(end_s, 2),
                "text": seg.get("text", "").strip()
            })

        declared_speakers = data.get("speakers", [])
        if isinstance(declared_speakers, list) and declared_speakers:
            all_speakers = list(dict.fromkeys(declared_speakers + list(speakers_set)))
        else:
            all_speakers = sorted(list(speakers_set))

        speaker_mapping = data.get("speaker_mapping", {})
        if not isinstance(speaker_mapping, dict):
            speaker_mapping = {}
        for spk in all_speakers:
            if spk not in speaker_mapping:
                speaker_mapping[spk] = spk

        result = {
            "speakers": all_speakers,
            "speaker_mapping": speaker_mapping,
            "segments": normalized_segments
        }
        if is_repaired:
            result["is_partial"] = True
            result["warning"] = "La transcripción fue recortada por longitud máxima, pero se recuperaron con éxito todos los segmentos generados."
        return result

    @staticmethod
    def format_seconds(seconds: float) -> str:
        """Converts seconds into HH:MM:SS or MM:SS."""
        secs = int(seconds)
        mins = secs // 60
        hrs = mins // 60
        rem_secs = secs % 60
        rem_mins = mins % 60
        if hrs > 0:
            return f"{hrs:02d}:{rem_mins:02d}:{rem_secs:02d}"
        return f"{rem_mins:02d}:{rem_secs:02d}"

    @staticmethod
    def parse_time_to_seconds(time_str: str) -> float:
        """Parses MM:SS or HH:MM:SS into seconds float."""
        parts = time_str.strip().split(":")
        try:
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 1:
                return float(parts[0])
        except Exception:
            pass
        return 0.0
