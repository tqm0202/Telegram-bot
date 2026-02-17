import logging

from aiogram import F, Router, types
from aiogram.filters import CommandStart
from telegram_bot.main.database.models import add_user
from telegram_bot.main.config import ADMIN_ID
from aiogram.types import Message

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message):
    logger.info(
        "Start command from user_id=%s username=%s",
        message.from_user.id,
        message.from_user.username,
    )
    add_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "Assalomu alaykum.\n\n"
        "Bu bot orqali admin bilan bog'lanishingiz mumkin.\n"
        "Siz yuborgan xabarlar, rasmlar va fayllar adminga yetkaziladi.\n\n"
        "Qanday ishlatish:\n"
        "1) Xabaringizni yozing yoki rasm/fayl yuboring.\n"
        "2) Admin javobini shu yerning o'zida olasiz.\n\n"
        "Boshlash uchun hozir xabar yuboring."
    )


@router.message()
async def user_message(message: Message):
    user = message.from_user
    if not user or user.id == ADMIN_ID:
        return
    if message.text and message.text.startswith("/start"):
        return

    content_type = message.content_type
    username = f"@{user.username}" if user.username else "yo'q"

    text = (
        f"📩 Yangi xabar\n\n"
        f"👤 ID: {user.id}\n"
        f"📛 Username: {username}\n"
        f"📦 Turi: {content_type}"
    )

    forwarded_message = await message.copy_to(ADMIN_ID)
    await message.bot.send_message(
        ADMIN_ID,
        text,
        reply_to_message_id=forwarded_message.message_id,
    )

    await message.answer("Xabaringiz admin'ga yuborildi ✅")
