import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from shared.database.adapter import db
from shared.services.sponsor_service import sponsor_service
from shared.services.i18n_base import t
from shared.keyboards.common import get_sponsor_inline_keyboard

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.in_(["check_sponsors", "check_sponsor_subs"]))
async def callback_check_sponsors(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    lang = user.get("language", "en") if user else "en"

    is_passed, missing = await sponsor_service.check_user_subscription(callback.bot, user_id)

    if is_passed:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(
            t("sponsor_verified", lang=lang),
            parse_mode="HTML"
        )
        await callback.answer("✅")
    else:
        kb = get_sponsor_inline_keyboard(missing, lang=lang)
        title = t("sponsor_gate_title", lang=lang)
        try:
            await callback.message.edit_text(title, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
        await callback.answer(t("sponsor_not_subbed", lang=lang), show_alert=True)
