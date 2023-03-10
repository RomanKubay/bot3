# Це для того, щоби бот працював у streamlit.io
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import sys

import database as db
import config
import keyboards as kb
# import logging
# logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_KEY)
dp = Dispatcher(bot)
db.bot = bot
import client

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
        case 'stop':
            await call.message.delete()
            sys.exit(0)
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
    if message.from_id == config.TG_ID:
        await message.delete()
        await message.answer('Команди для розробника (це мені):\n\n → !lastchange (канал) (скіко відняти) - Змінити id останнього повідомлення\nПриклад: !lastchange alert 3;\n → /stopbot - Зупинити бота;\n → /info - Отримати якусь інформацію;', reply_markup=kb.close)

@dp.message_handler(commands=['stopbot'], commands_prefix='!/')
async def stop_bot_command(message: types.Message):
    if message.from_id != config.TG_ID: return
    await message.delete()
    await message.answer("Ви справді бажаєте, щоб я завершив свою роботу?", reply_markup=kb.stop_bot)

@dp.message_handler(commands=['info'], commands_prefix='!/')
async def info_command(message: types.Message):
    if message.from_id == config.TG_ID:
        await message.delete()
        await message.answer(f' → Userlist:\n{db.userlist}\n\n → client data:\n{client.data}\n\n → runid - {db.runid}', reply_markup=kb.close)

@dp.message_handler(commands=['lastchange'], commands_prefix='!/')
async def lastchange_command(message: types.Message):
    if message.from_id == config.TG_ID:
        await message.delete()
        args = message.text.split(' ', 2)
        if len(args) == 3 and args[1] in client.data:
            # print(args, client.data, args[0] in client.data)
            client.data[args[1]] -= int(args[2])
            await message.answer(f'Змінено! Тепер id ост. повідомлення каналу {args[1]} - {client.data[args[1]]}', reply_markup=kb.close)
        else:
            print(f'lastchange error: len(args) == {len(args)} ({len(args) == 3}) and args[1] in client.data - {args[1] in client.data}')
            await message.answer('пиши полюцки', reply_markup=kb.close)

@dp.message_handler(content_types=types.ContentType.ANY)
async def text_handler(message: types.Message):
    # print('text', message.from_id == config.TG_ID, db.auth_now)
    if message.from_id == config.TG_ID and db.auth_now:
        auth_code, password = message.text.split(' ', 1)
        client.auth_code, client.password = auth_code, password
        await message.delete()
        db.auth_now = False
        print("Починаю стежити за оновленями")

async def updates_loop():
    await asyncio.sleep(2)
    while True:
        # Повідомлення з каналів
        l = len(client.CHANNELS)
        if l != 0:
            for msgid in range(l-1, -1, -1):
                for u in db.userlist:
                    await bot.send_message(u[0], client.CHANNELS[msgid], 'HTML')
                client.CHANNELS.pop(msgid)
        
        # Повітряні тривоги
        l = len(client.ALARMS)
        if l != 0:
            print('alarms -', l)
            for aid in range(l-1, -1, -1):
                a = client.ALARMS[aid]
                text = [f"🚨 Повітряна тривога у {config.regions[a[0]]}!", f"🟢 Відбій тривоги у {config.regions[a[0]]}!", f"🚨 Загроза артобстрілу у {config.regions[a[0]]}!", f"🟢 Відбій загрози артобстрілу у {config.regions[a[0]]}!", f"🔴 У {config.regions[a[0]]} щось відбувається! (@air_alert_ua)"][a[1]]
                # print(text, db.users_by_region(a[0]))
                for u in db.users_by_region(a[0]):
                    await bot.send_message(u, text)
                client.ALARMS.pop(aid)

        await asyncio.sleep(config.CHECK_DELAY)
loop.create_task(updates_loop())

async def check_another_run_loop():
    while True:
        if db.runid != db.get_runid():
            sys.exit(0)
        await asyncio.sleep(5)
loop.create_task(check_another_run_loop()) 


if __name__ == "__main__":
    print("Бот працює")
    executor.start_polling(dp, skip_updates=True)
