> 🌐 **Language / ภาษา:** **[🇬🇧 English](README.md)** | **[🇹🇭 ภาษาไทย](README.th.md)**

# 🎙️ Voice2Prompt (`v0.1.0`)

**Speech-to-Text Desktop Studio for AI Prompting (Powered by Groq `whisper-large-v3`)**

[![Platform: Windows Only](https://img.shields.io/badge/Platform-Windows%2010%2F11%20Only-0078D6?logo=windows)](#requirements)
[![License: MIT](https://img.shields.io/badge/License-MIT-10b981.svg)](LICENSE)
[![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-38bdf8.svg)](version.py)

**Voice2Prompt** is a lightweight **Windows** desktop application that lets you dictate long, natural voice prompts—including mixed languages and technical jargon—and instantly paste the transcribed text into **Claude Code, Cursor, ChatGPT, Gemini, or any terminal/IDE** without leaving your active window.

> **⚠️ Prerequisites at a Glance:**
> - **Windows Only:** Uses the native Win32 `RegisterHotKey` API (`user32.dll`) for zero-hook global hotkeys and Windows DPI awareness.
> - **Requires Your Own Groq API Key:** You must provide your own Groq API key (free tier available at [console.groq.com/keys](https://console.groq.com/keys)).

[![Voice2Prompt Screenshot](docs/screenshot.png)](https://youtu.be/QMGolEp1nx4)

> 🎬 **Watch the Behind-the-Scenes & Workflow Video:**
> - 🌐 **[English Video (YouTube)](https://youtu.be/QMGolEp1nx4)** — *Voice2Prompt: Try building simple tools for your own everyday life*
> - 🇹🇭 **[Thai Video / เวอร์ชันภาษาไทย (YouTube)](https://youtu.be/ItGYqpLYgaA)** — *เบื้องหลังการสร้าง Voice2Prompt: ลองสร้างเครื่องมือง่ายๆ ไว้ใช้ในชีวิตประจำวันด้วยตัวคุณเอง*

---

## ✨ Key Features

- **⚡ Fast Cloud Transcription (`whisper-large-v3`):** Uses Groq's LPU inference API for high-accuracy Speech-to-Text with low latency (actual response time depends on your network connection and recording length).
- **🌍 99 Languages Supported by Whisper (11 Built-in UI Presets + Auto-Detect):**
  - Underlying Groq `whisper-large-v3` supports **99 languages**.
  - Built-in UI selector includes **11 popular languages** verified against Groq's ISO-639-1 specification: **Thai (`th`), English (`en`), Chinese (`zh`), Japanese (`ja`), Korean (`ko`), Spanish (`es`), French (`fr`), German (`de`), Hindi (`hi`), Indonesian (`id`), Vietnamese (`vi`)**, plus **Auto-detect (`auto`)**.
  - Smart context prompting: Thai-English technical vocabulary hints are injected **only** when transcribing in Thai (`th`) or Auto-detect (`auto`), keeping non-Thai transcriptions pure.
- **💬 11 Interface Languages (Multilingual UI):** Automatically detects your Windows UI language on first launch, or switch the interface live in **Settings (`⚙️`)** across **11 languages** (**English, Thai, Chinese, Japanese, Korean, Spanish, French, German, Hindi, Indonesian, Vietnamese**) without restarting.
- **⌨️ Background Global Hotkey (`Ctrl + Alt + Space`):** Start and stop recording from inside any IDE, browser, or terminal without switching windows. Includes automatic conflict detection if another app has already registered the same shortcut.
- **📋 Auto-Copy to Clipboard:** Automatically copies the finished transcript to your clipboard—just press `Ctrl + V` in your AI CLI or chat box.
- **🔒 Zero-Disk History & Audio:**
  - Audio is recorded directly into an in-memory `io.BytesIO` WAV buffer (`16 kHz`, 16-bit mono) and never written to disk.
  - The 10 most recent transcripts are stored **strictly in RAM** (`collections.deque(maxlen=10)`) and vanish completely when you close the app.
- **🛡️ Long-Audio Auto-Chunking & 12-Minute Safety Cap:** Automatically splits recordings longer than 10 minutes into seamless 10-minute WAV chunks in memory and enforces a 12-minute (`~23 MB`) safety cap to stay safely below Groq's `25 MB` upload limit.

---

## 🔐 Where Your Data Goes (Privacy & Security Transparency)

We believe in strict transparency about how your audio and credentials are handled:

1. **Where Audio Is Processed (Third-Party Cloud API):**
   - Voice2Prompt **does not** run a local Whisper model on your GPU/CPU.
   - When you stop recording, the in-memory WAV audio buffer is sent over HTTPS (`https://api.groq.com/openai/v1/audio/transcriptions`) directly to **Groq Inc.** using your own API key. Please review [Groq's Privacy Policy](https://groq.com/privacy-policy/) regarding how Groq handles API requests.
2. **Where Your API Key Is Stored:**
   - **If loaded from an Environment Variable (`GROQ_API_KEY`) or `.env` file:** Your key stays strictly in RAM for the current session and is **never** written to `config.json`.
   - **If entered and saved in the GUI Settings (`⚙️`) dialog:** Your key is saved as **plain text** in your local Windows user profile at `%APPDATA%\Voice2Prompt\config.json` so you don't have to re-type it every time. Do not share your `%APPDATA%\Voice2Prompt\config.json` file with anyone.
3. **What Is Saved on Your Disk:**
   - **Audio files:** **None (`0 bytes`).** Recorded audio is held in RAM and discarded immediately after transcription (even if an error occurs).
   - **Prompt history:** **None (`0 bytes`).** Recent transcripts live only in RAM during the active session.
4. **What the Developers Receive:**
   - **Nothing.** Voice2Prompt contains **zero** telemetry, analytics, crash reporters, or intermediate proxy servers.

For vulnerability reporting instructions, please see [SECURITY.md](SECURITY.md).

---

## 🔑 Getting a Free Groq API Key

1. Visit **[GroqCloud Console](https://console.groq.com/keys)** and sign in.
2. Click **"Create API Key"** and copy your key (starts with `gsk_...`).
3. Provide the key to Voice2Prompt using **one** of these 3 methods:
   - **Method 1 (Easiest — GUI Settings):** Launch the app, click **`⚙️ Settings`** in the top-right corner, paste your `gsk_...` key, and click **Save Settings**.
   - **Method 2 (`.env` File for Developers):** Copy `.env.example` to `.env` and set:
     ```env
     GROQ_API_KEY=gsk_your_api_key_here
     ```
   - **Method 3 (System Environment Variable):** Set `GROQ_API_KEY` (or `VOICE2PROMPT_ENV_FILE` pointing to a custom `.env` path) in your Windows User Environment Variables.

---

## 🚀 Installation & Running from Source

### Requirements
- **OS:** Windows 10 or Windows 11 (64-bit)
- **Python:** Python 3.10 or newer
- **Hardware:** Any working microphone input device

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/wichayasith-creator/Voice2Prompt.git
cd Voice2Prompt

# 2. Install runtime dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

---

## 🛠️ Building a Standalone `.exe` & Running Tests

If you want to run the test suite or package Voice2Prompt into a standalone Windows executable (`dist\Voice2Prompt.exe`):

```bash
# Install development & build dependencies (pytest, pyinstaller)
pip install -r requirements-dev.txt

# Run the automated unit test suite
pytest t_voice2prompt.py

# Build standalone executable (or simply run build.bat)
pyinstaller --noconsole --onefile --clean --collect-all customtkinter --name "Voice2Prompt" main.py
```

Running `build.bat` automatically builds `dist\Voice2Prompt.exe` and prints its **SHA256 checksum**. You can also run `make_checksum.bat` at any time to regenerate `dist\Voice2Prompt.exe.sha256.txt`.

---

## 🛡️ Windows SmartScreen & Antivirus Notice

Because open-source builds of `Voice2Prompt.exe` are packaged with **PyInstaller (`--onefile`)** and are **not digitally signed** with a paid Extended Validation (EV) code-signing certificate:

- Windows Defender SmartScreen may display an *"Windows protected your PC — Unknown publisher"* prompt on first launch, and some heuristic antivirus scanners may flag unsigned PyInstaller bootloaders.
- **Recommended Safe Practices:**
  1. **Never disable Windows Defender SmartScreen or your antivirus software.**
  2. If downloading a pre-built `.exe` from official **GitHub Releases**, always verify that its **SHA256 checksum** matches the checksum published in the release notes (`certutil -hashfile Voice2Prompt.exe SHA256`).
  3. If you prefer maximum assurance, run directly from Python source (`python main.py`) or build the `.exe` yourself using `build.bat` after inspecting the code.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
