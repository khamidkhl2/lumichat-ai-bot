import logging
from typing import List, Dict
from collections import deque
from config import config

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        # Maps user_id -> deque of message dicts: [{"role": "user"|"assistant", "content": "..."}]
        self._stores: Dict[int, deque] = {}

    async def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """Returns conversation history, checking DB if not in memory."""
        if user_id in self._stores:
            return list(self._stores[user_id])

        try:
            from shared.database.adapter import db
            db_history = await db.get_chat_history(user_id, limit=self.max_messages)
            self._stores[user_id] = deque(db_history, maxlen=self.max_messages)
            return list(self._stores[user_id])
        except Exception as e:
            logger.debug(f"Could not fetch history from DB for {user_id}: {e}")
            if user_id not in self._stores:
                self._stores[user_id] = deque(maxlen=self.max_messages)
            return list(self._stores[user_id])

    async def add_user_message(self, user_id: int, content: str):
        """Appends user message to sliding window and saves to DB."""
        if user_id not in self._stores:
            await self.get_history(user_id)
        self._stores[user_id].append({"role": "user", "content": content})

        try:
            from shared.database.adapter import db
            await db.add_chat_message(user_id, "user", content)
        except Exception as e:
            logger.debug(f"Could not persist user message to DB: {e}")

    async def add_assistant_message(self, user_id: int, content: str):
        """Appends assistant message to sliding window and saves to DB."""
        if user_id not in self._stores:
            await self.get_history(user_id)
        self._stores[user_id].append({"role": "assistant", "content": content})

        try:
            from shared.database.adapter import db
            await db.add_chat_message(user_id, "assistant", content)
        except Exception as e:
            logger.debug(f"Could not persist assistant message to DB: {e}")

    async def clear_history(self, user_id: int) -> int:
        """Clears memory from both in-memory cache and DB."""
        count = 0
        if user_id in self._stores:
            count = len(self._stores[user_id])
            self._stores[user_id].clear()

        try:
            from shared.database.adapter import db
            db_count = await db.clear_chat_history(user_id)
            count = max(count, db_count)
        except Exception as e:
            logger.debug(f"Could not clear DB history for {user_id}: {e}")

        return count

    def get_cached_count(self, user_id: int) -> int:
        """Returns message count in memory cache."""
        return len(self._stores.get(user_id, []))

memory_service = MemoryService(max_messages=config.MAX_MEMORY_MESSAGES)
