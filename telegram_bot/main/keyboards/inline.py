from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def open_admin_panel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Admin panelni ochish", callback_data="admin:open_panel")]
        ]
    )


def admin_panel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Adminlar ro'yxati", callback_data="admin:list")],
            [InlineKeyboardButton(text="Admin qo'shish", callback_data="admin:add")],
            [InlineKeyboardButton(text="Asosiy adminni almashtirish", callback_data="admin:set_primary")],
            [InlineKeyboardButton(text="Adminni o'chirish", callback_data="admin:remove")],
            [InlineKeyboardButton(text="Bekor qilish", callback_data="admin:cancel")],
        ]
    )
