import os
import io
import wave
import json
import tempfile
from unittest.mock import patch, MagicMock
import numpy as np
import pytest
import requests

from version import __version__
from i18n import (
    TRANSLATIONS,
    SUPPORTED_SPOKEN_LANGUAGES,
    VALID_SPOKEN_CODES,
    t,
    get_spoken_language_display_map,
)
from audio_recorder import AudioRecorder
from history_manager import HistoryManager
from stt_service import STTService, get_default_config_path
from hotkey_manager import GlobalHotkeyManager, HOTKEY_PRESETS
import main


def _make_dummy_wav(duration_sec: int = 1, sample_rate: int = 16000) -> bytes:
    samples = np.zeros(sample_rate * duration_sec, dtype=np.int16)
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())
    return bio.getvalue()


def test_vu_meter_math_no_overflow():
    """Verify that VU RMS calculation handles int16 extrema without overflow."""
    test_data = np.array([-32768, 32767, 16000, -16000, 500, -500, 0], dtype=np.int16)

    float_data = test_data.astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(float_data**2)))
    volume = min(1.0, max(0.0, rms * 4.0))

    assert 0.0 <= volume <= 1.0
    assert not np.isnan(volume)
    assert not np.isinf(volume)


def test_in_memory_history_no_disk_files():
    """Verify history is stored purely in RAM and never touches disk."""
    hist = HistoryManager()

    curr_files = set(os.listdir(os.path.dirname(os.path.abspath(__file__))))

    item1 = hist.add("ข้อความทดสอบที่ 1")
    item2 = hist.add("ข้อความทดสอบที่ 2")
    item3 = hist.add("ข้อความทดสอบที่ 2")  # Duplicate test

    assert item1 is not None
    assert item2 is not None
    assert len(hist.get_recent(10)) == 2  # duplicate not added
    assert hist.get_recent(10)[0]["text"] == "ข้อความทดสอบที่ 2"

    new_files = set(os.listdir(os.path.dirname(os.path.abspath(__file__))))
    assert "history.json" not in new_files

    hist.clear()
    assert len(hist.get_recent()) == 0


def test_api_key_security_env_key_never_written():
    """Verify that credentials loaded from environment / .env are NEVER written to config.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_cfg = os.path.join(tmpdir, "config.json")
        orig_env = os.environ.get("GROQ_API_KEY")
        try:
            if not orig_env:
                os.environ["GROQ_API_KEY"] = "gsk_test_env_secret_key_do_not_persist_999"
            service = STTService(config_path=tmp_cfg)
            assert service._key_from_env is True
            assert len(service.config.get("groq_api_key", "")) > 10

            # Save any other setting
            service.save_setting("language", "en")

            # Read the physical file from disk
            assert os.path.exists(tmp_cfg)
            with open(tmp_cfg, "r", encoding="utf-8") as f:
                saved_json = json.load(f)

            # CRITICAL SECURITY ASSERTION: File MUST NOT contain the env API key!
            assert saved_json.get("groq_api_key") == "", "SECURITY LEAK: environment key was saved to disk!"

            # Now test when user explicitly sets their own key
            service.set_user_api_key("gsk_user_custom_key_12345")
            assert service._key_from_env is False
            with open(tmp_cfg, "r", encoding="utf-8") as f:
                saved_json = json.load(f)
            assert saved_json.get("groq_api_key") == "gsk_user_custom_key_12345"
        finally:
            if orig_env is None:
                os.environ.pop("GROQ_API_KEY", None)
            else:
                os.environ["GROQ_API_KEY"] = orig_env


def test_wav_auto_chunking():
    """Verify that WAV bytes exceeding 10 minutes are properly chunked."""
    sample_rate = 16000
    duration_sec = 650  # > 10 minutes (600s)
    wav_bytes = _make_dummy_wav(duration_sec=duration_sec, sample_rate=sample_rate)

    chunks = STTService.chunk_wav_bytes(wav_bytes, max_seconds=600)
    assert len(chunks) == 2  # Should be split into 600s + 50s chunks

    for c in chunks:
        with io.BytesIO(c) as c_bio:
            with wave.open(c_bio, "rb") as c_wf:
                assert c_wf.getframerate() == 16000
                assert c_wf.getnchannels() == 1


def test_recording_safety_limit_constant():
    """Verify safety recording duration is 12 minutes (720 seconds)."""
    assert main.MAX_RECORDING_SECONDS == 720


def test_global_hotkey_presets():
    """Verify hotkey presets are registered."""
    assert "Ctrl + Alt + Space" in HOTKEY_PRESETS
    assert "Ctrl + Shift + R" in HOTKEY_PRESETS
    assert "F8" in HOTKEY_PRESETS


def test_audio_recorder_stream_open_failure_recovers():
    """Item 1: If sd.InputStream fails to open/start, is_recording must stay False and next attempt must succeed."""
    rec = AudioRecorder()

    with patch("audio_recorder.sd.InputStream", side_effect=RuntimeError("Microphone disconnected")):
        with pytest.raises(RuntimeError, match="Microphone disconnected"):
            rec.start_recording()

    # State must remain clean after failure
    assert rec.is_recording is False
    assert rec._stream is None

    # Subsequent start_recording() with working stream must succeed
    mock_stream = MagicMock()
    with patch("audio_recorder.sd.InputStream", return_value=mock_stream):
        rec.start_recording()
        assert rec.is_recording is True
        assert rec._stream is mock_stream
        mock_stream.start.assert_called_once()
        rec.stop_recording()
        assert rec.is_recording is False


def test_hotkey_manager_start_returns_false_on_conflict():
    """Item 2: GlobalHotkeyManager.start() returns False when RegisterHotKey fails (conflict), True when it succeeds."""
    mgr = GlobalHotkeyManager(callback=lambda: None)

    with patch("hotkey_manager.ctypes.windll.user32") as mock_user32:
        # Simulate conflict: RegisterHotKey returns 0
        mock_user32.RegisterHotKey.return_value = 0
        ok = mgr.start("Ctrl + Alt + Space")
        assert ok is False
        assert mgr.registered is False
        mgr.stop()

        # Simulate success: RegisterHotKey returns 1, GetMessageW returns 0 (exit loop cleanly)
        mock_user32.RegisterHotKey.return_value = 1
        mock_user32.GetMessageW.return_value = 0
        ok2 = mgr.start("F8")
        assert ok2 is True
        assert mgr.registered is True
        mgr.stop()


def test_corrupted_wav_raises_value_error():
    """Item 4: Corrupted WAV bytes raise a clear ValueError instead of silently passing."""
    bad_bytes = b"NOT_A_VALID_WAV_HEADER_1234567890"
    with pytest.raises(ValueError) as exc_info:
        STTService.chunk_wav_bytes(bad_bytes, max_seconds=600, ui_lang="en")
    assert "corrupted" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


def test_stt_conditional_thai_prompt_and_11_languages():
    """Items 3 & 12: Verify all 11 spoken languages + auto, and ensure Thai prompt is sent ONLY for th/auto."""
    expected_codes = {"th", "en", "zh", "ja", "ko", "es", "fr", "de", "hi", "id", "vi", "auto"}
    assert VALID_SPOKEN_CODES == expected_codes
    assert len(SUPPORTED_SPOKEN_LANGUAGES) == 12

    wav_bytes = _make_dummy_wav(duration_sec=1)

    with tempfile.TemporaryDirectory() as tmpdir:
        service = STTService(config_path=os.path.join(tmpdir, "config.json"))
        service.config["groq_api_key"] = "gsk_dummy_key_for_unit_test"

        for code in expected_codes:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"text": f"transcribed_{code}"}

            with patch("stt_service.requests.post", return_value=mock_resp) as mock_post:
                result = service.transcribe(wav_bytes, language=code)
                assert result == f"transcribed_{code}"
                sent_data = mock_post.call_args.kwargs["data"]

                if code == "auto":
                    assert "language" not in sent_data
                    assert "prompt" in sent_data
                elif code == "th":
                    assert sent_data["language"] == "th"
                    assert "prompt" in sent_data
                else:
                    assert sent_data["language"] == code
                    assert "prompt" not in sent_data, f"Thai prompt must NOT be sent for language={code}"


def test_i18n_translation_keys_match_all_11_ui_languages():
    """Item 11: Verify all 11 UI languages have identical keys and non-empty strings."""
    expected_ui_langs = {"th", "en", "zh", "ja", "ko", "es", "fr", "de", "hi", "id", "vi"}
    assert set(TRANSLATIONS.keys()) == expected_ui_langs

    base_keys = set(TRANSLATIONS["en"].keys())
    for lang_code in expected_ui_langs:
        lang_keys = set(TRANSLATIONS[lang_code].keys())
        assert lang_keys == base_keys, f"Key mismatch in UI language '{lang_code}'"
        for k in base_keys:
            val = TRANSLATIONS[lang_code][k]
            assert isinstance(val, str) and len(val.strip()) > 0, f"Empty translation for {lang_code}.{k}"
        assert len(get_spoken_language_display_map(lang_code)) == 12


def test_stt_error_messages_429_401_5xx_timeout_conn():
    """Items 9 & 16: Verify friendly (>20 words) bilingual error messages for 429, 401/403, 5xx, Timeout, ConnectionError."""
    wav_bytes = _make_dummy_wav(duration_sec=1)
    secret_key = "gsk_super_secret_should_never_appear_in_error"

    with tempfile.TemporaryDirectory() as tmpdir:
        service = STTService(config_path=os.path.join(tmpdir, "config.json"))
        service.config["groq_api_key"] = secret_key

        for ui_lang in ("th", "en"):
            service.config["ui_lang"] = ui_lang

            # 1. HTTP 429 with Retry-After header
            resp_429 = MagicMock(status_code=429, headers={"Retry-After": "25"})
            with patch("stt_service.requests.post", return_value=resp_429):
                with pytest.raises(RuntimeError) as exc_429:
                    service.transcribe(wav_bytes, language="en")
                msg = str(exc_429.value)
                assert len(msg.split()) > 20
                assert "25" in msg
                assert secret_key not in msg
                assert "Traceback" not in msg

            # 2. HTTP 429 without Retry-After header
            resp_429_no_hdr = MagicMock(status_code=429, headers={})
            with patch("stt_service.requests.post", return_value=resp_429_no_hdr):
                with pytest.raises(RuntimeError) as exc_429_b:
                    service.transcribe(wav_bytes, language="en")
                msg = str(exc_429_b.value)
                assert len(msg.split()) > 20
                assert secret_key not in msg

            # 3. HTTP 401 Unauthorized
            resp_401 = MagicMock(status_code=401, headers={})
            with patch("stt_service.requests.post", return_value=resp_401):
                with pytest.raises(RuntimeError) as exc_401:
                    service.transcribe(wav_bytes, language="en")
                msg = str(exc_401.value)
                assert len(msg.split()) > 20
                assert secret_key not in msg

            # 4. HTTP 503 Server Error
            resp_503 = MagicMock(status_code=503, headers={})
            with patch("stt_service.requests.post", return_value=resp_503):
                with pytest.raises(RuntimeError) as exc_503:
                    service.transcribe(wav_bytes, language="en")
                msg = str(exc_503.value)
                assert len(msg.split()) > 20
                assert "503" in msg
                assert secret_key not in msg

            # 5. Timeout
            with patch("stt_service.requests.post", side_effect=requests.exceptions.Timeout("timed out")):
                with pytest.raises(RuntimeError) as exc_to:
                    service.transcribe(wav_bytes, language="en")
                msg = str(exc_to.value)
                assert len(msg.split()) > 20
                assert secret_key not in msg

            # 6. ConnectionError
            with patch("stt_service.requests.post", side_effect=requests.exceptions.ConnectionError("DNS fail")):
                with pytest.raises(RuntimeError) as exc_conn:
                    service.transcribe(wav_bytes, language="en")
                msg = str(exc_conn.value)
                assert len(msg.split()) > 20
                assert secret_key not in msg


def test_version_semver():
    """Item 15: Verify semantic version string."""
    assert __version__ == "0.1.0"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
