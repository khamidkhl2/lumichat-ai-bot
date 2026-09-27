import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest

from config import config
from shared.database.adapter import db
from shared.services.sponsor_service import sponsor_service
from shared.services.cross_promo import cross_promo
from shared.services.i18n_base import t
from shared.keyboards.common import get_sponsor_inline_keyboard, get_vip_inline_keyboard

from services.memory_service import memory_service
from services.personas import get_user_persona, get_persona_info
from services.groq_service import groq_service
from services.telegram_formatter import format_telegram_html
from keyboards.inline import get_chat_actions_keyboard

logger = logging.getLogger(__name__)
router = Router()

CLEAR_CONFIRMATIONS = {
    "en": "🧹 <b>Conversation memory cleared!</b>\nLumiChat is ready for a fresh topic.",
    "ru": "🧹 <b>Память диалога очищена!</b>\nLumiChat готов к новой теме.",
    "uz": "🧹 <b>Suhbat xotirasi tozalandi!</b>\nLumiChat yangi mavzuni muhokama qilishga tayyor.",
    "es": "🧹 <b>¡Memoria de la conversación borrada!</b>\nLumiChat está listo para un nuevo tema."
}

@router.message(Command("clear"))
@router.message(Command("new"))
async def cmd_clear_memory(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    lang = user.get("language", "en") if user else "en"

    await memory_service.clear_history(user_id)
    msg = CLEAR_CONFIRMATIONS.get(lang, CLEAR_CONFIRMATIONS["en"])
    await message.answer(msg, parse_mode="HTML")

@router.callback_query(F.data == "chat_clear_memory")
async def callback_clear_memory(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    lang = user.get("language", "en") if user else "en"

    await memory_service.clear_history(user_id)
    msg = CLEAR_CONFIRMATIONS.get(lang, CLEAR_CONFIRMATIONS["en"])
    await callback.message.answer(msg, parse_mode="HTML")
    await callback.answer("Memory cleared!")

async def _send_safe_response(message: Message, text: str, lang: str = "en"):
    """
    Sends response using Telegram HTML parse mode. Splits message if > 4000 characters,
    and falls back to plain text if HTML parsing encounters any unexpected issue.
    """
    max_chunk = 4000
    chunks = [text[i:i + max_chunk] for i in range(0, len(text), max_chunk)] if len(text) > max_chunk else [text]

    for idx, chunk in enumerate(chunks):
        is_last = (idx == len(chunks) - 1)
        kb = get_chat_actions_keyboard(lang) if is_last else None
        try:
            # Send using HTML formatting
            await message.answer(chunk, reply_markup=kb, parse_mode="HTML")
        except TelegramBadRequest as e:
            logger.warning(f"HTML send failed ({e}), falling back to plain text")
            try:
                # Strip HTML tags or send plain text
                await message.answer(chunk, reply_markup=kb, parse_mode=None)
            except Exception as e2:
                logger.error(f"Plain text send also failed: {e2}")

@router.message(F.text & ~F.text.startswith("/"))
async def handle_user_chat(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Friend"
    tg_lang = message.from_user.language_code or "en"

    # 1. Fetch or create user record
    user = await db.get_or_create_user(user_id, username, first_name, tg_lang=tg_lang)
    lang = user.get("language", "en")

    # 2. Sponsor Gate Check
    is_subbed, missing = await sponsor_service.check_user_subscription(message.bot, user_id)
    if not is_subbed:
        title = t("sponsor_gate_title", lang=lang)
        kb = get_sponsor_inline_keyboard(missing, lang=lang)
        await message.answer(title, reply_markup=kb, parse_mode="HTML")
        return

    # 3. Daily Quota Check (VIP bypasses)
    is_allowed, count, limit = await db.check_daily_quota(user_id, "chat", config.DAILY_LIMIT_CHAT)
    if not is_allowed:
        quota_msg = t(
            "quota_reached",
            lang=lang,
            count=count,
            limit=limit,
            needed=config.REFERRALS_FOR_VIP
        )
        kb = get_vip_inline_keyboard(config.VIP_PRICE_STARS, lang=lang)
        await message.answer(quota_msg, reply_markup=kb, parse_mode="HTML")
        return

    # 4. Show typing status while generating
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # 5. Retrieve active persona and conversation history
    persona_id = await get_user_persona(user_id)
    persona_info = get_persona_info(persona_id)
    system_prompt = persona_info["system_prompt"]

    history = await memory_service.get_history(user_id)
    # Add new user message to history payload for Groq
    query_messages = list(history)
    query_messages.append({"role": "user", "content": message.text})

    # 6. Call Groq AI service
    ai_reply = await groq_service.generate_response(
        messages=query_messages,
        system_prompt=system_prompt,
        user_lang=lang
    )

    # 7. Update sliding window & DB persistence
    await memory_service.add_user_message(user_id, message.text)
    await memory_service.add_assistant_message(user_id, ai_reply)

    # 8. Format raw AI response into clean Telegram HTML
    formatted_reply = format_telegram_html(ai_reply)

    # 9. Append subtle cross-promotion tip footer (in native HTML)
    tip = cross_promo.get_tip_footer("chat", lang=lang)
    full_response = formatted_reply + (tip if tip else "")

    # 10. Send response safely
    await _send_safe_response(message, full_response, lang=lang)

    # 11. Increment daily usage counter in database
    await db.increment_daily_usage(user_id, "chat")
