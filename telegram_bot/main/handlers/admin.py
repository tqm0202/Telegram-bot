from aiogram import F, Router, types
from telegram_bot.main.config import ADMIN_ID
from aiogram.types import Message


router = Router()


@router.message(F.from_user.id == ADMIN_ID)
async def admin_handler(message: Message):

    # Agar admin reply qilsa
    if message.reply_to_message:
        original_text = message.reply_to_message.text or message.reply_to_message.caption or ""

        # User ID ni ajratib olamiz
        lines = original_text.split("\n")
        user_id_line = [line for line in lines if "ID:" in line]

        if user_id_line:
            user_id = int(user_id_line[0].split(":")[1].strip())

            await message.copy_to(user_id)
            await message.answer("Javob yuborildi ✅")
