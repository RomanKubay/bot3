# Це для того, щоби бот працював у streamlit.io
import asyncio
_loop_ = asyncio.new_event_loop()
asyncio.set_event_loop(_loop_)

from aiogram import Bot, Dispatcher, executor, types
import asyncio

import database as db
import config
import client

import logging
logging.basicConfig(level=logging.WARNING)


# Load bot
bot = Bot(token=config.API_KEY)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'], commands_prefix='!/')
async def start_command(message: types.Message):
    if message.from_id in db.userlist:
        await message.answer('/unsubscribe - Не отримувати оповіщення')
        return
    db.new_user(message.from_id)
    await message.answer('Вітаю! Вам надходитимуть повідомлення.\n/unsubscribe - Не отримувати оповіщення')

@dp.message_handler(commands=['unsubscribe'], commands_prefix='!/')
async def unsubscribe_command(message: types.Message):
    db.remove_user(message.from_id)
    await message.answer('Всьо! Тепер Вам не будуть надходити повідомлення.\n/start - Отримувати оповіщення')

# Команди для розробника (мені)
@dp.message_handler(commands=['admin'], commands_prefix='!/')
async def admin_command(message: types.Message):
    if message.from_id == 1041234545:
        await message.answer('Команди для розробника (це мені):\n\n → /stopbot - Зупиняє бота;\n → /runid - Дізнатись runid бота;')

@dp.message_handler(commands=['stopbot'], commands_prefix='!/')
async def stop_bot_command(message: types.Message):
    if message.from_id != 1041234545: return
    await message.answer("Зупиняю бота...")
    _loop_.stop()

@dp.message_handler(commands=['runid'], commands_prefix='!/')
async def runid_command(message: types.Message):
    if message.from_id == 1041234545:
        await message.answer(str(db.runid))


async def updates_loop():
    await asyncio.sleep(2)
    print("Починаю стежити за оновленями")
    while True:
        upd, for_all = await client.get_updates()
        if upd != None and for_all:
            for u in db.userlist: await bot.send_message(u, upd, 'HTML')
        await asyncio.sleep(7)
_loop_.create_task(updates_loop())

async def check_another_run_loop():
    while True:
        if db.runid != db.get_runid():
            _loop_.stop()
            break
        await asyncio.sleep(4)
_loop_.create_task(check_another_run_loop()) 

if __name__ == "__main__":
    print("Бот працює")
    executor.start_polling(dp, skip_updates=True)
