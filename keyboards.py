from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

close = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('❌ Закрити', callback_data="close")]])
