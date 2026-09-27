from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shared.keyboards.common import (
    get_main_reply_keyboard,
    get_language_inline_keyboard,
    get_sponsor_inline_keyboard,
    get_vip_inline_keyboard
)
from services.personas import get_all_personas, get_persona_name

def get_persona_inline_keyboard(current_persona: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Builds inline keyboard listing all available AI personas."""
    buttons = []
    personas = get_all_personas()
    for p in personas:
        pid = p["id"]
        emoji = p["emoji"]
        name = get_persona_name(pid, lang=lang)
        mark = " ✅" if pid == current_persona else ""
        buttons.append([
            InlineKeyboardButton(text=f"{emoji} {name}{mark}", callback_data=f"set_persona:{pid}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_chat_actions_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Quick inline actions for chat responses."""
    labels = {
        "en": ("🧹 Clear Memory", "🎭 Personas"),
        "ru": ("🧹 Очистить память", "🎭 Персонажи"),
        "uz": ("🧹 Xotirani tozalash", "🎭 Qiyofalar"),
        "es": ("🧹 Borrar memoria", "🎭 Personajes")
    }
    lbl_clear, lbl_persona = labels.get(lang, labels["en"])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=lbl_clear, callback_data="chat_clear_memory"),
            InlineKeyboardButton(text=lbl_persona, callback_data="open_personas")
        ]
    ])

__all__ = [
    "get_persona_inline_keyboard",
    "get_chat_actions_keyboard",
    "get_main_reply_keyboard",
    "get_language_inline_keyboard",
    "get_sponsor_inline_keyboard",
    "get_vip_inline_keyboard"
]
