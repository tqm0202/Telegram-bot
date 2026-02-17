import logging

from aiogram import F, Router, types
from aiogram.filters import CommandStart
from telegram_bot.main.database.models import add_user, get_primary_admin_id, is_admin
from telegram_bot.main.keyboards.inline import open_admin_panel_keyboard
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
    if is_admin(message.from_user.id):
        await message.answer(
            "Siz admin sifatida kirdingiz.\n"
            "Adminni boshqarish uchun tugmani bosing yoki /admin yozing.",
            reply_markup=open_admin_panel_keyboard(),
        )
        return
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
    admin_id = get_primary_admin_id()
    if not user or is_admin(user.id):
        return
    if message.text and message.text.startswith("/start"):
        return
    add_user(user.id, user.username)

    content_type = message.content_type
    username = f"@{user.username}" if user.username else "yo'q"

    text = (
        f"📩 Yangi xabar\n\n"
        f"👤 ID: {user.id}\n"
        f"📛 Username: {username}\n"
        f"📦 Turi: {content_type}"
    )

    forwarded_message = await message.copy_to(admin_id)
    await message.bot.send_message(
        admin_id,
        text,
        reply_to_message_id=forwarded_message.message_id,
    )

    await message.answer("Xabaringiz admin'ga yuborildi ✅")
