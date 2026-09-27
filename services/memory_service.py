from typing import List, Dict
from collections import deque
from config import config

class MemoryService:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        # Maps user_id -> deque of message dicts: [{"role": "user"|"assistant", "content": "..."}]
        self._stores: Dict[int, deque] = {}

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """Returns the conversation history for a user as a list."""
        if user_id not in self._stores:
            return []
        return list(self._stores[user_id])

    def add_user_message(self, user_id: int, content: str):
        """Appends a user message to the sliding window."""
        if user_id not in self._stores:
            self._stores[user_id] = deque(maxlen=self.max_messages)
        self._stores[user_id].append({"role": "user", "content": content})

    def add_assistant_message(self, user_id: int, content: str):
        """Appends an assistant message to the sliding window."""
        if user_id not in self._stores:
            self._stores[user_id] = deque(maxlen=self.max_messages)
        self._stores[user_id].append({"role": "assistant", "content": content})

    def clear_history(self, user_id: int) -> int:
        """Clears memory for a user and returns number of cleared messages."""
        if user_id in self._stores:
            count = len(self._stores[user_id])
            self._stores[user_id].clear()
            return count
        return 0

    def get_message_count(self, user_id: int) -> int:
        """Returns current number of messages in memory for the user."""
        return len(self._stores.get(user_id, []))

memory_service = MemoryService(max_messages=config.MAX_MEMORY_MESSAGES)
