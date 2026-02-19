import logging

from aiogram import Router
from aiogram.filters import CommandStart
from telegram_bot.main.database.models import (
    add_user,
    get_primary_admin_id,
    is_admin,
    save_incoming_message,
)
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
    file_meta = _extract_file_meta(message)
    username = f"@{user.username}" if user.username else "yo'q"
    save_incoming_message(
        telegram_message_id=message.message_id,
        chat_id=message.chat.id,
        user_id=user.id,
        username=username,
        content_type=message.content_type,
        text=message.text,
        caption=message.caption,
        file_id=file_meta.get("file_id"),
        file_unique_id=file_meta.get("file_unique_id"),
        file_name=file_meta.get("file_name"),
        mime_type=file_meta.get("mime_type"),
        file_size=file_meta.get("file_size"),
        payload=message.model_dump(mode="json", exclude_none=True),
    )

    content_type = message.content_type

    text = (
        f"📩 Yangi xabar\n\n"
        f"👤 ID: {user.id}\n"
        f"📛 Username: {username}\n"
    )

    forwarded_message = await message.copy_to(admin_id)
    await message.bot.send_message(
        admin_id,
        text,
        reply_to_message_id=forwarded_message.message_id,
    )
    
    await message.answer("Xabaringiz admin'ga yuborildi ✅")


def _extract_file_meta(message: Message) -> dict:
    if message.document:
        return {
            "file_id": message.document.file_id,
            "file_unique_id": message.document.file_unique_id,
            "file_name": message.document.file_name,
            "mime_type": message.document.mime_type,
            "file_size": message.document.file_size,
        }
    if message.photo:
        photo = message.photo[-1]
        return {
            "file_id": photo.file_id,
            "file_unique_id": photo.file_unique_id,
            "file_name": None,
            "mime_type": None,
            "file_size": photo.file_size,
        }
    if message.video:
        return {
            "file_id": message.video.file_id,
            "file_unique_id": message.video.file_unique_id,
            "file_name": message.video.file_name,
            "mime_type": message.video.mime_type,
            "file_size": message.video.file_size,
        }
    if message.audio:
        return {
            "file_id": message.audio.file_id,
            "file_unique_id": message.audio.file_unique_id,
            "file_name": message.audio.file_name,
            "mime_type": message.audio.mime_type,
            "file_size": message.audio.file_size,
        }
    if message.voice:
        return {
            "file_id": message.voice.file_id,
            "file_unique_id": message.voice.file_unique_id,
            "file_name": None,
            "mime_type": message.voice.mime_type,
            "file_size": message.voice.file_size,
        }
    if message.video_note:
        return {
            "file_id": message.video_note.file_id,
            "file_unique_id": message.video_note.file_unique_id,
            "file_name": None,
            "mime_type": None,
            "file_size": message.video_note.file_size,
        }
    if message.sticker:
        return {
            "file_id": message.sticker.file_id,
            "file_unique_id": message.sticker.file_unique_id,
            "file_name": message.sticker.emoji,
            "mime_type": None,
            "file_size": message.sticker.file_size,
        }
    if message.animation:
        return {
            "file_id": message.animation.file_id,
            "file_unique_id": message.animation.file_unique_id,
            "file_name": message.animation.file_name,
            "mime_type": message.animation.mime_type,
            "file_size": message.animation.file_size,
        }
    return {}
