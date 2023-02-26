# Це для того, щоби бот працював у streamlit.io
import asyncio
_loop_ = asyncio.new_event_loop()
asyncio.set_event_loop(_loop_)

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

import database as db
import config
import client

import logging
logging.basicConfig(level=logging.WARNING)

# Load bot
bot = Bot(token=config.API_KEY)
dp = Dispatcher(bot)
close_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('❌ Закрити', callback_data="close")]])

@dp.message_handler(commands=['start'], commands_prefix='!/')
async def start_command(message: types.Message):
    if db.get_user_i(message.from_id) is not None:
        await message.answer('/settings - Змінити регіон\n/unsubscribe - Не отримувати оповіщення')
        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    for r in range(len(config.regions)):
        keyboard.insert(InlineKeyboardButton(config.regions[r], callback_data=f"new_{r}"))
    await message.answer("👋🏼 Привіт! Вибери свій регіон", reply_markup=keyboard)

@dp.message_handler(commands=['settings'], commands_prefix='!/')
async def settings_command(message: types.Message):
    user_index = db.get_user_i(message.from_id)
    if user_index is None:
        await start_command(message)
        return
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton('❌ Закрити', callback_data="close"))
    for r in range(len(config.regions)):
        keyboard.insert(InlineKeyboardButton(config.regions[r], callback_data=f"change_{r}"))
    await message.answer(f"Вибери регіон (Зараз вибрано {config.regions[db.userlist[user_index][1]]})", reply_markup=keyboard)

@dp.message_handler(commands=['unsubscribe'], commands_prefix='!/')
async def unsubscribe_command(message: types.Message):
    if db.get_user_i(message.from_id) is None:
        await message.answer('Я ЗАБОРОНЯЮ ТОБІ ВІДПИСУВАТИСЬ!!.\n/start - Отримувати оповіщення)')
        return
    db.remove_user(message.from_id)
    await message.answer('Всьо! Тепер ти не будеш отримувати повідомлення.\n/start - Отримувати оповіщення')

@dp.callback_query_handler(lambda callback_query: True)
async def callback(call: types.CallbackQuery):
    query = call.data.split("_")
    match query[0]:
        case 'close': await call.message.delete()
        case 'new':
            if db.get_user_i(call.from_user.id) is not None: return
            db.new_user(call.from_user.id, int(query[1]))
            await call.message.answer(f'Регіон - {config.regions[int(query[1])]}\nВітаю! Тобі надходитимуть повідомлення.\n\n/settings - Змінити регіон\n/unsubscribe - Не отримувати оповіщення\n\nТакож можеш підписатися на канал розробника - @devromchik')
            await call.message.delete()
        case 'change':
            if db.get_user_i(call.from_user.id) is None: return
            db.change_region(call.from_user.id, int(query[1]))
            await call.message.answer(f'Твій регіон тепер {config.regions[int(query[1])]}')
            await call.message.delete()

# Команди для розробника (мені)
@dp.message_handler(commands=['admin'], commands_prefix='!/')
async def admin_command(message: types.Message):
    if message.from_id == 1041234545:
        await message.delete()
        await message.answer('Команди для розробника (це мені):\n\n → /stopbot - Зупиняє бота;\n → /runid - Дізнатись runid бота;\n → /level - Рівень тривоги;', reply_markup=close_kb)

@dp.message_handler(commands=['stopbot'], commands_prefix='!/')
async def stop_bot_command(message: types.Message):
    if message.from_id != 1041234545: return
    await message.delete()
    await message.answer("Зупиняю бота...", reply_markup=close_kb)
    _loop_.stop()

@dp.message_handler(commands=['runid'], commands_prefix='!/')
async def runid_command(message: types.Message):
    if message.from_id == 1041234545:
        await message.delete()
        await message.answer(str(db.runid), reply_markup=close_kb)

@dp.message_handler(commands=['level'], commands_prefix='!/')
async def level_command(message: types.Message):
    if message.from_id == 1041234545:
        await message.delete()
        await message.answer(f"{client.data['alarm_level']} → {['Все спокійно', 'Тривога по всій Україні'][client.data['alarm_level']]}", reply_markup=close_kb)


async def updates_loop():
    await asyncio.sleep(2)
    print("Починаю стежити за оновленями")
    while True:
        ch, alarms = await client.get_channel_updates()

        # Повідомлення з каналів
        if ch != None:
            for u in db.userlist: await bot.send_message(u, ch, 'HTML')
        
        # Повітряні тривоги
        for a in alarms:
            text = [f"🚨 Повітряна тривога у {config.regions[a[0]]}!", f"🟢 Відбій тривоги у {config.regions[a[0]]}!", f"🚨 Загроза артобстрілу у {config.regions[a[0]]}!", f"🟢 Відбій загрози артобстрілу у {config.regions[a[0]]}!"][a[1]]
            # print(text)
            # print(db.userlist)
            # print(config.regions[a[0]])
            for u in db.users_by_region(a[0]): await bot.send_message(u, text)

        await asyncio.sleep(config.CHECK_DELAY)
_loop_.create_task(updates_loop())

async def check_another_run_loop():
    while True:
        if db.runid != db.get_runid():
            _loop_.stop()
            break
        await asyncio.sleep(6)
_loop_.create_task(check_another_run_loop()) 

if __name__ == "__main__":
    print("Бот працює")
    executor.start_polling(dp, skip_updates=True)
