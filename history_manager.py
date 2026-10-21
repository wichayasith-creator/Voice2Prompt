import uuid
from datetime import datetime

class HistoryManager:
    """
    In-memory history manager for Voice2Prompt.
    Stores up to recent entries in RAM during the active session.
    No data is persisted to disk, preserving privacy and clean state upon app restart.
    """
    def __init__(self):
        self._items = []

    def add(self, text: str) -> dict:
        text = text.strip()
        if not text:
            return None
        
        # Don't add duplicate if it's identical to the latest entry
        if self._items and self._items[0].get("text") == text:
            return self._items[0]

        item = {
            "id": str(uuid.uuid4())[:8],
            "text": text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time_display": datetime.now().strftime("%H:%M:%S")
        }
        self._items.insert(0, item)
        return item

    def get_recent(self, limit: int = 10) -> list:
        return self._items[:limit]

    def get_all(self) -> list:
        return self._items

    def delete(self, item_id: str):
        self._items = [item for item in self._items if item.get("id") != item_id]

    def clear(self):
        self._items = []
