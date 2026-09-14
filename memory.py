import json
import os
import uuid
from datetime import datetime

CHATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats.json")


class ChatStore:
    """Handles persistence of multiple chat sessions to a local JSON file."""

    def __init__(self, path: str = CHATS_FILE):
        self.path = path
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def all_chats(self):
        """Return chats sorted by most recently updated first."""
        items = list(self._data.values())
        items.sort(key=lambda c: c.get("updated_at", ""), reverse=True)
        return items

    def get(self, chat_id: str):
        return self._data.get(chat_id)

    def create_chat(self) -> str:
        chat_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        self._data[chat_id] = {
            "id": chat_id,
            "title": "New chat",
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }
        self._save()
        return chat_id

    def delete_chat(self, chat_id: str):
        if chat_id in self._data:
            del self._data[chat_id]
            self._save()

    def rename_chat(self, chat_id: str, title: str):
        if chat_id in self._data:
            self._data[chat_id]["title"] = title[:60]
            self._save()

    def ensure_chat(self, chat_id: str):
        """Create a chat entry for chat_id if it doesn't exist yet (lazy creation)."""
        if chat_id not in self._data:
            now = datetime.now().isoformat()
            self._data[chat_id] = {
                "id": chat_id,
                "title": "New chat",
                "messages": [],
                "created_at": now,
                "updated_at": now,
            }
            self._save()

    def add_message(self, chat_id: str, role: str, content: str):
        self.ensure_chat(chat_id)
        self._data[chat_id]["messages"].append({"role": role, "content": content})
        self._data[chat_id]["updated_at"] = datetime.now().isoformat()

        # Auto-title the chat from the first user message
        if self._data[chat_id]["title"] == "New chat" and role == "user":
            title = content.strip().split("\n")[0]
            self._data[chat_id]["title"] = (title[:47] + "...") if len(title) > 50 else title

        self._save()

    def set_messages(self, chat_id: str, messages: list):
        if chat_id in self._data:
            self._data[chat_id]["messages"] = messages
            self._data[chat_id]["updated_at"] = datetime.now().isoformat()
            self._save()

    def is_empty(self, chat_id: str) -> bool:
        chat = self._data.get(chat_id)
        return not chat or not chat.get("messages")
