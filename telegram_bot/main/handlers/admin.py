from aiogram import F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import CallbackQuery, Message

from telegram_bot.main.database.models import (
    add_admin,
    is_admin,
    list_admins,
    remove_admin,
    set_primary_admin,
)
from telegram_bot.main.keyboards.inline import admin_panel_keyboard, open_admin_panel_keyboard


router = Router()
pending_actions = {}


@router.message()
async def admin_handler(message: Message):
    if not message.from_user or not is_admin(message.from_user.id):
        raise SkipHandler()

    if message.text == "/admin":
        await message.answer(
            "Admin paneli:\nKerakli amalni tugma orqali tanlang.",
            reply_markup=admin_panel_keyboard(),
        )
        return
    if message.text == "/adminhelp":
        await message.answer(
            "Admin qo'llanma:\n"
            "1) /admin ni bosing\n"
            "2) Tugmadan amalni tanlang\n"
            "3) Kerak bo'lsa user_id yuboring",
            reply_markup=open_admin_panel_keyboard(),
        )
        return

    if message.text and message.text.startswith("/setadmin"):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip().isdigit():
            await message.answer("Foydalanish: /setadmin <user_id>")
            return
        new_admin_id = int(parts[1].strip())
        set_primary_admin(new_admin_id)
        await message.answer(f"Yangi admin belgilandi: {new_admin_id}")
        return

    action = pending_actions.get(message.from_user.id)
    if action:
        if not message.text or not message.text.strip().isdigit():
            await message.answer("Faqat raqamli user_id yuboring.")
            return

        target_user_id = int(message.text.strip())
        if action == "add":
            created = add_admin(target_user_id)
            if created:
                await message.answer(f"Admin qo'shildi: {target_user_id}")
            else:
                await message.answer(f"Bu user allaqachon admin: {target_user_id}")
        elif action == "set_primary":
            set_primary_admin(target_user_id)
            await message.answer(f"Asosiy admin o'zgartirildi: {target_user_id}")
        elif action == "remove":
            ok, reason = remove_admin(target_user_id)
            if ok:
                await message.answer(f"Admin o'chirildi: {target_user_id}")
            elif reason == "primary":
                await message.answer("Asosiy adminni o'chirib bo'lmaydi. Avval boshqa primary admin belgilang.")
            else:
                await message.answer("Bunday admin topilmadi.")
        pending_actions.pop(message.from_user.id, None)
        return

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


@router.callback_query(F.data.startswith("admin:"))
async def admin_panel_callback(callback: CallbackQuery):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    action = callback.data.split(":", maxsplit=1)[1]
    user_id = callback.from_user.id

    if action == "list":
        admins = list_admins()
        if not admins:
            text = "Adminlar ro'yxati bo'sh."
        else:
            lines = ["Adminlar ro'yxati:"]
            for admin_id, is_primary_admin in admins:
                role = " (asosiy)" if is_primary_admin else ""
                lines.append(f"- {admin_id}{role}")
            text = "\n".join(lines)
        await callback.message.answer(text)
        await callback.answer()
        return
    if action == "open_panel":
        await callback.message.answer(
            "Admin paneli:\nKerakli amalni tugma orqali tanlang.",
            reply_markup=admin_panel_keyboard(),
        )
        await callback.answer()
        return

    if action == "cancel":
        pending_actions.pop(user_id, None)
        await callback.message.answer("Bekor qilindi.")
        await callback.answer()
        return

    if action in {"add", "set_primary", "remove"}:
        pending_actions[user_id] = action
        prompts = {
            "add": "Qo'shmoqchi bo'lgan admin user_id sini yuboring.",
            "set_primary": "Yangi asosiy admin user_id sini yuboring.",
            "remove": "O'chirmoqchi bo'lgan admin user_id sini yuboring.",
        }
        await callback.message.answer(prompts[action])
        await callback.answer()
