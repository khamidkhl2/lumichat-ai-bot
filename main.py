import asyncio
import logging
import sys
import os

# Ensure parent directory is in sys.path
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import config
from shared.database.adapter import db

# Import routers
from handlers.start import router as start_router
from handlers.persona import router as persona_router
from handlers.sponsor_gate import router as sponsor_gate_router
from handlers.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("LumiChat")

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Start bot & overview"),
        BotCommand(command="persona", description="Switch AI Persona & Role"),
        BotCommand(command="new", description="Reset conversation memory"),
        BotCommand(command="clear", description="Clear memory context"),
        BotCommand(command="vip", description="Get VIP Pass (Unlimited)"),
        BotCommand(command="referral", description="Invite friends for free VIP"),
        BotCommand(command="bots", description="Discover sister bots"),
        BotCommand(command="lang", description="Switch interface language"),
        BotCommand(command="help", description="How to use LumiChat"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"Could not set bot commands: {e}")

async def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is not configured! Please set BOT_TOKEN_CHAT or BOT_TOKEN in .env.")
        return

    # 1. Initialize shared database
    logger.info("Initializing database...")
    await db.init()

    # 2. Setup Bot & Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # 3. Register Routers in order of priority
    dp.include_router(start_router)
    dp.include_router(persona_router)
    dp.include_router(sponsor_gate_router)
    dp.include_router(chat_router)  # Chat text handler must be last

    # 4. Set Bot Menu Commands
    await set_bot_commands(bot)

    try:
        bot_user = await bot.get_me()
        logger.info(f"🚀 LumiChat (@{bot_user.username}) is running!")
    except Exception as e:
        logger.warning(f"Could not fetch bot identity: {e}")

    # 5. Start Polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
