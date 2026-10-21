import io
import wave
import threading
import numpy as np
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.is_recording = False
        self._frames = []
        self._stream = None
        self._lock = threading.Lock()
        self.current_volume = 0.0  # Normalized 0.0 to 1.0 for VU meter

    def _audio_callback(self, indata, frames, time_info, status):
        if not self.is_recording:
            return
        data = indata.copy()
        with self._lock:
            self._frames.append(data)

        # Calculate volume level (RMS) safely with float32 normalization
        try:
            float_data = data.astype(np.float32) / 32768.0
            rms = float(np.sqrt(np.mean(float_data**2)))
            self.current_volume = min(1.0, max(0.0, rms * 4.0))
        except Exception:
            self.current_volume = 0.0

    def start_recording(self, device_index=None):
        if self.is_recording:
            return
        with self._lock:
            self._frames = []
        self.current_volume = 0.0

        stream = None
        try:
            stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16",
                device=device_index,
                callback=self._audio_callback,
            )
            stream.start()
            self._stream = stream
            self.is_recording = True
        except Exception:
            self.is_recording = False
            if stream is not None:
                try:
                    stream.close()
                except Exception:
                    pass
            self._stream = None
            raise

    def stop_recording(self) -> bytes:
        if not self.is_recording:
            return b""
        self.is_recording = False
        self.current_volume = 0.0

        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        with self._lock:
            if not self._frames:
                return b""
            audio_data = np.concatenate(self._frames, axis=0)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

        wav_buffer.seek(0)
        return wav_buffer.read()

    @staticmethod
    def list_input_devices():
        devices = []
        try:
            device_list = sd.query_devices()
            default_in = sd.default.device[0]
            for idx, d in enumerate(device_list):
                if d.get("max_input_channels", 0) > 0:
                    name = d.get("name", f"Device {idx}")
                    devices.append({
                        "index": idx,
                        "name": name,
                        "is_default": (idx == default_in),
                    })
        except Exception as e:
            print(f"Error querying audio devices: {e}")
        return devices
