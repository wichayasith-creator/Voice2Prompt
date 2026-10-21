# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in **Voice2Prompt**, please **do not** open a public GitHub issue.

Instead, please report it privately using **GitHub Private Vulnerability Reporting (Security Advisories)** on this repository:
1. Go to the **Security** tab of the repository on GitHub.
2. Click **Report a vulnerability** to open a private advisory report.
3. Provide steps to reproduce the issue and any relevant technical details.

---

## Security & Data Handling Scope

To help users and auditors understand how **Voice2Prompt** handles credentials and audio data:

1. **API Key Storage & Isolation:**
   * Users provide their own **Groq API Key** (`gsk_...`).
   * If the key is loaded from an environment variable (`GROQ_API_KEY`) or a `.env` file (`VOICE2PROMPT_ENV_FILE` / `.env`), it is kept strictly in memory and is **never** written to `%APPDATA%\Voice2Prompt\config.json`.
   * If a user explicitly enters and saves an API key through the in-app **Settings (`⚙️`)** dialog, that key is stored in plain text inside the user's local profile at `%APPDATA%\Voice2Prompt\config.json`.
2. **Third-Party Audio Processing:**
   * Recorded audio is held in RAM (`io.BytesIO` WAV buffer) and transmitted over HTTPS (`https://api.groq.com/openai/v1/audio/transcriptions`) to **Groq Cloud** for speech-to-text transcription using `whisper-large-v3`.
   * Audio is **not** processed locally on the machine.
3. **Zero Disk Persistence for Audio & History:**
   * Voice2Prompt never writes recorded `.wav` files to disk.
   * The 10-item recent transcription history is stored purely in RAM (`HistoryManager`) and is cleared immediately when the application closes.
   * The developers of Voice2Prompt do not operate any backend servers and never receive your audio, transcripts, or API keys.
