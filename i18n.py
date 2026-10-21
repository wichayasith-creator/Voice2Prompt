# -*- coding: utf-8 -*-
"""
i18n.py — Bilingual (Thai / English) string table and language helpers for Voice2Prompt.
"""
import ctypes
import locale

SUPPORTED_UI_LANGUAGES = {
    "th": "ไทย (Thai)",
    "en": "English",
}

# Verified ISO-639-1 codes supported by Groq whisper-large-v3
SUPPORTED_SPOKEN_LANGUAGES = [
    ("th", {"th": "ไทย (Thai - th)", "en": "Thai (ไทย - th)"}),
    ("en", {"th": "อังกฤษ (English - en)", "en": "English (en)"}),
    ("zh", {"th": "จีน (Chinese - zh)", "en": "Chinese (中文 - zh)"}),
    ("ja", {"th": "ญี่ปุ่น (Japanese - ja)", "en": "Japanese (日本語 - ja)"}),
    ("ko", {"th": "เกาหลี (Korean - ko)", "en": "Korean (한국어 - ko)"}),
    ("es", {"th": "สเปน (Spanish - es)", "en": "Spanish (Español - es)"}),
    ("fr", {"th": "ฝรั่งเศส (French - fr)", "en": "French (Français - fr)"}),
    ("de", {"th": "เยอรมัน (German - de)", "en": "German (Deutsch - de)"}),
    ("hi", {"th": "ฮินดี (Hindi - hi)", "en": "Hindi (हिन्दी - hi)"}),
    ("id", {"th": "อินโดนีเซีย (Indonesian - id)", "en": "Indonesian (Bahasa - id)"}),
    ("vi", {"th": "เวียดนาม (Vietnamese - vi)", "en": "Vietnamese (Tiếng Việt - vi)"}),
    ("auto", {"th": "ตรวจจับอัตโนมัติ (Auto-detect)", "en": "Auto-detect Language"}),
]

VALID_SPOKEN_CODES = {code for code, _ in SUPPORTED_SPOKEN_LANGUAGES}


def detect_default_ui_lang() -> str:
    """Return 'th' if Windows UI / system locale is Thai, otherwise 'en'."""
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        # 0x041e is Thai (th-TH), primary language mask 0x3ff == 0x1e
        if (lang_id & 0x3FF) == 0x1E:
            return "th"
        if lang_id != 0:
            return "en"
    except Exception:
        pass

    try:
        loc, _ = locale.getlocale()
        if loc and loc.lower().startswith(("th", "thai")):
            return "th"
    except Exception:
        pass
    return "en"


TRANSLATIONS = {
    "th": {
        "app_title": "Voice2Prompt v{version} — แปลงเสียงพูดเป็นข้อความสำหรับคุยกับ AI",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ ตั้งค่า",
        "switch_ontop": "📌 ปักหมุดบนสุด",
        "btn_record_idle": "🔴 กดเพื่อพูด (Record / Spacebar)",
        "btn_record_listening": "⏹️ กำลังฟัง... กดเพื่อหยุด (Stop)",
        "btn_record_processing": "⏳ กำลังแปลงเสียง...",
        "status_ready": "⚪ พร้อมบันทึกเสียง (กดปุ่มหรือ Spacebar)",
        "status_recording": "🔴 กำลังบันทึกเสียง...",
        "status_auto_limit": "⏳ หยุดอัตโนมัติ (ครบ 12 นาที — ขีดจำกัดไฟล์ 25 MB)...",
        "status_processing_groq": "⏳ กำลังส่งประมวลผล (Groq Whisper)...",
        "status_no_audio": "⚪ ไม่พบข้อมูลเสียง",
        "status_no_speech": "⚪ ตรวจไม่พบเสียงพูด",
        "status_error": "❌ เกิดข้อผิดพลาด",
        "status_done_copied": "✅ แปลงเสียงและคัดลอกลง Clipboard แล้ว!",
        "status_done": "✅ แปลงเสียงเรียบร้อย!",
        "status_copied_history": "✅ คัดลอกข้อความจากประวัติแล้ว!",
        "status_loaded_history": "📝 โหลดข้อความเข้าช่องแก้ไขแล้ว",
        "status_settings_saved": "✅ บันทึกการตั้งค่าเรียบร้อย",
        "status_hotkey_conflict": "⚠️ ปุ่มลัด ({combo}) ถูกใช้อยู่โดยโปรแกรมอื่น กรุณาเปลี่ยนในหน้าตั้งค่า",
        "editor_title": "📝 ข้อความสำหรับส่งให้ AI (สามารถพิมพ์แก้ไขได้โดยตรง):",
        "char_count": "{count} ตัวอักษร",
        "btn_copy": "📋 คัดลอกข้อความ (Copy to Clipboard)",
        "btn_copied_flash": "✅ คัดลอกเรียบร้อยแล้ว!",
        "check_autocopy": "📋 Copy อัตโนมัติ",
        "check_append": "ต่อท้ายข้อความเดิม",
        "btn_clear": "🧹 ล้าง",
        "hist_title": "🕒 ประวัติ 10 ข้อความล่าสุด",
        "btn_clear_hist": "ล้าง",
        "hist_empty": "ยังไม่มีประวัติข้อความ (เก็บเฉพาะในเซสชัน RAM)",
        "btn_hist_use": "✏️ ใช้",
        "btn_hist_copy": "📋 Copy",
        "confirm_clear_hist_title": "ยืนยัน",
        "confirm_clear_hist_msg": "ต้องการล้างประวัติข้อความทั้งหมดหรือไม่?",
        "err_rec_title": "เกิดข้อผิดพลาดในการบันทึกเสียง",
        "err_stt_title": "ข้อผิดพลาดในการแปลงเสียง",
        "settings_title": "ตั้งค่า Voice2Prompt (v{version})",
        "settings_ui_lang": "💬 ภาษาหน้าจอโปรแกรม (UI Language):",
        "settings_mic": "🎙️ ไมโครโฟน (Audio Input Device):",
        "settings_default_mic": "ไมโครโฟนเริ่มต้น (Default Microphone)",
        "settings_api_key": "🔑 Groq API Key (รับคีย์ฟรีได้ที่ console.groq.com หรือตั้งใน .env):",
        "settings_spoken_lang": "🌐 ภาษาที่ใช้พูด (Spoken Language):",
        "settings_hotkey_header": "⌨️ ระบบปุ่มลัด Global Hotkey (กดได้จากทุกหน้าต่าง):",
        "settings_hotkey_enable": "เปิดใช้งาน Global Hotkey",
        "settings_btn_save": "บันทึกการตั้งค่า",
        # Detailed, user-friendly error messages (>20 words, 3 parts: what happened, what to do, audio retention truth)
        "err_no_api_key": (
            "ยังไม่ได้ตั้งค่า Groq API Key สำหรับแปลงเสียง กรุณากดปุ่ม 'ตั้งค่า' (⚙️) มุมขวาบนเพื่อใส่คีย์ของคุณ (รับฟรีที่ console.groq.com) "
            "หมายเหตุ: เสียงที่เพิ่งอัดไว้ไม่ได้ถูกเก็บค้างไว้ในระบบ กรุณากดอัดเสียงใหม่อีกครั้งหลังใส่คีย์เสร็จครับ"
        ),
        "err_invalid_wav": (
            "ข้อมูลไฟล์เสียง WAV ในหน่วยความจำเสียหายหรือไม่ถูกต้องทำให้ไม่สามารถตัดแบ่งไฟล์ได้ "
            "กรุณาตรวจสอบการเชื่อมต่อไมโครโฟนแล้วลองกดอัดเสียงใหม่อีกครั้ง (เสียงรอบที่ผิดพลาดไม่ได้ถูกเก็บไว้ในระบบครับ)"
        ),
        "err_rate_limit_429": (
            "ตอนนี้คุณเรียกใช้งานถี่เกินโควตาฟรีของ Groq ในหนึ่งนาทีแล้วครับ (ไม่ใช่ตัวโปรแกรมเสียนะครับ) "
            "กรุณารอประมาณ {wait} แล้วค่อยกดอัดเสียงใหม่อีกครั้ง เนื่องจากโปรแกรมไม่ได้เก็บไฟล์เสียงที่ล้มเหลวค้างไว้ในหน่วยความจำ "
            "หากพบปัญหานี้บ่อย แนะนำให้พูดต่อเนื่องให้ยาวขึ้นต่อการกดหนึ่งครั้ง หรืออัปเกรดแผนการใช้งานบัญชี Groq ของคุณครับ"
        ),
        "err_auth_401_403": (
            "ไม่สามารถยืนยันตัวตนกับระบบ Groq ได้ เนื่องจาก API Key ไม่ถูกต้องหรือถูกระงับการใช้งาน "
            "กรุณาเปิดหน้า 'ตั้งค่า' (⚙️) เพื่อตรวจสอบและวาง Groq API Key ที่ถูกต้องใหม่อีกครั้ง "
            "ทั้งนี้เสียงที่คุณเพิ่งพูดไม่ได้ถูกบันทึกเก็บไว้ในเครื่อง กรุณากดอัดเสียงใหม่หลังจากแก้ไขคีย์เรียบร้อยแล้วครับ"
        ),
        "err_network_conn": (
            "ไม่สามารถเชื่อมต่ออินเทอร์เน็ตไปยังเซิร์ฟเวอร์ของ Groq ได้ในขณะนี้ (อาจเกิดจากเน็ตหลุดหรือไฟร์วอลล์บล็อก) "
            "กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ตของคุณแล้วลองใหม่อีกครั้ง "
            "หมายเหตุ: เพื่อความเป็นส่วนตัว โปรแกรมไม่ได้บันทึกเสียงที่ส่งไม่สำเร็จไว้บนดิสก์ กรุณากดอัดเสียงใหม่เมื่ออินเทอร์เน็ตพร้อมใช้งานครับ"
        ),
        "err_timeout": (
            "การส่งเสียงไปประมวลผลที่เซิร์ฟเวอร์ Groq ใช้เวลานานเกินกำหนด (Timeout) อาจเกิดจากอินเทอร์เน็ตช้าหรือไฟล์เสียงมีขนาดใหญ่ "
            "กรุณาตรวจสอบสัญญาณอินเทอร์เน็ตแล้วลองกดอัดเสียงใหม่อีกครั้ง เนื่องจากเสียงรอบก่อนไม่ได้ถูกเก็บค้างไว้ในหน่วยความจำครับ"
        ),
        "err_server_5xx": (
            "เซิร์ฟเวอร์ของ Groq ขัดข้องชั่วคราว (HTTP {code}) ไม่ได้เกิดจากความผิดพลาดของโปรแกรมในเครื่องของคุณครับ "
            "กรุณาเว้นระยะรอสักครู่แล้วค่อยกดอัดเสียงใหม่อีกครั้ง เนื่องจากโปรแกรมไม่ได้เก็บไฟล์เสียงที่ส่งไม่สำเร็จค้างไว้ในระบบครับ"
        ),
        "err_generic_api": (
            "การแปลงเสียงผ่านระบบ Groq ขัดข้อง (รหัสสถานะ HTTP {code}) กรุณาตรวจสอบการตั้งค่าหรือลองใหม่อีกครั้งในภายหลัง "
            "ทั้งนี้โปรแกรมไม่ได้บันทึกไฟล์เสียงที่ล้มเหลวไว้ในหน่วยความจำ กรุณากดอัดเสียงใหม่อีกครั้งเมื่อพร้อมครับ"
        ),
    },
    "en": {
        "app_title": "Voice2Prompt v{version} — Speech-to-Text Studio for AI Prompting",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ Settings",
        "switch_ontop": "📌 Always on Top",
        "btn_record_idle": "🔴 Click to Speak (Record / Spacebar)",
        "btn_record_listening": "⏹️ Listening... Click to Stop",
        "btn_record_processing": "⏳ Transcribing...",
        "status_ready": "⚪ Ready to record (Click button or press Spacebar)",
        "status_recording": "🔴 Recording audio...",
        "status_auto_limit": "⏳ Auto-stopped (12-minute safety cap for 25 MB limit)...",
        "status_processing_groq": "⏳ Transcribing with Groq Whisper...",
        "status_no_audio": "⚪ No audio data captured",
        "status_no_speech": "⚪ No speech detected",
        "status_error": "❌ Transcription error",
        "status_done_copied": "✅ Transcribed and copied to Clipboard!",
        "status_done": "✅ Transcription complete!",
        "status_copied_history": "✅ Copied item from history!",
        "status_loaded_history": "📝 Loaded item into editor",
        "status_settings_saved": "✅ Settings saved successfully",
        "status_hotkey_conflict": "⚠️ Hotkey ({combo}) is already in use by another app. Please change it in Settings.",
        "editor_title": "📝 Prompt Text for AI (Editable directly):",
        "char_count": "{count} chars",
        "btn_copy": "📋 Copy Text (Copy to Clipboard)",
        "btn_copied_flash": "✅ Copied to Clipboard!",
        "check_autocopy": "📋 Auto-Copy",
        "check_append": "Append to existing text",
        "btn_clear": "🧹 Clear",
        "hist_title": "🕒 Recent 10 Transcripts",
        "btn_clear_hist": "Clear",
        "hist_empty": "No history yet (stored in RAM for this session only)",
        "btn_hist_use": "✏️ Edit",
        "btn_hist_copy": "📋 Copy",
        "confirm_clear_hist_title": "Confirm Clear",
        "confirm_clear_hist_msg": "Are you sure you want to clear all session history?",
        "err_rec_title": "Audio Recording Error",
        "err_stt_title": "Speech Transcription Error",
        "settings_title": "Voice2Prompt Settings (v{version})",
        "settings_ui_lang": "💬 Interface Language (UI Language):",
        "settings_mic": "🎙️ Microphone (Audio Input Device):",
        "settings_default_mic": "Default Microphone",
        "settings_api_key": "🔑 Groq API Key (Get a free key at console.groq.com or set in .env):",
        "settings_spoken_lang": "🌐 Spoken Language:",
        "settings_hotkey_header": "⌨️ Global Hotkey (Trigger from any window):",
        "settings_hotkey_enable": "Enable Global Hotkey",
        "settings_btn_save": "Save Settings",
        # Detailed, user-friendly error messages (>20 words, 3 parts: what happened, what to do, audio retention truth)
        "err_no_api_key": (
            "No Groq API Key is configured yet. Please click the 'Settings' (⚙️) button in the top-right corner to enter your free API key from console.groq.com. "
            "Note that your previous recording was not retained in memory, so please record your voice again after saving your key."
        ),
        "err_invalid_wav": (
            "The recorded WAV audio data in memory was corrupted or invalid and could not be processed. "
            "Please check your microphone connection and try recording again, as the failed audio buffer is not retained in memory."
        ),
        "err_rate_limit_429": (
            "You have reached Groq's free-tier rate limit per minute (the application itself is working normally). "
            "Please wait about {wait} and then record again, because failed audio buffers are not kept in memory after a request. "
            "If you encounter this limit often, try speaking in longer continuous takes or upgrading your Groq API plan."
        ),
        "err_auth_401_403": (
            "Groq rejected the API key because it is invalid, expired, or unauthorized. "
            "Please open 'Settings' (⚙️) to verify and enter a valid Groq API key from console.groq.com. "
            "For your privacy, the audio from this attempt was not retained in memory, so please record again after updating your key."
        ),
        "err_network_conn": (
            "Could not connect to Groq's transcription servers (your internet connection may be offline or blocked by a firewall). "
            "Please check your network connection and try again. "
            "Because Voice2Prompt does not save failed audio recordings to disk or memory, you will need to record again once connected."
        ),
        "err_timeout": (
            "The transcription request to Groq timed out, which usually happens on a slow internet connection or with very long recordings. "
            "Please check your network connection and record again, as the previous audio buffer was not retained in memory."
        ),
        "err_server_5xx": (
            "Groq's transcription server experienced a temporary internal error (HTTP {code}); this is not a bug in your local application. "
            "Please wait a moment and try recording again, as the audio from the failed request was not kept in memory."
        ),
        "err_generic_api": (
            "The transcription request to Groq failed (HTTP status {code}). Please verify your settings or try again shortly. "
            "Note that the audio from this failed attempt was not retained in memory, so please record again when ready."
        ),
    },
}


def t(key: str, lang: str = "th", **kwargs) -> str:
    """Translate `key` into `lang` ('th' or 'en') with keyword formatting."""
    lang_dict = TRANSLATIONS.get(lang) or TRANSLATIONS["en"]
    template = lang_dict.get(key) or TRANSLATIONS["en"].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def get_spoken_language_display_map(ui_lang: str = "th") -> dict[str, str]:
    """Return mapping of display_label -> iso_code for the current UI language."""
    lang_key = "th" if ui_lang == "th" else "en"
    return {labels[lang_key]: code for code, labels in SUPPORTED_SPOKEN_LANGUAGES}


def get_spoken_language_label(iso_code: str, ui_lang: str = "th") -> str:
    """Return display label for a given ISO code in the current UI language."""
    lang_key = "th" if ui_lang == "th" else "en"
    for code, labels in SUPPORTED_SPOKEN_LANGUAGES:
        if code == iso_code:
            return labels[lang_key]
    return SUPPORTED_SPOKEN_LANGUAGES[0][1][lang_key]
