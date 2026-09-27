import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from shared.database.adapter import db
from services.personas import (
    get_user_persona,
    set_user_persona,
    get_persona_info,
    get_persona_name,
    get_persona_desc
)
from keyboards.inline import get_persona_inline_keyboard

logger = logging.getLogger(__name__)
router = Router()

PERSONA_MENU_TITLES = {
    "en": (
        "🎭 <b>Select AI Persona & Specialization:</b>\n\n"
        "Choose how LumiChat should act and respond to you:\n\n"
        "• <b>General Assistant:</b> Smart daily tasks & brainstorming\n"
        "• <b>Homework Tutor:</b> Step-by-step math & science mentor\n"
        "• <b>Senior Developer:</b> Clean code, architecture & debugging\n"
        "• <b>Translator:</b> Nuanced multi-lingual translation\n"
        "• <b>Storyteller:</b> Creative writing, novels & worldbuilding\n\n"
        "👇 Tap a persona below to activate:"
    ),
    "ru": (
        "🎭 <b>Выберите персонажа и специализацию ИИ:</b>\n\n"
        "Выберите, в какой роли LumiChat будет отвечать вам:\n\n"
        "• <b>Умный помощник:</b> Повседневные вопросы и идеи\n"
        "• <b>Репетитор:</b> Пошаговое объяснение математики и уроков\n"
        "• <b>Senior Разработчик:</b> Качественный код, алгоритмы и баги\n"
        "• <b>Переводчик:</b> Точный перевод с сохранением смысла и стиля\n"
        "• <b>Рассказчик:</b> Сюжеты, сценарии, стихи и креативные тексты\n\n"
        "👇 Нажмите на персонажа ниже для активации:"
    ),
    "uz": (
        "🎭 <b>AI qiyofasi va yo'nalishini tanlang:</b>\n\n"
        "LumiChat sizga qaysi rolda javob berishini xohlaysiz:\n\n"
        "• <b>Aqlli Yordamchi:</b> Umumiy savollar va g'oyalar\n"
        "• <b>O'qituvchi:</b> Matematika va fanlarni bosqichma-bosqich yechish\n"
        "• <b>Senior Dasturchi:</b> Mukammal kod, arxitektura va xatolar tahlili\n"
        "• <b>Tarjimon:</b> 50+ tillarda aniq va tabiiy tarjima\n"
        "• <b>Ijodiy Hikoyachi:</b> Hikoyalar, ssenariylar va badiiy matnlar\n\n"
        "👇 Quyidagi tugmalardan birini bosing:"
    ),
    "es": (
        "🎭 <b>Selecciona la Especialidad del Asistente:</b>\n\n"
        "Elige cómo quieres que responda LumiChat:\n\n"
        "• <b>Asistente General:</b> Preguntas diarias y redacción\n"
        "• <b>Tutor:</b> Explicaciones paso a paso de matemáticas y tareas\n"
        "• <b>Desarrollador Senior:</b> Código limpio, arquitectura y depuración\n"
        "• <b>Traductor:</b> Traducción precisa y natural\n"
        "• <b>Escritor Creativo:</b> Cuentos, novelas y narrativas\n\n"
        "👇 Elige un personaje abajo:"
    )
}

@router.message(Command("persona"))
async def cmd_persona(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    lang = user.get("language", "en") if user else "en"
    current_persona = await get_user_persona(user_id)

    title = PERSONA_MENU_TITLES.get(lang, PERSONA_MENU_TITLES["en"])
    kb = get_persona_inline_keyboard(current_persona, lang=lang)
    await message.answer(title, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "open_personas")
async def callback_open_personas(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    lang = user.get("language", "en") if user else "en"
    current_persona = await get_user_persona(user_id)

    title = PERSONA_MENU_TITLES.get(lang, PERSONA_MENU_TITLES["en"])
    kb = get_persona_inline_keyboard(current_persona, lang=lang)
    await callback.message.edit_text(title, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("set_persona:"))
async def callback_set_persona(callback: CallbackQuery):
    persona_id = callback.data.split(":", 1)[1]
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    lang = user.get("language", "en") if user else "en"

    await set_user_persona(user_id, persona_id)
    info = get_persona_info(persona_id)
    name = get_persona_name(persona_id, lang=lang)
    desc = get_persona_desc(persona_id, lang=lang)

    confirmations = {
        "en": f"✅ Activated persona: <b>{info['emoji']} {name}</b>\n\n<i>{desc}</i>\n\nSend your message to start!",
        "ru": f"✅ Выбран персонаж: <b>{info['emoji']} {name}</b>\n\n<i>{desc}</i>\n\nОтправьте сообщение, чтобы начать!",
        "uz": f"✅ Qiyofa tanlandi: <b>{info['emoji']} {name}</b>\n\n<i>{desc}</i>\n\nBoshlash uchun xabaringizni yuboring!",
        "es": f"✅ Personaje activado: <b>{info['emoji']} {name}</b>\n\n<i>{desc}</i>\n\n¡Envía tu mensaje para comenzar!"
    }
    msg = confirmations.get(lang, confirmations["en"])
    kb = get_persona_inline_keyboard(persona_id, lang=lang)
    await callback.message.edit_text(msg, reply_markup=kb, parse_mode="HTML")
    await callback.answer(f"Switched to {name}!")
