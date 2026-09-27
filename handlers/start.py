import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from config import config
from shared.database.adapter import db
from shared.services.i18n_base import t
from shared.services.cross_promo import cross_promo
from keyboards.inline import (
    get_main_reply_keyboard,
    get_language_inline_keyboard,
    get_vip_inline_keyboard
)
from services.personas import get_user_persona, get_persona_name

logger = logging.getLogger(__name__)
router = Router()

BOT_DESCRIPTIONS = {
    "en": (
        "🤖 I am <b>LumiChat</b>, your powerful AI Assistant powered by Groq LLaMA-3.3.\n\n"
        "✨ <b>What I can do:</b>\n"
        "• Answer complex questions & brainstorm ideas\n"
        "• Solve math & homework step-by-step (/persona)\n"
        "• Write, review & debug code in any language\n"
        "• Translate between 50+ languages fluently\n"
        "• Remember context across your conversation (/clear to reset)\n\n"
        f"🎁 <b>Free Daily Quota:</b> {config.DAILY_LIMIT_CHAT} messages/day (VIP = Unlimited)"
    ),
    "ru": (
        "🤖 Я <b>LumiChat</b> — твой умный ИИ-помощник на базе Groq LLaMA-3.3.\n\n"
        "✨ <b>Что я умею:</b>\n"
        "• Отвечать на любые вопросы и генерировать идеи\n"
        "• Решать задачи и домашние задания с пояснениями (/persona)\n"
        "• Писать и находить ошибки в коде на любых языках\n"
        "• Переводить тексты на 50+ языков с нюансами\n"
        "• Помнить контекст диалога (/clear для сброса)\n\n"
        f"🎁 <b>Бесплатный лимит:</b> {config.DAILY_LIMIT_CHAT} сообщений в день (VIP = Безлимит)"
    ),
    "uz": (
        "🤖 Men <b>LumiChat</b> — Groq LLaMA-3.3 asosida ishlovchi aqlli AI yordamchingizman.\n\n"
        "✨ <b>Imkoniyatlarim:</b>\n"
        "• Murakkab savollarga javob berish va g'oyalar yaratish\n"
        "• Matematika va uy vazifalarini bosqichma-bosqich yechish (/persona)\n"
        "• Istalgan dasturlash tilida kod yozish va xatolarni tuzatish\n"
        "• 50 dan ortiq tillarda aniq tarjima qilish\n"
        "• Suhbat kontekstini eslab qolish (/clear tozalash uchun)\n\n"
        f"🎁 <b>Kunlik bepul limit:</b> {config.DAILY_LIMIT_CHAT} ta xabar (VIP = Cheksiz)"
    ),
    "es": (
        "🤖 Soy <b>LumiChat</b>, tu asistente inteligente impulsado por Groq LLaMA-3.3.\n\n"
        "✨ <b>Lo que puedo hacer:</b>\n"
        "• Responder preguntas y crear ideas\n"
        "• Resolver tareas y matemáticas paso a paso (/persona)\n"
        "• Escribir y depurar código en cualquier lenguaje\n"
        "• Traducir con precisión entre más de 50 idiomas\n"
        "• Recordar el contexto de la conversación (/clear para reiniciar)\n\n"
        f"🎁 <b>Cuota diaria gratuita:</b> {config.DAILY_LIMIT_CHAT} mensajes/día (VIP = Ilimitado)"
    )
}

HELP_TEXTS = {
    "en": (
        "📖 <b>How to use LumiChat:</b>\n\n"
        "1. <b>Chat Naturally:</b> Send any message or question directly in this chat.\n"
        "2. <b>AI Personas:</b> Use /persona to switch between Math Tutor, Code Expert, Translator, Storyteller, or General Assistant.\n"
        "3. <b>Memory & Context:</b> The bot remembers your last 10 messages. Use /new or /clear to start a fresh topic.\n"
        f"4. <b>Daily Limit:</b> Free users get {config.DAILY_LIMIT_CHAT} messages per day.\n"
        "5. <b>VIP Unlimited:</b> Upgrade to VIP via /vip or invite friends via /referral for free VIP!\n\n"
        "⚡️ <b>Commands:</b>\n"
        "/persona - Change AI role & specialization\n"
        "/clear or /new - Reset conversation memory\n"
        "/vip - Get unlimited ad-free access (Stars)\n"
        "/referral - Invite friends for free VIP\n"
        "/bots - Discover our other free AI bots\n"
        "/lang - Switch interface language"
    ),
    "ru": (
        "📖 <b>Руководство по использованию LumiChat:</b>\n\n"
        "1. <b>Общайтесь:</b> Просто отправьте любой вопрос или текст в этот чат.\n"
        "2. <b>Персонажи ИИ:</b> Используйте /persona для переключения на Репетитора, Программиста, Переводчика, Рассказчика.\n"
        "3. <b>Память диалога:</b> Бот помнит последние 10 сообщений. Используйте /clear или /new для новой темы.\n"
        f"4. <b>Лимиты:</b> Бесплатно доступно {config.DAILY_LIMIT_CHAT} сообщений в день.\n"
        "5. <b>VIP Безлимит:</b> Активируйте VIP через /vip или зовите друзей через /referral!\n\n"
        "⚡️ <b>Команды:</b>\n"
        "/persona - Выбрать роль ассистента\n"
        "/clear или /new - Сбросить память диалога\n"
        "/vip - Безлимитный доступ (Stars)\n"
        "/referral - Пригласить друзей за VIP\n"
        "/bots - Другие наши бесплатные боты\n"
        "/lang - Сменить язык интерфейса"
    ),
    "uz": (
        "📖 <b>LumiChat dan foydalanish qo'llanmasi:</b>\n\n"
        "1. <b>Savol yuboring:</b> Shunchaki xabar yoki savolingizni yozib yuboring.\n"
        "2. <b>AI Qiyofalari:</b> /persona orqali O'qituvchi, Dasturchi, Tarjimon yoki Yozuvchi rejimini tanlang.\n"
        "3. <b>Suhbat xotirasi:</b> Bot oxirgi 10 ta xabarni eslab qoladi. Yangi mavzu uchun /clear yoki /new buyrug'idan foydalaning.\n"
        f"4. <b>Kunlik limit:</b> Kuniga {config.DAILY_LIMIT_CHAT} ta bepul xabar.\n"
        "5. <b>VIP Cheksiz:</b> /vip orqali cheksiz qiling yoki /referral orqali do'stlarni taklif qilib bepul VIP oling!\n\n"
        "⚡️ <b>Buyruqlar:</b>\n"
        "/persona - AI qiyofasini o'zgartirish\n"
        "/clear yoki /new - Suhbat xotirasini tozalash\n"
        "/vip - Cheksiz VIP olish (Stars)\n"
        "/referral - Do'stlarni taklif qilish\n"
        "/bots - Boshqa bepul botlarimiz\n"
        "/lang - Tilni o'zgartirish"
    ),
    "es": (
        "📖 <b>Cómo usar LumiChat:</b>\n\n"
        "1. <b>Chatea libremente:</b> Envía cualquier mensaje o pregunta aquí.\n"
        "2. <b>Personajes de IA:</b> Usa /persona para cambiar a Tutor, Desarrollador, Traductor, Escritor o Asistente.\n"
        "3. <b>Memoria:</b> El bot recuerda tus últimos 10 mensajes. Usa /clear o /new para reiniciar.\n"
        f"4. <b>Límite diario:</b> {config.DAILY_LIMIT_CHAT} mensajes gratuitos al día.\n"
        "5. <b>VIP Ilimitado:</b> Consigue VIP con /vip o invita amigos con /referral.\n\n"
        "⚡️ <b>Comandos:</b>\n"
        "/persona - Cambiar especialidad de la IA\n"
        "/clear o /new - Borrar memoria del chat\n"
        "/vip - Acceso VIP ilimitado (Stars)\n"
        "/referral - Invitar amigos por VIP\n"
        "/bots - Descubrir otros bots gratuitos\n"
        "/lang - Cambiar idioma"
    )
}

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or "Friend"
    tg_lang = message.from_user.language_code or "en"

    # Check for referral or network campaign args
    args = message.text.split()[1] if len(message.text.split()) > 1 else ""
    referrer_id = None
    if args.startswith("ref_") and args[4:].isdigit():
        referrer_id = int(args[4:])

    user = await db.get_or_create_user(
        user_id=user_id,
        username=username,
        first_name=first_name,
        tg_lang=tg_lang,
        referrer_id=referrer_id
    )
    lang = user.get("language", "en")

    bot_desc = BOT_DESCRIPTIONS.get(lang, BOT_DESCRIPTIONS["en"])
    welcome_msg = t("welcome", lang=lang, bot_name=config.BOT_NAME, bot_desc=bot_desc)

    await message.answer(
        welcome_msg,
        reply_markup=get_main_reply_keyboard(lang),
        parse_mode="HTML"
    )

@router.message(Command("help"))
@router.message(F.text.in_(["❓ Help & Guide", "❓ Помощь", "❓ Yordam", "❓ Ayuda"]))
async def cmd_help(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user.get("language", "en") if user else "en"
    help_body = HELP_TEXTS.get(lang, HELP_TEXTS["en"])
    await message.answer(help_body, parse_mode="HTML")

@router.message(Command("lang"))
@router.message(F.text.in_(["🌐 Language", "🌐 Язык / Language", "🌐 Til / Language", "🌐 Idioma / Language"]))
async def cmd_lang(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user.get("language", "en") if user else "en"
    await message.answer(
        t("lang_select", lang=lang),
        reply_markup=get_language_inline_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_lang:"))
async def callback_set_lang(callback: CallbackQuery):
    lang_code = callback.data.split(":", 1)[1]
    await db.set_user_language(callback.from_user.id, lang_code)
    msg = t("lang_changed", lang=lang_code)
    await callback.message.edit_text(msg, parse_mode="HTML")
    await callback.message.answer(
        t("welcome", lang=lang_code, bot_name=config.BOT_NAME, bot_desc=BOT_DESCRIPTIONS.get(lang_code, BOT_DESCRIPTIONS["en"])),
        reply_markup=get_main_reply_keyboard(lang_code),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(Command("vip"))
@router.message(F.text.in_(["👑 VIP Pass (Ad-Free)", "👑 VIP Доступ (Без рекламы)", "👑 VIP Obuna (Reklamasiz)", "👑 Pase VIP (Sin anuncios)"]))
async def cmd_vip(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user.get("language", "en") if user else "en"
    is_vip = user.get("is_vip") if user else False

    if is_vip:
        await message.answer("👑 <b>You already have active VIP status!</b>\nEnjoy unlimited requests and zero sponsor gates.", parse_mode="HTML")
        return

    vip_text = t("vip_title", lang=lang, stars=config.VIP_PRICE_STARS)
    kb = get_vip_inline_keyboard(config.VIP_PRICE_STARS, lang=lang)
    await message.answer(vip_text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "buy_vip_stars")
async def callback_buy_vip_stars(callback: CallbackQuery):
    prices = [LabeledPrice(label=f"LumiChat 30-Day VIP Pass", amount=config.VIP_PRICE_STARS)]
    await callback.bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="👑 30-Day VIP Pass (LumiChat)",
        description="Unlimited AI messages, priority response speed, and zero sponsor channel requirements.",
        payload=f"vip_chat_{callback.from_user.id}",
        currency="XTR",
        prices=prices
    )
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    if payload.startswith("vip_chat_"):
        user_id = int(payload.split("_")[-1])
        await db.set_user_vip(user_id, days=30)
        user = await db.get_user(user_id)
        lang = user.get("language", "en") if user else "en"
        await message.answer(t("vip_success", lang=lang), parse_mode="HTML")

@router.message(Command("referral"))
@router.message(F.text.in_(["👥 Invite Friends", "👥 Пригласить друзей", "👥 Do'stlarni taklif qilish", "👥 Invitar amigos"]))
async def cmd_referral(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user.get("language", "en") if user else "en"
    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"
    ref_count = user.get("referral_count", 0) if user else 0

    text = t("referral_title", lang=lang, count=ref_count, needed=config.REFERRALS_FOR_VIP, link=ref_link)
    await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "view_referral")
async def callback_view_referral(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    lang = user.get("language", "en") if user else "en"
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{callback.from_user.id}"
    ref_count = user.get("referral_count", 0) if user else 0

    text = t("referral_title", lang=lang, count=ref_count, needed=config.REFERRALS_FOR_VIP, link=ref_link)
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@router.message(Command("bots"))
@router.message(F.text.in_(["⚡️ More Free Bots", "⚡️ Другие бесплатные боты", "⚡️ Boshqa bepul botlar", "⚡️ Más Bots Gratis"]))
async def cmd_bots(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user.get("language", "en") if user else "en"
    kb = cross_promo.get_bots_keyboard(current_bot_id="chat", lang=lang)
    title = t("bots_menu_title", lang=lang)
    await message.answer(title, reply_markup=kb, parse_mode="HTML")
