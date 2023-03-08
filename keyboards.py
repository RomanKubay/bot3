from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

close = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('❌ Закрити', callback_data="close")]])
stop_bot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('🆗 Так, закрийся', callback_data="stop")],
    [InlineKeyboardButton('🙅‍♂️ Ні. Поки що працюй', callback_data="close")]
])
