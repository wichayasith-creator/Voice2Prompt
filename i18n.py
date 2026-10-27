# -*- coding: utf-8 -*-
"""
i18n.py — Multilingual (11 UI languages + 11 Spoken languages + Auto) string table and helpers for Voice2Prompt.
Supported UI & Spoken ISO-639-1 codes: th, en, zh, ja, ko, es, fr, de, hi, id, vi
"""
import ctypes
import locale

SUPPORTED_UI_LANGUAGES = {
    "th": "ไทย (Thai)",
    "en": "English",
    "zh": "中文 (Chinese)",
    "ja": "日本語 (Japanese)",
    "ko": "한국어 (Korean)",
    "es": "Español (Spanish)",
    "fr": "Français (French)",
    "de": "Deutsch (German)",
    "hi": "हिन्दी (Hindi)",
    "id": "Bahasa Indonesia (Indonesian)",
    "vi": "Tiếng Việt (Vietnamese)",
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
    (
        "auto",
        {
            "th": "ตรวจจับอัตโนมัติ (Auto-detect)",
            "en": "Auto-detect Language",
            "zh": "自动检测语言 (Auto-detect)",
            "ja": "言語を自動検出 (Auto-detect)",
            "ko": "언어 자동 감지 (Auto-detect)",
            "es": "Detectar idioma automáticamente (Auto)",
            "fr": "Détection automatique (Auto)",
            "de": "Sprache automatisch erkennen (Auto)",
            "hi": "भाषा स्वतः पहचानें (Auto-detect)",
            "id": "Deteksi Bahasa Otomatis (Auto)",
            "vi": "Tự động nhận diện ngôn ngữ (Auto)",
        },
    ),
]

VALID_SPOKEN_CODES = {code for code, _ in SUPPORTED_SPOKEN_LANGUAGES}

# Windows Primary Language ID (LANGID & 0x3FF) to ISO-639-1 code mapping
_WIN_PRIMARY_LANG_MAP = {
    0x1E: "th",  # Thai
    0x09: "en",  # English
    0x04: "zh",  # Chinese
    0x11: "ja",  # Japanese
    0x12: "ko",  # Korean
    0x0A: "es",  # Spanish
    0x0C: "fr",  # French
    0x07: "de",  # German
    0x39: "hi",  # Hindi
    0x21: "id",  # Indonesian
    0x2A: "vi",  # Vietnamese
}


def detect_default_ui_lang() -> str:
    """Detect user's Windows UI / system locale across all 11 supported languages, defaulting to 'en'."""
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        primary = lang_id & 0x3FF
        if primary in _WIN_PRIMARY_LANG_MAP:
            return _WIN_PRIMARY_LANG_MAP[primary]
        if lang_id != 0:
            return "en"
    except Exception:
        pass

    try:
        loc, _ = locale.getlocale()
        if loc:
            loc_lower = loc.lower()
            for code in SUPPORTED_UI_LANGUAGES:
                if loc_lower.startswith(code):
                    return code
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
    "zh": {
        "app_title": "Voice2Prompt v{version} — AI 提示词语音转文字工作室",
        "app_subtitle": "AI 提示词语音转文字工作室 (v{version})",
        "btn_settings": "⚙️ 设置",
        "switch_ontop": "📌 窗口置顶",
        "btn_record_idle": "🔴 点击开始说话 (录音 / 空格键)",
        "btn_record_listening": "⏹️ 正在倾听... 点击停止 (Stop)",
        "btn_record_processing": "⏳ 正在转写语音...",
        "status_ready": "⚪ 准备就绪 (点击按钮或按空格键录音)",
        "status_recording": "🔴 正在录制语音...",
        "status_auto_limit": "⏳ 已自动停止 (达到 12 分钟 / 25 MB 安全上限)...",
        "status_processing_groq": "⏳ 正在通过 Groq Whisper 转写...",
        "status_no_audio": "⚪ 未捕获到音频数据",
        "status_no_speech": "⚪ 未检测到语音内容",
        "status_error": "❌ 转写发生错误",
        "status_done_copied": "✅ 语音转写完成并已复制到剪贴板！",
        "status_done": "✅ 语音转写完成！",
        "status_copied_history": "✅ 已从历史记录复制文本！",
        "status_loaded_history": "📝 已加载到编辑框",
        "status_settings_saved": "✅ 设置已成功保存",
        "status_hotkey_conflict": "⚠️ 全局快捷键 ({combo}) 已被其他程序占用，请在设置中更改。",
        "editor_title": "📝 发送给 AI 的提示词文本 (可直接编辑):",
        "char_count": "{count} 字符",
        "btn_copy": "📋 复制文本 (Copy to Clipboard)",
        "btn_copied_flash": "✅ 已复制到剪贴板！",
        "check_autocopy": "📋 自动复制",
        "check_append": "追加到现有文本末尾",
        "btn_clear": "🧹 清空",
        "hist_title": "🕒 最近 10 条记录",
        "btn_clear_hist": "清空",
        "hist_empty": "暂无历史记录 (仅保存在当前会话内存中)",
        "btn_hist_use": "✏️ 编辑",
        "btn_hist_copy": "📋 复制",
        "confirm_clear_hist_title": "确认清空",
        "confirm_clear_hist_msg": "确定要清空当前会话的所有历史记录吗？",
        "err_rec_title": "音频录制错误",
        "err_stt_title": "语音转写错误",
        "settings_title": "Voice2Prompt 设置 (v{version})",
        "settings_ui_lang": "💬 界面显示语言 (UI Language):",
        "settings_mic": "🎙️ 麦克风设备 (Audio Input Device):",
        "settings_default_mic": "默认麦克风 (Default Microphone)",
        "settings_api_key": "🔑 Groq API 密钥 (可在 console.groq.com 免费获取或配置于 .env):",
        "settings_spoken_lang": "🌐 说话语言 (Spoken Language):",
        "settings_hotkey_header": "⌨️ 全局快捷键 (可在任何窗口触发):",
        "settings_hotkey_enable": "启用全局快捷键",
        "settings_btn_save": "保存设置",
        "err_no_api_key": (
            "尚未配置 Groq API 密钥。请点击右上角的“设置” (⚙️) 按钮输入您在 console.groq.com 免费获取的 API 密钥。"
            "请注意：刚才录制的音频不会保留在内存中，保存密钥后请重新点击录音。"
        ),
        "err_invalid_wav": (
            "内存中的 WAV 音频数据已损坏或格式无效，无法进行分块处理。"
            "请检查您的麦克风连接并重新录制语音，失败的音频缓冲区不会保留在内存中。"
        ),
        "err_rate_limit_429": (
            "您已达到 Groq 免费层每分钟的请求速率限制（本程序本身运行正常）。"
            "请等待约 {wait} 后再重新录音，因为请求失败后的音频数据不会保留在内存中。"
            "如果经常遇到此限制，建议单次连续说完整段话，或升级您的 Groq API 账户套餐。"
        ),
        "err_auth_401_403": (
            "Groq 拒绝了您的 API 密钥，因为该密钥无效、已过期或未授权。"
            "请打开“设置” (⚙️) 检查并重新输入来自 console.groq.com 的有效 Groq API 密钥。"
            "出于隐私保护，刚才录制的音频未保存在内存中，更新密钥后请重新录音。"
        ),
        "err_network_conn": (
            "目前无法连接到 Groq 转写服务器（您的网络可能已断开或被防火墙拦截）。"
            "请检查您的互联网连接后再试一次。"
            "由于 Voice2Prompt 不会将失败的录音保存在磁盘或内存中，恢复网络后请重新录制语音。"
        ),
        "err_timeout": (
            "向 Groq 发送的语音转写请求超时，通常是因为网络连接较慢或录音文件较大。"
            "请检查网络连接并重新录音，之前的音频缓冲区不会保留在内存中。"
        ),
        "err_server_5xx": (
            "Groq 转写服务器出现临时内部错误 (HTTP {code})，这不是您本地程序的问题。"
            "请稍候片刻再重新录音，因为失败请求的音频数据不会保留在内存中。"
        ),
        "err_generic_api": (
            "Groq 语音转写请求失败 (HTTP 状态码 {code})。请检查您的设置或稍后重试。"
            "请注意本次失败尝试的音频未保留在内存中，准备好后请重新开始录音。"
        ),
    },
    "ja": {
        "app_title": "Voice2Prompt v{version} — AIプロンプト用 音声テキスト化スタジオ",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ 設定",
        "switch_ontop": "📌 常に手前に表示",
        "btn_record_idle": "🔴 クリックして話す (録音 / Spaceキー)",
        "btn_record_listening": "⏹️ 聞き取り中... クリックで停止",
        "btn_record_processing": "⏳ 文字起こし中...",
        "status_ready": "⚪ 録音準備完了 (ボタンまたはSpaceキーを押してください)",
        "status_recording": "🔴 音声を録音中...",
        "status_auto_limit": "⏳ 自動停止しました (12分 / 25 MB制限の安全上限)...",
        "status_processing_groq": "⏳ Groq Whisperで文字起こし中...",
        "status_no_audio": "⚪ 音声データがありません",
        "status_no_speech": "⚪ 音声が検出されませんでした",
        "status_error": "❌ 文字起こしエラー",
        "status_done_copied": "✅ 文字起こし完了・クリップボードにコピーしました！",
        "status_done": "✅ 文字起こしが完了しました！",
        "status_copied_history": "✅ 履歴からコピーしました！",
        "status_loaded_history": "📝 エディタに読み込みました",
        "status_settings_saved": "✅ 設定を保存しました",
        "status_hotkey_conflict": "⚠️ ホットキー ({combo}) は他のアプリで使用中です。設定から変更してください。",
        "editor_title": "📝 AI送信用プロンプトテキスト (直接編集可能):",
        "char_count": "{count} 文字",
        "btn_copy": "📋 テキストをコピー (Copy to Clipboard)",
        "btn_copied_flash": "✅ コピーしました！",
        "check_autocopy": "📋 自動コピー",
        "check_append": "既存のテキストに追記",
        "btn_clear": "🧹 クリア",
        "hist_title": "🕒 最新10件の履歴",
        "btn_clear_hist": "消去",
        "hist_empty": "履歴はまだありません (このセッションのRAMにのみ保存されます)",
        "btn_hist_use": "✏️ 編集",
        "btn_hist_copy": "📋 コピー",
        "confirm_clear_hist_title": "履歴消去の確認",
        "confirm_clear_hist_msg": "セッション内のすべての履歴を消去してもよろしいですか？",
        "err_rec_title": "録音エラー",
        "err_stt_title": "文字起こしエラー",
        "settings_title": "Voice2Prompt 設定 (v{version})",
        "settings_ui_lang": "💬 表示言語 (UI Language):",
        "settings_mic": "🎙️ マイク (Audio Input Device):",
        "settings_default_mic": "既定のマイク (Default Microphone)",
        "settings_api_key": "🔑 Groq APIキー (console.groq.comで無料取得、または.envに設定):",
        "settings_spoken_lang": "🌐 話す言語 (Spoken Language):",
        "settings_hotkey_header": "⌨️ グローバルホットキー (どのウィンドウからでも操作可能):",
        "settings_hotkey_enable": "グローバルホットキーを有効化",
        "settings_btn_save": "設定を保存",
        "err_no_api_key": (
            "Groq APIキーがまだ設定されていません。右上の「設定」(⚙️) ボタンをクリックし、console.groq.com で取得した無料APIキーを入力してください。"
            "なお、直前の録音データはメモリに保持されないため、キーの保存後に再度録音してください。"
        ),
        "err_invalid_wav": (
            "メモリ内のWAV音声データが破損しているか無効なため、処理できませんでした。"
            "マイクの接続を確認してからもう一度録音してください（失敗した音声データはメモリに保持されません）。"
        ),
        "err_rate_limit_429": (
            "Groqの無料プランにおける1分あたりの利用上限に達しました（アプリ自体の不具合ではありません）。"
            "失敗した音声データはメモリに残らないため、約 {wait} 待ってからもう一度録音してください。"
            "頻繁に発生する場合は、1回の録音でまとめて長く話すか、Groq APIプランのアップグレードをご検討ください。"
        ),
        "err_auth_401_403": (
            "APIキーが無効、期限切れ、または権限がないため、Groqサーバーに拒否されました。"
            "「設定」(⚙️) を開き、console.groq.com の有効なGroq APIキーを確認して再入力してください。"
            "プライバシー保護のため直前の音声はメモリに保持されていませんので、キー更新後に再度録音してください。"
        ),
        "err_network_conn": (
            "Groqの文字起こしサーバーに接続できませんでした（インターネット未接続またはファイアウォールによる遮断の可能性があります）。"
            "ネットワーク接続を確認してからもう一度お試しください。"
            "Voice2Promptは失敗した録音をディスクやメモリに保存しないため、接続回復後に再度録音してください。"
        ),
        "err_timeout": (
            "Groqサーバーへのリクエストがタイムアウトしました。通信速度が遅いか、録音時間が長い場合に発生することがあります。"
            "ネットワーク接続を確認し、再度録音してください（直前の音声データはメモリに保持されていません）。"
        ),
        "err_server_5xx": (
            "Groqの文字起こしサーバーで一時的な内部エラー (HTTP {code}) が発生しました。ローカルアプリの不具合ではありません。"
            "失敗した音声データはメモリに保持されないため、しばらく待ってから再度録音してください。"
        ),
        "err_generic_api": (
            "Groqへの文字起こしリクエストが失敗しました (HTTP {code})。設定を確認するか、しばらくしてからもう一度お試しください。"
            "なお、今回の失敗した音声データはメモリに保持されていないため、準備ができたら再度録音してください。"
        ),
    },
    "ko": {
        "app_title": "Voice2Prompt v{version} — AI 프롬프트용 음성-텍스트 변환 스튜디오",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ 설정",
        "switch_ontop": "📌 항상 위에 표시",
        "btn_record_idle": "🔴 클릭하여 말하기 (녹음 / 스페이스바)",
        "btn_record_listening": "⏹️ 듣는 중... 클릭하여 중지",
        "btn_record_processing": "⏳ 텍스트 변환 중...",
        "status_ready": "⚪ 녹음 준비 완료 (버튼을 클릭하거나 스페이스바를 누르세요)",
        "status_recording": "🔴 음성 녹음 중...",
        "status_auto_limit": "⏳ 자동 중지됨 (12분 / 25 MB 안전 제한 도달)...",
        "status_processing_groq": "⏳ Groq Whisper로 변환 중...",
        "status_no_audio": "⚪ 캡처된 오디오 데이터 없음",
        "status_no_speech": "⚪ 음성이 감지되지 않았습니다",
        "status_error": "❌ 변환 오류 발생",
        "status_done_copied": "✅ 변환 완료 및 클립보드에 복사되었습니다!",
        "status_done": "✅ 음성 변환 완료!",
        "status_copied_history": "✅ 기록에서 텍스트를 복사했습니다!",
        "status_loaded_history": "📝 편집기로 텍스트를 불러왔습니다",
        "status_settings_saved": "✅ 설정이 저장되었습니다",
        "status_hotkey_conflict": "⚠️ 단축키 ({combo})가 이미 다른 프로그램에서 사용 중입니다. 설정에서 변경해 주세요.",
        "editor_title": "📝 AI에게 보낼 프롬프트 텍스트 (직접 수정 가능):",
        "char_count": "{count}자",
        "btn_copy": "📋 텍스트 복사 (Copy to Clipboard)",
        "btn_copied_flash": "✅ 클립보드에 복사됨!",
        "check_autocopy": "📋 자동 복사",
        "check_append": "기존 텍스트 뒤에 이어쓰기",
        "btn_clear": "🧹 지우기",
        "hist_title": "🕒 최근 10개 변환 기록",
        "btn_clear_hist": "비우기",
        "hist_empty": "아직 기록이 없습니다 (현재 세션의 RAM에만 저장됨)",
        "btn_hist_use": "✏️ 편집",
        "btn_hist_copy": "📋 복사",
        "confirm_clear_hist_title": "기록 삭제 확인",
        "confirm_clear_hist_msg": "현재 세션의 모든 변환 기록을 삭제하시겠습니까?",
        "err_rec_title": "오디오 녹음 오류",
        "err_stt_title": "음성 변환 오류",
        "settings_title": "Voice2Prompt 설정 (v{version})",
        "settings_ui_lang": "💬 인터페이스 언어 (UI Language):",
        "settings_mic": "🎙️ 마이크 장치 (Audio Input Device):",
        "settings_default_mic": "기본 마이크 (Default Microphone)",
        "settings_api_key": "🔑 Groq API 키 (console.groq.com에서 무료 발급 또는 .env에 설정):",
        "settings_spoken_lang": "🌐 발화 언어 (Spoken Language):",
        "settings_hotkey_header": "⌨️ 글로벌 단축키 (모든 창에서 작동):",
        "settings_hotkey_enable": "글로벌 단축키 활성화",
        "settings_btn_save": "설정 저장",
        "err_no_api_key": (
            "아직 Groq API 키가 설정되지 않았습니다. 오른쪽 상단의 '설정' (⚙️) 버튼을 눌러 console.groq.com에서 발급받은 무료 API 키를 입력해 주세요. "
            "참고로 방금 녹음한 음성은 메모리에 유지되지 않으므로 키를 저장한 후 다시 녹음해 주세요."
        ),
        "err_invalid_wav": (
            "메모리의 WAV 오디오 데이터가 손상되었거나 유효하지 않아 처리할 수 없습니다. "
            "마이크 연결 상태를 확인한 후 다시 녹음해 주세요. 실패한 오디오 버퍼는 메모리에 보관되지 않습니다."
        ),
        "err_rate_limit_429": (
            "Groq 무료 등급의 분당 요청 한도에 도달했습니다 (프로그램 자체 오류는 아닙니다). "
            "실패한 오디오 버퍼는 메모리에 유지되지 않으므로 약 {wait} 후에 다시 녹음해 주세요. "
            "이 제한이 자주 발생하면 한 번 녹음할 때 더 길게 이어서 말하거나 Groq API 플랜을 업그레이드하는 것이 좋습니다."
        ),
        "err_auth_401_403": (
            "API 키가 잘못되었거나 만료되어 Groq 서버에서 인증을 거부했습니다. "
            "'설정' (⚙️) 창을 열어 console.groq.com의 유효한 Groq API 키를 확인하고 다시 입력해 주세요. "
            "개인정보 보호를 위해 방금 녹음한 음성은 메모리에 남지 않으므로 키를 수정한 뒤 다시 녹음해 주세요."
        ),
        "err_network_conn": (
            "Groq 변환 서버에 연결할 수 없습니다 (인터넷 연결이 끊겼거나 방화벽에 의해 차단되었을 수 있습니다). "
            "네트워크 연결을 확인한 후 다시 시도해 주세요. "
            "Voice2Prompt는 실패한 녹음을 디스크나 메모리에 저장하지 않으므로 인터넷이 연결되면 다시 녹음해 주세요."
        ),
        "err_timeout": (
            "Groq 서버로 보낸 변환 요청 시간이 초과되었습니다. 주로 인터넷 속도가 느리거나 녹음 파일이 클 때 발생합니다. "
            "네트워크 상태를 확인하고 다시 녹음해 주세요. 이전 오디오 버퍼는 메모리에 유지되지 않습니다."
        ),
        "err_server_5xx": (
            "Groq 변환 서버에 일시적인 내부 오류 (HTTP {code})가 발생했으며 로컬 프로그램의 문제가 아닙니다. "
            "실패한 요청의 오디오는 메모리에 보관되지 않으므로 잠시 기다린 후 다시 녹음해 주세요."
        ),
        "err_generic_api": (
            "Groq 음성 변환 요청이 실패했습니다 (HTTP 상태 코드 {code}). 설정을 확인하거나 잠시 후 다시 시도해 주세요. "
            "실패한 시도의 오디오 데이터는 메모리에 유지되지 않으므로 준비되면 다시 녹음해 주세요."
        ),
    },
    "es": {
        "app_title": "Voice2Prompt v{version} — Estudio de Voz a Texto para Prompts de IA",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ Ajustes",
        "switch_ontop": "📌 Siempre visible",
        "btn_record_idle": "🔴 Haz clic para hablar (Grabar / Espacio)",
        "btn_record_listening": "⏹️ Escuchando... Haz clic para detener",
        "btn_record_processing": "⏳ Transcribiendo...",
        "status_ready": "⚪ Listo para grabar (Haz clic o pulsa Espacio)",
        "status_recording": "🔴 Grabando audio...",
        "status_auto_limit": "⏳ Detenido automáticamente (límite seguro de 12 min / 25 MB)...",
        "status_processing_groq": "⏳ Transcribiendo con Groq Whisper...",
        "status_no_audio": "⚪ No se capturó audio",
        "status_no_speech": "⚪ No se detectó voz",
        "status_error": "❌ Error de transcripción",
        "status_done_copied": "✅ ¡Transcrito y copiado al portapapeles!",
        "status_done": "✅ ¡Transcripción completada!",
        "status_copied_history": "✅ ¡Copiado del historial!",
        "status_loaded_history": "📝 Cargado en el editor",
        "status_settings_saved": "✅ Ajustes guardados correctamente",
        "status_hotkey_conflict": "⚠️ El atajo ({combo}) ya está en uso por otra aplicación. Cámbialo en Ajustes.",
        "editor_title": "📝 Texto del Prompt para IA (Editable directamente):",
        "char_count": "{count} caracteres",
        "btn_copy": "📋 Copiar texto (Copy to Clipboard)",
        "btn_copied_flash": "✅ ¡Copiado al portapapeles!",
        "check_autocopy": "📋 Auto-copiar",
        "check_append": "Añadir al texto existente",
        "btn_clear": "🧹 Limpiar",
        "hist_title": "🕒 Últimas 10 transcripciones",
        "btn_clear_hist": "Borrar",
        "hist_empty": "Sin historial aún (se guarda solo en RAM durante esta sesión)",
        "btn_hist_use": "✏️ Editar",
        "btn_hist_copy": "📋 Copiar",
        "confirm_clear_hist_title": "Confirmar borrado",
        "confirm_clear_hist_msg": "¿Seguro que deseas borrar todo el historial de esta sesión?",
        "err_rec_title": "Error de grabación de audio",
        "err_stt_title": "Error de transcripción de voz",
        "settings_title": "Ajustes de Voice2Prompt (v{version})",
        "settings_ui_lang": "💬 Idioma de la interfaz (UI Language):",
        "settings_mic": "🎙️ Micrófono (Dispositivo de entrada):",
        "settings_default_mic": "Micrófono predeterminado",
        "settings_api_key": "🔑 Clave API de Groq (Gratis en console.groq.com o en .env):",
        "settings_spoken_lang": "🌐 Idioma hablado (Spoken Language):",
        "settings_hotkey_header": "⌨️ Atajo global (Funciona desde cualquier ventana):",
        "settings_hotkey_enable": "Activar atajo global",
        "settings_btn_save": "Guardar ajustes",
        "err_no_api_key": (
            "Aún no se ha configurado ninguna clave API de Groq. Haz clic en el botón 'Ajustes' (⚙️) arriba a la derecha para introducir tu clave gratuita de console.groq.com. "
            "Ten en cuenta que la grabación anterior no se guardó en la memoria, así que vuelve a grabar tu voz después de guardar la clave."
        ),
        "err_invalid_wav": (
            "Los datos de audio WAV grabados en la memoria estaban dañados o no eran válidos y no se pudieron procesar. "
            "Comprueba la conexión de tu micrófono e intenta grabar de nuevo, ya que el búfer de audio fallido no se conserva en la memoria."
        ),
        "err_rate_limit_429": (
            "Has alcanzado el límite de solicitudes por minuto del plan gratuito de Groq (la aplicación funciona con normalidad). "
            "Espera unos {wait} y vuelve a grabar, porque los búferes de audio fallidos no se conservan en la memoria tras una solicitud. "
            "Si encuentras este límite a menudo, intenta hablar en tomas continuas más largas o actualiza tu plan de Groq API."
        ),
        "err_auth_401_403": (
            "Groq rechazó la clave API porque no es válida, ha caducado o no tiene autorización. "
            "Abre 'Ajustes' (⚙️) para verificar e introducir una clave API de Groq válida desde console.groq.com. "
            "Por tu privacidad, el audio de este intento no se conservó en la memoria, así que vuelve a grabar tras actualizar tu clave."
        ),
        "err_network_conn": (
            "No se pudo conectar con los servidores de transcripción de Groq (tu conexión a Internet puede estar caída o bloqueada por un firewall). "
            "Comprueba tu conexión de red e inténtalo de nuevo. "
            "Como Voice2Prompt no guarda las grabaciones fallidas en el disco ni en la memoria, tendrás que volver a grabar cuando tengas conexión."
        ),
        "err_timeout": (
            "La solicitud de transcripción a Groq agotó el tiempo de espera, lo cual suele ocurrir con conexiones lentas o grabaciones muy largas. "
            "Comprueba tu conexión a Internet y vuelve a grabar, ya que el búfer de audio anterior no se conservó en la memoria."
        ),
        "err_server_5xx": (
            "El servidor de transcripción de Groq experimentó un error interno temporal (HTTP {code}); esto no es un fallo de tu aplicación local. "
            "Espera un momento e intenta grabar de nuevo, ya que el audio de la solicitud fallida no se guardó en la memoria."
        ),
        "err_generic_api": (
            "La solicitud de transcripción a Groq falló (estado HTTP {code}). Verifica tus ajustes o inténtalo de nuevo en unos instantes. "
            "Ten en cuenta que el audio de este intento fallido no se conservó en la memoria, así que vuelve a grabar cuando estés listo."
        ),
    },
    "fr": {
        "app_title": "Voice2Prompt v{version} — Studio Voix-vers-Texte pour Prompts IA",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ Paramètres",
        "switch_ontop": "📌 Toujours au premier plan",
        "btn_record_idle": "🔴 Cliquez pour parler (Enregistrer / Espace)",
        "btn_record_listening": "⏹️ Écoute en cours... Cliquez pour arrêter",
        "btn_record_processing": "⏳ Transcription...",
        "status_ready": "⚪ Prêt à enregistrer (Cliquez ou appuyez sur Espace)",
        "status_recording": "🔴 Enregistrement audio...",
        "status_auto_limit": "⏳ Arrêt automatique (limite de sécurité de 12 min / 25 Mo)...",
        "status_processing_groq": "⏳ Transcription via Groq Whisper...",
        "status_no_audio": "⚪ Aucun audio capturé",
        "status_no_speech": "⚪ Aucune parole détectée",
        "status_error": "❌ Erreur de transcription",
        "status_done_copied": "✅ Transcrit et copié dans le presse-papiers !",
        "status_done": "✅ Transcription terminée !",
        "status_copied_history": "✅ Copié depuis l'historique !",
        "status_loaded_history": "📝 Chargé dans l'éditeur",
        "status_settings_saved": "✅ Paramètres enregistrés avec succès",
        "status_hotkey_conflict": "⚠️ Le raccourci ({combo}) est déjà utilisé par une autre application. Modifiez-le dans les Paramètres.",
        "editor_title": "📝 Texte du Prompt pour l'IA (Modifiable directement) :",
        "char_count": "{count} caractères",
        "btn_copy": "📋 Copier le texte (Copy to Clipboard)",
        "btn_copied_flash": "✅ Copié dans le presse-papiers !",
        "check_autocopy": "📋 Copie auto",
        "check_append": "Ajouter à la suite du texte",
        "btn_clear": "🧹 Effacer",
        "hist_title": "🕒 10 dernières transcriptions",
        "btn_clear_hist": "Vider",
        "hist_empty": "Aucun historique (stocké uniquement en RAM pour cette session)",
        "btn_hist_use": "✏️ Éditer",
        "btn_hist_copy": "📋 Copier",
        "confirm_clear_hist_title": "Confirmer la suppression",
        "confirm_clear_hist_msg": "Voulez-vous vraiment effacer tout l'historique de cette session ?",
        "err_rec_title": "Erreur d'enregistrement audio",
        "err_stt_title": "Erreur de transcription vocale",
        "settings_title": "Paramètres Voice2Prompt (v{version})",
        "settings_ui_lang": "💬 Langue de l'interface (UI Language) :",
        "settings_mic": "🎙️ Microphone (Périphérique d'entrée) :",
        "settings_default_mic": "Microphone par défaut",
        "settings_api_key": "🔑 Clé API Groq (Gratuite sur console.groq.com ou via .env) :",
        "settings_spoken_lang": "🌐 Langue parlée (Spoken Language) :",
        "settings_hotkey_header": "⌨️ Raccourci global (Depuis n'importe quelle fenêtre) :",
        "settings_hotkey_enable": "Activer le raccourci global",
        "settings_btn_save": "Enregistrer les paramètres",
        "err_no_api_key": (
            "Aucune clé API Groq n'est encore configurée. Veuillez cliquer sur le bouton 'Paramètres' (⚙️) en haut à droite pour saisir votre clé gratuite obtenue sur console.groq.com. "
            "Notez que votre enregistrement précédent n'a pas été conservé en mémoire ; veuillez réenregistrer votre voix après avoir sauvegardé la clé."
        ),
        "err_invalid_wav": (
            "Les données audio WAV enregistrées en mémoire étaient corrompues ou invalides et n'ont pas pu être traitées. "
            "Veuillez vérifier le branchement de votre microphone et réessayer d'enregistrer, car le tampon audio en échec n'est pas conservé en mémoire."
        ),
        "err_rate_limit_429": (
            "Vous avez atteint la limite de requêtes par minute de l'offre gratuite de Groq (l'application elle-même fonctionne normalement). "
            "Veuillez patienter environ {wait} avant d'enregistrer à nouveau, car les tampons audio en échec ne sont pas gardés en mémoire. "
            "Si vous rencontrez souvent cette limite, essayez de parler en prises continues plus longues ou passez à une offre Groq supérieure."
        ),
        "err_auth_401_403": (
            "Groq a rejeté la clé API car elle est invalide, expirée ou non autorisée. "
            "Veuillez ouvrir les 'Paramètres' (⚙️) pour vérifier et saisir une clé API Groq valide depuis console.groq.com. "
            "Pour votre confidentialité, l'audio de cette tentative n'a pas été conservé en mémoire ; veuillez réenregistrer après avoir mis à jour votre clé."
        ),
        "err_network_conn": (
            "Impossible de se connecter aux serveurs de transcription de Groq (votre connexion Internet est peut-être hors ligne ou bloquée par un pare-feu). "
            "Veuillez vérifier votre connexion réseau et réessayer. "
            "Comme Voice2Prompt n'enregistre pas les audios en échec sur le disque ou en mémoire, vous devrez réenregistrer une fois connecté."
        ),
        "err_timeout": (
            "La requête de transcription vers Groq a expiré, ce qui arrive généralement avec une connexion Internet lente ou de très longs enregistrements. "
            "Veuillez vérifier votre connexion réseau et enregistrer à nouveau, car le tampon audio précédent n'a pas été conservé en mémoire."
        ),
        "err_server_5xx": (
            "Le serveur de transcription de Groq a rencontré une erreur interne temporaire (HTTP {code}) ; ce n'est pas un bug de votre application locale. "
            "Veuillez patienter un instant et réessayer d'enregistrer, car l'audio de la requête échouée n'a pas été conservé en mémoire."
        ),
        "err_generic_api": (
            "La requête de transcription vers Groq a échoué (statut HTTP {code}). Veuillez vérifier vos paramètres ou réessayer dans un instant. "
            "Notez que l'audio de cette tentative échouée n'a pas été conservé en mémoire ; veuillez réenregistrer lorsque vous êtes prêt."
        ),
    },
    "de": {
        "app_title": "Voice2Prompt v{version} — Sprache-zu-Text-Studio für KI-Prompts",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ Einstellungen",
        "switch_ontop": "📌 Immer im Vordergrund",
        "btn_record_idle": "🔴 Klicken zum Sprechen (Aufnahme / Leertaste)",
        "btn_record_listening": "⏹️ Höre zu... Klicken zum Stoppen",
        "btn_record_processing": "⏳ Transkribiere...",
        "status_ready": "⚪ Bereit zur Aufnahme (Button klicken oder Leertaste drücken)",
        "status_recording": "🔴 Audio wird aufgenommen...",
        "status_auto_limit": "⏳ Automatisch gestoppt (12-Minuten-Sicherheitslimit für 25 MB)...",
        "status_processing_groq": "⏳ Transkribiere mit Groq Whisper...",
        "status_no_audio": "⚪ Keine Audiodaten erfasst",
        "status_no_speech": "⚪ Keine Sprache erkannt",
        "status_error": "❌ Transkriptionsfehler",
        "status_done_copied": "✅ Transkribiert und in die Zwischenablage kopiert!",
        "status_done": "✅ Transkription abgeschlossen!",
        "status_copied_history": "✅ Aus dem Verlauf kopiert!",
        "status_loaded_history": "📝 In den Editor geladen",
        "status_settings_saved": "✅ Einstellungen erfolgreich gespeichert",
        "status_hotkey_conflict": "⚠️ Tastenkombination ({combo}) wird bereits von einem anderen Programm verwendet. Bitte in den Einstellungen ändern.",
        "editor_title": "📝 Prompt-Text für KI (Direkt bearbeitbar):",
        "char_count": "{count} Zeichen",
        "btn_copy": "📋 Text kopieren (Copy to Clipboard)",
        "btn_copied_flash": "✅ In Zwischenablage kopiert!",
        "check_autocopy": "📋 Auto-Kopieren",
        "check_append": "An bestehenden Text anhängen",
        "btn_clear": "🧹 Leeren",
        "hist_title": "🕒 Letzte 10 Transkripte",
        "btn_clear_hist": "Löschen",
        "hist_empty": "Noch kein Verlauf (wird nur im RAM für diese Sitzung gespeichert)",
        "btn_hist_use": "✏️ Bearbeiten",
        "btn_hist_copy": "📋 Kopieren",
        "confirm_clear_hist_title": "Löschen bestätigen",
        "confirm_clear_hist_msg": "Möchten Sie wirklich den gesamten Sitzungsverlauf löschen?",
        "err_rec_title": "Audio-Aufnahmefehler",
        "err_stt_title": "Sprachtranskriptionsfehler",
        "settings_title": "Voice2Prompt Einstellungen (v{version})",
        "settings_ui_lang": "💬 Oberflächensprache (UI Language):",
        "settings_mic": "🎙️ Mikrofon (Audio-Eingabegerät):",
        "settings_default_mic": "Standardmikrofon",
        "settings_api_key": "🔑 Groq API-Schlüssel (Kostenlos unter console.groq.com oder in .env):",
        "settings_spoken_lang": "🌐 Gesprochene Sprache (Spoken Language):",
        "settings_hotkey_header": "⌨️ Globaler Hotkey (Aus jedem Fenster auslösbar):",
        "settings_hotkey_enable": "Globalen Hotkey aktivieren",
        "settings_btn_save": "Einstellungen speichern",
        "err_no_api_key": (
            "Es ist noch kein Groq API-Schlüssel konfiguriert. Bitte klicken Sie oben rechts auf 'Einstellungen' (⚙️), um Ihren kostenlosen API-Schlüssel von console.groq.com einzugeben. "
            "Hinweis: Ihre vorherige Aufnahme wurde nicht im Arbeitsspeicher behalten. Bitte nehmen Sie Ihre Stimme nach dem Speichern des Schlüssels erneut auf."
        ),
        "err_invalid_wav": (
            "Die im Arbeitsspeicher aufgezeichneten WAV-Audiodaten waren beschädigt oder ungültig und konnten nicht verarbeitet werden. "
            "Bitte überprüfen Sie Ihre Mikrofonverbindung und starten Sie die Aufnahme erneut, da fehlgeschlagene Audiopuffer nicht im Speicher verbleiben."
        ),
        "err_rate_limit_429": (
            "Sie haben das Minutenlimit des kostenlosen Groq-Tarifs erreicht (die Anwendung selbst funktioniert einwandfrei). "
            "Bitte warten Sie etwa {wait} und starten Sie dann eine neue Aufnahme, da fehlgeschlagene Audiopuffer nicht im Arbeitsspeicher gespeichert werden. "
            "Wenn dieses Limit häufig auftritt, sprechen Sie längere zusammenhängende Abschnitte oder führen Sie ein Upgrade Ihres Groq-Tarifs durch."
        ),
        "err_auth_401_403": (
            "Groq hat den API-Schlüssel abgelehnt, da er ungültig, abgelaufen oder nicht autorisiert ist. "
            "Bitte öffnen Sie die 'Einstellungen' (⚙️), um einen gültigen Groq API-Schlüssel von console.groq.com einzugeben. "
            "Zu Ihrem Datenschutz wurde das Audio dieses Versuchs nicht im Speicher behalten; bitte nehmen Sie nach dem Aktualisieren des Schlüssels erneut auf."
        ),
        "err_network_conn": (
            "Verbindung zu den Groq-Transkriptionsservern fehlgeschlagen (Ihre Internetverbindung ist möglicherweise getrennt oder durch eine Firewall blockiert). "
            "Bitte überprüfen Sie Ihre Netzwerkverbindung und versuchen Sie es erneut. "
            "Da Voice2Prompt fehlgeschlagene Aufnahmen weder auf der Festplatte noch im RAM speichert, müssen Sie nach Wiederherstellung der Verbindung neu aufnehmen."
        ),
        "err_timeout": (
            "Die Transkriptionsanfrage an Groq hat das Zeitlimit überschritten, was meist bei langsamer Internetverbindung oder sehr langen Aufnahmen passiert. "
            "Bitte prüfen Sie Ihre Netzwerkverbindung und nehmen Sie erneut auf, da der vorherige Audiopuffer nicht im Speicher behalten wurde."
        ),
        "err_server_5xx": (
            "Auf dem Groq-Transkriptionsserver ist ein vorübergehender interner Fehler aufgetreten (HTTP {code}); dies ist kein Fehler Ihrer lokalen Anwendung. "
            "Bitte warten Sie einen Moment und starten Sie eine neue Aufnahme, da das Audio der fehlgeschlagenen Anfrage nicht im Speicher behalten wurde."
        ),
        "err_generic_api": (
            "Die Transkriptionsanfrage an Groq ist fehlgeschlagen (HTTP-Status {code}). Bitte überprüfen Sie Ihre Einstellungen oder versuchen Sie es gleich noch einmal. "
            "Beachten Sie, dass das Audio dieses fehlgeschlagenen Versuchs nicht im Speicher behalten wurde. Bitte nehmen Sie erneut auf, sobald Sie bereit sind."
        ),
    },
    "hi": {
        "app_title": "Voice2Prompt v{version} — AI प्रॉम्प्टिंग के लिए स्पीच-टू-टेक्स्ट स्टूडियो",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ सेटिंग्स",
        "switch_ontop": "📌 हमेशा ऊपर रखें",
        "btn_record_idle": "🔴 बोलने के लिए क्लिक करें (Record / Spacebar)",
        "btn_record_listening": "⏹️ सुन रहा है... रोकने के लिए क्लिक करें",
        "btn_record_processing": "⏳ ट्रांसक्राइब हो रहा है...",
        "status_ready": "⚪ रिकॉर्डिंग के लिए तैयार (बटन दबाएं या Spacebar दबाएं)",
        "status_recording": "🔴 ऑडियो रिकॉर्ड हो रहा है...",
        "status_auto_limit": "⏳ स्वतः रुक गया (12 मिनट / 25 MB सुरक्षा सीमा)...",
        "status_processing_groq": "⏳ Groq Whisper से ट्रांसक्राइब हो रहा है...",
        "status_no_audio": "⚪ कोई ऑडियो डेटा नहीं मिला",
        "status_no_speech": "⚪ कोई आवाज़ नहीं पहचानी गई",
        "status_error": "❌ ट्रांसक्रिप्शन त्रुटि",
        "status_done_copied": "✅ ट्रांसक्राइब हो गया और क्लिपबोर्ड पर कॉपी हो गया!",
        "status_done": "✅ ट्रांसक्रिप्शन पूरा हुआ!",
        "status_copied_history": "✅ हिस्ट्री से टेक्स्ट कॉपी किया गया!",
        "status_loaded_history": "📝 एडिटर में लोड किया गया",
        "status_settings_saved": "✅ सेटिंग्स सफलतापूर्वक सहेजी गईं",
        "status_hotkey_conflict": "⚠️ हॉटकी ({combo}) पहले से किसी अन्य ऐप द्वारा उपयोग में है। कृपया इसे सेटिंग्स में बदलें।",
        "editor_title": "📝 AI के लिए प्रॉम्प्ट टेक्स्ट (सीधे संपादित करें):",
        "char_count": "{count} अक्षर",
        "btn_copy": "📋 टेक्स्ट कॉपी करें (Copy to Clipboard)",
        "btn_copied_flash": "✅ क्लिपबोर्ड पर कॉपी हो गया!",
        "check_autocopy": "📋 ऑटो-कॉपी",
        "check_append": "मौजूदा टेक्स्ट के आगे जोड़ें",
        "btn_clear": "🧹 साफ़ करें",
        "hist_title": "🕒 हाल के 10 ट्रांसक्रिप्ट",
        "btn_clear_hist": "हटाएं",
        "hist_empty": "अभी कोई हिस्ट्री नहीं है (केवल इस सेशन के लिए RAM में सुरक्षित)",
        "btn_hist_use": "✏️ संपादित करें",
        "btn_hist_copy": "📋 कॉपी",
        "confirm_clear_hist_title": "साफ़ करने की पुष्टि करें",
        "confirm_clear_hist_msg": "क्या आप वाकई इस सेशन की सारी हिस्ट्री मिटाना चाहते हैं?",
        "err_rec_title": "ऑडियो रिकॉर्डिंग त्रुटि",
        "err_stt_title": "स्पीच ट्रांसक्रिप्शन त्रुटि",
        "settings_title": "Voice2Prompt सेटिंग्स (v{version})",
        "settings_ui_lang": "💬 इंटरफ़ेस भाषा (UI Language):",
        "settings_mic": "🎙️ माइक्रोफ़ोन (Audio Input Device):",
        "settings_default_mic": "डिफ़ॉल्ट माइक्रोफ़ोन (Default Microphone)",
        "settings_api_key": "🔑 Groq API Key (console.groq.com से मुफ़्त पाएं या .env में सेट करें):",
        "settings_spoken_lang": "🌐 बोलने की भाषा (Spoken Language):",
        "settings_hotkey_header": "⌨️ ग्लोबल हॉटकी (किसी भी विंडो से चालू करें):",
        "settings_hotkey_enable": "ग्लोबल हॉटकी चालू करें",
        "settings_btn_save": "सेटिंग्स सहेजें",
        "err_no_api_key": (
            "अभी तक कोई Groq API Key सेट नहीं की गई है। कृपया console.groq.com से अपनी मुफ़्त API Key डालने के लिए ऊपर दाईं ओर 'सेटिंग्स' (⚙️) बटन पर क्लिक करें। "
            "ध्यान दें कि आपकी पिछली रिकॉर्डिंग मेमोरी में सहेजी नहीं गई थी, इसलिए की (Key) सहेजने के बाद कृपया अपनी आवाज़ दोबारा रिकॉर्ड करें।"
        ),
        "err_invalid_wav": (
            "मेमोरी में रिकॉर्ड किया गया WAV ऑडियो डेटा खराब या अमान्य था और उसे प्रोसेस नहीं किया जा सका। "
            "कृपया अपने माइक्रोफ़ोन का कनेक्शन जांचें और दोबारा रिकॉर्ड करने का प्रयास करें, क्योंकि विफल ऑडियो बफ़र मेमोरी में नहीं रखा जाता है।"
        ),
        "err_rate_limit_429": (
            "आप प्रति मिनट Groq के मुफ़्त-टियर रेट लिमिट तक पहुँच गए हैं (यह ऐप की खराबी नहीं है)। "
            "कृपया लगभग {wait} प्रतीक्षा करें और फिर दोबारा रिकॉर्ड करें, क्योंकि अनुरोध विफल होने के बाद ऑडियो बफ़र मेमोरी में नहीं रखे जाते हैं। "
            "यदि आपको यह समस्या बार-बार आती है, तो एक बार में लंबा लगातार बोलने का प्रयास करें या अपना Groq API प्लान अपग्रेड करें।"
        ),
        "err_auth_401_403": (
            "Groq ने API Key को अस्वीकार कर दिया क्योंकि यह अमान्य, समाप्त या अनधिकृत है। "
            "कृपया console.groq.com से एक मान्य Groq API Key जांचने और डालने के लिए 'सेटिंग्स' (⚙️) खोलें। "
            "आपकी गोपनीयता के लिए, इस प्रयास का ऑडियो मेमोरी में नहीं रखा गया था, इसलिए अपनी Key अपडेट करने के बाद कृपया दोबारा रिकॉर्ड करें।"
        ),
        "err_network_conn": (
            "Groq के ट्रांसक्रिप्शन सर्वर से कनेक्ट नहीं हो सका (आपका इंटरनेट कनेक्शन ऑफ़लाइन हो सकता है या फ़ायरवॉल द्वारा रोका गया है)। "
            "कृपया अपना नेटवर्क कनेक्शन जांचें और पुनः प्रयास करें। "
            "चूंकि Voice2Prompt विफल ऑडियो रिकॉर्डिंग को डिस्क या मेमोरी में सेव नहीं करता है, इसलिए इंटरनेट जुड़ने पर आपको दोबारा रिकॉर्ड करना होगा।"
        ),
        "err_timeout": (
            "Groq को भेजा गया ट्रांसक्रिप्शन अनुरोध टाइम-आउट हो गया, जो आमतौर पर धीमे इंटरनेट कनेक्शन या बहुत लंबी रिकॉर्डिंग के कारण होता है। "
            "कृपया अपना नेटवर्क कनेक्शन जांचें और दोबारा रिकॉर्ड करें, क्योंकि पिछला ऑडियो बफ़र मेमोरी में नहीं रखा गया था।"
        ),
        "err_server_5xx": (
            "Groq के ट्रांसक्रिप्शन सर्वर में एक अस्थायी आंतरिक त्रुटि (HTTP {code}) हुई है; यह आपके लोकल ऐप का बग नहीं है। "
            "कृपया कुछ क्षण प्रतीक्षा करें और दोबारा रिकॉर्ड करने का प्रयास करें, क्योंकि विफल अनुरोध का ऑडियो मेमोरी में नहीं रखा गया था।"
        ),
        "err_generic_api": (
            "Groq को भेजा गया ट्रांसक्रिप्शन अनुरोध विफल रहा (HTTP स्थिति {code})। कृपया अपनी सेटिंग्स जांचें या थोड़ी देर बाद पुनः प्रयास करें। "
            "ध्यान दें कि इस विफल प्रयास का ऑडियो मेमोरी में नहीं रखा गया था, इसलिए तैयार होने पर कृपया दोबारा रिकॉर्ड करें।"
        ),
    },
    "id": {
        "app_title": "Voice2Prompt v{version} — Studio Suara-ke-Teks untuk Prompt AI",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ Pengaturan",
        "switch_ontop": "📌 Selalu di Atas",
        "btn_record_idle": "🔴 Klik untuk Bicara (Rekam / Spasi)",
        "btn_record_listening": "⏹️ Mendengarkan... Klik untuk Berhenti",
        "btn_record_processing": "⏳ Mentranskripsi...",
        "status_ready": "⚪ Siap merekam (Klik tombol atau tekan Spasi)",
        "status_recording": "🔴 Merekam audio...",
        "status_auto_limit": "⏳ Berhenti otomatis (batas aman 12 menit / 25 MB)...",
        "status_processing_groq": "⏳ Mentranskripsi dengan Groq Whisper...",
        "status_no_audio": "⚪ Tidak ada data audio yang tertangkap",
        "status_no_speech": "⚪ Tidak ada suara ucapan yang terdeteksi",
        "status_error": "❌ Kesalahan transkripsi",
        "status_done_copied": "✅ Berhasil ditranskripsi dan disalin ke Clipboard!",
        "status_done": "✅ Transkripsi selesai!",
        "status_copied_history": "✅ Teks disalin dari riwayat!",
        "status_loaded_history": "📝 Dimuat ke dalam editor",
        "status_settings_saved": "✅ Pengaturan berhasil disimpan",
        "status_hotkey_conflict": "⚠️ Pintasan ({combo}) sedang digunakan oleh aplikasi lain. Silakan ubah di Pengaturan.",
        "editor_title": "📝 Teks Prompt untuk AI (Dapat diedit langsung):",
        "char_count": "{count} karakter",
        "btn_copy": "📋 Salin Teks (Copy to Clipboard)",
        "btn_copied_flash": "✅ Disalin ke Clipboard!",
        "check_autocopy": "📋 Salin Otomatis",
        "check_append": "Tambahkan ke teks yang ada",
        "btn_clear": "🧹 Bersihkan",
        "hist_title": "🕒 10 Transkrip Terakhir",
        "btn_clear_hist": "Hapus",
        "hist_empty": "Belum ada riwayat (disimpan di RAM hanya untuk sesi ini)",
        "btn_hist_use": "✏️ Edit",
        "btn_hist_copy": "📋 Salin",
        "confirm_clear_hist_title": "Konfirmasi Hapus",
        "confirm_clear_hist_msg": "Apakah Anda yakin ingin menghapus semua riwayat sesi ini?",
        "err_rec_title": "Kesalahan Perekaman Audio",
        "err_stt_title": "Kesalahan Transkripsi Suara",
        "settings_title": "Pengaturan Voice2Prompt (v{version})",
        "settings_ui_lang": "💬 Bahasa Antarmuka (UI Language):",
        "settings_mic": "🎙️ Mikrofon (Perangkat Input Audio):",
        "settings_default_mic": "Mikrofon Default",
        "settings_api_key": "🔑 Groq API Key (Dapatkan gratis di console.groq.com atau atur di .env):",
        "settings_spoken_lang": "🌐 Bahasa Ucapan (Spoken Language):",
        "settings_hotkey_header": "⌨️ Pintasan Global (Aktifkan dari jendela mana saja):",
        "settings_hotkey_enable": "Aktifkan Pintasan Global",
        "settings_btn_save": "Simpan Pengaturan",
        "err_no_api_key": (
            "Groq API Key belum dikonfigurasi. Silakan klik tombol 'Pengaturan' (⚙️) di pojok kanan atas untuk memasukkan API key gratis Anda dari console.groq.com. "
            "Perlu diketahui bahwa rekaman Anda sebelumnya tidak disimpan di memori, jadi silakan rekam ulang suara Anda setelah menyimpan key."
        ),
        "err_invalid_wav": (
            "Data audio WAV yang direkam di memori rusak atau tidak valid sehingga tidak dapat diproses. "
            "Silakan periksa koneksi mikrofon Anda dan coba rekam lagi, karena buffer audio yang gagal tidak disimpan di memori."
        ),
        "err_rate_limit_429": (
            "Anda telah mencapai batas permintaan per menit untuk paket gratis Groq (aplikasi ini sendiri berjalan normal). "
            "Silakan tunggu sekitar {wait} lalu rekam kembali, karena buffer audio yang gagal tidak disimpan di memori setelah permintaan selesai. "
            "Jika Anda sering mengalami batas ini, cobalah berbicara lebih panjang dalam satu kali rekam atau tingkatkan paket Groq API Anda."
        ),
        "err_auth_401_403": (
            "Groq menolak API key karena tidak valid, kedaluwarsa, atau tidak memiliki izin. "
            "Silakan buka 'Pengaturan' (⚙️) untuk memeriksa dan memasukkan Groq API key yang valid dari console.groq.com. "
            "Demi privasi Anda, audio dari percobaan ini tidak disimpan di memori, jadi silakan rekam ulang setelah memperbarui key Anda."
        ),
        "err_network_conn": (
            "Tidak dapat terhubung ke server transkripsi Groq (koneksi internet Anda mungkin terputus atau diblokir oleh firewall). "
            "Silakan periksa koneksi jaringan Anda dan coba lagi. "
            "Karena Voice2Prompt tidak menyimpan rekaman audio yang gagal ke disk atau memori, Anda perlu merekam ulang setelah terhubung kembali."
        ),
        "err_timeout": (
            "Permintaan transkripsi ke Groq melewati batas waktu (timeout), yang biasanya terjadi pada koneksi internet lambat atau rekaman yang sangat panjang. "
            "Silakan periksa koneksi jaringan Anda dan rekam ulang, karena buffer audio sebelumnya tidak disimpan di memori."
        ),
        "err_server_5xx": (
            "Server transkripsi Groq mengalami kesalahan internal sementara (HTTP {code}); ini bukan kerusakan pada aplikasi lokal Anda. "
            "Silakan tunggu sebentar dan coba rekam lagi, karena audio dari permintaan yang gagal tidak disimpan di memori."
        ),
        "err_generic_api": (
            "Permintaan transkripsi ke Groq gagal (status HTTP {code}). Silakan periksa pengaturan Anda atau coba lagi beberapa saat lagi. "
            "Perlu diingat bahwa audio dari percobaan yang gagal ini tidak disimpan di memori, jadi silakan rekam ulang saat Anda siap."
        ),
    },
    "vi": {
        "app_title": "Voice2Prompt v{version} — Studio Chuyển Giọng Nói Thành Văn Bản Cho AI Prompt",
        "app_subtitle": "Speech-to-Text Studio for AI Prompting (v{version})",
        "btn_settings": "⚙️ Cài đặt",
        "switch_ontop": "📌 Luôn nổi trên cùng",
        "btn_record_idle": "🔴 Nhấn để nói (Ghi âm / Phím cách)",
        "btn_record_listening": "⏹️ Đang nghe... Nhấn để dừng",
        "btn_record_processing": "⏳ Đang chuyển đổi...",
        "status_ready": "⚪ Sẵn sàng ghi âm (Nhấn nút hoặc phím Spacebar)",
        "status_recording": "🔴 Đang ghi âm giọng nói...",
        "status_auto_limit": "⏳ Tự động dừng (giới hạn an toàn 12 phút / 25 MB)...",
        "status_processing_groq": "⏳ Đang xử lý qua Groq Whisper...",
        "status_no_audio": "⚪ Không thu được dữ liệu âm thanh",
        "status_no_speech": "⚪ Không phát hiện giọng nói",
        "status_error": "❌ Lỗi chuyển đổi giọng nói",
        "status_done_copied": "✅ Đã chuyển đổi và sao chép vào Clipboard!",
        "status_done": "✅ Chuyển đổi hoàn tất!",
        "status_copied_history": "✅ Đã sao chép văn bản từ lịch sử!",
        "status_loaded_history": "📝 Đã tải văn bản vào khung soạn thảo",
        "status_settings_saved": "✅ Đã lưu cài đặt thành công",
        "status_hotkey_conflict": "⚠️ Phím tắt ({combo}) đang được sử dụng bởi ứng dụng khác. Vui lòng đổi trong Cài đặt.",
        "editor_title": "📝 Văn bản Prompt gửi cho AI (Có thể chỉnh sửa trực tiếp):",
        "char_count": "{count} ký tự",
        "btn_copy": "📋 Sao chép văn bản (Copy to Clipboard)",
        "btn_copied_flash": "✅ Đã sao chép vào Clipboard!",
        "check_autocopy": "📋 Tự động sao chép",
        "check_append": "Nối tiếp vào văn bản hiện có",
        "btn_clear": "🧹 Xóa",
        "hist_title": "🕒 10 bản ghi gần nhất",
        "btn_clear_hist": "Xóa hết",
        "hist_empty": "Chưa có lịch sử (chỉ lưu trên RAM trong phiên làm việc này)",
        "btn_hist_use": "✏️ Sửa",
        "btn_hist_copy": "📋 Chép",
        "confirm_clear_hist_title": "Xác nhận xóa",
        "confirm_clear_hist_msg": "Bạn có chắc chắn muốn xóa toàn bộ lịch sử của phiên này không?",
        "err_rec_title": "Lỗi ghi âm",
        "err_stt_title": "Lỗi chuyển đổi giọng nói",
        "settings_title": "Cài đặt Voice2Prompt (v{version})",
        "settings_ui_lang": "💬 Ngôn ngữ giao diện (UI Language):",
        "settings_mic": "🎙️ Micro (Thiết bị thu âm):",
        "settings_default_mic": "Micro mặc định (Default Microphone)",
        "settings_api_key": "🔑 Khóa API Groq (Lấy miễn phí tại console.groq.com hoặc đặt trong .env):",
        "settings_spoken_lang": "🌐 Ngôn ngữ nói (Spoken Language):",
        "settings_hotkey_header": "⌨️ Phím tắt toàn cục (Bấm từ bất kỳ cửa sổ nào):",
        "settings_hotkey_enable": "Bật phím tắt toàn cục (Global Hotkey)",
        "settings_btn_save": "Lưu cài đặt",
        "err_no_api_key": (
            "Chưa cấu hình Groq API Key. Vui lòng nhấn nút 'Cài đặt' (⚙️) ở góc trên bên phải để nhập khóa API miễn phí từ console.groq.com. "
            "Lưu ý rằng bản ghi âm vừa rồi không được giữ lại trong bộ nhớ, vì vậy vui lòng ghi âm lại sau khi đã lưu khóa."
        ),
        "err_invalid_wav": (
            "Dữ liệu âm thanh WAV trong bộ nhớ bị lỗi hoặc không hợp lệ nên không thể xử lý. "
            "Vui lòng kiểm tra kết nối micro và thử ghi âm lại, vì bộ đệm âm thanh bị lỗi không được giữ lại trong bộ nhớ."
        ),
        "err_rate_limit_429": (
            "Bạn đã chạm giới hạn số lần gọi mỗi phút của gói Groq miễn phí (ứng dụng vẫn hoạt động bình thường). "
            "Vui lòng đợi khoảng {wait} rồi ghi âm lại, vì dữ liệu âm thanh của lần gửi lỗi không được lưu giữ trong bộ nhớ. "
            "Nếu thường xuyên gặp giới hạn này, bạn nên nói liền mạch dài hơnใน mỗi lần bấm hoặc nâng cấp gói Groq API."
        ),
        "err_auth_401_403": (
            "Groq đã từ chối khóa API vì khóa không hợp lệ, đã hết hạn hoặc không có quyền truy cập. "
            "Vui lòng mở 'Cài đặt' (⚙️) để kiểm tra và nhập lại khóa API Groq hợp lệ từ console.groq.com. "
            "Để bảo mật quyền riêng tư, âm thanh vừa thu không được lưu trong bộ nhớ, vui lòng ghi âm lại sau khi cập nhật khóa."
        ),
        "err_network_conn": (
            "Không thể kết nối tới máy chủ chuyển đổi của Groq (mạng Internetของ bạn có thểกำลัง mất kết nối hoặc bị tường lửa chặn). "
            "Vui lòng kiểm tra kết nối mạng và thử lại. "
            "Vì Voice2Prompt không lưu các bản ghi âm lỗiลง ổ cứng hay bộ nhớ, bạn cần ghi âm lại sau khi có mạng."
        ),
        "err_timeout": (
            "Yêu cầu chuyển đổi giọng nói gửi tới Groq đã quá thời gian chờ (Timeout), thường do mạng chậm hoặc bản ghi âm quá dài. "
            "Vui lòng kiểm tra kết nối mạng và ghi âm lại, vì bộ đệm âm thanh trước đó không được giữ lại trong bộ nhớ."
        ),
        "err_server_5xx": (
            "Máy chủ chuyển đổi của Groq đang gặp sự cố nội bộ tạm thời (HTTP {code}); đây không phải lỗi của ứng dụng trên máy bạn. "
            "Vui lòng đợi giây lát rồi thử ghi âm lại, vì âm thanh của yêu cầu bị lỗi không được lưu lại trong bộ nhớ."
        ),
        "err_generic_api": (
            "Yêu cầu chuyển đổi giọng nói qua Groq không thành công (mã HTTP {code}). Vui lòng kiểm tra lại cài đặt hoặc thử lại sau ít phút. "
            "Lưu ý rằng âm thanh của lần thử lỗi này không được giữ lại trong bộ nhớ, vui lòng ghi âm lại khi sẵn sàng."
        ),
    },
}


def t(key: str, lang: str = "th", **kwargs) -> str:
    """Translate `key` into `lang` (any of the 11 UI languages, fallback to 'en') with keyword formatting."""
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
    result = {}
    for code, labels in SUPPORTED_SPOKEN_LANGUAGES:
        label = labels.get(ui_lang) or labels.get("en")
        result[label] = code
    return result


def get_spoken_language_label(iso_code: str, ui_lang: str = "th") -> str:
    """Return display label for a given ISO code in the current UI language."""
    for code, labels in SUPPORTED_SPOKEN_LANGUAGES:
        if code == iso_code:
            return labels.get(ui_lang) or labels.get("en")
    first_labels = SUPPORTED_SPOKEN_LANGUAGES[0][1]
    return first_labels.get(ui_lang) or first_labels.get("en")
