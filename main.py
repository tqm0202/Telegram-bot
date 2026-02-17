import asyncio
import logging

from aiogram import Bot, Dispatcher
from telegram_bot.main.config import BOT_TOKEN
from telegram_bot.main.handlers import user, admin
from telegram_bot.main.database.models import create_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    create_tables()

    dp.include_router(user.router)
    dp.include_router(admin.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
