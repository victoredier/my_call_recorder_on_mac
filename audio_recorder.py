import sounddevice as sd
import soundfile as sf
import queue
import threading
import sys

class AudioRecorder:
  """
  Handles audio recording in a separate thread to prevent blocking
  the main application UI.
  """
  def __init__(self):
    self.is_recording = False
    self.queue = queue.Queue()
    self.thread = None
    self.error_message = None
    self.is_paused = False

  def _callback(self, indata, frames, time, status):
    """Called by sounddevice for each block of audio data."""
    if status:
      print(f"Audio callback status: {status}", file=sys.stderr)
    self.queue.put(indata.copy())

  def _record_loop(self, filepath):
    """The main loop running in the background thread."""
    try:
      # Retrieve default input device properties
      device_info = sd.query_devices(sd.default.device[0], 'input')
      samplerate = int(device_info['default_samplerate'])
      channels = min(2, device_info['max_input_channels'])
      
      if channels < 1:
        raise ValueError("No input channels available on default device.")

      # Open sound file for writing
      with sf.SoundFile(filepath, mode='x', samplerate=samplerate,
                        channels=channels, subtype='PCM_24') as file:
        
        # Start the audio input stream
        with sd.InputStream(samplerate=samplerate, channels=channels,
                            callback=self._callback):
          
          # Read from queue and write to file
          while self.is_recording:
            try:
              data = self.queue.get(timeout=0.1)
              if not self.is_paused:
                file.write(data)
            except queue.Empty:
              # Continue checking the loop condition
              continue
              
    except Exception as e:
      self.error_message = str(e)
      print(f"Recording error: {e}", file=sys.stderr)
      self.is_recording = False

  def start_recording(self, filepath):
    """Starts the audio recording process."""
    if self.is_recording:
      return False
    
    self.error_message = None
    self.is_recording = True
    self.is_paused = False
    
    # Clear the queue of any residual data
    while not self.queue.empty():
      try:
        self.queue.get_nowait()
      except queue.Empty:
        break
      
    # Spawn background thread for the recording loop
    self.thread = threading.Thread(target=self._record_loop, args=(filepath,))
    self.thread.start()
    return True

  def stop_recording(self):
    """Signals the recording loop to stop and waits for completion."""
    if not self.is_recording:
      return False
    
    self.is_recording = False
    if self.thread:
      self.thread.join()
      
    return True

  def pause_recording(self):
    """Pauses the recording."""
    if not self.is_recording or self.is_paused:
      return False
    
    self.is_paused = True
    return True

  def resume_recording(self):
    """Resumes the recording."""
    if not self.is_recording or not self.is_paused:
      return False
    
    self.is_paused = False
    return True
