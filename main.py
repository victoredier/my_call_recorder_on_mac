import os
import subprocess
import webbrowser
from datetime import datetime
import rumps

from audio_recorder import AudioRecorder, check_microphone_permission
from storage_manager import StorageManager
from server import start_server

# Paths to minimalist menu bar icons
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

def _find_asset(name: str) -> str:
  candidates = [
      os.path.join(PROJECT_DIR, "assets", name),
      os.path.join(PROJECT_DIR, "..", "Resources", "assets", name),
      os.path.join(PROJECT_DIR, "..", "Resources", name),
      os.path.join(PROJECT_DIR, "Resources", "assets", name),
  ]
  for c in candidates:
    if os.path.exists(c):
      return os.path.abspath(c)
  return os.path.join(PROJECT_DIR, "assets", name)

ICON_IDLE = _find_asset("menu_icon.png")
ICON_RECORDING = _find_asset("menu_icon_recording.png")
ICON_PAUSED = _find_asset("menu_icon_paused.png")

# Fallback protection if macOS sandbox restricts Application Support
_orig_app_support = rumps.application_support
def _safe_app_support(name):
  try:
    return _orig_app_support(name)
  except Exception:
    fallback = os.path.expanduser("~/.call_recorder")
    os.makedirs(fallback, exist_ok=True)
    return fallback
rumps.application_support = _safe_app_support

class CallRecorderApp(rumps.App):
  """
  macOS Menu Bar application for recording audio calls.
  Saves calls into dedicated subfolders with metadata and audio files.
  Includes a local web dashboard for listing, transcribing with Gemini, and editing.
  """
  def __init__(self):
    super(CallRecorderApp, self).__init__(
        name="Call Recorder",
        title=None,
        icon=ICON_IDLE if os.path.exists(ICON_IDLE) else "🎙️",
        template=True if os.path.exists(ICON_IDLE) else None
    )
    self.recorder = AudioRecorder()
    self.storage = StorageManager()
    self.current_meeting = None
    self.server_port = 5050

    # Start local HTTP dashboard server in background thread
    try:
      self.server = start_server(port=self.server_port)
    except Exception as e:
      print(f"Error starting local dashboard server: {e}")
      self.server = None
    
    # Check microphone permission on startup so the system prompt appears if needed
    check_microphone_permission()

    # Menu Items
    self.start_button = rumps.MenuItem("Iniciar Grabación", callback=self.on_start)
    self.pause_button = rumps.MenuItem("Pausar Grabación", callback=self.on_pause_toggle)
    self.stop_button = rumps.MenuItem("Detener Grabación", callback=self.on_stop)
    self.dashboard_button = rumps.MenuItem("Abrir Dashboard de Llamadas...", callback=self.open_dashboard)
    self.folder_button = rumps.MenuItem("Abrir Carpeta en Finder", callback=self.open_folder)

    self.menu = [
        self.start_button,
        self.pause_button,
        self.stop_button,
        None,  # Separator
        self.dashboard_button,
        self.folder_button,
        None   # Separator (rumps adds Quit below)
    ]

  def on_start(self, _):
    """Starts recording audio into a new dedicated meeting subfolder."""
    if self.recorder.is_recording:
      return

    now = datetime.now()
    default_name = f"Llamada {now.strftime('%d/%m/%Y %H:%M')}"
    
    try:
      self.current_meeting = self.storage.create_meeting(name=default_name)
    except Exception as e:
      rumps.alert("Error de Almacenamiento", f"No se pudo crear la carpeta de grabación: {e}")
      return

    audio_path = self.current_meeting["audio_path"]
    folder_name = self.current_meeting["folder_name"]

    # Begin the audio recording
    success = self.recorder.start_recording(audio_path)
    if success:
      if os.path.exists(ICON_RECORDING):
        self.template = False
        self.icon = ICON_RECORDING
      self.title = " 🔴"
      self.pause_button.title = "Pausar Grabación"
      rumps.notification("Call Recorder", "Grabación Iniciada", f"Guardando en carpeta: {folder_name}")
    else:
      error_msg = self.recorder.error_message or "Error desconocido."
      rumps.alert("Error de Grabación", f"No se pudo iniciar el micrófono:\n\n{error_msg}")
      if "Ajustes del Sistema" in error_msg:
        try:
          subprocess.Popen(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"])
        except Exception:
          pass

  def on_stop(self, _):
    """Stops audio recording and finalizes meeting metadata without prompting."""
    if not self.recorder.is_recording:
      return

    success = self.recorder.stop_recording()
    if success and self.current_meeting:
      self.title = None
      if os.path.exists(ICON_IDLE):
        self.template = True
        self.icon = ICON_IDLE
      self.pause_button.title = "Pausar Grabación"

      meeting_dir = self.current_meeting["meeting_dir"]
      meeting_name = self.current_meeting.get("name", "Llamada")

      # Finalize metadata with duration and name
      self.storage.finalize_recording(meeting_dir, name=meeting_name)
      rumps.notification(
          "Call Recorder",
          "Grabación Guardada",
          f"Reunión: {meeting_name}\nAbre el Dashboard para ver o transcribir."
      )
      self.current_meeting = None

  def on_pause_toggle(self, sender):
    """Callback for the 'Pause/Resume Recording' menu item."""
    if not self.recorder.is_recording:
      return

    if self.recorder.is_paused:
      if self.recorder.resume_recording():
        sender.title = "Pausar Grabación"
        if os.path.exists(ICON_RECORDING):
          self.template = False
          self.icon = ICON_RECORDING
        self.title = " 🔴"
    else:
      if self.recorder.pause_recording():
        sender.title = "Reanudar Grabación"
        if os.path.exists(ICON_PAUSED):
          self.template = False
          self.icon = ICON_PAUSED
        self.title = " ⏸️"

  def open_dashboard(self, _):
    """Opens the web dashboard in the default browser."""
    url = f"http://localhost:{self.server_port}"
    webbrowser.open(url)

  def open_folder(self, _):
    """Opens the recordings root directory in macOS Finder."""
    base_dir = self.storage.base_path
    try:
      subprocess.Popen(["open", base_dir])
    except Exception as e:
      rumps.alert("Error", f"No se pudo abrir Finder: {e}")

if __name__ == "__main__":
  app = CallRecorderApp()
  app.run()
