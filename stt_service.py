import os
import sys
import io
import json
import wave
import logging
import requests

from i18n import detect_default_ui_lang, t

logger = logging.getLogger(__name__)


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
    Loads GROQ_API_KEY from process environment or a .env file.
    """
    env_key = os.getenv("GROQ_API_KEY", "").strip()
    if env_key:
        return env_key

    search_list = [env_path] if env_path else _candidate_env_files()
    for path in search_list:
        if not path or not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("GROQ_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip("\"'")
                        if val:
                            return val
        except Exception as e:
            logger.warning("Failed to read .env file at %s: %s", path, e)
    return ""


def _format_retry_wait(retry_after_header: str | None, ui_lang: str) -> str:
    if retry_after_header:
        val_str = str(retry_after_header).strip()
        try:
            secs = int(float(val_str))
            if secs > 0:
                return f"{secs} วินาที" if ui_lang == "th" else f"{secs} seconds"
        except ValueError:
            pass
    return "1 นาที" if ui_lang == "th" else "1 minute"


class STTService:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or CONFIG_FILE
        self._key_from_env = False
        self.config = self._load_config()

    def _load_config(self) -> dict:
        data = {
            "groq_api_key": "",
            "language": "th",
            "ui_language": detect_default_ui_lang(),
            "model": "whisper-large-v3",
            "device_index": None,
            "auto_copy": True,
            "global_hotkey_enabled": True,
            "global_hotkey_combo": "Ctrl + Alt + Space",
        }
        # 1. Try loading from AppData config.json
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    data.update(saved)
            except Exception as e:
                logger.warning("Error reading config %s: %s", self.config_path, e)

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
            to_save["groq_api_key"] = ""

        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning("Error persisting config %s: %s", self.config_path, e)

    @staticmethod
    def chunk_wav_bytes(wav_bytes: bytes, max_seconds: int = 600, ui_lang: str = "th") -> list:
        """
        Splits WAV audio into chunks not exceeding max_seconds (default 10 min / ~19.2 MB),
        preventing HTTP 413 Payload Too Large on Groq Whisper (25 MB limit).
        Raises ValueError if wav_bytes is not a valid WAV container.
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
        except Exception as e:
            logger.error("Invalid or corrupted WAV audio data in chunk_wav_bytes: %s", e)
            raise ValueError(t("err_invalid_wav", lang=ui_lang)) from e

    def _transcribe_single_chunk(self, wav_bytes: bytes, language: str = None) -> str:
        ui_lang = self.config.get("ui_language", "th")
        api_key = self.config.get("groq_api_key", "").strip()
        if not api_key:
            raise ValueError(t("err_no_api_key", lang=ui_lang))

        if not wav_bytes or len(wav_bytes) < 1000:
            return ""

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {api_key}",
        }
        files = {
            "file": ("recording.wav", wav_bytes, "audio/wav"),
        }

        target_lang = language or self.config.get("language", "th")
        data = {
            "model": self.config.get("model", "whisper-large-v3"),
            "response_format": "json",
        }

        if target_lang and target_lang != "auto":
            data["language"] = target_lang

        # Send Thai context prompt ONLY when spoken language is Thai ('th') or Auto ('auto')
        if target_lang in ("th", "auto", None, ""):
            data["prompt"] = "สนทนาภาษาไทยและอังกฤษ ป้อนคำสั่ง AI เขียนโค้ด พรอมต์"

        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        except requests.exceptions.Timeout as e:
            logger.warning("Groq transcription request timed out.")
            raise RuntimeError(t("err_timeout", lang=ui_lang)) from e
        except requests.exceptions.ConnectionError as e:
            logger.warning("Groq transcription connection error.")
            raise RuntimeError(t("err_network_conn", lang=ui_lang)) from e
        except requests.exceptions.RequestException as e:
            logger.warning("Groq transcription network exception.")
            raise RuntimeError(t("err_network_conn", lang=ui_lang)) from e

        status = response.status_code
        if status != 200:
            if status == 429:
                headers_dict = getattr(response, "headers", {}) or {}
                retry_hdr = headers_dict.get("Retry-After") or headers_dict.get("retry-after")
                wait_str = _format_retry_wait(retry_hdr, ui_lang)
                raise RuntimeError(t("err_rate_limit_429", lang=ui_lang, wait=wait_str))
            if status in (401, 403):
                raise RuntimeError(t("err_auth_401_403", lang=ui_lang))
            if status >= 500:
                raise RuntimeError(t("err_server_5xx", lang=ui_lang, code=status))
            raise RuntimeError(t("err_generic_api", lang=ui_lang, code=status))

        result = response.json()
        return result.get("text", "").strip()

    def transcribe(self, wav_bytes: bytes, language: str = None) -> str:
        """
        Transcribes audio using Groq Whisper. Automatically handles chunking
        if recording exceeds 10 minutes (~19.2 MB).
        """
        ui_lang = self.config.get("ui_language", "th")
        chunks = self.chunk_wav_bytes(wav_bytes, max_seconds=600, ui_lang=ui_lang)
        results = []
        for chunk in chunks:
            text = self._transcribe_single_chunk(chunk, language=language)
            if text:
                results.append(text)

        return " ".join(results).strip()
