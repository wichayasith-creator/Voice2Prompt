import os
import sys
import io
import json
import wave
import requests

def get_default_config_path() -> str:
    appdata = os.getenv("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    cfg_dir = os.path.join(appdata, "Voice2Prompt")
    os.makedirs(cfg_dir, exist_ok=True)
    return os.path.join(cfg_dir, "config.json")

CONFIG_FILE = get_default_config_path()


def _candidate_env_files() -> list:
    candidates = []
    custom_env = os.getenv("VOICE2PROMPT_ENV_FILE", "").strip()
    if custom_env:
        candidates.append(custom_env)
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        candidates.append(os.path.join(exe_dir, ".env"))
        candidates.append(os.path.join(os.path.dirname(exe_dir), ".env"))
    src_dir = os.path.dirname(os.path.abspath(__file__))
    candidates.append(os.path.join(src_dir, ".env"))
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    candidates.append(os.path.join(appdata, "Voice2Prompt", ".env"))
    return candidates


def _load_env_groq_key(env_path: str = None) -> str:
    """
    Loads GROQ_API_KEY from process environment or a local .env file.
    Supports ENV_FILE=<path> pointer inside .env for external secret vaults.
    """
    env_key = os.getenv("GROQ_API_KEY", "").strip()
    if env_key:
        return env_key

    search_list = [env_path] if env_path else _candidate_env_files()
    for start_path in search_list:
        if not start_path or not os.path.exists(start_path):
            continue
        try:
            visited = set()
            cur_path = start_path
            while cur_path and os.path.exists(cur_path) and cur_path not in visited:
                visited.add(cur_path)
                next_path = None
                with open(cur_path, "r", encoding="utf-8", errors="ignore") as f:
                    for raw_line in f:
                        line = raw_line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if line.startswith("GROQ_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip("\"'")
                            if val:
                                return val
                        elif line.startswith("ENV_FILE="):
                            next_path = line.split("=", 1)[1].strip().strip("\"'")
                cur_path = next_path
        except Exception:
            pass
    return ""


class STTService:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or CONFIG_FILE
        self._key_from_env = False
        self.config = self._load_config()

    def _load_config(self) -> dict:
        data = {
            "groq_api_key": "",
            "language": "th",
            "model": "whisper-large-v3",
            "device_index": None,
            "auto_copy": True,
            "global_hotkey_enabled": True,
            "global_hotkey_combo": "Ctrl + Alt + Space"
        }
        # 1. Try loading from AppData config.json
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    data.update(saved)
            except Exception as e:
                print(f"Error reading config: {e}")

        # 2. If no key in config.json, fall back to environment / .env
        if not data.get("groq_api_key"):
            env_key = _load_env_groq_key()
            if env_key:
                data["groq_api_key"] = env_key
                self._key_from_env = True
        else:
            self._key_from_env = False

        return data

    def save_setting(self, key: str, value):
        """Update in-memory setting and persist to config.json (safely ignoring env keys)."""
        if key == "groq_api_key":
            # If user explicitly enters or modifies the key
            value = str(value).strip()
            self._key_from_env = False
            self.config[key] = value
        else:
            self.config[key] = value

        self._persist_config()

    def set_user_api_key(self, api_key: str):
        self.config["groq_api_key"] = api_key.strip()
        self._key_from_env = False
        self._persist_config()

    def _persist_config(self):
        r"""
        Saves configuration to %APPDATA%\Voice2Prompt\config.json.
        SECURITY RULE: If the API key was sourced from environment/.env, never write it to config.json!
        """
        to_save = dict(self.config)
        if self._key_from_env:
            # Strip key before saving to prevent leakage of environment credentials
            to_save["groq_api_key"] = ""

        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error persisting config: {e}")

    @staticmethod
    def chunk_wav_bytes(wav_bytes: bytes, max_seconds: int = 600) -> list:
        """
        Splits WAV audio into chunks not exceeding max_seconds (default 10 min / ~19.2 MB),
        preventing HTTP 413 Payload Too Large on Groq Whisper (25 MB limit).
        """
        try:
            with io.BytesIO(wav_bytes) as bio:
                with wave.open(bio, "rb") as wf:
                    channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    framerate = wf.getframerate()
                    n_frames = wf.getnframes()

                    chunk_frames = framerate * max_seconds
                    if n_frames <= chunk_frames:
                        return [wav_bytes]

                    chunks = []
                    frames_read = 0
                    while frames_read < n_frames:
                        to_read = min(chunk_frames, n_frames - frames_read)
                        data = wf.readframes(to_read)
                        frames_read += to_read

                        c_bio = io.BytesIO()
                        with wave.open(c_bio, "wb") as c_wf:
                            c_wf.setnchannels(channels)
                            c_wf.setsampwidth(sampwidth)
                            c_wf.setframerate(framerate)
                            c_wf.writeframes(data)
                        c_bio.seek(0)
                        chunks.append(c_bio.read())
                    return chunks
        except Exception:
            return [wav_bytes]

    def _transcribe_single_chunk(self, wav_bytes: bytes, language: str = None) -> str:
        api_key = self.config.get("groq_api_key", "").strip()
        if not api_key:
            raise ValueError("ยังไม่ได้ตั้งค่า GROQ_API_KEY กรุณาใส่ API Key ในการตั้งค่า")

        if not wav_bytes or len(wav_bytes) < 1000:
            return ""

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        files = {
            "file": ("recording.wav", wav_bytes, "audio/wav")
        }

        target_lang = language or self.config.get("language", "th")
        data = {
            "model": self.config.get("model", "whisper-large-v3"),
            "response_format": "json"
        }

        if target_lang and target_lang != "auto":
            data["language"] = target_lang

        # Context prompt for Thai/English tech & AI prompts
        data["prompt"] = "สนทนาภาษาไทยและอังกฤษ ป้อนคำสั่ง AI เขียนโค้ด พรอมต์"

        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)

        if response.status_code != 200:
            error_msg = response.text
            try:
                err_json = response.json()
                if "error" in err_json and "message" in err_json["error"]:
                    error_msg = err_json["error"]["message"]
            except Exception:
                pass
            raise RuntimeError(f"API Error ({response.status_code}): {error_msg}")

        result = response.json()
        return result.get("text", "").strip()

    def transcribe(self, wav_bytes: bytes, language: str = None) -> str:
        """
        Transcribes audio using Groq Whisper. Automatically handles chunking
        if recording exceeds 10 minutes (~19.2 MB).
        """
        chunks = self.chunk_wav_bytes(wav_bytes, max_seconds=600)
        results = []
        for chunk in chunks:
            text = self._transcribe_single_chunk(chunk, language=language)
            if text:
                results.append(text)

        return " ".join(results).strip()
