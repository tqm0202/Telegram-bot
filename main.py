import asyncio
import logging

from aiogram import Bot, Dispatcher
from telegram_bot.main.config import BOT_TOKEN
from telegram_bot.main.handlers import user, admin
from telegram_bot.main.database.models import create_tables
from telegram_bot.main.database.db import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), current_user")
        current_database, current_user = cursor.fetchone()
        logging.info(
            "Connected to PostgreSQL database=%s user=%s",
            current_database,
            current_user,
        )
    finally:
        conn.close()

    create_tables()

    dp.include_router(admin.router)
    dp.include_router(user.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
