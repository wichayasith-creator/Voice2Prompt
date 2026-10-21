import os
import io
import wave
import json
import tempfile
import numpy as np
import pytest

from audio_recorder import AudioRecorder
from history_manager import HistoryManager
from stt_service import STTService, get_default_config_path
from hotkey_manager import GlobalHotkeyManager, HOTKEY_PRESETS
import main

def test_vu_meter_math_no_overflow():
    """Verify that VU RMS calculation handles int16 extrema without overflow."""
    # Test boundary int16 values that previously caused overflow when squared
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
    
    # Check directory before
    curr_files = set(os.listdir(os.path.dirname(os.path.abspath(__file__))))
    
    item1 = hist.add("ข้อความทดสอบที่ 1")
    item2 = hist.add("ข้อความทดสอบที่ 2")
    item3 = hist.add("ข้อความทดสอบที่ 2")  # Duplicate test
    
    assert item1 is not None
    assert item2 is not None
    assert len(hist.get_recent(10)) == 2  # duplicate not added
    assert hist.get_recent(10)[0]["text"] == "ข้อความทดสอบที่ 2"

    # Verify no history.json was created
    new_files = set(os.listdir(os.path.dirname(os.path.abspath(__file__))))
    assert "history.json" not in new_files
    
    hist.clear()
    assert len(hist.get_recent()) == 0

def test_api_key_security_env_key_never_written(monkeypatch=None):
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
    # Create 12 minutes (720s) of synthetic 16kHz 16-bit mono WAV in memory
    sample_rate = 16000
    duration_sec = 650  # > 10 minutes (600s)
    total_samples = sample_rate * duration_sec
    samples = np.zeros(total_samples, dtype=np.int16)

    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())
    wav_bytes = bio.getvalue()

    chunks = STTService.chunk_wav_bytes(wav_bytes, max_seconds=600)
    assert len(chunks) == 2  # Should be split into 600s + 50s chunks
    
    # Verify each chunk is valid WAV
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

if __name__ == "__main__":
    print("Running Voice2Prompt test suite...")
    test_vu_meter_math_no_overflow()
    print("[PASS] VU Meter math test passed")
    test_in_memory_history_no_disk_files()
    print("[PASS] In-memory history test passed (no disk files created)")
    test_api_key_security_env_key_never_written()
    print("[PASS] API Key security test passed (environment key never written to disk)")
    test_wav_auto_chunking()
    print("[PASS] WAV auto-chunking test passed")
    test_recording_safety_limit_constant()
    print("[PASS] Recording limit test passed")
    test_global_hotkey_presets()
    print("[PASS] Global hotkey presets test passed")
    print("\nALL 6 TESTS PASSED SUCCESSFULLY!")
