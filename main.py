import os
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# 1. Windows DPI-Awareness before GUI init to prevent blurred text
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from version import __version__
from i18n import (
    t,
    SUPPORTED_UI_LANGUAGES,
    get_spoken_language_display_map,
    get_spoken_language_label,
)
from audio_recorder import AudioRecorder
from stt_service import STTService
from history_manager import HistoryManager
from hotkey_manager import GlobalHotkeyManager, HOTKEY_PRESETS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT_FAMILY = "Leelawadee UI"
MAX_RECORDING_SECONDS = 720  # 12 minutes (~23 MB WAV, safely within Groq 25 MB limit)


class Voice2PromptApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Services
        self.history_mgr = HistoryManager()
        self.stt_service = STTService()
        self.recorder = AudioRecorder()

        # State
        self.ui_lang = self.stt_service.config.get("ui_lang", "th")
        self.record_start_time = 0
        self.is_recording = False
        self.is_processing = False
        self.append_mode = False
        self.auto_copy = self.stt_service.config.get("auto_copy", True)
        self._startup_hotkey_conflict_combo = None

        self.title(t("app_title", lang=self.ui_lang, version=__version__))
        self.geometry("1040x700")
        self.minsize(880, 580)

        # Global Hotkey Manager
        self.hotkey_mgr = GlobalHotkeyManager(callback=self._on_global_hotkey)
        if self.stt_service.config.get("global_hotkey_enabled", True):
            combo = self.stt_service.config.get("global_hotkey_combo", "Ctrl + Alt + Space")
            ok = self.hotkey_mgr.start(combo)
            if not ok:
                self._startup_hotkey_conflict_combo = combo

        self._build_ui()
        self._bind_shortcuts()
        self._load_history()

        if self._startup_hotkey_conflict_combo:
            self.status_label.configure(
                text=t("status_hotkey_conflict", lang=self.ui_lang, combo=self._startup_hotkey_conflict_combo),
                text_color="#fbbf24",
            )

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_global_hotkey(self):
        # Trigger record toggle safely on Tkinter main thread
        self.after(0, self._toggle_record)

    def _play_sound_cue(self, kind: str):
        """Play a non-blocking 2-tone audio cue on start/done if sound_cue_enabled is True."""
        if not self.stt_service.config.get("sound_cue_enabled", True):
            return

        def _beep_worker():
            try:
                import winsound
                if kind == "start":
                    winsound.Beep(660, 55)
                    winsound.Beep(880, 65)
                elif kind == "done":
                    winsound.Beep(784, 55)
                    winsound.Beep(1175, 75)
            except Exception:
                pass

        threading.Thread(target=_beep_worker, daemon=True).start()

    def _on_close(self):
        self.hotkey_mgr.stop()
        if self.is_recording:
            try:
                self.recorder.stop_recording()
            except Exception:
                pass
        self.destroy()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#18181b", height=60)
        self.header_frame.pack(fill="x", side="top")

        # Title & Icon
        self.logo_label = ctk.CTkLabel(
            self.header_frame,
            text="🎙️ Voice2Prompt",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color="#f4f4f5",
        )
        self.logo_label.pack(side="left", padx=20, pady=12)

        self.sub_logo = ctk.CTkLabel(
            self.header_frame,
            text=t("app_subtitle", lang=self.ui_lang, version=__version__),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color="#a1a1aa",
        )
        self.sub_logo.pack(side="left", pady=12)

        # Header controls
        self.btn_settings = ctk.CTkButton(
            self.header_frame,
            text=t("btn_settings", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            width=100,
            height=32,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._open_settings,
        )
        self.btn_settings.pack(side="right", padx=15, pady=14)

        self.switch_ontop = ctk.CTkSwitch(
            self.header_frame,
            text=t("switch_ontop", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            command=self._toggle_always_on_top,
        )
        self.switch_ontop.pack(side="right", padx=10, pady=14)

        # ── Main Container (2 Columns) ──────────────────────────────────────
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=12)

        # Left Column (Editor & Recording Controls)
        self.left_frame = ctk.CTkFrame(self.main_container, fg_color="#18181b", corner_radius=12)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Right Column (History - 10 Messages)
        self.right_frame = ctk.CTkFrame(self.main_container, fg_color="#18181b", corner_radius=12, width=350)
        self.right_frame.pack(side="right", fill="both", expand=False, padx=(8, 0))
        self.right_frame.pack_propagate(False)

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        # 1. Recording Bar
        self.rec_control_box = ctk.CTkFrame(self.left_frame, fg_color="#27272a", corner_radius=10)
        self.rec_control_box.pack(fill="x", padx=15, pady=15)

        # Record button
        self.btn_record = ctk.CTkButton(
            self.rec_control_box,
            text=t("btn_record_idle", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            fg_color="#e11d48",
            hover_color="#be123c",
            height=46,
            corner_radius=23,
            command=self._toggle_record,
        )
        self.btn_record.pack(fill="x", padx=15, pady=(15, 10))

        # Status & Timer frame
        stat_frame = ctk.CTkFrame(self.rec_control_box, fg_color="transparent")
        stat_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            stat_frame,
            text=t("status_ready", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color="#a1a1aa",
        )
        self.status_label.pack(side="left")

        self.timer_label = ctk.CTkLabel(
            stat_frame,
            text="00:00",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color="#f4f4f5",
        )
        self.timer_label.pack(side="right")

        # VU Volume meter bar
        self.vu_bar = ctk.CTkProgressBar(self.rec_control_box, height=8, corner_radius=4)
        self.vu_bar.set(0.0)
        self.vu_bar.configure(progress_color="#10b981", fg_color="#3f3f46")
        self.vu_bar.pack(fill="x", padx=15, pady=(0, 15))

        # 2. Text Editor Area
        editor_header = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        editor_header.pack(fill="x", padx=15, pady=(5, 4))

        self.editor_title = ctk.CTkLabel(
            editor_header,
            text=t("editor_title", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color="#e4e4e7",
        )
        self.editor_title.pack(side="left")

        self.char_count_label = ctk.CTkLabel(
            editor_header,
            text=t("char_count", lang=self.ui_lang, count=0),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color="#71717a",
        )
        self.char_count_label.pack(side="right")

        # Text box
        self.textbox = ctk.CTkTextbox(
            self.left_frame,
            font=ctk.CTkFont(family=FONT_FAMILY, size=15),
            wrap="word",
            corner_radius=8,
            fg_color="#09090b",
            text_color="#fafafa",
        )
        self.textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.textbox.bind("<KeyRelease>", self._on_text_change)

        # 3. Action Toolbar (Bottom)
        action_bar = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        action_bar.pack(fill="x", padx=15, pady=(0, 15))

        # Big Copy Button
        self.btn_copy = ctk.CTkButton(
            action_bar,
            text=t("btn_copy", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=42,
            corner_radius=8,
            command=self._copy_text,
        )
        self.btn_copy.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Auto Copy Checkbox
        self.check_autocopy = ctk.CTkCheckBox(
            action_bar,
            text=t("check_autocopy", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            command=self._toggle_autocopy,
        )
        if self.auto_copy:
            self.check_autocopy.select()
        else:
            self.check_autocopy.deselect()
        self.check_autocopy.pack(side="right", padx=6)

        # Append Mode Checkbox
        self.check_append = ctk.CTkCheckBox(
            action_bar,
            text=t("check_append", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            command=self._toggle_append_mode,
        )
        self.check_append.pack(side="right", padx=6)

        # Clear Button
        self.btn_clear = ctk.CTkButton(
            action_bar,
            text=t("btn_clear", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            width=76,
            height=42,
            fg_color="#27272a",
            hover_color="#3f3f46",
            command=self._clear_text,
        )
        self.btn_clear.pack(side="right", padx=(0, 6))

    def _build_right_panel(self):
        # Header
        hist_header = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        hist_header.pack(fill="x", padx=15, pady=(15, 10))

        self.lbl_hist = ctk.CTkLabel(
            hist_header,
            text=t("hist_title", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color="#f4f4f5",
        )
        self.lbl_hist.pack(side="left")

        self.btn_clear_hist = ctk.CTkButton(
            hist_header,
            text=t("btn_clear_hist", lang=self.ui_lang),
            width=54,
            height=26,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            fg_color="#27272a",
            hover_color="#71717a",
            command=self._clear_history,
        )
        self.btn_clear_hist.pack(side="right")

        # Scrollable list for cards
        self.history_scroll = ctk.CTkScrollableFrame(
            self.right_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        self.history_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

    def apply_ui_language(self, lang: str = None):
        """Update all visible UI widgets to match the active UI language ('th' or 'en')."""
        if lang in SUPPORTED_UI_LANGUAGES:
            self.ui_lang = lang
        else:
            self.ui_lang = self.stt_service.config.get("ui_lang", "th")

        self.title(t("app_title", lang=self.ui_lang, version=__version__))
        self.sub_logo.configure(text=t("app_subtitle", lang=self.ui_lang, version=__version__))
        self.btn_settings.configure(text=t("btn_settings", lang=self.ui_lang))
        self.switch_ontop.configure(text=t("switch_ontop", lang=self.ui_lang))

        if self.is_recording:
            self.btn_record.configure(text=t("btn_record_listening", lang=self.ui_lang))
        elif self.is_processing:
            self.btn_record.configure(text=t("btn_record_processing", lang=self.ui_lang))
        else:
            self.btn_record.configure(text=t("btn_record_idle", lang=self.ui_lang))

        self.editor_title.configure(text=t("editor_title", lang=self.ui_lang))
        self._on_text_change()
        self.btn_copy.configure(text=t("btn_copy", lang=self.ui_lang))
        self.check_autocopy.configure(text=t("check_autocopy", lang=self.ui_lang))
        self.check_append.configure(text=t("check_append", lang=self.ui_lang))
        self.btn_clear.configure(text=t("btn_clear", lang=self.ui_lang))
        self.lbl_hist.configure(text=t("hist_title", lang=self.ui_lang))
        self.btn_clear_hist.configure(text=t("btn_clear_hist", lang=self.ui_lang))
        self._load_history()

    def _bind_shortcuts(self):
        self.bind("<F8>", lambda e: self._toggle_record())
        # Spacebar records only when textbox does not have focus
        self.bind("<space>", self._on_space_pressed)

    def _on_space_pressed(self, event):
        focused = self.focus_get()
        if focused != self.textbox._textbox:
            self._toggle_record()

    def _toggle_always_on_top(self):
        is_on = self.switch_ontop.get() == 1
        self.attributes("-topmost", is_on)

    def _toggle_append_mode(self):
        self.append_mode = (self.check_append.get() == 1)

    def _toggle_autocopy(self):
        self.auto_copy = (self.check_autocopy.get() == 1)
        self.stt_service.save_setting("auto_copy", self.auto_copy)

    def _on_text_change(self, event=None):
        text = self.textbox.get("1.0", "end-1c")
        self.char_count_label.configure(text=t("char_count", lang=self.ui_lang, count=len(text)))

    def _toggle_record(self):
        if self.is_processing:
            # Block starting new recording while transcribing
            return

        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        try:
            device_idx = self.stt_service.config.get("device_index")
            self.recorder.start_recording(device_index=device_idx)
            self.is_recording = True
            self.record_start_time = time.time()
            self._play_sound_cue("start")

            # UI Update
            self.btn_record.configure(
                text=t("btn_record_listening", lang=self.ui_lang),
                fg_color="#9f1239",
                hover_color="#881337",
            )
            self.status_label.configure(text=t("status_recording", lang=self.ui_lang), text_color="#f43f5e")

            # Main-thread periodic polling for timer & VU meter (Thread-safe)
            self._poll_timer_and_vu()
        except Exception as e:
            messagebox.showerror(t("err_rec_title", lang=self.ui_lang), str(e))
            self.is_recording = False

    def _poll_timer_and_vu(self):
        if not self.is_recording:
            self.vu_bar.set(0.0)
            return

        elapsed = int(time.time() - self.record_start_time)
        mins, secs = divmod(elapsed, 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        self.vu_bar.set(self.recorder.current_volume)

        # Safety auto-stop at 12 minutes (~23 MB, safely within Groq 25 MB limit)
        if elapsed >= MAX_RECORDING_SECONDS:
            self._stop_recording(auto_limit=True)
            return

        self.after(50, self._poll_timer_and_vu)

    def _stop_recording(self, auto_limit: bool = False):
        if not self.is_recording:
            return

        self.is_recording = False
        self.is_processing = True
        self.vu_bar.set(0.0)

        self.btn_record.configure(
            text=t("btn_record_processing", lang=self.ui_lang),
            fg_color="#d97706",
            hover_color="#b45309",
            state="disabled",
        )
        if auto_limit:
            self.status_label.configure(text=t("status_auto_limit", lang=self.ui_lang), text_color="#fbbf24")
        else:
            self.status_label.configure(text=t("status_processing_groq", lang=self.ui_lang), text_color="#fbbf24")

        # Process STT in background thread
        threading.Thread(target=self._process_stt_thread, daemon=True).start()

    def _process_stt_thread(self):
        try:
            wav_bytes = self.recorder.stop_recording()
            if not wav_bytes:
                self.after(0, lambda: self._update_status_after_stt(t("status_no_audio", lang=self.ui_lang), "#a1a1aa"))
                return

            text = self.stt_service.transcribe(wav_bytes)
            if not text:
                self.after(0, lambda: self._update_status_after_stt(t("status_no_speech", lang=self.ui_lang), "#a1a1aa"))
                return

            # Apply transcription on main thread
            self.after(0, lambda: self._apply_transcription(text))
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: messagebox.showerror(t("err_stt_title", lang=self.ui_lang), err_msg))
            self.after(0, lambda: self._update_status_after_stt(t("status_error", lang=self.ui_lang), "#f43f5e"))

    def _apply_transcription(self, new_text: str):
        if self.append_mode:
            current_text = self.textbox.get("1.0", "end-1c").strip()
            if current_text:
                full_text = current_text + " " + new_text
            else:
                full_text = new_text
        else:
            full_text = new_text

        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", full_text)
        self._on_text_change()

        # Add to in-memory history
        self.history_mgr.add(full_text)
        self._load_history()

        # Auto Copy if enabled
        self._play_sound_cue("done")
        if self.auto_copy:
            self._copy_text(silent=True)
            self._update_status_after_stt(t("status_done_copied", lang=self.ui_lang), "#10b981")
        else:
            self._update_status_after_stt(t("status_done", lang=self.ui_lang), "#10b981")

    def _update_status_after_stt(self, status_text: str, color: str):
        self.is_processing = False
        self.btn_record.configure(
            text=t("btn_record_idle", lang=self.ui_lang),
            fg_color="#e11d48",
            hover_color="#be123c",
            state="normal",
        )
        self.status_label.configure(text=status_text, text_color=color)

    def _copy_text(self, silent: bool = False):
        text = self.textbox.get("1.0", "end-1c").strip()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

        if not silent:
            orig_text = t("btn_copy", lang=self.ui_lang)
            orig_color = self.btn_copy.cget("fg_color")
            self.btn_copy.configure(text=t("btn_copied_flash", lang=self.ui_lang), fg_color="#10b981")
            self.after(1400, lambda: self.btn_copy.configure(text=orig_text, fg_color=orig_color))

    def _clear_text(self):
        self.textbox.delete("1.0", "end")
        self._on_text_change()

    def _load_history(self):
        # Clear existing widgets in scrollable frame
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        items = self.history_mgr.get_recent(limit=10)
        if not items:
            lbl_empty = ctk.CTkLabel(
                self.history_scroll,
                text=t("hist_empty", lang=self.ui_lang),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color="#71717a",
                wraplength=300,
            )
            lbl_empty.pack(pady=20)
            return

        for item in items:
            card = ctk.CTkFrame(self.history_scroll, fg_color="#27272a", corner_radius=8)
            card.pack(fill="x", pady=4, padx=2)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=8, pady=(6, 2))

            time_lbl = ctk.CTkLabel(
                top_row,
                text=f"🕒 {item.get('time_display', '')}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                text_color="#a1a1aa",
            )
            time_lbl.pack(side="left")

            btn_use = ctk.CTkButton(
                top_row,
                text=t("btn_hist_use", lang=self.ui_lang),
                width=52,
                height=22,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color="#3f3f46",
                hover_color="#52525b",
                command=lambda txt=item["text"]: self._load_item_to_editor(txt),
            )
            btn_use.pack(side="right", padx=(4, 0))

            btn_card_copy = ctk.CTkButton(
                top_row,
                text=t("btn_hist_copy", lang=self.ui_lang),
                width=54,
                height=22,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color="#059669",
                hover_color="#047857",
                command=lambda txt=item["text"]: self._copy_specific_text(txt),
            )
            btn_card_copy.pack(side="right")

            text_preview = item.get("text", "")
            if len(text_preview) > 120:
                text_preview = text_preview[:117] + "..."

            msg_lbl = ctk.CTkLabel(
                card,
                text=text_preview,
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color="#e4e4e7",
                wraplength=280,
                justify="left",
                anchor="w",
            )
            msg_lbl.pack(fill="x", padx=8, pady=(0, 8), anchor="w")

    def _copy_specific_text(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.status_label.configure(text=t("status_copied_history", lang=self.ui_lang), text_color="#10b981")

    def _load_item_to_editor(self, text: str):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self._on_text_change()
        self.status_label.configure(text=t("status_loaded_history", lang=self.ui_lang), text_color="#38bdf8")

    def _clear_history(self):
        if messagebox.askyesno(
            t("confirm_clear_hist_title", lang=self.ui_lang),
            t("confirm_clear_hist_msg", lang=self.ui_lang),
        ):
            self.history_mgr.clear()
            self._load_history()

    # ── Settings Dialog ──────────────────────────────────────────────────────
    def _open_settings(self):
        settings_win = ctk.CTkToplevel(self)
        settings_win.title(t("settings_title", lang=self.ui_lang, version=__version__))
        settings_win.geometry("540x650")
        settings_win.resizable(False, False)
        settings_win.attributes("-topmost", True)
        settings_win.grab_set()

        pad_f = ctk.CTkFrame(settings_win, fg_color="transparent")
        pad_f.pack(fill="both", expand=True, padx=25, pady=16)

        # 0. UI Language
        ctk.CTkLabel(
            pad_f,
            text=t("settings_ui_lang", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
        ).pack(anchor="w", pady=(0, 2))
        ui_lang_display_to_code = {label: code for code, label in SUPPORTED_UI_LANGUAGES.items()}
        ui_lang_combo = ctk.CTkComboBox(
            pad_f,
            values=list(ui_lang_display_to_code.keys()),
            width=480,
            font=ctk.CTkFont(family=FONT_FAMILY),
        )
        ui_lang_combo.set(SUPPORTED_UI_LANGUAGES.get(self.ui_lang, SUPPORTED_UI_LANGUAGES["th"]))
        ui_lang_combo.pack(pady=(0, 10))

        # 1. Microphone Device
        ctk.CTkLabel(
            pad_f,
            text=t("settings_mic", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
        ).pack(anchor="w", pady=(0, 2))
        devices = AudioRecorder.list_input_devices()
        dev_names = [f"[{d['index']}] {d['name']}" for d in devices] or [
            t("settings_default_mic", lang=self.ui_lang)
        ]

        current_dev_idx = self.stt_service.config.get("device_index")
        default_val = dev_names[0]
        if current_dev_idx is not None:
            for n in dev_names:
                if n.startswith(f"[{current_dev_idx}]"):
                    default_val = n
                    break

        dev_combo = ctk.CTkComboBox(pad_f, values=dev_names, width=480, font=ctk.CTkFont(family=FONT_FAMILY))
        dev_combo.set(default_val)
        dev_combo.pack(pady=(0, 10))

        # 2. Groq API Key
        ctk.CTkLabel(
            pad_f,
            text=t("settings_api_key", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
        ).pack(anchor="w", pady=(0, 2))
        key_entry = ctk.CTkEntry(
            pad_f,
            width=480,
            show="*",
            placeholder_text="gsk_...",
            font=ctk.CTkFont(family=FONT_FAMILY),
        )
        key_entry.insert(0, self.stt_service.config.get("groq_api_key", ""))
        key_entry.pack(pady=(0, 10))

        # 3. Spoken Language Pair (Primary + Secondary Dual-Language Support)
        dual_lbl_txt = (
            "🌐 ภาษาที่ใช้พูดคู่ 2 ภาษา (ภาษาหลัก + ภาษารอง):"
            if self.ui_lang == "th"
            else t("settings_spoken_lang", lang=self.ui_lang)
        )
        ctk.CTkLabel(
            pad_f,
            text=dual_lbl_txt,
            font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
        ).pack(anchor="w", pady=(0, 2))

        spoken_lang_map = get_spoken_language_display_map(self.ui_lang)
        lang_pair_row = ctk.CTkFrame(pad_f, fg_color="transparent")
        lang_pair_row.pack(fill="x", pady=(0, 10))

        lang_combo = ctk.CTkComboBox(
            lang_pair_row,
            values=list(spoken_lang_map.keys()),
            width=232,
            font=ctk.CTkFont(family=FONT_FAMILY),
        )
        cur_lang = self.stt_service.config.get("language", "th")
        lang_combo.set(get_spoken_language_label(cur_lang, self.ui_lang))
        lang_combo.pack(side="left")

        ctk.CTkLabel(
            lang_pair_row,
            text="+",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
        ).pack(side="left", padx=6)

        sec_lang_combo = ctk.CTkComboBox(
            lang_pair_row,
            values=list(spoken_lang_map.keys()),
            width=232,
            font=ctk.CTkFont(family=FONT_FAMILY),
        )
        cur_sec_lang = self.stt_service.config.get("secondary_language", "en")
        sec_lang_combo.set(get_spoken_language_label(cur_sec_lang, self.ui_lang))
        sec_lang_combo.pack(side="right")

        # 4. Global Hotkey & Dual Sound Cue Settings
        ctk.CTkLabel(
            pad_f,
            text=t("settings_hotkey_header", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))

        hotkey_enable_var = tk.BooleanVar(value=self.stt_service.config.get("global_hotkey_enabled", True))
        check_hotkey = ctk.CTkCheckBox(
            pad_f,
            text=t("settings_hotkey_enable", lang=self.ui_lang),
            variable=hotkey_enable_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        )
        check_hotkey.pack(anchor="w", pady=(0, 6))

        hotkey_options = list(HOTKEY_PRESETS.keys())
        hotkey_combo = ctk.CTkComboBox(pad_f, values=hotkey_options, width=480, font=ctk.CTkFont(family=FONT_FAMILY))
        cur_combo = self.stt_service.config.get("global_hotkey_combo", "Ctrl + Alt + Space")
        if cur_combo in hotkey_options:
            hotkey_combo.set(cur_combo)
        else:
            hotkey_combo.set(hotkey_options[0])
        hotkey_combo.pack(pady=(0, 10))

        sound_cue_var = tk.BooleanVar(value=self.stt_service.config.get("sound_cue_enabled", True))
        sound_cue_txt = (
            "🔊 เปิดเสียงสัญญาณคู่ 2 จังหวะ (เตือนตอนเริ่มอัด & แปลงเสร็จ)"
            if self.ui_lang == "th"
            else "🔊 Enable 2-Tone Audio Cues (Start & Complete Chime)"
        )
        check_sound_cue = ctk.CTkCheckBox(
            pad_f,
            text=sound_cue_txt,
            variable=sound_cue_var,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        )
        check_sound_cue.pack(anchor="w", pady=(0, 14))

        # Save Button
        def save():
            # UI Language
            chosen_ui_lang = ui_lang_display_to_code.get(ui_lang_combo.get(), "th")
            self.stt_service.save_setting("ui_lang", chosen_ui_lang)

            selected_dev_str = dev_combo.get()
            dev_idx = None
            if selected_dev_str.startswith("["):
                try:
                    dev_idx = int(selected_dev_str.split("]")[0].replace("[", ""))
                except Exception:
                    dev_idx = None

            self.stt_service.save_setting("device_index", dev_idx)

            # API Key
            new_key = key_entry.get().strip()
            orig_key = self.stt_service.config.get("groq_api_key", "").strip()
            if new_key != orig_key:
                self.stt_service.set_user_api_key(new_key)

            # Spoken Language Pair (Primary + Secondary)
            chosen_spoken_code = spoken_lang_map.get(lang_combo.get(), "th")
            chosen_sec_code = spoken_lang_map.get(sec_lang_combo.get(), "en")
            self.stt_service.save_setting("language", chosen_spoken_code)
            self.stt_service.save_setting("secondary_language", chosen_sec_code)
            self.stt_service.save_setting("sound_cue_enabled", sound_cue_var.get())

            # Apply UI language immediately
            self.apply_ui_language(chosen_ui_lang)

            # Global Hotkey
            hk_enabled = hotkey_enable_var.get()
            hk_choice = hotkey_combo.get()
            self.stt_service.save_setting("global_hotkey_enabled", hk_enabled)
            self.stt_service.save_setting("global_hotkey_combo", hk_choice)

            # Reconfigure hotkey manager live & check conflict
            hotkey_ok = True
            if hk_enabled:
                hotkey_ok = self.hotkey_mgr.start(hk_choice)
            else:
                self.hotkey_mgr.stop()

            settings_win.destroy()
            if hk_enabled and not hotkey_ok:
                self.status_label.configure(
                    text=t("status_hotkey_conflict", lang=self.ui_lang, combo=hk_choice),
                    text_color="#fbbf24",
                )
            else:
                self.status_label.configure(
                    text=t("status_settings_saved", lang=self.ui_lang),
                    text_color="#10b981",
                )

        btn_save = ctk.CTkButton(
            pad_f,
            text=t("settings_btn_save", lang=self.ui_lang),
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            height=38,
            command=save,
        )
        btn_save.pack(fill="x")


if __name__ == "__main__":
    app = Voice2PromptApp()
    app.mainloop()
