import os
import sys
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

# Ensure parent directory is in sys.path so 'shared' module is available
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

load_dotenv()

@dataclass
class ChatBotConfig:
    # Telegram Bot Token
    BOT_TOKEN: str = os.getenv("BOT_TOKEN_CHAT") or os.getenv("BOT_TOKEN", "")
    
    # Administrators
    ADMIN_IDS: List[int] = field(default_factory=list)

    # Groq AI Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_PRIMARY_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "750"))
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))

    # Memory / Conversation Context
    MAX_MEMORY_MESSAGES: int = int(os.getenv("MAX_MEMORY_MESSAGES", "10"))

    # Quotas & VIP
    DAILY_LIMIT_CHAT: int = int(os.getenv("DAILY_LIMIT_CHAT", "15"))
    VIP_PRICE_STARS: int = int(os.getenv("VIP_PRICE_STARS", "50"))
    REFERRALS_FOR_VIP: int = int(os.getenv("REFERRALS_FOR_VIP", "3"))

    # Bot Metadata
    BOT_NAME: str = "LumiChat"
    BOT_USERNAME: str = os.getenv("BOT_USERNAME_CHAT", "lumichat_ai_bot")

    def __post_init__(self):
        admin_str = os.getenv("ADMIN_IDS", "5831301324")
        self.ADMIN_IDS = [int(x.strip()) for x in admin_str.split(",") if x.strip().isdigit()]

config = ChatBotConfig()
