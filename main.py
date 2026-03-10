import os
import rumps
from datetime import datetime
from audio_recorder import AudioRecorder

class CallRecorderApp(rumps.App):
  """
  macOS Menu Bar application for recording audio calls.
  Provides a simple Start/Stop toggle UI.
  """
  def __init__(self):
    # Initialize with default microphone icon
    super(CallRecorderApp, self).__init__("🎙️")
    self.recorder = AudioRecorder()
    
    # Add Menu Items
    self.start_button = rumps.MenuItem("Start Recording", callback=self.on_start)
    self.stop_button = rumps.MenuItem("Stop Recording", callback=self.on_stop)
    self.menu = [self.start_button, self.stop_button]

  def _get_save_path(self):
    """Resolves and ensures the existence of the save directory."""
    default_path = os.path.expanduser("~/Recordings")
    path = os.environ.get("CALL_RECORDINGS_PATH", default_path)
    
    if not os.path.exists(path):
      try:
        os.makedirs(path)
      except Exception as e:
        rumps.alert("Directory Error", f"Unable to create recordings folder: {e}")
        return None
    return path

  def on_start(self, _):
    """Callback for the 'Start Recording' menu item."""
    if self.recorder.is_recording:
      return

    save_dir = self._get_save_path()
    if not save_dir:
      return

    filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.wav')
    filepath = os.path.join(save_dir, filename)

    # Begin the audio recording
    success = self.recorder.start_recording(filepath)
    if success:
      self.title = "🔴🎙️"  # Update icon to show active recording
      rumps.notification("Call Recorder", "Recording Started", f"Saving to {filename}")
    else:
      error_msg = self.recorder.error_message or "Unknown error."
      rumps.alert("Recording Error", f"Could not start audio device: {error_msg}")

  def on_stop(self, _):
    """Callback for the 'Stop Recording' menu item."""
    if not self.recorder.is_recording:
      return

    success = self.recorder.stop_recording()
    if success:
      self.title = "🎙️"  # Reset icon
      rumps.notification("Call Recorder", "Recording Stopped", "Audio successfully saved.")

if __name__ == "__main__":
  app = CallRecorderApp()
  app.run()
