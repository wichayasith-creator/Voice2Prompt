import ctypes
from ctypes import wintypes
import threading

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

HOTKEY_PRESETS = {
    "Ctrl + Alt + Space": (MOD_CONTROL | MOD_ALT, 0x20),   # VK_SPACE
    "Ctrl + Shift + R": (MOD_CONTROL | MOD_SHIFT, ord('R')),
    "Ctrl + Alt + R": (MOD_CONTROL | MOD_ALT, ord('R')),
    "F8": (0, 0x77),                                       # VK_F8
    "F9": (0, 0x78)                                        # VK_F9
}

class GlobalHotkeyManager:
    """
    Lightweight, native Windows Global Hotkey manager via Win32 RegisterHotKey.
    Requires no external pip packages (zero-dependency).
    """
    def __init__(self, callback):
        self.callback = callback
        self.thread = None
        self.thread_id = None
        self.enabled = False
        self.combo_name = "Ctrl + Alt + Space"
        self._lock = threading.Lock()

    def start(self, combo_name: str = "Ctrl + Alt + Space"):
        with self._lock:
            self.stop()
            self.combo_name = combo_name
            self.enabled = True
            ready_event = threading.Event()
            self.thread = threading.Thread(target=self._run_loop, args=(ready_event,), daemon=True)
            self.thread.start()
            ready_event.wait(timeout=1.0)

    def stop(self):
        self.enabled = False
        if self.thread_id:
            try:
                ctypes.windll.user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        self.thread = None
        self.thread_id = None

    def _run_loop(self, ready_event: threading.Event):
        user32 = ctypes.windll.user32
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        mod, vk = HOTKEY_PRESETS.get(self.combo_name, HOTKEY_PRESETS["Ctrl + Alt + Space"])

        # Try RegisterHotKey with MOD_NOREPEAT, fallback without
        res = user32.RegisterHotKey(None, 1, mod | MOD_NOREPEAT, vk)
        if not res:
            res = user32.RegisterHotKey(None, 1, mod, vk)

        ready_event.set()

        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                if self.callback and self.enabled:
                    try:
                        self.callback()
                    except Exception as e:
                        print(f"Hotkey callback error: {e}")
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, 1)
